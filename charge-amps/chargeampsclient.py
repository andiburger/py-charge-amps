"""
Python client class for charge amps.
This module holds the connection to the cloud backend and refreshes the connection when needed.
"""
from enum import Enum
from aiohttp import ClientResponse, ClientSession
from aiohttp.web import HTTPException

import logging
import time
import jwt

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

API_BASE_URL = "https://eapi.charge.space"
API_VERSION = "v5"

class UserStatus(Enum):
    Valid = 1
    Invaild = 2
    Undef = 3

class User:
    def __init__(self,
                 username: str,
                 password: str,
                 apiKey: str):
        self._userid = None
        self._firstName = None
        self._lastName = None
        self._email = username
        self._password = password
        self._apiKey = apiKey
        self._mobile = None
        self._rfidTags = None
        self._userStatus = None
        return self
    
    def update_user_info(self, user_info:dict)->bool:
        self._userid = user_info["id"]
        self._firstName = user_info["firstName"]
        self._lastName = user_info["lastName"]
        self._mobile = user_info["mobile"]
        self._rfidTags = user_info["rfidTags"]
        self._userStatus = self.__get_user_status(user_info["userStatus"])
        return True

    def __get_user_status(self, status)->UserStatus:
        if status is "Valid":
            return UserStatus.Valid
        elif status is "Invalid":
            return UserStatus.Invaild
        else:
            return UserStatus.Undef

class Client:
    def __init__(self,
            email: str,
            password: str,
            apiKey: str,
            api_url: str
    ):
        self._logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self._user = User(username=email,password=password,apiKey=apiKey)
        self._session = Session(api_url)
        self._session._init_token()
        self._user.update_user_info(self._session.get_user_info())
        return self

class Session:
    def __init__(self, 
                api_url : str
                ):
        self._logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self._token = None
        self._refreshToken = None
        self.__csession = ClientSession(raise_for_status=True)
        self._headers = {}
        self.__lastresponse = {}
        self._base_url = api_url or API_BASE_URL
        self._ssl = False
        self._token_expire = 0


    def get_user_info(self)->dict:
        if self.__lastresponse["user"]:
            return self.__lastresponse["user"]
        return None

    async def _init_token(self)->None:
        if self._token_expire > time.time():
            return

        if self._token is None:
            self._logger.info("Token not found")
        elif self._token_expire > 0:
            self._logger.info("Token expired")

        response = None

        if self._refreshToken:
            try:
                self._logger.info("Found refresh token, try refresh")
                response = await self._session.post(
                    urljoin(self._base_url, f"/api/{API_VERSION}/auth/refreshToken"),
                    ssl=self._ssl,
                    headers={"apiKey": self._api_key},
                    json={"token": self._token, "refreshToken": self._refreshToken},
                )
                self._logger.debug("Refresh successful")
            except HTTPException:
                self._logger.warning("Token refresh failed")
                self._token = None
                self._refreshToken = None
        else:
            self._token = None

        if self._token is None:
            try:
                self._logger.debug("Try login")
                response = await self._session.post(
                    urljoin(self._base_url, f"/api/{API_VERSION}/auth/login"),
                    ssl=self._ssl,
                    headers={"apiKey": self._api_key},
                    json={"email": self._email, "password": self._password},
                )
                self._logger.debug("Login successful")
            except HTTPException as exc:
                self._logger.error("Login failed")
                self._token = None
                self._refreshToken = None
                self._token_expire = 0
                raise exc

        if response is None:
            self._logger.error("No response")
            return

        response_payload = await response.json()
        self.__lastresponse = response_payload

        self._token = response_payload["token"]
        self._refreshToken = response_payload["refreshToken"]

        token_payload = jwt.decode(self._token, options={"verify_signature": False})
        self._token_expire = token_payload.get("exp", 0)

        self._headers["Authorization"] = f"Bearer {self._token}"
        



