import os
import sys
import time
import traceback

# ANSI Color Fix
os.system('')

from Function_Loader import (
    checking_requirements,
    download_and_run_github_exe,
    download_and_update_main_exe,
    request_admin,
)
from KeyAuth_Loader import keyauth_login_system, keyauthapp
from Security_Loader import run_security_check
from Style_Loader import (
    BOLD,
    CYAN,
    GREEN,
    RED,
    RESET,
    YELLOW,
    draw_animated_header,
    setup_terminal_size,
)


def animate_text(text, delay=0.3):
    """টেক্সটের ডট অ্যানিমেট করার জন্য হেল্পার ফাংশন"""
    for _ in range(2):
        for dots in [".  ", ".. ", "..."]:
            sys.stdout.write(f"\r{text}{dots}")
            sys.stdout.flush()
            time.sleep(delay)
    print(f"\r{text}...   ")
    
    
def main():
    # 🛡️ Step 1: Admin Permission Check
    request_admin()

    # 🔒 Step 2: Anti-Debug / Security Check in Background
    run_security_check()

    try:
        # Step 3: Set Terminal Size
        setup_terminal_size(cols=100, lines=30)

        # 🔑 Step 4: Login System (First UI Screen)
        is_authenticated = keyauth_login_system()

        # লগইন না হলে প্রোগ্রাম সেখানেই ক্লোজ হবে
        if not is_authenticated:
            print(f"\n    {BOLD}{RED}❌ AUTHENTICATION FAILED.PROGRAM CLOSE AFTER 2 SECONDS{RESET}")
            time.sleep(2)
            return

        # 🚀 Step 5: Login Successful -> Show Main Page & Header
        os.system("cls" if os.name == "nt" else "clear")
        draw_animated_header(title="BD HEX CHEAT", width=100)

        print(f"\n    {BOLD}{GREEN}✔ AUTHENTICATION SUCCESSFUL WELCOME {keyauthapp.user_data.username}.{RESET}\n")
        
        animate_text(f"    {BOLD}{CYAN}INITIALIZING SYSTEM", delay=0.2)
        time.sleep(0.5)
        
        # Cheek Main Exe Update
        is_updated_or_running = download_and_update_main_exe()
        
        if is_updated_or_running:
            print(f"\n    {BOLD}{GREEN}✔ New EXE launched. Exiting loader...{RESET}")
            time.sleep(1)
            sys.exit(0)
        
        # ⚙️ Step 6: Execute Main Page Function
        if not checking_requirements():
            print(f"    {BOLD}{YELLOW}REQUIREMENTS CHECK FAILED.{RESET}")
            return

        download_and_run_github_exe()

    except Exception as e:  # noqa: BLE001
        print(f"\n{RED}[CRITICAL ERROR]: {e}{RESET}")
        traceback.print_exc()

    finally:
        print()
        for i in range(3, 0, -1):
            sys.stdout.write(
                f"\r{BOLD}{YELLOW}Closing panel in {i} second(s)...{RESET}"
            )
            sys.stdout.flush()
            time.sleep(1)
        print(f"\r{BOLD}{RED}Panel closed.{RESET}" + " " * 15)
        sys.exit()


if __name__ == "__main__":
    main()