from aiogram.enums import ParseMode

from database.database import SessionLocal
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from sqlalchemy.orm import Session
from aiogram.filters import Command
from database.repository import Repository
from config import get_leetcode_info, fetch_daily_coding_challenge, get_problem_details

repository = Repository()


def get_db():
    db = SessionLocal()
    return db


router = Router()


@router.message(Command("help"))
async def get_help_command(msg: Message):
    kaz = InlineKeyboardButton(text="Kaz", callback_data='Kz')
    eng = InlineKeyboardButton(text="Eng", callback_data='En')
    await msg.answer("Choose a language / Тілді таңдаңыз:",
                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[[kaz, eng]]))


async def send_long_message(bot, chat_id, text):
    chunks = [text[i:i + 2048] for i in range(0, len(text), 2048)]
    for chunk in chunks:
        await bot.send_message(chat_id, chunk)


@router.callback_query(lambda c: c.data == 'Kz')
async def process_callback_kz(callback_query: CallbackQuery):
    text = """
    Мұнда қолданылатын командалар:\n
/start - ботты бастау үшін
/profile - озіңіздін leetcode профилі алу үшін
/leetcode - формат: '/leetcode username' leetcode профилін алу үшін
/delete_profile - профиль ошыру үшін
/tc - бyгiнгі челлендж
/rating - топ 100 рейтынгы жаксы адамды алу
    """
    await send_long_message(callback_query.bot, callback_query.from_user.id, text)


@router.callback_query(lambda c: c.data == 'En')
async def process_callback_en(callback_query: CallbackQuery):
    text = """
    Here are the available commands:
/start - Start the bot
/profile - Get Leetcode profile
/leetcode - Add Leetcode profile
/delete_profile - Delete Leetcode profile
/tc - Report a bug
/rating - Get list top 100 users
    """
    await send_long_message(callback_query.bot, callback_query.from_user.id, text)


@router.message(Command("start"))
async def start_handler(msg: Message, db: Session = get_db()):
    await msg.answer("Сәлем, мен Leetcode күндік chalange есептерін жіберетін бот болам"
                     )
    repository.create_user(db, msg.from_user.id, msg.from_user.username)


@router.message(Command("profile"))
async def get_profile(msg: Message, db: Session = get_db()):
    user_id = msg.from_user.id
    user_profile = repository.get_user_by_tg_id(db, user_id)

    if user_profile:
        user_data = f"Username: {user_profile.username}\n"

        if user_profile.leetcode:
            leetcode_data = get_leetcode_info(user_profile.leetcode[0].username)
            if leetcode_data['total_solved'] != user_profile.leetcode[0].total_solved:
                repository.update_leetcode(db,
                                           total=leetcode_data["total_solved"],
                                           hard=leetcode_data["hard_solved"],
                                           medium=leetcode_data["medium_solved"],
                                           easy=leetcode_data["easy_solved"],
                                           rating=leetcode_data["ranking"],
                                           telegram_id=msg.from_user.id)

            for leetcode_profile in user_profile.leetcode:
                user_data += (
                    f"\n"
                    f"Leetcode username: {leetcode_profile.username}\n"
                    f"Total Solved: {leetcode_profile.total_solved}\n"
                    f"Hard Solved: {leetcode_profile.hard_solved}\n"
                    f"Easy solved: {leetcode_profile.easy_solved}\n"
                    f"Medium Solved: {leetcode_profile.medium_solved}\n"
                    f"Rating: {leetcode_profile.rating}\n\n"
                )

        await msg.answer(user_data)
    else:
        await msg.answer("Пайдалушы табылмады.")


@router.message(Command("leetcode"))
async def get_user_leetcode_username(msg: Message, db: Session = get_db()):
    user_profile = repository.get_user_by_tg_id(db, msg.from_user.id)

    if user_profile and user_profile.leetcode:
        await msg.answer(
            "Егер сізде Leetcode профилі тікелген болса, оны көру үшін /profile түймесін басыңыз. Жана профилді "
            "тіркеу үшін /delete_profile түймесін басып, жана ақаунтыңызды тіркеуге болады")
    elif len(msg.text.split()) != 2:
        await msg.answer("Отiнем дұрыс форматта енгізуіңіздi сұраймын.\nМысалы - /leetcode пайдаланушы аты")
    else:
        username = msg.text.split()[1]
        data = get_leetcode_info(username)
        if data != "Пайдаланушы табылмады":
            await msg.answer("Рахмет! Сiздiн Leetcode профилінiз тіркелді, тексеру yшiн /profile")
            repository.create_leetcode(db, username=username,
                                       total=data["total_solved"],
                                       hard=data["hard_solved"],
                                       medium=data["medium_solved"],
                                       easy=data["easy_solved"],
                                       rating=data["ranking"],
                                       telegram_id=msg.from_user.id)
        else:
            await msg.answer("қате Leetcode пайдалуншы аты. Отинем қайта енгiзiнiздi отiнемiн.")


@router.message(Command("delete_profile"))
async def delete_profile(msg: Message, db: Session = get_db()):
    user_profile = repository.get_user_by_tg_id(db, msg.from_user.id)

    if user_profile and user_profile.leetcode:
        ya = InlineKeyboardButton(text="Келiсемiн", callback_data='Ya')
        joq = InlineKeyboardButton(text="Догару", callback_data='Joq')
        await msg.answer("Сіз профильді өшіруге сенімдісіз бе?",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[[ya, joq]]))
    else:
        await msg.answer("Сізде тіркелген парақша жоқ((((")


@router.callback_query(lambda c: c.data == 'Ya')
async def process_callback_yes(callback_query: CallbackQuery, db: Session = get_db()):
    user = repository.get_user_by_tg_id(db, callback_query.from_user.id)
    if user.leetcode:
        repository.delete_leetcode(db, callback_query.from_user.id)
        await callback_query.answer("Парақша өшірілді.")
    else:
        await callback_query.answer("Парақша табылмады")


@router.callback_query(lambda c: c.data == 'Joq')
async def process_callback_no(callback_query: CallbackQuery, db: Session = get_db()):
    user = repository.get_user_by_tg_id(db, callback_query.from_user.id)

    if user.leetcode:
        await callback_query.answer("Өшіру догарылды")

    else:
        await callback_query.answer("Парақша табылмады")


@router.message(Command('tc'))
async def get_todays_challenge(msg: Message):
    await msg.answer(get_formatted(), parse_mode=ParseMode.MARKDOWN)


def get_formatted():
    daily = get_problem_details(fetch_daily_coding_challenge())
    title, description, input_data = daily
    temp = description
    description = description.split("Example 1")
    example = temp[temp.find("Example 1"):temp.find("Constraints")]
    constraints = temp[temp.find("Constraints"):]
    formatted_message = f"""
    *Leetcode Daily Challenge*
*Title*: {title}

*Description*:
{description[0]}

*Examples*:
{example}

*Constraints*
{constraints}

*URL*
https://leetcode.com/problems/{str(title).replace(" ", "-").replace("'", "")}/
        """.strip()
    return formatted_message


@router.message(Command("rating"))
async def get_top_100(msg: Message, db: Session = get_db()):
    await msg.answer("Куте турыныз деректер алынуда")
    users = ""
    for i in repository.get_top_100_user(db):
        users += f"{i[0]}     {i[1]}\n"

    await msg.answer("Топ 100 рейтингы жогары колданушы\n\n"
                     + "Username     Leetcode-Rating\n" +
                     users)
