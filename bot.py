import os, subprocess, tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = os.getenv("BOT_TOKEN")
ASK = 1
user_file = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video bhejo, fir time bhejo jaise: 0:05 0:30")

async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    f = update.message.video or update.message.document
    tf = await context.bot.get_file(f.file_id)
    path = os.path.join(tempfile.gettempdir(), f"{update.effective_user.id}.mp4")
    await tf.download_to_drive(path)
    user_file[update.effective_user.id] = path
    await update.message.reply_text("Video mil gaya! Ab time bhejo -> 0:05 0:30")
    return ASK

async def do_trim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        s, e = update.message.text.split()
        inp = user_file.get(update.effective_user.id)
        out = os.path.join(tempfile.gettempdir(), f"{update.effective_user.id}_out.mp4")
        await update.message.reply_text(f"Cut kar raha hu {s} se {e} tak...")
        subprocess.run(["ffmpeg","-y","-ss",s,"-to",e,"-i",inp,"-c:v","libx264","-c:a","aac",out], check=True)
        await context.bot.send_video(chat_id=update.effective_chat.id, video=open(out,'rb'))
        await update.message.reply_text("Ho gaya! ✅")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}\nFormat aise bhejo: 0:10 0:25")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()
conv = ConversationHandler(
    entry_points=[MessageHandler(filters.VIDEO | filters.Document.VIDEO, get_video)],
    states={ASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, do_trim)]},
    fallbacks=[CommandHandler("start", start)]
)
app.add_handler(CommandHandler("start", start))
app.add_handler(conv)
app.run_polling()
