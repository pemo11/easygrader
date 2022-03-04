# file: TaskTest.py

class TaskTest:

    def __init__(self, id, active, type):
        self.id = id
        self.name = "Test"
        self.active = active
        self.type = type
        self.testClass = ""
        self.testDescription = ""
        self.testMethod = ""
        self.testScore = ""

    def __repr__(self):
        return f"Id={self.id} Active={self.active} Type={self.type}"
