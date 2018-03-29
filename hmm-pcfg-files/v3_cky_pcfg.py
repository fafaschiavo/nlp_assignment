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
from collections import defaultdict

def q(x, y1, y2):
	global nonterminal_prob
	return nonterminal_prob[x][y1][y2]

def q_unary(x, w):
	global terminal_prob
	return terminal_prob[x][w]

def recover_tree(x, bp, i, j, X):
	if i == j:
		return [X, x[i]]
	else:
		Y, Z, s = bp[i, j, X]
		return [X, recover_tree(x, bp, i, s, Y), recover_tree(x, bp, s+1, j, Z)]

sentences_to_tag = io.open('test_sents')
branches_raw = io.open('pcfg')
nonterminal_prob = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
terminal_prob = defaultdict(lambda: defaultdict(float))

N = []
E = []
binary_rules = {}
for line in branches_raw:
	current_line = line.split('\n')[0].split('	')
	origin = current_line[0]
	endpoints_raw = current_line[1]
	endpoints = current_line[1].split(' ')
	probability = float(current_line[2])
	probability = 10 ** probability

	if len(endpoints) == 2:
		N = N + endpoints
		nonterminal_prob[origin][endpoints[0]][endpoints[1]] = float(probability)
		if origin in binary_rules:
			binary_rules[origin].append([endpoints[0], endpoints[1]])
		else:
			binary_rules[origin] = [[endpoints[0], endpoints[1]]]
	else:
		E = E + endpoints
		terminal_prob[origin][endpoints[0]] = float(probability)

N = list(set(N))
E = list(set(E))

tokenized_sentences = []
for line in sentences_to_tag:
	current_line = line.split('\n')[0].split(' ')
	tokenized_sentences.append(current_line)

# N - Total non-terminal (non-words) array
# E - Toal terminal (words) array
# x - sentence
for x in tokenized_sentences[2:3]:
	n = len(x)
	pi = defaultdict(float)
	bp = {}

	# pass_by_check = [[0 for j in xrange(n)] for i in xrange(n)]

	for i in xrange(n):
		w = x[i]
		for X in N:
			pi[i, i, X] = q_unary(X, w)

	for l in xrange(1, n):
		for i in xrange(n-l):
			j = i + l
			for X in N:
				max_score = 0
				args = None
				if X in binary_rules:
					for rule in binary_rules[X]:
						Y, Z = rule
						for s in xrange(i, j):
							if pi[i, s, Y] and pi[s + 1, j, Z]:
								score = q(X, Y, Z) * pi[i, s, Y] * pi[s + 1, j, Z]
								if score > max_score:
									max_score = score
									args = Y, Z, s
				if max_score:
					pi[i, j, X] = max_score
					bp[i, j, X] = args


	# for key in pi:
	# 	if key[0] == 0 and key[1] == (n-1):
	# 		# print '%d | %d' % (key[0], key[1])
	# 		print key[2]

	# for line in pass_by_check:
	# 	print line


	if pi[0, n-1, 'S']:
		print 'There you go...'
		print recover_tree(x, bp, 0, n-1, 'S')
	else:
		max_score = 0
		args = None
		for X in N:
			if max_score < pi[0, n-1, X]:
				max_score = pi[0, n-1, X]
				args = 0, n-1, X
		print 'There you go...'
		print recover_tree(x, bp, *args)


