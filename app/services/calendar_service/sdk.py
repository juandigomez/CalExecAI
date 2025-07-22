"""Calendar SDK."""

import os

from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class CalendarSDK():

    def __init__(self, pk_file_path: str, token_file_path: str, scopes: list[str]) -> None:
        self.pk_file_path = pk_file_path
        self.token_file_path = token_file_path
        self.scopes = scopes

    def authenticate(self):
        creds = None
        
        if os.path.exists(self.token_file_path):
            creds = self.get_creds_from_token()

        if not creds:
            creds = self.get_creds_from_pk()
            self.cache_creds_as_token(creds)
        elif creds and creds.expired and creds.refresh_token:
            # Refresh silently
            creds.refresh(Request())
            self.cache_creds_as_token(creds)
        elif not creds.valid:
            # Fallback: must re-authenticate
            creds = self.get_creds_from_pk()
            self.cache_creds_as_token(creds)
            
        return creds
    
    def get_creds_from_token(self):
        return Credentials.from_authorized_user_file(self.token_file_path, self.scopes)

    def get_creds_from_pk(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.pk_file_path, self.scopes)
        creds = flow.run_local_server(port=0)
        return creds

    def cache_creds_as_token(self, creds: Any):
        with open(self.token_file_path, "w") as token:
            token.write(creds.to_json())

    @property
    def credentials(self):
        if not hasattr(self, "_credentials"):
            self._credentials = self.authenticate()
        return self._credentials

    @property
    def resource(self):
        if not hasattr(self, "_resource"):
            self._resource = build("calendar", "v3", credentials=self.credentials)
        return self._resource

    @property
    def user_resource(self):
        if not hasattr(self, "_user_resource"):
            self._user_resource = build("oauth2", "v2", credentials=self.credentials)
        return self._user_resource
