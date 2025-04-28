import json
import datetime
import webscraper

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from dateutil.relativedelta import relativedelta

# Збираємо дані з сайту cyberion.ua та створюємо JSON-файли
print("Get news ...")
webscraper.news_create_json()

print("Get clubs ...")
webscraper.clubs_create_json()

print("Get tournaments ...")
webscraper.tournaments_create_json()

# Відкриваємо і читаємо JSON-файл
with open("news.json", "r", encoding="utf-8") as f:
    dataNews = json.load(f)

with open("clubs.json", "r", encoding="utf-8") as f:
    dataClubs = json.load(f)

with open("tournaments.json", "r", encoding="utf-8") as f:
    dataTournaments = json.load(f)

# Токен бота
TOKEN = "*********"

# Зберігаємо останнє повідомлення бота
user_bot_messages = {}

dash = "──────────────────"

# Параметри
BUTTONS_PER_PAGE = 4
ALL_OPTIONS = [f" {club}" for club in dataClubs]

# Генерація клавіатури для сторінки
def build_inline_keyboard_clubs(page: int):
    start = page * BUTTONS_PER_PAGE
    end = start + BUTTONS_PER_PAGE
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"option:{opt}")]
        for opt in ALL_OPTIONS[start:end]
    ]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page:{page - 1}"))
    if end < len(ALL_OPTIONS):
        nav.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"page:{page + 1}"))

    if nav:
        buttons.append(nav)
    
    buttons.append([InlineKeyboardButton("Головна", callback_data="home")])

    return InlineKeyboardMarkup(buttons)

def build_inline_keyboard_home():
    buttons = [
        [InlineKeyboardButton(text="Новини", callback_data="news")],
        [InlineKeyboardButton(text="Клуби", callback_data="clubs")],
        [InlineKeyboardButton(text="Турніри", callback_data="tournaments")]
    ]
    return InlineKeyboardMarkup(buttons)

def build_inline_keyboard_news():
    buttons = [
        [InlineKeyboardButton(text="Поточний місяць", callback_data="now")],
        [InlineKeyboardButton(text="Минулий місяць", callback_data="past")],
        [InlineKeyboardButton("Головна", callback_data="home")]
    ]
    return InlineKeyboardMarkup(buttons)

def build_inline_keyboard_tournaments():
    buttons = [
        [InlineKeyboardButton("Головна", callback_data="home")]
    ]
    return InlineKeyboardMarkup(buttons)

# Видаляємо і повідомлення користувача, і бота
async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Видалити повідомлення користувача (команду або текст)
    try:
        await context.bot.delete_message(chat_id, update.message.message_id)
    except:
        print("Error delete user msg")
        pass

    # Видалити попереднє повідомлення бота
    old_msg_id = user_bot_messages.get(user_id)
    if old_msg_id:
        try:
            await context.bot.delete_message(chat_id, old_msg_id)
        except:
            print("Error delete bot msg")
            pass

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await clear_chat(update, context)
    print("Use bot /start")
    msg = await update.message.reply_text(
        "Оберіть варіант:",
        reply_markup=build_inline_keyboard_home()
    )

    user_bot_messages[update.effective_user.id] = msg.message_id

# Вивід новиви в залежності від обраного періоду
async def send_news(update: Update):
    newsNow = []

    today = datetime.date.today()
    format_today = f""
    text = f''

    if update.callback_query.data == "now":
        format_today = f"{today.month}.{today.year}"
        text = f'✅ Ви обрали Поточний місяць:\n{dash}\n'
    elif update.callback_query.data == "past":
        past_time = today - relativedelta(months=1)
        format_today = f"{past_time.month}.{past_time.year}"
        text = f'✅ Ви обрали Минулий місяць:\n{dash}\n'

    for news in dataNews:
        date_str = news["date"]
        date_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y")

        fomat_date_news = f"{date_obj.month}.{date_obj.year}"

        if fomat_date_news == format_today:
            newsNow.append(news)    

    for news in newsNow:
        text += f'🔥 <b>{news["title"]}</b>\n📅 <b>{news["date"]}</b>\n\n📰 Деталі за посиланням:\n<a href="{news["url"]}">cyberion.ua/news</a>\n{dash}\n'

    try:  
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=build_inline_keyboard_news(),
            parse_mode="HTML",
            disable_web_page_preview=True
            )
    except:
        print("No edit text")

# Обробка callback_data
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # обов'язково

    data = query.data

    if data.startswith("page:"):
        page = int(data.split(":")[1])
        await query.edit_message_reply_markup(reply_markup=build_inline_keyboard_clubs(page))

    elif data.startswith("news"):
        await query.edit_message_text(
            text="Оберіть період:",
            reply_markup=build_inline_keyboard_news()
            )
    
    elif data.startswith("now"):
        await send_news(update)

    elif data.startswith("past"):
        await send_news(update)
    
    elif data.startswith("clubs"):
        await query.edit_message_text(
            text="Оберіть місто:",
            reply_markup=build_inline_keyboard_clubs(page=0)
            )
    
    elif data.startswith("tournaments"):
        text = f'🕹️ Список турнірів:\n{dash}\n'
        for tournament in dataTournaments:
            text += f'🎮 <b>{tournament["title"]}</b>\n\n{tournament["parameters"]}\n\n📝 <a href="https://cyberion.ua/kololeague">Зареєструватись</a>\n{dash}\n'

        try:
            await query.edit_message_text(
                text=text,
                reply_markup=build_inline_keyboard_tournaments(),
                parse_mode="HTML"
                )
        except:
            print("No edit text")
        
    elif data.startswith("home"):
        await query.edit_message_text(
            text="Головне меню:",
            reply_markup=build_inline_keyboard_home()
            )

    elif data.startswith("option:"):
        option = data.split(":", 1)[1]
        text = f'✅ Ви обрали місто: {option} \n{dash}\n'
        cut = option[1:len(option)]
        dataClubsCity = dataClubs[cut]

        if dataClubsCity[0]["url_club"] != "":
            
            for club in dataClubsCity:
                if club["title"][:8] == "CYBERION":
                    title = club["title"][9:]
                else:
                    title = club["title"]
                text += f'📍 <b>{title}</b>\n<a href="https://www.google.com/maps/search/?api=1&query={club["location"]}"><i>{club["location"][len(cut)+1:]}</i></a>\n🎮 <a href="{club["url_club"]}">Сайт клубу</a> 🌐\n🗓️ <a href="{club["social"]}">Бронювання</a>\n{dash}\n'
              
            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=build_inline_keyboard_clubs(page=0),
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            except:
                print("No edit text")

        else:
            
            try:
                await query.edit_message_text(
                    text=f'✅ Ви обрали місто: {option}\n\n🚀 <b>НЕЗАБАРОМ ВІДКРИТТЯ!</b>  ',
                    reply_markup=build_inline_keyboard_clubs(page=0),
                    parse_mode="HTML",
                    disable_web_page_preview=True
                    )
            except:
                print("No edit text")
    
# Запуск
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот працює!")
    app.run_polling()

if __name__ == '__main__':
    main()
    