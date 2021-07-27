import logging
import json

from aiogram import Bot, Dispatcher, executor, types

from models import User
from defs import the_counter, get_msg, get_user, user_create, send
import config as cfg


logging.basicConfig(level=cfg.logging_level)


bot = Bot(token=cfg.bot_token, parse_mode='html')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        text = ("Salut. Dans le chat privé, vous ne pouvez accéder qu'au commande."
                '/balance.')
        await message.answer(text)


@dp.message_handler(commands=['send'])
async def send_cmd(message: types.Message):
    if message.chat.type == 'group'\
    or message.chat.type == 'supergroup'\
    and message.chat.id in cfg.aviable_chats:
        try:
            sum = int(message.text.split(' ')[1])
            if message.reply_to_message:
                await send(sum, message=message)
            else:
                text = ('Pour transférer les pièces, vous devez répondre '
                        'au message du destinataire.')
                await message.reply(text)
        except:
            text = ('Vous avez mal saisi la commande. La manière correcte est:'
                    ' <code>/envoyer le montant</code>')
            await message.reply(text)
    await the_counter(message)


@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):
    user = await get_user(str(message.from_user.id))
    if user:
        await message.reply(f'Ваш баланс: {str(user.balance)} монет.')
    else:
        if message.chat.id in cfg.aviable_chats:
            await user_create(message.from_user)
            await message.reply('Vous avez enregistré un portefeuille.')
        else:
            await message.reply("Vous n'avez pas de portefeuille.")
    await the_counter(message)


@dp.message_handler(commands=['get_chat'])
async def get_chat(message: types.Message):
    text = 'Chat ID: <code>' + str(message.chat.id) + '</code>.'
    await message.reply(text)


@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    await get_msg(message)


@dp.message_handler()
async def get_message(message: types.Message):
    if message.new_chat_members:
        for user in message.new_chat_members:
            if user.is_bot == False:
                if get_user(str(user.id)) == False:
                    await user_create(user)
                    await the_counter(message)
    if message.left_chat_member:
        if get_user(str(message.left_chat_member.id)):
            id = str(message.left_chat_member.id)
            User.delete().where(id == id).execute()


async def on_startup(dp):
    await bot.set_my_commands([types.BotCommand('envoyer',
                                                'Convertir vos pièces en FIAT'),
                               types.BotCommand('balance',
                                                'Voir le solde')])


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
