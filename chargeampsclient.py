"""
Python client class for charge amps.
This module holds the connection to the cloud backend and refreshes the connection when needed.
"""
from aiohttp import ClientResponse, ClientSession
from aiohttp.web import HTTPException

import logging
import time
import jwt

from datetime import datetime
from urllib.parse import urljoin

from utils import datetime_field

from chargeampsdata import (UserStatus,ChargePointConnector, 
                            ChargePoint, ChargingSession, ChargePointSettings, 
                            ChargePointConnectorSettings, ChargePointPartner, 
                            ChargePointStatus, ChargePointMeasurement, 
                            ChargePointConnectorStatus, ChargePointScheduleOverrideStatus, 
                            ChargePointSchedule, ChargeAmpsUser, StartAuth,
                            ChargePointAuth, ChargePointIds)

API_BASE_URL = "https://eapi.charge.space"
API_VERSION = "v5"
UNUSED_RFID_SLOT = "00000000000000"


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
        return None
    
    def print_user_info(self)->None:
        print("username: "+self._email + "\nfirstname: "+self._firstName + "\nlastname: "+self._lastName + "\nuserstatus: "+self._userStatus.name)
    
    def update_user_info(self, user_info:dict)->bool:
        self._userid = user_info["id"]
        self._firstName = user_info["firstName"]
        self._lastName = user_info["lastName"]
        self._mobile = user_info["mobile"]
        self._rfidTags = user_info["rfidTags"]
        self._userStatus = UserStatus[user_info["userStatus"]]
        return True

class Client:
    def __init__(self,
            email: str,
            password: str,
            apiKey: str,
            api_url: str
    ):
        self._logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self._user = User(username=email,password=password,apiKey=apiKey)
        self._session = Session(api_url, self._user)
        return None
    
    async def init_session(self)->None:
        await self._session.init_session()
        self._user.update_user_info(self._session.get_user_info())

    async def close_session(self)->None:
        await self._session.shutdown()
    
    async def get_chargepoints(self) -> list[ChargePoint]:
       return await self._session.get_chargepoints()
    
    async def get_chargepoint_status(self, charge_point_id: str) -> ChargePointStatus:
        return await self._session.get_chargepoint_status(charge_point_id)
    
    async def get_connector_chargingsessions(
        self,
        charge_point_id: str,
        connector_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        return await self._session.get_connector_chargingsessions(charge_point_id=charge_point_id,connector_id=connector_id,start_time=start_time,end_time=end_time)

    async def get_chargingsessions(
        self,
        charge_point_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        return await self._session.get_chargingsessions(charge_point_id=charge_point_id,start_time=start_time,end_time=end_time)
    
    async def get_specific_chargingsession(
        self,
        charge_point_id: str,
        session_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        return await self._session.get_specific_chargingsession(charge_point_id=charge_point_id,session_id=session_id,start_time=start_time,end_time=end_time)

    async def get_rfid_chargingsessions(
        self,
        charge_point_id: str,
        connector_id: int,
        rfid: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        return await self._session.get_rfid_chargingsessions(charge_point_id=charge_point_id,connector_id=connector_id,rfid=rfid,start_time=start_time,end_time=end_time)

    async def get_chargepoint_connector_settings(self, charge_point_id: str, connector_id: int) -> ChargePointConnectorSettings:
        return await self._session.get_chargepoint_connector_settings(charge_point_id=charge_point_id, connector_id=connector_id)
    
    async def get_chargepoint_settings(self, charge_point_id: str) -> ChargePointSettings:
        return await self._session.get_chargepoint_settings(charge_point_id=charge_point_id)
    
    async def get_chargepoint_partner(self, charge_point_id: str) -> ChargePointPartner:
        return await self._session.get_chargepoint_partner(charge_point_id=charge_point_id)
    
    async def get_chargepoint_override_status(self, charge_point_id: str) -> ChargePointScheduleOverrideStatus:
        return await self._session.get_chargepoint_override_status(charge_point_id=charge_point_id)
    
    async def get_chargepoint_schedules(self, charge_point_id: str) -> list[ChargePointSchedule]:
        return await self._session.get_chargepoint_schedules(charge_point_id=charge_point_id)
    
    async def get_chargepoint_schedule(self, charge_point_id: str, schedule_id:int) -> ChargePointSchedule:
        return await self._session.get_chargepoint_schedule(charge_point_id=charge_point_id,schedule_id=schedule_id)
    
    async def get_user(self, user_id:str) -> ChargeAmpsUser:
        return await self._session.get_user(user_id=user_id)
    
    async def get_registered_rfid_tags(self, charge_point_id: str) -> list:
        return await self._session.get_registered_rfid_tags(charge_point_id=charge_point_id)

class Session:
    def __init__(self, 
                api_url : str,
                user : User
                ):
        self._logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self._token = None
        self._refreshToken = None
        self._headers = {}
        self.__lastresponse = {}
        self._base_url = api_url or API_BASE_URL
        self._ssl = False
        self._token_expire = 0
        self._user = user
        self._csession = None
    
    async def shutdown(self) -> None:
        await self._csession.close()

    async def init_session(self)->None:
        self._csession = ClientSession(raise_for_status=True)
        await self._get_token()
        return None

    def get_user_info(self)->dict:
        if self.__lastresponse["user"]:
            return self.__lastresponse["user"]
        return None

    async def _get_token(self)->None:
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
                response = await self._csession.post(
                    urljoin(self._base_url, f"/api/{API_VERSION}/auth/refreshToken"),
                    ssl=self._ssl,
                    headers={"apiKey": self._user._apiKey},
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
                response = await self._csession.post(
                    urljoin(self._base_url, f"/api/{API_VERSION}/auth/login"),
                    ssl=self._ssl,
                    headers={"apiKey": self._user._apiKey},
                    json={"email": self._user._email, "password": self._user._password},
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
        
    async def _post(self, path, **kwargs) -> ClientResponse:
        await self._get_token()
        headers = kwargs.pop("headers", self._headers)
        return await self._csession.post(urljoin(self._base_url, path), ssl=self._ssl, headers=headers, **kwargs)

    async def _get(self, path, **kwargs) -> ClientResponse:
        await self._get_token()
        headers = kwargs.pop("headers", self._headers)
        return await self._csession.get(urljoin(self._base_url, path), ssl=self._ssl, headers=headers, **kwargs)

    async def _put(self, path, **kwargs) -> ClientResponse:
        await self._get_token()
        headers = kwargs.pop("headers", self._headers)
        return await self._csession.put(urljoin(self._base_url, path), ssl=self._ssl, headers=headers, **kwargs)

    async def _delete(self, path, **kwargs) -> ClientResponse:
        await self._get_token()
        headers = kwargs.pop("headers", self._headers)
        return await self._csession.delete(urljoin(self._base_url, path), ssl=self._ssl, headers=headers, **kwargs)
    
    async def get_chargepoints(self) -> list[ChargePoint]:
        """Get all owned chargepoints"""
        request_uri = f"/api/{API_VERSION}/chargepoints/owned"
        response = await self._get(request_uri)
        res = []
        for chargepoint in await response.json():
            res.append(ChargePoint.from_dict(chargepoint))
        return res
    
    async def get_registered_rfid_tags(self, charge_point_id: str) -> list:
        """Get all registered RFID tags for a specific charge point."""
        charging_sessions = await self.get_chargingsessions(charge_point_id)
        rfid_tags = []
        for c_session in charging_sessions:
            if c_session.rfid not in rfid_tags and c_session.rfid != UNUSED_RFID_SLOT:
                rfid_tags.append(c_session.rfid)
        return rfid_tags

    async def get_chargepoint_status(self, charge_point_id: str) -> ChargePointStatus:
        """Get charge point status"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/status"
        response = await self._get(request_uri)
        payload = await response.json()
        return ChargePointStatus.from_dict(payload)

    async def get_connector_chargingsessions(
        self,
        charge_point_id: str,
        connector_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        """Get all charging sessions of a specific connector"""
        query_params = {}
        if start_time:
            query_params["startTime"] = start_time.isoformat()
        if end_time:
            query_params["endTime"] = end_time.isoformat()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/connectors/{connector_id}/chargingsessions"
        response = await self._get(request_uri, params=query_params)
        res = []
        for session in await response.json():
            res.append(ChargingSession.from_dict(session))
        return res
    
    async def get_rfid_chargingsessions(
        self,
        charge_point_id: str,
        connector_id: int,
        rfid: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        """Get all charging sessions of a specific connector"""
        query_params = {}
        if start_time:
            query_params["startTime"] = start_time.isoformat()
        if end_time:
            query_params["endTime"] = end_time.isoformat()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/connectors/{connector_id}/chargingsessions"
        response = await self._get(request_uri, params=query_params)
        res = []
        for session in await response.json():
            chrgSession = ChargingSession.from_dict(session)
            if chrgSession.rfid == rfid:
                res.append(chrgSession)
        return res
    
    async def get_chargingsessions(
        self,
        charge_point_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        """Get all charging sessions"""
        query_params = {}
        if start_time:
            query_params["startTime"] = start_time.isoformat()
        if end_time:
            query_params["endTime"] = end_time.isoformat()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/chargingsessions"
        response = await self._get(request_uri, params=query_params)
        res = []
        for session in await response.json():
            res.append(ChargingSession.from_dict(session))
        return res
    
    async def get_specific_chargingsession(
        self,
        charge_point_id: str,
        session_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None) -> list[ChargingSession]:
        """Get all charging sessions of a specific connector"""
        query_params = {}
        if start_time:
            query_params["startTime"] = start_time.isoformat()
        if end_time:
            query_params["endTime"] = end_time.isoformat()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/chargingsessions/{session_id}"
        response = await self._get(request_uri, params=query_params)
        res = []
        for session in await response.json():
            res.append(ChargingSession.from_dict(session))
        return res
    
    async def get_chargepoint_connector_settings(self, charge_point_id: str, connector_id: int) -> ChargePointConnectorSettings:
        """Get all owned chargepoints"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/connectors/{connector_id}/settings"
        response = await self._get(request_uri)
        payload = await response.json()
        return ChargePointConnectorSettings.from_dict(payload)
    
    async def get_chargepoint_settings(self, charge_point_id: str) -> ChargePointSettings:
        """Get chargepoint settings"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/settings"
        response = await self._get(request_uri)
        payload = await response.json()
        return ChargePointSettings.from_dict(payload)
    
    async def get_chargepoint_partner(self, charge_point_id: str) -> ChargePointPartner:
        """Get chargepoint settings"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/partner"
        response = await self._get(request_uri)
        payload = await response.json()
        return ChargePointPartner.from_dict(payload)
    
    async def get_chargepoint_override_status(self, charge_point_id: str) -> ChargePointScheduleOverrideStatus:
        """Get chargepoint settings"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/schedule/override/status"
        response = await self._get(request_uri)
        payload = await response.json()
        return ChargePointScheduleOverrideStatus.from_dict(payload)
    
    async def get_chargepoint_schedules(self, charge_point_id: str) -> list[ChargePointSchedule]:
        """Get chargepoint settings"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/schedules"
        response = await self._get(request_uri)
        payload = await response.json()
        res = []
        for session in await response.json():
            res.append(ChargePointSchedule.from_dict(session))
        return res
    
    async def get_chargepoint_schedule(self, charge_point_id: str, schedule_id:int) -> ChargePointSchedule:
        """Get chargepoint settings"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/schedules/{schedule_id}"
        response = await self._get(request_uri)
        payload = await response.json()
        return ChargePointSchedule.from_dict(payload)
    
    async def get_user(self, user_id:str) -> ChargeAmpsUser:
        """Get chargepoint settings"""
        request_uri = f"/api/{API_VERSION}/users/{user_id}"
        response = await self._get(request_uri)
        payload = await response.json()
        return ChargeAmpsUser.from_dict(payload)
    
    async def set_chargepoint_settings(self, settings: ChargePointSettings) -> None:
        """Set chargepoint settings"""
        payload = settings.to_dict()
        charge_point_id = settings.id
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/settings"
        await self._put(request_uri, json=payload)
    
    async def set_chargepoint_connector_settings(self, settings: ChargePointConnectorSettings) -> None:
        """Get all owned chargepoints"""
        payload = settings.to_dict()
        charge_point_id = settings.charge_point_id
        connector_id = settings.connector_id
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/connectors/{connector_id}/settings"
        await self._put(request_uri, json=payload)

    async def set_chargepoint_schedule_override(self, charge_point_id: str, connector_id: int) -> None:
        """override chargepoint schedule"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/connectors/{connector_id}/schedule/override"
        await self._put(request_uri, json="{}")

    async def remote_start(self, charge_point_id: str, connector_id: int, start_auth: StartAuth) -> None:
        """Remote start chargepoint"""
        payload = start_auth.to_dict()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/connectors/{connector_id}/remotestart"
        await self._put(request_uri, json=payload)

    async def remote_stop(self, charge_point_id: str, connector_id: int) -> None:
        """Remote stop chargepoint"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/connectors/{connector_id}/remotestop"
        await self._put(request_uri, json="{}")

    async def reboot(self, charge_point_id: str) -> None:
        """Reboot chargepoint"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/reboot"
        await self._put(request_uri, json="{}")

    async def register(self, charge_point_id: str, chrg_point_auth: ChargePointAuth) -> None:
        """Register chargepoint to auth user"""
        payload = chrg_point_auth.to_dict()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/register"
        await self._put(request_uri, json=payload)

    async def update_schedule(self, charge_point_id: str, chrg_schedule: ChargePointSchedule) -> None:
        """Update charge schedules. For CAPI charger only"""
        payload = chrg_schedule.to_dict()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/schedules"
        await self._put(request_uri, json=payload)

    async def register(self, charge_point_id: str, chrg_point_auth: ChargePointAuth) -> None:
        """Unregister chargepoint from user"""
        payload = chrg_point_auth.to_dict()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/unregister"
        await self._put(request_uri, json=payload)

    async def disable(self, chrg_point_ids: ChargePointIds) -> None:
        """Disable callback on chargepoints"""
        payload = chrg_point_ids.to_dict()
        request_uri = f"/api/{API_VERSION}/chargepoints/callbacks/disable"
        await self._put(request_uri, json=payload)
    
    async def enable(self, chrg_point_ids: ChargePointIds) -> None:
        """Enable callback on chargepoints"""
        payload = chrg_point_ids.to_dict()
        request_uri = f"/api/{API_VERSION}/chargepoints/callbacks/enable"
        await self._put(request_uri, json=payload)

    async def create_schedule(self, charge_point_id: str, chrg_schedule: ChargePointSchedule) -> None:
        """create charge schedules. For CAPI charger only"""
        payload = chrg_schedule.to_dict()
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/schedules"
        await self._post(request_uri, json=payload)

    async def delete_schedule(self, charge_point_id: str, schedule_id:int) -> None:
        """Delete charge schedules. For CAPI charger only"""
        request_uri = f"/api/{API_VERSION}/chargepoints/{charge_point_id}/schedules/{schedule_id}"
        await self._delete(request_uri, json="{}")
    