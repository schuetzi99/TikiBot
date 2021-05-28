try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

import math
from rectbutton import RectButton


class SelectScreen(Frame):
    def __init__(self, master, items, callback=None, labeltext=None, cols=3):
        super(SelectScreen, self).__init__(master)
        self.master = master
        self.bgcolor = master.bgcolor
        self.configure(bg=self.bgcolor)
        self.callback = callback if callback else self.handle_button_select
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

        self.update_buttons(items)

        if callable(getattr(self, "handle_button_new", None)):
            newbtn = RectButton(self.botomframe, text="\u002b", width=40, command=self.handle_button_new)
            newbtn.grid(column=1, row=98, sticky=S+W)
        self.bottomframe = Label(self, fg="red")
        self.bottomframe.grid(row=2, column=0, pady=(3, 0), sticky='se')
        backbtn = RectButton(self.bottomframe, text="\u23ce", width=120, command=self.handle_button_back)
        backbtn.grid(column=3, row=0, sticky='se')
        #self.grid_rowconfigure(97, weight=1)
        #self.grid_rowconfigure(99, minsize=10)

    def update_buttons(self, items, cols=3):
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []
        self.items = items
        rows = math.ceil(len(items)/cols)
        col, row = 0, 0
        for item in items:
            name = item
            icon = None
            state = NORMAL
            fg = None
            bg = None
            cb = None
            compound=CENTER
            if type(item) is dict:
                name = item['name']
                icon = item.get('icon', None)
                state = DISABLED if item.get('disabled', False) else NORMAL
                fg = item.get('fgcolor', None)
                bg = item.get('bgcolor', None)
                cb = item.get('callback', None)
                compound = item.get('compound', CENTER)
            targ_col = 1 + col
            targ_row = 1 + row
            if not icon:
                icon = ""
            img = self.master.get_image(icon)
            cmd = cb if cb else lambda x=name: self.callback(x)
            btn = Button(self.frame_buttons, text=name, image=img, compound=compound, fg=fg, bg=bg, state=state, command=cmd, height = 80, width = 300)
            btn.grid(column=targ_col, row=targ_row, sticky=N+E+W)
            self.buttons.append(btn)
            col += 1
            if col >= cols:
                row += 1
                col = 0
        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        self.frame_buttons.update_idletasks()

        # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
        #self.first5columns_width = sum([self.buttons[j].winfo_width() for j in range(0, 1)]) * 3
        self.first5columns_width = self.buttons[0].winfo_width() * 3
        self.first5rows_height = (self.buttons[0].winfo_height()*5)
        #self.first10rows_height = sum([self.buttons[i].winfo_height() for i in range(0, 10)])
        self.buttonframe.config(width=self.first5columns_width + self.vsb.winfo_width(),
                    height=self.first5rows_height)
        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


    def handle_button_back(self):
        self.master.screen_pop()

    def handle_button_select(self, item):
        pass


