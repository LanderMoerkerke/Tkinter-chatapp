import socket
import logging
from threading import Thread

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from Week_5.server.Server import Server
from Week_5.model.Classes import BrakingDistance, RoadCondition

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s--%(processName)s %(filename)s:%(lineno)s--%(message)s")

class ServerWindow(Frame):
    def __init__(self, port=7000, master=None, message_queue=None):
        Frame.__init__(self, master)
        # Thread.__init__(self)
        self.master = master
        self.initWindow()

        self.server = Server(socket.gethostname(), port, message_queue)
        self.toggleServer()
        self.__port = port
        self.__message_queue = message_queue

    def initWindow(self):
        logging.info("Creating server window...")
        self.master.title("Server")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Log-berichten server:").grid(row=0)
        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.lstnumbers = Listbox(self, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.lstnumbers.yview)

        self.lstnumbers.grid(row=1, column=0, sticky=N + S + E + W)
        self.scrollbar.grid(row=1, column=1, sticky=N + S)

        self.btn_text = StringVar()
        self.btn_text.set("Start server")
        self.buttonServer = Button(self, textvariable=self.btn_text, command=self.toggleServer)
        self.buttonServer.grid(row=3, column=0, columnspan=2, pady=(5, 5), padx=(5, 5), sticky=N + S + E + W)

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