from aiogram import types, F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import executor as executor
from google.oauth2 import service_account
import googleapiclient.discovery
from aiohttp import web

from aiogram.fsm.storage.memory import MemoryStorage, State
from aiogram.filters.state import StatesGroup

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os
from google.oauth2.credentials import Credentials

# from httplib2 import Credentials


# import secure

availabelButtons = ['Continue', 'Cancel']


# bot = Bot(secure.BOT_TOKEN)
bot = Bot("6428549800:AAGC4VYwauwge6pbO-WXJ7EyIINw5Uj3u-E")
router = Router()


# файл с учетными данными гугл
SERVICE_ACCOUNT_FILE = 'creds1.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def makeRowKyeboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text = item) for item in items]
    return ReplyKeyboardMarkup(keyboard = [row], resize_keyboard = True)


# Создание класса состояний
class EventStates(StatesGroup):
    name = State()  # Состояние для ввода названия события
    start_date = State()  # Состояние для ввода даты начала события
    start_time = State()  # Состояние для ввода времени начала события
    end_date = State()  # Состояние для ввода даты окончания события
    end_time = State()  # Состояние для ввода времени окончания события
    description = State()  # Состояние для ввода описания события


# Создание события в Google Calendar
async def create_event(event_data):
    print(event_data)
    SERVICE_ACCOUNT_FILE = '/Users/alexag/Desktop/googleBot/creds1.json'
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/calendar']
    )
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': event_data['summary'],
        'start': {
            'dateTime': event_data['start_datetime'],
            'timeZone': 'Europe/Moscow',
        },
        'end': {
            'dateTime': event_data['end_datetime'],
            'timeZone': 'Europe/Moscow',
        },
        'description': event_data['description'],
    }

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('creds1.json'):
        creds = Credentials.from_authorized_user_file('creds1.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds1.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('creds1.json', 'w') as token:
            token.write(creds.to_json())

    

    try:
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        service.events().insert(calendarId='3849e27ee5d66228f160fe12d6ba15dc5399e96d573787fb5190d45884c57b64@group.calendar.google.com', body=event).execute()
        # events = service.events()
        # insertOp = events.insert(calendarId='3849e27ee5d66228f160fe12d6ba15dc5399e96d573787fb5190d45884c57b64@group.calendar.google.com', body=event)
        # result = insertOp.execute()



    
        return event.get('htmlLink')
    except Exception as err:

        print(err)

# Роутер добавки ивента
@router.message(F.text.lower() == "add an event")
async def start(message: types.Message, state: FSMContext):
    await message.reply("Send the name of event")
    await state.set_state(EventStates.name)  # Установка состояния на ввод названия события

# Машина состояния имени
@router.message(EventStates.name)
async def process_event_name_step(message: types.Message, state: FSMContext):
    event_data = {'summary': message.text}
    await message.reply("Введите дату начала события в формате ДД.ММ.ГГГГ:")
    await state.set_state(EventStates.start_date)  # Установка состояния на ввод даты начала события
    await state.update_data(event_data)  # Сохранение данных в состоянии

    


# Машина состояния даты
@router.message(EventStates.start_date)
async def process_event_start_date_step(message: types.Message, state: FSMContext):
    try:
        start_date = datetime.datetime.strptime(message.text, '%d.%m.%Y').date()
        event_data = await state.get_data()
        event_data['start_datetime'] = start_date.isoformat()
        await message.reply("Введите время начала события в формате ЧЧ:ММ")
        await state.set_state(EventStates.start_time)  # Установка состояния на ввод времени начала события
        await state.update_data(event_data)  # Сохранение данных в состоянии
    except ValueError:
        await message.reply("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ")


# Машина состояния времени
@router.message(EventStates.start_time)
async def process_event_start_time_step(message: types.Message, state: FSMContext):
    try:
        start_time = datetime.datetime.strptime(message.text, '%H:%M').time()
        event_data = await state.get_data()
        event_data['start_datetime'] = start_time.isoformat()
        await message.reply("Введите дату окончания события в формате ДД.ММ.ГГГГ")
        await state.set_state(EventStates.end_date)  # Установка состояния на ввод даты окончания события
        await state.update_data(event_data)  # Сохранение данных в состоянии
    except ValueError:
        await message.reply("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ")


# Машина состояния конца даты
@router.message(EventStates.end_date)
async def process_event_end_date_step(message: types.Message, state: FSMContext):
    try:
        end_date = datetime.datetime.strptime(message.text, '%d.%m.%Y').date()
        event_data = await state.get_data()
        event_data['end_datetime'] = end_date.isoformat()
        await message.reply("Введите время окончания события в формате ЧЧ:ММ")
        await state.set_state(EventStates.end_time)  # Установка состояния на ввод времени окончания события
        await state.update_data(event_data)  # Сохранение данных в состоянии
    except ValueError:
        await message.reply("Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ:")


# Машина состояния конца времени
@router.message(EventStates.end_time)
async def process_event_end_time_step(message: types.Message, state: FSMContext):
    try:
        end_time = datetime.datetime.strptime(message.text, '%H:%M').time()
        event_data = await state.get_data()
        event_data['end_datetime'] = end_time.isoformat()
        await message.reply("Введите описание события:")
        await state.set_state(EventStates.description)  # Установка состояния на ввод описания события
        await state.update_data(event_data)  # Сохранение данных в состоянии
    except ValueError:
        await message.reply("Неверный формат времени. Пожалуйста, введите время в формате ЧЧ:ММ:")


# Машина состояния описания
@router.message(EventStates.description)
async def process_event_description_step(message: types.Message, state: FSMContext):
    event_data = await state.get_data()
    event_data['description'] = message.text

    # Создание события в Google Calendar
    try:
        await create_event(event_data)
    except Exception as Er:
        print(Er)




    

    await message.reply("Событие успешно создано!")
    await state.clear()  # Очистка состояния
