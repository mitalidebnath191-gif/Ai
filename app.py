import os
import telebot
from fastapi import FastAPI, Request, Response
import g4f

BOT_TOKEN = os.getenv("BOT_TOKEN", "8663805678:AAEKwFhAEtfkuH04hueFsWQOswzqdZYoiY8")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "👋 হ্যালো! আমি আপনার এআই অ্যাসিস্ট্যান্ট। আমাকে যেকোনো প্রশ্ন জিজ্ঞেস করতে পারেন।")
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
        # সরাসরি সবচেয়ে ফাস্ট প্রোভাইডার ব্যবহার করার চেষ্টা
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
            # provider=g4f.Provider.Blackbox (অটোমেটিক সবচেয়ে ফাস্টটি বেছে নেওয়ার জন্য এটি ফাঁকা রাখা হলো)
        )
        
        # রেসপন্স ঠিকঠাক আসলে মেসেজ পাঠাবে
        if isinstance(response, str) and response.strip() != "":
            for msg in split_message(response):
                bot.send_message(user_id, msg)
        else:
            bot.send_message(user_id, "দুঃখিত, আমি ঠিক বুঝতে পারিনি। আবার বলবেন?")
            
    except Exception as e:
        # কোনো এরর আসলে ইউজারকে কোনো বিরক্তিকর মেসেজ দেবে না, শুধু সার্ভারে লগ করে রাখবে
        print(f"AI Error: {e}")

@app.post("/webhook")
async def process_webhook(request: Request):
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = await request.body()
            update = telebot.types.Update.de_json(json_string.decode('utf-8'))
            
            bot.process_new_updates([update])
        # সব অবস্থাতেই 200 OK পাঠাবে যাতে টেলিগ্রাম লুপ না তৈরি করে
        return Response(status_code=200)
    except Exception as e:
        print(f"Webhook Error: {e}")
        return Response(status_code=200)

@app.get("/")
def read_root():
    return {"status": "Fast AI Bot is running smoothly!"}
