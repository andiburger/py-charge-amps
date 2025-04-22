import configparser
import getpass
from utils import encrypt, get_or_create_encryption_key
import os

def prompt_cfg_interactive():
    """
    Prompts the user for configuration details interactively and saves them to a cfg.ini file.
    """
    print("📦 Let's create your cfg.ini configuration file!\n")

    config = configparser.ConfigParser()

    # USERDATA section
    print("🔐 USERDATA section:")
    email = input("Enter your email address: ").strip()
    password = getpass.getpass("Enter your password (hidden): ").strip()
    api_key = getpass.getpass("Enter your API key (hidden): ").strip()

    key = get_or_create_encryption_key()

    config["USERDATA"] = {
        "email": encrypt(email, key),
        "password": encrypt(password, key),
        "apiKey": api_key
    }

    # GENERAL section
    print("\n⚙️ GENERAL section:")
    base_url = input("Enter base URL [https://api.chargeamps.com]: ").strip() or "https://api.chargeamps.com"
    price_kwh = input("Enter price per kWh (e.g. 0.30): ").strip()

    config["GENERAL"] = {
        "baseUrl": base_url,
        "pricekWh": price_kwh
    }

    # File path
    default_path = "cfg.ini"
    path = input(f"\n📁 Where to save the config? [default: {default_path}]: ").strip() or default_path

    # Save to file
    with open(path, "w") as configfile:
        config.write(configfile)

    print(f"\n✅ Configuration saved to {path}")

if __name__ == "__main__":
    prompt_cfg_interactive()