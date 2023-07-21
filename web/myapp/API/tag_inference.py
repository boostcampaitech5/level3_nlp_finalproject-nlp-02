import re
import torch
import pandas as pd
import matplotlib.pyplot as plt

from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
from tqdm.auto import tqdm
from peft import PeftModel, PeftConfig

class TagModel:
    
    def __init__(self, title, content, topics = None, summarized = None, testing = False):
        self.title = title
        self.content = self._content_cleaning(content)
        self.topics = topics
        self.summarized = summarized

        
    def inference(self):
        
        # peft_model_id는 admin에서 접근 가능하도록 구현할 예정
        peft_model_id = "/opt/ml/level3_nlp_finalproject-nlp-02/model/results/07-19_02:51:24_kullm_bs1_lr1e-4_ttc_1600_test/checkpoints/epoch: 4 - loss: 0.5216"
        config = PeftConfig.from_pretrained(peft_model_id)
        
        base_model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        ).to(device=f"cuda", non_blocking=True)
        
        model = PeftModel.from_pretrained(base_model, peft_model_id)
        tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

        model = model.to('cuda')
        model.eval()
        
        inputs = tokenizer(f"Instruction(명령어):\n'다음의 블로그 글에 어울리는 태그 5개를 생성하시오. 태그의 형식은 다음과 같음. [#영어(한글), #영어(한글), #영어(한글), #영어(한글), #영어(한글)]'\n\n### Input(입력):\n주제는 [{self.topics}], 제목은 [{self.title}], 본문은 [{self.content}]이다.\n\n### Response(응답): ", return_tensors="pt")

        with torch.no_grad():
            outputs = model.generate(input_ids=inputs["input_ids"].to("cuda"),
                                    attention_mask = inputs['attention_mask'].to("cuda"),
                                    max_new_tokens=60)
            
            return tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0]
        
        
    def _content_cleaning(content):
        
        content = content.replace(u"\u200b", u"")
        content = re.sub('\s+', ' ', content)
        content = re.sub('https://.*?\s', '[LINK]', content)
        
        return content