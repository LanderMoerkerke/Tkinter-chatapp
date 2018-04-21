import logging
import socket
import json
import threading
from server.Clienthandler import ClientHandler as Ch

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s--%(processName)s %(filename)s:%(lineno)s--%(message)s")

class Server(threading.Thread):
    def __init__(self, pHost, pPort, pMessageQueue=None):
        threading.Thread.__init__(self)

        self.host = pHost
        self.port = pPort
        self.messageQueue = pMessageQueue
        self.__serverStatus = False

    @property
    def statusServer(self):
        return self.__serverStatus

    def startServer(self):
        logging.info("Creating serversocket...")
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        self.__serverStatus = True
        logging.info("Server started")

    def stopServer(self):
        logging.info("Stopping server...")
        self.__serverStatus = False
        self.serversocket.close()
        logging.info("Stopped server")

    def run(self):
        logging.info("Threat run server started")
        logging.info("Amount of threads active: %s" % threading.active_count())

        try:
            while self.__serverStatus:
                logging.info("Waiting for a client...")

                # establish a connection!
                clientsocket, addr = self.serversocket.accept()
                logging.info("Got a connection from %s" % str(addr))

                cls = Ch(clientsocket, self.messageQueue)
                cls.start()

                logging.info("Amount of threads active: %s" % threading.active_count())

        except Exception as ex:
            logging.error(ex)
            self.serversocket.close()
            self.__serverStatus = False
            logging.info("Server closed")

    def print_message_gui(self, message):
        self.messageQueue.put("<Server> %s" % message)

rs = Server(socket.gethostname(), 7000, )
rs.startServer()
rs.run()
