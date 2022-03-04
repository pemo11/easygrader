# file: TaskAction.py

class TaskAction:

    def __init__(self, id, active, type, command):
        self.id = id
        self.active = active
        self.type = type
        self.command = command

    def __repr__(self):
        return f"Id={self.id} Active={self.active} Type={self.type} Command={self.command}"
