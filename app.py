import os
import telebot
from fastapi import FastAPI, Request, Response
from duckduckgo_search import DDGS

# আপনার দেওয়া টেলিগ্রাম বট টোকেন
BOT_TOKEN = "8663805678:AAFFEeOMUUws72NdRBYS3nbqjZFnex9C8R4"
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

app = FastAPI()

# বড় মেসেজকে ৪০০০ ক্যারেক্টারের টুকরোতে ভাগ করার ফাংশন
def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# বটের স্টার্ট কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 হ্যালো! আমি আপনার Vercel AI অ্যাসিস্ট্যান্ট।\n\n"
        "🤖 আমি ChatGPT বা Gemini-র মতো যেকোনো প্রশ্নের উত্তর দিতে পারি এবং কোডিংও করতে পারি।\n"
        "⚡ Vercel Serverless হওয়ায় আমি ২৪ ঘণ্টাই সম্পূর্ণ ফ্রিতে সচল থাকব!"
    )
    bot.reply_to(message, welcome_text)

# ইউজার মেসেজ হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    user_id = message.chat.id
    user_query = message.text
    
    bot.send_chat_action(user_id, 'typing')
    
    try:
        # DuckDuckGo-র ফ্রি AI API ব্যবহার করে জিপিটি মডেল কল করা
        with DDGS() as ddgs:
            response = ddgs.chat(keywords=user_query, model='gpt-4o-mini')
            ai_reply = response
        
        messages_to_send = split_message(ai_reply)
        for msg in messages_to_send:
            bot.send_message(user_id, msg)
            
    except Exception as e:
        bot.reply_to(message, f"❌ দুঃখিত, একটি সমস্যা হয়েছে।\nভুল: {str(e)}")

# Vercel-এর জন্য Webhook রুট/এন্ডপয়েন্ট
@app.post(f"/{BOT_TOKEN}")
async def process_webhook(request: Request):
    if request.headers.get('content-type') == 'application/json':
        json_string = await request.body()
        update = telebot.types.Update.de_json(json_string.decode('utf-8'))
        bot.process_new_updates([update])
        return Response(status_code=200)
    else:
        return Response(status_code=403)

@app.get("/")
def read_root():
    return {"status": "Telegram Bot is running on Vercel"}
                          
