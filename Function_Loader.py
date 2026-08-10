import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import winreg
import zipfile
from datetime import datetime, timedelta, timezone

import rarfile
import requests

# Windows Terminal ANSI Color Fix
os.system('')

from Style_Loader import BOLD, CYAN, GREEN, RED, RESET, YELLOW

GITHUB_USER = "splshameem420"
REPO_NAME   = "FREE-FIRE-PANEL"
BRANCH      = "main"
EXE_FOLDER  = "Panel"
EXE_NAME    = "Loader_Free.exe"

DX_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/Requirements/Microsoft%20DirectX/dxwebsetup.exe"
VC_URL = f"https://media.githubusercontent.com/media/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/Requirements/Microsoft%20Visual%20C%2B%2B/Microsoft%20Visual%20C%2B%2B.zip"

# 📂 ইউজারের চোখ থেকে আড়ালে LocalAppData ফোল্ডারে সেভ করার পাথ
APP_STORAGE_DIR = os.path.join(os.getenv('LOCALAPPDATA'), "BD_Hex_Cheat")
DATE_TRACK_FILE = os.path.join(APP_STORAGE_DIR, "folder_commit_date.json")

# ফোল্ডার না থাকলে স্বয়ংক্রিয়ভাবে তৈরি হবে
if not os.path.exists(APP_STORAGE_DIR):
    os.makedirs(APP_STORAGE_DIR, exist_ok=True)

# Cheek Admin Permission
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:  # noqa: BLE001
        return False

# Admin Permission Request
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

# Temp Directory Remove Function
def remove_temp_dir(dir_path):
    """পারমিশন বা ফাইল লক সমস্যা থাকলেও নিরাপদে ফোল্ডার ডিলিট করার ফাংশন"""
    if os.path.exists(dir_path):
        time.sleep(1) 
        try:
            shutil.rmtree(dir_path, ignore_errors=True)
        except Exception:  # noqa: BLE001, S110
            pass

# Check Visual C++ Runtimes Installed
def check_vc_installed_thoroughly():
    """২০০৫-২০২৬ পর্যন্ত রানটাইমগুলোর উপস্থিতি চেক করা"""
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

# Check Requirements
def checking_requirements():
    print(f"    {BOLD}{CYAN}2. Checking requirement files", end="", flush=True)
    for _ in range(3):
        for dots in [".  ", ".. ", "..."]:
            sys.stdout.write(f"\r    {BOLD}{CYAN}2. Checking requirement files{dots}")
            sys.stdout.flush()
            time.sleep(0.3)

    print(f"\r    {BOLD}{CYAN}2. Checking requirement files...   {RESET}")
    time.sleep(0.5)

    vc_ok = check_vc_installed_thoroughly()

    system_path = os.environ.get('SystemRoot', 'C:\\Windows')
    dx_file = os.path.join(system_path, 'System32', 'd3dx9_43.dll')
    dx_ok = os.path.exists(dx_file)

    if vc_ok and dx_ok:
        print(f"       {GREEN}{BOLD}✔ Requirement files already installed...{RESET}")
        time.sleep(0.8)
        return True

    print(f"       {YELLOW}{BOLD}Requirement files update detected! Downloading...{RESET}")
    time.sleep(1)

    # হিডেন স্টোরেজ পাথে টেম্প ফাইল প্রসেস করা
    vc_zip = os.path.join(APP_STORAGE_DIR, "vc_temp.zip")
    dx_exe = os.path.join(APP_STORAGE_DIR, "dxwebsetup.exe")
    extract_dir = os.path.join(APP_STORAGE_DIR, "req_extract_temp")

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
                print(f"       {GREEN}{BOLD}Visual C++ Install Complete!{RESET}")

        if not dx_ok:
            print(f"       {CYAN}{BOLD}Downloading DirectX Web Setup...{RESET}")
            req = urllib.request.Request(DX_URL, headers=headers)
            with urllib.request.urlopen(req) as response, open(dx_exe, 'wb') as f:
                f.write(response.read())

            print(f"       {CYAN}{BOLD}Installing DirectX (Silent)...{RESET}")
            subprocess.run([dx_exe, "/Q"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"       {GREEN}{BOLD}DirectX Install Complete!{RESET}")

        # ফাইল ক্লিনিং (Clean Up)
        if os.path.exists(vc_zip):
            try: os.remove(vc_zip)
            except Exception: pass  # noqa: BLE001, S110

        if os.path.exists(dx_exe):
            try: os.remove(dx_exe)
            except Exception: pass  # noqa: BLE001, S110

        remove_temp_dir(extract_dir)

        print(f"       {GREEN}{BOLD}All requirement files successfully configured!{RESET}")
        return True

    except Exception as e:  # noqa: BLE001
        print(f"       {RED}{BOLD}Installation failed: {e}{RESET}")
        
        if os.path.exists(vc_zip):
            try: os.remove(vc_zip)
            except Exception: pass  # noqa: BLE001, S110

        if os.path.exists(dx_exe):
            try: os.remove(dx_exe)
            except Exception: pass  # noqa: BLE001, S110

        remove_temp_dir(extract_dir)
            
        return False

# GitHub EXE Download and Run Function Daili C++ Free panel exe
def download_and_run_github_exe():
    """Panel ফোল্ডারের Commit Date চেক, ডাউনলোড, এক্সট্র্যাক্ট এবং আসল .exe ফাইল খুঁজে রান করার ফাংশন"""
    def get_latest_github_data():

        contents_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{EXE_FOLDER}?ref={BRANCH}"
        commits_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/commits?path={EXE_FOLDER}&sha={BRANCH}&page=1&per_page=1"

        rar_files = []
        latest_commit_date = None

        try:
            res_contents = requests.get(contents_url, timeout=10)
            if res_contents.status_code == 200:
                for item in res_contents.json():
                    if item.get("type") == "file" and item.get(
                        "name", ""
                    ).endswith((".rar", ".exe", ".zip")):
                        rar_files.append(item)

            res_commits = requests.get(commits_url, timeout=10)
            if res_commits.status_code == 200 and len(res_commits.json()) > 0:
                latest_commit_date = res_commits.json()[0]["commit"]["committer"]["date"]

        except Exception as e:  # noqa: BLE001
            print(f"        {RED}{BOLD}Error fetching API: {e}{RESET}")

        if rar_files:
            latest_file = max(rar_files, key=lambda x: x["name"])
            return (
                latest_file["name"],
                latest_file["download_url"],
                latest_commit_date,
            )

        return None, None, None

    def get_online_bd_now():
        """পিসির ঘড়ি বাইপাস প্রতিরোধে সরাসরি অনলাইন সার্ভার থেকে আসল বাংলাদেশ সময় সংগ্রহ করে"""
        try:
            response = requests.head("https://api.github.com", timeout=5)
            server_date_str = response.headers.get("Date")
            if server_date_str:
                utc_now = datetime.strptime(server_date_str, "%a, %d %b %Y %H:%M:%S GMT")  # noqa: DTZ007
                return utc_now + timedelta(hours=6)
        except Exception:  # noqa: BLE001, S110
            pass

        return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=6))).replace(tzinfo=None)

    def parse_bd_datetime(utc_string):
        """GitHub ISO সময়কে বাংলাদেশ সময়ে রূপান্তর করে"""
        if not utc_string:
            return None, ""
        try:
            clean_time_str = utc_string.replace("Z", "").replace("T", " ")
            if "." in clean_time_str:
                clean_time_str = clean_time_str.split(".")[0]

            utc_dt = datetime.strptime(clean_time_str, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
            bd_dt = utc_dt + timedelta(hours=6)
            return bd_dt, bd_dt.strftime("%Y-%m-%d %I:%M:%S %p")
        except Exception:  # noqa: BLE001
            return None, utc_string

    def get_saved_commit_date():
        if os.path.exists(DATE_TRACK_FILE):
            try:
                with open(DATE_TRACK_FILE, "r") as f:
                    return json.load(f).get("folder_commit_date", "")
            except Exception:  # noqa: BLE001, S110
                pass
        return ""

    def save_commit_date(commit_date):
        if commit_date:
            try:
                with open(DATE_TRACK_FILE, "w") as f:
                    json.dump({"folder_commit_date": commit_date}, f)
            except Exception:  # noqa: BLE001, S110
                pass

    def purge_old_files():
        """মেয়াদ শেষ হলে লোকাল ফোল্ডারের সব পুরনো .rar, .zip এবং .exe ফাইল মুছে ফেলে"""
        if os.path.exists(APP_STORAGE_DIR):
            for file in os.listdir(APP_STORAGE_DIR):
                file_path = os.path.join(APP_STORAGE_DIR, file)

                if file == os.path.basename(DATE_TRACK_FILE):
                    continue

                if file.endswith((".rar", ".zip", ".exe")):
                    try:
                        os.remove(file_path)
                    except Exception:  # noqa: BLE001, S110
                        pass

    def download_file(file_url, save_path):
        print(f"        {CYAN}Downloading...{RESET}")
        try:
            get_response = requests.get(file_url, stream=True, timeout=15)
            if get_response.status_code == 200:
                total_size = int(get_response.headers.get("content-length", 0))
                downloaded = 0

                with open(save_path, "wb") as file:
                    for chunk in get_response.iter_content(chunk_size=4096):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = downloaded * 100 // total_size
                                done = int(20 * downloaded / total_size)
                                sys.stdout.write(f"\r    {GREEN}[{'=' * done}{' ' * (20 - done)}] {percent}%{RESET}")
                                sys.stdout.flush()

                print(f"       {GREEN}{BOLD}Download Completed!{RESET}")
                return True
        except Exception as e:  # noqa: BLE001
            print(f"        {RED}{BOLD}Download Error: {e}{RESET}")
        return False

    def extract_rar(file_path):
        if file_path.endswith(".rar"):
            try:
                unrar_tool = None
                local_unrar = os.path.join(APP_STORAGE_DIR, "UnRAR.exe")
                winrar_paths = [
                    r"C:\Program Files\WinRAR\UnRAR.exe",
                    r"C:\Program Files\WinRAR\WinRAR.exe",
                    r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
                    r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
                    local_unrar,
                ]

                for path in winrar_paths:
                    if os.path.exists(path):
                        unrar_tool = path
                        break
                if not unrar_tool:
                    unrar_url = "https://www.rarlab.com/rar/unrar.exe"
                    try:
                        res = requests.get(unrar_url, timeout=10)
                        if res.status_code == 200:
                            with open(local_unrar, "wb") as f:
                                f.write(res.content)
                            unrar_tool = local_unrar
                    except Exception:  # noqa: BLE001, S110
                        pass

                if not unrar_tool or not os.path.exists(unrar_tool):
                    print(f"        {RED}{BOLD}Failed to acquire UnRAR tool!{RESET}")
                    return False
                rarfile.UNRAR_TOOL = unrar_tool

                with rarfile.RarFile(file_path) as rf:
                    rf.extractall(path=APP_STORAGE_DIR, pwd="1")

                return True

            except Exception as e:  # noqa: BLE001
                print(f"        {RED}{BOLD}Extraction Error: {e}{RESET}")
                return False

        return True

    def find_and_run_exe():
        exe_to_run = None
        for root, _, files in os.walk(APP_STORAGE_DIR):
            for file in files:
                if file.endswith(".exe") and not file.startswith("python"):
                    exe_to_run = os.path.join(root, file)
                    break
            if exe_to_run:
                break

        if exe_to_run and os.path.exists(exe_to_run):
            print(f"        {YELLOW}Launching Panel ({os.path.basename(exe_to_run)})...{RESET}")
            time.sleep(1)
            subprocess.Popen(
                [exe_to_run],
                cwd=APP_STORAGE_DIR,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            return True
        else:
            print(f"        {RED}{BOLD}No executable (.exe) found!{RESET}")
            return False

    print(f"    {YELLOW}3. Checking Panel Updates...{RESET}")

    rar_file_name, file_url, latest_commit_date = get_latest_github_data()

    if not rar_file_name or not file_url or not latest_commit_date:
        print(f"        {RED}{BOLD} No Update File Found {RESET}")
        return False

    online_bd_now = get_online_bd_now()
    commit_bd_dt, formatted_time = parse_bd_datetime(latest_commit_date)

    # ১. রাত ১২:০০ টার পর পুরনো দিনের সব প্যানেল অফলাইন করে মুছে ফেলার লজিক
    if commit_bd_dt and commit_bd_dt.date() < online_bd_now.date():
        print(f"        {RED}{BOLD} No update found for today! (Previous version expired at 12:00 AM){RESET}")
        purge_old_files()
        return False

    local_rar_path = os.path.join(APP_STORAGE_DIR, rar_file_name)
    saved_commit_date = get_saved_commit_date()

    # ২. আজকের দিনে আপডেট নামানো থাকলে সেটি চালানো হবে
    if os.path.exists(local_rar_path) and saved_commit_date == latest_commit_date:
        print(f"        {GREEN}{BOLD}Panel is up to date ({formatted_time}){RESET}")
        return find_and_run_exe()

    # ৩. আজকের নতুন আপডেট পাওয়ার পর ডাউনলোড ও এক্সট্র্যাক্ট
    print(f"        {YELLOW}New update detected! ({formatted_time}){RESET}")

    purge_old_files()

    if download_file(file_url, local_rar_path) and extract_rar(local_rar_path):
        save_commit_date(latest_commit_date)
        return find_and_run_exe()

    return False

# Main EXE Download and Update Function
def download_and_update_main_exe():
    """ভার্সন ফাইল চেক করে মেইন এক্সি (Main EXE) রিপ্লেস করবে ও রান করবে"""
    version_json_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/version.json"

    print(f"    {YELLOW}{BOLD}1. Checking for Main EXE Updates...{RESET}")

    try:
        ver_res = requests.get(version_json_url, headers={"Cache-Control": "no-cache"}, timeout=10)
        
        if ver_res.status_code == 200:
            version_data = ver_res.json()
            latest_version = version_data.get("version", "2.0")

            dynamic_exe_name = f"bd-hex-cheat{latest_version}.exe"
            file_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/Updates/{dynamic_exe_name}"
            local_file_path = os.path.join(APP_STORAGE_DIR, dynamic_exe_name)

            head_response = requests.head(file_url, headers={"Cache-Control": "no-cache"}, timeout=10)

            if head_response.status_code == 200:
                remote_size = int(head_response.headers.get("content-length", 0))
                if os.path.exists(local_file_path):
                    local_size = os.path.getsize(local_file_path)
                    if remote_size > 0 and local_size == remote_size:
                        print(f"    {GREEN}{BOLD}Main EXE (v{latest_version}) is up to date!{RESET}")
                        return True
                print(f"    {YELLOW}{BOLD}New Main EXE Update (v{latest_version}) Found! Replacing old version...{RESET}")
                get_response = requests.get(file_url, stream=True, timeout=15)

                if get_response.status_code == 200:
                    downloaded = 0
                    with open(local_file_path, "wb") as file:
                        for chunk in get_response.iter_content(chunk_size=4096):
                            if chunk:
                                file.write(chunk)
                                downloaded += len(chunk)
                                if remote_size > 0:
                                    percent = downloaded * 100 // remote_size
                                    done = int(20 * downloaded / remote_size)
                                    sys.stdout.write(f"\r    {GREEN}[{'=' * done}{' ' * (20 - done)}] {percent}%{RESET}")
                                    sys.stdout.flush()

                    print(f"    {GREEN}{BOLD}Main EXE Updated Successfully!{RESET}")

                    for old_file in os.listdir(APP_STORAGE_DIR):
                        if old_file.startswith("bd-hex-cheat") and old_file.endswith(".exe") and old_file != dynamic_exe_name:
                            try:
                                os.remove(os.path.join(APP_STORAGE_DIR, old_file))
                            except Exception:  # noqa: BLE001, S110
                                pass

                    print(f"        {CYAN}Launching Updated Main EXE...{RESET}")
                    time.sleep(1)

                    subprocess.Popen(
                        [local_file_path],
                        cwd=APP_STORAGE_DIR,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                    return True

    except Exception as e:  # noqa: BLE001
        print(f"    {RED}{BOLD}❌ Error: {e}{RESET}")

    return False



