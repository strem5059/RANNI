import subprocess
import psutil
import os
import time
from pathlib import Path
from core.utils.logger import ranni_logger

class SystemExecutor:
    def __init__(self, permissions=None):
        self.logger = ranni_logger.bind(module="executor")
        self.permissions = permissions or {}

    def execute(self, intent, params):
        action_map = {
            "open_application": self._open_application,
            "close_application": self._close_application,
            "list_windows": self._list_windows,
            "minimize_window": self._minimize_window,
            "maximize_window": self._maximize_window,
            "system_info": self._system_info,
            "volume_up": self._volume_up,
            "volume_down": self._volume_down,
            "volume_mute": self._volume_mute,
            "time_date": self._time_date,
            "lock_system": self._lock_system,
            "shutdown": self._shutdown,
            "restart": self._restart,
            "sleep": self._sleep,
            "screenshot": self._screenshot,
            "keyboard_type": self._keyboard_type,
            "list_directory": self._list_directory,
            "read_file": self._read_file,
            "write_file": self._write_file,
        }
        handler = action_map.get(intent)
        if not handler:
            self.logger.warning(f"Intención desconocida: {intent}")
            return {"success": False, "message": f"No sé cómo hacer: {intent}"}

        if not self._check_permission(intent):
            return {"success": False, "message": f"No tengo permiso para: {intent}"}

        try:
            return handler(params)
        except Exception as e:
            self.logger.error(f"Error ejecutando {intent}: {e}")
            return {"success": False, "message": str(e)}

    def _check_permission(self, intent):
        if intent in self.permissions:
            rule = self.permissions[intent]
            if rule == "deny":
                return False
        return True

    def _open_application(self, params):
        name = params.get("name", "").lower()
        path = params.get("path", "")
        app_map = {
            "chrome": "chrome",
            "firefox": "firefox",
            "edge": "msedge",
            "notepad": "notepad",
            "calculator": "calc",
            "explorer": "explorer",
            "cmd": "cmd",
            "terminal": "cmd",
            "powershell": "powershell",
            "vscode": "code",
            "spotify": "spotify",
            "word": "winword",
            "excel": "excel",
            "outlook": "outlook",
        }
        executable = path or app_map.get(name, name)
        if os.name == "nt":
            subprocess.Popen(f"start {executable}", shell=True)
        else:
            subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.logger.info(f"Abriendo: {executable}")
        return {"success": True, "message": f"Abriendo {name}"}

    def _close_application(self, params):
        name = params.get("name", "")
        for proc in psutil.process_iter(["pid", "name"]):
            if name.lower() in proc.info["name"].lower():
                proc.terminate()
                self.logger.info(f"Cerrando: {proc.info['name']} (PID: {proc.info['pid']})")
                return {"success": True, "message": f"Cerrando {name}"}
        return {"success": False, "message": f"No encontré {name} ejecutándose"}

    def _list_windows(self, params):
        try:
            import pygetwindow as gw
            windows = gw.getAllTitles()
            open_windows = [w for w in windows if w.strip()]
            return {"success": True, "message": f"Ventanas abiertas: {len(open_windows)}", "data": open_windows}
        except ImportError:
            return {"success": False, "message": "pygetwindow no instalado"}

    def _minimize_window(self, params):
        title = params.get("title", "")
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title)
            if windows:
                windows[0].minimize()
            return {"success": True, "message": "Ventana minimizada"}
        except:
            return {"success": False, "message": "No se pudo minimizar"}

    def _maximize_window(self, params):
        title = params.get("title", "")
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title)
            if windows:
                windows[0].maximize()
            return {"success": True, "message": "Ventana maximizada"}
        except:
            return {"success": False, "message": "No se pudo maximizar"}

    def _system_info(self, params):
        info_type = params.get("type", "general")
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        info = {
            "cpu": f"CPU: {cpu_percent}%",
            "ram": f"RAM: {memory.percent}% usado ({memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB)",
            "disk": f"Disco: {disk.percent}% usado ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)",
            "general": f"CPU: {cpu_percent}% | RAM: {memory.percent}% | Disco: {disk.percent}%"
        }
        msg = info.get(info_type, info["general"])
        return {"success": True, "message": msg, "data": info}

    def _volume_up(self, params):
        amount = params.get("amount", 10)
        if os.name == "nt":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current + amount / 100), None)
        return {"success": True, "message": f"Volumen subido {amount}%"}

    def _volume_down(self, params):
        amount = params.get("amount", 10)
        if os.name == "nt":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current - amount / 100), None)
        return {"success": True, "message": f"Volumen bajado {amount}%"}

    def _volume_mute(self, params):
        if os.name == "nt":
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(True, None)
        return {"success": True, "message": "Volumen silenciado"}

    def _time_date(self, params):
        from datetime import datetime
        now = datetime.now()
        return {"success": True, "message": f"Son las {now.strftime('%H:%M:%S')} del {now.strftime('%d/%m/%Y')}"}

    def _lock_system(self, params):
        if os.name == "nt":
            subprocess.run("rundll32.exe user32.dll,LockWorkStation")
        return {"success": True, "message": "Sistema bloqueado"}

    def _shutdown(self, params):
        if os.name == "nt":
            subprocess.run("shutdown /s /t 10", shell=True)
        return {"success": True, "message": "Apagando en 10 segundos"}

    def _restart(self, params):
        if os.name == "nt":
            subprocess.run("shutdown /r /t 10", shell=True)
        return {"success": True, "message": "Reiniciando en 10 segundos"}

    def _sleep(self, params):
        if os.name == "nt":
            subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return {"success": True, "message": "Suspensión activada"}

    def _screenshot(self, params):
        try:
            import pyautogui
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            path = str(Path.home() / "Desktop" / f"ranni_screenshot_{timestamp}.png")
            pyautogui.screenshot(path)
            return {"success": True, "message": f"Captura guardada en {path}", "data": path}
        except:
            return {"success": False, "message": "No se pudo tomar captura"}

    def _keyboard_type(self, params):
        text = params.get("text", "")
        try:
            import pyautogui
            pyautogui.write(text, interval=0.02)
            return {"success": True, "message": "Texto escrito"}
        except:
            return {"success": False, "message": "No se pudo escribir"}

    def _list_directory(self, params):
        path = params.get("path", ".")
        try:
            entries = os.listdir(path)
            return {"success": True, "message": f"Directorios: {len(entries)}", "data": entries[:20]}
        except:
            return {"success": False, "message": f"No se pudo listar: {path}"}

    def _read_file(self, params):
        path = params.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"success": True, "message": f"Archivo leído: {len(content)} caracteres", "data": content[:1000]}
        except:
            return {"success": False, "message": f"No se pudo leer: {path}"}

    def _write_file(self, params):
        path = params.get("path", "")
        content = params.get("content", "")
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "message": f"Archivo escrito: {path}"}
        except:
            return {"success": False, "message": f"No se pudo escribir: {path}"}
