#!/usr/bin/env python3.10

import argparse 

class Writer:



    def __init__(self):
        
        self.verbose = True
        self.phrases = []
        
        parser = argparse.ArgumentParser(description="Bert Chat File Maker", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--name', default='./../data/phrases.txt.orig', help='name for "phrases" input file.')
        parser.add_argument('--list', action='store_true', help='list all possible phrases.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        self.args = parser.parse_args()
        
        self.verbose = self.args.verbose 
        self.list = self.args.list 

    def read_input_file(self):
        with open(self.args.name, "r") as phrases:
            phrase = phrases.readlines()
            for i in phrase:
                p = i.split(";")
                p = [ x.strip() for x in p ]
                self.phrases.append(p)

            pass 
        print(self.phrases)


if __name__ == '__main__':
    w = Writer()
    w.read_input_file()


