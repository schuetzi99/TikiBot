try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

from recipes import Recipe, OZ
from rectbutton import RectButton
from dispensing_screen import DispensingScreen


class PourScreen(Frame):
    def __init__(self, master, recipe):
        super(PourScreen, self).__init__(master, class_="Pour")
        self.master = master
        self.recipe = recipe
        self.pouricon = self.master.get_image("PourIcon.gif")
        self.desc = Text(self, width=32, state=DISABLED)
        lbl = Label(self, text="Amount to dispense:")
        upbtn = RectButton(self, text="+", width=120, repeatdelay=500, repeatinterval=100, command=self.handle_button_up)
        self.selbtn = Button(self, text="\nPour\n6 oz", image=self.pouricon, compound=CENTER, width=120, height=160, command=self.handle_button_sel)
        dnbtn = RectButton(self, text="−", width=120, repeatdelay=500, repeatinterval=100, command=self.handle_button_dn)
        backbtn = RectButton(self, text="\u23ce", width=120, command=self.handle_button_back)

        self.desc.grid(column=1, row=1, rowspan=7, sticky=N+S+E+W)
        lbl.grid(column=3, row=1, sticky=N)
        upbtn.grid(column=3, row=3, sticky=S)
        self.selbtn.grid(column=3, row=4, pady=5, sticky=N+S)
        dnbtn.grid(column=3, row=5, sticky=N)
        backbtn.grid(column=3, row=7, sticky=S)

        self.grid_columnconfigure(0, minsize=20)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, minsize=20)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, minsize=20)
        self.grid_rowconfigure(0, minsize=20)
        self.grid_rowconfigure(2, minsize=20)
        self.grid_rowconfigure(6, minsize=40)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, minsize=20)

        self.set_amount(6)

    def get_amount(self):
        return int(self.selbtn.cget('text').split()[1])

    def set_amount(self, val):
        self.selbtn.config(text="\nPour\n%d oz" % val)
        self.update_recipe_desc()

    def update_recipe_desc(self):
        vol = self.get_amount()
        partial = vol * OZ / self.recipe.totalVolume()
        self.desc.config(state=NORMAL)
        self.desc.delete(1.0, END)
        self.desc.tag_config("recipe", lmargin1=3, rmargin=3, spacing1=2, spacing3=2, background="#077", foreground="white")
        self.desc.insert(END, "%s\n" % self.recipe.getName(), "recipe")
        for ing in self.recipe.ingredients:
            self.desc.insert(END, "%s\n" % ing.readableDesc(partial))
        self.desc.config(state=DISABLED)
        self.master.update()

    def handle_button_up(self):
        val = self.get_amount()
        if val < 16:
            val += 1
        self.set_amount(val)

    def handle_button_dn(self):
        val = self.get_amount()
        if val > 1:
            val -= 1
        self.set_amount(val)

    def handle_button_sel(self):
        vol = self.get_amount() * OZ
        self.master.screen_push(DispensingScreen(self.master, self.recipe, vol))

    def handle_button_back(self):
        self.master.screen_pop()

