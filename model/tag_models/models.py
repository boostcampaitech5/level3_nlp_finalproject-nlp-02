import torch
import numpy as np
import torch.nn.functional as F
import pytorch_lightning as pl
import pickle

from utils import metrics
from . import lr_schedule_controller

class Model(pl.LightningModule):
    def __init__(self, LM, tokenizer, CFG):
        super().__init__()
        self.save_hyperparameters()
        self.CFG = CFG

        # 사용할 모델을 호출
        self.LM = LM                            # Language Model
        self.tokenizer = tokenizer              # Tokenizer
        
        self.loss_func = torch.nn.CrossEntropyLoss()
        self.optim = torch.optim.AdamW
        

    def forward(self, input_ids, attention_mask, labels):
        outputs = self.LM(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        return outputs

    def training_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(
            input_ids=x['input_ids'],
            attention_mask=x['attention_mask'],
            labels=x['labels']
        )
        loss = outputs['loss']
        
        self.log("train_loss", loss)

        return loss
    
    # 이하 데이터셋 구축 이후 상세 구현 예정

    def validation_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(
            input_ids=x['input_ids'],
            attention_mask=x['attention_mask'],
            labels=x['labels']
        )
        loss = outputs['loss']
        
        self.log("val_loss", loss)  
        # breakpoint()
        
        # generated_tokens = ''.join([self.tokenizer.convert_ids_to_tokens(sample) for sample in torch.argmax(outputs['logits'], dim=-1)])
        # reference_tokens = ''.join(y)
        
        # self.log("generated_tokens", generated_tokens)
        # self.log("reference_tokens", reference_tokens)
        
        return loss

    def predict_step(self, batch, batch_idx):
        x, y = batch
        breakpoint()
        gened_list = []
        with torch.no_grad():
            for i in x:            
                gened = self.LM.generate(**self.tokenizer(i, return_tensors='pt', return_token_type_ids=False), 
                                        max_new_tokens=256,
                                        early_stopping=True,
                                        do_sample=True,
                                        eos_token_id=2)
                gened_list.append(self.tokenizer.decode(gened[0]))
            
        return gened_list

    def confusion_matrix_inference(self, x):
        outputs = self(
            input_ids=x['input_ids'].to('cuda'),
            attention_mask=x['attention_mask'].to('cuda'),
            token_type_ids=x['token_type_ids'].to('cuda')
        )
        probs = F.softmax(outputs['logits'], dim=-1)
        preds = np.argmax(probs.cpu().detach().numpy(), axis=-1)

        return preds, probs.tolist()

    def configure_optimizers(self):
        optimizer = self.optim(self.parameters(), lr=self.CFG['train']['LR']['lr'])

        if self.CFG['train']['LR']['name'] == 'LambdaLR':
            scheduler = torch.optim.lr_scheduler.LambdaLR(
                optimizer=optimizer,
                lr_lambda=lambda epoch: 0.95 ** epoch,
                last_epoch=-1,
                verbose=False)
        elif self.CFG['train']['LR']['name'] == 'StepLR':
            scheduler = torch.optim.lr_scheduler.StepLR(
                optimizer=optimizer,
                step_size=5,
                gamma=0.3,
                verbose=True)
        elif self.CFG['train']['LR']['name'] == 'CyclicLR':
            scheduler = torch.optim.lr_scheduler.CyclicLR(optimizer, base_lr=self.CFG['train']['LR']['lr'] / self.CFG['train']['LR']['base'], 
                                                          max_lr=self.CFG['train']['LR']['lr'] / self.CFG['train']['LR']['max'], 
                                                          step_size_up=self.CFG['train']['LR']['step_up'], 
                                                          step_size_down=self.CFG['train']['LR']['step_down'], cycle_momentum=False, mode='exp_range')
        elif self.CFG['train']['LR']['name'] == 'ExponentialLR':
            scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer=optimizer, gamma=0.5,verbose=True)
        elif self.CFG['train']['LR']['name'] == 'WarmupConstantLR':
            scheduler = lr_schedule_controller.WarmupConstantLR(optimizer, warmup_steps=self.CFG['train']['LR']['warmupconstantLR_step'])
        elif self.CFG['train']['LR']['name'] == 'WarmupDecayLR':
            scheduler = lr_schedule_controller.WarmupDecayLR(optimizer, warmup_steps=self.CFG['train']['LR']['warmupdecayLR_warmup'], total_steps=self.CFG['train']['LR']['warmupdecayLR_total'])

        
        lr_scheduler = {
            'scheduler': scheduler,
            'interval' : self.CFG['train']['LR']['interval'],
            'name': self.CFG['train']['LR']['name']
        }

        return [optimizer], [lr_scheduler]