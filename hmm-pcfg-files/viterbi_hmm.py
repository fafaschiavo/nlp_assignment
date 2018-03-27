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

emits['sentence_boundary'] = {}
emits['sentence_boundary']['sentence_boundary'] = 0

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

tokenized_sentences = []
for line in sentences_to_tag:
	current_line = line.split('\n')[0].split(' ')
	tokenized_sentences.append(current_line)

previous_pi = np.asarray([0])
for sentence in tokenized_sentences:
	previous_word = 'sentence_boundary'
	sentence = sentence + ['sentence_boundary']
	matrix_set = []
	for word in sentence:
		try:
			current_word_tags = list(emits[word].keys())
		except Exception as e:
			current_word_tags = total_possible_tags
		
		try:
			previous_word_tags = list(emits[previous_word].keys())
		except Exception as e:
			previous_word_tags = total_possible_tags
		
		local_matrix = np.zeros((len(previous_word_tags), len(current_word_tags)))
		for i in xrange(0,len(previous_word_tags)):
			for j in xrange(0,len(current_word_tags)):

				try:
					transition = trans[previous_word_tags[i]][current_word_tags[j]]
				except Exception as e:
					transition = equally_distributed_probability

				try:
					emission = emits[word][current_word_tags[j]]
				except Exception as e:
					emission = equally_distributed_probability
				
				local_matrix[i][j] = transition + emission

		matrix_set.append(local_matrix.transpose())
		previous_word = word

	chosen_paths = []
	for index in xrange(0,len(matrix_set)):
		current_word_matrix = matrix_set[index]
		current_pi = np.zeros(current_word_matrix.shape[0])

		updated_word_matrix = np.zeros(current_word_matrix.shape)

		for x in xrange(0,current_word_matrix.shape[0]):
			for y in xrange(0,current_word_matrix.shape[1]):
				updated_word_matrix[x][y] = current_word_matrix[x][y] + previous_pi[y]

		possible_path = []
		for x in xrange(0,updated_word_matrix.shape[0]):
			current_pi[x] = np.amax(updated_word_matrix[x])
			possible_path.append(np.argmax(updated_word_matrix[x]))

		chosen_paths.append(possible_path[0])

		previous_pi = current_pi

	best_path = []
	for x in xrange(0,len(sentence)-1):
		try:
			current_word_tags = list(emits[sentence[x]].keys())
		except Exception as e:
			current_word_tags = total_possible_tags
		best_path.append(current_word_tags[chosen_paths[x+1]])

	print ' '.join(best_path)

	if os.path.exists('test_postags'):
		append_write = 'a'
	else:
		append_write = 'w'
	file = open('test_postags', append_write)
	file.write(' '.join(best_path) + '\n')
	file.close()