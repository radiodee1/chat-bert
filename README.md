# chat-bert
Using bert for a chatbot

## Steps

1. Write a file in `./data/construct.txt.orig` for defining your chatbot. Include all rooms and all phrases and replies. A sample file is below.

```
room:1
computer assistant; ok assistant; 2
ok computer assistant; ok assistant; 2

room:2
hello ; hello; -1  
how are you; i am fine; -1 
what is your name; my name is jane; -1  
do you like pizza; yes i like pizza; -1  
good bye; later; -1 
what time is it; i don't know; -1
what is your height;  i will tell you my height. just ask;5
ow old are you; i'm twenty years old ;-1
do you like food; no i don't like food;-1 
what would you like for your birthday?;i think it will be tomorrow.;-1
that means the way you think.;i do not know.;-1

room:5
how tall are you; i am five feet tall; -1
how tall; five feet tall; -1
```
Each room is used to define a category or the room in a maze structure. Most lines in the file are separated by semicolons. The lines that describe which room is used are separated by colons. The number after the phrase and response is the number of the room to go to when the particular phrase is detected. If you put a 5 at the end of a line, for example, the chatbot would go to room 5 when that phrase is detected. If you put a 0 or -1 at that spot, there is no change in the room number when the phrase is detected.

2. Go to the `./src/` folder and execute the `./build_files.py` python script. This takes the `./data/construct.txt.orig` file and constructs all the associated room and response files. It also rewrites the `./data/phrases.txt` file. This file contains the information for all other files.

Some of the files can be modified after the `build_files.py` python script. Room files, for example, can be enhanced with a description of the room. Also, the `react_***.sh` files can be edited to contain shell commands that are executed with each phrase recongintion. When running the `build_files.py` script, use the `--write` flag to over-write the construct/room/response/react files that are part of the repository and found in the `data` folder.

3. Go to the `./src/` folder and execute the `./build_multipliers.py` script. You must execute this once for each room, and specify the room with the `--room` flag. You will also want to use the `--write` flag. 

This allows the program to record the `min` variable and store it in the room file. This is not done by the `build_files.py` script. Without the `min` number the program always chooses the highest value for replies. It is desirable somtimes for the program not to pick any response, but to allow the user to try replying again. The `build_multipliers.py` program also constructs the multipliers for each input phrase. This option does not work very well, so it is discouraged or recomended for testing or development.

4. Go to the `./data/` folder and edit the `room` and `react` files.

After the `build_multipliers.py` file is done the files in the folder can be edited by hand. The `build_multipliers.py` file is the last one to edit the output files in place.

