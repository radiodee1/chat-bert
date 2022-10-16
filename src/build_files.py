#!/usr/bin/env python3.10

import argparse 

class Writer:



    def __init__(self):
        self.verbose = True

        '''
        self.phrases = [ [] for _ in range(NUMBER_ROOMS + 1)]
        self.batches = [] 
        self.rooms = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.multipliers = [ [] for _ in range(NUMBER_ROOMS + 1) ]
        self.responses = [ "" for _ in range(NUMBER_ROOMS + 1) ]
        self.destination = [ 1 for _ in range(NUMBER_ROOMS + 1) ]
        self.room = 1 
        '''

        parser = argparse.ArgumentParser(description="Bert Chat File Maker", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--name', default='./../data/phrases.txt.orig', help='name for "phrases" input file.')
        parser.add_argument('--list', action='store_true', help='list all possible phrases.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        self.args = parser.parse_args()
        
        self.verbose = self.args.verbose 
        self.list = self.args.list 


if __name__ == '__main__':
    w = Writer()


