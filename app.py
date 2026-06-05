import os
import telebot
from fastapi import FastAPI, Request, Response
from g4f.client import Client

# টোকেন সেটআপ
BOT_TOKEN = os.getenv("BOT_TOKEN", "8663805678:AAEKwFhAEtfkuH04hueFsWQOswzqdZYoiY8")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()
client = Client()

# মেসেজ বড় হলে ভেঙে পাঠানোর ফাংশন
def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        welcome_text = "👋 হ্যালো! আমি আপনার GPT4Free AI অ্যাসিস্ট্যান্ট। আমাকে যেকোনো প্রশ্ন জিজ্ঞেস করতে পারেন।"
        bot.reply_to(message, welcome_text)
    except Exception as e:
        print(f"Welcome error: {e}")

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    user_id = message.chat.id
    
    # টাইপিং স্ট্যাটাস
    try:
        bot.send_chat_action(user_id, 'typing')
    except:
        pass
        
    try:
        # GPT4Free থেকে রেসপন্স জেনারেট করা
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # g4f নিজে থেকেই সবচেয়ে ফাস্ট ফ্রি প্রোভাইডার বেছে নেবে
            messages=[{"role": "user", "content": message.text}],
        )
        
        ai_reply = response.choices[0].message.content if response.choices else "❌ কোনো উত্তর পাওয়া যায়নি।"
        
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
            
    except Exception as e:
        # Vercel 10-second timeout বা অন্য কোনো Error আসলে বট ক্র্যাশ না করে এই মেসেজ দেবে
        try:
            bot.reply_to(message, "⚠️ এআই সার্ভার এই মুহূর্তে একটু ব্যস্ত আছে বা রেসপন্স আনতে দেরি হচ্ছে। দয়া করে একটু পর আবার মেসেজ দিন।")
            print(f"AI Generation Error: {e}")
        except:
            pass

# 🛠️ ওয়েবহুক রুট (এখানেই টেলিগ্রাম মেসেজ পাঠাবে)
@app.post("/webhook")
async def process_webhook(request: Request):
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = await request.body()
            update = telebot.types.Update.de_json(json_string.decode('utf-8'))
            
            bot.process_new_updates([update])
            return Response(status_code=200)
        return Response(status_code=403)
    except Exception as e:
        print(f"Webhook Exception: {e}")
        return Response(status_code=200) # 500 এর বদলে 200 দিচ্ছি যাতে টেলিগ্রাম বারবার একই রিকোয়েস্ট পাঠিয়ে স্প্যাম না করে

@app.get("/")
def read_root():
    return {"status": "GPT4Free Telegram Bot is running smoothly on Vercel!"}
    
