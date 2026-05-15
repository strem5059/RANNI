import schedule
import time
import threading
from datetime import datetime
from core.utils.logger import ranni_logger

class TaskAutomation:
    def __init__(self):
        self.logger = ranni_logger.bind(module="automation")
        self.tasks = {}
        self._running = False
        self._thread = None

    def start_scheduler(self):
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.logger.info("Planificador de tareas iniciado")

    def _run_loop(self):
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def add_daily_task(self, task_id, time_str, callback, args=None):
        schedule.every().day.at(time_str).do(callback, *(args or []))
        self.tasks[task_id] = {"type": "daily", "time": time_str, "callback": callback}
        self.logger.info(f"Tarea diaria '{task_id}' programada a las {time_str}")

    def add_interval_task(self, task_id, minutes, callback, args=None):
        schedule.every(minutes).minutes.do(callback, *(args or []))
        self.tasks[task_id] = {"type": "interval", "minutes": minutes, "callback": callback}
        self.logger.info(f"Tarea '{task_id}' cada {minutes} minutos")

    def remove_task(self, task_id):
        schedule.clear(task_id)
        self.tasks.pop(task_id, None)

    def list_tasks(self):
        return list(self.tasks.keys())

    def stop(self):
        self._running = False
        schedule.clear()
