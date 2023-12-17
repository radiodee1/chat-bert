#!/usr/bin/env python3 


#from re import S
#from transformers import BertTokenizer, BertForNextSentencePrediction
#import torch
from dotenv import load_dotenv
import argparse
import os 
#import transformers 
#from gpt.src.model import model
import sys
import re 
import json

load_dotenv()

BERT_MODEL_NAME = [
    'bert-base-uncased', 
    'bert-large-uncased', 
    'google/bert_uncased_L-8_H-512_A-8',
    'meta/llama2-13B:latest;single',
    'meta/llama2-13B:latest;batch',
    'meta/llama2-7B:latest;batch',
    'meta/llama2-7B:latest;single'
]


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

if BERT_MODEL <=2:
    import torch
    from transformers import BertTokenizer, BertForNextSentencePrediction
    #import transformers

if BERT_MODEL >= 3: 
    #from gpt.src.model import model
    import requests

try:
    NUMBER_ROOMS = int(os.environ['NUMBER_ROOMS'])
except:
    NUMBER_ROOMS = 15 

LINE_PHRASE = 0
LINE_RESPONSE = 1 
LINE_NUMBER = 2 
LINE_ROOM = 3 
LINE_MIXINS = 4 



ROOM_TEXT = '''
# @ Uncomment this line to use this text as 'room' text. Leave the leading '@' character.
Text will be saved until the end of the file.
'''

PROMPT_LLAMA = '''Return a number between 0 and 1 that shows the similarity of these two sentences, or the
likelyhood that one would follow the other in writing or conversation.
'''

def strip_model_name(name, num, part=0):
    x = name[num].split(';')[part]
    print(x)
    return x 

def model(prompt, length=25, temperature=0.001):
    print("***", *prompt, "***")
    llama_pipeline_key =  os.environ['LLAMA_PIPELINE']
    llama_model = strip_model_name(BERT_MODEL_NAME, BERT_MODEL) #'meta/llama2-13B:latest'
    llama_url = 'https://www.mystic.ai/v3/runs'

    llama_headers = {
        'Authorization' : "Bearer " + llama_pipeline_key,
        'Content-Type': 'application/json',
    }

    llama_data = {
	"pipeline_id_or_pointer": llama_model,
	"async_run": False,
	"input_data": 
		[
		    *prompt,
			{
				"type": "dictionary",
				"value": {
					"do_sample": False,
					"max_new_tokens": length,
					"presence_penalty": 1,
					"temperature": temperature,
					"top_k": 50,
					"top_p": 0.9,
					"use_cache": True,
                    #"CUDA_LAUNCH_BLOCKING":"1"
				}
			}
		]
	} 

    run = requests.request('POST', url=llama_url, headers=llama_headers, data=json.dumps(llama_data))
   
    output = run.json()  #["result"]['outputs'][0]['value']

    return output

class Modify:


    def __init__(self):
        #self.max_room = NUMBER_ROOMS


        parser = argparse.ArgumentParser(description="Room Wise Multiplier Update", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--lowest', action='store_true', help='use lowest for base comparison.')
        parser.add_argument('--room', default=1, help='room number.')
        parser.add_argument('--write', action="store_true", help="change file contents")
        parser.add_argument('--folder', default='./../data/', help='folder name for files.')
        parser.add_argument('--list', action='store_true', help='list all possible phrases.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        parser.add_argument('--name', default='./../data/construct.txt.orig', help='name for "construct" input file.')
        parser.add_argument('--batch', action="store_true", help="operate on all rooms at once.")
        self.args = parser.parse_args()

        self.verbose = True

        self.room_list = []

        self.read_num_rooms()
        
        NUMBER_ROOMS = self.max_room 

        print(NUMBER_ROOMS, self.max_room)

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
        self.mixin_str = ["mixin:0" for _ in range(NUMBER_ROOMS + 1)]

        self.list_len = 0 
        
        self.verbose = self.args.verbose 
        self.room = int(self.args.room)
        self.list = self.args.list 
        self.write = self.args.write 
        self.batch = self.args.batch

        name = BERT_MODEL_NAME

        index = BERT_MODEL
        if index <= 2:
            self.tokenizer = BertTokenizer.from_pretrained(name[index])
            self.model = BertForNextSentencePrediction.from_pretrained(name[index])
        
        num = 0 
        with open(self.args.folder + '/phrases.txt' , "r") as p:
            for i in p.readlines():
                if i.strip() != "":
                    num += 1 
            self.NUM_PHRASES = num - 1  
            print(self.NUM_PHRASES, "NUM_PHRASES")
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
        #print(logits)
        #print(len(logits))
        
        num = 0 
        highest = -1 
        lowest = -1 
        for i in range( len(logits)):
            m1.append(float(logits[i][0]))  
            if num < self.list_len: 
                m = float(m1[i])
                print(m, "mmm", i, self.list_len)
                tot += m 
                if m <= float(m1[lowest]):
                    lowest = i 
                if m >= float(m1[highest]):
                    highest = i
            num += 1 
        if lowest != -1:
            average = tot / float(len(logits))  
            print(average,'average')
            print(m1[lowest], 'lowest', lowest, mult[lowest]['phrase'])
            self.min[self.room] = max(float(m1[lowest]) - ( float(m1[lowest])) / 4.0, 0.0 )
            print("min", self.min[self.room])
        if highest != -1: 
            for i in range(len(logits)):
                if float(m1[i]) == 0.0:
                    m1[i] = 0.00001
                if not self.args.lowest: 
                    mult[i]['multiplier'] = average / float(m1[i]) 
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
            room.write(self.mixin_str[self.room] + "\n")
            room.write("rooms:" + str(','.join([str(i) for i in self.room_list]) + "\n"))
            room.write(ROOM_TEXT + "\n")
        pass 

    def bert_batch_compare(self, prompt1, prompt2):
        logits = [0,0]
        if BERT_MODEL <= 2:
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

        if BERT_MODEL >= 3 and strip_model_name(BERT_MODEL_NAME, BERT_MODEL, 1) == 'single':
            length = 25
            temperature = 0.001
            logits = []
            for i in range(len(prompt1)):
                prompt = PROMPT_LLAMA + 'sentence 1: ' + prompt1[i] + '\nsentence 2: ' + prompt2[i] + '\nSimilarity: '
                prompt_combined = []
                prompt_combined.append(
                    {
                        "type": "string",
                        "value": prompt,
                    }
                )
                #PROMPT_LLAMA + ' ' + prompt1[i] + ' ' + prompt2[i])
                print(prompt_combined)
                logits_individual = model(prompt_combined, length)
                print(logits_individual)
                logits_out = logits_individual['result']['outputs'][0]['value']
                float_list = re.findall(r"[-+]?\d*\.?\d+", logits_out)
                if len(float_list) > 0:
                    float_value = float_list[0]
                else:
                    float_value = 0 
                print(float_value, '<<<<')
                # Convert the float string to a float number
                float_value = float(float_value)
                logits.append([float_value, -1.0 + float_value])

            print(logits)


        if BERT_MODEL >= 3 and strip_model_name(BERT_MODEL_NAME, BERT_MODEL, 1) == 'batch':
            length = 25
            temperature = 0.001
            logits = []
            prompt_combined = []
            for i in range(len(prompt1)):
                prompt = PROMPT_LLAMA  + prompt1[i] + '\n' + prompt2[i]
                
                prompt_combined.append(
                    {
                        "type": "string",
                        "value": prompt,
                    }
                )
                #PROMPT_LLAMA + ' ' + prompt1[i] + ' ' + prompt2[i])
            print(prompt_combined)
            logits_individual = model(prompt_combined, length)
            print(logits_individual)
            logits = logits_individual
            print(logits)

        return logits

    def read_phrases_file(self, name='phrases.txt'):
        

        self.rooms = [ [] for _ in range(self.max_room + 1) ]
        self.multipliers = [ [] for _ in range(self.max_room + 1) ]
        self.responses = [ "" for _ in range(self.NUM_PHRASES + 1) ]
        self.phrases = [ [] for _ in range(self.max_room + 1)]
        self.destination = [ 1 for _ in range(self.NUM_PHRASES + 1)]
        self.text = [ "" for _ in range(self.max_room + 1)]

        for i in range(self.max_room - 0):
            self.read_room_file("room", i + 1)
        #for i in range(self.NUM_PHRASES):
        #    self.read_response_file(i+ 1)
        for i in range(self.max_room - 0): 
            num = 0 
            with open(self.args.folder + name, 'r') as p:
                phrases = p.readlines()
                for phrase in phrases:
                    lines = phrase.split(";")
                    if lines[0].strip() == "" or phrase.strip().startswith("rooms:"):# or i + 1 not in self.room_list:
                        continue
                    if  num < self.NUM_PHRASES + 1 :
                        d = {
                                "phrase": lines[ LINE_PHRASE ].strip(), 
                                "response": lines[ LINE_RESPONSE ].strip(), 
                                #"number":  self.rooms[i+1][num+1], 
                                "index": num,
                                "destination": int(lines[ LINE_NUMBER ]), 
                                #"multiplier": self.multipliers[i + 1][num] ## <-- right??
                            }
                        if i < NUMBER_ROOMS + 1:
                            try:
                                d["multiplier"] = self.multipliers[i+1][num]
                                d['destination'] = self.rooms[i + 1][num] #self.destination[num + 1]
                            except:
                                print(i, num, "indexes")
                                d['multiplier'] = 0.0 
                                

                        self.phrases[i+1].append(d)
                    num += 1 
        if self.verbose :
            print(self.phrases)
            #print(num, "num")
            #exit()
            pass

    def read_num_rooms(self):

        name = self.args.name               
        with open(self.args.folder + name, "r") as phrases:
            phrase = phrases.readlines()
            for i in phrase:
                if i.strip().startswith("room:"):
                    room = int(i.strip().split(":")[1])
                    self.room_list.append(room)
        self.max_room = max(self.room_list)
        print(self.max_room,'- max rooms -', self.args.folder, self.room_list)
 
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
                #print(lines)
                if num < self.NUM_PHRASES + 0 and not ending_found and int(number) <= self.max_room:
                    if room.strip() == "" :
                        ending_found = True
                        num += 1 
                        continue
                    if room.strip().startswith("min:") or room.strip().startswith("mixin:"):
                        ending_found = True
                        #print(num, name_ending, NUMBER_ROOMS)
                        num += 1 
                        continue 
                    self.rooms[int(number)].append(int(lines[0]))
                    #if int(lines[0]) not in self.room_list and int(lines[0]) > 0:
                    #    self.room_list.append(int(lines[0]))
                    if len(lines) > 1: 
                        self.multipliers[int(number)].append(float(lines[1]))
                    else:
                        self.multipliers[int(number)].append(1.0)
                else:
                    ending_found = True
                if ending_found and not room.strip().startswith("min:"):
                    if room.strip().startswith("mixin:"):
                        print(number, room.strip(), self.max_room)
                        self.mixin_str[int(number)] = str(room.strip())
                        
                    else:
                        ending += room.strip() + "\n"
                    #print(ending, "ending")
                elif ending_found and room.strip().startswith("min:"):
                    self.min[int(number)] = float(room.strip().split(":")[1])
                num += 1 
            if ending.strip().startswith("@"):
                self.text[int(number)] = ending.strip() 
            
            if self.verbose: 
                print(self.rooms, 'rooms')
                print(self.text,"text")
                print(self.multipliers, "multipliers")
                print(self.min, "MIN")
            #print(self.room_list, "list")


    def process_phrases(self):
        self.batches = []
        b = []
        num = 0 
        index = 0 
        for d in self.phrases[self.room]:
            d['index'] = index 
            if float(d["multiplier"]) != 0.0: 
                if self.list: 
                    print(d["phrase"], index)
                b.append(d)
                if num < BATCH_SIZE:
                    num += 1 
                else: 
                    self.batches.append(b)
                    num = 0 
                    b = []
                #b.append(d)
            index += 1 
        self.list_len = len(b)
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
    if k.batch:
        for room in k.room_list:
            k.room = room 

            k.read_phrases_file()
            k.process_phrases()
            k.bert_stat_room()
            k.write_room_file()
            print(room ,"completed.")
        exit()

    k.read_phrases_file()
    k.process_phrases()
    k.bert_stat_room()
    k.write_room_file()
    print()
 
