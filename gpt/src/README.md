# GPT MODEL

You must set the environment variables for mystic-ai and pipeline-ai.

```
export GPT_ETC_GPTJ_MODEL="your pipeline-ai token here."
export GPT_ETC_GPTJ_KEY="your pipeline-ai key here"
```

You can test if it's set by executing:

```
echo $GPT_ETC_GPTJ_MODEL 
echo $GPT_ETC_GPTJ_KEY
```

# LLAMA MODEL

LLAMA is from Meta. You need a token from them to run a LLAMA model. This code is supposed to work with Mystic Pipeline, and therefore needs a token from them as well. Tokens are stored in the host `.bashrc` file. The Meta token is called `LLAMA_META` and the pipeline token is called `LLAMA_PIPELINE`.

For the LLAMA_META key, go to 'https://ai.meta.com/llama/' and sign up for one. Then go to 'https://huggingface.co/meta-llama/Llama-2-13b' and apply there also.

For the LLAMA_PIPELINE key, go to 'https://www.mystic.ai/meta/llama2-13B/api' and click on the 'create token' button.
