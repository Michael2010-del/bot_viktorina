import telebot
from config import token
from collections import defaultdict
from logic import quiz_questions

user_responses = {} 
points = defaultdict(int)

bot = telebot.TeleBot(token)

def send_question(chat_id):
    bot.send_message(chat_id, quiz_questions[user_responses[chat_id]].text, reply_markup=quiz_questions[user_responses[chat_id]].gen_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    if call.data == "correct":
        bot.answer_callback_query(call.id, "Answer is correct")
        points[call.message.chat.id] += 1
    elif call.data == "wrong":
        bot.answer_callback_query(call.id, "Answer is wrong")
    
    user_responses[call.message.chat.id] += 1
    
    if user_responses[call.message.chat.id] >= len(quiz_questions):
        total_points = points[call.message.chat.id]
        total_questions = len(quiz_questions)
        bot.send_message(
            call.message.chat.id, 
            f"🎉 Викторина завершена!\n"
            f"📊 Ваш результат: {total_points} из {total_questions} очков\n\n"
        )
        # Добавляем кнопку для рестарта
        from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 Начать заново", callback_data="restart"))
        bot.send_message(call.message.chat.id, "Хотите попробовать снова?", reply_markup=markup)
    else:
        send_question(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart_quiz(call):
    # Сбрасываем прогресс для этого пользователя
    user_responses[call.message.chat.id] = 0
    points[call.message.chat.id] = 0
    bot.answer_callback_query(call.id, "Викторина началась заново!")
    send_question(call.message.chat.id)

@bot.message_handler(commands=['start'])
def start(message):
    # ВАЖНО: Всегда сбрасываем прогресс при команде /start
    user_responses[message.chat.id] = 0
    points[message.chat.id] = 0
    
    # Приветственное сообщение
    bot.send_message(
        message.chat.id,
        "🎮 Добро пожаловать в викторину!\n"
        f"Будет задано {len(quiz_questions)} вопросов.\n"
        "Нажимайте на кнопки под вопросами для выбора ответа.\n"
        "Удачи! 🍀"
    )
    send_question(message.chat.id)

bot.infinity_polling()