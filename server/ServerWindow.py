import socket
import logging
import json
from bson import json_util
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
        while True:
            obj = self.__messageQueue.get()

            if isinstance(obj, list):
                # [dict(message), nickname]
                logging.info("Retreived item from messagequeue: %s" % obj)

                message = obj[0]
                nickname = obj[1]

                if message["text"] == "CLOSE_SERVER":
                    logging.info("Text is equal to CLOSE SERVER, break!")
                    break

                # Message wordt op het logvenster geprint
                self.lstlog.insert(END, "%s: %s" % (nickname, message["text"]))

                # Message wordt naar de db gestuurd
                self.__mc.SendMessage(self.serverId, nickname, message)

                # Message wordt doorgestuurd naar iedere clienthandler
                logging.info("Sending messages to clienthandlers")
                self.SendMessageToHandlers("MSG",
                                           json.dumps(
                                               obj, default=json_util.default))

            elif isinstance(obj, str):
                # Clent exited the chatroom
                self.lstlog.insert(END, obj)
                if obj[-8:] == "chatroom":
                    # self.server.clientHandlers.remove()
                    self.SendMessageToHandlers("INF",
                                               json.dumps(
                                                   obj,
                                                   default=json_util.default))
            else:
                logging.critical("Item not implemented: %s, %s" % (obj,
                                                                   type(obj)))
            # Task done
            self.__messageQueue.task_done()

        print("queue stop")

    def SendMessageToHandlers(self, command, objJson):
        for clh in self.server.clientHandlers:
            clh.SendMessageToChatwindow(command, objJson)

    def processDatabaseQueue(self):
        while True:
            item = self.__databaseQueue.get()

            logging.info("Got a queue-item, databasequeue: %s" % item)

            dc = item[0]
            cmd = item[1]

            try:
                if cmd == "addClient":
                    # krijgt client binnen om toe te voegen
                    logging.info("Got addclient")
                    self.__mc.AddClient(dc, self.serverId)
                    self.lstlog.insert(END, "User: %s joined" % dc["nickname"])
                    self.SendMessageToHandlers(
                        "INF",
                        json.dumps(
                            "User: %s joined the chatroom" % dc["nickname"]))
                elif cmd == "offlineClient":
                    # krijgt client binnen om offline te zetten
                    logging.info("Got offlineclient")
                    self.__mc.LogoutClient(dc["nickname"], self.serverId)

                clients = self.__mc.GetClients(self.serverId)

                # Sends list of nicknames to clienthandler for used nicknames
                self.server.currentNicknames = [
                    client["nickname"].lower() for client in clients
                ]

                # Updating used nicknames in CLH's
                for clh in self.server.clientHandlers:
                    clh.currentNicknames = self.server.currentNicknames

                # Send list of clients to clienthandlers (for list online)
                self.SendMessageToHandlers("CLT",
                                           json.dumps(
                                               clients,
                                               default=json_util.default))

                # Updates lstClients (for list online and offline)
                self.lstclients.delete(0, END)
                [
                    self.lstclients.insert(END, client["nickname"])
                    if client["online"] else self.lstoffline.insert(
                        END, client["nickname"]) for client in clients
                ]

                # Task done
                self.__databaseQueue.task_done()

            except Exception as ex:
                raise ex
        print("queue stop")

    def initWindow(self):
        logging.info("Creating server window...")
        self.master.title("Server")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        self.scrollbarnn = Scrollbar(self, orient=VERTICAL)
        self.scrollbarlog = Scrollbar(self, orient=VERTICAL)
        self.scrollbaroff = Scrollbar(self, orient=VERTICAL)

        # listview Online
        Label(
            self, text="Online:").grid(
                row=0, column=0, sticky=W, padx=(5, 0))
        self.lstclients = Listbox(
            self, yscrollcommand=self.scrollbarnn.set, width=25, height=15)

        # Binds function with click event
        self.lstclients.bind('<<ListboxSelect>>', self.selectNickname)
        self.scrollbarnn.config(command=self.lstclients.yview)
        self.lstclients.grid(
            row=1, column=0, pady=(0, 7), padx=(5, 0), sticky=N + S + W)
        self.scrollbarnn.grid(row=1, column=1, pady=(0, 7), sticky=N + S + W)

        # listview Offline
        Label(
            self, text="Offline:").grid(
                row=2, column=0, sticky=W + N, padx=(5, 0))
        self.lstoffline = Listbox(
            self, yscrollcommand=self.scrollbaroff.set, width=25, height=15)
        self.scrollbaroff.config(command=self.lstoffline.yview)
        self.lstoffline.grid(
            row=3, column=0, pady=(0, 7), padx=(5, 0), sticky=N + S + W)
        self.scrollbaroff.grid(row=3, column=1, pady=(0, 7), sticky=N + S + W)
        Grid.rowconfigure(self, 2, weight=4)

        # knop start/stop server
        self.serverBtn = Button(self, text="Start/stop server", width=20)
        self.serverBtn.grid(row=4, column=0, pady=(0, 7), columnspan=2)

        # listview logberichten
        Label(
            self, text="Log-berichten server:").grid(
                row=0, column=2, sticky=W)
        self.lstlog = Listbox(
            self, yscrollcommand=self.scrollbarlog.set, width=80, height=30)
        self.scrollbarlog.config(command=self.lstlog.yview)
        self.lstlog.grid(
            row=1, column=2, pady=(0, 7), rowspan=4, sticky=N + S + E + W)
        self.scrollbarlog.grid(
            row=1,
            column=3,
            padx=(0, 5),
            pady=(0, 7),
            rowspan=4,
            sticky=N + W + E + S)

        Grid.rowconfigure(self, 2, weight=1)
        Grid.columnconfigure(self, 4, weight=1)

        logging.info("Serverwindow created")

    def selectNickname(self, e):
        selected = self.lstclients.get(ACTIVE)
        if selected:
            client = self.__mc.GetClientByNickname(selected, self.serverId)
            print(client)
            messagebox.showinfo(client["nickname"], str(client["messages"]))
        self.lstclients.selection_clear(0, END)

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
