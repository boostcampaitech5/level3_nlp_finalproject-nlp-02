import pandas as pd
import torch
import gc
import re
import Levenshtein as lev
import gensim

from tqdm import tqdm
from konlpy.tag import Okt
from gensim.models import Word2Vec, KeyedVectors
from rouge_score import rouge_scorer
from tag_inference import TagModel
from tqdm.auto import tqdm

okt=Okt()
model = gensim.models.Word2Vec.load("ko_blog.bin")

def calculate_jaccard_score(pred: str, gt: str):
    
    return len(set(pred) & set(gt)) / len(set(pred) | set(gt))


def calculate_rouge_score(pred: str, gt: str):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    
    pred = ' '.join(list(pred))
    gt = ' '.join(list(gt))
    
    scores = scorer.score(pred, gt)
    score = (scores['rouge1'].fmeasure + scores['rougeL'].fmeasure) / 2
    
    return score


def calculate_lev_score(pred: str, gt: str):
    score = lev.ratio(pred, gt)
    return score

def w2v_calculate_score(pred: str, gt: str):

    pred = re.sub(r'^#','',pred)
    gt = re.sub(r'^#','',gt)
    pred_morphs = okt.morphs(pred)
    gt_morphs = okt.morphs(gt)
    score_L=[]
    
    for i in gt_morphs:
        if  len(gt_morphs)>1 and len(i)<=1:
            continue
        for j in pred_morphs:
            if len(pred_morphs)>1 and len(j)<=1:
                continue
            try:
                score = model.wv.similarity(i,j)
                if score < 0:
                    score = 0
                elif score > 1:
                    score = 1
                score_L.append(score)
            except:
                score_L.append(0)
                
    if len(score_L)==0:
        score_L.append(0)
    similarity_score = max(score_L)

    return similarity_score


def evaluate(predictions, ground_truths):
    # Step 1: Compute candidate scores
    
    JRL_SCORE = []
    
    for idx, method in enumerate([calculate_jaccard_score, calculate_rouge_score, calculate_lev_score]):
        
        scores_matrix = [[method(pred, gt) for gt in ground_truths] for pred in predictions]

        final_scores = []
        for _ in range(5):
            # Step 2 & 3: Assign prediction-ground truth pairs and avoid double assignments
            max_score = -1
            max_score_index = (-1, -1)
            for i, scores in enumerate(scores_matrix):
                for j, score in enumerate(scores):
                    if score > max_score:
                        max_score = score
                        max_score_index = (i, j)

            # assign the ground truth with maximum score to the prediction
            final_scores.append(max_score)
            pred_index, gt_index = max_score_index

            # remove the scores for the chosen prediction and ground truth
            scores_matrix[pred_index] = [-1] * len(ground_truths)  # invalidates row
            for scores in scores_matrix:
                scores[gt_index] = -1  # invalidates column

        # Step 4: Calculate the final score
        JRL_SCORE.append(sum(final_scores) / len(final_scores))
        
    return JRL_SCORE


if __name__ == "__main__":
    tag_model = TagModel(title = None, content = None)
    
    data = pd.read_csv('./dataset/evaluate/dataset.csv')
    
    gts = data['GT_tag']
    titles = data['title']
    contents = data['content']
    
    preds = []
    
    sanity_check = []
    jaccard_score = []
    rouge_score = []
    lev_score = []
    
    for gt, title, content in tqdm(zip(gts, titles, contents)):
        tag_model.title = title
        tag_model.content = content
        
        pred = tag_model.inference()
        
        torch.cuda.empty_cache()
        gc.collect()
        
        preds.append(pred)
        
        if re.fullmatch(r'\s*#[^\(]+\([^\)]+\),\s*#[^\(]+\([^\)]+\),\s*#[^\(]+\([^\)]+\),\s*#[^\(]+\([^\)]+\),\s*#[^\(]+\([^\)]+\)\s*[,]*', pred):
            sanity_check.append(1)
            
            gt = gt.split(', ')
            pred = pred.split(', ')
            
            scores = evaluate(pred, gt)
            
            jaccard_score.append(scores[0])
            rouge_score.append(scores[1])
            lev_score.append(scores[2])
            
        else:
            sanity_check.append(0)
            
            jaccard_score.append(0)
            rouge_score.append(0)
            lev_score.append(0)
            
            
    data['jaccard_score'] = jaccard_score
    data['rouge_score'] = rouge_score
    data['lev_score'] = lev_score
    data['sanity_check'] = sanity_check
    
    print('average_jaccard_score: ', sum(jaccard_score) / len(jaccard_score))
    print('average_rouge_score: ', sum(rouge_score) / len(rouge_score))
    print('average_lev_score: ', sum(lev_score) / len(lev_score))
    print('average_sanity_checked: ', sum(sanity_check) / len(sanity_check))
    
    data.to_csv('dataset_evaluated.csv', sep=',', na_rep='NaN',index=False)