from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_auth = KeyboardButton('VERIFY')
btn_person = KeyboardButton('Добавить ФИО')
btn_bio = KeyboardButton('Добавить ФОТО')

auth = ReplyKeyboardMarkup(resize_keyboard = True)
auth.add(btn_auth)

person = ReplyKeyboardMarkup(resize_keyboard = True)
person.add(btn_person)

bio = ReplyKeyboardMarkup(resize_keyboard = True)
bio.add(btn_bio)