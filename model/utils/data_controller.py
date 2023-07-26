import re
import pickle
import torch
import yaml
import pandas as pd
import pytorch_lightning as pl
import re

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

class Dataset(Dataset):
    """
    Dataloader에서 불러온 데이터를 Dataset으로 만들기
    """

    def __init__(self, data, train=False):
        self.inputs = data[0]
        self.tags = data[1]
        self.train = train

    def __getitem__(self, idx):
        if self.train:
            inputs = {key: val[idx].clone().detach()
                    for key, val in self.inputs.items()}
            tags = self.tags[idx]
                
            return inputs, tags
        else:
            return self.inputs[idx], self.tags[idx]
        
    def __len__(self):
        if self.train:        
            return len(self.inputs['input_ids'])
        else:
            return len(self.inputs)
        
class Dataloader(pl.LightningDataModule):
    
    """
    원본 데이터를 불러와 전처리 후 Dataloader 만들어 Dataset에 넘겨 최종적으로 사용할 데이터셋 만들기
    """

    def __init__(self, tokenizer, CFG):
        super(Dataloader, self).__init__()
        self.CFG = CFG
        self.tokenizer = tokenizer
        
        self.train_valid_df, self.predict_df = load_data()

        self.train_dataset = None
        self.val_dataset = None
        
        predict = self.preprocessing(self.predict_df)
        self.predict_dataset = Dataset(predict)

    def tokenizing(self, x, train=False):
        
        """ 
        Arguments:
        x: pd.DataFrame

        Returns:
        inputs: Dict({'input_ids', 'attention_mask', 'labels', ...}), 각 tensor(num_data, max_length)
        """
        
        instruction = '다음의 블로그 글에 어울리는 태그 5개를 생성하시오. 태그의 형식은 다음과 같음. [#영어(한글), #영어(한글), #영어(한글), #영어(한글), #영어(한글)]'
        x['instruction'] = instruction
        
        x['context'] = x['context'].apply(lambda x: x.replace(u"\u200b", u""))
        x['context'] = x['context'].apply(lambda sample: re.sub('\s+', ' ', sample))
        x['context'] = x['context'].apply(lambda sample: re.sub('https://.*?\s', '[LINK]', sample))
        
        if self.CFG['train']['prompts'] == 'topic_title_summarize':
            prompts_list = [f"### Instruction(명령어):\n{row['instruction']}\n\n### Input(입력):\n주제는 [{row['small_topic']}], 제목은 [{row['title']}], 한 줄 요약은 [{row['summarize']}]이다.\n\n### Response(응답): " for _ , row in x.iterrows()]
            
        elif self.CFG['train']['prompts'] == 'topic_title_context':
            prompts_list = [f"### Instruction(명령어):\n{row['instruction']}\n\n### Input(입력):\n주제는 [{row['small_topic']}], 제목은 [{row['title']}], 본문은 [{row['context']}]이다.\n\n### Response(응답): \n" for _ , row in x.iterrows()]
        
        elif self.CFG['train']['prompts'] == 'title_context':
            prompts_list = [f"### Instruction(명령어):\n{row['instruction']}\n\n### Input(입력):\n제목은 [{row['title']}], 본문은 [{row['context']}]이다.\n\n### Response(응답): \n" for _ , row in x.iterrows()]
        
        else:
            raise ValueError('unappropriate prompts')
            
        if train:
            if self.CFG['train']['korean_first']:
                answers_list = [
                    f"#{row['tag1'][1:].split('(')[1][:-1]}({row['tag1'][1:].split('(')[0]}), #{row['tag2'][1:].split('(')[1][:-1]}({row['tag2'][1:].split('(')[0]}), #{row['tag3'][1:].split('(')[1][:-1]}({row['tag3'][1:].split('(')[0]}), #{row['tag4'][1:].split('(')[1][:-1]}({row['tag4'][1:].split('(')[0]}), #{row['tag5'][1:].split('(')[1][:-1]}({row['tag5'][1:].split('(')[0]})"
                    for _, row in x.iterrows()
                ]


            else:
                answers_list = [f"{row['tag1']}, {row['tag2']}, {row['tag3']}, {row['tag4']}, {row['tag5']}" for _ , row in x.iterrows()]
                
            inputs = self.tokenizer(
                prompts_list,
                answers_list,
                return_tensors='pt',
                padding=True,
                truncation='only_first',
                max_length=self.CFG['train']['token_max_len'],
                add_special_tokens=True,
            )
            
            labels = [[-100] * (x.tolist().index(1)) + inputs['input_ids'][idx][x.tolist().index(1):].tolist() for idx, x in tqdm(enumerate(inputs['token_type_ids']))]
            inputs['labels'] = torch.tensor(labels)
            
            return inputs

        else:            
            return prompts_list

    def preprocessing(self, x, train=False):
        DC = DataCleaning(self.CFG['select_DC'])
        DA = DataAugmentation(self.CFG['select_DA'])

        if train:
            # x = DC.process(x)
            # x = DA.process(x)         
            
            # 텍스트 데이터 토큰화
            train_x, val_x = train_test_split(x,
                                            test_size=self.CFG['train']['test_size'],
                                            shuffle=True,
                                            random_state=self.CFG['seed'])
            
            train_inputs = self.tokenizing(train_x, train=True)
            train_tags = [', '.join([row['tag1'], row['tag2'], row['tag3'], row['tag4'], row['tag5']]) for _, row in train_x.iterrows()]
            
            val_inputs = self.tokenizing(val_x, train=True)
            val_tags = [', '.join([row['tag1'], row['tag2'], row['tag3'], row['tag4'], row['tag5']]) for _, row in val_x.iterrows()]

            return (train_inputs, train_tags), (val_inputs, val_tags)
        
        else:
            # x = DC.process(x)

            # 텍스트 데이터 토큰화
            predict_inputs = self.tokenizing(x, train=False)
            predict_tags = [', '.join([row['tag1'], row['tag2'], row['tag3'], row['tag4'], row['tag5']]) for _, row in x.iterrows()]
            
            return (predict_inputs, predict_tags)

    def setup(self, stage='fit'):
        if stage == 'fit':
            # 학습 데이터 준비
            train, val = self.preprocessing(self.train_valid_df, train=True)
            self.train_dataset = Dataset(train, train=True)
            self.val_dataset = Dataset(val, train=True)
        else:
            # 평가 데이터 호출
            predict = self.preprocessing(self.predict_df)
            self.predict_dataset = Dataset(predict)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.CFG['train']['batch_size'], shuffle=True)
    
    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.CFG['train']['batch_size'], shuffle=True)

    def predict_dataloader(self):
        return DataLoader(self.predict_dataset, batch_size=self.CFG['train']['batch_size'], shuffle=False)
    
class DataCleaning():
    """
    config select DC에 명시된 Data Cleaning 기법을 적용시켜주는 클래스
    """
    def __init__(self, select_list):
        self.select_list = select_list
        
    def process(self, df):
        if self.select_list:
            for method_name in self.select_list:
                print('method name: '+ method_name)
                
                print('before:')
                print(df.head(1))
                
                method = eval("self." + method_name)
                df = method(df)
                
                print('after:')
                print(df.head(1))

        return df

    """
    data cleaning 코드
    """
    def data_cleaning_demo(self, df):
        """ 
        Arguments:
        df: Cleaning을 수행하고자 하는 DataFrame
        
        Return:
        df: Cleaning 작업이 완료된 DataFrame
        """
                
        return df


class DataAugmentation():
    """
    config select DA에 명시된 Data Augmentation 기법을 적용시켜주는 클래스
    """

    def __init__(self, select_list):
        self.select_list = select_list

    def process(self, df):
        if self.select_list:
            aug_df = pd.DataFrame(columns=df.columns)

            for method_name in self.select_list:
                method = eval("self." + method_name)
                aug_df = pd.concat([aug_df, method(df)])

            df = pd.concat([df, aug_df])

        return df
    
    """
    data augmentation 코드
    """
    
    def data_augmentation_demo(self, df):
        """

        Arguments:
        df: augmentation을 수행하고자 하는 DataFrame

        Return:
        df: augmentation된 DataFrame (exclude original)
        """
        
        return df


def load_data():
    """
    학습 데이터와 테스트 데이터 DataFrame 가져오기
    """
    with open('./config/use_config.yaml') as f:
        CFG = yaml.load(f, Loader=yaml.FullLoader)
        
    df = pd.read_csv('./dataset/dataset.csv')
    
    train_valid_df, predict_df = train_test_split(df, test_size=CFG['train']['test_size'], random_state=CFG['seed'])
        
    return train_valid_df, predict_df