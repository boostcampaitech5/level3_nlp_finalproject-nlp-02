# FOR LORA ONLY

import torch
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import pytorch_lightning as pl

from transformers import AutoTokenizer, AutoModel, pipeline, AutoModelForCausalLM
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
    
    model = model.to('cuda')
    model.eval()
    
    # dataset 불러오기
    dataloader = data_controller.Dataloader(tokenizer, CFG)
    
    generated_tags = []
    reference_tags = []
    
    for sample, tags in tqdm(dataloader.predict_dataset):
        inputs = tokenizer(sample, return_tensors="pt")
        prompt_len = len(inputs['input_ids'])
        
        with torch.no_grad():
            outputs = model.generate(input_ids=inputs["input_ids"].to("cuda"), attention_mask = inputs['attention_mask'].to("cuda"), max_new_tokens=100)[prompt_len:]
            
            generated_tags.append(tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0])
            reference_tags.append(tags)
            
    df = pd.DataFrame({'generated_tags' : generated_tags,
                       'reference_tags' : reference_tags})
    
    df.to_csv(CFG['inference']['model_path'] + "_inference.csv", encoding = 'utf-8-sig')
