import argparse
import cPickle
import os

from collections import Counter
from tqdm import tqdm

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--qa_split_dir', type=str, default='data/preprocessed/vqa_v2'
    '/qa_split_objattr_answer_3div4_genome_memft_check_all_answer_thres1_50000_thres2_-1_with_seen_answer_in_test',
    help=' ')
config = parser.parse_args()

print('load qid2anno')
qid2anno = cPickle.load(
    open('data/VQA_v2/annotations/qid2anno_trainval2014.pkl', 'rb'))

print('load qa_split')
qa_split = cPickle.load(
    open(os.path.join(config.qa_split_dir, 'qa_split.pkl'), 'rb'))

print('load answer_dict')
answer_dict = cPickle.load(
    open(os.path.join(config.qa_split_dir, 'answer_dict.pkl'), 'rb'))

train_answer_list = answer_dict['vocab'][:answer_dict['num_train_answer']]
train_answer_set = set(train_answer_list)
test_answer_set = set(answer_dict['vocab']) - train_answer_set

test_qid2anno = {}
test_detail_split = {
    'total': [],
    'no_train': [],
    'no_test': [],
}
for qid in tqdm(qa_split['test'], desc='make test_qid2anno'):
    anno = qid2anno[qid]
    answers = [a['answer'] for a in anno['answers']]

    ans_count = Counter(answers)
    ans_score = {a: min(float(c) / 3.0, 1.0) for a, c in ans_count.items()}
    anno['answer_score'] = ans_score
    test_qid2anno[qid] = anno

    test_detail_split['total'].append(qid)
    if len(set(answers) & train_answer_set) == 0:
        test_detail_split['no_train'].append(qid)
    if len(set(answers) & test_answer_set) == 0:
        test_detail_split['no_test'].append(qid)

print('dump test_qid2anno')
cPickle.dump(test_qid2anno,
             open(os.path.join(config.qa_split_dir, 'test_qid2anno.pkl'), 'wb'))
cPickle.dump(test_detail_split,
             open(os.path.join(config.qa_split_dir, 'test_detail_split.pkl'), 'wb'))
print('done')
