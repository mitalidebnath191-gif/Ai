import os
import telebot
from fastapi import FastAPI, Request, Response
import requests
import urllib.parse

# টোকেন সেটআপ
BOT_TOKEN = os.getenv("BOT_TOKEN", "8663805678:AAEKwFhAEtfkuH04hueFsWQOswzqdZYoiY8")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "👋 হ্যালো! আমি এখন ডাইরেক্ট API এর মাধ্যমে সংযুক্ত। আমাকে যেকোনো প্রশ্ন করতে পারেন!")
    except:
        pass

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    user_id = message.chat.id
    
    try:
        bot.send_chat_action(user_id, 'typing')
    except:
        pass
        
    try:
        # g4f এর বদলে সরাসরি Pollinations AI এর ডাইরেক্ট ওয়েব API ব্যবহার (অনেক ফাস্ট এবং ক্র্যাশ-ফ্রি)
        encoded_prompt = urllib.parse.quote(message.text)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        
        # API থেকে রেসপন্স আনা
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200 and response.text:
            ai_reply = response.text
        else:
            ai_reply = "দুঃখিত, আমি এই মুহূর্তে উত্তর তৈরি করতে পারছি না।"
            
        # মেসেজ পাঠানো
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
            
    except Exception as e:
        print(f"Direct API Error: {e}")
        # সার্ভার থেকে কোনো এরর আসলে চুপ না থেকে ইউজারকে জানাবে
        try:
            bot.send_message(user_id, "⚠️ একটু সমস্যা হচ্ছে, দয়া করে আবার প্রশ্ন করুন।")
        except:
            pass

@app.post("/webhook")
async def process_webhook(request: Request):
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = await request.body()
            update = telebot.types.Update.de_json(json_string.decode('utf-8'))
            
            bot.process_new_updates([update])
        return Response(status_code=200)
    except Exception as e:
        print(f"Webhook Error: {e}")
        return Response(status_code=200)

@app.get("/")
def read_root():
    return {"status": "Direct API Bot is running without crashes!"}
        
