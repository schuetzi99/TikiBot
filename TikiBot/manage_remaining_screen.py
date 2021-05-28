try:  # Python 2
    from Tkinter import *  # noqa
except ImportError:  # Python 3
    from tkinter import *  # noqa

import math
import operator
from feeds import SupplyFeed
from recipes import Recipe
from select_screen import SelectScreen
from alpha_screen import AlphaScreen
from feed_edit_screen import FeedEditScreen
from list_screen import ListScreen
from notify_screen import NotifyScreen
from touch_checkbox import TouchCheckbox
from touch_spinner import TouchSpinner
from exportpdf import ExportPdf


class ManageRemainingScreen(ListScreen):
    def __init__(self, master):
        super(ManageRemainingScreen, self).__init__(
            master,
            self._get_items,
            label_text="Flascheninhalt bearbeiten:",
            rem_sp=self.item_remaining,
            ep_cb=self.exportpdf,
        )
        self.bgcolor = master.bgcolor,
        self.configure(bg=self.bgcolor),

    def _get_items(self):
        return [
            {
                "name": "#%d %s, Restinhalt: %d" % (feed.motor_num, feed.getName(), feed.getRemaining()),
                "data": feed,
                "fgcolor": 'red' if feed.remaining <=0 else 'orange' if feed.remaining <=50 else None,
                "bgcolor": 'white' if feed.avail else 'grey',
            }
            for feed in SupplyFeed.getAllOrdered() if feed.motor_num < 24
        ]

    def activate(self):
        self.update_listbox()

    def item_remaining(self, oldval, newval):
        #self.feed = sel_feed
        self.data.remaining = newval

    def exportpdf():
        #recipes=Resipe.getAll()
        self.ExportPdf.exportpdf()

