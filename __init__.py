# -*- coding: utf-8 -*-
#
# Copyright: 2017 Shivam Sharma <shivam.src@gmail.com>
# License: GNU GPL v2 or higher


from gi.repository import Gtk
from zim.plugins import PluginClass
from zim.gui.pageview import PageViewExtension
from zim.actions import action
from zim.gui.widgets import Dialog, InputEntry
import json
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


class ZoteroPlugin(PluginClass):
    """plugin info for zim."""

    plugin_info = {
        'name': _('Zotero Citations'),
        'description': _('Zotero is a free cross-platform desktop reference and paper management program (http://www.zotero.org/).'
                         'This plugin allows you to insert Zotero citations that link directly to the Zotero desktop application.'
                         'You need to install the "zotxt" plugin in Zotero application, and the Zotero application must be running'
                         ' for this plugin to function.'),
        'authors': 'Shivam Sharma',
        'help': 'Plugins:Zotero Citations',
    }

    # def zotero_handle(self, link):
    #     """Handle Zotero links of the form zotero://."""
    #     url = link.replace('zotero', 'http')
    #     try:
    #         if "success" in urlopen(url).read().lower():
    #             return True
    #         else:
    #             return False
    #     except:
    #         return False

    plugin_preferences = (
        ('link_format', 'choice', _('Link Format'),
         'betterbibtexkey',
         ('betterbibtexkey', 'easykey', 'key', 'bibliography')),
    )


class ZoteroPageViewExtension(PageViewExtension):
    """Define the input window."""

    def __init__(self, plugin, pageview):
        """Window constructor."""
        PageViewExtension.__init__(self, plugin, pageview)
        self.preferences = plugin.preferences

    @action(_('_Citation...'), accelerator='<Primary><Alt>I', menuhints='notebook')  # T: menu item
    def insert_citation(self):
        """Will be called by the menu item or key binding."""
        dialog = ZoteroDialog.unique(self, self.pageview, self.preferences)
        dialog.show_all()


class ZoteroDialog(Dialog):
    """The Zotero specific Input Dialog."""

    def __init__(self, pageview, preferences):
        """Initialize the Input Box with options."""
        Dialog.__init__(self, pageview, _('Search in Zotero'),  # T: Dialog title
                        button=_('_GO'),  # T: Button label
                        defaultwindowsize=(350, 200))

        self.pageview = pageview
        self.textentry = InputEntry()
        self.vbox.pack_start(self.textentry, False, True, 0)
        self.preferences = preferences
        first = None
        options = ["Search in Title, Author and Date",
                   "Search in All Fields and Tags",
                   "Search Everywhere"]
        for text in options:
            self.radio = Gtk.RadioButton(first, text)
            if not first:
                first = self.radio
            self.vbox.pack_start(self.radio, False, True, 0)
            self.radio.show()

    def run(self):
        """Call the widget.dialog.run method."""
        Dialog.run(self)

    def do_response_ok(self):
        """Call to insert citation when pressing ok."""
        text = self.textentry.get_text()
        buffer = self.pageview.textview.get_buffer()
        active = [r for r in self.radio.get_group() if r.get_active()]  # @+
        radiotext = active[0].get_label()  # @+
        self.insert_citation(text, radiotext, buffer)
        return True

    def insert_citation(self, text, radiotext, buffer):
        """Will insert the whole bibliography text."""
        root = "127.0.0.1:23119/zotxt"
        method = ''  # Method defaults to titleCreatorYear
        if "Tags" in radiotext:
            method = '&method=fields'
        elif "Everywhere" in radiotext:
            method = '&method=everything'
        link_format = self.preferences['link_format']
        format = '&format=' + link_format
        url = 'http://' + root + '/search?q=' + text + format + method
        try:
            resp = json.loads(urlopen(url).read())
            if link_format == 'bibliography':
                for i in resp:
                    key = i['key']
                    try:
                        zotlink = 'zotero://' + root + '/select?key=' + key
                        bibtext = i['text']
                        buffer.insert_link_at_cursor(bibtext, href=zotlink)
                        buffer.insert_at_cursor("\n")
                    except:
                        pass
            elif link_format == 'betterbibtexkey':
                for key in resp:
                    try:
                        zotlink = ('zotero://' + root +
                                   '/select?betterbibtexkey=' + key)
                        buffer.insert_link_at_cursor(key, href=zotlink)
                        buffer.insert_at_cursor("\n")
                    except:
                        pass
            elif link_format == 'easykey':
                for key in resp:
                    try:
                        zotlink = ('zotero://' + root +
                                   '/select?easykey=' + key)
                        buffer.insert_link_at_cursor(key, href=zotlink)
                        buffer.insert_at_cursor("\n")
                    except:
                        pass
            elif link_format == 'key':
                for key in resp:
                    try:
                        zotlink = ('zotero://' + root +
                                   '/select?key=' + key)
                        buffer.insert_link_at_cursor(key, href=zotlink)
                        buffer.insert_at_cursor("\n")
                    except:
                        pass
            else:
                buffer.insert_at_cursor('link format unknown: ' + link_format
                                        + "\n")
        except:
            pass
