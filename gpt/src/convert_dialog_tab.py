#!/usr/bin/env python3

import codecs
import argparse
import sys

def minimal_format(text, do_format):
    if not do_format or len(text) == 0:
        return text
    while (text[0] == " " or text[0] == "." or text[0] == "?" or text[0] == "!") and len(text) > 1:
        text = text[1:]
    if len(text.split(".")) > 1:
        text = text.split(".")[0] + "."
    if len(text.split("?")) > 1:
        text = text.split("?")[0] + "?"
    if len(text.split("!")) > 1:
        text = text.split("!")[0] + "!"
    text = text.strip()
    text = text.split(" ")[:args.tokens]
    text = " ".join(text)
    return text

if len(sys.argv) > 1:
    txtname = sys.argv[1]
    print(txtname)
    print('This first arg should be the path to the movie corpus file.')

parser = argparse.ArgumentParser(description='Make tab file from the movie corpus file.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('basefile', metavar='FILE', type=str, help='Base file from movie corpus for tab output.')
parser.add_argument("--tabname", default="questions.tsv", type=str, help="Resulting tab file name.")
parser.add_argument('--length', default=2000, type=int, help="Length, in sentences, of output file.")
parser.add_argument("--do_format", action="store_true", help="Format or not format.")
parser.add_argument("--tokens", default=50, type=int, help="Default number of tokens in sentences.")
args = parser.parse_args()

if not args.tabname.endswith(".tsv"):
    args.tabname += ".tsv"

if __name__ == "__main__":
    l = []
    num = 0
    f = codecs.open(args.basefile, 'r',encoding='cp1252' ,buffering=1000 ) 
    for x in f:
        y = x.split('+')[-1]
        y = minimal_format(y, args.do_format)
        if not y.lower() in l and len(y) != 0:
            l.append(y)
            num += 1 
            if num == args.length: break

    f.close()
    print(l)
    print(num)

    tab = open("../data/" + args.tabname, "w")
    for i in range(len(l)):
        l[i] = minimal_format(l[i], args.do_format)
        #print(str(i) + ' ', end='')
        tab.write(l[i].strip() + "\t" + str(i).strip() + "\n" )
    tab.close()
