import datetime
import requests
import os
import platform

# Constants
WEBHOOK_URL = ""  # Replace with your actual webhook URL

class Logger:
    @staticmethod
    def log_to_discord(log_type, username, hardware_id, discord_id="", license_type=""):
        """Sends logs to Discord webhook."""
        now = datetime.datetime.now()
        log_details = (
            "> **User**\n> " + username
            + "\n\n> **Discord ID**\n> " + discord_id
            + "\n\n> **License Type**\n> " + license_type
            + "\n\n> **Hardware ID**\n> " + hardware_id
            + "\n\n> **Time**\n> " + now.strftime("%H:%M:%S")
            + "\n\n> **Date**\n> " + now.strftime("%Y-%m-%d")
        )

        embed = {
            "title": "Authentication Log",
            "description": "Login Successful" if log_type == "login" else "Login Attempt Failed",
            "color": 0x00FF00 if log_type == "login" else 0xFF0000,  # Bright green for success, bright red for failure
            "timestamp": now.isoformat(),
            "fields": [
                {"name": "Log Details", "value": log_details},
            ],
        }

        payload = {"embeds": [embed]}
        try:
            requests.post(WEBHOOK_URL, json=payload)
        except requests.exceptions.RequestException as e:
            print("Failed to log to Discord webhook:", e)

class Authenticator:
    @staticmethod
    def get_user_data():
        """Fetches user data from a remote source securely."""
        try:
            response = requests.get("DATABASE / PASTE URL HERE")
            response.raise_for_status()
            return response.text.strip().split("\n")
        except requests.exceptions.RequestException as e:
            print("Failed to fetch user data:", e)
            return []

    @staticmethod
    def validate_user(username, user_data):
        for data in user_data:
            parts = data.split("//")
            if len(parts) == 2:
                stored_username, details = parts
                if stored_username == username:
                    discord_id, license_type = details.split("--")
                    return username, discord_id, license_type
        return None

    @staticmethod
    def login():
        """Performs user login and logs relevant information."""
        clear_console()
        welcome_message = (
            "\033[36m"
            + "-" * 40
            + "\n    Welcome to ExiAuth\n"
            + "-" * 40
            + "\033[0m"
        )

        while True:
            print(welcome_message)
            username = input("\033[1mEnter your username:\033[0m ").strip()

            if not username:
                print("\033[91mPlease provide a valid username.\033[0m")
                continue

            user_data = Authenticator.get_user_data()
            found_user = Authenticator.validate_user(username, user_data)

            if found_user:
                clear_console()
                print("\033[92m" + "-" * 30)
                print("  User Successfully Logged In!")
                print("-" * 30 + "\033[0m")
                print(f"\033[1mUsername:\033[0m {found_user[0]}")
                print(f"\033[1mLicense Type:\033[0m {found_user[2]}")
                print(f"\033[1mDiscord ID:\033[0m {found_user[1]}")
                
                # Log the successful login
                Logger.log_to_discord("login", found_user[0], platform.node(), found_user[1], found_user[2])
                
                break
            else:
                clear_console()
                print("\033[91m" + "-" * 30)
                print("      Invalid username")
                print("-" * 30 + "\033[0m")
                Logger.log_to_discord("login_attempt", username, platform.node(), "", "")
                input("Press Enter to continue to the login form...")
                clear_console()

def clear_console():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    Authenticator.login()