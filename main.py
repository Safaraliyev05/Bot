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

cumulative_user_actions = {
    'started': set(),
    'first_lesson': set(),
    'second_lesson': set(),
    'third_lesson': set(),
    'fourth_lesson': set()
}


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

tr_reminder_keyboard = InlineKeyboardBuilder()
tr_reminder_keyboard.row(InlineKeyboardButton(text="Ha ko'rdim, bonus dars bering!", callback_data="fourth_lesson"))
tr_reminder_keyboard.row(InlineKeyboardButton(text="Yo'q, hoziroq ko'raman", callback_data="watch_third_lesson"))

for_reminder_keyboard = InlineKeyboardBuilder()
for_reminder_keyboard.row(InlineKeyboardButton(text="Ha, anketani bering", callback_data="google_form"))

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
    first_video = FSInputFile('media/teasers/first_teaser.mp4')
    await bot.send_video(
        chat_id=message.chat.id,
        video=first_video,
        width=720, height=405
    )

    await bot.send_message(
        chat_id=message.chat.id,
        reply_markup=first_lesson_keyboard.as_markup(),
        text='Text message'
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
        reply_markup=first_lesson_keyboard.as_markup(),
        text='Text message'

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

    first_video = FSInputFile('media/teasers/second_teaser.mp4')
    await bot.send_video(
        chat_id=query.message.chat.id,
        video=first_video,
    )

    await bot.send_message(
        chat_id=query.message.chat.id,
        reply_markup=second_lesson_keyboard.as_markup(),
        text='Text message'
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
        reply_markup=second_lesson_keyboard.as_markup(),
        text='Text message'
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
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
        reply_markup=third_lesson_keyboard.as_markup(),
        text='Text message'
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
        reply_markup=third_lesson_keyboard.as_markup(),
        text='Text message'
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
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
        reply_markup=fourth_lesson_keyboard.as_markup(),
        text='Text message'
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
        reply_markup=fourth_lesson_keyboard.as_markup(),
        text='Text message'
    )

    await asyncio.create_task(
        send_message_after_delay(
            chat_id=query.message.chat.id,
            delay_minutes=10,
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


@dp.message(Command('users'))
async def send_user_info(message: Message) -> None:
    data = {
        "Name": [info['name'] for info in user_info.values()],
        "Phone Number": [info['phone_number'] for info in user_info.values()]
    }
    df = pd.DataFrame(data)

    file_path = "media/users.xlsx"
    df.to_excel(file_path, index=False)

    await bot.send_document(chat_id=message.chat.id, document=FSInputFile(file_path))


async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Polling failed: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
