try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa


import math
from recipes import Recipe
from rectbutton import RectButton
from recipe_screen import RecipeScreen
from lock_screen import LockScreen
from config_screen import ConfigScreen
from byingredient_screen import ByIngredientScreen
from information_screen import InformationScreen
from manage_remaining_screen import ManageRemainingScreen
from feeds import SupplyFeed


class MainScreen(Frame):
    def __init__(self, master):
        super(MainScreen, self).__init__(master, class_="MainScreen")
        self.master = master
        self.bgcolor = master.bgcolor
        self.buttons = []
        self.update_buttons()
        self.configure(bg=self.bgcolor)
        
        
    def update_buttons(self):
        for btn in self.buttons:
            btn.forget()
            btn.destroy()
        types = Recipe.getTypeNames()
        colsarr = [1, 2, 3, 2, 3, 3, 4, 4, 5, 5]
        maxcols = colsarr[len(types)]
        col, row = 1, 1
        leer_bg = SupplyFeed.areFeedsEmpty()
        for type_ in types:
            img = self.master.get_image(Recipe.getTypeIcon(type_))
            cmd = lambda typ=type_: self.handle_type_button(typ)
            btn = Button(self, text=type_, compound=TOP, image=img, command=cmd, width=160)
            btn.grid(column=col, row=row, padx=5, pady=5)
            self.buttons.append(btn)
            col += 1
            if col > maxcols:
                col = 1
                row += 1
                self.rowconfigure(row, weight=0)
        img = self.master.get_image("nachZutatenIcon.gif")
        btn = Button(self, text="nach Zutaten", compound=TOP, image=img, command=self.handle_button_ingredients, width=160)
        btn.grid(column=col, row=row, padx=5, pady=5)
        self.buttons.append(btn)
        img2 = self.master.get_image("InformationIcon.gif")
        btn2 = Button(self, text="Info", compound=TOP, image=img2, command=self.handle_button_information, width=170)
        btn2.grid(column=col+1, row=row, padx=5, pady=5)
        self.buttons.append(btn2)
        emptybtn = Button(self, text="Zutat leer", command=self.handle_button_empty, bg=leer_bg)
        emptybtn.grid(column=1, row=row+1, sticky=S+W)
        confbtn = RectButton(self, text="\u2699", command=self.handle_button_conf, width=15, height=20)
        confbtn.grid(column=maxcols, row=row, columnspan=2, rowspan=2, sticky=S+E)
        self.buttons.append(confbtn)
        self.columnconfigure(0, weight=1)
        for col in range(maxcols):
            self.columnconfigure(col+1, weight=0)
        self.columnconfigure(maxcols+1, weight=1)
        self.columnconfigure(maxcols+2, weight=0)
        self.columnconfigure(maxcols+3, weight=0)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(row+1, weight=1)
        self.rowconfigure(row+2, weight=0)
        self.rowconfigure(row+3, weight=0)

    def activate(self):
        self.update_buttons()

    def handle_type_button(self, type_):
        recipes = Recipe.getRecipesByType(type_)
        self.master.screen_push(RecipeScreen(self.master, recipes, "Wähle aus der Kategorie %s:" % type_))

    def handle_button_ingredients(self):
        self.master.screen_push(ByIngredientScreen(self.master))

    def handle_button_information(self):
        self.master.screen_push(InformationScreen(self.master))

    def handle_button_conf(self):
        self.master.screen_push(LockScreen(self.master, ConfigScreen(self.master)))
        
    def handle_button_empty(self):
        self.master.screen_push(ManageRemainingScreen(self.master))


