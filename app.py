import os
import telebot
from fastapi import FastAPI, Request, Response
import g4f
# শুধু সেই প্রোভাইডারগুলো ইমপোর্ট করছি যারা Vercel-এ ব্লক হয় না
from g4f.Provider import PollinationsAI, Blackbox, DuckDuckGo

BOT_TOKEN = os.getenv("BOT_TOKEN", "8663805678:AAEKwFhAEtfkuH04hueFsWQOswzqdZYoiY8")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "👋 হ্যালো! আমি এখন নতুন অ্যান্টি-ব্লক সিস্টেম নিয়ে রেডি!")
    except:
        pass

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    user_id = message.chat.id
    
    try:
        bot.send_chat_action(user_id, 'typing')
    except:
        pass
        
    ai_reply = ""
    
    # 🎯 Vercel-এর জন্য সবচেয়ে নিরাপদ ৩টি প্রোভাইডার
    safe_providers = [PollinationsAI, Blackbox, DuckDuckGo]
    
    for provider in safe_providers:
        try:
            # নির্দিষ্ট প্রোভাইডার ব্যবহার করে উত্তর আনা
            response = g4f.ChatCompletion.create(
                model=g4f.models.default, 
                messages=[{"role": "user", "content": message.text}],
                provider=provider
            )
            
            if isinstance(response, str) and response.strip() != "":
                ai_reply = response
                break # উত্তর পেলেই লুপ থেকে বেরিয়ে যাবে
                
        except Exception as e:
            print(f"{provider.__name__} Failed: {e}")
            continue

    # যদি ৩টি নিরাপদ প্রোভাইডারও ডাউন থাকে
    if not ai_reply:
        ai_reply = "দুঃখিত, এখন ইন্টারনেট থেকে ডেটা আনতে একটু সমস্যা হচ্ছে। একটু পর আবার ট্রাই করুন।"

    try:
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
    except Exception as e:
        print(f"Send Error: {e}")

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
    return {"status": "Anti-Block AI Bot is running!"}
            
