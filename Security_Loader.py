import ctypes
import sys

# ANSI Color Codes
RED = '\033[91m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

def is_debugger_present():
    """Checks if the application is running under a debugger."""
    try:
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0
    except Exception:  # noqa: BLE001
        return False

def is_admin():
    """Checks if the script is running with Administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:  # noqa: BLE001
        return False

def run_security_check():
    """Main security wall. Call this function at startup."""
    # 1. Anti-Debugging Check
    if is_debugger_present():
        print(f"\n{RED}{BOLD}[SECURITY ALERT] Debugger / Inspection Tool Detected! Access Denied.{RESET}\n")
        sys.exit(1)

    # 2. Administrator Rights Check (Optional Info Warning)
    if not is_admin():
        print(f"{YELLOW}{BOLD}[WARNING] Running without Administrator privileges. Some features might be restricted.{RESET}")

    return True