from datetime import datetime
from utils import datetime_field
from enum import Enum

from dataclasses import dataclass
from dataclasses_json import LetterCase, dataclass_json

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnector:
    """Class representing a connector of a charge point."""
    charge_point_id: str
    connector_id: int
    type: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePoint:
    """Class representing a charge point."""
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
    """Class representing a charging session."""
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
    """Class representing settings for a charge point."""
    id: str
    dimmer: str
    down_light: bool

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnectorSettings:
    """Class representing settings for a connector of a charge point."""
    charge_point_id: str
    connector_id: int
    mode: str
    rfid_lock: bool
    cable_lock: bool
    max_current: float | None = None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointPartner:
    """Class representing a partner associated with a charge point."""
    id: int
    name: str
    description: str
    email: str
    phone: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointMeasurement:
    """Class representing a measurement of a charge point."""
    phase: str
    current: float
    voltage: float

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointConnectorStatus:
    """Class representing the status of a connector of a charge point."""
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
    """Class representing the status of a charge point."""
    id: str
    status: str
    connector_statuses: list[ChargePointConnectorStatus]

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointScheduleOverrideStatus:
    """Class representing the status of a schedule override for a charge point."""
    connector_id: int
    is_overriden: bool

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointSchedule:
    """Class representing a schedule for a charge point."""
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
    """Enum representing the status of a user."""
    Valid = 1
    Invaild = 2
    Undef = 3

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class RFIDTag:
    """Class representing an RFID tag."""
    active: bool
    rfid: str
    rfidDec: str | None
    rfidDecReverse: str | None

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargeAmpsUser:
    """Class representing a user in the ChargeAmps system."""
    id: str
    firstName: str
    lastName: str
    email: str
    mobile: str
    rfidTags: list[RFIDTag]
    userStatus: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class StartAuth:
    """Class representing the authentication information for starting a session."""
    rfid_length: int
    rfid_format: str
    rfid: str
    external_transaction_id: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointAuth:
    """Class representing the authentication information for a charge point."""
    chargePointId: str
    password: str
    chargePointName: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass(frozen=True)
class ChargePointIds:
    """Class representing a list of charge point IDs."""
    chargePointId: list[str]