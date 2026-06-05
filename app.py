import os
import telebot
from fastapi import FastAPI, Request, Response
from duckduckgo_search import DDGS

# Environment Variable থেকে টোকেন নেওয়া
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "8663805678:AAEKwFhAEtfkuH04hueFsWQOswzqdZYoiY8"

# threaded=False এবং অবশ্যই নতুন টোকেনটি নিশ্চিত করা হয়েছে
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = FastAPI()

def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        welcome_text = "👋 হ্যালো! আমি আপনার Vercel AI অ্যাসিস্ট্যান্ট। আমাকে যেকোনো কোডিং বা সাধারণ প্রশ্ন জিজ্ঞেস করতে পারেন।"
        bot.reply_to(message, welcome_text)
    except Exception as e:
        print(f"Welcome error: {e}")

@bot.message_handler(func=lambda message: True)
def handle_ai_response(message):
    user_id = message.chat.id
    
    # টাইপিং স্ট্যাটাস পাঠানো
    try:
        bot.send_chat_action(user_id, 'typing')
    except:
        pass
        
    try:
        # জিপিটি মডেল ব্যবহার করে DuckDuckGo থেকে ফ্রি রেসপন্স জেনারেট করা
        with DDGS() as ddgs:
            response = ddgs.chat(keywords=message.text, model='gpt-4o-mini')
            ai_reply = response if response else "❌ দুঃখিত, কোনো উত্তর পাওয়া যায়নি।"
        
        # ৪০০০ ক্যারেক্টারের বেশি হলে স্প্লিট করে মেসেজ পাঠানো
        for msg in split_message(ai_reply):
            bot.send_message(user_id, msg)
            
    except Exception as e:
        # কোনো কারণে এরর আসলে টেলিগ্রামে ইউজারকে জানানো
        try:
            bot.reply_to(message, f"❌ এআই প্রসেসিংয়ে সমস্যা হয়েছে।\nভুল: {str(e)}")
        except:
            print(f"Telegram reply failed: {e}")

# 🛠️ এটি আপনার মূল ওয়েব হুক রুট
@app.post("/webhook")
async def process_webhook(request: Request):
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = await request.body()
            update = telebot.types.Update.de_json(json_string.decode('utf-8'))
            
            # ভেরসেল সার্ভারলেস এনভায়রনমেন্টে আপডেট প্রসেস করার সঠিক নিয়ম
            bot.process_new_updates([update])
            return Response(status_code=200)
        return Response(status_code=403)
    except Exception as e:
        print(f"Webhook Exception: {e}")
        return Response(status_code=500)

@app.get("/")
def read_root():
    return {"status": "Telegram Bot is running smoothly from app.py"}
