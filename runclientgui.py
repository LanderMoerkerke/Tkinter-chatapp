from tkinter import Tk
from client.LoginWindow import LoginWindow

root = Tk()
root.geometry("800x600")
app = LoginWindow(7000, root)
root.mainloop()
