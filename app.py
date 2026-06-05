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
        bot.reply_to(message, "👋 হ্যালো! আমি আপনার সুপার স্মার্ট বট। আমাকে প্রশ্ন করুন, আমি ইন্টারনেট খুঁজে উত্তর আনবোই!")
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
    
    # 🎯 এখানে বটকে বলে দেওয়া হলো সে পর্যায়ক্রমে কাদের কাছে উত্তর খুঁজবে
    models_to_try = [
        "gemini-pro",        # ১. প্রথমে যাবে গুগলের জেমিনির কাছে
        "gpt-3.5-turbo",     # ২. জেমিনি ফেইল করলে যাবে চ্যাটজিপিটি-র কাছে
        "claude-3-opus",     # ৩. সেটাও ফেইল করলে যাবে ক্লড (Claude) এর কাছে
        "llama-3-8b-instruct" # ৪. সবশেষে যাবে মেটার লামার (Llama) কাছে
    ]
    
    # লুপ (Loop) চালিয়ে একটার পর একটা চেক করা
    for model_name in models_to_try:
        try:
            response = g4f.ChatCompletion.create(
                model=model_name, 
                messages=[{"role": "user", "content": message.text}]
            )
            
            # যদি উত্তর ঠিকঠাক আসে এবং ফাঁকা না হয়
            if isinstance(response, str) and response.strip() != "":
                ai_reply = response
                # উত্তর পেয়ে গেলে 'break' দিয়ে আর অন্য এআই-এর কাছে যাবে না, এখানেই থেমে যাবে
                break 
                
        except Exception as e:
            # কোনো এআই ফেইল করলে চুপ করে পরেরটার কাছে চলে যাবে (continue)
            print(f"{model_name} Failed: {e}")
            continue 

    # যদি উপরের ৪টি এআই-ই একবারে ফেইল করে (যেটা হওয়ার চান্স ১%), তখন এই মেসেজ দেবে
    if not ai_reply:
        ai_reply = "দুঃখিত, এই মুহূর্তে ইন্টারনেটের সব এআই সার্ভার ডাউন আছে। একটু পর আবার মেসেজ দিন, আমি ঠিক উত্তর দিয়ে দেব!"

    # মেসেজ পাঠানো
    try:
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
    except Exception as e:
        print(f"Message Send Error: {e}")

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
    return {"status": "Ultimate Multi-AI Bot is running!"}
            
