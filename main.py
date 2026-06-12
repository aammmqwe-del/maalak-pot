from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
import os
import asyncio

# الإعدادات المخفية والأمان
TOKEN = os.environ.get("BOT_TOKEN")
MY_ID = 844192857  # معرفك الخاص
CHANNEL_ID = "@maalak_49"  # معرف قناتك
DB_FILE = "video_db.txt"

# سجل إرسالات المستخدمين
user_history = {}

CATEGORIES = {
    "قيم اوف ثرونز": ["قيم اوف ثرونز", "game of thrones", "got"],
    "بانشي": ["بانشي", "banshee"],
    "ديكستر": ["ديكستر", "dexter"],
    "Peaky blinders 💀": ["peaky blinders", "بيكي بلايندرز"],
    "The Blacklist": ["the blacklist", "بلاك ليست"],
    "المعاقب": ["المعاقب", "the punisher"],
    "سبرانو": ["سبرانو", "sopranos"],
    "The Mentalist": ["the mentalist", "مينتليست"],
    "The walking dead": ["the walking dead", "والكينق ديد"],
    "جون ويك": ["جون ويك", "john wick"],
    "هاري بوتر": ["هاري بوتر", "harry potter"],
    "مقاطع عشوائية": ["عشوائي", "random"]
}

cache = {cat: [] for cat in CATEGORIES.keys()}

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    parts = line.strip().split("|")
                    if len(parts) == 2:
                        cat, fid = parts
                        if cat in cache: cache[cat].append(fid)

load_db()

# التحقق من الاشتراك
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, update.effective_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# أمر الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text("عذراً، يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت:\n" + CHANNEL_ID)
        return
    
    welcome_msg = "نورتوا بوت ملاك مشاهده ممتعه💗💞"
    keyboard = [
        ["قيم اوف ثرونز", "بانشي"], ["ديكستر", "Peaky blinders 💀"],
        ["The Blacklist", "المعاقب"], ["سبرانو", "The Mentalist"],
        ["The walking dead", "جون ويك"], ["هاري بوتر", "مقاطع عشوائية"]
    ]
    await update.message.reply_text(welcome_msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# أمر الإحصائيات (مخصص لك)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != MY_ID: return
    msg = "📊 **إحصائيات البوت الحالية:**\n\n"
    for cat, videos in cache.items():
        msg += f"• {cat}: {len(videos)} مقطع\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# حفظ المقاطع (مخصص لك)
async def save_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != MY_ID: return
    if not update.message.caption: return
    caption = update.message.caption.lower()
    for cat, tags in CATEGORIES.items():
        if any(tag in caption for tag in tags):
            fid = update.message.video.file_id
            if fid not in cache[cat]:
                cache[cat].append(fid)
                with open(DB_FILE, "a", encoding="utf-8") as f: f.write(f"{cat}|{fid}\n")
                await update.message.reply_text(f"تم حفظ المقطع في قسم: {cat}")
            else:
                await update.message.reply_text("هذا المقطع موجود مسبقاً!")
            return

# عرض المقاطع مع التحقق من الاشتراك
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await update.message.reply_text("يجب الاشتراك في القناة لاستخدام البوت: " + CHANNEL_ID)
        return

    user_id = update.message.from_user.id
    cat = update.message.text
    
    if cat not in cache or not cache[cat]:
        await update.message.reply_text("عذراً، هذا القسم فارغ حالياً.")
        return

    if user_id not in user_history: user_history[user_id] = {}
    if cat not in user_history[user_id]: user_history[user_id][cat] = []

    available = [v for v in cache[cat] if v not in user_history[user_id][cat]]
    if not available:
        user_history[user_id][cat] = []
        available = cache[cat]

    chosen_video = random.choice(available)
    user_history[user_id][cat].append(chosen_video)
    await update.message.reply_video(video=chosen_video)


# تشغيل البوت الرسمي بالخلفية كـ Worker
def main():
    if not TOKEN:
        raise ValueError("خطأ: لم يتم العثور على BOT_TOKEN!")
        
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.VIDEO & filters.CAPTION, save_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    
    print("بوت المقاطع (Maalak48) يعمل الآن بنجاح وبدون توقف..")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
