import socket
import logging
from threading import Thread
from queue import Queue

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from server.Server import Server
from model.MongoConnector import MongoConnector

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format=
    "%(asctime)s\t%(levelname)s--%(processName)s %(filename)s:%(lineno)s--%(message)s"
)


class ServerWindow(Frame):
    def __init__(self, port=7000, master=None):
        Frame.__init__(self, master)
        # Thread.__init__(self)
        self.master = master
        self.initWindow()

        self.__mc = MongoConnector("localhost", "chat", "password", "chatapp")
        self.serverId = self.__mc.CreateServer().inserted_id

        self.initMessageQueue()
        self.initDatabaseQueue()

        self.server = Server(socket.gethostname(), port, self.__messageQueue,
                             self.__databaseQueue)

        self.toggleServer()
        self.__port = port

    def initMessageQueue(self):
        self.__messageQueue = Queue(10)
        t = Thread(target=self.print_messsages_from_messageQueue)
        t.start()

    def initDatabaseQueue(self):
        self.__databaseQueue = Queue(10)
        t = Thread(target=self.processDatabaseQueue)
        t.start()
        logging.info("Databasequeue started")

    def print_messsages_from_messageQueue(self):
        message = self.__messageQueue.get()
        while message != "CLOSE_SERVER":
            self.lstnumbers.insert(END, message)
            self.__messageQueue.task_done()
            message = self.__messageQueue.get()
        print("queue stop")

    def processDatabaseQueue(self):
        print("processsing")
        client = self.__databaseQueue.get()
        while self.server.statusServer:
            self.__mc.AddClient(client, self.serverId)
            self.__databaseQueue.task_done()
            client = self.__databaseQueue.get()
        print("queue stop")

    def initWindow(self):
        logging.info("Creating server window...")
        self.master.title("Server")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Log-berichten server:").grid(row=0)
        self.scrollbarnn = Scrollbar(self, orient=VERTICAL)
        self.scrollbarlog = Scrollbar(self, orient=VERTICAL)

        self.lstclients = Listbox(self, yscrollcommand=self.scrollbarnn.set)
        self.scrollbarnn.config(command=self.lstclients.yview)

        self.lstlog = Listbox(self, yscrollcommand=self.scrollbarlog.set)
        self.scrollbarlog.config(command=self.lstlog.yview)

        self.lstclients.grid(
            row=1, column=0, columnspan=2, sticky=N + S + E + W)
        self.scrollbarnn.grid(row=1, column=1, sticky=N + S)

        WidgetNames = ['Button', 'Canvas']
        for widget in WidgetNames:
            self.lstclients.insert(0, widget)

        self.lstlog.grid(row=1, column=2, sticky=N + S + E + W)
        self.scrollbarlog.grid(row=1, column=3, sticky=N + S)

        self.btn_text = StringVar()
        self.btn_text.set("Start server")

        self.buttonServer = Button(
            self, textvariable=self.btn_text, command=self.toggleServer)

        self.buttonServer.grid(
            row=3,
            column=0,
            columnspan=4,
            pady=(5, 5),
            padx=(5, 5),
            sticky=N + S + E + W)

        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

        logging.info("Serverwindow created")

    def toggleServer(self):
        if self.server.statusServer:
            self.server.stopServer()
        else:
            self.server.startServer()
            self.server.start()

    def closeServer(self):
        self.server.stopServer()

    def statusServer(self):
        return self.server.statusServer()
