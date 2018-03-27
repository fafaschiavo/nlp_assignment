#!/usr/bin/env python
import os
import re
import io
import argparse
from collections import defaultdict, namedtuple
import pandas as pd
import itertools
import math
import numpy as np

sentences_to_tag = io.open('test_sents')
branches_raw = io.open('pcfg')
branches = {}
branches_reversed = {}
for line in branches_raw:
	current_line = line.split('\n')[0].split('	')
	origin = current_line[0]
	endpoints = current_line[1].split(' ')
	probability = current_line[2]
	for endpoint in endpoints:
		if origin not in branches:
			branches[origin] = {}
			branches[origin][endpoint] = probability
		else:
			branches[origin][endpoint] = probability

		if endpoint not in branches_reversed:
			branches_reversed[endpoint] = {}
			branches_reversed[endpoint][origin] = probability
		else:
			branches_reversed[endpoint][origin] = probability

total_origins = list(set(branches_reversed.keys()))
total_amount_of_endpoints = len(total_origins)

tokenized_sentences = []
for line in sentences_to_tag:
	current_line = line.split('\n')[0].split(' ')
	tokenized_sentences.append(current_line)

for sentence in tokenized_sentences[:1]:
	number_of_words = len(sentence)
	pi_matrix = np.zeros((number_of_words, number_of_words, total_amount_of_endpoints))
	print pi_matrix.shape
	for l in xrange(0,number_of_words-1):
		for i in xrange(0,number_of_words-l):
			j = i + l
			for X in total_origins:
				for s in xrange(i,(j-1)):
					pass



# 	print sentence