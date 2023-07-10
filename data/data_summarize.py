import pandas as pd
import torch
import nltk
import gc

from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

nltk.download('punkt')

df=pd.read_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/0706_Tistory_Context.csv')

print('model and tokenizer build...')
model_dir = "lcw99/t5-large-korean-text-summary"
model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
if torch.cuda.is_available():
    model.to('cuda')
tokenizer = AutoTokenizer.from_pretrained(model_dir)
print('DONE!')

def summarize(x):

    prefix = "summarize: "
    inputs = [prefix + x]
    inputs = tokenizer(inputs, truncation=True, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = inputs.to('cuda')
        gc.collect()
        torch.cuda.empty_cache()
    try:
        output = model.generate(**inputs, num_beams=3, do_sample=True, min_length=80, max_length=140)
        decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        result = nltk.sent_tokenize(decoded_output.strip())[0]
        # print('RESULT >>', result)
        return result
    except IndexError:
        return 'NaN'
    except RuntimeError as e:
        if "CUDA" in str(e):
            # optimizer.zero_grad()
            gc.collect()
            torch.cuda.empty_cache()
            return 'NaN'
        return 'NaN'
n = 2000

for i in range(3,len(df)//n):
  print('---------------------'+str(i*n).zfill(5),str((i+1)*n).zfill(5)+'---------------------')
  df_tmp = df.iloc[i*n:(i+1)*n].copy()
  tqdm.pandas()
  print(len(df_tmp))
  df_tmp['summarize'] = df_tmp['context'].progress_apply(lambda x: summarize(x))
  print('making csv...')
  df_tmp.to_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/Tistory/Tistory_summarize_'+str(i*n).zfill(5)+'.csv', sep=',', na_rep='NaN',index=False) # do not write index
  print('DONE!')

print('---------------------'+str((i+1)*n).zfill(5),str((i+1)*n+(len(df)%n)).zfill(5)+'---------------------')
df_tmp = df.iloc[(i+1)*n:(i+1)*n+(len(df)%n)].copy()
tqdm.pandas()
print(len(df_tmp))
df_tmp['summarize'] = df_tmp['context'].progress_apply(lambda x: summarize(x))
print('making csv...')
df_tmp.to_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/Tistory/Tistory_summarize_'+str((i+1)*n).zfill(5)+'.csv', sep=',', na_rep='NaN',index=False) # do not write index
print('DONE!')