### 외부 라이브러리 ###
import os
import yaml
import wandb
import pandas as pd

from datasets import (
    Dataset,
    DatasetDict,
    Features,
    Value,
    load_from_disk
)
from transformers import (
    AutoConfig,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorWithPadding,
    EvalPrediction,
    TrainingArguments,
    set_seed,
    Seq2SeqTrainer
)
from tqdm.auto import tqdm
from shutil import copyfile

### 우리가 만든 라이브러리 ###
from utils import utils, data_controller
from models import *

import warnings
warnings.filterwarnings('ignore')


### MAIN ###
printer = utils.Printer()

# config 불러오기
printer.start('config 불러오기')
with open('config/use/use_config.yaml') as f:
    CFG = yaml.load(f, Loader=yaml.FullLoader)
with open('config/use/use_trainer_args.yaml') as f:
    TRAIN_ARGS = yaml.load(f, Loader=yaml.FullLoader)
printer.done()

# transformers에서 seed 고정하기
printer.start('SEED 고정하기')
set_seed(CFG['seed'])
TRAIN_ARGS['seed'] = CFG['seed']
TRAIN_ARGS['per_device_train_batch_size'] = CFG['option']['batch_size']
printer.done()

if __name__ == "__main__":
    # 실험 폴더 생성
    printer.start('실험 폴더 생성')
    folder_name, save_path = utils.get_folder_name(CFG)
    TRAIN_ARGS['output_dir'] = save_path + "/train"
    printer.done()
    # config 복사
    printer.start("config 저장중...")
    copyfile('config/use/use_config.yaml',save_path+'/use_config.yaml')
    copyfile('config/use/use_trainer_args.yaml',save_path+'/use_trainer_args.yaml')
    printer.done()
    # wandb 설정
    wandb.init(name=folder_name, project=CFG['wandb']['project'], 
               config=CFG, entity=CFG['wandb']['id'], dir=save_path)
    # 데이터셋 가져오기
    printer.start('train/test 데이터셋 가져오기')
    train_dataset = load_from_disk('input/data/datasets/train_dataset')
    printer.done()
    # Trainer의 Args 객체 가져오기
    printer.start('Trainer Args 가져오기')
    training_args = TrainingArguments(**TRAIN_ARGS)
    printer.done()

    # config, tokenizer, model 가져오기
    printer.start('HuggingFace에서 모델 및 토크나이저 가져오기')
    config = AutoConfig.from_pretrained(CFG['model']['model_name'])
    if 'bert' in CFG['model']['model_name'] and 'roberta' not in CFG['model']['model_name']:  # 수정 필요
        config.num_attention_heads = CFG['model']['num_attention_heads']
        config.attention_probs_dropout_prob = CFG['model']['attention_probs_dropout_prob']
        config.num_hidden_layers = CFG['model']['num_hidden_layers']
        config.hidden_dropout_prob = CFG['model']['hidden_dropout_prob']
    tokenizer = AutoTokenizer.from_pretrained(CFG['model']['model_name'], use_fast=True) # rust tokenizer if use_fast == True else python tokenizer
    # model_class = eval(CFG['model']['select_option'][CFG['model']['option']])
    model = AutoModelForSeq2SeqLM.from_pretrained(CFG['model']['model_name'])
    printer.done()

    # 토큰화를 위한 파라미터 설정
    printer.start('토큰화를 위한 파라미터 설정')
    CFG['tokenizer']['max_seq_length'] = min(CFG['tokenizer']['max_seq_length'],
                                             tokenizer.model_max_length)
    fn_kwargs = {
        'tokenizer': tokenizer,
        'pad_on_right': tokenizer.padding_side == "right", # Padding에 대한 옵션을 설정합니다. | (question|context) 혹은 (context|question)로 세팅 가능합니다.
        "CFG": CFG,
    }
    printer.done()
    if training_args.do_train:
        # train/valid 데이터셋 정의
        printer.start('train/valid 데이터셋 정의')
        if CFG['model']['pretrain']:
            aug_df = pd.read_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/' + CFG['model']['pretrain'])
            new_data = Dataset.from_pandas(aug_df)
            train_data = new_data
            print('Pretrain with this new dataset\n\n')
            print(train_data)
        else:
            train_data = train_dataset['train']
            print('finetuning or just train with original dataset')
            print(train_data)
        val_data = train_dataset['validation']
        print(val_data)
        printer.done()

        # 데이터 토큰나이징
        printer.start("train 토크나이징")   #수정
        fn_kwargs['column_names']= train_data.column_names
        train_data = train_data.map(
            data_controller.train_tokenizing,
            batched=True,
            num_proc=None,
            remove_columns=train_data.column_names,
            load_from_cache_file=not False,
            fn_kwargs=fn_kwargs
        )
        printer.done()
        printer.start("val 토크나이징")
        fn_kwargs['column_names']= val_data.column_names
        val_data = val_data.map(
            data_controller.val_tokenizing,
            batched=True,
            num_proc=None,
            remove_columns=val_data.column_names,
            load_from_cache_file=not False,
            fn_kwargs=fn_kwargs
        )
        printer.done()

        # Data collator
        # flag가 True이면 이미 max length로 padding된 상태입니다.
        # 그렇지 않다면 data collator에서 padding을 진행해야합니다.
        data_collator = DataCollatorWithPadding(
            tokenizer, pad_to_multiple_of=8 if training_args.fp16 else None  #수정
        )

        # Trainer 초기화
        printer.start("Trainer 초기화")
        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=train_data,
            eval_dataset=val_data,
            eval_examples=train_dataset["validation"],
            tokenizer=tokenizer,
            data_collator=data_collator,
            post_process_function=post_processing_function,  #수정
            compute_metrics=utils.compute_metrics,  #수정
        )
        printer.done()

        # Training
        printer.start("학습중...")
        train_result = trainer.train()
        trainer.save_model()
        printer.done()
        printer.start("모델 및 metrics 저장")
        metrics = train_result.metrics
        metrics['train_samples'] = len(train_data)

        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)
        trainer.save_state()

        output_train_file = os.path.join(training_args.output_dir, "train_results.txt")

        with open(output_train_file, "w") as writer:
            for key, value in sorted(train_result.metrics.items()):
                writer.write(f"{key} = {value}\n")

        # State 저장
        trainer.state.save_to_json(
            os.path.join(training_args.output_dir, "trainer_state.json")
        )
        printer.done()

        # val 평가
        printer.start("val 평가")
        metrics = trainer.evaluate()

        metrics["val_samples"] = len(val_data)

        trainer.log_metrics("val", metrics)
        trainer.save_metrics("val", metrics)
        printer.done()

    else:
        # Trainer 초기화
        data_collator = DataCollatorWithPadding(
            tokenizer, pad_to_multiple_of=8 if training_args.fp16 else None  #수정
        )
        printer.start("Trainer 초기화")
        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            tokenizer=tokenizer,
            data_collator=data_collator,
            post_process_function=post_processing_function,  #수정
            compute_metrics=utils.compute_metrics,  #수정
        )
        printer.done()

    # predict 단계
    training_args.do_eval = False
    training_args.do_predict = True
    training_args.output_dir = save_path + '/test'
    test_dataset = load_from_disk('input/data/datasets/test_dataset')
    test_data = test_dataset['validation']

    printer.start("test 토크나이징")
    fn_kwargs['column_names']= test_data.column_names
    test_data = test_data.map(
        data_controller.val_tokenizing,
        batched=True,
        num_proc=None,
        remove_columns=test_data.column_names,
        load_from_cache_file=not False,
        fn_kwargs=fn_kwargs
    )
    printer.done()
    printer.start("predict 수행중...")
    predictions = trainer.predict(
        test_dataset=test_data,
        test_examples=test_dataset['validation']
    )
    printer.done()

    print("main_process 끝 ^_^")
