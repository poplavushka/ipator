import csv #импорт модуля csv для работы с csv таблицами
import numpy as np #для операций с чиселками
from telegram import Update #импорт классов телеграма для обработки ответов пользователя
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram.error import NetworkError, Unauthorized, Conflict

# consonants из cons.csv
with open('cons.csv', 'r', encoding='utf8') as consf: #открываем csv файл с согласными
    reader = csv.reader(consf)
    rows = list(reader) #считываем строки в список
    consonant_questions = dict(zip(rows[0][2:], rows[1][2:])) #создаем словарь вопросов из первых двух строк
    consonants = [] #пустой список для хранения данных о согласных
    firstrow = rows[0] # сохраняем первую строку (заголовок)
    representation_consonants = {} #пустой словарь для значений представимости согласных
    for row in rows[2:]: #начиная с третьей ходим по строчкам
        answers = dict(zip(firstrow[2:], row[2:])) #создаем словарь ответов для каждого согласного
        consonants.append({'name': row[0], 'answers': answers}) #добавляем данные о согласных в список
    for row in rows[2:]:
        representation_consonants[row[0]] = float(row[1])

# vowels тоже самое, что с согласными
with open('vowels.csv', 'r', encoding='utf8') as vowsf:
    reader_v = csv.reader(vowsf)
    rows_v = list(reader_v)
    vow_questions = dict(zip(rows_v[0][2:], rows_v[1][2:]))
    vowels = []
    firstrow_v = rows_v[0]
    representation_vowels = {}
    for row_v in rows_v[2:]:
        answers = dict(zip(firstrow_v[2:], row_v[2:]))
        vowels.append({'name': row_v[0], 'answers': answers})
    for row_v in rows_v[2:]:
        representation_vowels[row_v[0]] = float(row_v[1])

def right_answer(phoneme, question, givenanswer): #функция для определения правильных ответов для фонемы и вопроса
    if phoneme['answers'][question] == -1: #если 1 - то правильный
        return givenanswer
    return float(phoneme['answers'][question])

def calculate_phoneme_probability(phoneme, questions_so_far, answers_so_far, representation): #рассчитываем вероятность того, что фонема - загаданная, в зависимости от ответов
    #вероятность того, что загадана n-ная фонема, в целом
    P_phoneme = representation[phoneme['name']]
    #Likelihood
    P_answers_given_phoneme = 1
    P_answers_given_not_phoneme = 1
    for question, answer in zip(questions_so_far, answers_so_far):
        P_answers_given_phoneme *= max(1 - abs(answer - right_answer(phoneme, question, answer)), 0.01)
        P_answer_not_phoneme = np.mean([1 - abs(answer - right_answer(not_phoneme, question, answer))
                                        for not_phoneme in phonemes if not_phoneme['name'] != phoneme['name']])
        P_answers_given_not_phoneme *= max(P_answer_not_phoneme, 0.01)
    #полученные ответы
    P_answers = P_phoneme * P_answers_given_phoneme + (1 - P_phoneme) * P_answers_given_not_phoneme
    #теорема Байеса
    P_character_given_answers = (P_answers_given_phoneme * P_phoneme) / P_answers

    return P_character_given_answers

def calculate_probabilities(questions_so_far, answers_so_far):
    probabilities = [] #список для хранения вероятностей
    for phoneme in phonemes:
        probabilities.append({
            'name': phoneme['name'],
            'probability': calculate_phoneme_probability(phoneme, questions_so_far, answers_so_far, representation)
        })
    return probabilities
#состояние диалога с пользователем
CHOOSING, ASKING, VERIFYING = range(3)

def start(update: Update, _: CallbackContext) -> int: #обработка команды старт
    update.message.reply_text("Привет! Ты хочешь загадать гласный или согласный звук?")
    return CHOOSING

def choose_type(update: Update, context: CallbackContext) -> int: # обрабатываем ответ пользователя о типе фонемы
    user_input = update.message.text.lower()  
    if user_input in ['гласный', 'согласный']:
        context.user_data['type'] = user_input  # сохраняем тип фонемы в данных пользователя
        context.user_data['questions_so_far'] = []
        context.user_data['answers_so_far'] = []
        if user_input == 'гласный':
            context.user_data['questions'] = list(vow_questions.keys())
            global phonemes, representation
            phonemes = vowels
            representation = representation_vowels
        else:
            context.user_data['questions'] = list(consonant_questions.keys())
            phonemes = consonants
            representation = representation_consonants
        return ask_question(update, context)
    else:
        update.message.reply_text("Выбери 'гласный' или 'согласный'.")
        return CHOOSING

def ask_question(update: Update, context: CallbackContext) -> int:
    if context.user_data['questions']:
        question = context.user_data['questions'].pop(0)
        context.user_data['current_question'] = question
        update.message.reply_text(vow_questions[question] if context.user_data['type'] == 'гласный' else consonant_questions[question])
        return ASKING
    else:
        return identify_sound(update, context) #если вопросов не осталось, определяем звук

def receive_answer(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.lower()
    current_question = context.user_data['current_question']
    answer_map = { #варианты ответов пользователя
        'да': 1.0,
        'нет': 0.0,
        'не знаю': 0.5,
        'скорее да': 0.75,
        'скорее нет': 0.25
    }
    answer = answer_map.get(user_input, 0.5)
    context.user_data['questions_so_far'].append(current_question)
    context.user_data['answers_so_far'].append(answer)
    return ask_question(update, context) #задаем след вопрос

def identify_sound(update: Update, context: CallbackContext) -> int: #функция определяет звук
    questions_so_far = context.user_data['questions_so_far'] #хранят заданные вопросы и ответы
    answers_so_far = context.user_data['answers_so_far']

    probabilities = calculate_probabilities(questions_so_far, answers_so_far)
    probabilities.sort(key=lambda x: x['probability'], reverse=True) #вероятности расположены по убыванию
    
    if probabilities: #проверяет на пустоту списка
        best_guess = probabilities[0]['name'] #берем первый элемент
        best_guess_rep = round(representation[best_guess], 3) * 100 #приводим в порядок репрезентативность звука
        update.message.reply_text(f"Мне кажется, что ты загадал звук: {best_guess}, верно? кстати, он присутствует в {best_guess_rep}% языков мира :)") #отправляем пользователю сообщение с звуком и процентом репрезентативности, потом ждем подтверждения
        return VERIFYING
    else:
        update.message.reply_text("Я не смог отгадать звук...Попробуй ещё раз")
        return CHOOSING

def verify_answer(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.lower()
    if user_input == 'да':
        update.message.reply_text('ура, а вот ссылка, где ты подробнее сможешь узнать о звуках языков мира: https://phoible.org/parameters')
    elif user_input == 'нет':
        update.message.reply_text('эх, давай сыграем ещё раз!')
        return CHOOSING
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Пока!")
    return ConversationHandler.END

def main(): #функция запускающая бота
    TOKEN = "6943899690:AAGJ5YL34KKX1wpbmdzhmSheSnQSZI11fQg" 
    updater = Updater(TOKEN) 
    dispatcher = updater.dispatcher #получаем диспетчер для регистрации обрабатывающих штук

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.text & ~Filters.command, choose_type)], 
            ASKING: [MessageHandler(Filters.text & ~Filters.command, receive_answer)],
            VERIFYING: [MessageHandler(Filters.text & ~Filters.command, verify_answer)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler) #добавляем обрабатывателя диалогов

    try:
        updater.start_polling()
        updater.idle()
    except NetworkError as e:
        print(f"NetworkError: {e}")
    except Conflict as e:
        print(f"Conflict: {e}. Make sure no other instances are running.")
    except Unauthorized as e:
        print(f"Unauthorized: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__": #проверяет запсукается ли скрипт напрямую и вызывает функцию для запуска бота
    main()