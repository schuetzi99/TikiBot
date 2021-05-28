try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

from rectbutton import RectButton
from manage_feeds_screen import ManageFeedsScreen
from manage_recipes_screen import ManageRecipesScreen
from dump_screen import DumpScreen
from lock_screen import LockScreen
from notify_screen import NotifyScreen
from shutdown_screen import ShutdownScreen
from touch_checkbox import TouchCheckbox
from clean_screen import CleanScreen


class ConfigScreen(Frame):
    def __init__(self, master):
        super(ConfigScreen, self).__init__(master)
        self.use_metric = IntVar()
        self.use_metric.set(1 if self.master.use_metric else 0)
        feedsbtn = RectButton(self, text="Zutaten ändern", command=self.handle_button_feeds)
        recipesbtn = RectButton(self, text="Rezepte ändern", command=self.handle_button_recipes)
        fillbtn = RectButton(self, text="Fülle alle Schläuche", command=self.handle_button_fill)
        emptybtn = RectButton(self, text="Leere alle Schläuche", command=self.handle_button_empty)
        cleanbtn = RectButton(self, text="Spüle alle Pumpen", command=self.handle_button_clean)
        unitbtn = TouchCheckbox(self, text="Metrische Einheiten", variable=self.use_metric, command=self.handle_button_metric)
        chpassbtn = RectButton(self, text="Passcode ändern", command=self.handle_button_chpass)
        shutdownbtn = RectButton(self, text="Shutdown", command=self.handle_button_shutdown)
        backbtn = RectButton(self, text="\u23ce", width=120, command=self.handle_button_back)
        feedsbtn.grid(column=1, row=1, padx=20, pady=10, sticky=N+E+W)
        recipesbtn.grid(column=1, row=2, padx=20, pady=10, sticky=N+E+W)
        emptybtn.grid(column=1, row=3, padx=20, pady=10, sticky=N+E+W)
        unitbtn.grid(column=1, row=4, padx=20, pady=10, sticky=N+W)
        chpassbtn.grid(column=2, row=1, padx=20, pady=10, sticky=N+E+W)
        shutdownbtn.grid(column=2, row=2, padx=20, pady=10, sticky=N+E+W)
        cleanbtn.grid(column=2, row=3, padx=20, pady=10, sticky=N+E+W)
        fillbtn.grid(column=2, row=4, padx=20, pady=10, sticky=N+E+W)
        backbtn.grid(column=3, row=9, padx=20, pady=10, sticky=S+E)
        self.columnconfigure(0, minsize=20)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(4, minsize=20)
        self.rowconfigure(0, minsize=10)
        self.rowconfigure(8, weight=1)
        self.rowconfigure(9, minsize=10)
        self.bgcolor = master.bgcolor
        self.configure(bg=self.bgcolor)
        self.amount = -20
        self.turns = 2

    def handle_button_feeds(self):
        self.master.screen_push(ManageFeedsScreen(self.master))

    def handle_button_recipes(self):
        self.master.screen_push(ManageRecipesScreen(self.master))

    def handle_button_dump(self):
        self.master.screen_push(DumpScreen(self.master))

    def handle_button_clean(self):
        self.amount = 30
        self.turns = 5
        self.pumpcount = 1
        self.master.screen_push(CleanScreen(self.master, self.amount, self.turns, self.pumpcount))

    def handle_button_fill(self):
        self.amount = 30
        self.turns = 1
        self.pumpcount = 4
        self.master.screen_push(CleanScreen(self.master, self.amount, self.turns, self.pumpcount))

    def handle_button_empty(self):
        self.amount = -30
        self.turns = 1
        self.pumpcount = 4
        self.master.screen_push(CleanScreen(self.master, self.amount, self.turns, self.pumpcount))

    def handle_button_metric(self):
        self.master.use_metric = self.use_metric.get() != 0
        self.master.save_configs()

    def handle_button_shutdown(self):
        self.master.screen_push(ShutdownScreen(self.master))

    def handle_button_back(self):
        self.master.screen_pop()

    def handle_button_chpass(self):
        self.master.screen_push(LockScreen(self.master, labeltext="Neues Passwort eingeben:", set_pass=self.change_passcode_step1))

    def change_passcode_step1(self, newpass):
        self.newpasscode = newpass
        self.master.screen_pop()
        self.master.screen_push(LockScreen(self.master, labeltext="Neues Passwort bestätigen:", set_pass=self.change_passcode_step2))

    def change_passcode_step2(self, newpass):
        if newpass == self.newpasscode:
            self.master.set_passcode(newpass)
            self.master.save_configs()
            self.master.screen_pop()
        else:
            self.master.screen_pop()
            self.handle_button_chpass()
            self.master.screen_push(NotifyScreen(self.master, "Passcodes didn't match!"))


