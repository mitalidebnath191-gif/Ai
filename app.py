import os
import telebot
from fastapi import FastAPI, Request, Response
from duckduckgo_search import DDGS

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "8663805678:AAFFEeOMUUws72NdRBYS3nbqjZFnex9C8R4"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()  # 👈 এই নামটির সাথে Vercel লিংক করবে

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 হ্যালো! আমি আপনার Vercel AI অ্যাসিস্ট্যান্ট। আমাকে যেকোনো প্রশ্ন করতে পারেন।")

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    user_id = message.chat.id
    bot.send_chat_action(user_id, 'typing')
    try:
        with DDGS() as ddgs:
            response = ddgs.chat(keywords=message.text, model='gpt-4o-mini')
        for msg in split_message(response):
            bot.send_message(user_id, msg)
    except Exception as e:
        bot.reply_to(message, f"❌ ভুল: {str(e)}")

@app.post("/webhook")
async def process_webhook(request: Request):
    if request.headers.get('content-type') == 'application/json':
        json_string = await request.body()
        update = telebot.types.Update.de_json(json_string.decode('utf-8'))
        bot.process_new_updates([update])
        return Response(status_code=200)
    return Response(status_code=403)

@app.get("/")
def read_root():
    return {"status": "Telegram Bot is running from app.py"}
        
