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

try:
    NUMBER_ROOMS = int(os.environ['NUMBER_ROOMS'])
except:
    NUMBER_ROOMS = 10 

LINE_PHRASE = 0
LINE_RESPONSE = 1 
LINE_NUMBER = 2 

class Kernel:


    def __init__(self):
        self.verbose = True

        self.phrases = [ [] for _ in range(NUMBER_ROOMS + 1)]
        self.batches = [] 
        self.rooms = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.multipliers = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.responses = [ "" for _ in range(NUMBER_ROOMS + 1) ]
        self.destination = [ 1 for _ in range(NUMBER_ROOMS + 1) ]
        self.room = 1 

        parser = argparse.ArgumentParser(description="Bert Chat", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        #parser.add_argument('--raw-pattern', action='store_true', help='output all raw patterns.')
        #parser.add_argument('--count', action='store_true', help='count number of responses.')
        #parser.add_argument('--name', default='calculate', help='name for "count" operation output files.')
        parser.add_argument('--list', action='store_true', help='list all possible phrases.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        self.args = parser.parse_args()
        
        self.verbose = self.args.verbose 
        self.list = self.args.list 

        name = [ 'bert-base-uncased', 'bert-large-uncased', 'google/bert_uncased_L-8_H-512_A-8' ]
        index = BERT_MODEL
        self.tokenizer = BertTokenizer.from_pretrained(name[index])
        self.model = BertForNextSentencePrediction.from_pretrained(name[index])
        pass 

    def bert_find_room(self, userstr):
        p1 = []
        p2 = []
        m1 = []
        for i in self.phrases[self.room]:
            p1.append(i['phrase'])
            p2.append(userstr)
        logits = self.bert_batch_compare(p1, p2)

        highest = 0 
        for i in range(len(logits)):
            #print(logits[i])
            m1.append(logits[i][0] * self.phrases[self.room][i]['multiplier'])
            m = float(m1[i])
            if m > float(m1[highest]):
                highest = i 
        if self.verbose: 
            print(m1)
            print(float(m1[highest]), "highest")
            print(self.room, "old room")
            print(self.phrases, "phrases") 
        print(self.room, "room")
        print(self.phrases[self.room][highest]['response'])
        self.room = self.phrases[self.room][highest]['destination']        
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

    def read_phrases_file(self, name='phrases.txt'):
         
        self.rooms = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.multipliers = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.responses = [ "" for _ in range(NUMBER_ROOMS + 1) ]
        self.phrases = [ [] for _ in range(NUMBER_ROOMS + 1)]
        self.destination = [ 1 for _ in range(NUMBER_ROOMS + 1)]

        for i in range(NUMBER_ROOMS):
            self.read_room_file("room", i + 1)
        for i in range(NUMBER_ROOMS): 
            num = 0 
            with open('./../data/' + name, 'r') as p:
                phrases = p.readlines()
                for phrase in phrases:
                    lines = phrase.split(";")
                    if  num < NUM_PHRASES :
                        d = {
                                "phrase": lines[ LINE_PHRASE ].strip(), 
                                "response": lines[ LINE_RESPONSE ].strip(), 
                                #"number":  self.rooms[i+1][num+1], 
                                "index": num,
                                "destination": int(lines[ LINE_NUMBER ]), 
                                "multiplier": self.multipliers[num + 1][i] ## <-- right??
                            }
                        if i < NUMBER_ROOMS + 1:
                            d['response'] = self.responses[num + 1]
                            d['destination'] = self.destination[num + 1]
                        self.phrases[i+1].append(d)
                    num += 1 
        if self.verbose:
            print(self.phrases)
            print(num, "num")
            pass

    def read_room_file(self, rooms_file, number, responses_file="responses"):
        name_ending = "_" + ("000" + str(number))[-3:] + ".txt"

        if self.verbose: 
            print(self.rooms, "room")
            print(self.responses, "responses")
            print(rooms_file + name_ending)

        num = 0
        with open('./../data/' + rooms_file + name_ending, 'r') as p:
            newroom = p.readlines() 
            for room in newroom:
                lines = room.split(';')
                # print(lines)
                self.rooms[int(number)].append(int(lines[0]))
                if len(lines) > 1: 
                    self.multipliers[int(number)].append(float(lines[1]))
                else:
                    self.multipliers[int(number)].append(1.0)
                num += 1 
            if self.verbose: 
                print(self.rooms, 'rooms')
                print(self.multipliers)

        num = 0 
        with open("./../data/" + responses_file + name_ending, "r") as p:
            response = p.readlines()
            #l = ""
            for r in response:
                #r = r.strip()
                #print(number, r, "response here...")
                if num != 0: 
                    lines = r.strip()
                    #l += lines + "\n"
                    self.responses[int(number)] += lines + "\n"
                else:
                    self.destination[int(number)] = int(r.strip())
                num += 1 
            
            if self.verbose: 
                print(self.responses[int(number)], ":responses")
                print(self.destination[int(number)], "dest")
        
    def process_phrases(self):
        self.batches = []
        b = []
        num = 0 
        for d in self.phrases[self.room]:
            if float(d["multiplier"]) != 0.0: 
                if self.list: 
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
            self.batches.append(b)
        if self.verbose:
            print(self.batches, 'batches')
            print(b, "b")
         

if __name__ == '__main__':

    k = Kernel()
    k.read_phrases_file()
    k.process_phrases()
    k.room = 1
    print()
    while True:
        input_string = input("> ")
        k.bert_find_room(input_string);

