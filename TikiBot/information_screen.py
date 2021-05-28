try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

from rectbutton import RectButton


class InformationScreen(Frame):
    def __init__(self, master, callback=None, labeltext='Information', cols=1):
        super(InformationScreen, self).__init__(master)
        self.master = master
        self.bgcolor = master.bgcolor
        self.configure(bg=self.bgcolor)
        self.callback = callback # if callback else self.handle_button_select
        self.buttons = []
        if labeltext:
            self.upperframe = Label(self, text=labeltext, fg="green")
            self.upperframe.grid(row=0, column=0, pady=(5, 0), sticky='nw')
            
        self.buttonframe = Frame(self)
        self.buttonframe.grid(row=1, column=0, pady=(5, 0), sticky='nw')
        self.buttonframe.grid_rowconfigure(0, weight=1)
        self.buttonframe.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        self.buttonframe.grid_propagate(False)

        # Add a canvas in that frame
        self.canvas = Canvas(self.buttonframe, bg=self.bgcolor)
        self.canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        self.vsb = Scrollbar(self.buttonframe, orient="vertical", command=self.canvas.yview, width=40, troughcolor="#98B17C", bg="#F6E70A", activebackground="#FFFC74")
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Create a frame to contain the buttons
        self.frame_buttons = Frame(self.canvas, bg=self.bgcolor)
        self.canvas.create_window((0, 0), window=self.frame_buttons, anchor='nw')

        self.update_buttons()

        if callable(getattr(self, "handle_button_new", None)):
            newbtn = RectButton(self.botomframe, text="\u002b", width=40, command=self.handle_button_new)
            newbtn.grid(column=1, row=98, sticky=S+W)
        self.bottomframe = Label(self, fg="red")
        self.bottomframe.grid(row=2, column=0, pady=(3, 0), sticky='se')
        backbtn = RectButton(self.bottomframe, text="\u23ce", width=120, command=self.handle_button_back)
        backbtn.grid(column=3, row=0, sticky='se')
        #self.grid_rowconfigure(97, weight=1)
        #self.grid_rowconfigure(99, minsize=10)

    def update_buttons(self, cols=1):
        # INHALT
        quote_info = """Diesen Cocktail-Automat kannst Du mieten.
Alle Infos unter:

    www.let-him-mix.de

oder einfach QR-Code scannen, und Kontakt speichern.

  Kontakt Dornstadt                                         Kontakt Zwickau"""
        
        qrcharles = self.master.get_image("qr-charles.png")
        qrjames = self.master.get_image("qr-james.png")

        text_height=quote_info.count('\n')+1
        Txt1 = Text(self.frame_buttons, height=text_height, width=72)
        Txt1.pack()
        Txt1.insert(END, quote_info)
        
        Txt2 = Text(self.frame_buttons, height=10, width=36)
        Txt2.pack()
        Txt2.insert(END, '\n')
        Txt2.image_create(END, image=qrcharles)
        Txt2.pack(side=LEFT)

        Txt3 = Text(self.frame_buttons, height=10, width=36)
        Txt3.pack()
        Txt3.insert(END, '\n')
        Txt3.image_create(END, image=qrjames)
        Txt3.pack(side=RIGHT)

        self.frame_buttons.update_idletasks()
        
        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        self.first5columns_width = 950 #self.buttons[0].winfo_width() * 3
        self.first5rows_height = 500 #(self.buttons[0].winfo_height()*5)
        self.buttonframe.config(width=self.first5columns_width + self.vsb.winfo_width(),
                    height=self.first5rows_height)
        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


    def handle_button_back(self):
        self.master.screen_pop()

