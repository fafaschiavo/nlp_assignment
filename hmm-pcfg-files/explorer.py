#!/usr/bin/env python
import re
import io
import argparse
from collections import defaultdict, namedtuple
import pandas as pd
import itertools
import math
from tqdm import tqdm

sentences_to_tag = io.open('dev_sents')

emits_raw = io.open('hmm_emits')
emits = {}
for line in emits_raw:
	current_line = line.split('\n')[0].split('	')
	tag = current_line[0]
	word = current_line[1]
	prob = float(current_line[2])
	if word in emits:
		emits[word][tag] = prob
	else:
		emits[word] = {}
		emits[word][tag] = prob

trans_raw = io.open('hmm_trans')
trans = {}
for line in trans_raw:
	current_line = line.split('\n')[0].split('	')
	first_tag = current_line[0]
	second_tag = current_line[1]
	prob = float(current_line[2])
	if first_tag in trans:
		trans[first_tag][second_tag] = prob
	else:
		trans[first_tag] = {}
		trans[first_tag][second_tag] = prob

total_possible_tags = list(set(list(trans.keys())))
equally_distributed_probability = 1/float(len(total_possible_tags))
equally_distributed_probability = math.log10(equally_distributed_probability)

# use emits and trans (use 'sentence_boundary' for key to sentence beginnig/end)

print emits['w']

tokenized_sentences = []
for line in sentences_to_tag:
	current_line = line.split('\n')[0].split(' ')
	tokenized_sentences.append(current_line)

for sentence in tokenized_sentences:
	sencence_possibilities = []
	total_amount_of_possibilities = 1
	for word in sentence:
		if word in emits:
			sencence_possibilities.append(list(emits[word].keys()))
			total_amount_of_possibilities = total_amount_of_possibilities*len(list(emits[word].keys()))
		else:
			sencence_possibilities.append(total_possible_tags)
			total_amount_of_possibilities = total_amount_of_possibilities*len(total_possible_tags)

	print total_amount_of_possibilities
	combined_possibilities = itertools.product(*sencence_possibilities)

	best_probability_so_far = -99999
	best_combination_so_far = []
	with tqdm(total=total_amount_of_possibilities) as pbar:
		for combination in combined_possibilities:
			pbar.update(10)
			current_probability = 0
			for i in xrange(0,len(sentence)):
				current_pos = combination[i]
				if i != 0:
					previous_pos = combination[i-1]
				else:
					previous_pos = 'sentence_boundary'
				current_word = sentence[i]
				if current_word in emits:
					current_emission = emits[current_word][current_pos]
				else:
					current_emission = equally_distributed_probability

				try:
					current_transmission = trans[previous_pos][current_pos]
				except Exception as e:
					current_probability = -99999
					break				
				current_probability = current_probability + current_emission + current_transmission
				if current_probability < best_probability_so_far:
					break
			
			if current_probability > best_probability_so_far:
				best_probability_so_far = current_probability
				best_combination_so_far = combination

		print best_combination_so_far