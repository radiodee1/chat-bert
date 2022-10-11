#!/usr/bin/env python3.10 

from transformers import BertTokenizer, BertForNextSentencePrediction
import torch
from dotenv import load_dotenv
import argparse
import os 
import transformers 

load_dotenv()

try:
    BATCH_SIZE=int(os.environ['BATCH_SIZE']) 
except:
    BATCH_SIZE = 32

try:
    WORD_FACTOR=int(os.environ['WORD_FACTOR']) 
except:
    WORD_FACTOR = -1

try:
    DOUBLE_COMPARE=int(os.environ['DOUBLE_COMPARE']) 
except:
    DOUBLE_COMPARE = 0

try:
    MAX_LENGTH=int(os.environ['MAX_LENGTH']) 
except:
    MAX_LENGTH = 16

try:
    CUDA=int(os.environ['CUDA']) 
except:
    CUDA = 0

try:
    BERT_MODEL=int(os.environ['BERT_MODEL'])
except:
    BERT_MODEL = 0

try:
    WEIGHT_TEMPLATE=float(os.environ['WEIGHT_TEMPLATE'])
except:
    WEIGHT_TEMPLATE= 1.0

try:
    WEIGHT_PATTERN=float(os.environ['WEIGHT_PATTERN'])
except:
    WEIGHT_PATTERN= 1.0


class Kernel:

    def __init__(self):
        self.verbose = True
        
        parser = argparse.ArgumentParser(description="Bert Chat", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--raw-pattern', action='store_true', help='output all raw patterns.')
        parser.add_argument('--count', action='store_true', help='count number of responses.')
        parser.add_argument('--name', default='calculate', help='name for "count" operation output files.')
        parser.add_argument('--disable-ok', action='store_true', help='disable "ok" operation for BERT output.')
        self.args = parser.parse_args()

        name = [ 'bert-base-uncased', 'bert-large-uncased', 'google/bert_uncased_L-8_H-512_A-8' ]
        index = BERT_MODEL
        self.tokenizer = BertTokenizer.from_pretrained(name[index])
        self.model = BertForNextSentencePrediction.from_pretrained(name[index])
        pass 

    def bert_batch_compare(self, prompt1, prompt2):
        encoding = self.tokenizer(prompt1, prompt2, return_tensors='pt', padding=True, truncation=True, add_special_tokens=True, max_length=MAX_LENGTH)
        #target = torch.LongTensor(self.target)
        target = torch.ones((1,len(prompt1)), dtype=torch.long)
        if CUDA == 1:
            encoding = encoding.to('cuda')
            target = target.to('cuda')

        #outputs = self.model(**encoding, next_sentence_label=target)
        outputs = self.model(**encoding, labels=target)
        logits = outputs.logits.detach()
        #print(outputs, '< logits')
        return logits


if __name__ == '__main__':

    k = Kernel()
    p1 = ["hi there", "hi there", "hello", "this is making no sense", "go to the moon", "1 2 3 ", "4 5 6 ", "do not go."]
    p2 = ["hello",   "hi there", "hello" , "go to the moon", "go to the moon", "4 5 6 ", "1 2 3 ", "don't go."]
    logits = k.bert_batch_compare(p1, p2)
    if self.verbose: 
        print(p1)
        print(p2)
    print(logits)

