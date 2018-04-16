class Message():
    def __init__(self, text, **args):
        import datetime

        self.dateSent = datetime.datetime.now()
        self.text = text

    def __str__(self):
        print()
        print(self.text)
        return "{0} - {1}".format(self.dateSent.strftime("%H:%M:%S"), self.text)
