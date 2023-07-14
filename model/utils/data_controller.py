import re
import pickle
import torch
import yaml
import pandas as pd
import pytorch_lightning as pl

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from transformers import DataCollatorForLanguageModeling
from tqdm import tqdm
# from konlpy.tag import Okt
# from pykospacing import Spacing
# from hanspell import spell_checker
# from pororo import Pororo
# from hangulize import hangulize


class Dataset(Dataset):
    """
    Dataloader에서 불러온 데이터를 Dataset으로 만들기
    """

    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets

    def __getitem__(self, idx):
        inputs = {key: val[idx].clone().detach()
                  for key, val in self.inputs.items()}
        targets = {key: val[idx].clone().detach()
                  for key, val in self.targets.items()}
            
        return inputs, targets
        
    def __len__(self):        
        return len(self.inputs['input_ids'])
        
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
        self.predict_dataset = None

    def tokenizing(self, x):
        
        """ 
        데이터셋 구축 후 구현 예정

        Arguments:
        x: pd.DataFrame

        Returns:
        inputs: Dict({'input_ids', 'labels', 'attention_mask'}), 각 tensor(num_data, max_length)
        """
        
        data_list = [f"### 명령어: {row['instruction']}\n\n### 맥락: {row['input']}\n\n답변: {row['tag1']} {row['tag2']} {row['tag3']} {row['tag4']} {row['tag5']}" for _ , row in x.iterrows()]

        inputs = self.tokenizer(
            data_list,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=self.CFG['train']['token_max_len'],
            add_special_tokens=True,
        )

        return inputs

    def preprocessing(self, x, train=False):
        DC = DataCleaning(self.CFG['select_DC'])
        DA = DataAugmentation(self.CFG['select_DA'])
        tokenizing_method = self.tokenizing

        if train:
            x = DC.process(x)
            x = DA.process(x)         
            
            train_x = x.drop(['label'], axis=1)
            train_y = x['label']
        
            train_x, val_x, train_y, val_y = train_test_split(train_x, train_y,
                                            test_size=self.CFG['train']['test_size'],
                                            shuffle=True,
                                            random_state=self.CFG['seed'])
            
            train_inputs = tokenizing_method(train_x)
            train_targets = tokenizing_method(train_y)

            val_inputs = tokenizing_method(val_x)
            val_targets = tokenizing_method(val_y)     # ([sub_types], [obj_types])

            return (train_inputs, train_targets), (val_inputs, val_targets)
        else:
            x = DC.process(x)
            
            predict_x = x.drop(['label'], axis=1)
            predict_y = x['label']

            # 텍스트 데이터 토큰화
            predict_inputs = tokenizing_method(predict_x)
            predict_targets = tokenizing_method(predict_y)
        
            return (predict_inputs, predict_targets)

    def setup(self, stage='fit'):
        if stage == 'fit':
            # 학습 데이터 준비
            train, val = self.preprocessing(self.train_valid_df, train=True)
            
            self.train_dataset = Dataset(train[0], train[1])
            self.val_dataset = Dataset(val[0], val[1])
        else:
            # 평가 데이터 호출
            predict = self.preprocessing(self.predict_df)
            self.predict_dataset = Dataset(predict[0], predict[1])

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.CFG['train']['batch_size'], shuffle=self.CFG['train']['shuffle'])
    
    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.CFG['train']['batch_size'], shuffle=self.CFG['train']['shuffle'])

    def predict_dataloader(self):
        return DataLoader(self.predict_dataset, batch_size=self.CFG['train']['batch_size'])
    
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