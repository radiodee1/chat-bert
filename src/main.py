#!/usr/bin/env python3.10 

from transformers import BertTokenizer, BertForNextSentencePrediction
import torch
from dotenv import load_dotenv
import argparse
import os 
#import transformers
import subprocess 

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
    NUMBER_ROOMS = int(os.environ['NUMBER_ROOMS'])
except:
    NUMBER_ROOMS = 15 

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
        self.text = [ "" for _ in range(NUMBER_ROOMS + 1)]
        self.min = [ 0.0 for _ in range(NUMBER_ROOMS + 1) ]

        self.latest_replies = []
        self.old_userstr = ""

        self.room = 1
        self.oldroom = 0 

        parser = argparse.ArgumentParser(description="Bert Chat", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--response', action='store_true', help='Use response for all calculations.')
        parser.add_argument('--multiplier', action='store_true', help='use multiplier in calculations.')
        parser.add_argument('--folder', default='./../data/', help='folder name for files.')
        parser.add_argument('--list', action='store_true', help='list all possible phrases.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        self.args = parser.parse_args()
        
        self.verbose = self.args.verbose 
        self.list = self.args.list 

        name = [ 'bert-base-uncased', 'bert-large-uncased', 'google/bert_uncased_L-8_H-512_A-8' ]
        index = BERT_MODEL
        self.tokenizer = BertTokenizer.from_pretrained(name[index])
        self.model = BertForNextSentencePrediction.from_pretrained(name[index])
        
        num = 0 
        with open(self.args.folder + '/phrases.txt' , "r") as p:
            for i in p.readlines():
                if i.strip() != "":
                    num += 1 
            self.NUM_PHRASES = num - 1  
            #print(NUM_PHRASES, "NUM_PHRASES")
        pass 

    def bert_find_room(self, userstr):
        p1 = []
        p2 = []
        mult = []
        m1 = []
        logits = []
        if self.old_userstr != userstr:
            self.latest_replies = []

        for i in self.batches:
            p1 = []
            p2 = []
            for ii in i:
                if self.args.response:
                    p1.append(ii['response'])
                    print("response")
                else: 
                    p1.append(ii['phrase'])
                p2.append(userstr)
                mult.append(ii)
            log1 = self.bert_batch_compare(p1, p2)
            logits.extend(log1)
        #print(logits)
        #print(len(logits))

        highest = -1 
        for i in range(len(logits)):
            if self.args.multiplier: 
                m1.append(float(logits[i][0] * mult[i]['multiplier'])) 
            else:
                m1.append(float(logits[i][0]))
            m = float(m1[i])
            if m >= float(self.min[self.room]):
                if m >= float(m1[highest]) and i not in self.latest_replies:
                    highest = i
        if highest == -1:
            if self.verbose:
                print(self.min[self.room], "min")
                print(logits)
                print(m1,"after multiplier")
            #do something here... don't change room.
            return 
        if self.verbose: 
            print(m1)
            print(float(m1[highest]), "highest")
            print(self.room, "old room")
            
        #print(self.room, "room")
        self.latest_replies.append(highest)
        self.old_userstr = userstr 

        response = mult[highest]["response"]
        print(response)
        self.room =  mult[highest]['destination'] 
        if self.room != self.oldroom:
            self.latest_replies = []
            print(self.text[self.room])
        self.oldroom = self.room 
        # launch script...
        number = mult[highest]['number'] + 1 ## <-- all index numbers start with 1
        if int(number) <= 0:
            return 
        self.launch_script(number, userstr)
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

    def launch_script(self, number, userstr):
        name_ending = "_" + ("000" + str(number))[-3:] + ".sh"

        #convert userstr to url-encoded form??
        z = subprocess.call(["bash", self.args.folder + "react" + name_ending, str(self.room), userstr])
        pass 

    def read_phrases_file(self, name='phrases.txt'):
         
        self.rooms = [ [] for _ in range(NUMBER_ROOMS + 1 ) ]
        self.multipliers = [ [] for _ in range(NUMBER_ROOMS + 1 ) ]
        self.responses = [ "" for _ in range(self.NUM_PHRASES + 1 + 1) ]
        self.phrases = [ [] for _ in range(NUMBER_ROOMS + 1)]
        self.destination = [ 1 for _ in range(self.NUM_PHRASES + 1 + 1)]
        self.text = [ "" for _ in range(NUMBER_ROOMS + 1)]

        for i in range(NUMBER_ROOMS):
            self.read_room_file("room", i + 1)
        for i in range(0, self.NUM_PHRASES + 1):
            self.read_response_file(i+ 1)
        for i in range(NUMBER_ROOMS): 
            num = 0  
            with open(self.args.folder + name, 'r') as p:
                phrases = p.readlines()
                for phrase in phrases:
                    lines = phrase.split(";")
                    if  num <= self.NUM_PHRASES + 1 :
                        d = {
                                "phrase": lines[ LINE_PHRASE ].strip(), 
                                "response": lines[ LINE_RESPONSE ].strip(), 
                                "number":num, #  self.rooms[i+1][num+1], 
                                "index": num,
                                "destination": int(lines[ LINE_NUMBER ]), 
                                "multiplier": self.multipliers[i + 1][num +1 ] ## <-- right??
                            }
                        if i < NUMBER_ROOMS + 1:
                            d['response'] = self.responses[num + 1]
                            d['destination'] = self.rooms[i + 1][num +1] 
                        self.phrases[i+1].append(d)
                    num += 1 
        if self.verbose :
            print(self.phrases,'read phrases')
            print(num, "num")
            pass

    def read_room_file(self, rooms_file, number, responses_file="responses"):
        name_ending = "_" + ("000" + str(number))[-3:] + ".txt"

        if self.verbose: 
            print(self.rooms, "room")
            print(self.responses, "responses")
            print(rooms_file + name_ending)
        
        self.multipliers[int(number)].append(1.0)
        num = 0 
        ending = ""
        ending_found = False 
        self.rooms[int(number)].append(1)

        with open(self.args.folder + rooms_file + name_ending, 'r') as p:
            newroom = p.readlines() 
            for room in newroom:
                lines = room.split(';')
                # print(lines)
                if num <= self.NUM_PHRASES + 1 and not ending_found:                     
                    if room.strip() == "" or room.strip().startswith("min:"):
                        #continue 
                        ending_found = True
                    else: 
                        self.rooms[int(number)].append(int(lines[0]))
                        if len(lines) > 1: 
                            self.multipliers[int(number)].append(float(lines[1]))
                        else:
                            self.multipliers[int(number)].append(1.0)
                else:
                    ending_found = True
                if ending_found and not room.strip().startswith("min"):
                    ending += room.strip() + "\n"
                    #print(ending, "ending")
                elif ending_found and room.strip().startswith("min"):
                    self.min[int(number)] = float(room.strip().split(":")[1])
                num += 1 
            if ending.strip().startswith("@"):
                self.text[int(number)] = ending.strip() 
            
            if self.verbose: 
                print(self.rooms, 'rooms')
                print(self.text,"text")
                print(self.multipliers, "multipliers")
                print(self.min, "MIN")
                print(self.phrases[self.room])


    def read_response_file(self, number, responses_file="responses"):
        name_ending = "_" + ("000" + str(number))[-3:] + ".txt"

        num = 0 
        with open(self.args.folder + responses_file + name_ending, "r") as p:
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
                    #print(number, 'number')
                    self.destination[int(number)] = int(r.strip())
                num += 1 
            
            if self.verbose: 
                print(self.responses[int(number)], ":responses")
                print(self.destination[int(number)], "dest")
        
    def process_phrases(self):
        self.batches = []
        b = []
        num = 0
        index = 0 
        for d in self.phrases[self.room]:
            if float(d["multiplier"]) != 0.0: 
                if self.list: 
                    print(d["phrase"],d['destination'])

                d['index'] = index  
                b.append(d)
                if num < BATCH_SIZE:
                    num += 1 
                else: 
                    self.batches.append(b)
                    num = 0 
                    b = []
                #b.append(d)
            index += 1 
        if self.verbose:
            print("store all phrases")
        if len(b) > 0 and len(b) < BATCH_SIZE: 
            pad = []
            for i in range(len(b), BATCH_SIZE):
                pad.append({
                    'phrase': "",
                    'multiplier': 0.0,
                    'response': "",
                    'destination' : 1,
                    'index': -1 
                    })
            if self.verbose: 
                print("must pad batches")
            b.extend(pad)
            self.batches.append(b)
        if self.verbose :
            print(self.batches, 'batches')
            print(b, "b")
         

if __name__ == '__main__':

    k = Kernel()
    k.read_phrases_file()
    
    k.room = 1
    print()
    while True:
        print("room", k.room)
        input_string = input("> ")
        k.process_phrases()
        k.bert_find_room(input_string);

