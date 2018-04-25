import logging
import ujson
from pymongo import MongoClient, errors
from model.Message import Message
from model.Client import Client
from bson import ObjectId
import datetime


class MongoConnector():
    __CL_SERVER = "server"

    def __init__(self, pHost, pUsername, pPassword, db):
        self.__dsn = {
            "host": pHost,
            "port": 27017,
            "username": pUsername,
            "password": pPassword,
            "authSource": db
        }

        self.__connector = MongoClient(
            **self.__dsn, authMechanism="SCRAM-SHA-1")
        self.__cursor = self.__connector[db]

    def CheckUniqueNickname(self, nickname, serverId):
        nicknames = [nn.lower() for nn in self.GetNicknames(serverId)]

        if nickname.lower() in nicknames:
            return False
        else:
            return True

    # Send data
    def SendDocument(self, collection, document):
        try:
            logging.debug("Sending document to %s" % collection)
            data = self.__cursor[collection].insert_one(document)
            logging.debug("Sending complete")
            return data
        except errors.WriteError as we:
            logging.error("Document failed to send")

    def SendArrayDocuments(self, collection, documents):
        try:
            logging.debug("Sending documents to %s" % collection)
            data = self.__cursor[collection].insert_many(documents)
            logging.debug("Sending complete")
            return data
        except errors.WriteError as we:
            logging.error("Document failed to send")

    def CreateServer(self):
        try:
            logging.debug("Creating server")
            document = {"dateCreated": datetime.datetime.now(), "clients": []}
            server = self.__cursor[self.__CL_SERVER].insert_one(document)
            logging.debug("Server created")
            return server
        except errors.WriteError as we:
            logging.error("Server failed to create")

    def SendMessage(self, serverId, nickname, message):
        try:
            logging.debug("Updating server %s" % serverId)
            data = self.__cursor[self.__CL_SERVER].update_one(
                {
                    "_id": serverId,
                    "clients.nickname": nickname
                }, {'$push': {
                    "clients.$.messages": message.__dict__
                }})
            logging.debug("Sending complete")
            return data
        except errors.WriteError as we:
            logging.error("Document failed to send")

    # nog aanpassen krijgt dict binnen maar moet class zijn
    def AddClient(self, client, serverId):
        if self.CheckUniqueNickname(client["nickname"], serverId):
            try:
                logging.debug("Inserting client (%s) in server %s" %
                              (client["nickname"], serverId))
                data = self.__cursor[self.__CL_SERVER].update_one(
                    {
                        "_id": serverId
                    }, {'$push': {
                        "clients": client
                    }})
                logging.debug("Client added")
                return data
            except errors.WriteError as we:
                logging.error("Data failed to retreive")
        else:
            raise Exception

    # Get data
    def GetClients(self, serverId):
        try:
            logging.debug("Getting data from server %s" % serverId)
            data = self.__cursor[self.__CL_SERVER].find_one({
                "_id": serverId
            }, {"clients": 1})
            logging.debug("Retreiving complete")
            return data["clients"]
        except errors.WriteError as we:
            logging.error("Data failed to retreive")

    def GetNicknames(self, serverId):
        data = self.GetClients(serverId)

        try:
            logging.debug("Getting nicknames from clients")
            nicknames = [d["nickname"] for d in data]
            logging.debug("Nicknames retreived")
            return nicknames
        except Exception as identifier:
            logging.error("Nicknames failed to extract")

    def GetClientByNickname(self, nickname, serverId):
        try:
            logging.debug("Getting data from client %s" % nickname)
            data = self.__cursor[self.__CL_SERVER].find_one(
                {
                    "clients.nickname": nickname,
                    "_id": serverId,
                }, {"clients.$.messages": 1})
            logging.debug("Retreiving client complete")
            return data
        except errors.WriteError as we:
            logging.error("Data failed to retreive")

    def GetMessagesByClientId(self, clientId):
        data = self.GetClientByClientId(clientId)

        try:
            logging.debug("Getting data from client %s" % clientId)
            messages = data["clients"][0]["messages"]
            logging.debug("Retreiving client complete")
            return messages
        except errors.WriteError as we:
            logging.error("Data failed to retreive")


def main():

    from pprint import pprint

    mc = MongoConnector("localhost", "chat", "password", "chatapp")

    # cl = Client("Jan", "jJ", "jj@hotmail.com")
    # post = [ { "dateCreated": "2018-04-14 15:49:32.597768", "dateClosed": "2018-04-14 15:49:32.597768", "clients": [ { "name": "Lander Moerkerke", "nickname": "lander", "dateLogin": "2018-04-14 15:49:32.597768", "dateLogout": "2018-04-14 15:49:32.597768", "online": True, "email": "lander.moerkerke@student.howest.be", "[messages]": [ { "dateSent": "2018-04-14 15:49:32.597768", "text": "Hoi :)" } ] }, { "name": "Jamie Fong", "nickname": "jamie", "dateLogin": "2018-04-14 15:49:32.597768", "dateLogout": "2018-04-14 15:49:32.597768", "online": False, "email": "jamie.fong@student.howest.be", "messages": [ { "dateSent": "2018-04-14 15:49:32.597768", "text": "Hallo!" } ] } ] }]
    # print(post)
    # test = mc.SendArrayDocuments("server", post)
    # test = mc.SendMessage(ObjectId("5ad2080b67db1d158cff4b3e"), ObjectId("5ad314fd67db1d42b87a112c"), Message("ko"))
    # test = mc.CheckUniqueNickname("lander", ObjectId("5ad2080b67db1d158cff4b3e"))
    # test = mc.GetClients(ObjectId("5ad2080b67db1d158cff4b3e"))
    # test = mc.GetMessagesByClientId(ObjectId("5ad314fd67db1d42b87a112c"))
    # test = mc.AddClient(cl, ObjectId("5ad2080b67db1d158cff4b3e"))
    # test = mc.GetClientByNickname("lander", ObjectId("5ad2080b67db1d158cff4b3e"))
    test = mc.CreateServer()
    pprint(test.inserted_id)
    for i in test:
        print(Message(**i))

    # print(Message("Test"))


if __name__ == '__main__':
    main()
