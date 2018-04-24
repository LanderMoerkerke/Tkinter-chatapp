"""Herwerken Oef5 van Week_4: GUI Clientside."""
import socket
import logging
import ujson
from enum import Enum
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from Week_5.model.Classes import BrakingDistance, RoadCondition

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,
    format=
    "%(asctime)s\t%(levelname)s--%(processName)s %(filename)s:%(lineno)s--%(message)s"
)


class ChatWindow(Frame):
    def __init__(self, port, master=None):
        super().__init__(master)

        self.master = master
        self.__port = port

        self.init_chat()
        self.makeConnnectionWithServer()

    def init_chat(self):
        logging.info("Creating client window...")
        # changing the title of our master widget
        self.master.title("Chatapp")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Speed (km/u):").grid(row=0)
        Label(self, text="Reaction time (sec):", pady=10).grid(row=1)
        Label(self, text="Type road:", pady=10).grid(row=2)

        self.entSpeed = Entry(self, width=40)
        self.entReaction = Entry(self, width=40)
        self.cboRoad = Combobox(self, width=40)

        self.entSpeed.grid(row=0, column=1, sticky=E + W, pady=(5, 5))
        self.entReaction.grid(row=1, column=1, sticky=E + W)
        self.cboRoad.grid(row=2, column=1, sticky=E + W)

        self.cboRoad["values"] = ["Wet surface", "Dry surface"]

        Label(self, text="km/u").grid(row=0, column=2)
        Label(self, text="sec", pady=10).grid(row=1, column=2)

        self.buttonCalculate = Button(
            self, text="Calculate brake distance", command=self.Calculate)
        self.buttonCalculate.grid(
            row=3,
            column=0,
            columnspan=3,
            pady=(5, 5),
            padx=(5, 5),
            sticky=N + S + E + W)

        Grid.rowconfigure(self, 3, weight=1)
        Grid.columnconfigure(self, 1, weight=1)
        logging.info("Clientwindow created")

    def makeConnnectionWithServer(self):
        try:
            logging.info("Making connection with server...")
            # get local machine name
            host = socket.gethostname()
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connection to hostname on the port.
            self.s.connect((host, self.__port))
            self.my_writer_obj = self.s.makefile(mode='rw')
            logging.info("Open connection with server succesfully")
        except Exception as ex:
            logging.error("Foutmelding: %s" % str(ex))
            messagebox.showinfo("Stopafstand - foutmelding",
                                "Something has gone wrong...")
            self.__del__()

    def __del__(self):
        self.close_connection()

    def Calculate(self):
        try:
            speed = float(self.entSpeed.get())
            reaction_time = float(self.entReaction.get())
            surface = self.cboRoad.current()

            logging.info("Got value speed: %s" % speed)
            logging.info("Got value reaction time: %s" % reaction_time)
            logging.info("Got index of surface: %s" % surface)

            obj = BrakingDistance(speed, reaction_time, surface)
            self.my_writer_obj.write("%s\n" % ujson.dumps(obj))
            self.my_writer_obj.flush()

            # waiting for answer
            result = float(self.my_writer_obj.readline().rstrip('\n'))

            messagebox.showinfo("Stopafstand",
                                "De stopafstand bedraagt: %.2f" % result)
            # self.label_resultaat['text'] = "{0}".format(result)

        except Exception as ex:
            logging.error("Foutmelding: %s" % ex)
            messagebox.showinfo("Error", "Something has gone wrong...")
            logging.error(ex)
            raise ex
            self.__del__()

    def close_connection(self):
        try:
            logging.info("Close connection with server...")
            self.my_writer_obj.write("%s\n" % "CLOSE")
            self.my_writer_obj.flush()
            self.s.close()
        except Exception as ex:
            logging.error("Foutmelding: Close connection with server failed")
