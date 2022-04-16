# file: Loghelper.py
import os.path
from datetime import datetime

heute = datetime.now().date()
logPath = os.path.join(os.path.dirname(__file__), f"simpelgraderV1_{heute}.log")

def logInfo(Message):
    uhrzeit = datetime.now().time().strftime("%H:%M")
    with open (logPath, "a", encoding="utf8") as fh:
        fh.write(f"|{uhrzeit}|Info: *** {Message}\n")

def logError(Message):
    uhrzeit = datetime.now().time().strftime("%H:%M")
    with open (logPath, "a", encoding="utf8") as fh:
        fh.write(f"|{uhrzeit}|Error: !!! {Message}\n")
