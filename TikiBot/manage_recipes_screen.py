try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

import math
import operator
from recipes import Recipe, type_icons
from select_screen import SelectScreen
from alpha_screen import AlphaScreen
from recipe_edit_screen import RecipeEditScreen
from list_screen import ListScreen


class ManageRecipesScreen(ListScreen):
    def __init__(self, master):
        super(ManageRecipesScreen, self).__init__(
            master,
            self._get_items,
            label_text="Ein Rezept zum bearbeiten auswählen:",
            add_cb=self.item_add,
            del_cb=self.item_del,
            edit_cb=self.item_edit,
        )
        self.bgcolor = master.bgcolor
        self.configure(bg=self.bgcolor)

    def _get_items(self):
        return [
            {
                "name": recipe.getName(),
                "data": recipe,
            }
            for recipe in sorted(Recipe.getAll(), key=operator.attrgetter('name'))
        ]

    def activate(self):
        self.update_listbox()

    def item_add(self):
        try:
            for n in range(99):
                name = "Rezept %d" % (n+1)
                Recipe.getByName(name)
        except KeyError:
            pass
        self.master.screen_push(AlphaScreen(self.master, label="Name für neues Rezept:", defval=name, callback=self._item_add_finish))

    def _item_add_finish(self, name):
        for typ in type_icons.keys():
            break
        recipe = Recipe(master, typ, name, mixit)
        self.master.save_configs()
        self.update_listbox()
        self.master.screen_pop()
        self.master.screen_push(RecipeEditScreen(self.master, recipe))

    def item_del(self, idx, txt, recipe):
        self.sel_recipe = recipe
        self.master.screen_push(SelectScreen(self.master, ["Bestätigen"], labeltext='Lösche das Rezept "%s"?' % txt, callback=self._item_del_finish))

    def _item_del_finish(self, confirm):
        if confirm == "Confirm":
            self.sel_recipe.delete_recipe()
            self.master.save_configs()
        self.master.screen_pop()

    def item_edit(self, idx, txt, recipe):
        self.master.screen_push(RecipeEditScreen(self.master, recipe))

