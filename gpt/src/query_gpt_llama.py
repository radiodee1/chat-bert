#!/usr/bin/env python3

import codecs
import argparse
import sys
import os 
import json 

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

def get_gpt(question, reply):
    prompt = PREPEND + "\n\nHuman: " + question.strip() + "\nJane: " + reply.strip() + "\n\nHuman: "
    if args.short:
        prompt = PREPEND + "\n\nHuman: " + question.strip() + "\nJane: "
    prompt = prompt.replace("Human", args.ident_ques).replace("Jane", args.ident_answ)
    if args.verbose: 
        print("--")
        print(prompt)
    pipeline_token = os.environ['GPT_ETC_GPTJ_MODEL']
    pipeline_key = os.environ['GPT_ETC_GPTJ_KEY']

    llama_meta_key = os.environ['LLAMA_META']
    llama_pipeline_key =  os.environ['LLAMA_PIPELINE']
    llama_model = 'meta/llama2-13B:v7'
    llama_url = 'https://www.mystic.ai/v3/runs'

    llama_headers = {
        'Authorization' : "Bearer " + llama_pipeline_key,
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }

    llama_data = {
	"pipeline_id_or_pointer": llama_model,
	"async_run": False,
	"input_data": 
		[
			{
				"type": "string",
				"value": prompt
			},
			{
				"type": "dictionary",
				"value": {
					"do_sample": False,
					"max_new_tokens": 100,
					"presence_penalty": 1,
					"temperature": args.temperature,
					"top_k": 50,
					"top_p": 0.9,
					"use_cache": True
				}
			}
		]
	} 

    run = requests.request('POST', url=llama_url, headers=llama_headers, data=llama_data)
    #r = run.prepare()
    #s = requests.Session()
    #j = s.send(r)
    
    output = run.text #["result_preview"][0][0]
    if args.verbose:
        print(run)
        print(output)
    if args.short:
        output = "Human: " + question.strip() + "\nJane: " + output 
    output = extract_pairs(output)    
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
    return out_list 

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
parser.add_argument("--temperature", default=0.2, help="Temperature for gpt-j call.")
parser.add_argument("--ident_ques", default="Human", help="Identity string for question.")
parser.add_argument("--ident_answ", default="Jane", help="Identity string for answer.")
args = parser.parse_args()

PREPEND = '''{human}: Hi?
{jane}: Hello there.

{human}: Do you like candy?
{jane}: Yes I like candy.

{human}: What is your favorite color?
{jane}: My favorite color is blue.

{human}: How old are you?
{jane}: I am 21 years old.'''.format(human=args.ident_ques, jane=args.ident_answ)

if __name__ == "__main__":
    gpt_list = []
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
                        gpt_response = get_gpt( question, reply )
                        if check_pair_list(gpt_response, gpt_list):
                            gpt_list.append(gpt_response)
                        else:
                            print(gpt_response)
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
