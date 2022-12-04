#!/usr/bin/env python3.10

import argparse 
import os 
#import shutil 
from dotenv import load_dotenv

try:
    NUMBER_ROOMS = int(os.environ['NUMBER_ROOMS'])
except:
    NUMBER_ROOMS = 15 

ROOM_TEXT = '''
# @ Uncomment this line to use this text as 'room' text. Leave the leading '@' character.
Text will be saved until the end of the file.
'''

REACT_TEXT = '''
# This file is to be executed when a phrase has a response. 

# This text might be helpful for internet searches!!
# google-chrome www.google.com/?q=$2
# x-www-browser www.google.com/?q=$2
# xdg-email
# libreoffice
# echo $@
# echo $0 
'''

class Writer:



    def __init__(self):
        
        self.verbose = True
        self.phrases = []
        self.mixins = [ [ '0' ] for _ in range(NUMBER_ROOMS) ]
        
        parser = argparse.ArgumentParser(description="Bert Chat File Maker", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--folder', default='./../data/', help="folder for all output files.")
        parser.add_argument('--name', default='./../data/construct.txt.orig', help='name for "construct" input file.')
        parser.add_argument('--list', action='store_true', help='list all possible phrases.')
        parser.add_argument('--verbose', action="store_true", help="print verbose output.")
        parser.add_argument('--write', action="store_true", help="change file contents")
        self.args = parser.parse_args()
        
        self.verbose = self.args.verbose 
        self.list = self.args.list 
        self.write = self.args.write 

        if not self.args.name.startswith(self.args.folder):
            self.write = True

    def read_input_file(self):
        room = 1
        mixin = ['0']
        
        with open(self.args.name, "r") as phrases:
            phrase = phrases.readlines()
            for i in phrase:
                skip = False 
                if i.strip() == "" or i.strip().startswith("#"):
                    skip = True
                    #continue 
                if i.strip().startswith("room:"):
                    room = int(i.strip().split(":")[1])
                    skip = True ## do not try to save room number alone
                if i.strip().startswith("mixin:"):
                    mixin = [str(x) for x in i.strip()[len("mixin:"):].strip().split(",")]
                    self.mixins[room] = mixin
                    #print(self.mixins)
                    skip = True
                if not skip:
                    p = i.split(";")
                    p = [ x.strip() for x in p ]
                    p.append(str(room))
                    p.append(','.join(self.mixins[room]))
                    self.phrases.append(p)
        if len(self.mixins[room]) == 0:
            self.mixins[room] = ['0']
            pass
        print(self.phrases)

    def write_output_files(self):
        print(self.args.folder)
        try: 
            s = os.stat(self.args.name)
        except:
            print("stat failure")
            exit()
        if self.write: 
            #shutil.copy(self.args.name, self.args.folder + "/phrases.txt")
            with open(self.args.folder + "/phrases.txt", 'w') as phrases:
                for ii in self.phrases:
                    iii = ';'.join(ii)
                    phrases.write(iii + "\n")

        for i in range(len(self.phrases) ):
            line_ending = "_" + ("000" + str(i + 1))[-3:] + ".txt"
            if self.verbose: 
                print(line_ending)
            if self.write: 
                with open(self.args.folder + "/responses" + line_ending, "w") as responses:
                    responses.write("1\n" + self.phrases[i][1] + "\n")
                line_ending = line_ending.replace('txt','sh')
                with open(self.args.folder + "/react" + line_ending, "w") as react:
                    react.write(REACT_TEXT.strip() + "\n")
                    react.write("# " + self.phrases[i][0] + " - " + self.phrases[i][1] + "\n")
                os.chmod(self.args.folder + "/react" + line_ending, 0o766)
            
        for i in range(NUMBER_ROOMS):
            line_ending = "_" + ("000" + str(i + 1))[-3:] + ".txt"
            #print(line_ending)
            if self.write: 
                with open(self.args.folder + "/room" + line_ending, "w") as rooms:
                    for ii in range(len(self.phrases) ):
                        dest = int(self.phrases[ii][2]) # str(i+ 1)
                        mult = 1.0
                        #print(self.phrases[ii])
                        if i + 1 != int(self.phrases[ii][3]):
                            dest = 0 
                            mult = 0.0
                        if int(self.phrases[ii][2]) <= 0: # and i + 1 == int(self.phrases[ii][3]):
                            dest = int(self.phrases[ii][2])# str(i + 1)
                        rooms.write(str(dest) + ";" + str(mult) + ";" + self.phrases[ii][0].upper() + "\n")
                    rooms.write("min:0.0\n")
                    rooms.write("mixin:" + ','.join(self.mixins[i]) + "\n")
                    rooms.write(ROOM_TEXT + "\n")


if __name__ == '__main__':
    w = Writer()
    w.read_input_file()
    w.write_output_files()

