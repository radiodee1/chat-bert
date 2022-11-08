# GPT-j

GPT-j is used for generating question answer pairs. We found that the bert model was good at figuring out what input sentence went with what output sentence, but this only worked if the programmer thought ahead of time about a given subject. It would be quite possible for the sentences that the programmer used to be narrowly focused on only a very few topics.

For this we generate sentences for the bert implementation by using GPT-j. This is a one-time generating process that takes place at what would be the equivelent of 'build time.' It takes some time. 

We choose a number of sentences between 0 and 1,000. Not all generated sentences are usable. The number of usable sentences can be between 20 and 60. The idea is that this sequence of sentences will provide a padding for the model and make the model more general and usable.

When the bert model sees the same input twice it outputs the same output. This shortcoming is not addressed.
