from aiogram import Router, types, F
from aiogram.fsm.storage.memory import MemoryStorage, State
from aiogram.filters.state import StatesGroup
from aiogram.fsm.context import FSMContext

import executor as executor
from google.oauth2 import service_account
import googleapiclient.discovery
from aiohttp import web
from googleapiclient.discovery import build
from google.oauth2 import service_account
# Импортируйте необходимые модули для работы с Google Calendar API


storage = MemoryStorage()
router = Router()

# Создание класса состояний
class DeleteEventStates(StatesGroup):
    waiting_for_start_date = State()
    waiting_for_end_date = State()


@router.message(F.text.lower() == 'delete an event')
async def delete_event_handler(message: types.Message, state: FSMContext):
    await message.reply("Введите дату начала события в формате ГГГГ-ММ-ДД:")

    # Устанавливаем состояние ожидания ввода
    await state.set_state(DeleteEventStates.waiting_for_start_date)


@router.message(DeleteEventStates.waiting_for_start_date)
async def process_start_date(message: types.Message, state: FSMContext):
    start_date = message.text.strip() # Убираем знаки из инпута даты

    # Проверяем корректность введеннной даты 
    if not is_valid_date(start_date):
        await message.reply("Некорректный формат даты. Пожалуйста, используйте формат: ГГГГ-ММ-ДД")
        return

    # Сохр дату начала события в состоянии 
    await state.update_data(start_date=start_date)

    await message.reply("Введите дату окончания события в формате ГГГГ-ММ-ДД:")

    # состояние ожидания даты окончания события
    await state.set_state(DeleteEventStates.waiting_for_end_date)


@router.message(DeleteEventStates.waiting_for_end_date)
async def process_end_date(message: types.Message, state: FSMContext):
    end_date = message.text.strip()

    # Проверяем корректность введенной даты окончания события
    if not is_valid_date(end_date):
        await message.reply("Некорректный формат даты. Пожалуйста, используйте формат: ГГГГ-ММ-ДД")
        return

    # Извлекаем дату начала события из состояния бота
    data = await state.get_data()
    start_date = data.get('start_date')

    # Удаление события из Google Calendar API
    delete_event(start_date, end_date)

    await message.reply("Событие успешно удалено")

    # Завершаем состояние
    await state.clear()


def is_valid_date(date):
    # проверка формата

    return True


def delete_event(start_date, end_date):
    
    # id
    calendar_id = '3849e27ee5d66228f160fe12d6ba15dc5399e96d573787fb5190d45884c57b64@group.calendar.google.com'

    # Загрузка учетных данных
    credentials_path = service_account.Credentials.from_service_account_file('creds1.json',
                                                                       scopes=['https://www.googleapis.com/auth/calendar'])

    # Подключение к гугл апи
    credentials = service_account.Credentials.from_service_account_file('creds1.json')
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    # Поиск событий с указанным интервалом
    events_list = service.events().list(calendarId=calendar_id,
                                        timeMin=start_date,
                                        timeMax=end_date).execute()

    if 'items' in events_list:
        events = events_list['items']

        # Удаление каждого найденного события
        for event in events:
            event_id = event['id']
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    