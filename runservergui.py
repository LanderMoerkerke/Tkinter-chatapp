from tkinter import Tk
from server.ServerWindow import ServerWindow

root = Tk()
# root.geometry("800x600")
app = ServerWindow(7000, root)
root.mainloop()
