import torch
import pandas as pd
import matplotlib.pyplot as plt

from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
from tqdm.auto import tqdm
from peft import PeftModel, PeftConfig

class TagModel:
    
    def __init__(self, title, context, topics = None, summarized = None, testing = False):
        self.title = title
        self.content = content
        self.topics = topics
        self.summarized = summarized
        
    def inference():
        peft_model_id = "/opt/ml/level3_nlp_finalproject-nlp-02/model/results/07-19_02:51:24_kullm_bs1_lr1e-4_ttc_1600_test/checkpoints/epoch: 4 - loss: 0.5216"
        config = PeftConfig.from_pretrained(peft_model_id)
        
        base_model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        ).to(device=f"cuda", non_blocking=True)
        
        model = PeftModel.from_pretrained(KoAlpaca, peft_model_id)
        tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

        model = model.to('cuda')
        model.eval()
        
        inputs = tokenizer("Instruction(명령어):\n'다음의 블로그 글에 어울리는 태그 5개를 생성하시오. 태그의 형식은 다음과 같음. [#영어(한글), #영어(한글), #영어(한글), #영어(한글), #영어(한글)]'\n\n### Input(입력):\n주제는 [요리·레시피], 제목은 [만들기 쉬운 볶음우동 레시피 굴소스 야끼우동 만들기], 한 줄 요약은 [어묵우동, 김치우동 재료에 따라 사양한 우동을 끓여 먹기도 좋고 사리로 넣어 먹기도 좋은 가성비 좋은 식재료 우동면을 사놓으면 어묵우동, 김치우동 재료에 따라 사리로 넣어 먹기도 좋다.]이다.\n\n### Response(응답): ", return_tensors="pt")

        with torch.no_grad():
            outputs = model.generate(input_ids=inputs["input_ids"].to("cuda"),
                                    attention_mask = inputs['attention_mask'].to("cuda"),
                                    max_new_tokens=60)
            print(tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0])