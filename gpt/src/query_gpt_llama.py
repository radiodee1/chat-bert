#!/usr/bin/env python3

import codecs
import argparse
import sys
import os 
import json
import random

import requests

#from pipeline import PipelineCloud

blacklist = [
        "_",
        "-",
        "*",
        "@",
        ":",
        ";",
        "%",
        "??",
        "..",
        "!!",
        "(",
        ")",
        "-",
        "$",
        "[",
        "]",
        "{",
        "}",
        "~",
        '"',
        "''"
        #"'"
        ]

GPT_NATURAL = 1 
GPT_MECHANICAL = 0 
 

def get_gpt(question, reply, run_num=0):
    prompt = ''
    if run_num == GPT_NATURAL:
        prompt = PREPEND_NATURAL + "\n\nHuman: " + question.strip() + "\nJane: " + reply.strip() + "\n\nHuman: "
    if run_num == GPT_NATURAL and (args.short or args.mechanical):
        prompt = PREPEND_NATURAL + "\n\nHuman: " + question.strip() + "\nJane: "
    
    prompt = prompt.replace("Human", args.ident_ques).replace("Jane", args.ident_answ)
    
    if run_num == GPT_MECHANICAL:
        prompt = PREPEND_QUESTION + shuffle_words(question.strip() + " " + reply.strip())
        if args.short:
            #prompt = PREPEND_QUESTION + shuffle_words(question.strip())
            pass 
    if args.verbose: 
        print("--")
        print(prompt)

    #llama_meta_key = os.environ['LLAMA_META']

    llama_pipeline_key =  os.environ['LLAMA_PIPELINE']
    llama_model = 'meta/llama2-13B:v7'
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
			{
				"type": "string",
				"value": prompt,
			},
			{
				"type": "dictionary",
				"value": {
					"do_sample": False,
					"max_new_tokens": 25,
					"presence_penalty": 1,
					"temperature": args.temperature,
					"top_k": 50,
					"top_p": 0.9,
					"use_cache": True
				}
			}
		]
	} 

    run = requests.request('POST', url=llama_url, headers=llama_headers, data=json.dumps(llama_data))
   
    output = run.json()["result"]['outputs'][0]['value']
    if args.verbose:
        print('response',  run, run_num)
        print(output)
        print(llama_pipeline_key)
        print("--" + prompt + "--")
    if args.short and not args.mechanical:
        output = "Human: " + question.strip() + "\nJane: "  + output 
        pass 
    if not args.mechanical:
        output = extract_pairs(output)   
    if args.mechanical:
        output = extract_question(output)
        output = extract_pairs(output )[0] ## remove identity string
    return output

def extract_pairs(output):
    output = output.split("\n")[0:2]
    out_list = []
    for i in output:
        if i.startswith(args.ident_ques + ":"):
            i = i[len(args.ident_ques + ":"):]
        if i.startswith(args.ident_answ + ":"):
            i = i[len(args.ident_answ + ":"):]
        out_list.append(i.strip())
    print(out_list, "<<<<")
    return out_list 

def extract_question(output):
    line = output.strip().split('\n')[0]
    print(line)
    return line

def shuffle_words(line):
    arr = line.strip().split(' ')
    arr = list(arr)
    random.shuffle(arr)
    new_list = []
    for i in arr:
        x = i[-1]
        if i.lower() in new_list:
            continue 
        if x in ['!', '?', '.']:
            new_list.append(i[0:-1].lower())
        else:
            new_list.append(i.lower())
    x = ' '.join(new_list)
    #x = '"' + x + '"'
    print('x', line, 'x', x, 'x')
    return x

def check_pair_list(output, saved = []):
    skip = False 
    for i in output:
        #print(i[1:], ":capitalize", i )
        if i.strip() == "":
            skip = True
        if len(i) > 2 and i[1:].lower() != i[1:]:
            skip = True
        for j in blacklist:
            if j in i:
                skip = True
        if len(i.split(" ")) <= 1:
            skip = True 
    for i in saved:
        if args.verbose: 
            print(output[0].strip()[:-1], i[0].strip()[:-1])
        if output[0].strip()[:-1] == i[0].strip()[:-1]:
            skip = True 
    return not skip


parser = argparse.ArgumentParser(description='Make file from the movie corpus file.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--verbose', action="store_true", help='Show verbose output.')
parser.add_argument("--tabname", default="./../data/questions.tsv", type=str, help="tab file name.")
parser.add_argument('--length', default=20, type=int, help="Length, in sentence pairs, of output file.")
parser.add_argument("--room", default="2", help="room for entry.")
parser.add_argument("--file", default="./../data/construct.txt.gpt", help="Default sentence output file.")
parser.add_argument("--skip", default=0, help="Start processing at this point.")
parser.add_argument("--short", action="store_true", help="Use shortened input prompt.")
parser.add_argument("--temperature", default=0.2, help="Temperature for gpt call.")
parser.add_argument('--mechanical', action='store_true', help="Build question mechanically using another gpt query.")
parser.add_argument("--ident_ques", default="Human", help="Identity string for question.")
parser.add_argument("--ident_answ", default="Jane", help="Identity string for answer.")
args = parser.parse_args()

PREPEND_NATURAL = '''Answer with the personality designated.

{human}: Hi?
{jane}: Hello there.

{human}: Do you like candy?
{jane}: Yes I like candy.

{human}: What is your favorite color?
{jane}: My favorite color is blue.

{human}: How old are you?
{jane}: I am 21 years old.'''.format(human=args.ident_ques, jane=args.ident_answ)

PREPEND_QUESTION = '''Reorganize the words in the following text to form a question sentence.
Leave out as few words as possible. End the sentence with a question mark.
'''

if __name__ == "__main__":
    if args.mechanical:
        args.short = True 
    num_gpt_passes = 0 
    gpt_list = []
    question = ''
    with open(args.tabname, "r") as r: 
        num = 0 
        lines = r.readlines()
        for line in lines:
            if num < int(args.skip) * 2:
                num += 1 
                continue 
            try: 
                if num % 2 == 0:
                    question = line.split("\t")[0]
                else:
                    reply = line.split("\t")[0]
                    if question.strip() != "" and reply.strip() != "":
                        gpt_response = []
                        if args.mechanical:
                            gpt_question = get_gpt( question, reply, GPT_MECHANICAL )
                            #args.short = True 
                            gpt_answer = get_gpt( gpt_question, reply, GPT_NATURAL )
                            gpt_response = [gpt_question, gpt_answer]
                            if check_pair_list( gpt_response, gpt_list ):
                                gpt_list.append( gpt_response )
                        if not args.mechanical:
                            gpt_response = get_gpt( question, reply, GPT_NATURAL )
                            if check_pair_list(gpt_response, gpt_list):
                                gpt_list.append(gpt_response)
                            
                        print("*" , gpt_response , "*")
                    print("Num:", (num // 2) + 1 ,len(gpt_list))
                if num >= args.length * 2:
                    break
            except: 
                break 
            num += 1 
    if args.verbose:
        print(gpt_list)
    with open(args.file, "w") as w:
        num = 0 
        w.write("room:" + str(args.room) + "\n")
        for line in gpt_list:
            if len(line) > 1:
                w.write(line[0].lower() + ";" + line[1].lower() + ";" + str(-1) + "\n")
                num += 1 
        print("Ending:", num)
