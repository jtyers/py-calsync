import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
CALLBACK_LISTEN_PORT = 56133


__cached_service = None


def __get_underlying_calendar_service():
    global __cached_service
    if __cached_service is None:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=CALLBACK_LISTEN_PORT)
            # Save the credentials for the next run
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        __cached_service = build("calendar", "v3", credentials=creds)

    return __cached_service


def get_calendar_service():
    underlying = __get_underlying_calendar_service()
    return CalendarService(service=underlying)


class CalendarService:
    """Wrapper around the Google Calendar Service API, to make mocking/testing much
    easier."""

    def __init__(self, service):
        self.service = service

    def list_calendars(self, **kwargs):
        result = self.service.calendarList().list(**kwargs).execute()
        return result.get("items", [])

    def list_events(self, **kwargs):
        result = self.service.events().list(**kwargs).execute()
        return result.get("items", [])

    def insert_event(self, **kwargs):
        result = self.service.events().insert(**kwargs).execute()
        return result

    def import_event(self, **kwargs):
        result = self.service.events().import_(**kwargs).execute()
        return result
