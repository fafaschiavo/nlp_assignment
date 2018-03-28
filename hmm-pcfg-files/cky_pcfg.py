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
from math import log10

def get_combination_prob(lefty, righty):
	global branches
	global branches_reversed
	global branches_raw_reversed
	combination_to_find = lefty + ' ' + righty
	if combination_to_find in branches_raw_reversed:
		return branches_raw_reversed[combination_to_find]
	else:
		return False


sentences_to_tag = io.open('test_sents')
branches_raw = io.open('pcfg')
branches = {}
branches_reversed = {}
branches_raw_reversed = {}
for line in branches_raw:
	current_line = line.split('\n')[0].split('	')
	origin = current_line[0]
	endpoints_raw = current_line[1]
	endpoints = current_line[1].split(' ')
	probability = float(current_line[2])

	if endpoints_raw in branches_raw_reversed:
		branches_raw_reversed[endpoints_raw][origin] = probability
	else:
		branches_raw_reversed[endpoints_raw] = {}
		branches_raw_reversed[endpoints_raw][origin] = probability

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
total_words = []
for line in sentences_to_tag:
	current_line = line.split('\n')[0].split(' ')
	tokenized_sentences.append(current_line)
	total_words = total_words + current_line

total_words = list(set(total_words))
total_pre_terminals = []
for word in total_words:
	if word in branches_reversed:
		total_pre_terminals = total_pre_terminals + branches_reversed[word].keys()

total_pre_terminals = list(set(total_pre_terminals))
average_probability_dict = {}
for pre_terminal in total_pre_terminals:
	total = 0
	total_amount = 0
	for key in branches[pre_terminal]:
		current_prob = float(branches[pre_terminal][key])
		current_prob = 10 ** current_prob
		total = total + current_prob
		total_amount = total_amount + 1
	average_prob = total/total_amount
	log_average_prob = log10(average_prob)
	average_probability_dict[pre_terminal] = log_average_prob

for sentence in tokenized_sentences[2:3]:
	number_of_words = len(sentence)
	matrix = [[0 for x in range(number_of_words)] for y in range(number_of_words)]
	pi = [[0 for x in range(number_of_words)] for y in range(number_of_words)]
	for x in xrange(0,number_of_words):
		word = sentence[x]
		if  word in branches_reversed:
			origins = branches_reversed[word]
			print origins
		else:
			origins = average_probability_dict.copy()
		matrix[x][x] = origins.keys()

print number_of_words
s = 2
for s in xrange(2,number_of_words+1):
	for i in xrange(0,number_of_words+1-s):
		j = i + s
		current_parents = []
		for cut in range(i+1,j):
			first_part = [i, cut]
			second_part = [cut, j]
			lefty = matrix[i][cut-1]
			righty = matrix[cut][j-1]

			for left in lefty:
				for right in righty:
					possible_parents = get_combination_prob(left, right)
					current_combination = [left, right]
					if possible_parents:
						current_parents = current_parents + possible_parents.keys()
			
			matrix[i][j-1] = current_parents

			# print lefty
			# print righty
			print '%d %d - cut %d | intervals %s - %s |' % (i, j, cut, str(first_part), str(second_part))
			# print current_parents
			print 'Now processing combinations ... ----------------'
	# 		break
	# 	break
	# break











