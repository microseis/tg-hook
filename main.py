import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from fastapi import FastAPI

BOT_TOKEN = os.getenv("BOT_TOKEN")
NGROK_URL = os.getenv("NGROK_URL")

WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
WEB_SERVER_PORT = os.getenv("WEB_SERVER_PORT")

WEBHOOK_PATH = os.getenv("WEBHOOK_PATH")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Обработчик при нажати на команду `/start`"""
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@router.message()
async def echo_handler(message: types.Message) -> None:
    """Дублирование отправленного сообщения ботом"""
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")


dp = Dispatcher()
dp.include_router(router)

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(f"{NGROK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )

    uvicorn.run(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
