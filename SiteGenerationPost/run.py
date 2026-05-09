import subprocess
import time
import sys

print("Запуск сервера...")
proc = subprocess.Popen([sys.executable, "app.py"], cwd=r"C:\PythonProjects\Website-OpenCod\SiteGenerationPost")
time.sleep(3)
print("Сервер запущен. Нажмите Ctrl+C для остановки.")
proc.wait()