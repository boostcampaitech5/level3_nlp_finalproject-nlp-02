import os
import evaluate
import torch
import numpy as np

from datetime import datetime, timezone, timedelta
from datasets import load_metric

class Printer():
    def __init__(self):
        self.count = 1
        self.order = ''
        self.output = "!LOGGER: {0:<30}"
    
    def start(self, order):
        self.order = order
        print(self.output.format(f"{self.count} Start. >> {self.order}"))

    def done(self):
        print(self.output.format(f"{self.count} Done. >> {self.order}"))
        self.count += 1

def get_folder_name(CFG):
    """
    고유값을 생성해 실험 결과 기록할 폴더를 생성
    """
    now = datetime.now(tz=timezone(timedelta(hours=9)))
    folder_name = f"{now.strftime('%d%H%M%S')}-{CFG['실험명']}"
    save_path = f"./results/{folder_name}"
    CFG['save_path'] = save_path
    os.makedirs(save_path)
    os.makedirs(save_path + '/train')
    os.makedirs(save_path + '/test')
    if 'extract' in CFG['CL']:
        os.makedirs(save_path + '/prediction_train')

    return folder_name, save_path

def compute_metrics(eval_pred):
    rouge_score = load_metric("rouge")
    predictions, labels = eval_pred
    # 생성된 요약을 텍스트로 디코딩
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    # 레이블 내의 -100을 교체한다.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    # 레퍼런스 요약을 텍스트로 디코딩
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    # ROUGE는 각 문장 다음에 개행문자를 요구한다.
    decoded_preds = ["\n".join(sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = ["\n".join(sent_tokenize(label.strip())) for label in decoded_labels]
    # ROUGE 점수 계산
    result = rouge_score.compute(
        predictions=decoded_preds, references=decoded_labels, use_stemmer=True
    )
    # 중간 점수(median scores) 추출
    result = {key: value.mid.fmeasure * 100 for key, value in result.items()}
    return {k: round(v, 4) for k, v in result.items()}

# class NewDataCollator(DataCollatorWithPadding):
#     def __init__(self, tokenizer, pad_to_multiple_of=None):
#         super().__init__(tokenizer, pad_to_multiple_of)

#     def __call__(self, features):
#         batch = super().__call__(features)

#         if "masked_lm_labels" in batch:
#              batch["masked_lm_labels"] = [torch.tensor(label, dtype=torch.long) for label in batch["masked_lm_labels"]]


#         return batch