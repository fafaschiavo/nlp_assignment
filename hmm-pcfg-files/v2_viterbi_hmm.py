#!/usr/bin/env python
import re
import io
import argparse
from collections import defaultdict, namedtuple
import pandas as pd
import itertools
import math
from tqdm import tqdm
from viterbi_trellis import ViterbiTrellis

def emit_from_concat(digest):
	if digest == 'sentence_boundary':
		return 0
	word = digest.split('_')[0]
	tag = digest.split('_', 1)[1]
	global emits
	return emits[word][tag]

def trans_from_concat(digest1, digest2):
	tag1 = digest1.split('_', 1)[1]
	tag2 = digest2.split('_', 1)[1]
	global trans
	try:
		return trans[tag1][tag2]
	except:
		return -999999
	



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

tokenized_sentences = []
for line in sentences_to_tag:
	current_line = line.split('\n')[0].split(' ')
	tokenized_sentences.append(current_line)

viterbi_matrix = []
viterbi_matrix.append(['sentence_boundary'])
for sentence in tokenized_sentences[:1]:
	for word in sentence:
		possible_tags = list(emits[word].keys())
		concat_list = [word + '_' + tag for tag in possible_tags]
		print concat_list
		viterbi_matrix.append(concat_list)
viterbi_matrix.append(['sentence_boundary'])
print viterbi_matrix

for i in xrange(0,len(viterbi_matrix)):
	for j in xrange(0,len(viterbi_matrix[i])):
		emit_from_concat(viterbi_matrix[i][j])

v = ViterbiTrellis(viterbi_matrix, lambda x: emit_from_concat(x), lambda x, y: trans_from_concat(x, y))
best_path = v.viterbi_best_path()
print best_path

for index in xrange(0,len(best_path)):
	print viterbi_matrix[index][best_path[index]]

# def print_and_return(x):
# 	print '-------'
# 	print x
# 	print '-------'
# 	return x / 2.0

# def print_and_return_2(x, y):
# 	print '======='
# 	print x
# 	print y
# 	print '======='
# 	return abs(y - x)

# v = ViterbiTrellis([[2, 6, 4], [4, 6], [0, 2, 6]], lambda x: print_and_return(x), lambda x, y: print_and_return_2(x, y))
# best_path = v.viterbi_best_path()
# print best_path











