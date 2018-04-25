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
        io = self.socketClient.makefile(mode='rw')

        msg = io.readline().rstrip('\n')

        while not self.initialized:
            logging.info("Client received: %s" % msg)
            try:
                self.client = json.loads(
                    msg, object_hook=json_util.object_hook)
                self.databaseQueue.put(self.client)
                self.initialized = True
            except ValueError as ve:
                logging.error("Cannot convert message")
            except Exception as ex:
                logging.error(ex)
            finally:
                msg = io.readline().rstrip('\n')

        while msg.lower() != "close":
            logging.info("Message received: %s" % msg)

            try:
                message = json.loads(msg, object_hook=json_util.object_hook)
                sender_object = [message, self.client["nickname"]]
                logging.info("Message parsed: %s" % sender_object)
                self.messageQueue.put(sender_object)
            except Exception as ex:
                logging.error(ex)
            except ValueError as ve:
                logging.error("Cannot parse message to json. %s" % ve)
            finally:
                msg = io.readline().rstrip('\n')

            msg = io.readline().rstrip('\n')
        self.socketClient.close()
        logging.info("Connection closed")
