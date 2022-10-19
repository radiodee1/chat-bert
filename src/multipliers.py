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
    NUMBER_ROOMS = int(os.environ['NUMBER_ROOMS'])
except:
    NUMBER_ROOMS = 15 

LINE_PHRASE = 0
LINE_RESPONSE = 1 
LINE_NUMBER = 2 

ROOM_TEXT = '''
# @ Uncomment this line to use this text as 'room' text. Leave the leading '@' character.
Text will be saved until the end of the file.
'''



class Modify:


    def __init__(self):
        self.verbose = True

        self.phrases = [ [] for _ in range(NUMBER_ROOMS + 1)]
        self.batches = [] 
        self.rooms = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.multipliers = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.responses = [] # [ "" for _ in range(self.NUM_PHRASES + 1) ]
        self.destination = [] # [ 1 for _ in range(self.NUM_PHRASES + 1) ]
        self.text = [ "" for _ in range(NUMBER_ROOMS + 1)]
        self.min = [ 0.0 for _ in range(NUMBER_ROOMS + 1) ]
        self.room = 1
        self.oldroom = 0 

        parser = argparse.ArgumentParser(description="Room Wise Multiplier Update", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--lowest', action='store_true', help='use lowest for base comparison.')
        parser.add_argument('--room', default=1, help='count number of responses.')
        parser.add_argument('--write', action="store_true", help="change file contents")
        parser.add_argument('--folder', default='./../data/', help='folder name for files.')
        parser.add_argument('--list', action='store_true', help='list all possible phrases.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        self.args = parser.parse_args()
        
        self.verbose = self.args.verbose 
        self.room = int(self.args.room)
        self.list = self.args.list 
        self.write = self.args.write 

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



    def bert_stat_room(self):
        p1 = []
        p2 = []
        tot = 0
        mult = []
        m1 = []
        logits = []
        for i in self.batches:
            p1 = []
            p2 = []
            for ii in i: 
                p1.append(ii['phrase'])
                p2.append(ii['phrase'])
                mult.append(ii)
            log1 = self.bert_batch_compare(p1, p2)
            logits.extend(log1)
        print(logits)
        print(len(logits))
        

        highest = -1 
        lowest = -1 
        for i in range(len(logits)):
            
            m1.append(float(logits[i][0]))  
            m = float(m1[i])
            print(m, "mmm")
            tot += m 
            if m <= float(m1[lowest]):
                lowest = i 
            if m >= float(m1[highest]):
                highest = i
        if lowest != -1:
            average = tot / float(len(logits))  
            print(average,'average')
            print(m1[lowest], 'lowest')
            self.min[self.room] = float(m1[lowest]) - (average - float(m1[lowest])) / 2.0 
        if highest != -1: 
            for i in range(len(logits)):
                if not self.args.lowest: 
                    mult[i]['multiplier'] = average / float(m1[i]) # float(m1[highest]) / float(m1[i])
                else:
                    mult[i]['multiplier'] = float(m1[lowest]) / float(m1[i])
        # put multiplier in self.phrases!!
        
        for i in range(len(self.phrases[self.room])):
            z = 1.0 
            ii = i # self.phrases[i]['index']
            for j in range(len(mult)):
                if mult[j]['index'] == ii:
                    z = mult[j]['multiplier']
            if self.phrases[self.room][i]['multiplier'] != 0.0: 
                self.phrases[self.room][i]['multiplier'] = z

        #print some stuff
        if self.verbose:
            print(self.min[self.room], "min")
            print(logits)
            print(mult,"after multiplier")
            print(self.phrases, "phrases")
            #do something here... don't change room.
             
            #if self.verbose: 
            print(m1)
            #print(float(m1[highest]), "highest")
            print(self.room, "old room")
            
        pass 

    def write_room_file(self):
        if not self.write:
            return 
        number = self.room  
        name_ending = "_" + ("000" + str(number))[-3:] + ".txt"
        name = 'room' 
        with open(self.args.folder + "/" + name + name_ending, "w") as room:
            for i in self.phrases[self.room]:
                room.write(str(i['destination']) + ";" + str(i['multiplier']) + ';' + str(i['phrase'].upper()) + "\n")
            room.write('min:' + str(self.min[self.room]) + "\n")
            room.write(ROOM_TEXT + "\n")
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
        self.responses = [ "" for _ in range(self.NUM_PHRASES + 1) ]
        self.phrases = [ [] for _ in range(NUMBER_ROOMS + 1)]
        self.destination = [ 1 for _ in range(self.NUM_PHRASES + 1)]
        self.text = [ "" for _ in range(NUMBER_ROOMS + 1)]

        for i in range(NUMBER_ROOMS):
            self.read_room_file("room", i + 1)
        for i in range(self.NUM_PHRASES):
            self.read_response_file(i+ 1)
        for i in range(NUMBER_ROOMS  ): 
            num = 0 
            with open(self.args.folder + name, 'r') as p:
                phrases = p.readlines()
                for phrase in phrases:
                    lines = phrase.split(";")
                    if  num < self.NUM_PHRASES + 1 :
                        d = {
                                "phrase": lines[ LINE_PHRASE ].strip(), 
                                "response": lines[ LINE_RESPONSE ].strip(), 
                                #"number":  self.rooms[i+1][num+1], 
                                "index": num,
                                "destination": int(lines[ LINE_NUMBER ]), 
                                "multiplier": self.multipliers[i + 1][num] ## <-- right??
                            }
                        if i < NUMBER_ROOMS + 1:
                            d['response'] = self.responses[num ].strip()
                            d['destination'] = self.rooms[i + 1][num] #self.destination[num + 1]
                        self.phrases[i+1].append(d)
                    num += 1 
        if self.verbose :
            print(self.phrases)
            print(num, "num")
            #exit()
            pass

    def read_room_file(self, rooms_file, number, responses_file="responses"):
        name_ending = "_" + ("000" + str(number))[-3:] + ".txt"

        if self.verbose: 
            print(self.rooms, "room")
            print(self.responses, "responses")
            print(rooms_file + name_ending)

        num = 0
        ending = ""
        ending_found = False 
        with open(self.args.folder + rooms_file + name_ending, 'r') as p:
            newroom = p.readlines() 
            for room in newroom:
                lines = room.split(';')
                print(lines)
                if num < self.NUM_PHRASES + 1 and not ending_found:
                    if room.strip() == "" or room.strip().startswith("min:"):
                        continue 
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
            d['index'] = index 
            if float(d["multiplier"]) != 0.0: 
                if self.list: 
                    print(d["phrase"])
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
                    'index': 0 
                    })
            if self.verbose: 
                print("must pad batches")
            b.extend(pad)
            self.batches.append(b)
        if self.verbose:
            print(self.batches, 'batches')
            print(b, "b")
         

if __name__ == '__main__':

    k = Modify() 
    k.read_phrases_file()
    k.process_phrases()
    k.bert_stat_room()
    k.write_room_file()
    print()
 
