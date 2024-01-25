from aiogram import Bot, Dispatcher, executor, types

import config.bot_config as bot_config
from lores_image import ImagesHandler
import resources.markups as markups
import resources.texts as texts
import database as db
import os

bot = Bot(bot_config.BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    db.db_delete_user_data(user_id)
    db.db_insert_ids(user_id)
    await bot.send_message(user_id, f"Привет, {message.from_user.first_name}!")
    await bot.send_message(user_id, texts.intro, reply_markup=markups.auth)


@dp.message_handler()
async def bot_message(message: types.Message):
    user_id = message.from_user.id
    if (message.chat.type == 'private'):
        if (message.text == 'VERIFY'):
            db.db_set_state("login", user_id)
            await bot.send_message(user_id, "Введите Логин:")
        elif (message.text != bot_config.bot_login and db.db_get_state(user_id) == "login"):
            await bot.send_message(user_id, "Введите Логин:")
        elif (message.text == bot_config.bot_login and db.db_get_state(user_id) == "login"):
            db.db_set_state("pass", user_id)
            await bot.send_message(user_id, "Введите Пароль:")
        elif (message.text != bot_config.bot_password and db.db_get_state(user_id) == "pass"):
            await bot.send_message(user_id, "Введите Пароль:")
        elif (message.text == bot_config.bot_password and db.db_get_state(user_id) == "pass"):
            db.db_set_state("person", user_id)
            db.db_set_auth("done", user_id)
            await bot.send_message(user_id, "Поздравляем, вы успешно верифицированы!", 
                                    reply_markup=markups.person)
        elif (db.db_get_auth(user_id) == "done"):
            if (message.text == 'Добавить ФИО'):
                db.db_set_state("name", user_id)
                await bot.send_message(user_id, "Введите Имя:")
            elif (db.db_get_state(user_id) == "name"):
                db.db_set_name(message.text, user_id)
                db.db_set_state("surname", user_id)
                await bot.send_message(user_id, "Введите Фамилию:")
            elif (db.db_get_state(user_id) == "surname"):
                db.db_set_surname(message.text, user_id)
                db.db_set_state("bio", user_id)
                data = db.db_get_names(user_id)
                await bot.send_message(user_id, f"Спасибо, {data[0]} {data[1]}, рады знакомству!",
                                        reply_markup=markups.bio)
            elif (message.text == 'Добавить ФОТО'):
                await bot.send_message(user_id, texts.photo)
            elif (message.text == 'Узнать статус'):
                status_enter = db.db_get_status(user_id)
                if status_enter == 'in':
                    await bot.send_message(user_id, 'В офисе.')
                else:
                    await bot.send_message(user_id, 'Покинул офис.')
            else:
                await bot.send_message(user_id, "Не понимаю")
        else:
            await bot.send_message(user_id, "Попробуйте снова (VERIFY):")


@dp.message_handler(content_types=['photo'])
async def photo_handler(message: types.Message):
    user_id = message.from_user.id
    if (db.db_get_state(user_id) != "status") :
        photo_path = f"images/photo{user_id}.jpg"
        photo = message.photo[-1]
        await bot.download_file_by_id(photo.file_id, photo_path)
        ph = ImagesHandler(path_image_directory=photo_path, BASEWIDTH=500)
        ph.process_images()
        new_photo_path = f"images/new/photo{user_id}.jpg"
        db.db_add_photo(new_photo_path, user_id)
        db.db_set_state("status", user_id)
        os.remove(photo_path)
        os.remove(new_photo_path)
        data = db.db_get_names(user_id)
        await bot.send_message(user_id, 
                                f"Спасибо, {data[0]} {data[1]}. Ваше фото добавлено.",
                                reply_markup=markups.status)
    else:
        data = db.db_get_names(user_id)
        await bot.send_message(user_id, 
            f"{data[0]}, ваше фото уже добавлено. Чтобы поменять его, вам необходимо обратиться к начальству.")


if (__name__ == '__main__'):
    executor.start_polling(dp, skip_updates = True)