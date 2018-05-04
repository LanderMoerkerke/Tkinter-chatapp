import socket
import logging
import json
from threading import Thread

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from bson import json_util

from model.Client import Client
from model.Message import Message

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    level=logging.DEBUG,
    format=
    "%(asctime)s\t%(levelname)s--%(processName)s %(filename)s:%(lineno)s--%(message)s"
)


class ChatWindow(Frame):
    def __init__(self, port, clientsocket, writerobj, master=None):
        super().__init__(master)

        self.master = master
        self.__port = 7000
        self.my_writer_obj = writerobj

        self.init_chat()

        t = Thread(target=self.readStreamWriter)
        t.start()

        # testen
        # self.makeConnnectionWithServer()
        # self.client = Client("Lander", "JF", "blabla")
        # self.my_writer_obj.write(
        #     json.dumps(self.client.__dict__, default=json_util.default) + "\n")
        # self.my_writer_obj.flush()

        # self.clientsocket = clientsocket
        # self.my_writer_obj = self.clientsocket.makefile(mode='rw')

    def init_chat(self):
        logging.info("Creating client window...")
        # changing the title of our master widget
        self.master.title("Chat Window")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # Declaration
        # Left side
        Label(self, text="Online:", padx=5).grid(row=0, column=0, sticky=W)
        self.scrollbarnn = Scrollbar(self, orient=VERTICAL)
        self.lstClients = Listbox(self, yscrollcommand=self.scrollbarnn.set)

        # Right side
        Label(self, text="Chat:", pady=5).grid(row=0, column=2, sticky=W)
        self.scrollbarchat = Scrollbar(self, orient=VERTICAL)
        self.lstChat = Listbox(self, yscrollcommand=self.scrollbarchat.set)

        # Bottom
        self.entChat = Entry(self, width=40)

        # Grid SETUP
        # Left side
        self.lstClients.grid(
            row=1,
            column=0,
            rowspan=2,
            pady=(0, 7),
            padx=(5, 0),
            sticky=N + S + W)
        self.scrollbarnn.grid(
            row=1, column=1, rowspan=2, pady=(0, 7), sticky=N + S + W)

        # Right side
        self.lstChat.grid(row=1, column=2, columnspan=2, sticky=N + S + E + W)
        self.scrollbarchat.grid(
            row=1, column=4, padx=(0, 0), sticky=N + W + E + S)

        # Bottom
        self.entChat.grid(row=2, column=2, sticky=E + W)

        self.btnSendMessage = Button(
            self, text="Send", command=self.sendMessage)
        self.btnSendMessage.grid(
            row=2,
            column=3,
            columnspan=2,
            pady=(5, 5),
            padx=(5, 5),
            sticky=N + S + E + W)

        Grid.rowconfigure(self, 3, weight=1)
        Grid.columnconfigure(self, 5, weight=1)
        logging.info("Clientwindow created")

    def __del__(self):
        self.close_connection()

    def sendMessage(self):
        try:
            logging.info("Button send pressed")
            message = Message(self.entChat.get())

            self.my_writer_obj.write(
                json.dumps(message.__dict__, default=json_util.default) + "\n")
            self.my_writer_obj.flush()

            logging.info('Message sent "%s"' % message.text)
            self.entChat.delete(0, END)

        except Exception as ex:
            logging.error("Foutmelding: %s" % ex)
            messagebox.showinfo("Error", "Failed sending message")
            logging.error(ex)
            raise ex
            # self.__del__()

    def readStreamWriter(self):
        try:
            while True:
                # Verder uitwerken voor andere commando's
                # berichten ontvangen van andere mensen en printen in lstChats
                msg = self.my_writer_obj.readline().rstrip('\n')
                logging.info("Read stream writer found a message: %s" % msg)

                command = msg[:3]
                print(msg[3:])
                obj = json.loads(msg[3:], object_hook=json_util.object_hook)
                print(obj)
                # kunnen onderscheid maken tussen message object en lijst online clients
                if command == "MSG":
                    logging.info("Command MSG triggered")
                    message = obj[0]
                    nickname = obj[1]
                    self.lstChat.insert(END, "%s: %s" % (nickname,
                                                         message["text"]))
                elif command == "CLT":
                    logging.info("Command CLT triggered")
                    self.printOnlineNicknames(obj)
        except Exception as ex:
            logging.error(ex)

    def printOnlineNicknames(self, lstNicknames):
        self.lstClients.delete(0, END)

        for nn in lstNicknames:
            print(nn)
            self.lstClients.insert(END, nn["nickname"])

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
    # root.geometry("800x600")
    app = ChatWindow(7000, None, root)
    root.mainloop()


if __name__ == '__main__':
    main()
