import json
import msvcrt
import os
import sys
import time

from keyauth import api
from Style_Loader import (
    BOLD,
    GREEN,
    RED,
    RESET,
    YELLOW,
    draw_cpp_style_login_box,
    setup_terminal_size,
)

# 📂 LocalAppData ফোল্ডারে ফাইল সেভ করার পাথ
APP_STORAGE_DIR = os.path.join(os.getenv('LOCALAPPDATA'), "NinjaLoader_Data")

if not os.path.exists(APP_STORAGE_DIR):
    os.makedirs(APP_STORAGE_DIR, exist_ok=True)

# Credentials ফাইলের নতুন লোকেশন
CREDENTIALS_FILE = os.path.join(APP_STORAGE_DIR, "auth_credentials.json")


def getchecksum():
    return ""


try:
    keyauthapp = api(
        name="BD HEX",
        ownerid="hoEyJjxAXk",
        version="1.0",
        hash_to_check=getchecksum(),
    )
except Exception as e:  # noqa: BLE001
    print(f"\n    {RED}Security Connection Failed: {e}{RESET}")
    time.sleep(2)
    sys.exit(1)


def save_credentials(username, password):
    try:
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({"username": username, "password": password}, f)
    except Exception:  # noqa: BLE001, S110
        pass


def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                data = json.load(f)
                return data.get("username"), data.get("password")
        except Exception:  # noqa: BLE001
            return None, None
    return None, None


def clear_saved_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        try:
            os.remove(CREDENTIALS_FILE)
        except Exception:  # noqa: BLE001, S110
            pass


def safe_keyauth_login(user, password):
    old_exit = os._exit
    exit_called = False
    captured_msg = ""

    def mock_exit(code=0):
        nonlocal exit_called
        exit_called = True

    os._exit = mock_exit

    try:
        keyauthapp.login(user, password)
    except SystemExit:
        exit_called = True
    except Exception as e:  # noqa: BLE001
        captured_msg = str(e)
    finally:
        os._exit = old_exit

    if exit_called:
        return False, "INVALID USERNAME OR PASSWORD. PLEASE TRY AGAIN."
    if captured_msg:
        return False, captured_msg
    if keyauthapp.user_data.username:
        return True, "SUCCESSFUL LOGIN"

    return False, "Login failed. Please check credentials."


def get_masked_input(
    width=100, username="", current_field="password", error_msg=""
):
    pw = ""
    while True:
        draw_cpp_style_login_box(width, username, "*" * len(pw), current_field)
        if error_msg:
            print(f"       {RED}{BOLD}❌ {error_msg}{RESET}\n")

        ch = msvcrt.getch()
        if ch in {b"\r", b"\n"}: 
            break
        elif ch == b"\x08":  # Backspace
            if len(pw) > 0:
                pw = pw[:-1]
        elif ch == b"\x03":  # Ctrl+C
            raise KeyboardInterrupt
        elif ch == b" ": 
            pw += " "
        else:
            try:
                char = ch.decode("utf-8")
                pw += char
            except Exception:  # noqa: BLE001, S110
                pass
    return pw


def keyauth_login_system():
    setup_terminal_size(cols=100, lines=32)
    error_msg = ""

    while True:
        saved_user, saved_pass = load_credentials()

        if saved_user and saved_pass and not error_msg:
            user = saved_user
            password = saved_pass

            draw_cpp_style_login_box(
                width=100,
                username=user,
                masked_password="*" * len(password),
                current_field="login",
            )
            print(
                f"       {YELLOW}USERNAME AND PASSWORD ALREADY SAVED || CLICK ENTER TO LOGIN OR SPACE TO CLEAR{RESET}"
            )

            while True:
                key = msvcrt.getch()
                if key in {b"\r", b"\n"}: 
                    break
                elif key == b" ": 
                    clear_saved_credentials()
                    error_msg = "YOUR USER AND PASSWORD HAS BEEN CLEARED || PLEASE RE-ENTER"
                    break

            if error_msg:
                continue

        else:
            draw_cpp_style_login_box(
                width=100,
                username="",
                masked_password="",
                current_field="USERNAME",
            )
            if error_msg:
                print(f"       {RED}{BOLD}❌ {error_msg}{RESET}\n")

            user = input("       ➔ USERNAME: ").strip()

            if not user:
                error_msg = "USERNAME EMPTY || PLEASE RE-ENTER"
                continue

            if os.name == "nt":
                password = get_masked_input(
                    width=100,
                    username=user,
                    current_field="PASSWORD",
                    error_msg="",
                ).strip()
            else:
                import getpass

                password = getpass.getpass("       ➔ PASSWORD: ").strip()

            if not password:
                error_msg = "PASSWORD EMPTY || PLEASE RE-ENTER"
                continue

        draw_cpp_style_login_box(
            width=100,
            username=user,
            masked_password="*" * len(password),
            current_field="login",
        )
        print(f"       {YELLOW}PLEASE WAIT FOR CONNECTION...{RESET}")

        success, message = safe_keyauth_login(user, password)

        if success:
            save_credentials(user, password)
            print(
                f"\n       {GREEN}{BOLD}ACCESS SUCCESSFUL, {keyauthapp.user_data.username}.{RESET}\n"
            )
            time.sleep(1.5)
            return True
        else:
            clear_saved_credentials()
            error_msg = message
            time.sleep(0.5)


if __name__ == "__main__":
    keyauth_login_system()