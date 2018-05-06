import threading
import logging
import json
from bson import json_util


class ClientHandler(threading.Thread):
    amountClients = 0

    def __init__(self, pSocketClient, pMessageQueue, pDatabaseQueue,
                 pCurrentclients):
        threading.Thread.__init__(self)

        self.socketClient = pSocketClient
        self.messageQueue = pMessageQueue
        self.databaseQueue = pDatabaseQueue
        self.id = ClientHandler.amountClients
        self.currentClients = pCurrentclients

        self.initialized = False

        ClientHandler.amountClients += 1

    def run(self):
        logging.info("Thread run server started")
        logging.info("Amount of threads active: %s" % threading.active_count())
        self.io = self.socketClient.makefile(mode='rw')

        try:
            while not self.initialized:
                msg = self.io.readline().rstrip('\n')

                while msg[:3] == "CLT":
                    msg = self.io.readline().rstrip('\n')

                logging.info("Client received: %s" % msg)

                try:
                    self.client = json.loads(
                        msg, object_hook=json_util.object_hook)

                    # Checks if nickname is in use
                    if self.client["nickname"].lower() in self.currentClients:
                        self.io.write("%s\n" % "cltfailed")
                        self.io.flush()
                    else:
                        self.databaseQueue.put(self.client)
                        self.initialized = True
                except Exception as ex:
                    self.io.write("%s\n" % "clientnotadded")
                    self.io.flush()
                    logging.error(ex)

            self.io.write("%s\n" % "clientadded")
            self.io.flush()
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
                    raise ex
                except ValueError as ve:
                    logging.error("Cannot parse message to json. %s" % ve)
        except Exception as ex:
            self.socketClient.close()
            logging.info("Connection closed")

    def SendMessageToChatwindow(self, command, objString):
        # logging.info("Sending message to chatwindow: %s" % objString)
        self.io.write("%s%s\n" % (command, objString))
        self.io.flush()
