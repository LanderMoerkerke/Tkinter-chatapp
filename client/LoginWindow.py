import logging
import socket
import json
from bson import json_util

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from tkinter import Toplevel

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
        # self.create_chatwindow()

    def init_window(self):
        self.master.title("Login")
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

    def GetFields(self):
        logging.info("Getting input fields")

        name = self.entry_name.get()
        nickname = self.entry_nickname.get()
        email = self.entry_email.get()

        self.client = Client(name, nickname, email)

        logging.info("Created client from input fields")

    def _login_btn_clicked(self):
        self.GetFields()

        # Checks if nickname is in use
        logging.info("Sending client")
        self.my_writer_obj.write(
            json.dumps(self.client.__dict__, default=json_util.default) + "\n")
        self.my_writer_obj.flush()

        msg = self.my_writer_obj.readline().rstrip('\n')

        while msg[:3] == "CLT":
            msg = self.my_writer_obj.readline().rstrip('\n')

        logging.info("Response nickname received: %s" % msg)

        if msg == "clientadded":
            self.create_chatwindow()
        elif msg == "cltfailed":
            logging.info("Nickname in use")
            messagebox.showinfo(
                "Nickname",
                "Nickname is already in use. Choose a different nickname.")
            # nickname is in use, wait for the user to press the button again

    def create_chatwindow(self):
        t = Toplevel(self)
        from client.ChatWindow import ChatWindow
        self.child = ChatWindow(self.__port, self.s, self.my_writer_obj, t)
        # t.wm_title("Chatwindow)
        # l = tk.Label(t, text="This is window #%s" % self.counter)
        # l.pack(side="top", fill="both", expand=True, padx=100, pady=100)

    def close_connection(self):
        try:
            logging.info("Close connection with server...")
            self.my_writer_obj.write("%s\n" % "CLOSE")
            self.my_writer_obj.flush()
            self.s.close()
        except Exception as ex:
            logging.error("Foutmelding: Close connection with server failed")


def main():
    root = Tk()
    # root.geometry("800x800")
    app = LoginWindow(7000, root)
    root.mainloop()


if __name__ == '__main__':
    main()
