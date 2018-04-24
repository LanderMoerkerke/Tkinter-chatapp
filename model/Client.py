from bson import ObjectId
import datetime


class Client():
    def __init__(self, name, nickname, email):
        self.name = name

        # nickname is unique
        self.nickname = nickname

        self.email = email
        self.dateLogin = datetime.datetime.now()
        self.dateLogout = None
        self.online = True
        self.messages = []
