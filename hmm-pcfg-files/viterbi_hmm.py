#!/usr/bin/env python
import re
import io
import argparse
from collections import defaultdict, namedtuple
import pandas as pd
import itertools
import math
from tqdm import tqdm
import copy

class Trellis:
	trell = []
	def __init__(self, emits, trans, words, average_distribution):
		self.trell = []
		self.average_distribution = average_distribution
		temp = {}
		labels = list(set(list(trans.keys())))
		for label in labels:
			temp[label] = [0,None]
		for word in words:
			self.trell.append([word,copy.deepcopy(temp)])
		self.fill_in(emits, trans)

	def fill_in(self, emits, trans):
		for i in range(len(self.trell)):
			for token in self.trell[i][1]:
				word = self.trell[i][0]
				if i == 0:
					if word in emits:
						if token in emits[word]:
							self.trell[i][1][token][0] = emits[word][token]
						else:
							self.trell[i][1][token][0] = -999999
					else:
						self.trell[i][1][token][0] = self.average_distribution
				else:
					max = None
					guess = None
					c = None
					for k in self.trell[i-1][1]:
						if token in trans[k]:
							c = self.trell[i-1][1][k][0] + trans[k][token]
						else:
							c = self.trell[i-1][1][k][0] - 999999
						if max == None or c > max:
							max = c
							guess = k
					if word in emits:
						if token in emits[word]:
							max += emits[word][token]
						else:
							max += -999999
					else:
						max += self.average_distribution

					self.trell[i][1][token][0] = max
					self.trell[i][1][token][1] = guess

	def return_max(self):
		tokens = []
		token = None
		for i in range(len(self.trell)-1,-1,-1):
			if token == None:
				max = None
				guess = None
				for k in self.trell[i][1]:
					if max == None or self.trell[i][1][k][0] > max:
						max = self.trell[i][1][k][0]
						token = self.trell[i][1][k][1]
						guess = k
				tokens.append(guess)
			else:
				tokens.append(token)
				token = self.trell[i][1][token][1]
		tokens.reverse()
		return tokens





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
	words = line.split('\n')[0].split(' ')
	new_trellis = Trellis(emits, trans, words, equally_distributed_probability)
	print new_trellis.return_max()
	break