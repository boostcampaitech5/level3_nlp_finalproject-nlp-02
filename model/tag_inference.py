import re
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from peft import PeftModel, PeftConfig

class TagModel:
    
    def __init__(self, title, content, topics = None, summarized = None, peft_model_id = "snob/TagMyBookmark-KoAlpaca-QLoRA-v1.0", testing = False, quantized = True):
        self.title = title
        self.content = content
        self.topics = topics
        self.summarized = summarized
        self.peft_model_id = peft_model_id
        self.config = PeftConfig.from_pretrained(self.peft_model_id)
        self.testing = testing
        self.quantized = quantized
        self.model, self.tokenizer = self._load_model_and_tokenizer()
        

    def inference(self):
        self.content = self._content_cleaning(self.content)
        
        self.model.eval()
        pipe = pipeline(
            'text-generation', 
            model=self.model,
            tokenizer=self.config.base_model_name_or_path,
            device='cuda'
        )
        
        prompt = self._generate_prompt()
        prompt_truncated = self._truncate_text(prompt, self.tokenizer, max_length=1900)
        
        ans = pipe(
            prompt_truncated, 
            do_sample=False, 
            max_new_tokens=60,
            temperature=0.5,
            top_p=0.5,
            return_full_text=False,
            eos_token_id=2,
        )
        return ans[0]['generated_text']
    
    
    def _content_cleaning(self, content):
        content = content.replace(u"\u200b", u"")
        content = re.sub('\s+', ' ', content)
        content = re.sub('https://.*?\s', '[LINK]', content)
        
        return content
    
    
    def _truncate_text(self, text, tokenizer, max_length):
        tokens = tokenizer.encode(text, truncation=True, max_length=max_length)
        return tokenizer.decode(tokens)
    
    
    def _generate_prompt(self):
        if 'KoAlpaca' in self.peft_model_id:
            
            prompt = f"### Instruction(명령어):\n다음의 블로그 글에 어울리는 태그 5개를 생성하시오. 태그의 형식은 다음과 같음. [#영어(한글), #영어(한글), #영어(한글), #영어(한글), #영어(한글)]\n\n### Input(입력):\n제목은 [{self.title}], 본문은 [{self.content}]이다.\n\n### Response(응답): \n"
            
            return prompt
        
        else:
            raise NotImplemented('Support Only KoAlpaca Model in VER 1.0')
            
            
    def _load_model_and_tokenizer(self):
        if self.quantized:
            bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16)
        
            base_model = AutoModelForCausalLM.from_pretrained(
                self.config.base_model_name_or_path,
                quantization_config=bnb_config,
                # torch_dtype=torch.float16,
                device_map={"":0},
                low_cpu_mem_usage=True)
            
            model = PeftModel.from_pretrained(base_model, self.peft_model_id)
            tokenizer = AutoTokenizer.from_pretrained(self.config.base_model_name_or_path)
            
            model = model.to('cuda')
            
            return model, tokenizer
            
        else:
            raise NotImplemented('Support Only Quantized Model in VER 1.0')
            

# 태그 모델 클래스 미리 호출시켜두기(매번 init하지 않기 위함)
tag_model_instance = TagModel(title=None, content=None)