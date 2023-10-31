import datetime
import json
from aiogram import F, types, Router
from aiogram.fsm.storage.memory import MemoryStorage
from googleapiclient.discovery import build
from google.oauth2 import service_account


router = Router()

# Инициализация сервисного аккаунта 
credentials = service_account.Credentials.from_service_account_file('creds1.json')


# Функция для получения событий из календаря
def get_events(start_date, end_date):
    # Создание объекта для доступа к API
    service = build('calendar', 'v3', credentials=credentials)

    

    # Выполнение запроса для получения событий за указанный период
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_date.isoformat(),
        timeMax=end_date.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    # Получение списка событий
    events = events_result.get('items', [])

    return events


@router.message(F.text.lower() == "look when we have a free time")
async def get_free_time(message: types.Message):
    # Определение даты проверки периода
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=14)

    # Получение списка событий из календаря за указанный период
    events = get_events(today, end_date)

    # Определение свободных промежутков времени
    free_slots = []
    current_datetime = datetime.datetime.combine(today, datetime.time(0, 0))
    while current_datetime.date() <= end_date:
        # Проверка на свободность времени 
        is_slot_free = True
        for event in events:
            event_start = datetime.datetime.fromisoformat(event['start']['dateTime'])
            event_end = datetime.datetime.fromisoformat(event['end']['dateTime'])
            if event_start <= current_datetime < event_end:
                is_slot_free = False
                break

        # Добавление свободного промежутка времени в список
        if is_slot_free:
            free_slots.append(current_datetime)

        # Переход к следующему промежутку времени
        current_datetime += datetime.timedelta(minutes=30)

    # Отправка сообщения с найденными свободными промежутками времени
    if free_slots:
        response = "Свободные промежутки времени:\n"
        for slot in free_slots:
            response += f"- {slot.time()}\n"
    else:
        response = "Нет свободных промежутков времени."

    await message.answer(response)

