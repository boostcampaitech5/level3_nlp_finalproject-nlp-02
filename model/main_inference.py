# FOR LORA ONLY

import torch
import gc
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import pytorch_lightning as pl

from transformers import AutoTokenizer, AutoModelForCausalLM
from nltk.translate.bleu_score import sentence_bleu
from tqdm.auto import tqdm
from peft import PeftModel, PeftConfig
from utils import data_controller


if __name__ == "__main__":
    """---Setting---"""

    # config 파일 불러오기
    with open('./config/use_config.yaml') as f:
        CFG = yaml.load(f, Loader=yaml.FullLoader)
    pl.seed_everything(CFG['seed'])

    # base_model, LoRA matrix 불러오기
    LORA_CONFIG = PeftConfig.from_pretrained(CFG['inference']['model_path'])
    base_model = AutoModelForCausalLM.from_pretrained(LORA_CONFIG.base_model_name_or_path,
                                                    torch_dtype=torch.float16,
                                                    low_cpu_mem_usage=True).to(device=f"cuda", non_blocking=True)
    model = PeftModel.from_pretrained(base_model, CFG['inference']['model_path'])
    tokenizer = AutoTokenizer.from_pretrained(LORA_CONFIG.base_model_name_or_path)
    
    breakpoint()
    
    model = model.to('cuda')
    model.eval()
    
    # dataset 불러오기
    dataloader = data_controller.Dataloader(tokenizer, CFG)
    
    generated_tags = []
    reference_tags = []
    
    for sample, tags in tqdm(dataloader.predict_dataset):
        inputs = tokenizer(sample, max_length=CFG['train']['token_max_len'], return_tensors="pt")
        prompt_len = len(inputs['input_ids'][0])
        
        with torch.no_grad():
            outputs = None
            
            outputs = model.generate(input_ids=inputs["input_ids"].to("cuda"), attention_mask = inputs['attention_mask'].to("cuda"), max_new_tokens=100).detach().cpu().numpy()[0][prompt_len:]
            
            print(torch.cuda.memory_allocated())
            print(torch.cuda.memory_reserved())
            
            del inputs
            
            gc.collect()
            torch.cuda.empty_cache()
            
            generated_tags.append(''.join(tokenizer.batch_decode(outputs, skip_special_tokens=True)))
            reference_tags.append(tags)
            
            gc.collect()
            torch.cuda.empty_cache()
            
            del outputs
            
            gc.collect()
            torch.cuda.empty_cache()
            
    df = pd.DataFrame({'generated_tags' : generated_tags,
                       'reference_tags' : reference_tags})
    
    df.to_csv(CFG['inference']['model_path'] + "/inference.csv", encoding = 'utf-8-sig')
