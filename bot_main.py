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
    await db.db_delete_user_data(user_id)
    await db.db_insert_ids(user_id)
    await bot.send_message(user_id, f"Привет, {message.from_user.first_name}!")
    await bot.send_message(user_id, texts.intro)
    await bot.send_message(user_id, "Чтобы продолжить, нажми на кнопку 'VERIFY'.", reply_markup=markups.auth)

@dp.message_handler()
async def bot_message(message: types.Message):
    user_id = message.from_user.id
    if (message.chat.type == 'private'):
        if (message.text == 'VERIFY'):
            await db.db_set_state("login", user_id)
            await bot.send_message(user_id, "Введите Логин:")
        elif (message.text != bot_config.bot_login and await db.db_get_state(user_id) == "login"):
            await bot.send_message(user_id, "Введите Логин:")
        elif (message.text == bot_config.bot_login and await db.db_get_state(user_id) == "login"):
            await db.db_set_state("pass", user_id)
            await bot.send_message(user_id, "Введите Пароль:")
        elif (message.text != bot_config.bot_password and await db.db_get_state(user_id) == "pass"):
            await bot.send_message(user_id, "Введите Пароль:")
        elif (message.text == bot_config.bot_password and await db.db_get_state(user_id) == "pass"):
            await db.db_set_state("person", user_id)
            await db.db_set_auth("done", user_id)
            await bot.send_message(user_id, "Поздравляем, вы успешно верифицированы!\nЧтобы продолжить, нажми на кнопку 'Добавить ФИО'", 
                                    reply_markup=markups.person)
        elif (await db.db_get_auth(user_id) == "done"):
            if (message.text == 'Добавить ФИО'):
                await db.db_set_state("name", user_id)
                await bot.send_message(user_id, "Введите Имя:")
            elif (await db.db_get_state(user_id) == "name"):
                await db.db_set_name(message.text, user_id)
                await db.db_set_state("surname", user_id)
                await bot.send_message(user_id, "Введите Фамилию:")
            elif (await db.db_get_state(user_id) == "surname"):
                await db.db_set_surname(message.text, user_id)
                await db.db_set_state("bio", user_id)
                data = await db.db_get_names(user_id)
                await bot.send_message(user_id, f"Спасибо, {data[0]}, рады знакомству!\nЧтобы продолжить, нажми на кнопку 'Добавить ФОТО'",
                                        reply_markup=markups.bio)
            elif (message.text == 'Добавить ФОТО'):
                await bot.send_message(user_id, texts.photo)
            elif (message.text == 'Узнать статус'):
                status_enter = await db.db_get_status(user_id)
                if status_enter == 'in':
                    await bot.send_message(user_id, 'В офисе.')
                else:
                    await bot.send_message(user_id, 'Покинул офис.')
            else:
                await bot.send_message(user_id, "Не понимаю")
        else:
            await bot.send_message(user_id, "Попробуйте снова (VERIFY)")


@dp.message_handler(content_types=['photo'])
async def photo_handler(message: types.Message):
    user_id = message.from_user.id
    if (await db.db_get_state(user_id) != "status") :
        photo_path = f"images/photo{user_id}.jpg"
        photo = message.photo[-1]
        await bot.download_file_by_id(photo.file_id, photo_path)
        ph = ImagesHandler(path_image_directory=photo_path, BASEWIDTH=500)
        ph.process_images()
        new_photo_path = f"images/new/photo{user_id}.jpg"
        await db.db_add_photo(new_photo_path, user_id)
        await db.db_set_state("status", user_id)
        os.remove(photo_path)
        os.remove(new_photo_path)
        data = await db.db_get_names(user_id)
        await bot.send_message(user_id, 
                                f"Спасибо, {data[0]}. Ваше фото добавлено.\n\nЧтобы отследить свое местоположение, нажми на кнопку 'Узнать статус'",
                                reply_markup=markups.status)
    else:
        data = await db.db_get_names(user_id)
        await bot.send_message(user_id, 
            f"{data[0]}, ваше фото уже добавлено. Чтобы поменять его, вам необходимо обратиться к администратору БД за помощью.")


if (__name__ == '__main__'):
    executor.start_polling(dp, skip_updates = True)