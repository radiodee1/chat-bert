#!/usr/bin/env python3

import codecs
import argparse
import sys
import os 
import json 

from pipeline import PipelineCloud

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
        "}"
        ]

PREPEND = '''Human: Hi?
Jane: Hello there.

Human: Do you like candy?
Jane: Yes I like candy.

Human: What is your favorite color?
Jane: My favorite color is blue.

Human: How old are you?
Jane: I am 21 years old.'''


def get_gpt(question, reply):
    prompt = PREPEND + "\n\nHuman: " + question.strip() + "\nJane: " + reply.strip() + "\n\nHuman: "
    if args.verbose: 
        print("--")
        print(prompt)
    pipeline_token = os.environ['GPT_ETC_GPTJ_MODEL']
    pipeline_key = os.environ['GPT_ETC_GPTJ_KEY']
    #print(pipeline_token, pipeline_key)
    api = PipelineCloud(token=pipeline_key)
    run = api.run_pipeline(
        pipeline_token,
        [
            prompt, # [prompt],
            {
                "response_length": 64,
                "temperature": 1.0,
                "top_k": 50
            },
        ],
    )
    
    output = run["result_preview"][0][0]
    if args.verbose:
        print(output)
    output = extract_pairs(output)    
    return output

def extract_pairs(output):
    output = output.split("\n")[0:2]
    out_list = []
    for i in output:
        if i.startswith("Human:"):
            i = i[len("Human:"):]
        if i.startswith("Jane:"):
            i = i[len("Jane:"):]
        out_list.append(i.strip())
    return out_list 

def check_pair_list(output):
    skip = False 
    for i in output:
        if i.strip() == "":
            skip = True 
        for j in blacklist:
            if j in i:
                skip = True
        if len(i.split(" ")) <= 1:
            skip = True 
    return not skip


parser = argparse.ArgumentParser(description='Make file from the movie corpus file.')
parser.add_argument('--verbose', action="store_true", help='Show verbose output.')
parser.add_argument("--tabname", default="./../data/questions.tsv", type=str, help="tab file name.")
parser.add_argument('--length', default=20, type=int, help="Length, in sentence pairs, of output file.")
parser.add_argument("--room", default="2", help="room for entry.")
parser.add_argument("--file", default="./../data/construct.txt.gpt", help="Default sentence output file.")
args = parser.parse_args()

if __name__ == "__main__":
    gpt_list = []
    with open(args.tabname, "r") as r: 
        num = 0 
        lines = r.readlines()
        for line in lines:
            if num % 2 == 0:
                question = line.split("\t")[0]
            else:
                reply = line.split("\t")[0]
                if question.strip() != "" and reply.strip() != "":
                    gpt_list.append(get_gpt(question, reply))
            if num >= args.length * 2:
                break 
            num += 1 
    if args.verbose:
        print(gpt_list)
    with open(args.file, "w") as w:
        w.write("room:" + str(args.room) + "\n")
        for line in gpt_list:
            if check_pair_list(line):
                w.write(line[0].lower() + ";" + line[1].lower() + ";" + str(-1) + "\n")