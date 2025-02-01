import random
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext

TOKEN = "8122685666:AAEOs9qjilcg0cT69vIwVR510_Rw9kXG_5A"

players = []
roles = {}

async def start(update: Update, context: CallbackContext) -> None:
    """شروع بازی و توضیح نحوه اضافه کردن بازیکنان"""
    await update.message.reply_text(
        "🎮 به بازی حقیقت و جرات خوش آمدید!\n\n"
        "برای اضافه کردن بازیکنان، دستور زیر را استفاده کنید:\n"
        "`/add نام_بازیکن`\n\n"
        "وقتی همه نام‌ها را اضافه کردید، دستور `/done` را ارسال کنید."
    )

async def add_player(update: Update, context: CallbackContext) -> None:
    """اضافه کردن بازیکنان با دستور /add"""
    global players
    args = context.args
    if not args:
        await update.message.reply_text("⚠ لطفاً نام بازیکن را بعد از `/add` وارد کنید!")
        return
    
    name = " ".join(args).strip()
    if name and name not in players:
        players.append(name)
        await update.message.reply_text(f"✅ {name} به بازی اضافه شد.")
    else:
        await update.message.reply_text("⚠ این نام قبلاً اضافه شده یا نام معتبری نیست!")

async def done(update: Update, context: CallbackContext) -> None:
    """تکمیل ثبت نام بازیکنان و شروع بازی"""
    global players, roles
    if len(players) < 4:
        await update.message.reply_text("🚨 برای شروع بازی حداقل ۴ بازیکن نیاز است!")
        return

    assign_roles()  # تعیین نقش بازیکنان
    await send_turn_message(update, context)

def assign_roles():
    """تعیین نقش‌های اولیه بازیکنان"""
    global players, roles
    roles = {
        players[0]: "❓ سؤال‌پرس",
        players[1]: "🎲 عددهای ۱ و ۲",
        players[2]: "🎲 عددهای ۳ و ۴",
        players[3]: "🎲 عددهای ۵ و ۶",
    }

async def send_turn_message(update: Update, context: CallbackContext) -> None:
    """ارسال پیام نوبت همراه با دکمه شیشه‌ای"""
    global roles

    roles_text = "\n".join([f"{name}: {role}" for name, role in roles.items()])
    
    keyboard = [[InlineKeyboardButton("✅ پرسیدم، بریم نفر بعد", callback_data="next_turn")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    current_turn = [name for name, role in roles.items() if role == "❓ سؤال‌پرس"][0]

    message = (
        f" بازی حقیقت! 👨‍🦽\n\n🔹 نقش بازیکنان:\n{roles_text}\n\n"
        f"🔸 حالا نوبت {current_turn}ه! 🎲 تاس بنداز و سوالتو بپرس."
    )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)

async def next_turn(update: Update, context: CallbackContext) -> None:
    """پایان دور، تغییر نوبت و جابه‌جایی نقش بازیکنان"""
    global roles, players
    query = update.callback_query
    await query.answer()

    # پیدا کردن بازیکن فعلی که سؤال‌پرس است
    current_questioner = [name for name, role in roles.items() if role == "❓ سؤال‌پرس"][0]
    current_index = players.index(current_questioner)

    # چرخش نقش‌ها: نفر بعدی سؤال‌پرس می‌شود
    next_index = (current_index + 1) % len(players)

    # جابجایی نقش‌ها
    new_roles = roles.copy()
    new_roles[players[next_index]] = "❓ سؤال‌پرس"
    new_roles[players[current_index]] = roles[players[next_index]]

    roles = new_roles  # به‌روزرسانی نقش‌ها

    await query.message.delete()  # حذف پیام قبلی با دکمه
    await send_turn_message(update, context)  # ارسال پیام جدید با دکمه جدید

def main():
    """اجرای بات تلگرام"""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_player))  # دستور جدید برای اضافه کردن بازیکنان
    application.add_handler(CommandHandler("done", done))
    application.add_handler(CallbackQueryHandler(next_turn, pattern="next_turn"))

    application.run_polling()

if __name__ == "__main__":
    main()
