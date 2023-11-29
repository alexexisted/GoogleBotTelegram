import os

from aiogram.types import message
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from aiogram import Router, types, F, Bot
from aiogram.fsm.storage.memory import MemoryStorage, State
from aiogram.filters.state import StatesGroup
from aiogram.fsm.context import FSMContext
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import secure


storage = MemoryStorage()
router = Router()
bot = Bot(secure.BOT_TOKEN)
day_start = ''


# Создание класса состояний
class DeleteEventStates(StatesGroup):
    beginning_st = State()
    ending_st = State()


# файл с учетными данными гугл
SERVICE_ACCOUNT_FILE = 'creds3.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']


@router.message(F.text.lower() == 'delete an event')
async def delete_event_handler(message: types.Message, state: FSMContext):
    await message.reply("Введите дату, где находится событие в формате ДД.ММ.ГГГГ")
    await state.set_state(DeleteEventStates.beginning_st)  # Установка состояния на ввод даты


@router.message(DeleteEventStates.beginning_st)
async def get_the_date(message: types.Message, state: FSMContext):
    try:
        start_date = datetime.datetime.strptime(message.text, '%d.%m.%Y').date()

        await delete_event(start_date)

    except ValueError as e:
        await message.reply("Incorrect input. Please try again. DD.MM.YYYY")

    await state.clear()


async def delete_event(start_date):
    ans_str = 'events: \n'

    creds = None

    if os.path.exists('token.json'):  # catch
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds3.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        end_date = start_date + datetime.timedelta(days=1)

        start_date2 = str(start_date) + 'T00:00:00Z'
        end_date2 = str(end_date) + 'T00:00:00Z'

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date2,
            timeMax=end_date2,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print('No events')
            return
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            output1 = start, event['summary']
            done_output = f"'You have', {event['summary']}, 'at', {start[:10]}, 'at', {start[11:16]}"
            sec_output = done_output.replace(',', '')
            ready_out = sec_output.replace("'", '')
            ans_str = ans_str + '\n' + ready_out + '\n'

        await message.reply(ans_str)

    except HttpError as err:
        print("You got an error", err)


    