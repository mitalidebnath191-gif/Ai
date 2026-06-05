import os
import telebot
from fastapi import FastAPI, Request, Response
import requests

# Vercel থেকে টোকেন এবং এপিআই কি নেওয়া হবে (নিরাপত্তার জন্য)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8663805678:AAEKwFhAEtfkuH04hueFsWQOswzqdZYoiY8")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "👋 হ্যালো! আমি Groq API দ্বারা চালিত। আমি সুপার ফাস্ট! আমাকে যেকোনো প্রশ্ন করতে পারেন।")
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
        # তোমার দেওয়া Groq এর ডাইরেক্ট API লিংক
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        payload = {
            "model": "llama3-8b-8192", # Groq-এর সবচেয়ে ফাস্ট এবং ফ্রি মডেল
            "messages": [{"role": "user", "content": message.text}]
        }
        
        # API থেকে রেসপন্স আনা
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            ai_reply = result['choices'][0]['message']['content']
        else:
            ai_reply = f"দুঃখিত, একটি সমস্যা হয়েছে। Error: {response.text}"
            
        # মেসেজ পাঠানো
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
            
    except Exception as e:
        print(f"API Error: {e}")
        try:
            bot.send_message(user_id, "⚠️ একটু সমস্যা হচ্ছে, দয়া করে আবার চেষ্টা করুন।")
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
    return {"status": "Groq API Bot is running at lightspeed!"}
        
