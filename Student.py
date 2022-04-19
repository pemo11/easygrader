# file: Student.py

'''
Represents a single student
'''
class Student:

    def __init__(self, id):
        self.id = id
        self.firstName = ""
        self.lastName = ""
        self.email = ""

    def __repr__(self):
        return f"Id: {self.id} Name: {self.firstName} {self.lastName} Mail: {self.email}"
