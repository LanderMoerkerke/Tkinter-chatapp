import threading
import logging
import json
from bson import json_util


class ClientHandler(threading.Thread):
    amountClients = 0

    def __init__(self, pSocketClient, pMessageQueue, pDatabaseQueue):
        threading.Thread.__init__(self)

        self.socketClient = pSocketClient
        self.messageQueue = pMessageQueue
        self.databaseQueue = pDatabaseQueue
        self.id = ClientHandler.amountClients

        self.initialized = False

        ClientHandler.amountClients += 1

    def run(self):
        logging.info("Threat run server started")
        logging.info("Amount of threads active: %s" % threading.active_count())
        self.io = self.socketClient.makefile(mode='rw')

        try:
            while not self.initialized:
                msg = self.io.readline().rstrip('\n')
                logging.info("Client received: %s" % msg)

                try:
                    self.client = json.loads(
                        msg, object_hook=json_util.object_hook)
                    self.databaseQueue.put(self.client)
                    self.initialized = True
                except ValueError as ve:
                    logging.error("Cannot convert message")
                except Exception as ex:
                    logging.error("Hierzo")
                    logging.error(ex)

            msg = self.io.readline().rstrip('\n')
            logging.info("Message received: %s" % msg)

            while msg.lower() != "close":
                try:
                    message = json.loads(
                        msg, object_hook=json_util.object_hook)
                    sender_object = [message, self.client["nickname"]]
                    logging.info("Message parsed: %s" % sender_object)
                    self.messageQueue.put(sender_object)

                    msg = self.io.readline().rstrip('\n')
                    logging.info("Message received: %s" % msg)
                except Exception as ex:
                    logging.error(ex)
                except ValueError as ve:
                    logging.error("Cannot parse message to json. %s" % ve)

                msg = self.io.readline().rstrip('\n')
        except Exception as ex:
            self.socketClient.close()
            logging.info("Connection closed")

    def SendMessageToChatwindow(self, objString):
        self.io.write("%s\n" % objString)
        self.io.flush()
