from dataclasses import field
from datetime import datetime
from typing import Optional

from ciso8601 import parse_datetime
from dataclasses_json import config
from marshmallow import fields


def datetime_encoder(x: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO 8601 string format."""
    return datetime.isoformat(x) if x is not None else None


def datetime_decoder(x: Optional[str]) -> Optional[datetime]:
    """Convert ISO 8601 string format to datetime."""
    return parse_datetime(x) if x is not None else None


def datetime_field():
    """Field for datetime serialization/deserialization.
    This function provides a field that can be used in dataclasses to handle datetime objects."""
    return field(
        default=None,
        metadata=config(
            encoder=datetime_encoder,
            decoder=datetime_decoder,
            mm_field=fields.DateTime(format="iso"),
        ),
    )