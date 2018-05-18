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

        self.__port = port
        self.server = None

        self.__mc = MongoConnector("localhost", "chat", "password", "chatapp")
        self.serverId = self.__mc.CreateServer().inserted_id

        self.initMessageQueue()
        self.initDatabaseQueue()

        self.initServer()

        # self.toggleServer()

    def initServer(self):
        self.server = Server(socket.gethostname(), self.__port,
                             self.__messageQueue, self.__databaseQueue)
        self.server.startServer()
        self.server.start()

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

            # [client dict, commando]
            dc = item[0]
            cmd = item[1]

            try:
                if cmd == "addClient":
                    # krijgt client binnen om toe te voegen
                    logging.info("Got addclient")
                    self.__mc.AddClient(dc, self.serverId)
                    self.lstlog.insert(
                        END, "%s joined the chatroom!" % dc["nickname"])
                    self.SendMessageToHandlers(
                        "INF",
                        json.dumps("%s joined the chatroom!" % dc["nickname"]))
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
                self.lstoffline.delete(0, END)
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

        # Binds function with click event to listboxes
        self.lstclients.bind('<<ListboxSelect>>', self.selectNickname)
        self.lstoffline.bind('<<ListboxSelect>>', self.selectNickname)

        # knop start/stop server
        self.btn_text = StringVar()
        self.btn_text.set("Stop server")
        self.serverBtn = Button(
            self,
            textvariable=self.btn_text,
            width=20,
            command=self.toggleServer)
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
        # checks if event is linked to which listbox
        if e.widget == self.lstclients:
            selected = self.lstclients.get(ACTIVE)
            if selected:
                client = self.__mc.GetClientByNickname(selected, self.serverId)

                output = self.__CreateOutput(client, 0)

                messagebox.showinfo(client["nickname"], "\n".join(output))
            self.lstclients.selection_clear(0, END)
        elif e.widget == self.lstoffline:
            selected = self.lstoffline.get(ACTIVE)
            if selected:
                client = self.__mc.GetClientByNickname(selected, self.serverId)

                output = self.__CreateOutput(client, 1)

                messagebox.showinfo(client["nickname"], "\n".join(output))
            self.lstoffline.selection_clear(0, END)

    def __CreateOutput(self, client, online):
        output = [
            "Name: %s" % client["name"],
            "Nickname: %s" % client["nickname"],
            "Email: %s" % client["email"],
            "Date login: %s" % client["dateLogin"].strftime("%c")
        ]

        if online:
            output.append(
                "Date logout: %s" % client["dateLogout"].strftime("%c"))
            output.append("Total online time: %s" %
                          (client["dateLogout"] - client["dateLogin"]))

        output.append("Messages sent:")
        output.extend([obj["text"] for obj in client["messages"]])
        return output

    def toggleServer(self):
        if self.server is not None and self.server.statusServer:
            # alert
            self.SendMessageToHandlers("ALT", json.dumps("CHATROOM IS CLOSED"))
            self.server.stopServer()
            self.btn_text.set("Start server")
        else:
            self.initServer()
            self.btn_text.set("Stop server")
