import ctypes
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import winreg
import zipfile

import requests

# Windows Terminal ANSI Color Fix
os.system('')

from Style_Loader import BOLD, CYAN, GREEN, RED, RESET, YELLOW

GITHUB_USER = "splshameem420"
REPO_NAME   = "Loader-"
BRANCH      = "main"
EXE_FOLDER  = "Panel"
EXE_NAME    = "Loader_Free.exe"

DX_URL = "https://raw.githubusercontent.com/splshameem420/Loader-/refs/heads/main/Requirements/Microsoft%20DirectX/dxwebsetup.exe"
VC_URL = "https://media.githubusercontent.com/media/splshameem420/Loader-/refs/heads/main/Requirements/Microsoft%20Visual%20C%2B%2B/Microsoft%20Visual%20C%2B%2B.zip"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:  # noqa: BLE001
        return False


def request_admin():
    """ইউজার অ্যাডমিন না হলে অ্যাডমিন হিসেবে নতুন উইন্ডো খুলবে"""
    if not is_admin():
        try:
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            if int(ret) > 32:
                os._exit(0)
            else:
                sys.exit(1)
        except Exception:  # noqa: BLE001
            sys.exit(1)

def remove_temp_dir(dir_path):
    """পারমিশন বা ফাইল লক সমস্যা থাকলেও নিরাপদে ফোল্ডার ডিলিট করার ফাংশন"""
    if os.path.exists(dir_path):
        time.sleep(1) 
        try:
            shutil.rmtree(dir_path, ignore_errors=True)
        except Exception:  # noqa: BLE001, S110
            pass

def check_vc_installed_thoroughly():
    """আপনার প্যাকেজে থাকা ২০০৫-২০২৬ পর্যন্ত রানটাইমগুলোর উপস্থিতি চেক করা"""
    system_path = os.environ.get('SystemRoot', 'C:\\Windows')
    
    core_dlls = [
        "msvcr100.dll",     # Visual C++ 2010
        "msvcr120.dll",     # Visual C++ 2013
        "vcruntime140.dll"  # Visual C++ 2015-2026 Redistributable
    ]

    missing_count = 0
    for dll in core_dlls:
        dll_32 = os.path.join(system_path, 'System32', dll)
        dll_64 = os.path.join(system_path, 'SysWOW64', dll)
        
        if not (os.path.exists(dll_32) or os.path.exists(dll_64)):
            missing_count += 1

    if missing_count == 0:
        return True

    uninstall_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    vc_count = 0
    for u_path in uninstall_paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, u_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    winreg.CloseKey(subkey)
                    
                    if "Visual C++" in display_name:
                        vc_count += 1
                except Exception:  # noqa: BLE001, S112
                    continue
            winreg.CloseKey(key)
        except Exception:  # noqa: BLE001, S112
            continue

    return vc_count >= 3


def checking_requirements():
    print(f"    {BOLD}{CYAN}1. Checking requirement files", end="", flush=True)
    for _ in range(3):
        for dots in [".  ", ".. ", "..."]:
            sys.stdout.write(f"\r    {BOLD}{CYAN}1. Checking requirement files{dots}")
            sys.stdout.flush()
            time.sleep(0.3)

    print(f"\r    {BOLD}{CYAN}1. Checking requirement files...   {RESET}")
    time.sleep(0.5)

    vc_ok = check_vc_installed_thoroughly()

    system_path = os.environ.get('SystemRoot', 'C:\\Windows')
    dx_file = os.path.join(system_path, 'System32', 'd3dx9_43.dll')
    dx_ok = os.path.exists(dx_file)
    

    if vc_ok and dx_ok:
        print(f"       {GREEN}{BOLD}✔ Requirement files already installed...{RESET}\n")
        time.sleep(0.8)
        return True

    print(f"       {YELLOW}{BOLD}Requirement files update detected! Downloading...{RESET}\n")
    time.sleep(1)

    vc_zip = "vc_temp.zip"
    dx_exe = "dxwebsetup.exe"
    extract_dir = "req_extract_temp"

    try:
        os.makedirs(extract_dir, exist_ok=True)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        if not vc_ok:
            print(f"       {CYAN}{BOLD}Downloading Visual C++ Package...{RESET}")
            req = urllib.request.Request(VC_URL, headers=headers)
            with urllib.request.urlopen(req) as response, open(vc_zip, 'wb') as f:
                f.write(response.read())

            print(f"       {CYAN}{BOLD}Extracting Visual C++...{RESET}")
            vc_target = os.path.join(extract_dir, "VC")
            with zipfile.ZipFile(vc_zip, 'r') as z:
                z.extractall(vc_target)

            bat_path = None
            for root, _, files in os.walk(vc_target):
                if "install_all.bat" in files:
                    bat_path = os.path.join(root, "install_all.bat")
                    break

            if bat_path:
                print(f"       {CYAN}{BOLD}Installing Visual C++ Runtimes...{RESET}")
                bat_dir = os.path.dirname(bat_path)
                subprocess.run(
                    f'cmd /c "echo. | {os.path.basename(bat_path)}"', 
                    cwd=bat_dir, 
                    shell=True, 
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"       {GREEN}{BOLD}Visual C++ Install Complete!{RESET}\n")

        if not dx_ok:
            print(f"       {CYAN}{BOLD}Downloading DirectX Web Setup...{RESET}")
            req = urllib.request.Request(DX_URL, headers=headers)
            with urllib.request.urlopen(req) as response, open(dx_exe, 'wb') as f:
                f.write(response.read())

            print(f"       {CYAN}{BOLD}Installing DirectX (Silent)...{RESET}")
            subprocess.run([dx_exe, "/Q"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"       {GREEN}{BOLD}DirectX Install Complete!{RESET}\n")

        # ফাইল ক্লিনিং (Clean Up)
        if os.path.exists(vc_zip):
            try: os.remove(vc_zip)
            except Exception: pass  # noqa: BLE001, S110

        if os.path.exists(dx_exe):
            try: os.remove(dx_exe)
            except Exception: pass  # noqa: BLE001, S110

        remove_temp_dir(extract_dir)

        print(f"       {GREEN}{BOLD}All requirement files successfully configured!{RESET}\n")
        return True

    except Exception as e:  # noqa: BLE001
        print(f"       {RED}{BOLD}Installation failed: {e}{RESET}\n")
        
        if os.path.exists(vc_zip):
            try: os.remove(vc_zip)
            except Exception: pass  # noqa: BLE001, S110

        if os.path.exists(dx_exe):
            try: os.remove(dx_exe)
            except Exception: pass  # noqa: BLE001, S110

        remove_temp_dir(extract_dir)
            
        return False
    
    
    
def download_and_run_github_exe():
    """উপরে ডিফাইন করা লিঙ্ক থেকে সরাসরি আপডেট চেক এবং রান করবে"""

    # 🔗 Raw URL তৈরি
    if EXE_FOLDER:
        file_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{EXE_FOLDER}/{EXE_NAME}"
    else:
        file_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{EXE_NAME}"

    local_file_path = os.path.join(os.getcwd(), EXE_NAME)

    print(f"    {YELLOW}Checking for updates...{RESET}")

    try:
        # ১. ফাইলের সাইজ চেক
        head_response = requests.head(file_url, timeout=10)

        if head_response.status_code == 200:
            remote_size = int(head_response.headers.get("content-length", 0))

            if os.path.exists(local_file_path):
                local_size = os.path.getsize(local_file_path)

                if local_size == remote_size and remote_size > 0:
                    print(
                        f"    {GREEN}{BOLD}✔ Latest version installed!{RESET}"
                    )
                    print(f"    {CYAN}Launching...{RESET}\n")
                    time.sleep(1)
                    subprocess.Popen(
                        [local_file_path], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    return True

            print(
                f"    {YELLOW}New update found! Downloading...{RESET}"
            )

            get_response = requests.get(file_url, stream=True, timeout=15)
            if get_response.status_code == 200:
                total_size = remote_size
                downloaded = 0

                with open(local_file_path, "wb") as file:
                    for chunk in get_response.iter_content(chunk_size=4096):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0:
                                percent = downloaded * 100 // total_size
                                done = int(20 * downloaded / total_size)
                                sys.stdout.write(
                                    f"\r    {GREEN}[{'=' * done}{' ' * (20 - done)}] {percent}%{RESET}"
                                )
                                sys.stdout.flush()

                print(
                    f"\n\n    {GREEN}{BOLD}✔ Download Completed!{RESET}"
                )
                print(f"    {CYAN}Launching...{RESET}\n")
                time.sleep(1)

                subprocess.Popen(
                    [local_file_path], 
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                return True
            else:
                print(
                    f"    {RED}{BOLD}❌ Failed to download! HTTP Status: {get_response.status_code}{RESET}\n"
                )

        else:
            print(
                f"    {RED}{BOLD}❌ File not found on GitHub.{RESET}\n"
            )

    except Exception as e:  # noqa: BLE001
        print(f"    {RED}{BOLD}❌ Connection Error: {e}{RESET}\n")

    if os.path.exists(local_file_path):
        print(
            f"    {YELLOW}Running existing local file offline...{RESET}\n"
        )
        time.sleep(1)
        
        subprocess.Popen(
            [local_file_path], 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        return True

    return False