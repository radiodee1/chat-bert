# GPT-j

GPT-j is used for generating question answer pairs. We found that the bert model was good at figuring out what input sentence went with what output sentence, but this only worked if the programmer thought ahead of time about a given subject. It would be quite possible for the sentences that the programmer used to be narrowly focused on only a very few topics.

For this we generate sentences for the bert implementation by using GPT-j. This is a one-time generating process that takes place at what would be the equivelent of 'build time.' It takes some time. 

We choose a number of sentences between 0 and 1,000. Not all generated sentences are usable. The number of usable sentences can be between 20 and 60. The idea is that this sequence of sentences will provide a padding for the model and make the model more general and usable.

When the bert model sees the same input twice it outputs the same output. This shortcoming is not addressed.

## Concept

First we download a corpus for Movie Dialogs. We separate this into sentences. We use the sentences and some prompt engineering to create a prompt for GPT-j. We send this to the GPT-j api over the internet. We get a single sentence which we test in several ways and also prune to a format that the bert model can use. We do this a number of times, a number between 0 and 1000. The process can take an hour or more. 

## Steps

1. `./do_00_download_database.sh` - This downloads the Movie Dialog Database.
2. `./do_10_make_question.sh` - This does some editing of the text from the Database.
3. `./do_20_query_gpt.sh` - This sends a prompt to the GPT-j instance. It is hard coded for 10 iterations.

## Notes

The `./do_20_query_gpt.sh` script needs to be edited with a number between 1 and 1000. A good value is 500. Alternately you can go to the `./src/` directory and run the `./query_gpt.py` script from there yourself. 

After the program is done you need to edit the output into the `./construct.txt.orig` file in your project.
