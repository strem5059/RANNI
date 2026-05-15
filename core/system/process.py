import psutil
from core.utils.logger import ranni_logger

class ProcessManager:
    def __init__(self):
        self.logger = ranni_logger.bind(module="process")

    def list_processes(self, filter_str=None):
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                pinfo = proc.info
                if filter_str and filter_str.lower() not in pinfo["name"].lower():
                    continue
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(processes, key=lambda p: p["cpu_percent"] or 0, reverse=True)

    def get_process_by_name(self, name):
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if name.lower() in proc.info["name"].lower():
                    return proc.info
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return None

    def kill_process(self, pid):
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True
        except psutil.NoSuchProcess:
            return False
        except psutil.AccessDenied:
            return False

    def get_system_load(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }
