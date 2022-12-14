# Sample `construct.txt.orig` File Explained:

```
# these lines are strictly literal. Notice that
# asterisks replace empty spaces in the question
# string. 

room:1
mixin:0 
*chat*bert*; ok assistant; 2
*bert*; ok assistant; 2

# these lines are conversational. They
# are at the center of this bot.

room:2
mixin:3 
read the mail; ok mail; -1
write a text file; ok writer; -1
tell me about this; internet ok; -1
search the internet for this; internet ok; -1
stop; ok; 1
exit; ok; 1

# this, below, is the 'mixin' room listing...
# in the example implementation this room is populated by the 
# gpt-j content. In the example the room is comprised of many pairs.

room:3
mixin:0
how are you; i am fine; -1 
what is your name; my name is jane; -1  
do you like pizza; yes i like pizza; -1  
good bye; later; -1 
what time is it; i don't know; -1
what is your height;  i will tell you my height. just ask again;5
ow old are you; i'm twenty years old ;-1

# below, these lines are non-sensical
# but the content of this room shows how a topic
# might be isolated to any given room.

room:5
mixin:3
how tall are you; i am five feet tall; -1
how tall; five feet tall; -1
what is your height; five feet tall; -1 
stop; ok; 2 
exit; ok; 2 
```

1. There are four rooms in this example. They are 1, 2, 3, and 5. Rooms are collections of question/answer pairs.
2. Each room group has the keyword 'room' that it starts with. The rooms need not be in any order.
3. The room keyword is followed by the 'mixin' keyword. Here a mixin identifies a group of question/answer pairs that are included with the room in question. 'Mixins' are not recursive, but you can include more than one. Many mixin room numbers can be on the same mixin line, and duplicates are ignored.
4. A question/answer pair is separated by semicolons and followed by a final semicolon and a number. 
5. If the number at the end of the question/answer pair is -1 or 0 and the question matches the user input question, there will be no room number change at the end of the turn. If the room is higher than 0, then the room number changes when and if the user input is matched.
6. White-space between rooms is ignored.
7. Full-line comments are allowed. They follow the '#' symbol. Partial-line comments are not supported.
8. The first question/answer pair is an example of a literal input. In that case the program will look for a user input that is _exactly_ the same as the supplied string. A literal input is denoted by replacing spaces in the phrase with asterisks. If there is at least one asterisk on the line with the input, the string or phrase will match that string only in the user input. In this example, if the user is in room 1 and types 'chat bert' the user is dropped in room 2. The input from the user must match exactly.

# Additional Notes:

* There are two keywords. They are 'room' and 'mixin'. They are separated from their values by a colon.

* Sentence pairs are separated by a semicolon, and followed by a semicolon and a number. The number is the room number to branch to when or if the first sentence in the pair matches the input sentence.

* The default number of rooms allowed span from '1' to '15'. This can be changed in the `.env` file.

* There is, for every sentence pair, a `react_***.sh` file. When the sentence pair is chosen the react file is run in the bash shell. This react file can be used for any shell scripting. You can start desktop programs. You can also, for example, run a 'curl' command that interacts with a distant server. You might use this for services like ITTT. Though it has not been tested, you might use the file to turn on or off household lights or appliances.

* When the react file is run, the main.py program passes some information to the script. This info includes the room number and some other info.
