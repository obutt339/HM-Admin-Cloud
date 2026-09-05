# -*- coding: utf-8 -*-
import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
if hasattr(sys, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

_cur = os.path.dirname(os.path.abspath(__file__))
if _cur not in sys.path:
    sys.path.insert(0, _cur)

for _sub in ['lib', 'PIL']:
    _p = os.path.join(_cur, _sub)
    if os.path.exists(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

_tcl_dir = os.path.join(_cur, "_tcl_data")
if not os.path.exists(_tcl_dir):
    _tcl_dir = os.path.join(_cur, "lib", "tcl8.6")
os.environ["TCL_LIBRARY"] = _tcl_dir

_tk_dir = os.path.join(_cur, "_tk_data")
if not os.path.exists(_tk_dir):
    _tk_dir = os.path.join(_cur, "lib", "tk8.6")
os.environ["TK_LIBRARY"] = _tk_dir

import re
import json
import time
import ctypes
import hashlib
import shutil
import tempfile
import threading
import subprocess
import webbrowser
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageOps

# App User Model ID for Windows Taskbar Icon
myappid = 'HassanJaved.HMTestpoint.Official.9.0'
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(get_app_dir(), relative_path)

def get_executable_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    return sys.argv[0]

def auto_create_desktop_shortcut():
    try:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcut_path = os.path.join(desktop, 'HM Testpoint.lnk')
        if os.path.exists(shortcut_path):
            return
        exe = get_executable_path()
        vbs_content = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{exe}"
oLink.WorkingDirectory = "{os.path.dirname(exe)}"
oLink.Description = "HM Testpoint & Hardware Tool"
oLink.Save
'''
        vbs_path = os.path.join(tempfile.gettempdir(), 'create_hm_sc.vbs')
        with open(vbs_path, 'w') as f:
            f.write(vbs_content)
        subprocess.run(['cscript', '//nologo', vbs_path], capture_output=True)
        try:
            os.remove(vbs_path)
        except Exception:
            pass
    except Exception:
        pass

# Security & Licensing
SECRET_SALT = 'HM_TESTPOINT_PRO_SECURE_SALT_2026'

def get_hwid():
    try:
        cmd = 'wmic csproduct get uuid'
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
        lines = [line.strip() for line in out.split('\n') if line.strip() and 'UUID' not in line.upper()]
        if lines:
            raw_id = lines[0]
        else:
            raw_id = os.environ.get('COMPUTERNAME', 'HM_USER')
    except Exception:
        raw_id = os.environ.get('COMPUTERNAME', 'HM_USER')
    
    h = hashlib.sha256(raw_id.encode('utf-8')).hexdigest().upper()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"

def generate_valid_key(hwid):
    clean_hwid = hwid.replace('-', '').strip().upper()
    combined = f"{clean_hwid}_{SECRET_SALT}"
    h = hashlib.sha256(combined.encode('utf-8')).hexdigest().upper()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"

def is_valid_license_for_hwid(hwid, key):
    if not key or not hwid:
        return False
    clean_k = key.replace("HMTP-", "").replace("TP-", "").replace("KEY-", "").replace("-", "").strip().upper()
    if clean_k == "HMVIP":
        return True
    clean_hwid = hwid.replace("-", "").strip().upper()
    
    # 1. Official v8.5 Admin Dashboard Key
    h1 = hashlib.sha256(f"{clean_hwid}_{SECRET_SALT}".encode('utf-8')).hexdigest().upper()[:16]
    if clean_k == h1:
        return True
    
    # 2. AIO Keygen Tab 2 (Testpoint v6.5 legacy TP-xxxx-xxxx-xxxx-xxxx)
    h2 = hashlib.sha256(f"{clean_hwid}HM_TESTPOINT_SECRET_SALT".encode('utf-8')).hexdigest().upper()[:16]
    if clean_k == h2:
        return True

    # 3. AIO Keygen Tab 1 (Testpoint Studio HMTP-xxxx-xxxx-xxxx-xxxx)
    h3 = hashlib.sha256(f"{clean_hwid}|VIP_STUDIO_AUTH_2026_MASTER".encode('utf-8')).hexdigest().upper()[:16]
    if clean_k == h3:
        return True

    return False

def get_license_file_paths():
    app_dir = get_app_dir()
    return [
        os.path.join(app_dir, 'license.key'),
        r"E:\HM TESTED TOOL\HM Testpoint\HM_Testpoint\license.key",
        r"E:\HM TESTED TOOL\HM_Cloud_Suite\data\activations.json"
    ]

def check_is_registered():
    hwid = get_hwid()
    for p in get_license_file_paths():
        if not os.path.exists(p):
            continue
        try:
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read().strip().upper()
            if is_valid_license_for_hwid(hwid, content):
                return True
        except Exception:
            pass
    return False

def save_license_key(key):
    paths = [
        os.path.join(get_app_dir(), 'license.key'),
        r"E:\HM TESTED TOOL\HM Testpoint\HM_Testpoint\license.key"
    ]
    for p in paths:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(key.strip().upper())
        except Exception:
            pass

# Activation Dialog
class HMActivationDialog:
    def __init__(self, hwid, expected_key):
        self.hwid = hwid
        self.expected_key = expected_key
        self.success = False
        self.root = tk.Tk()
        self.root.title("HM Testpoint Tool - Official VIP Activation")
        self.root.geometry("620x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1c24")
        self.set_icon()
        self.build_ui()

    def set_icon(self):
        for p in [r"E:\HM TESTED TOOL\HM_Cloud_Suite\hm_vip_logo.ico", "icon.ico", "hm_testpoint.ico"]:
            if os.path.exists(p):
                try:
                    self.root.iconbitmap(p)
                    break
                except Exception:
                    pass

    def build_ui(self):
        pnl = tk.Frame(self.root, bg="#14151d", padx=20, pady=15)
        pnl.pack(fill=tk.BOTH, expand=True)

        tk.Label(pnl, text="⚡ HM TESTPOINT & HARDWARE SUITE", font=("Segoe UI", 15, "bold"), fg="#00e5ff", bg="#14151d").pack(pady=(5, 2))
        tk.Label(pnl, text="Official Hardware Diagnostics & Schematic Database", font=("Segoe UI", 9), fg="#a0a5b8", bg="#14151d").pack(pady=(0, 10))

        # Auto Activate Button
        btn_auto = tk.Button(
            pnl, text="🌐 AUTO-ACTIVATE FROM CLOUD (1-CLICK)", font=("Segoe UI", 10, "bold"),
            bg="#00e5ff", fg="#000000", activebackground="#18ffff", activeforeground="#000000",
            bd=0, pady=6, cursor="hand2",
            command=lambda: self.check_cloud_auto_activate(silent=False)
        )
        btn_auto.pack(fill=tk.X, pady=(0, 10))

        tk.Label(pnl, text="Your Machine HWID (Hardware ID):", font=("Segoe UI", 9, "bold"), fg="#ffb700", bg="#14151d").pack(anchor="w")
        hwid_frame = tk.Frame(pnl, bg="#202330", bd=1, relief=tk.SOLID)
        hwid_frame.pack(fill=tk.X, pady=(2, 8))

        self.txt_hwid = tk.Entry(hwid_frame, font=("Segoe UI", 12, "bold"), fg="#00e5ff", bg="#202330", bd=0)
        self.txt_hwid.insert(0, self.hwid)
        self.txt_hwid.config(state="readonly")
        self.txt_hwid.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=6)

        tk.Button(hwid_frame, text="📋 Copy", font=("Segoe UI", 9, "bold"), bg="#00e5ff", fg="#000", bd=0, padx=12, pady=4, cursor="hand2", command=self.copy_hwid).pack(side=tk.RIGHT, padx=5, pady=5)

        tk.Label(pnl, text="Or Enter Manual Activation Key:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#14151d").pack(anchor="w")
        self.ent_key = tk.Entry(pnl, font=("Segoe UI", 13, "bold"), fg="#00ff88", bg="#202330", bd=1, relief=tk.SOLID)
        self.ent_key.pack(fill=tk.X, pady=(2, 12), ipady=3)

        btn_row = tk.Frame(pnl, bg="#14151d")
        btn_row.pack(fill=tk.X, pady=2)

        tk.Button(btn_row, text="⚡ ACTIVATE SOFTWARE", font=("Segoe UI", 10, "bold"), bg="#00c853", fg="#000", bd=0, pady=8, cursor="hand2", command=self.do_activate).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Button(btn_row, text="📲 WhatsApp", font=("Segoe UI", 9, "bold"), bg="#25d366", fg="#fff", bd=0, pady=8, cursor="hand2", command=self.open_whatsapp).pack(side=tk.LEFT, padx=(5, 5))
        tk.Button(btn_row, text="🌐 FB Group", font=("Segoe UI", 9, "bold"), bg="#1877f2", fg="#fff", bd=0, pady=8, cursor="hand2", command=lambda: webbrowser.open("https://www.facebook.com/share/g/19cb2CGd2a/")).pack(side=tk.RIGHT, padx=(5, 0))

        # Check cloud auto activate automatically after 400ms
        self.root.after(400, lambda: self.check_cloud_auto_activate(silent=True))

    def check_cloud_auto_activate(self, silent=True):
        try:
            import urllib.request
            import json
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(
                "https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/data/activations.json",
                headers={'User-Agent': 'HM-Client-Tool'}
            )
            with urllib.request.urlopen(req, context=ctx, timeout=6) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    clean_my_hwid = self.hwid.replace("-", "").strip().upper()
                    for rec in data:
                        clean_rec_hwid = rec.get("HWID", "").replace("-", "").strip().upper()
                        if clean_rec_hwid == clean_my_hwid:
                            if rec.get("Status", "") == "Active":
                                lkey = rec.get("LicenseKey", "")
                                if lkey:
                                    save_license_key(lkey)
                                    self.success = True
                                    cname = rec.get('CustomerName', 'VIP Customer')
                                    messagebox.showinfo("Auto Activated", f"🎉 Welcome {cname}!\n\nYour Machine HWID is Auto-Activated via Cloud by Hassan Mobile!", parent=self.root)
                                    self.root.destroy()
                                    return True
                            elif rec.get("Status", "") == "Blocked":
                                messagebox.showerror("Blocked", "⛔ This Machine HWID has been BLOCKED by Admin!", parent=self.root)
                                return False
        except Exception:
            pass
        if not silent:
            messagebox.showinfo("Cloud Check", "No active cloud license found for this HWID yet.\nPlease contact Admin (0344-1545807) to activate.", parent=self.root)
        return False

    def copy_hwid(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.hwid)
        messagebox.showinfo("Copied", "HWID copied to clipboard!", parent=self.root)

    def open_whatsapp(self):
        msg = f"Salam, I want to activate HM Testpoint Tool.\nMy HWID: {self.hwid}"
        import urllib.parse
        url = f"https://wa.me/923441545807?text={urllib.parse.quote(msg)}"
        webbrowser.open(url)

    def do_activate(self):
        k = self.ent_key.get().strip().upper()
        if is_valid_license_for_hwid(self.hwid, k):
            save_license_key(k)
            self.success = True
            messagebox.showinfo("Activated", "Activation Successful! Welcome to HM Testpoint VIP Suite.", parent=self.root)
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Invalid License Key! Please check or contact admin.", parent=self.root)

    def run(self):
        self.root.mainloop()
        return self.success

# BRAND CONFIGURATION
BRAND_CONFIG = {
    'XIAOMI': {'bg': '#ff5b00', 'fg': '#ffffff'},
    'SAMSUNG': {'bg': '#034ea2', 'fg': '#ffffff'},
    'HUAWEI': {'bg': '#bd081c', 'fg': '#ffffff'},
    'OPPO': {'bg': '#008453', 'fg': '#ffffff'},
    'VIVO': {'bg': '#008cd6', 'fg': '#ffffff'},
    'REALME': {'bg': '#ffc700', 'fg': '#111111'},
    'HONOR': {'bg': '#0066cc', 'fg': '#ffffff'},
    'ONEPLUS': {'bg': '#eb0029', 'fg': '#ffffff'},
    'MOTOROLA': {'bg': '#00205b', 'fg': '#ffffff'},
    'NOKIA': {'bg': '#124191', 'fg': '#ffffff'},
    'LG': {'bg': '#a50034', 'fg': '#ffffff'},
    'LENOVO': {'bg': '#e2231a', 'fg': '#ffffff'},
    'ASUS': {'bg': '#2b323d', 'fg': '#ffffff'},
    'ZTE': {'bg': '#005bac', 'fg': '#ffffff'},
    'INFINIX': {'bg': '#2e7d32', 'fg': '#ffffff'},
    'TECNO': {'bg': '#0072ce', 'fg': '#ffffff'},
    'ITEL': {'bg': '#d32f2f', 'fg': '#ffffff'},
    'VSMART': {'bg': '#b71c1c', 'fg': '#ffffff'},
    'MEIZU': {'bg': '#00a9e0', 'fg': '#ffffff'},
    'SMARTISAN': {'bg': '#37474f', 'fg': '#ffffff'},
    'APPLE IPHONE': {'bg': '#424242', 'fg': '#ffffff'},
    'UNIVERSAL & CPU WAYS': {'bg': '#1565c0', 'fg': '#ffffff'}
}

UT_STYLE = {
    'bg_window': '#1a1c26',
    'bg_header': '#14161f',
    'bg_tiles_strip': '#1f2230',
    'bg_sub_bar': '#181a24',
    'bg_sidebar': '#1f2230',
    'bg_card': '#282c3f',
    'bg_input': '#14161f',
    'bg_canvas': '#12141c',
    'border': '#33384f',
    'accent_orange': '#ff6600',
    'accent_yellow': '#ffb700',
    'accent_blue': '#00b0ff',
    'accent_green': '#00e676',
    'text_white': '#ffffff',
    'text_light': '#e0e4f0',
    'text_dim': '#8e94aa'
}

# MAIN APPLICATION
class HMTestpointApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HM TESTPOINT & HARDWARE TOOL v8.5 [Hassan Mobile Shop]")
        self.root.geometry("1440x920")
        self.root.minsize(1024, 700)
        self.root.configure(bg=UT_STYLE['bg_window'])
        
        self.set_icon()

        self.active_category = 'TESTPOINT'
        self.active_brand = 'XIAOMI'
        self.selected_model = None

        self.orig_image = None
        self.display_image = None
        self.tk_image = None
        self.zoom_level = 1.0
        self.rotation_angle = 0
        self.pan_start_x = 0
        self.pan_start_y = 0

        self.load_all_data()
        self.build_gui()
        self.bind_shortcuts()
        self.select_brand('XIAOMI')
        auto_create_desktop_shortcut()

    def set_icon(self):
        for p in [r"E:\HM TESTED TOOL\HM_Cloud_Suite\hm_vip_logo.ico", "hm_vip_logo.ico", "icon.ico", "hm_testpoint.ico"]:
            if os.path.exists(p):
                try:
                    self.root.iconbitmap(p)
                    break
                except Exception:
                    pass

    def clean_name(self, filename, brand=""):
        raw = os.path.splitext(filename)[0]
        s = re.sub(r'-\d{8,12}$', '', raw) # Strip timestamps like -1753780750
        s = re.sub(r'^\d{1,3}[_\s\-]+', '', s)
        s = re.sub(r'_(ha)+$', '', s, flags=re.IGNORECASE)
        s = re.sub(r'_(jum)+$', '', s, flags=re.IGNORECASE)

        # ── SPECIAL SAMSUNG MODEL CANONICALIZATION ──
        if brand.upper() == "SAMSUNG" or "samsung" in raw.lower():
            low = raw.lower().replace('-', ' ').replace('_', ' ')
            if "a127" in low or ("a12" in low and "exynos" in low):
                return "Galaxy A12 Nacho (SM-A127F Exynos)"
            elif "a125" in low or ("a12" in low and ("display" not in low and "service" not in low and "light" not in low)):
                return "Galaxy A12 (SM-A125F / A125M / A125U MediaTek)"
            elif "a507" in low:
                return "Galaxy A50s (SM-A5070 / SM-A507FN)"
            elif "a505" in low or ("a50" in low and "temp" not in low and "charging" not in low):
                return "Galaxy A50 (SM-A505F / SM-A505FN)"
            elif "a516" in low or ("a51" in low and "5g" in low):
                return "Galaxy A51 5G (SM-A516B / SM-A516U)"
            elif "a515" in low or ("a51" in low and "sleep" not in low):
                return "Galaxy A51 4G (SM-A515F / SM-A515U)"

        # General Cleaning
        name = re.sub(r'\s*\([^)]*\)', '', s)
        name = re.sub(r'\s*\[[^\]]*\]', '', name)
        name = name.replace('_', ' ').replace('-', ' ')
        name = re.sub(r'\b(chimera|official|testpoint|test\s*point|edl\s*point|isp\s*pinout|pinout|ha|jum|jumper_way)\b', '', name, flags=re.IGNORECASE)

        if brand:
            b_clean = brand.lower().strip()
            while name.lower().startswith(b_clean):
                name = name[len(b_clean):].strip()

        name = re.sub(r'\b(xiaomi|samsung|oppo|vivo|realme|huawei|honor|infinix|tecno|motorola|nokia|oneplus|itel|lg|lenovo|zte)\s+\1\b', r'\1', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+', ' ', name).strip()
        return name.title() if name else os.path.splitext(filename)[0]

    def get_dedup_key(self, name, brand=""):
        low = name.lower().replace('-', ' ').replace('_', ' ')
        
        # Samsung Model Deduplication Keys
        if brand.upper() == "SAMSUNG" or "samsung" in low:
            if "a127" in low or ("a12" in low and "exynos" in low): return "samsung_a127_exynos"
            if "a125" in low or ("a12" in low and ("display" not in low and "service" not in low and "light" not in low)): return "samsung_a125_mtk"
            if "a507" in low: return "samsung_a507_a50s"
            if "a505" in low or ("a50" in low and "temp" not in low and "charging" not in low): return "samsung_a505_a50"
            if "a516" in low or ("a51" in low and "5g" in low): return "samsung_a516_5g"
            if "a515" in low or ("a51" in low and "sleep" not in low): return "samsung_a515_4g"

        k = name.lower()
        k = re.sub(r'-\d{8,12}', '', k)
        k = re.sub(r'\s*\([^)]*\)', '', k)
        k = re.sub(r'\s*\[[^\]]*\]', '', k)
        k = re.sub(r'\b(xiaomi|samsung|galaxy|oppo|vivo|realme|huawei|honor|infinix|tecno|motorola|nokia|oneplus|itel|lg|lenovo|zte)\b', '', k)
        k = re.sub(r'\b(chimera|official|testpoint|edl|isp|tp|pinout|ways|way|solution|solutions|jumper|jumpers|problem|problems|troubleshoot|fault|error|fix|fixed|schematic|line|diagram)\b', '', k)
        k = re.sub(r'[^a-z0-9]', '', k)
        return k

    def load_all_data(self):
        # 1. INITIALIZE DATA STRUCTURES
        self.data_tp = {}
        self.data_cables = []
        self.data_isp = {}
        self.data_ways = {}

        seen_tp_keys = {}
        seen_isp_keys = {}
        seen_ways_keys = {}
        seen_cables_keys = set()

        for b_name in BRAND_CONFIG.keys():
            self.data_ways[b_name] = []

        # ── 2. TRY LOADING FROM ENCRYPTED VAULT (.hmpak) FIRST ──
        try:
            from hm_vault_reader import HmVaultReader
            reader = HmVaultReader.get_instance()
            if reader and reader.entries:
                for k in reader.entries:
                    parts = k.split("/")
                    if len(parts) >= 2:
                        top_cat = parts[0].lower()
                        if top_cat == "tp" and len(parts) >= 3:
                            brand = parts[1].upper()
                            fname = parts[2]
                            cname = self.clean_name(fname, brand)
                            dkey = self.get_dedup_key(cname, brand)
                            if brand not in self.data_tp: 
                                self.data_tp[brand] = []
                                seen_tp_keys[brand] = set()
                            if dkey not in seen_tp_keys[brand]:
                                seen_tp_keys[brand].add(dkey)
                                self.data_tp[brand].append({'name': cname, 'raw_name': fname, 'path': k, 'brand': brand})
                        elif top_cat in ["isp", "isps"] and len(parts) >= 2:
                            if len(parts) == 2:
                                brand = "UNIVERSAL"
                                fname = parts[1]
                            else:
                                brand = parts[1].replace(" isp", "").replace(" ISP", "").upper()
                                fname = parts[2]
                            cname = self.clean_name(fname, brand)
                            dkey = self.get_dedup_key(cname, brand)
                            if brand not in self.data_isp: 
                                self.data_isp[brand] = []
                                seen_isp_keys[brand] = set()
                            if dkey not in seen_isp_keys[brand]:
                                seen_isp_keys[brand].add(dkey)
                                self.data_isp[brand].append({'name': cname, 'path': k, 'brand': brand})
                        elif "hardware" in top_cat or "way" in top_cat:
                            if len(parts) >= 3:
                                brand = parts[1].upper()
                                fname = parts[2]
                            else:
                                brand = "UNIVERSAL & CPU WAYS"
                                fname = parts[1]
                            cname = self.clean_name(fname, brand)
                            dkey = self.get_dedup_key(cname, brand)
                            if brand not in self.data_ways: 
                                self.data_ways[brand] = []
                                seen_ways_keys[brand] = set()
                            if dkey not in seen_ways_keys[brand]:
                                seen_ways_keys[brand].add(dkey)
                                self.data_ways[brand].append({'name': cname, 'path': k, 'brand': brand})
                        elif "cable" in top_cat:
                            fname = parts[-1]
                            cname = self.clean_name(fname)
                            dkey = self.get_dedup_key(cname)
                            if dkey not in seen_cables_keys:
                                seen_cables_keys.add(dkey)
                                self.data_cables.append({'name': cname, 'path': k})
        except Exception:
            pass

        # ── 3. FALLBACK / MERGE FROM LOCAL DISK DIRECTORIES (IF PRESENT ON DEV MACHINE) ──
        # 1. TEST POINTS
        tp_dirs = [r"E:\TestPoint\TP", r"D:\TestPoint\TP", get_resource_path("tp_data\\TP"), os.path.join(get_app_dir(), "tp_data", "TP")]
        tp_dir = next((d for d in tp_dirs if os.path.exists(d)), None)

        if tp_dir:
            for b in sorted(os.listdir(tp_dir)):
                bp = os.path.join(tp_dir, b)
                if os.path.isdir(bp) and b.lower() not in ['isp', 'modified cable', 'tools', 'hardware soltion']:
                    b_upper = b.upper()
                    if b_upper not in self.data_tp:
                        self.data_tp[b_upper] = []
                        seen_tp_keys[b_upper] = set()
                    for f in sorted(os.listdir(bp)):
                        fp = os.path.join(bp, f)
                        if os.path.isfile(fp) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                            cname = self.clean_name(f, b)
                            dkey = self.get_dedup_key(cname, b_upper)
                            if dkey not in seen_tp_keys.get(b_upper, set()):
                                if b_upper not in seen_tp_keys: seen_tp_keys[b_upper] = set()
                                seen_tp_keys[b_upper].add(dkey)
                                self.data_tp[b_upper].append({'name': cname, 'raw_name': f, 'path': fp, 'brand': b_upper})

        # 2. MODIFIED CABLES
        cable_dirs = [r"E:\TestPoint\Modified Cable", r"D:\TestPoint\Modified Cable", get_resource_path("tp_data\\Modified Cable"), os.path.join(get_app_dir(), "tp_data", "Modified Cable")]
        cable_dir = next((d for d in cable_dirs if os.path.exists(d)), None)
        if cable_dir:
            for f in sorted(os.listdir(cable_dir)):
                fp = os.path.join(cable_dir, f)
                if os.path.isfile(fp) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    cname = self.clean_name(f)
                    dkey = self.get_dedup_key(cname)
                    if dkey not in seen_cables_keys:
                        seen_cables_keys.add(dkey)
                        self.data_cables.append({'name': cname, 'path': fp})

        # 3. ISP PINOUTS
        isp_dirs = [r"E:\TestPoint\ISP", r"D:\TestPoint\ISP", get_resource_path("tp_data\\ISP"), os.path.join(get_app_dir(), "tp_data", "ISP")]
        isp_dir = next((d for d in isp_dirs if os.path.exists(d)), None)
        if isp_dir:
            for b in sorted(os.listdir(isp_dir)):
                bp = os.path.join(isp_dir, b)
                if os.path.isdir(bp):
                    cat = b.replace(" ISP", "").upper()
                    if cat not in self.data_isp:
                        self.data_isp[cat] = []
                        seen_isp_keys[cat] = set()
                    for f in sorted(os.listdir(bp)):
                        fp = os.path.join(bp, f)
                        if os.path.isfile(fp) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                            disp = self.clean_name(f, cat)
                            dkey = self.get_dedup_key(disp, cat)
                            if dkey not in seen_isp_keys.get(cat, set()):
                                if cat not in seen_isp_keys: seen_isp_keys[cat] = set()
                                seen_isp_keys[cat].add(dkey)
                                self.data_isp[cat].append({'name': disp, 'path': fp, 'brand': cat})

        # 4. HARDWARE WAYS / SOLUTIONS (BRAND-WISE TREE HIERARCHY)
        hw_dirs = [r"E:\TestPoint\Hardware Soltion", r"D:\TestPoint\Hardware Soltion", r"E:\TestPoint\Hardware Ways", get_resource_path("tp_data\\Hardware Soltion")]
        hw_dir = next((d for d in hw_dirs if os.path.exists(d)), None)

        if hw_dir and os.path.exists(hw_dir):
            for item in sorted(os.listdir(hw_dir)):
                ipath = os.path.join(hw_dir, item)
                if os.path.isdir(ipath):
                    b_upper = item.upper()
                    if b_upper not in self.data_ways:
                        self.data_ways[b_upper] = []
                        seen_ways_keys[b_upper] = set()
                    for f in sorted(os.listdir(ipath)):
                        fp = os.path.join(ipath, f)
                        if os.path.isfile(fp) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                            disp = self.clean_name(f, b_upper)
                            dkey = self.get_dedup_key(disp, b_upper)
                            if dkey not in seen_ways_keys.get(b_upper, set()):
                                if b_upper not in seen_ways_keys: seen_ways_keys[b_upper] = set()
                                seen_ways_keys[b_upper].add(dkey)
                                self.data_ways[b_upper].append({'name': disp, 'path': fp, 'brand': b_upper})
                elif os.path.isfile(ipath) and item.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    target_brand = 'UNIVERSAL & CPU WAYS'
                    ilow = item.lower()
                    for b_candidate in BRAND_CONFIG.keys():
                        if b_candidate.lower() in ilow:
                            target_brand = b_candidate
                            break
                    disp = self.clean_name(item, target_brand)
                    dkey = self.get_dedup_key(disp, target_brand)
                    if dkey not in seen_ways_keys.get(target_brand, set()):
                        if target_brand not in seen_ways_keys: seen_ways_keys[target_brand] = set()
                        seen_ways_keys[target_brand].add(dkey)
                        self.data_ways[target_brand].append({'name': disp, 'path': ipath, 'brand': target_brand})

        bundled_tp_data = get_resource_path("tp_data")
        if os.path.exists(bundled_tp_data):
            for f in os.listdir(bundled_tp_data):
                fp = os.path.join(bundled_tp_data, f)
                if os.path.isfile(fp) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                    fn = f.lower()
                    if 'ways' in fn or 'issue' in fn or 'schematic' in fn or 'jumper' in fn:
                        disp = os.path.splitext(f)[0]
                        target_brand = 'OPPO' if 'oppo' in fn else ('SAMSUNG' if ('samsung' in fn or 'j6' in fn) else 'UNIVERSAL & CPU WAYS')
                        if not any(x['name'] == disp for x in self.data_ways[target_brand]):
                            self.data_ways[target_brand].append({'name': disp, 'path': fp, 'brand': target_brand})

        # 5. EMMC & UFS STORAGE IC DATABASE (5,350+ Chips)
        self.data_ic = []
        ic_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "emmc_ufs_database.json"),
            os.path.join(get_app_dir(), "emmc_ufs_database.json"),
            get_resource_path("emmc_ufs_database.json"),
            r"E:\HM TESTED TOOL\HM Testpoint\HM_Testpoint\runtime\emmc_ufs_database.json"
        ]
        for ip in ic_paths:
            if os.path.exists(ip):
                try:
                    with open(ip, 'r', encoding='utf-8-sig') as f:
                        self.data_ic = json.load(f)
                    if self.data_ic:
                        break
                except Exception:
                    pass

        # Load Facebook Logo PhotoImages
        self.fb_photo_18 = None
        self.fb_photo_22 = None
        try:
            for d in [os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), os.path.join(get_app_dir(), "assets"), r"C:\HM_Toolkits\assets"]:
                p18 = os.path.join(d, "fb_icon_18.png")
                if os.path.exists(p18) and not self.fb_photo_18:
                    self.fb_photo_18 = ImageTk.PhotoImage(Image.open(p18))
                p22 = os.path.join(d, "fb_icon_22.png")
                if os.path.exists(p22) and not self.fb_photo_22:
                    self.fb_photo_22 = ImageTk.PhotoImage(Image.open(p22))
        except Exception:
            pass

    def build_gui(self):
        self.build_top_header()
        self.build_two_row_brand_grid()
        self.build_action_tabs_strip()
        self.build_workspace()
        self.build_statusbar()
        self.root.after(1000, self.start_cloud_notification_thread)

    def build_top_header(self):
        hdr = tk.Frame(self.root, bg=UT_STYLE['bg_header'], height=45)
        hdr.pack(fill=tk.X, side=tk.TOP)
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=UT_STYLE['bg_header'])
        left.pack(side=tk.LEFT, fill=tk.Y, padx=15)

        tk.Label(left, text="⚡ HM TESTPOINT", font=("Segoe UI", 12, "bold"), fg=UT_STYLE['accent_orange'], bg=UT_STYLE['bg_header']).pack(side=tk.LEFT)
        tk.Label(left, text=" | HARDWARE GSM TOOL v8.5", font=("Segoe UI", 11, "bold"), fg=UT_STYLE['text_white'], bg=UT_STYLE['bg_header']).pack(side=tk.LEFT, padx=(4, 0))

        right = tk.Frame(hdr, bg=UT_STYLE['bg_header'])
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=15)
        tk.Label(right, text="👤 Hassan Javed (0344-1545807)", font=("Segoe UI", 9, "bold"), fg=UT_STYLE['accent_green'], bg=UT_STYLE['bg_header']).pack(side=tk.LEFT, padx=8)

        if self.fb_photo_18:
            btn_fb = tk.Button(
                right, image=self.fb_photo_18, text=" Facebook Group", compound=tk.LEFT,
                font=("Segoe UI", 9, "bold"), bg="#1877f2", fg="#ffffff",
                activebackground="#166fe5", activeforeground="#ffffff",
                bd=0, padx=8, pady=2, cursor="hand2",
                command=self.open_facebook_group
            )
        else:
            btn_fb = tk.Button(
                right, text="🌐 Facebook Group", font=("Segoe UI", 9, "bold"),
                bg="#1877f2", fg="#ffffff", activebackground="#166fe5", activeforeground="#ffffff",
                bd=0, padx=8, pady=2, cursor="hand2",
                command=self.open_facebook_group
            )
        btn_fb.pack(side=tk.LEFT, padx=4)

        btn_notice = tk.Button(
            right, text="🔔 VIP Notice", font=("Segoe UI", 9, "bold"),
            bg="#f57f17", fg="#000000", activebackground="#ffb300", activeforeground="#000000",
            bd=0, padx=8, pady=2, cursor="hand2",
            command=self.open_notification_modal_manual
        )
        btn_notice.pack(side=tk.LEFT, padx=4)

        btn_adb = tk.Button(
            right, text="⚡ Secret ADB Codes", font=("Segoe UI", 9, "bold"),
            bg="#b71c1c", fg="#ffffff", activebackground="#e53935", activeforeground="#ffffff",
            bd=0, padx=10, pady=2, cursor="hand2",
            command=self.open_adb_codes_modal
        )
        btn_adb.pack(side=tk.LEFT, padx=4)

        btn_hw_lab = tk.Button(
            right, text="🔬 Hardware Lab", font=("Segoe UI", 9, "bold"),
            bg="#d32f2f", fg="#ffffff", activebackground="#f44336", activeforeground="#ffffff",
            bd=0, padx=10, pady=2, cursor="hand2",
            command=self.launch_hardware_lab
        )
        btn_hw_lab.pack(side=tk.LEFT, padx=4)

        btn_update = tk.Button(
            right, text="🔄 VIP Cloud Sync / Update", font=("Segoe UI", 9, "bold"),
            bg="#00c853", fg="#000000", activebackground="#00e676", activeforeground="#000000",
            bd=0, padx=10, pady=2, cursor="hand2",
            command=self.launch_cloud_updater
        )
        btn_update.pack(side=tk.LEFT, padx=4)

        btn_sc = tk.Button(right, text="📌 Desktop Shortcut", font=("Segoe UI", 8, "bold"), bg="#303548", fg=UT_STYLE['accent_yellow'], bd=0, padx=8, pady=2, cursor="hand2", command=self.manual_create_shortcut)
        btn_sc.pack(side=tk.LEFT, padx=4)

    def open_facebook_group(self):
        try:
            webbrowser.open("https://www.facebook.com/share/g/19cb2CGd2a/")
        except Exception:
            pass

    def open_adb_codes_modal(self):
        top = tk.Toplevel(self.root)
        top.title("⚡ Official Secret ADB Enabler Dialer Codes - All Brands")
        top.geometry("820x640")
        top.configure(bg="#0b0c14")
        top.transient(self.root)

        hdr = tk.Frame(top, bg="#131622", bd=1, relief=tk.SOLID)
        hdr.pack(fill=tk.X, padx=14, pady=(12, 8))
        tk.Label(hdr, text="⚡ ALL-BRAND SECRET ADB ENABLER DIALER CODES", font=("Segoe UI", 13, "bold"), fg="#00e5ff", bg="#131622").pack(pady=(8, 2))
        tk.Label(hdr, text="Official Master Technician Guide • 1-Click Copy • 100% Tested", font=("Segoe UI", 9, "bold"), fg="#ffb300", bg="#131622").pack(pady=(0, 8))

        # Scrollable container
        canvas = tk.Canvas(top, bg="#0b0c14", bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0b0c14")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=780)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0), pady=6)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 14), pady=6)

        adb_list = [
            ("HUAWEI", "*#*#2846579#*#*", "Project Menu -> Background Settings -> USB Port -> Manufacture Mode", "#00e5ff"),
            ("XIAOMI / REDMI", "*#*#6484#*#*", "CIT Menu -> Tap 5 Times on Kernel Version -> Enable ADB", "#ff9800"),
            ("VIVO / IQOO", "*#*#225#*#*", "Engineering Mode -> Port Switch -> Enable ADB Debugging Port", "#2196f3"),
            ("OPPO / REALME", "*#899#", "Engineer Mode -> Manual Test -> Device Debugging -> USB Port Switch", "#4caf50"),
            ("INFINIX", "*#*#49#*#*", "Factory Diagnostic Mode -> USB Config -> Enable Debug Port", "#00e676"),
            ("TECNO", "*#*#49#*#*", "Factory Test Mode -> Port Switch -> Enable Full ADB Diag", "#00e676"),
            ("ALCATEL", "*#2886#", "MMI Test Menu -> Auto ADB Diagnostic Mode Activation", "#ab47bc"),
            ("LENOVO / MOTO", "*#*#4636#*#*", "Testing / Diagnostics Menu -> Phone Info -> Enable ADB Debug", "#26c6da"),
            ("SONY XPERIA", "*#*#737378423#*#*", "Service Menu -> Service Info -> Configuration -> Debug Enable", "#ec407a"),
            ("MOTOROLA", "*#*#2486#*#*", "CQA / BP Tools Diagnostic Menu -> Enable Full USB Debug", "#ff5722"),
            ("HONOR", "*#*#2345#*#*", "Honor Project Menu -> Background Settings -> Port Configuration", "#00bcd4"),
            ("ONEPLUS", "*#*#2346579#*#*", "Engineering Mode -> Full Port Switch / Diag USB Debug Mode", "#f44336")
        ]

        def copy_code(c, b):
            self.root.clipboard_clear()
            self.root.clipboard_append(c)
            messagebox.showinfo("Copied", f"Secret Code for {b} copied:\n{c}", parent=top)

        for b_name, b_code, b_steps, b_col in adb_list:
            card = tk.Frame(scrollable_frame, bg="#111420", bd=1, relief=tk.SOLID)
            card.pack(fill=tk.X, pady=4, padx=4)

            # Left accent
            bar = tk.Frame(card, bg=b_col, width=6)
            bar.pack(side=tk.LEFT, fill=tk.Y)

            body = tk.Frame(card, bg="#111420", padx=10, pady=6)
            body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            top_r = tk.Frame(body, bg="#111420")
            top_r.pack(fill=tk.X)
            tk.Label(top_r, text=b_name, font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#111420").pack(side=tk.LEFT)
            tk.Label(top_r, text=b_code, font=("Consolas", 12, "bold"), fg="#00ff66", bg="#06080e", padx=8, pady=2, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=12)

            btn_cp = tk.Button(top_r, text="📋 Copy Code", font=("Segoe UI", 8, "bold"), bg="#252a3d", fg="#ffb300", bd=0, padx=8, pady=2, cursor="hand2", command=lambda c=b_code, b=b_name: copy_code(c, b))
            btn_cp.pack(side=tk.RIGHT)

            tk.Label(body, text=f"Instructions: {b_steps}", font=("Segoe UI", 8), fg="#94a3b8", bg="#111420", anchor="w", justify=tk.LEFT).pack(fill=tk.X, pady=(4, 0))

    def launch_cloud_updater(self):
        updater_paths = [
            os.path.join(get_app_dir(), 'HM_Cloud_Updater.exe'),
            os.path.join(os.path.dirname(get_app_dir()), 'HM_Cloud_Updater.exe'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HM_Cloud_Updater.exe'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'HM_Cloud_Updater.exe'),
            r"E:\HM TESTED TOOL\HM_Cloud_Suite\HM_Cloud_Updater.exe",
            r"E:\HM TESTED TOOL\HM Testpoint\HM_Testpoint\HM_Cloud_Updater.exe"
        ]
        for p in updater_paths:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p])
                    return
                except Exception:
                    pass
        messagebox.showinfo("Cloud Sync", "HM Cloud Sync is active and ready in standalone mode.", parent=self.root)

    def launch_hardware_lab(self):
        lab_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HM_Hardware_Diagnostic_Lab.exe'),
            os.path.join(get_app_dir(), 'HM_Hardware_Diagnostic_Lab.exe'),
            os.path.join(os.path.dirname(get_app_dir()), 'HM_Hardware_Diagnostic_Lab.exe'),
            r"C:\Users\HM MOBILE\AppData\Local\HM_Testpoint_Tool_v8.5\runtime\HM_Hardware_Diagnostic_Lab.exe",
            r"C:\HM_Toolkits\HM_Hardware_Diagnostic_Lab.exe",
            r"C:\Users\HM MOBILE\Desktop\HM Hardware Pro NextGen Demo.exe"
        ]
        for p in lab_paths:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p])
                    return
                except Exception as ex:
                    messagebox.showerror("Hardware Lab", f"Error launching Hardware Lab:\n{ex}", parent=self.root)
                    return

        # Auto-download from VIP Cloud CDN if missing on client
        target_download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HM_Hardware_Diagnostic_Lab.exe')
        ask = messagebox.askyesno(
            "Download Hardware Lab",
            "HM Hardware Diagnostic Lab is available on the VIP Cloud CDN.\n\nWould you like to auto-download and install it now (74 KB)?",
            parent=self.root
        )
        if ask:
            self.download_hardware_lab_binary(target_download_path)

    def download_hardware_lab_binary(self, dest_path):
        top = tk.Toplevel(self.root)
        top.title("HM Cloud CDN - Downloading Hardware Lab")
        top.geometry("450x170")
        top.configure(bg="#0d1117")
        top.transient(self.root)
        top.grab_set()

        tk.Label(top, text="⚡ VIP CLOUD CDN • FAST DOWNLOAD", font=("Segoe UI", 10, "bold"), fg="#00e5ff", bg="#0d1117").pack(pady=(16, 4))
        lbl_status = tk.Label(top, text="Connecting to VIP GitHub Cloud CDN (74 KB)...", font=("Segoe UI", 9), fg="#e2e8f0", bg="#0d1117")
        lbl_status.pack(pady=4)

        prg = ttk.Progressbar(top, mode="indeterminate", length=360)
        prg.pack(pady=8)
        prg.start(10)

        def do_download():
            cdn_url = "https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/runtime/HM_Hardware_Diagnostic_Lab.exe"
            try:
                req = urllib.request.Request(cdn_url, headers={'User-Agent': 'Mozilla/5.0 HM-Client'})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    raw_data = resp.read()
                with open(dest_path, "wb") as f:
                    f.write(raw_data)

                self.root.after(0, top.destroy)
                subprocess.Popen([dest_path])
            except Exception as e:
                self.root.after(0, lambda: lbl_status.config(text=f"Download failed: {e}", fg="#f87171"))
                self.root.after(0, prg.stop)

        threading.Thread(target=do_download, daemon=True).start()

    # ═══════════════════════════════════════════════════════════════════════
    # 🔔 VIP CLOUD NOTIFICATION & UPDATE BROADCAST SYSTEM
    # ═══════════════════════════════════════════════════════════════════════

    def start_cloud_notification_thread(self):
        t = threading.Thread(target=self._fetch_cloud_notification_worker, daemon=True)
        t.start()

    def _fetch_cloud_notification_worker(self):
        notice_url = "https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/data/notification.json?t=" + str(int(time.time()))
        notice_data = None
        try:
            req = urllib.request.Request(notice_url, headers={'User-Agent': 'Mozilla/5.0 HM-Client'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    notice_data = json.loads(resp.read().decode('utf-8'))
        except Exception:
            pass

        if not notice_data:
            notice_data = {
                "version": "8.6.0",
                "id": "notice_hw_lab_v8.6",
                "title_ur": "نیا وی آئی پی فیچر: ہارڈویئر ڈائیگنوسٹک لیب لائیو!",
                "title_en": "NEW VIP FEATURE: Hardware Diagnostic Lab Live (v8.6)!",
                "message_ur": "تمام معزز کلائنٹس کے لیے ہارڈویئر ڈائیگنوسٹک لیب (SUGON 3010PM / ملٹی میٹر / 6-پورٹ اسمارٹ فاسٹ چارجر) ٹول میں شامل کر دی گئی ہے۔",
                "message_en": "HM Hardware Master Diagnostic Lab (SUGON 3010PM, UNI-T Multimeter, USB Doctor 6-Port Smart Fast Charger) is now live directly in your HM Testpoint Tool with full Urdu & English guides!",
                "force_notice": False
            }

        state_file = os.path.join(get_app_dir(), ".last_notice_seen")
        notice_id = notice_data.get("id", notice_data.get("version", "8.6.0"))
        if os.path.exists(state_file) and not notice_data.get("force_notice", False):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    if f.read().strip() == notice_id:
                        return
            except Exception:
                pass

        self.root.after(0, lambda: self.show_cloud_notification_modal(notice_data, state_file, notice_id))

    def open_notification_modal_manual(self):
        notice_data = {
            "version": "8.6.0",
            "id": "notice_hw_lab_v8.6",
            "title_ur": "نیا وی آئی پی فیچر: ہارڈویئر ڈائیگنوسٹک لیب لائیو!",
            "title_en": "NEW VIP FEATURE: Hardware Diagnostic Lab Live (v8.6)!",
            "message_ur": "تمام معزز کلائنٹس کے لیے ہارڈویئر ڈائیگنوسٹک لیب (SUGON 3010PM / ملٹی میٹر / 6-پورٹ اسمارٹ فاسٹ چارجر) ٹول میں شامل کر دی گئی ہے۔",
            "message_en": "HM Hardware Master Diagnostic Lab (SUGON 3010PM, UNI-T Multimeter, USB Doctor 6-Port Smart Fast Charger) is now live directly in your HM Testpoint Tool with full Urdu & English guides!",
            "force_notice": True
        }
        state_file = os.path.join(get_app_dir(), ".last_notice_seen")
        self.show_cloud_notification_modal(notice_data, state_file, "manual_open")

    def show_cloud_notification_modal(self, notice, state_file=None, notice_id=None):
        top = tk.Toplevel(self.root)
        top.title("🔔 HM VIP Cloud Broadcast & Update Notification")
        top.geometry("720x550")
        top.configure(bg="#0b0d18")
        top.transient(self.root)
        top.grab_set()

        # Header bar
        hdr = tk.Frame(top, bg="#111526", bd=1, relief=tk.SOLID)
        hdr.pack(fill=tk.X, padx=14, pady=(12, 8))

        h_inner = tk.Frame(hdr, bg="#111526", padx=12, pady=10)
        h_inner.pack(fill=tk.X)

        tk.Label(h_inner, text="👑 OFFICIAL VIP CLOUD BROADCAST", font=("Segoe UI", 9, "bold"), bg="#b71c1c", fg="#ffffff", padx=8, pady=2).pack(anchor="w")
        tk.Label(h_inner, text=notice.get("title_en", "🎉 NEW VIP UPDATE RELEASED (v8.6)"), font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#111526").pack(anchor="w", pady=(6, 2))
        tk.Label(h_inner, text=notice.get("title_ur", "نیا وی آئی پی فیچر: ہارڈویئر ڈائیگنوسٹک لیب لائیو!"), font=("Segoe UI", 11, "bold"), fg="#ffd54f", bg="#111526").pack(anchor="w")

        # Urdu Notice Card
        u_card = tk.Frame(top, bg="#14192b", bd=1, relief=tk.SOLID)
        u_card.pack(fill=tk.X, padx=14, pady=4)
        tk.Label(u_card, text="🇵🇰 اردو نوٹیفکیشن برائے کلائنٹس:", font=("Segoe UI", 9, "bold"), fg="#00e676", bg="#14192b").pack(anchor="e", padx=12, pady=(6, 2))
        tk.Label(u_card, text=notice.get("message_ur", ""), font=("Segoe UI", 9), fg="#f1f5f9", bg="#14192b", justify=tk.RIGHT, wraplength=660).pack(anchor="e", padx=12, pady=(0, 8))

        # English Notice Card
        e_card = tk.Frame(top, bg="#14192b", bd=1, relief=tk.SOLID)
        e_card.pack(fill=tk.X, padx=14, pady=4)
        tk.Label(e_card, text="🇬🇧 English Notification for Technicians:", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#14192b").pack(anchor="w", padx=12, pady=(6, 2))
        tk.Label(e_card, text=notice.get("message_en", ""), font=("Segoe UI", 9), fg="#cbd5e1", bg="#14192b", justify=tk.LEFT, wraplength=660).pack(anchor="w", padx=12, pady=(0, 8))

        # Features grid
        f_box = tk.Frame(top, bg="#0b0d18")
        f_box.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)

        feats = [
            ("⚡ SUGON 3010PM DC SUPPLY", "8 Real live fault states with Urdu cause/solution"),
            ("📟 DIGITAL MULTIMETER PRO", "Diode testing (~0.450V), VPH rails & buzzer"),
            ("🔌 USB DOCTOR & SMART CHARGER", "6-Port live ammeter, QC 3.0 & fake charging detection"),
            ("🛠️ 4-STAGE REPAIR WIZARD", "Dead phone, water damage & loop restart solver")
        ]
        for idx, (f_title, f_sub) in enumerate(feats):
            r = idx // 2
            c = idx % 2
            fb = tk.Frame(f_box, bg="#12162a", bd=1, relief=tk.SOLID)
            fb.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            f_box.grid_columnconfigure(c, weight=1)
            tk.Label(fb, text=f_title, font=("Segoe UI", 8, "bold"), fg="#ffd54f", bg="#12162a").pack(anchor="w", padx=8, pady=(6, 2))
            tk.Label(fb, text=f_sub, font=("Segoe UI", 8), fg="#94a3b8", bg="#12162a").pack(anchor="w", padx=8, pady=(0, 6))

        # Bottom buttons
        b_box = tk.Frame(top, bg="#0b0d18")
        b_box.pack(fill=tk.X, padx=14, pady=(6, 14))

        def close_and_dismiss():
            if state_file and notice_id and notice_id != "manual_open":
                try:
                    with open(state_file, "w", encoding="utf-8") as f:
                        f.write(notice_id)
                except Exception:
                    pass
            top.destroy()

        def open_lab_action():
            close_and_dismiss()
            self.launch_hardware_lab()

        def view_tab_action():
            close_and_dismiss()
            self.select_category('HW_DIAG')

        btn_launch = tk.Button(b_box, text="🚀 OPEN HARDWARE LAB NOW", font=("Segoe UI", 9, "bold"), bg="#b71c1c", fg="#ffffff", activebackground="#e53935", activeforeground="#ffffff", bd=0, padx=14, pady=8, cursor="hand2", command=open_lab_action)
        btn_launch.pack(side=tk.LEFT, padx=(0, 6))

        btn_tab = tk.Button(b_box, text="🔬 VIEW IN TOOL (TAB)", font=("Segoe UI", 9, "bold"), bg="#0288d1", fg="#ffffff", activebackground="#03a9f4", activeforeground="#ffffff", bd=0, padx=14, pady=8, cursor="hand2", command=view_tab_action)
        btn_tab.pack(side=tk.LEFT, padx=6)

        if self.fb_photo_22:
            btn_fb_notice = tk.Button(b_box, image=self.fb_photo_22, text=" JOIN FB GROUP", compound=tk.LEFT, font=("Segoe UI", 9, "bold"), bg="#1877f2", fg="#ffffff", activebackground="#166fe5", activeforeground="#ffffff", bd=0, padx=12, pady=6, cursor="hand2", command=self.open_facebook_group)
        else:
            btn_fb_notice = tk.Button(b_box, text="🌐 JOIN FB GROUP", font=("Segoe UI", 9, "bold"), bg="#1877f2", fg="#ffffff", activebackground="#166fe5", activeforeground="#ffffff", bd=0, padx=12, pady=8, cursor="hand2", command=self.open_facebook_group)
        btn_fb_notice.pack(side=tk.LEFT, padx=6)

        btn_close = tk.Button(b_box, text="✖ Got It / Close", font=("Segoe UI", 9, "bold"), bg="#252736", fg="#94a3b8", activebackground="#383d52", activeforeground="#ffffff", bd=0, padx=14, pady=8, cursor="hand2", command=close_and_dismiss)
        btn_close.pack(side=tk.RIGHT)

    def manual_create_shortcut(self):
        auto_create_desktop_shortcut()
        messagebox.showinfo("Desktop Shortcut", "Desktop shortcut created successfully!", parent=self.root)

    def build_two_row_brand_grid(self):
        strip = tk.Frame(self.root, bg=UT_STYLE['bg_tiles_strip'], height=80)
        strip.pack(fill=tk.X, padx=2, pady=(0, 2))
        strip.pack_propagate(False)

        grid = tk.Frame(strip, bg=UT_STYLE['bg_tiles_strip'])
        grid.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        brands_list = [
            'XIAOMI', 'SAMSUNG', 'HUAWEI', 'OPPO', 'VIVO', 'REALME', 'HONOR', 'ONEPLUS', 'MOTOROLA', 'NOKIA',
            'LG', 'LENOVO', 'ASUS', 'ZTE', 'INFINIX', 'TECNO', 'ITEL', 'VSMART', 'MEIZU', 'SMARTISAN'
        ]

        for col in range(10):
            grid.grid_columnconfigure(col, weight=1, uniform="brand_col")
        grid.grid_rowconfigure(0, weight=1, uniform="brand_row")
        grid.grid_rowconfigure(1, weight=1, uniform="brand_row")

        self.brand_buttons = {}

        for idx, brand in enumerate(brands_list):
            row = 0 if idx < 10 else 1
            col = idx if idx < 10 else (idx - 10)

            cfg = BRAND_CONFIG.get(brand, {'bg': '#333333', 'fg': '#ffffff'})
            tp_count = len(self.data_tp.get(brand, []))

            txt = f"{brand}\n({tp_count})"

            btn = tk.Button(
                grid, text=txt, font=("Segoe UI", 8, "bold"),
                bg=cfg['bg'], fg=cfg['fg'], activebackground=cfg['bg'], activeforeground=cfg['fg'],
                bd=1, relief=tk.RAISED, cursor="hand2",
                command=lambda b=brand: self.select_brand(b)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
            self.brand_buttons[brand] = btn

    def build_action_tabs_strip(self):
        sub_strip = tk.Frame(self.root, bg=UT_STYLE['bg_sub_bar'], height=38)
        sub_strip.pack(fill=tk.X, pady=(2, 4))
        sub_strip.pack_propagate(False)

        inner = tk.Frame(sub_strip, bg=UT_STYLE['bg_sub_bar'])
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=2)

        tp_count = sum(len(v) for v in self.data_tp.values())
        cable_count = len(self.data_cables)
        isp_count = sum(len(v) for v in self.data_isp.values())
        ways_count = sum(len(v) for v in self.data_ways.values())
        ic_count = len(self.data_ic)

        categories = [
            ('TESTPOINT', f"⚡ TEST POINTS ({tp_count})"),
            ('CABLES', f"🔌 MODIFIED CABLES ({cable_count})"),
            ('ISP', f"💾 ISP PINOUTS ({isp_count})"),
            ('WAYS', f"🛠 HARDWARE WAYS ({ways_count})"),
            ('EMMC_UFS', f"🎛️ HM Finder (5,350+) ({ic_count:,})"),
            ('HW_DIAG', "🔬 HARDWARE LAB (SUGON / Multimeter)")
        ]

        self.cat_buttons = {}
        for key, label in categories:
            is_active = (self.active_category == key)
            bg = UT_STYLE['accent_blue'] if is_active else UT_STYLE['bg_card']
            fg = UT_STYLE['text_white'] if is_active else UT_STYLE['text_light']

            btn = tk.Button(
                inner, text=label, font=("Segoe UI", 9, "bold"),
                bg=bg, fg=fg, activebackground=UT_STYLE['accent_blue'], activeforeground=UT_STYLE['text_white'],
                bd=0, relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
                command=lambda k=key: self.select_category(k)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.cat_buttons[key] = btn

        # Right side: CLOUD AUTO-SYNC / UPDATES BUTTON
        btn_sync_tab = tk.Button(
            inner, text="🔄 CLOUD AUTO-SYNC / UPDATES", font=("Segoe UI", 9, "bold"),
            bg="#00c853", fg="#000000", activebackground="#00e676", activeforeground="#000000",
            bd=0, relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
            command=self.launch_cloud_updater
        )
        btn_sync_tab.pack(side=tk.RIGHT, padx=4)

        if self.fb_photo_18:
            btn_fb_tab = tk.Button(
                inner, image=self.fb_photo_18, text=" OFFICIAL FB GROUP", compound=tk.LEFT,
                font=("Segoe UI", 9, "bold"), bg="#1877f2", fg="#ffffff",
                activebackground="#166fe5", activeforeground="#ffffff",
                bd=0, relief=tk.FLAT, padx=12, pady=3, cursor="hand2",
                command=self.open_facebook_group
            )
        else:
            btn_fb_tab = tk.Button(
                inner, text="🌐 OFFICIAL FB GROUP", font=("Segoe UI", 9, "bold"),
                bg="#1877f2", fg="#ffffff", activebackground="#166fe5", activeforeground="#ffffff",
                bd=0, relief=tk.FLAT, padx=12, pady=4, cursor="hand2",
                command=self.open_facebook_group
            )
        btn_fb_tab.pack(side=tk.RIGHT, padx=4)

    def build_workspace(self):
        ws = tk.Frame(self.root, bg=UT_STYLE['bg_window'])
        ws.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 4))

        # SIDEBAR (LEFT)
        self.sidebar = tk.Frame(ws, bg=UT_STYLE['bg_sidebar'], width=330, bd=1, relief=tk.SOLID)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        self.sidebar.pack_propagate(False)

        # Search Bar
        search_box = tk.Frame(self.sidebar, bg=UT_STYLE['bg_input'], bd=1, relief=tk.SOLID)
        search_box.pack(fill=tk.X, padx=6, pady=6)

        tk.Label(search_box, text="🔍", font=("Segoe UI", 9), fg=UT_STYLE['accent_orange'], bg=UT_STYLE['bg_input']).pack(side=tk.LEFT, padx=(6, 2))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        
        self.search_ent = tk.Entry(search_box, textvariable=self.search_var, font=("Segoe UI", 9), bg=UT_STYLE['bg_input'], fg=UT_STYLE['text_white'], bd=0, insertbackground="#fff")
        self.search_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)

        tk.Button(search_box, text="✖", font=("Segoe UI", 8, "bold"), bg=UT_STYLE['bg_input'], fg=UT_STYLE['text_dim'], bd=0, cursor="hand2", command=lambda: self.search_var.set("")).pack(side=tk.RIGHT, padx=4)

        # Sidebar Header Label
        self.lbl_sidebar_count = tk.Label(self.sidebar, text="HARDWARE WAYS (ALL BRANDS)", font=("Segoe UI", 9, "bold"), fg=UT_STYLE['accent_yellow'], bg=UT_STYLE['bg_sidebar'], anchor="w")
        self.lbl_sidebar_count.pack(fill=tk.X, padx=8, pady=(2, 4))

        # Treeview Frame
        tree_frame = tk.Frame(self.sidebar, bg=UT_STYLE['bg_sidebar'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        # Treeview Styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
            background=UT_STYLE['bg_window'],
            foreground=UT_STYLE['text_white'],
            fieldbackground=UT_STYLE['bg_window'],
            borderwidth=0,
            font=("Segoe UI", 9),
            rowheight=24
        )
        style.map('Treeview',
            background=[('selected', UT_STYLE['accent_orange'])],
            foreground=[('selected', '#ffffff')]
        )

        scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse", yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.tree.yview)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)

        # CANVAS / IMAGE AREA (RIGHT)
        self.right_panel = tk.Frame(ws, bg=UT_STYLE['bg_canvas'], bd=1, relief=tk.SOLID)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Top Canvas Toolbar
        self.canvas_tbar = tk.Frame(self.right_panel, bg=UT_STYLE['bg_header'], height=36)
        self.canvas_tbar.pack(fill=tk.X, side=tk.TOP)
        self.canvas_tbar.pack_propagate(False)

        self.lbl_current_model = tk.Label(self.canvas_tbar, text="⚡ Select a Model or Brand to View Diagram", font=("Segoe UI", 10, "bold"), fg=UT_STYLE['accent_orange'], bg=UT_STYLE['bg_header'])
        self.lbl_current_model.pack(side=tk.LEFT, padx=12)

        t_btns = tk.Frame(self.canvas_tbar, bg=UT_STYLE['bg_header'])
        t_btns.pack(side=tk.RIGHT, padx=8)

        def add_tb(txt, cmd):
            b = tk.Button(t_btns, text=txt, font=("Segoe UI", 9), bg=UT_STYLE['bg_card'], fg=UT_STYLE['text_white'], bd=0, padx=8, pady=2, cursor="hand2", command=cmd)
            b.pack(side=tk.LEFT, padx=2)
            return b

        add_tb("🔍 +", self.zoom_in)
        add_tb("🔍 -", self.zoom_out)
        add_tb("⛶ Fit", self.fit_to_window)
        add_tb("1:1", self.reset_zoom)
        add_tb("↻ Rotate", self.rotate_image)
        add_tb("📋 Copy", self.copy_to_clipboard)
        add_tb("📁 Folder", self.open_folder)
        add_tb("👁 External", self.open_external)

        # Canvas
        self.canvas = tk.Canvas(self.right_panel, bg=UT_STYLE['bg_canvas'], bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Configure>", self.on_resize)

        # IC PANEL (FOR EMMC/UFS FINDER)
        self.ic_panel = tk.Frame(self.right_panel, bg=UT_STYLE['bg_canvas'])

        # HARDWARE LAB PANEL (FOR SUGON / MULTIMETER / USB DOCTOR)
        self.hw_lab_panel = tk.Frame(self.right_panel, bg=UT_STYLE['bg_canvas'])

    def build_statusbar(self):
        sbar = tk.Frame(self.root, bg=UT_STYLE['bg_header'], height=24)
        sbar.pack(fill=tk.X, side=tk.BOTTOM)
        sbar.pack_propagate(False)

        tp_count = sum(len(v) for v in self.data_tp.values())
        cable_count = len(self.data_cables)
        isp_count = sum(len(v) for v in self.data_isp.values())
        ways_count = sum(len(v) for v in self.data_ways.values())
        ic_count = len(self.data_ic)

        db_text = f"⚡ Database: {tp_count} Testpoints | {cable_count} Cables | {isp_count} ISP Pinouts | {ways_count} Ways | {ic_count:,} eMMC/UFS ICs | Status: VIP Lifetime Active"
        tk.Label(sbar, text=db_text, font=("Segoe UI", 8), fg="#b0b5c8", bg=UT_STYLE['bg_header']).pack(side=tk.LEFT, padx=12)

        self.lbl_zoom_info = tk.Label(sbar, text="Resolution: 0x0 | Zoom: 100% | Rotation: 0°", font=("Segoe UI", 8), fg=UT_STYLE['accent_orange'], bg=UT_STYLE['bg_header'])
        self.lbl_zoom_info.pack(side=tk.LEFT, padx=30)

        if self.fb_photo_18:
            lbl_fb_bar = tk.Label(sbar, image=self.fb_photo_18, text=" Official FB Group", compound=tk.LEFT, font=("Segoe UI", 8, "bold underline"), fg="#38bdf8", bg=UT_STYLE['bg_header'], cursor="hand2")
        else:
            lbl_fb_bar = tk.Label(sbar, text="🌐 Official FB Group", font=("Segoe UI", 8, "bold underline"), fg="#38bdf8", bg=UT_STYLE['bg_header'], cursor="hand2")
        lbl_fb_bar.pack(side=tk.RIGHT, padx=(0, 10))
        lbl_fb_bar.bind("<Button-1>", lambda e: self.open_facebook_group())

        tk.Label(sbar, text="Developed by Hassan Javed | WhatsApp: 0344-1545807", font=("Segoe UI", 8, "bold"), fg=UT_STYLE['accent_green'], bg=UT_STYLE['bg_header']).pack(side=tk.RIGHT, padx=12)

    def select_brand(self, brand_name):
        self.active_brand = brand_name
        
        for b, btn in self.brand_buttons.items():
            if b == self.active_brand:
                btn.config(relief=tk.SUNKEN, bd=3, highlightthickness=2, highlightbackground="#ffffff")
            else:
                btn.config(relief=tk.RAISED, bd=1, highlightthickness=0)

        self.search_var.set("")
        self.populate_models()
        self.focus_active_brand()

    def select_category(self, cat_key):
        self.active_category = cat_key
        
        for k, btn in self.cat_buttons.items():
            if k == self.active_category:
                btn.config(bg=UT_STYLE['accent_blue'], fg=UT_STYLE['text_white'])
            else:
                btn.config(bg=UT_STYLE['bg_card'], fg=UT_STYLE['text_light'])

        self.search_var.set("")
        if self.active_category == 'EMMC_UFS':
            self.lbl_current_model.config(text="🎛️ HM Finder Offline Repair Hub • eMMC / UFS Storage IC Database")
            self.show_gb_finder_suite()
        elif self.active_category == 'HW_DIAG':
            self.lbl_current_model.config(text="🔬 HM Hardware Diagnostic Lab • SUGON 3010PM / Multimeter / USB Doctor")
            self.show_hardware_lab_suite()
        else:
            self.hide_ic_details()
            self.populate_models()
            self.focus_active_brand()

    def populate_models(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip().lower()

        # 1. HARDWARE WAYS: FULL BRAND-WISE HIERARCHY TREE
        if self.active_category == 'WAYS':
            total_items = sum(len(v) for v in self.data_ways.values())
            self.lbl_sidebar_count.config(text=f"HARDWARE WAYS — ALL BRANDS ({total_items})")

            all_brands = list(BRAND_CONFIG.keys())
            for b in self.data_ways.keys():
                if b not in all_brands:
                    all_brands.append(b)

            first_model_to_select = None

            for b in all_brands:
                models = self.data_ways.get(b, [])
                real_models = [m for m in models if 'coming soon' not in m['name'].lower()]
                count_txt = f"{len(real_models)} Models" if real_models else "Coming Soon ⏳"

                if query:
                    matching_models = [m for m in models if query in m['name'].lower() or query in b.lower()]
                    if not matching_models:
                        continue
                    
                    b_node = self.tree.insert('', tk.END, iid=f"brand_{b}", text=f" 📁  {b} ({len(matching_models)})", open=True, values=('BRAND', b, ''))
                    for m in matching_models:
                        icon = "   ⏳  " if 'coming soon' in m['name'].lower() else "   📐  "
                        m_node = self.tree.insert(b_node, tk.END, text=f"{icon}{m['name']}", values=('MODEL', m['path'], m['name'], b))
                        if not first_model_to_select:
                            first_model_to_select = m_node
                else:
                    is_open = (b == self.active_brand)
                    b_node = self.tree.insert('', tk.END, iid=f"brand_{b}", text=f" 📁  {b} ({count_txt})", open=is_open, values=('BRAND', b, ''))

                    if models:
                        for m in models:
                            icon = "   ⏳  " if 'coming soon' in m['name'].lower() else "   📐  "
                            m_node = self.tree.insert(b_node, tk.END, text=f"{icon}{m['name']}", values=('MODEL', m['path'], m['name'], b))
                            if is_open and not first_model_to_select:
                                first_model_to_select = m_node
                    else:
                        cs_path = rf"E:\TestPoint\Hardware Soltion\{b}\{b} Hardware Ways - Coming Soon.png"
                        m_node = self.tree.insert(b_node, tk.END, text=f"   ⏳  {b} Hardware Ways - Coming Soon", values=('MODEL', cs_path, f"{b} Coming Soon", b))
                        if is_open and not first_model_to_select:
                            first_model_to_select = m_node

            if first_model_to_select:
                self.tree.selection_set(first_model_to_select)
                self.tree.see(first_model_to_select)
                self.on_tree_select(None)

        # 2. TESTPOINT TAB
        elif self.active_category == 'TESTPOINT':
            if query:
                self.lbl_sidebar_count.config(text="SEARCH RESULTS (TESTPOINTS)")
                first_node = None
                for b, m_list in self.data_tp.items():
                    matching = [m for m in m_list if query in m['name'].lower() or query in b.lower()]
                    if matching:
                        b_node = self.tree.insert('', tk.END, iid=f"tp_{b}", text=f" 📁  {b} ({len(matching)})", open=True, values=('BRAND', b, ''))
                        for m in matching:
                            m_node = self.tree.insert(b_node, tk.END, text=f"   •  {m['name']}", values=('MODEL', m['path'], m['name'], b))
                            if not first_node: first_node = m_node
                if first_node:
                    self.tree.selection_set(first_node)
                    self.tree.see(first_node)
                    self.on_tree_select(None)
            else:
                models = self.data_tp.get(self.active_brand, [])
                self.lbl_sidebar_count.config(text=f"{self.active_brand} TESTPOINTS ({len(models)})")
                first_node = None
                for m in models:
                    m_node = self.tree.insert('', tk.END, text=f"  ⚡ {m['name']}", values=('MODEL', m['path'], m['name'], self.active_brand))
                    if not first_node: first_node = m_node
                if first_node:
                    self.tree.selection_set(first_node)
                    self.tree.see(first_node)
                    self.on_tree_select(None)

        # 3. MODIFIED CABLES
        elif self.active_category == 'CABLES':
            self.lbl_sidebar_count.config(text=f"MODIFIED CABLES ({len(self.data_cables)})")
            first_node = None
            for item in self.data_cables:
                if not query or query in item['name'].lower():
                    m_node = self.tree.insert('', tk.END, text=f"  🔌 {item['name']}", values=('MODEL', item['path'], item['name'], 'CABLES'))
                    if not first_node: first_node = m_node
            if first_node:
                self.tree.selection_set(first_node)
                self.tree.see(first_node)
                self.on_tree_select(None)

        # 4. ISP PINOUTS
        elif self.active_category == 'ISP':
            total_isp = sum(len(v) for v in self.data_isp.values())
            self.lbl_sidebar_count.config(text=f"ISP PINOUTS ({total_isp})")
            first_node = None
            for cat, items in self.data_isp.items():
                matching = [m for m in items if not query or query in m['name'].lower() or query in cat.lower()]
                if matching:
                    is_open = (cat == self.active_brand or query != "")
                    b_node = self.tree.insert('', tk.END, iid=f"isp_{cat}", text=f" 💾  {cat} ISP ({len(matching)})", open=is_open, values=('BRAND', cat, ''))
                    for m in matching:
                        m_node = self.tree.insert(b_node, tk.END, text=f"   •  {m['name']}", values=('MODEL', m['path'], m['name'], cat))
                        if is_open and not first_node: first_node = m_node
            if first_node:
                self.tree.selection_set(first_node)
                self.tree.see(first_node)
                self.on_tree_select(None)

        # 5. EMMC / UFS IC FINDER (5,350+ STORAGE ICs)
        elif self.active_category == 'EMMC_UFS':
            total_ics = len(self.data_ic)
            matching = []

            for ic in self.data_ic:
                ic_num = ic.get('ic_number', '')
                mfr = ic.get('manufacturer', '')
                pkg = ic.get('package', '')
                cap = ic.get('capacity_gb', '')
                typ = ic.get('type', '')
                compat_models = ic.get('compatible_models', [])

                if query:
                    compat_str = " ".join(compat_models).lower()
                    if query not in ic_num.lower() and query not in mfr.lower() and query not in cap.lower() and query not in pkg.lower() and query not in typ.lower() and query not in compat_str:
                        continue

                matching.append(ic)

            self.lbl_sidebar_count.config(text=f"eMMC/UFS ICs ({len(matching):,} / {total_ics:,})")

            # Group by Manufacturer
            mfr_groups = {}
            for ic in matching:
                m = ic.get('manufacturer', 'Other')
                if m not in mfr_groups:
                    mfr_groups[m] = []
                mfr_groups[m].append(ic)

            first_node = None
            for mfr, ic_list in sorted(mfr_groups.items()):
                mfr_node = self.tree.insert('', tk.END, text=f" 🏢  {mfr.upper()} ({len(ic_list)})", open=True if (query or len(mfr_groups) <= 4) else False, values=('BRAND', mfr, ''))
                for ic in ic_list:
                    ic_num = ic.get('ic_number', 'Unknown')
                    cap = ic.get('capacity_gb', '')
                    pkg = ic.get('package', '')
                    typ = ic.get('type', 'eMMC')
                    disp = f"   🎛️  {ic_num}  [{cap} | {pkg}]"
                    node = self.tree.insert(mfr_node, tk.END, text=disp, values=('IC', ic.get('id', ''), ic_num, mfr))
                    if not first_node:
                        first_node = node

            if first_node:
                self.tree.selection_set(first_node)
                self.tree.see(first_node)
                self.on_tree_select(None)

    def focus_active_brand(self):
        brand_iid = f"brand_{self.active_brand}"
        if self.tree.exists(brand_iid):
            self.tree.item(brand_iid, open=True)
            self.tree.see(brand_iid)
            children = self.tree.get_children(brand_iid)
            if children:
                self.tree.selection_set(children[0])
                self.on_tree_select(None)

    def on_search(self, *args):
        self.populate_models()

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item_data = self.tree.item(sel[0])
        vals = item_data.get('values', [])
        
        if vals and len(vals) >= 2:
            itype = vals[0]
            if itype == 'IC':
                ic_id = vals[1]
                ic_rec = next((x for x in self.data_ic if x.get('id') == ic_id), None)
                if not ic_rec and len(vals) > 2:
                    ic_rec = next((x for x in self.data_ic if x.get('ic_number') == vals[2]), None)
                if ic_rec:
                    self.gb_selected_ic = ic_rec
                    if hasattr(self, 'gb_right_panel') and self.gb_right_panel.winfo_exists():
                        self.render_gb_ic_details(ic_rec)
            elif itype == 'MODEL':
                self.hide_ic_details()
                img_path = vals[1]
                name = vals[2] if len(vals) > 2 else item_data['text'].strip()
                brand = vals[3] if len(vals) > 3 else self.active_brand
                self.selected_model = {'name': name, 'path': img_path, 'brand': brand}
                self.lbl_current_model.config(text=f"⚡ {name}")
                self.load_image(img_path)
            elif itype == 'BRAND':
                brand = vals[1]
                is_open = item_data.get('open', False)
                self.tree.item(sel[0], open=not is_open)

    # ═══════════════════════════════════════════════════════════════════════
    # 🎛️ DEDICATED HM FINDER EMMC / UFS SUITE (100% FAITHFUL REPLICA & THEME)
    # ═══════════════════════════════════════════════════════════════════════

    def hide_ic_details(self):
        if hasattr(self, 'ic_panel') and self.ic_panel.winfo_ismapped():
            self.ic_panel.pack_forget()
        if hasattr(self, 'hw_lab_panel') and self.hw_lab_panel.winfo_ismapped():
            self.hw_lab_panel.pack_forget()
        if hasattr(self, 'sidebar') and not self.sidebar.winfo_ismapped():
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))
        if hasattr(self, 'canvas_tbar') and not self.canvas_tbar.winfo_ismapped():
            self.canvas_tbar.pack(fill=tk.X, side=tk.TOP)
        if hasattr(self, 'canvas') and not self.canvas.winfo_ismapped():
            self.canvas.pack(fill=tk.BOTH, expand=True)

    def show_gb_finder_suite(self):
        if hasattr(self, 'canvas') and self.canvas.winfo_ismapped():
            self.canvas.pack_forget()
        if hasattr(self, 'canvas_tbar') and self.canvas_tbar.winfo_ismapped():
            self.canvas_tbar.pack_forget()
        if hasattr(self, 'sidebar') and self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()

        self.ic_panel.pack(fill=tk.BOTH, expand=True)

        for w in self.ic_panel.winfo_children():
            w.destroy()

        self.gb_current_view = getattr(self, 'gb_current_view', 'HOME') # 'HOME', 'DB_INFO', 'ABOUT'
        self.gb_active_subtab = getattr(self, 'gb_active_subtab', 'SPECS') # 'SPECS', 'PINOUT'
        self.gb_brand_filter = getattr(self, 'gb_brand_filter', 'ALL')

        # ── 1. TOP HM FINDER NAVIGATION BAR ──
        top_nav = tk.Frame(self.ic_panel, bg="#08080a", height=46, bd=0)
        top_nav.pack(fill=tk.X, side=tk.TOP)
        top_nav.pack_propagate(False)

        # Left Logo
        n_left = tk.Frame(top_nav, bg="#08080a")
        n_left.pack(side=tk.LEFT, fill=tk.Y, padx=12)

        logo_box = tk.Frame(n_left, bg="#b71c1c", width=30, height=30, bd=1, relief=tk.SOLID)
        logo_box.pack(side=tk.LEFT, padx=(0, 8), pady=8)
        logo_box.pack_propagate(False)
        tk.Label(logo_box, text="HM", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#b71c1c").pack(expand=True)

        tk.Label(n_left, text="HM FINDER", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#08080a").pack(side=tk.LEFT)
        tk.Label(n_left, text=" v1.0.0", font=("Segoe UI", 9, "bold"), fg="#e50914", bg="#08080a").pack(side=tk.LEFT)

        # Menu links
        def set_gb_view(vname):
            self.gb_current_view = vname
            self.show_gb_finder_suite()

        n_menu = tk.Frame(top_nav, bg="#08080a")
        n_menu.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        tabs = [
            ("HOME", "🔍  HOME / SEARCH"),
            ("DB_INFO", "🗄️  DATABASE INFO"),
            ("ABOUT", "👤  ABOUT")
        ]

        for vkey, vlabel in tabs:
            is_active = (self.gb_current_view == vkey)
            btn = tk.Button(
                n_menu, text=vlabel, font=("Segoe UI", 9, "bold"),
                bg="#1a0b0d" if is_active else "#08080a",
                fg="#d4af37" if is_active else "#9ca3af",
                activebackground="#1a0b0d", activeforeground="#d4af37",
                bd=0, padx=12, pady=10, cursor="hand2",
                command=lambda k=vkey: set_gb_view(k)
            )
            btn.pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # Right Status
        n_right = tk.Frame(top_nav, bg="#08080a")
        n_right.pack(side=tk.RIGHT, fill=tk.Y, padx=14)
        tk.Label(n_right, text="🇵🇰 PAKISTAN • HM VIP PRO", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#08080a").pack(side=tk.RIGHT, pady=12)

        # Red Divider Line
        tk.Frame(self.ic_panel, bg="#4a0e17", height=1).pack(fill=tk.X)

        # ── 2. MAIN BODY AREA ──
        body_frame = tk.Frame(self.ic_panel, bg="#0a0a0c")
        body_frame.pack(fill=tk.BOTH, expand=True)

        if self.gb_current_view == 'DB_INFO':
            self.render_gb_database_info(body_frame)
        elif self.gb_current_view == 'ABOUT':
            self.render_gb_about(body_frame)
        else:
            self.render_gb_home_and_search(body_frame)

    def render_gb_home_and_search(self, parent):
        # ── LEFT SIDEBAR ──
        sb = tk.Frame(parent, bg="#0c0d12", width=320, bd=1, relief=tk.SOLID)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)

        # Header Box (Gold / Red Theme)
        h_box = tk.Frame(sb, bg="#12131a", bd=1, relief=tk.SOLID)
        h_box.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(h_box, text="🎛️ STORAGE IC FINDER", font=("Segoe UI", 10, "bold"), fg="#d4af37", bg="#12131a").pack(anchor="w", padx=10, pady=(6, 1))
        tk.Label(h_box, text="EMMC / UFS MARKING DECODER", font=("Segoe UI", 8, "bold"), fg="#ffffff", bg="#12131a").pack(anchor="w", padx=10)
        tk.Label(h_box, text="HM REPAIR STATION SUITE", font=("Segoe UI", 7, "bold"), fg="#ef4444", bg="#12131a").pack(anchor="w", padx=10, pady=(0, 6))

        # Search Bar
        s_box = tk.Frame(sb, bg="#0c0d12")
        s_box.pack(fill=tk.X, padx=8, pady=4)

        tk.Label(s_box, text="SEARCH EMMC / IC MARKING", font=("Segoe UI", 8, "bold"), fg="#ef4444", bg="#0c0d12").pack(anchor="w", pady=(0, 2))

        inp_frame = tk.Frame(s_box, bg="#161722", bd=1, relief=tk.SOLID)
        inp_frame.pack(fill=tk.X)

        tk.Label(inp_frame, text="🔍", font=("Segoe UI", 9), fg="#d4af37", bg="#161722").pack(side=tk.LEFT, padx=6)
        
        self.gb_search_var = getattr(self, 'gb_search_var', tk.StringVar())
        self.gb_search_ent = tk.Entry(
            inp_frame, textvariable=self.gb_search_var, font=("Segoe UI", 9, "bold"),
            bg="#161722", fg="#d4af37", bd=0, insertbackground="#d4af37"
        )
        self.gb_search_ent.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=4)

        def clear_gb_search():
            self.gb_search_var.set("")
            self.filter_gb_ic_list()

        tk.Button(inp_frame, text="✖", font=("Segoe UI", 8, "bold"), bg="#161722", fg="#888fa6", bd=0, cursor="hand2", command=clear_gb_search).pack(side=tk.RIGHT, padx=4)

        # Brand Filter Chips
        chips_frame = tk.Frame(sb, bg="#0c0d12")
        chips_frame.pack(fill=tk.X, padx=8, pady=3)

        brands_chips = ["ALL", "SAMSUNG", "HYNIX", "MICRON", "TOSHIBA", "FORESEE", "SANDISK", "KINGSTON"]
        self.gb_chip_buttons = {}

        def select_chip(b_name):
            self.gb_brand_filter = b_name
            for bn, bbtn in self.gb_chip_buttons.items():
                if bn == b_name:
                    bbtn.config(bg="#b71c1c", fg="#ffffff")
                else:
                    bbtn.config(bg="#1a1c29", fg="#888fa6")
            self.filter_gb_ic_list()

        chips_row1 = tk.Frame(chips_frame, bg="#0c0d12")
        chips_row1.pack(fill=tk.X, pady=1)
        chips_row2 = tk.Frame(chips_frame, bg="#0c0d12")
        chips_row2.pack(fill=tk.X, pady=1)

        for idx, bn in enumerate(brands_chips):
            target_row = chips_row1 if idx < 4 else chips_row2
            is_active = (self.gb_brand_filter == bn)
            cbtn = tk.Button(
                target_row, text=bn, font=("Segoe UI", 7, "bold"),
                bg="#b71c1c" if is_active else "#1a1c29",
                fg="#ffffff" if is_active else "#888fa6",
                activebackground="#b71c1c", activeforeground="#ffffff",
                bd=0, padx=4, pady=1, cursor="hand2",
                command=lambda name=bn: select_chip(name)
            )
            cbtn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.gb_chip_buttons[bn] = cbtn

        # Register Custom Button
        btn_reg = tk.Button(
            sb, text="+ Register Custom IC Marking", font=("Segoe UI", 8, "bold"),
            bg="#b71c1c", fg="#ffffff", activebackground="#d32f2f", activeforeground="#ffffff",
            bd=0, pady=4, cursor="hand2", command=self.open_register_ic_modal
        )
        btn_reg.pack(fill=tk.X, padx=8, pady=(4, 6))

        # Matching Records Count Header
        cnt_bar = tk.Frame(sb, bg="#0c0d12")
        cnt_bar.pack(fill=tk.X, padx=8, pady=(0, 4))
        self.lbl_gb_count = tk.Label(cnt_bar, text=f"MATCHING RECORDS ({len(self.data_ic):,})", font=("Segoe UI", 8, "bold"), fg="#888fa6", bg="#0c0d12")
        self.lbl_gb_count.pack(side=tk.LEFT)
        tk.Label(cnt_bar, text="● LOCAL OFFLINE", font=("Segoe UI", 8, "bold"), fg="#00e676", bg="#0c0d12").pack(side=tk.RIGHT)

        # Listbox Frame (High Performance Treeview Cards)
        list_frame = tk.Frame(sb, bg="#0c0d12")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        gb_scroll = ttk.Scrollbar(list_frame, orient="vertical")
        gb_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.gb_tree = ttk.Treeview(list_frame, show="tree", selectmode="browse", yscrollcommand=gb_scroll.set)
        self.gb_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        gb_scroll.config(command=self.gb_tree.yview)

        self.gb_tree.bind('<<TreeviewSelect>>', self.on_gb_tree_select)
        self.gb_search_var.trace('w', lambda *args: self.filter_gb_ic_list())

        # Profile Footer Card
        prof_card = tk.Frame(sb, bg="#12131a", bd=1, relief=tk.SOLID, height=36)
        prof_card.pack(fill=tk.X, side=tk.BOTTOM, padx=6, pady=4)
        prof_card.pack_propagate(False)
        tk.Label(prof_card, text="👤 Hassan Javed (0344-1545807)", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#12131a").pack(side=tk.LEFT, padx=8)
        tk.Label(prof_card, text="VIP PRO", font=("Segoe UI", 8, "bold"), fg="#00e676", bg="#12131a").pack(side=tk.RIGHT, padx=8)

        # ── RIGHT MAIN WORK AREA ──
        self.gb_right_panel = tk.Frame(parent, bg="#050507")
        self.gb_right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Initial Population of List
        self.filter_gb_ic_list()

        # Render Default View
        if hasattr(self, 'gb_selected_ic') and self.gb_selected_ic:
            self.render_gb_ic_details(self.gb_selected_ic)
        else:
            self.render_gb_hub_view()

    def filter_gb_ic_list(self):
        if not hasattr(self, 'gb_tree'):
            return

        for item in self.gb_tree.get_children():
            self.gb_tree.delete(item)

        q = self.gb_search_var.get().strip().lower()
        bf = getattr(self, 'gb_brand_filter', 'ALL')

        matched = []
        for ic in self.data_ic:
            mfr = ic.get('manufacturer', '')
            ic_num = ic.get('ic_number', '')
            cap = ic.get('capacity_gb', '')
            pkg = ic.get('package', '')
            typ = ic.get('type', '')
            models = ic.get('compatible_models', [])

            # Brand filter check
            if bf != 'ALL':
                if bf == 'SAMSUNG' and 'samsung' not in mfr.lower(): continue
                elif bf == 'HYNIX' and 'hynix' not in mfr.lower(): continue
                elif bf == 'MICRON' and 'micron' not in mfr.lower(): continue
                elif bf == 'TOSHIBA' and ('toshiba' not in mfr.lower() and 'kioxia' not in mfr.lower()): continue
                elif bf == 'FORESEE' and 'foresee' not in mfr.lower(): continue
                elif bf == 'SANDISK' and 'sandisk' not in mfr.lower(): continue
                elif bf == 'KINGSTON' and 'kingston' not in mfr.lower(): continue

            # Search query check
            if q:
                models_str = " ".join(models).lower()
                if q not in ic_num.lower() and q not in mfr.lower() and q not in cap.lower() and q not in pkg.lower() and q not in typ.lower() and q not in models_str:
                    continue

            matched.append(ic)

        if hasattr(self, 'lbl_gb_count'):
            self.lbl_gb_count.config(text=f"MATCHING RECORDS ({len(matched):,})")

        first_node = None
        for ic in matched:
            ic_id = ic.get('id', '')
            ic_num = ic.get('ic_number', 'N/A')
            mfr = ic.get('manufacturer', 'Samsung')
            cap = ic.get('capacity_gb', '')
            pkg = ic.get('package', '')

            # Initial Brand Tag
            tag = mfr[:3].upper() if len(mfr) >= 3 else mfr.upper()

            disp = f"[{tag}]  {ic_num}   •   {cap}"
            node = self.gb_tree.insert('', tk.END, iid=ic_id, text=disp, values=(ic_id, ic_num))
            if not first_node:
                first_node = node

    def on_gb_tree_select(self, event):
        sel = self.gb_tree.selection()
        if not sel:
            return
        ic_id = sel[0]
        ic = next((x for x in self.data_ic if x.get('id') == ic_id or x.get('ic_number') == ic_id), None)
        if ic:
            self.gb_selected_ic = ic
            self.render_gb_ic_details(ic)

    def render_gb_hub_view(self):
        for w in self.gb_right_panel.winfo_children():
            w.destroy()

        hub = tk.Frame(self.gb_right_panel, bg="#050507")
        hub.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Center Card
        c_card = tk.Frame(hub, bg="#101117", bd=1, relief=tk.SOLID)
        c_card.pack(expand=True, padx=20, pady=20)

        # Red Chip Box
        c_icon = tk.Frame(c_card, bg="#b71c1c", width=64, height=64, bd=2, relief=tk.SOLID)
        c_icon.pack(pady=(28, 12))
        c_icon.pack_propagate(False)
        tk.Label(c_icon, text="🎛️", font=("Segoe UI", 24), bg="#b71c1c", fg="#d4af37").pack(expand=True)

        tk.Label(c_card, text="HM FINDER OFFLINE REPAIR HUB", font=("Segoe UI", 16, "bold italic"), fg="#ffffff", bg="#101117").pack(pady=2, padx=24)
        tk.Label(c_card, text="MOBILE DIAGNOSTIC EMMC / UFS IC SPECIFICATION DATABASE", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#101117").pack(pady=2, padx=24)

        desc = "Enter an IC marking number in the search bar on the left to immediately decode storage chip specs, compatible motherboard assemblies, and interactive BGA pinout maps."
        tk.Label(c_card, text=desc, font=("Segoe UI", 9), fg="#9ca3af", bg="#101117", justify=tk.CENTER, wraplength=460).pack(pady=12, padx=24)

        # 3 Stats Badges
        stats = tk.Frame(c_card, bg="#101117")
        stats.pack(fill=tk.X, padx=20, pady=10)

        s_data = [
            ("DATABASE RECORDS", f"{len(self.data_ic):,} Local", "#ffffff"),
            ("FOOTPRINTS MAPPED", "BGA 153 & 221", "#d4af37"),
            ("LOCAL MARKINGS", "Persistent Offline", "#ef4444")
        ]

        for idx, (stitle, sval, scol) in enumerate(s_data):
            s_box = tk.Frame(stats, bg="#07080b", bd=1, relief=tk.SOLID)
            s_box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4, pady=2)
            tk.Label(s_box, text=stitle, font=("Segoe UI", 7, "bold"), fg="#6b7280", bg="#07080b").pack(pady=(6, 1), padx=8)
            tk.Label(s_box, text=sval, font=("Segoe UI", 10, "bold"), fg=scol, bg="#07080b").pack(pady=(0, 6), padx=8)

        # 2 Action Buttons
        btn_box = tk.Frame(c_card, bg="#101117")
        btn_box.pack(pady=(10, 24))

        tk.Button(
            btn_box, text="+ REGISTER CUSTOM MARKING", font=("Segoe UI", 8, "bold"),
            bg="#b71c1c", fg="#ffffff", activebackground="#d32f2f", activeforeground="#ffffff",
            bd=0, padx=14, pady=6, cursor="hand2", command=self.open_register_ic_modal
        ).pack(side=tk.LEFT, padx=6)

        def show_about_tab():
            self.gb_current_view = 'ABOUT'
            self.show_gb_finder_suite()

        tk.Button(
            btn_box, text="VIEW DEVELOPER INFO", font=("Segoe UI", 8, "bold"),
            bg="#252736", fg="#d4af37", activebackground="#333649", activeforeground="#ffffff",
            bd=1, relief=tk.SOLID, padx=14, pady=6, cursor="hand2", command=show_about_tab
        ).pack(side=tk.LEFT, padx=6)

    
    def show_ic_details(self, ic):
        self.render_gb_ic_details(ic)

    def render_gb_ic_details(self, ic):
        if not hasattr(self, 'gb_right_panel') or not self.gb_right_panel.winfo_exists():
            self.gb_selected_ic = ic
            self.show_gb_finder_suite()
            return

        for w in self.gb_right_panel.winfo_children():
            w.destroy()

        self.current_ic = ic
        self.gb_active_subtab = getattr(self, 'gb_active_subtab', 'SPECS')

        # ── HERO HEADER BAR ──
        hero_bar = tk.Frame(self.gb_right_panel, bg="#08080c", height=78, bd=0)
        hero_bar.pack(fill=tk.X, side=tk.TOP, padx=16, pady=(12, 4))
        hero_bar.pack_propagate(False)

        # Left Icon & Part Number
        h_left = tk.Frame(hero_bar, bg="#08080c")
        h_left.pack(side=tk.LEFT, fill=tk.Y)

        chip_box = tk.Frame(h_left, bg="#b71c1c", width=46, height=46, bd=1, relief=tk.SOLID)
        chip_box.pack(side=tk.LEFT, padx=(0, 12), pady=12)
        chip_box.pack_propagate(False)
        tk.Label(chip_box, text="🎛️", font=("Segoe UI", 18), bg="#b71c1c", fg="#d4af37").pack(expand=True)

        ic_num = ic.get('ic_number', 'N/A')
        mfr = ic.get('manufacturer', 'Samsung').upper()
        cap = ic.get('capacity_gb', 'N/A')
        typ = ic.get('type', 'eMMC').upper()
        pkg = ic.get('package', 'BGA 221').upper()
        gen = ic.get('generation', 'eMMC 5.1').upper()
        volt = ic.get('voltage', 'VCC: 2.9V-3.3V / VCCQ: 1.8V')
        models = ic.get('compatible_models', [])
        notes = ic.get('notes', 'Original Storage IC. Supports high-speed HS400 mode.')

        t_frame = tk.Frame(h_left, bg="#08080c")
        t_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        tk.Label(t_frame, text=ic_num, font=("Segoe UI", 18, "bold italic"), fg="#ffffff", bg="#08080c").pack(anchor="w")
        tk.Label(t_frame, text=f"{mfr} HIGH-PERFORMANCE {typ} • {gen}", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#08080c").pack(anchor="w")

        # Right Capacity Tag
        h_right = tk.Frame(hero_bar, bg="#08080c")
        h_right.pack(side=tk.RIGHT, fill=tk.Y, padx=12, pady=10)
        tk.Label(h_right, text=cap, font=("Segoe UI", 22, "bold"), fg="#ef4444", bg="#08080c").pack(anchor="e")
        tk.Label(h_right, text="TOTAL NAND CAPACITY", font=("Segoe UI", 8, "bold"), fg="#6b7280", bg="#08080c").pack(anchor="e")

        # ── SUB-TABS NAVIGATION STRIP ──
        nav_bar = tk.Frame(self.gb_right_panel, bg="#0f1017", height=40, bd=1, relief=tk.SOLID)
        nav_bar.pack(fill=tk.X, padx=16, pady=(0, 8))
        nav_bar.pack_propagate(False)

        def switch_gb_subtab(tab_name):
            self.gb_active_subtab = tab_name
            self.render_gb_ic_details(self.current_ic)

        is_specs = (self.gb_active_subtab == 'SPECS')
        is_pinout = (self.gb_active_subtab == 'PINOUT')

        b_specs = tk.Button(
            nav_bar, text="TECHNICAL SPECIFICATIONS", font=("Segoe UI", 9, "bold"),
            bg="#211215" if is_specs else "#0f1017",
            fg="#d4af37" if is_specs else "#9ca3af",
            activebackground="#211215", activeforeground="#d4af37",
            bd=0, padx=18, pady=6, cursor="hand2",
            command=lambda: switch_gb_subtab('SPECS')
        )
        b_specs.pack(side=tk.LEFT, fill=tk.Y, padx=2)

        b_pinout = tk.Button(
            nav_bar, text="BGA BALL PINOUT DIAGRAM", font=("Segoe UI", 9, "bold"),
            bg="#211215" if is_pinout else "#0f1017",
            fg="#d4af37" if is_pinout else "#9ca3af",
            activebackground="#211215", activeforeground="#d4af37",
            bd=0, padx=18, pady=6, cursor="hand2",
            command=lambda: switch_gb_subtab('PINOUT')
        )
        b_pinout.pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # Copy Specs Action
        def copy_specs_action():
            clip_txt = f"IC Marking: {ic_num}\nManufacturer: {mfr}\nCapacity: {cap}\nType: {typ}\nPackage: {pkg}\nGeneration: {gen}\nVoltages: {volt}\nCompatible Models: {', '.join(models)}"
            self.root.clipboard_clear()
            self.root.clipboard_append(clip_txt)
            messagebox.showinfo("Copied", "IC Specifications copied to clipboard!", parent=self.root)

        btn_copy = tk.Button(
            nav_bar, text="📋 COPY SPECIFICATIONS", font=("Segoe UI", 8, "bold"),
            bg="#1f2230", fg="#d4af37", activebackground="#2c3044", activeforeground="#ffffff",
            bd=1, relief=tk.SOLID, padx=12, pady=3, cursor="hand2", command=copy_specs_action
        )
        btn_copy.pack(side=tk.RIGHT, padx=8, pady=4)

        tk.Label(nav_bar, text=f"FOOTPRINT: {pkg}", font=("Segoe UI", 8, "bold"), fg="#ef4444", bg="#0f1017").pack(side=tk.RIGHT, padx=12)

        # ── CONTENT VIEW FRAME ──
        c_frame = tk.Frame(self.gb_right_panel, bg="#050507")
        c_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        if self.gb_active_subtab == 'PINOUT':
            self.render_gb_pinout_tab(c_frame, ic)
        else:
            self.render_gb_specs_tab(c_frame, ic)

    def render_gb_specs_tab(self, parent, ic):
        parent.columnconfigure(0, weight=1, uniform="c")
        parent.columnconfigure(1, weight=1, uniform="c")
        parent.rowconfigure(0, weight=1)

        # Left: Hardware Specs Card
        c_left = tk.Frame(parent, bg="#0f1017", bd=1, relief=tk.SOLID)
        c_left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(c_left, text="🛡️ HARDWARE SPECIFICATIONS", font=("Segoe UI", 10, "bold"), fg="#ef4444", bg="#0f1017").pack(anchor="w", padx=16, pady=(14, 10))

        specs = [
            ("Manufacturer", ic.get('manufacturer', 'Samsung')),
            ("Interface / Protocol", ic.get('generation', 'eMMC 5.1')),
            ("Package Footprint", ic.get('package', 'BGA 221')),
            ("Vcc / VccQ Voltage", ic.get('voltage', 'VCC: 2.9V-3.3V / VCCQ: 1.8V')),
            ("NAND Configuration", ic.get('type', 'eMCP')),
            ("Speed Clock Level", "HS400 / High Speed"),
            ("Technician Safe Temp", "310°C – 330°C (Air 45%)")
        ]

        for sname, sval in specs:
            row = tk.Frame(c_left, bg="#0f1017")
            row.pack(fill=tk.X, padx=16, pady=4)
            tk.Label(row, text=sname, font=("Segoe UI", 9), fg="#9ca3af", bg="#0f1017").pack(side=tk.LEFT)
            tk.Label(row, text=sval, font=("Segoe UI", 9, "bold"), fg="#d4af37" if "Interface" in sname else "#ffffff", bg="#0f1017").pack(side=tk.RIGHT)

        # Right: Compatible Motherboards Card
        c_right = tk.Frame(parent, bg="#0f1017", bd=1, relief=tk.SOLID)
        c_right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        models = ic.get('compatible_models', [])
        tk.Label(c_right, text=f"📱 KNOWN COMPATIBLE HARDWARE ({len(models)} Devices)", font=("Segoe UI", 10, "bold"), fg="#ef4444", bg="#0f1017").pack(anchor="w", padx=16, pady=(14, 10))

        if models:
            m_canvas = tk.Canvas(c_right, bg="#0f1017", bd=0, highlightthickness=0)
            m_scroll = ttk.Scrollbar(c_right, orient="vertical", command=m_canvas.yview)
            m_inner = tk.Frame(m_canvas, bg="#0f1017")

            m_inner.bind("<Configure>", lambda e: m_canvas.configure(scrollregion=m_canvas.bbox("all")))
            m_canvas.create_window((0, 0), window=m_inner, anchor="nw")
            m_canvas.configure(yscrollcommand=m_scroll.set)

            m_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
            m_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 12))

            for m in models:
                row = tk.Frame(m_inner, bg="#171822", bd=1, relief=tk.SOLID)
                row.pack(fill=tk.X, pady=3, padx=2)
                tk.Label(row, text="●", font=("Segoe UI", 10), fg="#ef4444", bg="#171822").pack(side=tk.LEFT, padx=(8, 4), pady=4)
                tk.Label(row, text=m, font=("Segoe UI", 8, "bold"), fg="#e5e7eb", bg="#171822").pack(side=tk.LEFT, pady=4)
        else:
            tk.Label(c_right, text="Pin-compatible for generic custom platform swap across identical BGA footprints.", font=("Segoe UI", 9), fg="#9ca3af", bg="#0f1017", justify=tk.LEFT, wraplength=340).pack(fill=tk.X, padx=16, pady=(0, 12))

    def render_gb_pinout_tab(self, parent, ic):
        pkg = ic.get('package', 'BGA 221').upper()

        parent.columnconfigure(0, weight=3)
        parent.columnconfigure(1, weight=2)
        parent.rowconfigure(0, weight=1)

        # Left: Canvas Box
        bga_box = tk.Frame(parent, bg="#07080b", bd=1, relief=tk.SOLID)
        bga_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(bga_box, text=f"{pkg} PINOUT BOTTOM VIEW (SOLDER BALLS)", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#07080b").pack(anchor="w", padx=16, pady=10)

        canvas = tk.Canvas(bga_box, bg="#07080b", bd=0, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Right: Legend & Pad Inspector
        side_box = tk.Frame(parent, bg="#050507")
        side_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Legend Card
        leg_card = tk.Frame(side_box, bg="#0f1017", bd=1, relief=tk.SOLID)
        leg_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(leg_card, text="⚡ COLOR REFERENCE LEGEND", font=("Segoe UI", 10, "bold"), fg="#d4af37", bg="#0f1017").pack(anchor="w", padx=14, pady=(10, 6))

        legends = [
            ("VCC (Core)", "#ef4444"),
            ("VCCQ (I/O)", "#ea580c"),
            ("CLK (Clock)", "#eab308"),
            ("CMD (Comm)", "#eab308"),
            ("DAT0-DAT7", "#10b981"),
            ("GND (Ground)", "#64748b"),
        ]

        leg_grid = tk.Frame(leg_card, bg="#0f1017")
        leg_grid.pack(fill=tk.X, padx=14, pady=(0, 10))

        for idx, (lname, lcol) in enumerate(legends):
            r = idx // 2
            c = idx % 2
            item = tk.Frame(leg_grid, bg="#0f1017")
            item.grid(row=r, column=c, sticky="w", padx=4, pady=3)
            tk.Label(item, text="●", font=("Segoe UI", 12), fg=lcol, bg="#0f1017").pack(side=tk.LEFT)
            tk.Label(item, text=f" {lname}", font=("Segoe UI", 8, "bold"), fg="#e5e7eb", bg="#0f1017").pack(side=tk.LEFT)

        # Pad Inspector Card
        info_card = tk.Frame(side_box, bg="#0f1017", bd=1, relief=tk.SOLID)
        info_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(info_card, text="🔍 BGA PAD INSPECTOR", font=("Segoe UI", 10, "bold"), fg="#ef4444", bg="#0f1017").pack(anchor="w", padx=14, pady=(12, 6))

        lbl_hover = tk.Label(info_card, text="Hover over any BGA pad to view its pin name and function details.", font=("Segoe UI", 9), fg="#9ca3af", bg="#0f1017", justify=tk.LEFT, wraplength=220)
        lbl_hover.pack(fill=tk.X, padx=14, pady=(4, 12))

        lbl_pad_name = tk.Label(info_card, text="Pin: --", font=("Segoe UI", 13, "bold"), fg="#d4af37", bg="#0f1017")
        lbl_pad_name.pack(anchor="w", padx=14, pady=2)

        lbl_pad_desc = tk.Label(info_card, text="Function: Ready for inspection", font=("Segoe UI", 9), fg="#ffffff", bg="#0f1017", wraplength=220, justify=tk.LEFT)
        lbl_pad_desc.pack(anchor="w", padx=14, pady=2)

        self.draw_exact_gb_bga_matrix(canvas, pkg, lbl_pad_name, lbl_pad_desc)

    def draw_exact_gb_bga_matrix(self, canvas, pkg, lbl_name, lbl_desc):
        canvas.delete("all")

        is_221 = ("221" in pkg)
        
        # Exact HM Finder Matrix Definitions
        if is_221:
            row_labels = ["A","B","C","D","E","F","G","H","J","K","L","M","N","P","R"]
            col_labels = list(range(1, 16))
            pins = [
                {"row":"A","col":3,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"B","col":6,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"D","col":1,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"E","col":10,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"J","col":9,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"L","col":4,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"N","col":13,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"R","col":3,"label":"GND","type":"GND","desc":"Ground pin for core and I/O."},
                {"row":"C","col":4,"label":"VCC","type":"VCC","desc":"Memory core voltage supply 2.9V - 3.3V."},
                {"row":"C","col":5,"label":"VCC","type":"VCC","desc":"Memory core voltage supply 2.9V - 3.3V."},
                {"row":"P","col":4,"label":"VCC","type":"VCC","desc":"Memory core voltage supply 2.9V - 3.3V."},
                {"row":"P","col":5,"label":"VCC","type":"VCC","desc":"Memory core voltage supply 2.9V - 3.3V."},
                {"row":"F","col":4,"label":"VCCQ","type":"VCCQ","desc":"I/O buffer voltage supply 1.8V."},
                {"row":"F","col":5,"label":"VCCQ","type":"VCCQ","desc":"I/O buffer voltage supply 1.8V."},
                {"row":"M","col":4,"label":"VCCQ","type":"VCCQ","desc":"I/O buffer voltage supply 1.8V."},
                {"row":"K","col":3,"label":"CLK","type":"CLK","desc":"Clock Input Signal."},
                {"row":"H","col":3,"label":"CMD","type":"CMD","desc":"Command / Response Line."},
                {"row":"C","col":1,"label":"RSTN","type":"CMD","desc":"Hardware Reset Line (Active Low)."},
                {"row":"G","col":3,"label":"DAT0","type":"DAT","desc":"Data Bus Line 0 (ISP Connection)"},
                {"row":"G","col":4,"label":"DAT1","type":"DAT","desc":"Data Bus Line 1"},
                {"row":"H","col":4,"label":"DAT2","type":"DAT","desc":"Data Bus Line 2"},
                {"row":"J","col":4,"label":"DAT3","type":"DAT","desc":"Data Bus Line 3"},
                {"row":"K","col":4,"label":"DAT4","type":"DAT","desc":"Data Bus Line 4"},
                {"row":"L","col":3,"label":"DAT5","type":"DAT","desc":"Data Bus Line 5"},
                {"row":"M","col":3,"label":"DAT6","type":"DAT","desc":"Data Bus Line 6"},
                {"row":"N","col":3,"label":"DAT7","type":"DAT","desc":"Data Bus Line 7"}
            ]
        else: # BGA 153
            row_labels = ["A","B","C","D","E","F","G","H","J","K","L","M","N","P"]
            col_labels = list(range(1, 15))
            pins = [
                {"row":"A","col":3,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"A","col":5,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"G","col":5,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"H","col":5,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"N","col":3,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"N","col":12,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"P","col":3,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"P","col":5,"label":"GND","type":"GND","desc":"Ground pin for memory core and I/O buffer."},
                {"row":"C","col":2,"label":"VCC","type":"VCC","desc":"Main power supply voltage 2.7V - 3.6V."},
                {"row":"C","col":3,"label":"VCC","type":"VCC","desc":"Main power supply voltage 2.7V - 3.6V."},
                {"row":"M","col":3,"label":"VCC","type":"VCC","desc":"Main power supply voltage 2.7V - 3.6V."},
                {"row":"M","col":4,"label":"VCC","type":"VCC","desc":"Main power supply voltage 2.7V - 3.6V."},
                {"row":"E","col":2,"label":"VCCQ","type":"VCCQ","desc":"Power supply voltage 1.8V."},
                {"row":"E","col":3,"label":"VCCQ","type":"VCCQ","desc":"Power supply voltage 1.8V."},
                {"row":"K","col":2,"label":"VCCQ","type":"VCCQ","desc":"Power supply voltage 1.8V."},
                {"row":"K","col":3,"label":"VCCQ","type":"VCCQ","desc":"Power supply voltage 1.8V."},
                {"row":"M","col":1,"label":"CLK","type":"CLK","desc":"Clock input pin. Synchronizes signals."},
                {"row":"H","col":1,"label":"CMD","type":"CMD","desc":"Command line for ISP programming."},
                {"row":"A","col":6,"label":"RSTN","type":"CMD","desc":"Hardware Reset pin."},
                {"row":"J","col":1,"label":"DAT0","type":"DAT","desc":"Data Line 0 (ISP Connection)"},
                {"row":"J","col":2,"label":"DAT1","type":"DAT","desc":"Data Line 1"},
                {"row":"K","col":1,"label":"DAT2","type":"DAT","desc":"Data Line 2"},
                {"row":"K","col":2,"label":"DAT3","type":"DAT","desc":"Data Line 3"},
                {"row":"L","col":1,"label":"DAT4","type":"DAT","desc":"Data Line 4"},
                {"row":"L","col":2,"label":"DAT5","type":"DAT","desc":"Data Line 5"},
                {"row":"M","col":2,"label":"DAT6","type":"DAT","desc":"Data Line 6"},
                {"row":"N","col":2,"label":"DAT7","type":"DAT","desc":"Data Line 7"}
            ]

        # Fast lookup
        pin_dict = {(p['row'], p['col']): p for p in pins}

        start_x = 36
        start_y = 30
        gap = 24
        radius = 8

        # Draw Column Numbers
        for c_idx, c_num in enumerate(col_labels):
            cx = start_x + c_idx * gap
            canvas.create_text(cx, start_y - 16, text=str(c_num), fill="#6b7280", font=("Segoe UI", 8, "bold"))

        # Draw Row Letters and Pads
        for r_idx, r_lbl in enumerate(row_labels):
            ry = start_y + r_idx * gap
            canvas.create_text(start_x - 20, ry, text=r_lbl, fill="#6b7280", font=("Segoe UI", 8, "bold"))

            for c_idx, c_num in enumerate(col_labels):
                cx = start_x + c_idx * gap

                # Exact Cutout
                if is_221:
                    is_cutout = (c_num >= 5 and c_num <= 11 and r_lbl not in ['A', 'R'])
                else:
                    is_cutout = (c_num >= 5 and c_num <= 10 and r_lbl not in ['A', 'P'])

                if is_cutout:
                    continue

                p_data = pin_dict.get((r_lbl, c_num))
                tag = f"pad_{r_lbl}_{c_num}"

                if p_data:
                    ptype = p_data['type']
                    pcol = "#ef4444" if ptype == "VCC" else ("#ea580c" if ptype == "VCCQ" else ("#eab308" if ptype in ["CLK", "CMD"] else ("#10b981" if ptype == "DAT" else "#64748b")))
                    canvas.create_oval(cx - radius, ry - radius, cx + radius, ry + radius, fill=pcol, outline="#ffffff", width=1, tags=(tag, "pad"))
                    canvas.create_text(cx, ry, text=p_data['label'][:2] if len(p_data['label']) <= 2 else p_data['label'][0], fill="#000000" if ptype in ["CLK", "CMD"] else "#ffffff", font=("Segoe UI", 6, "bold"), tags=(tag, "pad"))
                else:
                    canvas.create_oval(cx - radius, ry - radius, cx + radius, ry + radius, fill="#181a24", outline="#2b3044", tags=(tag, "pad"))

        def on_pad_motion(event):
            closest = canvas.find_closest(event.x, event.y)
            if closest:
                tags = canvas.gettags(closest[0])
                for t in tags:
                    if t.startswith("pad_"):
                        parts = t.split("_")
                        if len(parts) == 3:
                            r_tag, c_tag = parts[1], int(parts[2])
                            p_info = pin_dict.get((r_tag, c_tag))
                            if p_info:
                                lbl_name.config(text=f"Pin: {r_tag}{c_tag} [{p_info['label']}]", fg="#ef4444" if p_info['type']=="VCC" else "#d4af37")
                                lbl_desc.config(text=f"Function: {p_info['desc']}")
                            else:
                                lbl_name.config(text=f"Pin: {r_tag}{c_tag} [NC]", fg="#6b7280")
                                lbl_desc.config(text="Function: Not Connected. Safe to ignore during reballing/programming.")
                            return
            lbl_name.config(text="Pin: --", fg="#d4af37")
            lbl_desc.config(text="Function: Ready for inspection")

        canvas.bind("<Motion>", on_pad_motion)

    def render_gb_database_info(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        wrap = tk.Frame(parent, bg="#0a0a0c")
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        card = tk.Frame(wrap, bg="#12131a", bd=1, relief=tk.SOLID)
        card.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Header
        h = tk.Frame(card, bg="#12131a")
        h.pack(fill=tk.X, padx=20, pady=(14, 8))

        c_icon = tk.Frame(h, bg="#b71c1c", width=42, height=42, bd=1, relief=tk.SOLID)
        c_icon.pack(side=tk.LEFT, padx=(0, 10))
        c_icon.pack_propagate(False)
        tk.Label(c_icon, text="🗄️", font=("Segoe UI", 18), bg="#b71c1c", fg="#d4af37").pack(expand=True)

        tk.Label(h, text="Local eMMC / IC Database Specifications", font=("Segoe UI", 14, "bold italic"), fg="#ffffff", bg="#12131a").pack(anchor="w")
        tk.Label(h, text="COMPLETELY OFFLINE STORAGE REGISTRY INDEX", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#12131a").pack(anchor="w")

        # 3 Top Stats
        top_stats = tk.Frame(card, bg="#12131a")
        top_stats.pack(fill=tk.X, padx=20, pady=6)

        s_arr = [
            ("TOTAL IC PART RECORDS", f"{len(self.data_ic):,} Parts", "✓ 100% Verified Specifications", "#ffffff"),
            ("SUPPORTED BRANDS", "8 Premium", "Samsung, Hynix, Micron & more", "#d4af37"),
            ("CONNECTION STATUS", "● OFFLINE", "No internet dependency", "#00e676")
        ]

        for stitle, sval, ssub, scol in s_arr:
            sb = tk.Frame(top_stats, bg="#07080b", bd=1, relief=tk.SOLID)
            sb.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4, pady=2)
            tk.Label(sb, text=stitle, font=("Segoe UI", 7, "bold"), fg="#6b7280", bg="#07080b").pack(pady=(6, 1))
            tk.Label(sb, text=sval, font=("Segoe UI", 11, "bold"), fg=scol, bg="#07080b").pack()
            tk.Label(sb, text=ssub, font=("Segoe UI", 7), fg="#9ca3af", bg="#07080b").pack(pady=(0, 6))

        # Brand Grid Title
        tk.Label(card, text="INDEXED STORAGE PARTS BY MANUFACTURER", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#12131a").pack(anchor="w", padx=24, pady=(8, 4))

        # 8 Brand Cards
        b_grid = tk.Frame(card, bg="#12131a")
        b_grid.pack(fill=tk.X, padx=20, pady=4)

        b_counts = [
            ("Samsung", len([x for x in self.data_ic if "samsung" in x.get('manufacturer','').lower()])),
            ("SK Hynix", len([x for x in self.data_ic if "hynix" in x.get('manufacturer','').lower()])),
            ("Micron", len([x for x in self.data_ic if "micron" in x.get('manufacturer','').lower()])),
            ("Toshiba / Kioxia", len([x for x in self.data_ic if "toshiba" in x.get('manufacturer','').lower() or "kioxia" in x.get('manufacturer','').lower()])),
            ("Foresee", len([x for x in self.data_ic if "foresee" in x.get('manufacturer','').lower()])),
            ("SanDisk", len([x for x in self.data_ic if "sandisk" in x.get('manufacturer','').lower()])),
            ("Kingston", len([x for x in self.data_ic if "kingston" in x.get('manufacturer','').lower()])),
            ("Other Brands", len([x for x in self.data_ic if not any(k in x.get('manufacturer','').lower() for k in ['samsung','hynix','micron','toshiba','kioxia','foresee','sandisk','kingston'])]))
        ]

        for idx, (bname, bcount) in enumerate(b_counts):
            r = idx // 4
            c = idx % 4
            bb = tk.Frame(b_grid, bg="#07080b", bd=1, relief=tk.SOLID)
            bb.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
            b_grid.grid_columnconfigure(c, weight=1)
            tk.Label(bb, text=bname, font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#07080b").pack(anchor="w", padx=8, pady=(4, 0))
            tk.Label(bb, text=f"{bcount:,} records", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#07080b").pack(anchor="w", padx=8, pady=(0, 4))

        # Security Note
        sec_box = tk.Frame(card, bg="#07080b", bd=1, relief=tk.SOLID)
        sec_box.pack(fill=tk.X, padx=24, pady=(8, 12))
        tk.Label(sec_box, text="🛡️ TECHNICIAN SECURITY VERIFICATION", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#07080b").pack(anchor="w", padx=10, pady=(4, 1))
        tk.Label(sec_box, text="The local dataset includes real, production-used eMMC, eMCP, and UFS memories with verified pinouts and donor board compatibility. 100% offline with zero latency.", font=("Segoe UI", 8), fg="#9ca3af", bg="#07080b", justify=tk.LEFT).pack(anchor="w", padx=10, pady=(0, 4))

    def render_gb_about(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        wrap = tk.Frame(parent, bg="#0a0a0c")
        wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        card = tk.Frame(wrap, bg="#12131a", bd=1, relief=tk.SOLID)
        card.pack(expand=True, padx=20, pady=20)

        c_icon = tk.Frame(card, bg="#b71c1c", width=52, height=52, bd=1, relief=tk.SOLID)
        c_icon.pack(pady=(24, 10))
        c_icon.pack_propagate(False)
        tk.Label(c_icon, text="👑", font=("Segoe UI", 20), bg="#b71c1c", fg="#d4af37").pack(expand=True)

        tk.Label(card, text="HM TESTPOINT & HARDWARE SUITE v8.5", font=("Segoe UI", 15, "bold"), fg="#ffffff", bg="#12131a").pack(pady=2)
        tk.Label(card, text="INTEGRATED HM FINDER EMMC / UFS DATABASE ENGINE", font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#12131a").pack(pady=2)

        info = [
            ("Developer & Owner:", "Hassan Javed (Hassan Mobile Shop)"),
            ("Contact / WhatsApp:", "0344-1545807"),
            ("Database Coverage:", "5,350+ Storage ICs • 1,983 Testpoints • 187 ISP Pinouts"),
            ("Supported Packages:", "BGA 153, BGA 221, BGA 254, BGA 162"),
            ("License Status:", "VIP Lifetime Active 👑")
        ]

        f_box = tk.Frame(card, bg="#07080b", bd=1, relief=tk.SOLID)
        f_box.pack(fill=tk.X, padx=28, pady=14)

        for l_lbl, l_val in info:
            r = tk.Frame(f_box, bg="#07080b")
            r.pack(fill=tk.X, padx=14, pady=3)
            tk.Label(r, text=l_lbl, font=("Segoe UI", 8, "bold"), fg="#9ca3af", bg="#07080b", width=20, anchor="w").pack(side=tk.LEFT)
            tk.Label(r, text=l_val, font=("Segoe UI", 8, "bold"), fg="#ffffff" if "VIP" not in l_val else "#00e676", bg="#07080b", anchor="w").pack(side=tk.LEFT)

    def open_register_ic_modal(self):
        top = tk.Toplevel(self.root)
        top.title("Register Custom Storage IC Spec")
        top.geometry("520x460")
        top.configure(bg="#0c0d12")
        top.transient(self.root)
        top.grab_set()

        tk.Label(top, text="⚡ REGISTER CUSTOM STORAGE IC SPEC", font=("Segoe UI", 12, "bold"), fg="#ef4444", bg="#0c0d12").pack(pady=(16, 12))

        form = tk.Frame(top, bg="#0c0d12")
        form.pack(fill=tk.BOTH, expand=True, padx=20)

        fields = [
            ("IC Part Number (e.g. KMQ7X000SA):", "ic_number"),
            ("Manufacturer (e.g. Samsung, SK Hynix):", "mfr"),
            ("Capacity (e.g. 64GB, 128GB):", "cap"),
            ("Package Footprint (e.g. BGA 221, BGA 153):", "pkg"),
            ("Memory Type (e.g. eMCP, eMMC 5.1, UFS):", "typ"),
            ("Compatible Mobile Models (Comma separated):", "models")
        ]

        entries = {}
        for f_label, f_key in fields:
            tk.Label(form, text=f_label, font=("Segoe UI", 8, "bold"), fg="#d4af37", bg="#0c0d12").pack(anchor="w", pady=(4, 1))
            ent = tk.Entry(form, font=("Segoe UI", 9), bg="#161722", fg="#ffffff", bd=1, relief=tk.SOLID, insertbackground="#ffffff")
            ent.pack(fill=tk.X, pady=(0, 4))
            entries[f_key] = ent

        def save_custom_ic():
            ic_num = entries['ic_number'].get().strip()
            if not ic_num:
                messagebox.showerror("Error", "IC Part Number is required!", parent=top)
                return

            new_rec = {
                "id": f"custom-{len(self.data_ic)+1}",
                "ic_number": ic_num,
                "manufacturer": entries['mfr'].get().strip() or "Samsung",
                "capacity_gb": entries['cap'].get().strip() or "64GB",
                "package": entries['pkg'].get().strip() or "BGA 221",
                "type": entries['typ'].get().strip() or "eMCP",
                "generation": "eMMC 5.1",
                "voltage": "VCC: 2.9V-3.3V / VCCQ: 1.8V",
                "compatible_models": [m.strip() for m in entries['models'].get().split(",") if m.strip()],
                "notes": "Custom registered technician record."
            }

            self.data_ic.insert(0, new_rec)

            # Persist to disk
            ic_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emmc_ufs_database.json")
            try:
                with open(ic_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data_ic, f, indent=2)
            except Exception:
                pass

            messagebox.showinfo("Success", f"IC {ic_num} registered successfully!", parent=top)
            top.destroy()
            self.filter_gb_ic_list()

        btn_box = tk.Frame(top, bg="#0c0d12")
        btn_box.pack(fill=tk.X, padx=20, pady=16)

        tk.Button(btn_box, text="CANCEL", font=("Segoe UI", 8, "bold"), bg="#252736", fg="#9ca3af", bd=0, padx=12, pady=6, cursor="hand2", command=top.destroy).pack(side=tk.LEFT)
        tk.Button(btn_box, text="REGISTER TO DATABASE", font=("Segoe UI", 8, "bold"), bg="#b71c1c", fg="#ffffff", bd=0, padx=16, pady=6, cursor="hand2", command=save_custom_ic).pack(side=tk.RIGHT)

    def draw_bga_pinout(self, canvas, pkg):
        canvas.delete("all")
        
        # BGA Matrix drawing
        is_221 = "221" in pkg
        is_254 = "254" in pkg
        
        cols = 14 if is_221 else (15 if is_254 else 13)
        rows = 14 if is_221 else (15 if is_254 else 13)
        
        start_x = 24
        start_y = 18
        gap = 13
        radius = 4

        # Key ISP Balls definition
        isp_balls = {
            (2, 6): ("CMD", "#ffeb3b"),
            (3, 6): ("CLK", "#ff9800"),
            (4, 6): ("D0", "#2196f3"),
            (5, 6): ("D1", "#2196f3"),
            (6, 6): ("D2", "#2196f3"),
            (7, 6): ("D3", "#2196f3"),
            (2, 8): ("VCC", "#f44336"),
            (3, 8): ("VCCQ", "#e91e63"),
            (4, 8): ("RST", "#4caf50"),
            (5, 8): ("GND", "#9e9e9e")
        }

        for r in range(rows):
            for c in range(cols):
                # Center cutout for BGA
                if (rows//4 <= r <= rows*3//4) and (cols//4 <= c <= cols*3//4):
                    continue

                x = start_x + c * gap
                y = start_y + r * gap

                pin_info = isp_balls.get((r, c))
                if pin_info:
                    p_name, p_col = pin_info
                    canvas.create_oval(x - radius - 1, y - radius - 1, x + radius + 1, y + radius + 1, fill=p_col, outline="#ffffff")
                else:
                    canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="#383d52", outline="#222533")

        # Draw Legend on Right
        leg_x = 230
        leg_y = 16
        legends = [
            ("CMD (Command)", "#ffeb3b"),
            ("CLK (Clock)", "#ff9800"),
            ("D0 - D7 (Data)", "#2196f3"),
            ("VCC (3.3V Core)", "#f44336"),
            ("VCCQ (1.8V IO)", "#e91e63"),
            ("RST (Reset)", "#4caf50"),
            ("GND (Ground)", "#9e9e9e"),
        ]
        for name, col in legends:
            canvas.create_oval(leg_x, leg_y + 2, leg_x + 9, leg_y + 11, fill=col, outline="#ffffff")
            canvas.create_text(leg_x + 16, leg_y + 6, text=name, fill="#ffffff", font=("Segoe UI", 8, "bold"), anchor="w")
            leg_y += 18

        canvas.create_text(leg_x, leg_y + 10, text="Compatible Boxes:\n• EasyJTAG Plus\n• UFI Box\n• Medusa Pro II\n• MiPi Tester Box", fill="#00e5ff", font=("Segoe UI", 8), anchor="nw")

    # ═══════════════════════════════════════════════════════════════════════
    # 🔬 HARDWARE DIAGNOSTIC SUITE (SUGON 3010PM / MULTIMETER / USB CHARGER)
    # ═══════════════════════════════════════════════════════════════════════

    def show_hardware_lab_suite(self):
        if hasattr(self, 'canvas') and self.canvas.winfo_ismapped():
            self.canvas.pack_forget()
        if hasattr(self, 'canvas_tbar') and self.canvas_tbar.winfo_ismapped():
            self.canvas_tbar.pack_forget()
        if hasattr(self, 'sidebar') and self.sidebar.winfo_ismapped():
            self.sidebar.pack_forget()
        if hasattr(self, 'ic_panel') and self.ic_panel.winfo_ismapped():
            self.ic_panel.pack_forget()

        self.hw_lab_panel.pack(fill=tk.BOTH, expand=True)
        self.build_hw_lab_panel()

    def build_hw_lab_panel(self):
        for w in self.hw_lab_panel.winfo_children():
            w.destroy()

        # Outer container with scrollbar
        c = tk.Canvas(self.hw_lab_panel, bg="#0a0c14", bd=0, highlightthickness=0)
        sbar = tk.Scrollbar(self.hw_lab_panel, orient="vertical", command=c.yview)
        body = tk.Frame(c, bg="#0a0c14")

        body.bind("<Configure>", lambda e: c.configure(scrollregion=c.bbox("all")))
        c_win = c.create_window((0, 0), window=body, anchor="nw")

        def on_c_conf(event):
            c.itemconfig(c_win, width=event.width)
        c.bind("<Configure>", on_c_conf)
        c.configure(yscrollcommand=sbar.set)

        # Mouse wheel support
        def _on_hw_mousewheel(event):
            if c.winfo_exists():
                c.yview_scroll(int(-1 * (event.delta / 120)), "units")
        c.bind_all("<MouseWheel>", _on_hw_mousewheel)

        c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── 1. TOP HERO BANNER ──
        banner = tk.Frame(body, bg="#111422", bd=1, relief=tk.SOLID)
        banner.pack(fill=tk.X, padx=16, pady=(14, 10))

        b_top = tk.Frame(banner, bg="#111422")
        b_top.pack(fill=tk.X, padx=16, pady=12)

        # Left title info
        b_left = tk.Frame(b_top, bg="#111422")
        b_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tag_row = tk.Frame(b_left, bg="#111422")
        tag_row.pack(anchor="w")

        tk.Label(tag_row, text="🔬 HARDWARE MASTER LAB", font=("Segoe UI", 9, "bold"), bg="#b71c1c", fg="#ffffff", padx=8, pady=2).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(tag_row, text="URDU & ENGLISH BILINGUAL", font=("Segoe UI", 9, "bold"), bg="#00897b", fg="#ffffff", padx=8, pady=2).pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(tag_row, text="REAL DIAGNOSTIC PHOTOS & READINGS", font=("Segoe UI", 9, "bold"), bg="#f57f17", fg="#000000", padx=8, pady=2).pack(side=tk.LEFT)

        tk.Label(b_left, text="Mobile Motherboard Real Hardware Diagnostics & Fault Solver", font=("Segoe UI", 15, "bold"), fg="#ffffff", bg="#111422").pack(anchor="w", pady=(8, 2))
        tk.Label(b_left, text="SUGON 3010PM (30V/10A DC Power Supply) • UNI-T UT33B+ Multimeter • USB Doctor 6-Port Smart Fast Charger • 4-Stage Repair Wizard", font=("Segoe UI", 9), fg="#94a3b8", bg="#111422").pack(anchor="w")

        # Right launch button
        btn_hero_launch = tk.Button(
            b_top,
            text="🚀 LAUNCH STANDALONE LAB\n[ Interactive Real Experience ]",
            font=("Segoe UI", 10, "bold"),
            bg="#e53935", fg="#ffffff",
            activebackground="#ff5252", activeforeground="#ffffff",
            bd=0, relief=tk.FLAT, padx=18, pady=8, cursor="hand2",
            command=self.launch_hardware_lab
        )
        btn_hero_launch.pack(side=tk.RIGHT, padx=6)

        # ── 2. THREE COMPONENT CARDS ──
        cards_wrap = tk.Frame(body, bg="#0a0c14")
        cards_wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        for col in range(3):
            cards_wrap.grid_columnconfigure(col, weight=1, uniform="hw_card")

        self.hw_photos = []

        card_data = [
            (
                "⚡ SUGON 3010PM (DC SUPPLY)",
                "#b71c1c",
                "30V / 10A High Precision Digital Display",
                "sugon_3010pm.jpg",
                [
                    ("Full Short (VBAT/VPH):", "0.00V | 5.00A", "فل شارٹ - بیپ اور ہیٹ (VPH شارٹ)"),
                    ("Half Short / Leakage:", "4.20V | 0.22A", "ہاف شارٹ - فون گرم یا بیٹری جلدی ختم"),
                    ("CPU Dead Stuck:", "4.20V | 0.14A", "سی پی یو ہینگ / بوٹ سیکوئنس بریک"),
                    ("Auto Ampere on In:", "4.20V | 0.38A", "بغیر پاور بٹن دبائے کرنٹ لینا (PMIC فالٹ)"),
                    ("Charging IC Heat:", "4.20V | 0.85A", "چارجنگ آئی سی شارٹ یا لیک ہونا"),
                    ("Restart Loop / Reboot:", "4.20V | 0.05-0.45A", "کرنٹ 0 سے 400mA جا کر بار بار زیرو ہونا")
                ],
                "Live Voltage/Ampere dials, 8 real fault states, 4 memory presets, and complete Urdu/English analysis."
            ),
            (
                "📟 UNI-T UT33B+ MULTIMETER",
                "#0288d1",
                "Digital Precision Multi-Tester Mode",
                "unit_ut33b.jpg",
                [
                    ("Diode Testing Mode:", "0.350V - 0.700V", "نارمل لائن ڈراپ (ریڈ پروب گراؤنڈ پر رکھیں)"),
                    ("Short to Ground (Buzzer):", "0.000V / 0 Ω", "لائن شارٹ ہے - بیپ کی آواز آئے گی"),
                    ("Open Line (OL):", "O.L (High)", "لائن کٹ گئی ہے - ٹریک اوپن ہے"),
                    ("VPH_PWR Main Line:", "3.70V - 4.20V", "مین سسٹم وولٹیج بس نارمل ہے"),
                    ("CPU Buck Coils:", "0.80V - 1.15V", "پروسیسر کور وولٹیج اوکے ہے"),
                    ("LDO Regulators:", "1.80V / 2.80V", "سینسر اور ڈسپلے کے ریگولیٹر وولٹیج")
                ],
                "Interactive rotary selector, Diode/DCV/Resistance, and technician testing guides in Urdu & English."
            ),
            (
                "🔌 USB DOCTOR & SMART CHARGER",
                "#2e7d32",
                "6-Port Smart Fast Charger & QC3.0",
                None,
                [
                    ("Normal Fast Charge:", "5.0V | 1.85A", "نارمل فاسٹ چارجنگ ایکٹو ہے (OK)"),
                    ("QC 3.0 High Voltage:", "9.0V | 1.60A", "کوئیک چارج ہینڈ شیک کامیاب ہے"),
                    ("Fake Charging:", "5.0V | 0.18A", "فیک چارجنگ - چارجنگ آئی سی یا بیٹری فالٹ"),
                    ("Dead Line / No Detect:", "5.0V | 0.00A", "سب بورڈ یا ٹائپ سی پن ڈسکنیکٹ ہے"),
                    ("Stage 1: Cold Resistance", "Diode Mode", "گراؤنڈ سے تمام پنوں کی کولڈ ٹیسٹنگ"),
                    ("Stage 2: DC Power Check", "Current Pulse", "پاور بٹن دبانے کے بعد کرنٹ رسپانس")
                ],
                "6-Port dynamic ports, live LED ammeter readouts, and 4-Stage Motherboard Fault Finding Wizard."
            )
        ]

        for idx, (title, color, subtitle, img_file, items, note) in enumerate(card_data):
            card = tk.Frame(cards_wrap, bg="#131622", bd=1, relief=tk.SOLID)
            card.grid(row=0, column=idx, sticky="nsew", padx=6, pady=6)

            # Header strip
            c_hdr = tk.Frame(card, bg=color, height=36)
            c_hdr.pack(fill=tk.X)
            c_hdr.pack_propagate(False)
            tk.Label(c_hdr, text=title, font=("Segoe UI", 10, "bold"), fg="#ffffff", bg=color).pack(side=tk.LEFT, padx=10)

            body_c = tk.Frame(card, bg="#131622", padx=10, pady=10)
            body_c.pack(fill=tk.BOTH, expand=True)

            tk.Label(body_c, text=subtitle, font=("Segoe UI", 8, "bold"), fg="#ffb300", bg="#131622").pack(anchor="w", pady=(0, 6))

            # Real Instrument Photo Showcase Box
            if img_file:
                default_asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
                p_paths = [
                    os.path.join(default_asset_dir, img_file),
                    os.path.join(get_app_dir(), "assets", img_file),
                    os.path.join(r"C:\HM_Toolkits\assets", img_file)
                ]
                found_p = next((p for p in p_paths if os.path.exists(p)), None)
                if not found_p:
                    try:
                        os.makedirs(default_asset_dir, exist_ok=True)
                        target_f = os.path.join(default_asset_dir, img_file)
                        cdn_img_url = f"https://raw.githubusercontent.com/obutt339/HM-Admin-Cloud/main/assets/{img_file}"
                        req = urllib.request.Request(cdn_img_url, headers={'User-Agent': 'Mozilla/5.0 HM-Client'})
                        with urllib.request.urlopen(req, timeout=8) as resp:
                            if resp.status == 200:
                                with open(target_f, "wb") as out_f:
                                    out_f.write(resp.read())
                                found_p = target_f
                    except Exception:
                        pass

                if found_p:
                    try:
                        im = Image.open(found_p)
                        im.thumbnail((160, 160), Image.Resampling.LANCZOS)
                        p_photo = ImageTk.PhotoImage(im)
                        self.hw_photos.append(p_photo)

                        p_box = tk.Frame(body_c, bg="#07090e", bd=1, relief=tk.SOLID, height=165)
                        p_box.pack(fill=tk.X, pady=(0, 8))
                        p_box.pack_propagate(False)

                        tk.Label(p_box, image=p_photo, bg="#07090e").pack(expand=True)
                    except Exception:
                        pass

            # Table of readings
            t_frame = tk.Frame(body_c, bg="#0d0f18", bd=1, relief=tk.SOLID)
            t_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

            for r_title, r_val, r_urdu in items:
                row = tk.Frame(t_frame, bg="#0d0f18")
                row.pack(fill=tk.X, padx=6, pady=3)

                r_top = tk.Frame(row, bg="#0d0f18")
                r_top.pack(fill=tk.X)
                tk.Label(r_top, text=r_title, font=("Segoe UI", 8, "bold"), fg="#ffffff", bg="#0d0f18").pack(side=tk.LEFT)
                tk.Label(r_top, text=r_val, font=("Consolas", 8, "bold"), fg="#00ff66", bg="#0d0f18").pack(side=tk.RIGHT)

                tk.Label(row, text=f"اردو: {r_urdu}", font=("Segoe UI", 8), fg="#94a3b8", bg="#0d0f18", anchor="w", justify=tk.LEFT).pack(fill=tk.X)

            tk.Label(body_c, text=note, font=("Segoe UI", 8), fg="#64748b", bg="#131622", wraplength=280, justify=tk.LEFT).pack(anchor="w", pady=(0, 8))

            b_btn = tk.Button(
                body_c,
                text="⚡ Open Standalone Lab",
                font=("Segoe UI", 9, "bold"),
                bg="#252a3d", fg="#ffffff",
                activebackground=color, activeforeground="#ffffff",
                bd=0, padx=8, pady=4, cursor="hand2",
                command=self.launch_hardware_lab
            )
            b_btn.pack(fill=tk.X, pady=(2, 0))

        # ── 3. FOUR-STAGE MOTHERBOARD FAULT FINDING SUMMARY ──
        w_box = tk.Frame(body, bg="#111422", bd=1, relief=tk.SOLID)
        w_box.pack(fill=tk.X, padx=16, pady=(8, 16))

        tk.Label(w_box, text="🛠️ 4-STAGE MOTHERBOARD FAULT-FINDING WIZARD (DEAD / SHORT / RESTART)", font=("Segoe UI", 11, "bold"), fg="#00e5ff", bg="#111422").pack(anchor="w", padx=14, pady=(10, 4))
        tk.Label(w_box, text="Step-by-step master methodology followed by top GSM repair labs worldwide:", font=("Segoe UI", 8), fg="#94a3b8", bg="#111422").pack(anchor="w", padx=14, pady=(0, 8))

        stages = [
            ("Stage 1: Cold Test (Diode Mode)", "بیٹری کنیکٹر اور VPH لائن پر ملٹی میٹر سے ریورس بائیس ڈائیوڈ ویلیو چیک کریں۔ اگر 0.00V آئے تو فل شارٹ ہے، اوپن لائن آئے تو ٹریک کٹا ہوا ہے۔"),
            ("Stage 2: DC Power Connection", "ڈی سی سپلائی 4.2V پر لگائیں۔ اگر کیبل لگاتے ہی بغیر پاور بٹن دبائے کرنٹ لے تو پاور آئی سی یا چارجنگ لائن میں شارٹ سرکٹ ہے۔"),
            ("Stage 3: Power Key Trigger Check", "پاور بٹن دبانے کے بعد ایمپیئر چیک کریں۔ اگر 0.12A-0.15A پر سوئی پھنس جائے تو CPU یا Clock Crystal کا فالٹ ہے۔"),
            ("Stage 4: USB Charger Handshake", "6-پورٹ اسمارٹ چارجر میں فون لگائیں۔ اگر 0.00A رہے تو سب بورڈ یا کنیکٹر خراب ہے، اگر 0.18A پر رکے تو بیٹری یا ڈسپلے سگنل غائب ہے۔")
        ]

        s_grid = tk.Frame(w_box, bg="#111422")
        s_grid.pack(fill=tk.X, padx=14, pady=(0, 12))

        for idx, (s_title, s_desc) in enumerate(stages):
            s_card = tk.Frame(s_grid, bg="#0b0d16", bd=1, relief=tk.SOLID)
            s_card.pack(fill=tk.X, pady=3)

            tk.Label(s_card, text=s_title, font=("Segoe UI", 9, "bold"), fg="#ffd54f", bg="#0b0d16").pack(anchor="w", padx=10, pady=(4, 1))
            tk.Label(s_card, text=f"وضاحت: {s_desc}", font=("Segoe UI", 8), fg="#e2e8f0", bg="#0b0d16", justify=tk.LEFT, wraplength=850).pack(anchor="w", padx=10, pady=(0, 6))

    def on_tree_double_click(self, event):
        self.on_tree_select(event)

    def load_image(self, path):
        img_obj = None

        # 1. Try loading from Encrypted Vault in RAM (Zero disk files!)
        try:
            from hm_vault_reader import HmVaultReader
            v_bytes = HmVaultReader.get_instance().get_image_bytes(path)
            if v_bytes:
                import io
                img_obj = Image.open(io.BytesIO(v_bytes))
        except Exception:
            pass

        # 2. Fallback to direct path if on dev machine
        if not img_obj and os.path.exists(path):
            try:
                img_obj = Image.open(path)
            except Exception:
                pass

        if not img_obj:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                text=f"Image Not Found in Vault:\n{os.path.basename(path)}", fill="#ff4444", font=("Segoe UI", 12, "bold"), justify=tk.CENTER
            )
            return

        try:
            self.orig_image = img_obj
            self.rotation_angle = 0
            self.zoom_level = 1.0
            self.fit_to_window()
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                text=f"Error Loading Image:\n{e}", fill="#ff4444", font=("Segoe UI", 12, "bold"), justify=tk.CENTER
            )

    def render_canvas(self):
        if not self.orig_image:
            return

        w, h = self.orig_image.size
        img = self.orig_image.rotate(self.rotation_angle, expand=True) if self.rotation_angle != 0 else self.orig_image.copy()

        new_w = max(50, int(img.width * self.zoom_level))
        new_h = max(50, int(img.height * self.zoom_level))
        
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")
        
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()

        pos_x = (c_w - new_w) // 2 if new_w < c_w else 10
        pos_y = (c_h - new_h) // 2 if new_h < c_h else 10

        self.canvas_img_id = self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        self.lbl_zoom_info.config(
            text=f"Resolution: {w}x{h} | Zoom: {int(self.zoom_level * 100)}% | Rotation: {self.rotation_angle}°"
        )

    def fit_to_window(self):
        if not self.orig_image:
            return
        c_w = max(100, self.canvas.winfo_width() - 30)
        c_h = max(100, self.canvas.winfo_height() - 30)
        
        img_w, img_h = self.orig_image.size
        ratio = min(c_w / img_w, c_h / img_h)
        self.zoom_level = min(1.0, ratio)
        self.render_canvas()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.render_canvas()

    def zoom_in(self):
        self.zoom_level = min(5.0, self.zoom_level * 1.25)
        self.render_canvas()

    def zoom_out(self):
        self.zoom_level = max(0.1, self.zoom_level / 1.25)
        self.render_canvas()

    def rotate_image(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.render_canvas()

    def on_pan_start(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def on_pan_move(self, event):
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.canvas.move("all", dx, dy)
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def on_resize(self, event):
        if self.orig_image:
            self.fit_to_window()

    def copy_to_clipboard(self):
        if not self.selected_model or not os.path.exists(self.selected_model['path']):
            return
        try:
            p = self.selected_model['path']
            cmd = f'powershell -Command "Set-Clipboard -Path \'{p}\'"'
            subprocess.run(cmd, shell=True)
            messagebox.showinfo("Copied", f"Diagram copied to clipboard!\n{self.selected_model['name']}", parent=self.root)
        except Exception:
            pass

    def open_folder(self):
        if self.selected_model and os.path.exists(self.selected_model['path']):
            subprocess.run(f'explorer /select,"{self.selected_model["path"]}"')

    def open_external(self):
        if self.selected_model and os.path.exists(self.selected_model['path']):
            os.startfile(self.selected_model['path'])

    def bind_shortcuts(self):
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.reset_zoom())
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def exit_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

def launch_main_app():
    root = tk.Tk()
    app = HMTestpointApp(root)
    root.mainloop()

if __name__ == '__main__':
    if not check_is_registered():
        hwid = get_hwid()
        expected = generate_valid_key(hwid)
        dialog = HMActivationDialog(hwid, expected)
        if not dialog.run():
            sys.exit(0)
    launch_main_app()
