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
    BATCH_SIZE = 8 # 32 


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
    NUM_PHRASES=int(os.environ['NUM_PHRASES'])
except:
    NUM_PHRASES = 10  

LINE_PHRASE = 0
LINE_RESPONSE = 1 
LINE_NUMBER = 2 
LINE_THRESHOLD = 3 

class Kernel:


    def __init__(self):
        self.verbose = True
        self.phrases = []
        self.batches = [] 

        parser = argparse.ArgumentParser(description="Bert Chat", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--raw-pattern', action='store_true', help='output all raw patterns.')
        parser.add_argument('--count', action='store_true', help='count number of responses.')
        parser.add_argument('--name', default='calculate', help='name for "count" operation output files.')
        parser.add_argument('--disable-ok', action='store_true', help='disable "ok" operation for BERT output.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        self.args = parser.parse_args()
        
        self.verbose = self.args.verbose 

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

    def read_phrases_file(self, name):
        self.phrases = []
        num = 0
        with open('./../data/' + name, 'r') as p:
            phrases = p.readlines()
            for phrase in phrases:
                lines = phrase.split(";")
                if len(lines) == 3 and num < NUM_PHRASES: 
                    d = {
                            "phrase": lines[ LINE_PHRASE ].strip(), 
                            "response": lines[ LINE_RESPONSE ].strip(), 
                            "number": int(lines[ LINE_NUMBER ].strip()),
                            "threshold": 0
                        }
                    self.phrases.append(d)
                    num += 1 
        if self.verbose:
            print(self.phrases)
            print(num, "num")
            pass

    def process_phrases(self):
        self.batches = []
        b = []
        num = 0 
        for d in self.phrases:
            print(d["phrase"])
            if num < BATCH_SIZE:
                num += 1 
            else: 
                self.batches.append(b)
                num = 0 
                b = []
            b.append(d["phrase"])
        if self.verbose:
            print("store all phrases")
        if len(b) > 0 and len(b) < BATCH_SIZE: 
            pad = []
            for i in range(len(b), BATCH_SIZE):
                pad.append("")
            if self.verbose: 
                print("must pad batches")
            b.extend(pad)
            print(b,"b")
            self.batches.append(b)
        if self.verbose:
            print(self.batches) 
         

if __name__ == '__main__':

    k = Kernel()
    p1 = ["hi there", "hi there", "hello", "this is making no sense", "go to the moon", "1 2 3 ", "4 5 6 ", "do not go."]
    p2 = ["hello",   "hi there", "hello" , "go to the moon", "go to the moon", "4 5 6 ", "1 2 3 ", "don't go."]
    logits = k.bert_batch_compare(p1, p2)
    if k.verbose: 
        print(p1)
        print(p2)
        print(logits)
    k.read_phrases_file("phrases.txt")
    p1 = []
    p2 = []
    print("phrases read")
    for d in k.phrases:
        p1.append(d["phrase"])
        p2.append(d["phrase"])
        print(d["phrase"])
    logits = k.bert_batch_compare(p1, p2)
    print(logits)
    k.process_phrases()
         

