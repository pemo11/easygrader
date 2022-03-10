# file: Student.py

'''
Represents a single student
'''
class Student:

    def __init__(self, name, email):
        self.id = -1
        self.name = name
        self.email = email

    def __repr__(self):
        return f"Name: {self.name} Mail: {self.email}"
