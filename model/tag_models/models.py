import torch
import numpy as np
import torch.nn.functional as F
import pytorch_lightning as pl
import pickle

from utils import metrics
from utils.data_controller import load_types2labelnum
from . import lr_schedule_controller

class Model(pl.LightningModule):
    def __init__(self, LM, tokenizer, CFG):
        super().__init__()
        self.save_hyperparameters()
        self.CFG = CFG

        # 사용할 모델을 호출
        self.LM = LM                            # Language Model
        self.tokenizer = tokenizer              # Tokenizer
        
        self.loss_func = torch.nn.CrossEntropyLoss(label_smoothing = self.CFG['train']['lossF']['smooth_scale'])
        self.optim = torch.optim.AdamW
        

    def forward(self, input_ids, attention_mask, token_type_ids):
        outputs = self.LM(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            output_hidden_states=True
        )
        
        return outputs

    def training_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(
            input_ids=x['input_ids'],
            attention_mask=x['attention_mask'],
            token_type_ids=x['token_type_ids']
        )
        loss = self.loss_func(outputs['logits'], y)
        
        self.log("train_loss", loss)

        return loss
    
    # 이하 데이터셋 구축 이후 상세 구현 예정

    def validation_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(
            input_ids=x['input_ids'],
            attention_mask=x['attention_mask'],
            token_type_ids=x['token_type_ids']
        )
        loss = self.loss_func(outputs['logits'], y)
        self.log("val_loss", loss)

        metric = metrics.compute_metrics(
            F.softmax(outputs['logits'], dim=-1), y)
        self.log('val_micro_f1_Score', metric['micro f1 score'])
        self.log('val_AUPRC', metric['auprc'])
        self.log('val_acc', metric['accuracy'])

        return loss

    def predict_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(
            input_ids=x['input_ids'],
            attention_mask=x['attention_mask'],
            token_type_ids=x['token_type_ids']
        )
        probs = F.softmax(outputs['logits'], dim=-1)
        preds = np.argmax(probs.cpu().numpy(), axis=-1)

        return preds, probs.tolist()

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