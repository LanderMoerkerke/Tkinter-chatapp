from bson import ObjectId
import datetime

class Client():
    def __init__(self, name, nickname, email):
        self.clientId = ObjectId()
        self.name = name
        self.nickname = nickname
        self.email = email
        self.dateLogin = datetime.datetime.now()
        self.online = True
        self.messages = []
