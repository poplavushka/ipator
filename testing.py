import csv
import numpy as np

#consonants

with open('cons.csv', 'r', encoding='utf8') as consf:
    reader = csv.reader(consf)
    rows = list(reader)
    consonant_questions = dict(zip(rows[0][2:], rows[1][2:]))
    consonants = []
    firstrow = rows[0]
    representation = {}
    for row in rows[2:]:
      answers =  dict(zip(firstrow[2:], row[2:]))
      consonants.append({'name': row[0], 'answers': answers})
    for row in rows[2:]:
        representation[row[0]] = row[1]

#vowels

with open('vowels.csv', 'r', encoding='utf8') as vowsf:
    reader_v = csv.reader(vowsf)
    rows_v = list(reader_v)
    vow_questions = dict(zip(rows_v[0][2:], rows_v[1][2:]))
    vowels = []
    firstrow_v = rows_v[0]
    representation = {}
    for row_v in rows_v[2:]:
      answers =  dict(zip(firstrow_v[2:], row_v[2:]))
      vowels.append({'name': row_v[0], 'answers': answers})
    for row in rows[2:]:
        representation[row[0]] = row[1]


def right_answer(phoneme, question, givenanswer):
    if phoneme['answers'][question] == -1:
        return givenanswer
    return phoneme['answers'][question]

def calculate_phoneme_probability(phoneme, questions_so_far, answers_so_far):
    # Prior
    P_phoneme =  representation[phoneme]

    # Likelihood
    P_answers_given_phoneme = 1
    P_answers_given_not_phoneme = 1
    for question, answer in zip(questions_so_far, answers_so_far):
        P_answers_given_phoneme *= max(
            1 - abs(answer - right_answer), 0.01)

        P_answer_not_phoneme = np.mean([1 - abs(answer - right_answer(not_character, question))
                                          for not_character in phonemes
                                          if not_character['name'] != phoneme['name']])
        P_answers_given_not_phoneme *= max(P_answer_not_phoneme, 0.01)

    # Evidence
    P_answers = P_phoneme * P_answers_given_phoneme + \
        (1 - P_phoneme) * P_answers_given_not_phoneme

    # Bayes Theorem
    P_character_given_answers = (
        P_answers_given_phoneme * P_phoneme) / P_answers

    return P_character_given_answers



def calculate_probabilites(questions_so_far, answers_so_far):
    probabilities = []
    for phoneme in phonemes:
        probabilities.append({
            'name': phoneme['name'],
            'probability': calculate_phoneme_probability(phoneme, questions_so_far, answers_so_far)
        })

    return probabilities

questions_so_far = []
answers_so_far = []

#если ответ "согласные", то phonemes это лист consonants, 
#если ответ "гласные", то phonemes это лист vowels