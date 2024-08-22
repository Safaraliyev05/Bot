import asyncio
import logging
import os
import sys

import pandas as pd
from aiogram import F, Dispatcher, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv('TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
bot = Bot(TOKEN)
dp = Dispatcher()

user_states = {}
user_info = {}

user_actions = {
    'started': set(),
    'first_lesson': set(),
    'second_lesson': set(),
    'third_lesson': set(),
    'fourth_lesson': set()
}

# Cumulative tracking dictionary
cumulative_user_actions = {
    'started': set(),
    'first_lesson': set(),
    'second_lesson': set(),
    'third_lesson': set(),
    'fourth_lesson': set()
}


# Keyboards
def create_lesson_keyboard(url):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Darsni ko'rish📹", url=url))
    keyboard.adjust(1)
    return keyboard


first_lesson_keyboard = create_lesson_keyboard('http://jahongirprank.uz/1-darslik/')
second_lesson_keyboard = create_lesson_keyboard('http://jahongirprank.uz/2-darslik/')
third_lesson_keyboard = create_lesson_keyboard('http://jahongirprank.uz/3-darslik/')
fourth_lesson_keyboard = create_lesson_keyboard('http://jahongirprank.uz/4-darslik/')

fr_reminder_keyboard = InlineKeyboardBuilder()
fr_reminder_keyboard.row(InlineKeyboardButton(text="Ha ko'rdim, bonus dars bering!", callback_data="second_lesson"))
fr_reminder_keyboard.row(InlineKeyboardButton(text="Yo'q, hoziroq ko'raman", callback_data='watch_first_lesson'))

sr_reminder_keyboard = InlineKeyboardBuilder()
sr_reminder_keyboard.row(InlineKeyboardButton(text="Ha ko'rdim, bonus dars bering", callback_data="third_lesson"))
sr_reminder_keyboard.row(InlineKeyboardButton(text="Hoziroq ko'raman", callback_data="watch_second_lesson"))

tr_reminder_keyboard = InlineKeyboardBuilder()
tr_reminder_keyboard.row(InlineKeyboardButton(text="Ha ko'rdim, bonus dars bering!", callback_data="fourth_lesson"))
tr_reminder_keyboard.row(InlineKeyboardButton(text="Yo'q, hoziroq ko'raman", callback_data="watch_third_lesson"))

for_reminder_keyboard = InlineKeyboardBuilder()
for_reminder_keyboard.row(InlineKeyboardButton(text="Ha, anketani bering", callback_data="google_form"))
for_reminder_keyboard.row(InlineKeyboardButton(text="Videoni endi ko'raman", callback_data="watch_fourth_lesson"))

google_form_k = InlineKeyboardBuilder()
google_form_k.row(InlineKeyboardButton(text="Anketani to'ldirish", url="https://forms.gle/6HCyDD4QBwqrXWNF8"))
google_form_k.adjust(1)

admin_kb = InlineKeyboardBuilder()
admin_kb.row(InlineKeyboardButton(text='Admin', url='@JahongirPrankAdmin'))

# Collect user info keyboard
user_info_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Send Contact", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


async def send_message_after_delay(chat_id, delay_minutes, message=None, video=None, video_note=None, audio=None,
                                   image=None, reply_markup=None):
    try:
        await asyncio.sleep(delay_minutes * 60)
        if message:
            await bot.send_message(chat_id, message, reply_markup=reply_markup)
        if video:
            await bot.send_video(chat_id, video=video)
        if video_note:
            await bot.send_video_note(chat_id, video_note=video_note)
        if audio:
            await bot.send_audio(chat_id, audio=audio)
        if image:
            await bot.send_photo(chat_id, photo=image)
    except Exception as e:
        logging.error(f"Failed to send message after delay: {e}")


@dp.message(CommandStart())
async def first_lesson(message: Message) -> None:
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = 'collecting_info'
        user_actions['started'].add(user_id)
        await message.answer("Please send your contact info to proceed.", reply_markup=user_info_keyboard)
        return

    if user_id not in user_info:
        await message.answer("Please send your contact info to proceed.", reply_markup=user_info_keyboard)
        return

    user_states[user_id] = 'first_lesson'
    user_actions['first_lesson'].add(user_id)  # Update action tracking
    first_video = FSInputFile('media/teasers/first_teaser.mp4')
    await bot.send_video(
        chat_id=message.chat.id,
        video=first_video,
        width=720, height=405
    )

    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Hey you, what's up {message.from_user.first_name}👋🏻\n\n"
             f"🕸Man Spiderman - Jahongir Saylavov sun'iy yordamchilari bo'laman😎\n\n"
             f"Grammatikasiz speaking chiqarishni isbotlab beradigan DARSLIK shu yerda 👇🏻 \n\n"
             f"📌Eslatib o'taman, darslik 24 soatdan keyin o'chib ketadi🫡\n",
        reply_markup=first_lesson_keyboard.as_markup()
    )

    video_note_file = FSInputFile('circle_videos/teaser_one.mp4')
    await asyncio.create_task(
        send_message_after_delay(
            chat_id=message.chat.id,
            delay_minutes=1,
            video_note=video_note_file
        )
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=message.chat.id,
            delay_minutes=10,
            message="🫢1 soat ichida darslikni ko'rgan obunachilarimga, "
                    "BONUS sifatida yana bitta darslik sovg'a qilmoqchiman🎁\n\n"
                    "Shustriy bo'lsez, ulgurib qolasiz✊🏻",
            reply_markup=fr_reminder_keyboard.as_markup()
        )
    )


@dp.message(F.content_type == 'contact')
async def collect_user_info(message: Message) -> None:
    user_id = message.from_user.id
    if user_states.get(user_id) == 'collecting_info':
        user_info[user_id] = {
            'name': message.contact.first_name,
            'phone_number': message.contact.phone_number
        }
        await first_lesson(message)


@dp.callback_query(F.data == 'watch_first_lesson')
async def watch_first_lesson(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_states.get(user_id) == 'watch_first_lesson':
        await query.answer("You have already selected an option.")
        return

    user_states[user_id] = 'watch_first_lesson'

    await query.message.reply(
        text=f"Hey, {query.from_user.first_name}\n\n"
             f"🗣Agar siz haliyam ZO'R SPEAKING uchun GRAMMATIKA YODLASH kerak deb o'ylasez,\n\n"
             f"bepul darslikdan keyin aniq fikriz o'zgaradi💯\n\n"
             f"*Videodars 24 soatdan keyin o'chadi, tezroq ko'rishni maslahat beraman 🫡",
        reply_markup=first_lesson_keyboard.as_markup()
    )

    audio = FSInputFile('audio_2024-07-24_05-23-07.ogg')
    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=1,
            audio=audio
        )
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
            message=f"Sizga YOMON XABAR bor 🫢\n\n"
                    f"Bilaman, ishlar bilan bo'lib, darsni ko'rishga vaqt topolmagan bo'lishiz mumkin🙍🏻\n\n"
                    f"🇺🇸Lekin sizda ingliz tilini OSON va QIZIQARLI o'rganishingiz uchun\n\n"
                    f"📌Keyin, $*000 pul to'lasangiz ham bu darsni ololmaysiz!",
            reply_markup=fr_reminder_keyboard.as_markup()
        )
    )


@dp.callback_query(F.data == 'second_lesson')
async def second_lesson(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_states.get(user_id) == 'second_lesson':
        await query.answer("You have already selected an option.")
        return

    user_states[user_id] = 'second_lesson'
    user_actions['second_lesson'].add(user_id)  # Update action tracking

    first_video = FSInputFile('media/teasers/second_teaser.mp4')
    await bot.send_video(
        chat_id=query.message.chat.id,
        video=first_video,
    )

    await bot.send_message(
        chat_id=query.message.chat.id,
        text=f"Eee malades, {query.from_user.first_name}\n\n"
             f"Endi sizda 2-darsni ko'rish imkoniyati bor 🎁\n\n"
             f"Bu darslikda : \n\n"
             f"❗️Speaking chiqarolmaslik sabablari va yechimlari\n"
             f"❗️Bir xil qolipdagi texnikalardan qutulib, QIZIQARLI yo'lda speaking o'rganish\n"
             f"❗️Qanday qilib man bir o'zim o'rganib, amerikanlardek speaking chiqarganim haqida o'rganasiz🫡\n"
             f"🗣Sizda darslikni ko'rish uchun 24 soat vaqt bor. Shuning uchun, tezroq ko'ring✊🏻",
        reply_markup=second_lesson_keyboard.as_markup()
    )

    video_note_file = FSInputFile('circle_videos/teaser_two.mp4')
    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=1,
            video_note=video_note_file
        )
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
            message=f"Hey, {query.from_user.first_name}!\n\n"
                    f"Bonus darslik sizga yoqtimi ?\n\n"
                    f"🗣Ayniqsa, grammatikasiz speaking chiqarish degan joyiga  mazza qigandursizaa 😅 \n\n"
                    f"Agar darsni oxirgacha ko'rgan bo'lsez, sizga yana bitta dars mandan 🎁\n\n",
            reply_markup=sr_reminder_keyboard.as_markup()
        )
    )


@dp.callback_query(F.data == 'watch_second_lesson')
async def watch_second_lesson(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_states.get(user_id) == 'watch_second_lesson':
        await query.answer("You have already selected an option.")
        return

    user_states[user_id] = 'watch_second_lesson'

    await query.message.reply(
        text=f"🫣{query.from_user.first_name}, Ingliz tilida grammatika yodlashdan charchagan bo'lsez kerak a... \n\n"
             f"Qiziqarli va oson metodikada SPEAKING chiqarishga qanaqa qarisiz 🤔\n\n"
             f"🎁Bu haqida BONUS DARSLIKda tushuntirdim. \n\n"
             f"🤫Hoziroq ko'rsangiz, yana bitta darsga dostup olasiz❗️",
        reply_markup=second_lesson_keyboard.as_markup()
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
            message=f"Keling, biroz hisob-kitob qilamiz.. \n\n"
                    f"🗣Odatiy yo'l bilan ingliz tili o'rgansangiz, "
                    f"12 oydan 24  oygacha bo'lgan vaqtda yaxshi gapirasiz.\n\n"
                    f"🔝Mani metodikam bilan ingliz tili o'rgansangiz, "
                    f"3 oydan 6 oygacha bo'lgan vaqtda bemalol ravon gapirolasiz!\n\n"
                    f"🤯QANDAY QILIB ? - deyabsizmi ?\n\n"
                    f"Bu haqida bepul darslikda tushuntirib berdim🎁\n\n"
                    f"Hoziroq darsni ko'rish uchun, pastdagi tugmani bosing👇🏻",
            reply_markup=sr_reminder_keyboard.as_markup()
        )
    )


@dp.callback_query(F.data == 'third_lesson')
async def third_lesson(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_states.get(user_id) == 'third_lesson':
        await query.answer("You have already selected an option.")
        return

    user_states[user_id] = 'third_lesson'
    user_actions['third_lesson'].add(user_id)

    third_video = FSInputFile('media/teasers/third_teaser.mp4')
    await bot.send_video(
        chat_id=query.message.chat.id,
        video=third_video,
        width=720, height=405
    )

    await bot.send_message(
        chat_id=query.message.chat.id,
        text=f"3-darsni ko'rishga ulgurdiiz 🎉\n\n"
             f"Bu darslikda : \n\n"
             f"❗️Speakingni ERKIN chiqarishning maxfiy formulalari va yechimlari\n"
             f"❗️Qisqa vaqt ichida so'z boyligini oshirish usullari\n"
             f"❗️Speakingda xatolarni kamaytirish texnikalari va HACKLAR bilan bo'lishaman\n"
             f"🗣Sizda darslikni ko'rish uchun 24 soat vaqt bor. Shuning uchun, tezroq ko'ring✊🏻",
        reply_markup=third_lesson_keyboard.as_markup()
    )

    video_note_file = FSInputFile('circle_videos/teaser_three.mp4')
    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=1,
            video_note=video_note_file
        )
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
            message=f"Hey, {query.from_user.first_name}!\n\n"
                    f"Bonus darslik sizga yoqtimi ?\n\n"
                    f"🗣Ayniqsa, grammatikasiz speaking chiqarish degan joyiga mazza qigandursiz...\n\n"
                    f"🎯Hoziroq 4-darsni ko'rish uchun bonus imkoniyatga ega bo'lishingiz mumkin\n\n"
                    f"❓Siz 3-darsni ko'rdingizmi?",
            reply_markup=tr_reminder_keyboard.as_markup()
        )
    )


@dp.callback_query(F.data == 'watch_third_lesson')
async def watch_third_lesson(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_states.get(user_id) == 'watch_third_lesson':
        await query.answer("You have already selected an option.")
        return

    user_states[user_id] = 'watch_third_lesson'

    await query.message.reply(
        text=f"🗣Ingliz tilida SPEAKING qilish sizda muommo bo'lmaydi❗️\n\n"
             f"Agar siz bu darsni ko'rib, berilgan KUN TARTIBIGA amal qilsangiz🔥\n\n"
             f"Darsni ko'rish uchun pastdagi tugmani bosing👇🏻",
        reply_markup=third_lesson_keyboard.as_markup()
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
            message=f"Agar siz haliyam ingliz tili o'rganish uchun 2-4 soat vaqt ajratsangiz, "
                    f"demak juda qiyin usuldan foydalanyapsiz❗️\n\n"
                    f"🗣Keling, man sizga ham OSON, ham QIZIQARLI metodika o'rgataman🎁\n\n"
                    f"Keyin siz ingliz tili muhitini yaratib, 3 oyda ravon gapira olasiz✅\n\n"
                    f"Darslikda hammasini tushuntirib berdim👇🏻",
            reply_markup=tr_reminder_keyboard.as_markup()
        )
    )


@dp.callback_query(F.data == 'fourth_lesson')
async def fourth_lesson(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_states.get(user_id) == 'fourth_lesson':
        await query.answer("You have already selected an option.")
        return

    user_states[user_id] = 'fourth_lesson'
    user_actions['fourth_lesson'].add(user_id)

    fourth_video = FSInputFile('media/teasers/fourth_teaser.mp4')
    await bot.send_video(
        chat_id=query.message.chat.id,
        video=fourth_video,
        width=720, height=405
    )

    await bot.send_message(
        chat_id=query.message.chat.id,
        text=f"4-darsni ko'rishga ulgurdiiz 🎉\n\n"
             f"Bu darslikda : \n\n"
             f"❗️Speakingda shubha va qo'rquvlarni yengish texnikalari\n"
             f"❗️O'zbek tilidan ingliz tiliga oson o'tish metodlari\n"
             f"❗️Mashhur video darsliklardan foydalanib, mazza qilib o'rganish usullari\n"
             f"🗣Sizda darslikni ko'rish uchun 24 soat vaqt bor. Shuning uchun, tezroq ko'ring✊🏻",
        reply_markup=fourth_lesson_keyboard.as_markup()
    )

    video_note_file = FSInputFile('circle_videos/teaser_four.mp4')
    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=1,
            video_note=video_note_file
        )
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
            message=f"Hey, {query.from_user.first_name}!\n\n"
                    f"Bonus darslik sizga yoqtimi ?\n\n"
                    f"🗣Ayniqsa, grammatikasiz speaking chiqarish degan joyiga mazza qigandursiz...\n\n"
                    f"🎯Anketani to'ldiring va yana bir BONUS darslik sovg'a qiling\n\n"
                    f"❓Siz 4-darsni ko'rdingizmi?",
            reply_markup=for_reminder_keyboard.as_markup()
        )
    )


@dp.callback_query(F.data == 'watch_fourth_lesson')
async def watch_fourth_lesson(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    if user_states.get(user_id) == 'watch_fourth_lesson':
        await query.answer("You have already selected an option.")
        return

    user_states[user_id] = 'watch_fourth_lesson'

    await query.message.reply(
        text=f"Bilasizmi, {query.from_user.first_name}\n\n"
             f"📌Bu video hammasidan ham muhim, chunki bu videodan keyin siz\n\n"
             f"Hayotingizda katta qaror qabul qilasiz❗️\n\n"
             f"- Yoki ingliz tili o'rganishni boshlaysiz va rivojlanasiz\n"
             f"- Yoki videoni ko'rmay, bir xil holatda qolib ketasiz!\n\n"
             f"Eng yomoni ingliz tilini samarasiz metodikalarda o'rganishni davom etib, "
             f"yillab vaqtingizu millionlab pullarizni bekorga sarf qivorasiz...\n\n"
             f"Tanlov o'zizda, shustri bo'ling 😉",
        reply_markup=fourth_lesson_keyboard.as_markup()
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
            message=f"'JUST SPEAK' kursim nega qo'rqmasdan O'zbekistonda yagona deyman ? \n\n"
                    f"1. Mani shaxsiy grammatikasiz speaking chiqarish metodikam boshqa ustozlarda yo'q ! \n\n"
                    f"2. Ingliz tili darajezdan qat'iy nazar, "
                    f"bu kurs sizga to'g'ri keladi. Chunki kursda hayotiy speaking ustida ishlaymiz.\n\n"
                    f"3. Faqat mani kursimda Kino ko'rib, musiqa eshitib ingliz tilida gaplashishni o'rganasiz."
                    f"Agar siz ham JUST SPEAK oilamizga qo'shilib, ingliz tilida ravon gaplashishni xohlasangiz,"
                    f"pastdagi ANKETAni to'ldiring👇🏻",
            reply_markup=for_reminder_keyboard.as_markup()
        )
    )


@dp.message(Command('report'))
async def get_report(message: Message):
    user_id = message.from_user.id

    if str(user_id) not in ADMIN_CHAT_ID:
        await message.answer("You are not authorized to access this command.")
        return

    report_text = f"Statistika\n\n" \
                  f"Start bosdi: {len(user_actions['started'])}\n" \
                  f"Birinchi dars: {len(user_actions['first_lesson'])}\n" \
                  f"Ikkinchi dars: {len(user_actions['second_lesson'])}\n" \
                  f"Uchinchi dars: {len(user_actions['third_lesson'])}\n" \
                  f"To'rtinchi dars: {len(user_actions['fourth_lesson'])}\n"

    await message.answer(report_text)


# Command to send user info as an Excel file
@dp.message(Command('users'))
async def send_user_info(message: Message) -> None:
    # Create a DataFrame from the user info dictionary
    data = {
        "Name": [info['name'] for info in user_info.values()],
        "Phone Number": [info['phone_number'] for info in user_info.values()]
    }
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    file_path = "media/users.xlsx"
    df.to_excel(file_path, index=False)

    # Send the Excel file to the user
    await bot.send_document(chat_id=message.chat.id, document=FSInputFile(file_path))


async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Polling failed: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
