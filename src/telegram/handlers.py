import os

from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command


router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Здоров, я надсилаю помилки по скрапінгу")


@router.message(Command("id"))
async def message_handler(msg: Message):
    await msg.answer(f"Твій ID: {msg.from_user.id}")


async def send_message_to_admin(message, id='278416481'):
    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode=ParseMode.HTML)
    await bot.send_message(id, message)
