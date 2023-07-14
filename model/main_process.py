import os
import argparse
import torch
import yaml
import pandas as pd
import pytorch_lightning as pl
import wandb

from tqdm.auto import tqdm
from tag_models.models import Model
from utils import utils, data_controller, print_trainable_parameters, LoRACheckpoint
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.callbacks import LearningRateMonitor
from shutil import copyfile
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model, PeftModel, PeftConfig

import warnings
warnings.filterwarnings('ignore')

if __name__ == "__main__":
    """---Setting---"""
    # argsparse 이용해서 실험명 가져오기
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--exp_name', type=str)
    args = parser.parse_args()
    # args.exp_name이 None이면 assert False라서 에러 발생 시키기
    assert args.exp_name is not None, "실험명을 입력해주세요."
    # config 파일 불러오기
    with open('./config/use_config.yaml') as f:
        CFG = yaml.load(f, Loader=yaml.FullLoader)
    # 실험 결과 파일 생성 및 폴더명 가져오기
    folder_name, save_path = utils.get_folder_name(CFG, args)
    copyfile('use_config.yaml',f"{save_path}/config.yaml")
    pl.seed_everything(CFG['seed'])
    # wandb 설정
    wandb_logger = wandb.init(
        name=folder_name, project="final_project", entity=CFG['wandb']['id'], dir=save_path)
    wandb_logger = WandbLogger()
    wandb_logger.experiment.config.update(CFG)

    """---Train---"""
    # 데이터 로더와 모델 가져오기
    tokenizer = AutoTokenizer.from_pretrained(CFG['train']['model_name'])
    tokenizer.pad_token = tokenizer.eos_token
    #CFG['train']['special_tokens_list'] = utils.get_add_special_tokens()
    #tokenizer.add_special_tokens({
    #    'additional_special_tokens': CFG['train']['special_tokens_list']
    #})
    
    dataloader = data_controller.Dataloader(tokenizer, CFG)
    
    #QLoRA
    if CFG['adapt']['peft'] == 'QLoRA':
        
        bnb_config = bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16)
        
        LM = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=CFG['train']['model_name'],
            quantization_config=bnb_config,
            device_map={"":0},
            low_cpu_mem_usage=True).to(device=f"cuda", non_blocking=True)
        
        LM.gradient_checkpointing_enable()
        LM = prepare_model_for_kbit_training(LM)
        
        peft_config = LoraConfig(r=CFG['adapt']['r'], 
            lora_alpha=CFG['adapt']['r'], 
            target_modules=["query_key_value"], 
            lora_dropout=CFG['adapt']['dropout'], 
            bias="none", 
            task_type="CAUSAL_LM")
        
        LM = get_peft_model(LM, peft_config)
    
    #LoRAFull
    elif CFG['adapt']['peft'] == 'LoRAFull':
        
        LM = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=CFG['train']['model_name'],
            low_cpu_mem_usage=True).to(device=f"cuda", non_blocking=True)
        
    #LoRAfp16
    elif CFG['adapt']['peft'] == 'LoRAfp16':
        
        LM = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=CFG['train']['model_name'],
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True).to(device=f"cuda", non_blocking=True)
        
    #Full-Finetuning
    else:
        
        LM = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=CFG['train']['model_name'],
        low_cpu_mem_usage=True).to(device=f"cuda", non_blocking=True)
    
    print_trainable_parameters(LM)
    
    LM.resize_token_embeddings(len(tokenizer))
    model = Model(LM, tokenizer, CFG)
    
    lr_monitor = LearningRateMonitor(logging_interval='step')
    callbacks = [lr_monitor]
    
    # check point
    checkpoint = ModelCheckpoint(monitor='val_loss',
        save_top_k=CFG['train']['save_top_k'],
        save_last=False,
        save_weights_only=True,
        verbose=True,
        dirpath=f"{save_path}/checkpoints",
        filename="{epoch}-{val_loss:.4f}",
        mode='min') if CFG['adapt']['peft'] == 'original' else \
    LoRACheckpoint(monitor='val_loss',
        save_top_k=CFG['train']['save_top_k'],
        dirpath = f"{save_path}/checkpoints",
        mode = 'min')
    
    callbacks.append(checkpoint)
    
    # Earlystopping
    if CFG['option']['early_stop']:
        early_stopping = EarlyStopping(
            monitor='val_loss', patience=CFG['train']['patience'], mode='max', verbose=True)
        callbacks.append(early_stopping)
    #
    # Trainer
    trainer = pl.Trainer(accelerator='gpu',
                         precision="16-mixed" if CFG['train']['halfprecision'] else 32,
                         accumulate_grad_batches=CFG['train']['gradient_accumulation'],
                         max_epochs=CFG['train']['epoch'],
                         default_root_dir=save_path,
                         log_every_n_steps=1,
                         val_check_interval=0.25,           # 1 epoch 당 valid loss 4번 체크: 학습여부 빠르게 체크
                         logger=wandb_logger,
                         callbacks=callbacks,
                         )

    """---fit---"""

    trainer.fit(model=model, datamodule=dataloader)

    """---Inference---"""
    
    generated_predict = trainer.predict(model=model, datamodule=dataloader)

    """---save---"""
    generated_predict = pd.Series(generated_predict)
    utils.save_csv(generated_predict, save_path, folder_name)

    if checkpoint in callbacks:
        for ckpt_name in tqdm(os.listdir(f"{save_path}/checkpoints"), desc="inferencing_ckpt"):
            print("Now...  "+ ckpt_name)
            
            peft_config = PeftConfig.from_pretrained(ckpt_name)
            model.LM = PeftModel.from_pretrained(model, ckpt_name)

            generated_predict = trainer.redict(model=model, datamodule=dataloader)
            utils.save_csv(generated_predict, save_path, folder_name, ckpt_name.split('-')[-1][:7])