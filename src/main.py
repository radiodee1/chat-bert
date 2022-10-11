#!/usr/bin/env python3.10 

from transformers import BertTokenizer, BertForNextSentencePrediction
import torch
from dotenv import load_dotenv
import argparse
import os 
import transformers 

load_dotenv()

try:
    AIML_DIR=os.environ['AIML_DIR'] 
except:
    AIML_DIR=''

try:
    BATCH_SIZE=int(os.environ['BATCH_SIZE']) 
except:
    BATCH_SIZE = 32

try:
    WORD_FACTOR=int(os.environ['WORD_FACTOR']) 
except:
    WORD_FACTOR = -1

try:
    DOUBLE_COMPARE=int(os.environ['DOUBLE_COMPARE']) 
except:
    DOUBLE_COMPARE = 0

try:
    MAX_LENGTH=int(os.environ['MAX_LENGTH']) 
except:
    MAX_LENGTH = 16

try:
    CUDA=int(os.environ['CUDA']) 
except:
    CUDA = 0

try:
    BERT_MODEL=int(os.environ['BERT_MODEL'])
except:
    BERT_MODEL = 0

try:
    WEIGHT_TEMPLATE=float(os.environ['WEIGHT_TEMPLATE'])
except:
    WEIGHT_TEMPLATE= 1.0

try:
    WEIGHT_PATTERN=float(os.environ['WEIGHT_PATTERN'])
except:
    WEIGHT_PATTERN= 1.0

try:
    AIML_FILE=str(os.environ['AIML_FILE'])
except:
    AIML_FILE = ''

try:
    SRAI_LITERAL=int(os.environ['SRAI_LITERAL'])
except:
    SRAI_LITERAL = 1



print("here")
