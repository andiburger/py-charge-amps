from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

from dataclasses import field
from datetime import datetime

from ciso8601 import parse_datetime
from dataclasses_json import config
from marshmallow import fields


def datetime_encoder(x: datetime | None) -> str | None:
    return datetime.isoformat(x) if x is not None else None


def datetime_decoder(x: str | None) -> datetime | None:
    return parse_datetime(x) if x is not None else None


def datetime_field():
    return field(
        default=None,
        metadata=config(
            encoder=datetime_encoder,
            decoder=datetime_decoder,
            mm_field=fields.DateTime(format="iso"),
        ),
    )


# Key generieren
def generate_key():
    """Generates a Fernet key for encryption/decryption."""
    return Fernet.generate_key()


# encrypt E-Mail


def encrypt(email: str, key: bytes) -> str:
    """Encrypts an email address using the provided key.
    Args:
        email (str): The email address to encrypt.
        key (bytes): The key used for encryption.
    Returns:
        str: The encrypted email address.
    """
    fernet = Fernet(key)
    return fernet.encrypt(email.encode()).decode()


# decrypt E-Mail
def decrypt(token: str, key: bytes) -> str:
    """Decrypts an encrypted email address using the provided key.
    Args:
        token (str): The encrypted email address to decrypt.
        key (bytes): The key used for decryption.
    Returns:
        str: The decrypted email address.
    """
    fernet = Fernet(key)
    return fernet.decrypt(token.encode()).decode()


def get_or_create_encryption_key():
    """
    Get or create an encryption key for email encryption.
    If the key already exists in the .env file, it will be returned.
    If not, a new key will be generated and saved to the .env file.
    """
    env_path = os.getenv("ENV_PATH",
                         os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv(dotenv_path=env_path)
    key = os.getenv("EMAIL_ENCRYPTION_KEY")

    if key:
        return key.encode() if isinstance(key, str) else key

    # Generate new key
    key = Fernet.generate_key().decode()

    # Read existing .env content
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Replace or append the key in the lines
    key_written = False
    for i, line in enumerate(lines):
        if line.startswith("EMAIL_ENCRYPTION_KEY="):
            lines[i] = f"EMAIL_ENCRYPTION_KEY={key}\n"
            key_written = True
            break
    if not key_written:
        lines.append(f"EMAIL_ENCRYPTION_KEY={key}\n")

    # Write updated lines to .env
    with open(env_path, "w") as f:
        f.writelines(lines)

    print("🔐 New EMAIL_ENCRYPTION_KEY generated and saved to .env")
    return key.encode() if isinstance(key, str) else key
