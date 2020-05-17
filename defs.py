import requests

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from peewee import DoesNotExist

from models import User
import config as cfg


counter = 0


async def the_counter(message: types.Message):
    global counter
    counter += 1
    if counter >= cfg.counter_max:
        counter = 0
        await get_msg(message)


async def get_msg(message: types.Message):
    url = cfg.messages_url
    respone = requests.get(url=url)
    data = respone.json()
    for msg in data:
        keyboard = None
        if msg['reply_markup']:
            keyboard = InlineKeyboardMarkup()
            for button in msg['reply_markup']['buttons']:
                btn = InlineKeyboardButton(button['text'],
                                           url=button['url'])
                keyboard.add(btn)
        dwpp = msg['disable_web_page_preview']
        dn = msg['disable_notification']
        await message.answer(msg['text'],
                             disable_web_page_preview=dwpp,
                             disable_notification=dn,
                             reply_markup=keyboard)



async def get_user(id: str):
    try:
        user = User.get(User.id == id)
        return user
    except DoesNotExist:
        return False


async def user_create(user: types.User):
    if user.username:
        User.create(id=str(user.id), username=user.username)
    else:
        User.create(id=str(user.id))


async def send(sum: int, message: types.Message):
    rtm = message.reply_to_message
    from_user = await get_user(str(message.from_user.id))
    to_user = await get_user(str(rtm.from_user.id))
    if from_user:
        if to_user:
            if from_user.balance >= sum:
                from_user.balance = from_user.balance - sum
                to_user.balance = to_user.balance + sum

                from_user.save()
                to_user.save()

                await message.reply(f'Переведено {str(sum)} денег.')
            else:
                await message.reply('У вас недостаточно денег.')
        else:
            if rtm.from_user.is_bot == False:
                await user_create(rtm.from_user)
                await send(sum, message=message)
    else:
        await user_create(message.from_user)
        await send(sum, message=message)