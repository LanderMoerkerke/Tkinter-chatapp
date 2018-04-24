import logging
import socket

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from model.Client import Client

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,
    format=
    "%(asctime)s\t%(levelname)s--%(processName)s %(filename)s:%(lineno)s--%(message)s"
)


class LoginWindow(Frame):
    def __init__(self, port, master=None):
        super().__init__(master)

        self.master = master
        self.__port = port

        self.init_window()
        self.makeConnnectionWithServer()

    def init_window(self):
        self.label_name = Label(self, text="Name")
        self.label_nickname = Label(self, text="Nickname")
        self.label_email = Label(self, text="Email")

        self.entry_name = Entry(self)
        self.entry_nickname = Entry(self)
        self.entry_email = Entry(self)

        self.label_name.grid(row=0, sticky=E)
        self.label_nickname.grid(row=1, sticky=E)
        self.label_email.grid(row=2, sticky=E)

        self.entry_name.grid(row=0, column=1)
        self.entry_nickname.grid(row=1, column=1)
        self.entry_email.grid(row=2, column=1)

        self.logbtn = Button(
            self, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)

        self.pack()

    def _login_btn_clicked(self):
        name = self.entry_name.get()
        nickname = self.entry_nickname.get()
        email = self.entry_email.get()

        self.client = Client(name, nickname, email)

        # Check if nickname is in use

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
            messagebox.showinfo("Something has gone wrong...")
            # self.__del__()

    def close_connection(self):
        try:
            logging.info("Close connection with server...")
            self.my_writer_obj.write("%s\n" % "CLOSE")
            self.my_writer_obj.flush()
            self.s.close()
        except Exception as ex:
            logging.error("Foutmelding: Close connection with server failed")


root = Tk()
# root.geometry("800x800")
app = LoginWindow(7000, root)
root.mainloop()
