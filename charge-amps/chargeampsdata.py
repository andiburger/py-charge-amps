from datetime import datetime
from utils import datetime_field
from enum import Enum

from dataclasses import dataclass
from dataclasses_json import LetterCase, dataclass_json

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnector:
    charge_point_id: str
    connector_id: int
    type: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePoint:
    id: str
    name: str
    password: str
    type: str
    is_loadbalanced: bool
    firmware_version: str
    hardware_version: str
    connectors: list[ChargePointConnector]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargingSession:
    id: int
    charge_point_id: str
    connector_id: int
    user_id: str
    rfid: str
    rfidDec: str
    rfidDecReverse: str 
    organisationId: str | None
    session_type: str
    total_consumption_kwh: float
    externalTransactionId: str | None
    externalId: str | None
    start_time: datetime | None = datetime_field()
    end_time: datetime | None = datetime_field()
    
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointSettings:
    id: str
    dimmer: str
    down_light: bool

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnectorSettings:
    charge_point_id: str
    connector_id: int
    mode: str
    rfid_lock: bool
    cable_lock: bool
    max_current: float | None = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointPartner:
    id: int
    name: str
    description: str
    email: str
    phone: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointMeasurement:
    phase: str
    current: float
    voltage: float

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnectorStatus:
    charge_point_id: str
    connector_id: int
    total_consumption_kwh: float
    status: str
    measurements: list[ChargePointMeasurement] | None
    start_time: datetime | None = datetime_field()
    end_time: datetime | None = datetime_field()
    session_id: str | None = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointStatus:
    id: str
    status: str
    connector_statuses: list[ChargePointConnectorStatus]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointScheduleOverrideStatus:
    connector_id: int
    is_overriden: bool

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointSchedule:
    id:  int
    chargePointId: str
    name: str
    active: bool
    startHours: int
    startMinutes: int
    endHours: int
    endMinutes: int
    timeZone: str
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool
    connectorIdList: str

class UserStatus(Enum):
    Valid = 1
    Invaild = 2
    Undef = 3

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class RFIDTag:
    active: bool
    rfid: str
    rfidDec: str | None
    rfidDecReverse: str | None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargeAmpsUser:
    id: str
    firstName: str
    lastName: str
    email: str
    mobile: str
    rfidTags: list[RFIDTag]
    userStatus: str