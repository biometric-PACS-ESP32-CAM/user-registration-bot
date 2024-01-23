from aiogram import Bot, Dispatcher, executor, types

import bot_config
import markups
import texts
import database

bot = Bot(bot_config.BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}!")
    await bot.send_message(message.from_user.id, texts.intro, reply_markup=markups.auth)


flg_verify, flg_login , flg_pass = False
flg_person, flg_name = False
@dp.message_handler()
async def bot_message(message: types.Message):
    if (message.chat.type == 'private'):
        if (message.text == 'VERIFY'):
            flg_verify = True
            await bot.send_message(message.from_user.id, "Введите Логин:")
        elif (message.text == bot_config.bot_login and flg_verify):
            flg_login = True
            await bot.send_message(message.from_user.id, "Введите Пароль:")
        elif (message.text == bot_config.bot_password and flg_verify and flg_login):
            flg_pass = True
            await bot.send_message(message.from_user.id, 
                                    "Поздравляем, вы успешно верифицированы!",
                                    reply_markup=markups.person)
        elif (flg_pass): # auth done
            if (message.text == 'Добавить ФИО'):
                flg_person = True
                await bot.send_message(message.from_user.id, "Введите Имя:")
            elif (flg_person):
                flg_name = True
                await bot.send_message(message.from_user.id, "Введите Фамилию:")
            elif (flg_person and flg_name):
                flg_person, flg_name = False
                await bot.send_message(message.from_user.id, 
                                        "Рады знакомству!",
                                        reply_markup=markups.bio)
            if (message.text == 'Добавить ФОТО'):
                await bot.send_message(message.from_user.id, texts.photo)
        else:
            await bot.send_message(message.from_user.id, "Попробуйте снова (VERIFY):")

if (__name__ == '__main__'):
    executor.start_polling(dp, skip_updates = True)