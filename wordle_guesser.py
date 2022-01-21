#!/usr/bin/env python3.6

import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt

## List of possible words from FiveThirtyEight: 
# https://fivethirtyeight.com/features/when-the-riddler-met-wordle/

# Guessable words
# https://docs.google.com/spreadsheets/d/1KR5lsyI60J1Ek6YgJRU2hKsk4iAOWvlPLUWjAZ6m8sg/edit#gid=0
# all_words = pd.read_csv('https://docs.google.com/spreadsheets/d/1KR5lsyI60J1Ek6YgJRU2hKsk4iAOWvlPLUWjAZ6m8sg/gviz/tq?tqx=out:csv&sheet=Sheet1', header=None)[0]

# Hidden words
# https://docs.google.com/spreadsheets/d/1-M0RIVVZqbeh0mZacdAsJyBrLuEmhKUhNaVAI-7pr2Y/edit#gid=0
all_words = pd.read_csv('https://docs.google.com/spreadsheets/d/1-M0RIVVZqbeh0mZacdAsJyBrLuEmhKUhNaVAI-7pr2Y/gviz/tq?tqx=out:csv&sheet=Sheet1', header=None)[0]

# from https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html
#letters_ordered = ['e','t','a','i','n','o','s','h','r','d','l','u','c','m','f','w','y','g','p','b','v','k','q','j','x','z']
#letters_ordered = ['e','a','r','i','o','t','n','s','l','c','u','d','p','m','h','g','b','f','y','w','k','v','x','z','j','q']
letter_freq = {'e': 56.88, 'a': 43.31, 'r': 38.64, 'i': 38.45, 'o': 36.51, 't': 35.43, 
               'n': 33.92, 's': 29.23, 'l': 27.98, 'c': 23.13, 'u': 18.51, 'd': 17.25, 
               'p': 16.14, 'm': 15.36, 'h': 15.31, 'g': 12.59, 'b': 10.56, 'f': 9.24, 
               'y': 9.06, 'w': 6.57, 'k': 5.61, 'v': 5.13, 'x': 1.48, 'z': 1.39, 'j': 1.00, 'q': 1.00}


def remaining_words(prior_guesses, prior_res):
    """
    remaining_words returns a list of possible remaining words that are consistent with the results (feedback)
    returned by wordle for any previous guesses.

    :prior_guesses: list of 5-character strings representing previous guesses
    :prior_res: list of feedback strings for previous guesses (in the same order as prior_guesses)
    :return: list of remaining words
    """     
    # Table with known information about each letter and the response from prior guesses
    know = pd.DataFrame({ 'letter': list(''.join(prior_guesses)),
                          'response': list(''.join(prior_res)),
                          'position': list(np.arange(1,6)) * len(prior_guesses)
                         })  
    
    # Excluded and yellow letters (excluded letters not counted if they also show up as green somewhere)
    excluded_letters = [l for l in list(know[know['response']=='x']['letter'].unique()) if l not in list(know[know['response']=='g']['letter'].unique())]
    yellow_letters = list(know[know['response']=='y']['letter'].unique())
    
    # Only words that don't contain excluded letters
    rm = [w for w in all_words if not any(l in w for l in excluded_letters)]
    
    # Only words that contain all yellow letters
    rm = [w for w in rm if (yellow_letters == []) | all(l in w for l in yellow_letters)]
    
    ## Only words that have green letters in the right place
    # positions with known letter
    green_pos = know[know['response']=='g'].groupby('position', as_index=False).max()[['position','letter']]

    # For each known position, filter only words that have the right letter in that position
    for p, l in green_pos.itertuples(index=False):
        rm = [w for w in rm if w[p-1] == l]    
        
    ## Only words that don't have yellow letters in the same place as previously
    # positions with yellow letter
    yellow_pos = know[know['response']=='y'].groupby(['position','letter'], as_index=False).max()[['position','letter']]

    # For each known position, filter only words that don't have the yellow letter in that position
    for p, l in yellow_pos.itertuples(index=False):
        rm = [w for w in rm if w[p-1] != l]         
        
    # Exclude words that were alrady tried
    rm = [w for w in rm if w not in prior_guesses]
    
    # Add word score and number of unique letters and return as randomized dataframe
    rm = pd.DataFrame({'word': rm})
    rm['unique_letters'] = rm['word'].map(lambda x: len(set(x)))
    rm = rm.sample(frac = 1.)
        
    return rm


def word_score(word):
    """
    word_score calculates a score based on letter frequencies. High score indicates a word with many
    common letters.

    :word: string 
    :return: score
    """      
    word_score = 0
    for c in word:
        word_score += letter_freq[c]
    return word_score


def suggest_next_random(prior_guesses, prior_res):
    """
    suggest_next_random suggests a next guess by randomly choosing from the list of remaining words

    :prior_guesses: list of 5-character strings representing previous guesses
    :prior_res: list of feedback strings for previous guesses (in the same order as prior_guesses)
    :return: suggested next guess (string)
    """  
    return remaining_words(prior_guesses, prior_res).sample(frac = 1.).iloc[0,0]


def suggest_next_by_score(prior_guesses, prior_res):
    """
    suggest_next_by_score suggests a next guess by choosing the word with the highest
    word score from the list of remaining words

    :prior_guesses: list of 5-character strings representing previous guesses
    :prior_res: list of feedback strings for previous guesses (in the same order as prior_guesses)
    :return: suggested next guess (string)
    """  
    suggest = remaining_words(prior_guesses, prior_res)
    suggest['score'] = suggest['word'].map(word_score)
    return suggest.sort_values('score', ascending=False).iloc[0,0]

# Initialize guesses and results (feedback)
guesses = ['irate']
res = []
print('Attempt 1:', guesses[-1])

# Get feedback up to 12 times and suggest next guess
for n_attempt in np.arange(12):
    res.append(input())  # Ask for feedback
    
    if res[-1] in ['exit','ggggg']:
        quit()
    
    guesses.append(suggest_next_random(guesses, res))
        
    print('Attempt 2:', guesses[-1])