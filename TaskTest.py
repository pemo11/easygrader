# file: TaskTest.py

class TaskTest:

    def __init__(self, id, name, active, type):
        self.id = id
        self.name = name
        self.active = active
        self.type = type
        self.testClass = ""
        self.testDescription = ""
        self.testMethod = ""
        self.testScore = ""

    def __repr__(self):
        return f"Id={self.id} Name={self.name} Active={self.active} Type={self.type}"
