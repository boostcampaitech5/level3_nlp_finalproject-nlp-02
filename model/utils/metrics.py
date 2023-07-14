import numpy as np
import pickle
import math
from sklearn.metrics import accuracy_score, f1_score, precision_recall_curve, auc


def klue_re_micro_f1(preds, labels):
    """ klue_re_micro_f1
    Note:   no relation 은 제외하고 f1 score를 계산합니다.

    Arguments:
    preds:  (batch, )
    labels: (batch, )

    Return:
    f1 value
    """
    with open('./code/dict_label_to_num.pkl', 'rb') as f:
        label2num = pickle.load(f)
    label_list = list(label2num.keys())

    # print : 0   / no relation은 계산에서 제외한다.
    no_relation_label_idx = label_list.index("no_relation")
    label_indices = list(range(len(label_list)))     # print : [0,1, ..., 29]
    label_indices.remove(no_relation_label_idx)     # print : [1, ..., 29]
    f1 = f1_score(labels, preds, average="micro", labels=label_indices)
    f1 *= 100.0    # 확률로 바꿔주기 위한 100 곱셈

    return f1


def klue_re_auprc(probs, labels, num_labels):
    """ KLUE-RE AUPRC
    Note:   해당 함수는 각각의 label(30개)에 대해 모델이 예측한 probability를 바탕으로 auprc를 계산하는 함수입니다.
            auprc는 x축 recall, y축 precision인 그래프에서의 면적 값을 의미합니다.
            각 클래스에 대한 auprc를 score에 저장한 후, 평균낸 값이 전체 auprc가 됩니다.

            labels의 사이즈를 probs와 맞추기 위해 np.eye를 통해 one-hot encoding으로 변환합니다.

    Arguments:
    probs:  (batch, num_labels)
    labels: (batch,)

    Return:
    average AUPRC score(float)
    """

    labels = np.eye(num_labels)[labels]
    score = np.zeros((num_labels,))     # label 각각에 대한 점수 기록을 위한 빈 numpy

    for c in range(num_labels):
        # axis=1, c 번째 column을 가져와서 1차원 array로 만듦(ravel). 사이즈 = (batch, )
        targets_c = labels.take([c], axis=1).ravel()
        preds_c = probs.take([c], axis=1).ravel()
        precision, recall, _ = precision_recall_curve(targets_c, preds_c)   # 배치 전체에 대한 계산 metric

        # 라벨 c 에 대해서 batch 전체를 가지고 auc 계산.
        score[c] = auc(recall, precision) if not math.isnan(auc(recall, precision)) else 0

    return np.average(score) * 100.0  # 배치 전체에 대해 계산했던 걸 다시 전체 평균


def compute_metrics(outputs, y):
    """ validation을 위한 metrics function
    Note:

    Arguments:
    outputs: 모델 output['logits']값으로부터 softmax가 취해진 값. (batch, num_label)
    y: 정답 값. (batch, )

    Return:
    Dict({'micro f1 score', 'auprc', 'accuracy'})
    """

    labels = y.cpu().detach().numpy()
    preds = outputs.cpu().detach().numpy().argmax(-1)
    probs = outputs.cpu().detach().numpy()   # (batch, num_labels)
    num_labels = outputs.size(-1)            # num_labels

    # calculate accuracy using sklearn's function
    f1 = klue_re_micro_f1(preds, labels)
    auprc = klue_re_auprc(probs, labels, num_labels)
    acc = accuracy_score(labels, preds)  # 리더보드 평가에는 포함되지 않습니다.

    return {
        'micro f1 score': f1,
        'auprc': auprc,
        'accuracy': acc,
    }