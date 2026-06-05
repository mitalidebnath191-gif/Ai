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
        # POST রিকোয়েস্টের মাধ্যমে পাঠানো হচ্ছে (যাতে বাংলা বা বড় টেক্সটে সমস্যা না হয়)
        url = "https://text.pollinations.ai/openai"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [{"role": "user", "content": message.text}],
            "model": "gpt-4o" # সবচেয়ে স্মার্ট এবং ফাস্ট মডেল
        }
        
        # API থেকে রেসপন্স আনা
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            ai_reply = result['choices'][0]['message']['content']
        else:
            ai_reply = "দুঃখিত, আমি এই মুহূর্তে উত্তর তৈরি করতে পারছি না।"
            
        # মেসেজ পাঠানো
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
            
    except Exception as e:
        print(f"API Error: {e}")
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
    return {"status": "POST API Bot is running perfectly!"}
        
