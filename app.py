import os
import telebot
from fastapi import FastAPI, Request, Response
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN", "8663805678:AAEKwFhAEtfkuH04hueFsWQOswzqdZYoiY8")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "👋 হ্যালো! আমি এখন সম্পূর্ণ প্রস্তুত। আমাকে যেকোনো বড় প্রশ্ন বা বাংলায় লিখতে পারেন!")
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
        # সঠিক URL এবং সাধারণ POST রিকোয়েস্ট
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [{"role": "user", "content": message.text}],
            "model": "openai" # এটি অটোমেটিক সবচেয়ে ভালো মডেলটি বেছে নেবে
        }
        
        # API থেকে রেসপন্স আনা
        response = requests.post(url, json=payload, timeout=15)
        
        # যদি রিকোয়েস্ট সফল হয় (200), তবে সরাসরি টেক্সটটাই হলো আমাদের উত্তর
        if response.status_code == 200 and response.text:
            ai_reply = response.text
        else:
            ai_reply = f"দুঃখিত, আমি এই মুহূর্তে উত্তর তৈরি করতে পারছি না। (সার্ভার স্ট্যাটাস: {response.status_code})"
            
        # মেসেজ পাঠানো
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
            
    except Exception as e:
        print(f"API Error: {e}")
        try:
            bot.send_message(user_id, "⚠️ রেসপন্স আনতে সমস্যা হচ্ছে, দয়া করে একটু পর আবার চেষ্টা করুন।")
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
    return {"status": "Perfect API Bot is running!"}
                             
