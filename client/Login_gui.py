import logging
import socket

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s--%(processName)s %(filename)s:%(lineno)s--%(message)s")

class ChatWindow(Frame):
    def __init__(self, port, master=None):
        super().__init__(master)

        self.master = master
        self.__port = port

        self.init_window()
        self.makeConnnectionWithServer()

    def init_window(self):
        self.label_nickname = Label(self, text="Nickname")
        self.label_password = Label(self, text="Password")

        self.entry_nickname = Entry(self)
        self.entry_password = Entry(self, show="*")

        self.label_nickname.grid(row=0, sticky=E)
        self.label_password.grid(row=1, sticky=E)
        self.entry_nickname.grid(row=0, column=1)
        self.entry_password.grid(row=1, column=1)

        self.checkbox = Checkbutton(self, text="Keep me logged in")
        self.checkbox.grid(columnspan=2)

        self.logbtn = Button(self, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)

        self.pack()

    def _login_btn_clicked(self):
        # print("Clicked")
        nickname = self.entry_nickname.get()
        password = self.entry_password.get()

        # print(username, password)

        # if username == "john" and password == "password":
        #     tm.showinfo("Login info", "Welcome John")
        # else:
        #     tm.showerror("Login error", "Incorrect username")

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


# import logging
# from tkinter import Tk
# from Week_5.client.Client_gui import ClientWindow
# logging.basicConfig(level=logging.INFO)


root = Tk()
app = ChatWindow(7000, root)
root.mainloop()
