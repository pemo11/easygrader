# file: ErrorReportItem.py
from datetime import datetime

class ErrorReportItem:

    def __init__(self, message):
        self.timestamp = datetime.now()
        self.category = "None"
        self.message = message

    def __repr__(self):
        return f"Error-Item: {self.message} at {self.strftime('%d.%m%.%Y %H:%M')}"
