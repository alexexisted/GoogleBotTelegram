import datetime
import os

from aiogram import F, types, Router
from googleapiclient.discovery import build
from aiogram.types import Message, message
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

router = Router()


# файл с учетными данными гугл
SERVICE_ACCOUNT_FILE = 'creds3.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Функция для получения событий из календаря


@router.message(F.text.lower() == "20 upcoming events")
async def get_events(message: types.Message):
    ans_str = "Your upcoming events: \n"
    # Создание объекта для доступа к API
    creds = None

    if os.path.exists('token.json'):  # catch
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)  # catch
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

        now = datetime.datetime.now().isoformat() + "Z"

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=20,
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