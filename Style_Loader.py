import os
import sys
import time

import pyfiglet

# Ensure UTF-8 encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ANSI Colors
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
MAGENTA = '\033[95m'
BOLD = '\033[1m'
RESET = '\033[0m'

def setup_terminal_size(cols=100, lines=30):
    """Sets static terminal dimensions."""
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.stdout.write(f"\033[8;{lines};{cols}t")
    sys.stdout.flush()

def draw_animated_header(title="PANEL UPDATER", width=100):
    """Draws big ASCII banner header dynamically."""
    top_border = "╔" + "═" * (width - 2) + "╗"
    bottom_border = "╚" + "═" * (width - 2) + "╝"
    
    fig = pyfiglet.Figlet(font='standard')
    ascii_art = fig.renderText(title)
    banner_lines = ascii_art.splitlines()

    for i in range(1, width + 1):
        sys.stdout.write(f"\r{CYAN}{'═' * i}{RESET}")
        sys.stdout.flush()
        time.sleep(0.002)
        
    print(f"\r{CYAN}{top_border}{RESET}")
    print(f"{CYAN}║{' ' * (width - 2)}║{RESET}")

    for line in banner_lines:
        if line.strip():
            padding = (width - 2 - len(line)) // 2
            formatted_line = " " * padding + line + " " * (width - 2 - padding - len(line))
            
            sys.stdout.write(f"{CYAN}║{RESET}{BOLD}{GREEN}")
            for char in formatted_line:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.0005)
            sys.stdout.write(f"{RESET}{CYAN}║{RESET}\n")

    print(f"{CYAN}║{' ' * (width - 2)}║{RESET}")
    print(f"{CYAN}{bottom_border}{RESET}\n")


def draw_cpp_style_login_box(width=100, username="", masked_password="", current_field="username"):
    """C++ স্টাইলের ফিক্সড বক্স ইউজারনেম, পাসওয়ার্ড এবং লগইন বাটন UI"""
    top_border = "╔" + "═" * (width - 2) + "╗"
    bottom_border = "╚" + "═" * (width - 2) + "╝"
    divider = "╠" + "═" * (width - 2) + "╣"

    os.system('cls' if os.name == 'nt' else 'clear')

    # Header Box
    print(f"{CYAN}{top_border}{RESET}")
    print(f"{CYAN}║{' ' * (width - 2)}║{RESET}")
    
    try:
        fig = pyfiglet.Figlet(font='standard')
        ascii_art = fig.renderText("BD HEX CHEAT LOGIN")
        for line in ascii_art.splitlines():
            if line.strip():
                pad = (width - 2 - len(line)) // 2
                fmt_line = " " * pad + line + " " * (width - 2 - pad - len(line))
                print(f"{CYAN}║{RESET}{BOLD}{GREEN}{fmt_line}{RESET}{CYAN}║{RESET}")
    except Exception:  # noqa: BLE001
        title = "=== BD HEX CHEAT LOGIN ==="
        pad = (width - 2 - len(title)) // 2
        print(f"{CYAN}║{RESET}{' ' * pad}{BOLD}{GREEN}{title}{RESET}{' ' * (width - 2 - pad - len(title))}{CYAN}║{RESET}")

    print(f"{CYAN}║{' ' * (width - 2)}║{RESET}")
    print(f"{CYAN}{divider}{RESET}")

    # Info Lines
    info1 = f"Developer: {YELLOW}Akash Mia{RESET}  |  Status: {GREEN}Online{RESET}  |  Version: {CYAN}1.0{RESET}"
    plain_info1 = "Developer: Akash Mia  |  Status: Online  |  Version: 1.0"
    pad1 = (width - 2 - len(plain_info1)) // 2
    print(f"{CYAN}║{RESET}{' ' * pad1}{info1}{' ' * (width - 2 - pad1 - len(plain_info1))}{CYAN}║{RESET}")

    info2 = f"Security: {GREEN}KeyAuth Protected{RESET}  |  System: {MAGENTA}Active{RESET}"
    plain_info2 = "Security: KeyAuth Protected  |  System: Active"
    pad2 = (width - 2 - len(plain_info2)) // 2
    print(f"{CYAN}║{RESET}{' ' * pad2}{info2}{' ' * (width - 2 - pad2 - len(plain_info2))}{CYAN}║{RESET}")

    print(f"{CYAN}{bottom_border}{RESET}\n")

    # ┌────────────────────── C++ Style Input Boxes ──────────────────────┐
    inner_width = 60
    left_pad = (width - inner_width) // 2
    indent = " " * left_pad

    # Username Box
    u_border_color = YELLOW if current_field == "username" else CYAN
    print(f"{indent}{u_border_color}┌── [ USERNAME ] " + "─" * (inner_width - 18) + f"┐{RESET}")
    u_disp = username if username else ("Typing..." if current_field == "username" else "")
    u_line = f"  USERNAME ➔ {u_disp}"
    pad_u = inner_width - 2 - len(f"  USERNAME ➔ {username if username else ('Typing...' if current_field == 'username' else '')}")
    print(f"{indent}{u_border_color}│{RESET}{BOLD}{u_line}{' ' * max(0, pad_u)}{u_border_color}│{RESET}")
    print(f"{indent}{u_border_color}└" + "─" * (inner_width - 2) + f"┘{RESET}")

    print()

    # Password Box
    p_border_color = YELLOW if current_field == "password" else CYAN
    print(f"{indent}{p_border_color}┌── [ PASSWORD ] " + "─" * (inner_width - 18) + f"┐{RESET}")
    p_disp = masked_password if masked_password else ("Typing..." if current_field == "password" else "")
    p_line = f"  PASSWORD ➔ {p_disp}"
    pad_p = inner_width - 2 - len(f"  PASSWORD ➔ {masked_password if masked_password else ('Typing...' if current_field == 'password' else '')}")
    print(f"{indent}{p_border_color}│{RESET}{BOLD}{p_line}{' ' * max(0, pad_p)}{p_border_color}│{RESET}")
    print(f"{indent}{p_border_color}└" + "─" * (inner_width - 2) + f"┘{RESET}")

    print()

    # Login Button Box
    l_border_color = GREEN if current_field == "login" else CYAN
    btn_text = "[ LOGIN NOW ]" if current_field == "login" else "[ LOGGING IN... ]"
    pad_l = (inner_width - 2 - len(btn_text)) // 2
    
    print(f"{indent}{l_border_color}┌" + "─" * (inner_width - 2) + f"┐{RESET}")
    print(f"{indent}{l_border_color}│{RESET}{' ' * pad_l}{BOLD}{GREEN}{btn_text}{RESET}{' ' * (inner_width - 2 - pad_l - len(btn_text))}{l_border_color}│{RESET}")
    print(f"{indent}{l_border_color}└" + "─" * (inner_width - 2) + f"┘{RESET}\n")