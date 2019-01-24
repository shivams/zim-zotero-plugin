# -*- coding: utf-8 -*-
#
# Copyright: 2017 Shivam Sharma <shivam.src@gmail.com>
# License: GNU GPL v2 or higher


import gtk
from zim.plugins import PluginClass, extends, WindowExtension
from zim.errors import Error
from zim.actions import action
from zim.applications import Application, ApplicationError
from zim.gui.widgets import Dialog, Button, InputEntry, ScrolledWindow
import json
import urllib2


class ZoteroPlugin(PluginClass):
    """plugin info for zim."""

    plugin_info = {
        'name': _('Zotero Citations modified'),
        'description': _('Zotero is a free cross-platform desktop reference and paper management program (http://www.zotero.org/).'
                         'This plugin allows you to insert Zotero citations that link directly to the Zotero desktop application.'
                         'You need to install the "zotxt" plugin in Zotero application, and the Zotero application must be running'
                         ' for this plugin to function.'),
        'author': 'Shivam Sharma',
        'help': 'Plugins:Zotero Citations',
    }

    def zotero_handle(self, link):
        """Handle Zotero links of the form zotero://."""
        url = link.replace('zotero', 'http')
        try:
            if "success" in urllib2.urlopen(url).read().lower():
                return True
            else:
                return False
        except:
            return False

    plugin_preferences = (
        ('bibliography_style', 'choice', _('Bibliography Style'),
         'betterbibtexkey',
         ('betterbibtexkey', 'easykey', 'key', 'bibliography')),
    )


@extends('MainWindow')
class MainWindowExtension(WindowExtension):

    uimanager_xml = '''
    <ui>
        <menubar name='menubar'>
            <menu action='insert_menu'>
                <placeholder name='plugin_items'>
                    <menuitem action='insert_citation'/>
                </placeholder>
            </menu>
        </menubar>
    </ui>
    '''

    def __init__(self, plugin, window):
        """Window constructor."""
        WindowExtension.__init__(self, plugin, window)
        self.preferences = plugin.preferences
        self.window.ui.register_url_handler('zotero',
                                            self.plugin.zotero_handle)

    @action(_('_Citation...'), '', '<Primary><Alt>I')  # T: menu item
    def insert_citation(self):
        """Will be called by the menu item or key binding."""
        ZoteroDialog(self.window, self.window.pageview, self.preferences).run()


class ZoteroDialog(Dialog):

    def __init__(self, ui, pageview, preferences):
        Dialog.__init__(self, ui, _('Search in Zotero'),  # T: Dialog title
                        button=(_('_GO'), 'gtk-ok'),  # T: Button label
                        defaultwindowsize=(350, 200))

        self.pageview = pageview
        self.textentry = InputEntry()
        self.vbox.pack_start(self.textentry, False)
        self.preferences = preferences
        first = None
        options = ["Search in Title, Author and Date",
                   "Search in All Fields and Tags",
                   "Search Everywhere"]
        for text in options:
            self.radio = gtk.RadioButton(first, text)
            if not first:
                first = self.radio
            self.vbox.pack_start(self.radio, expand=False)
            self.radio.show()

    def run(self):
        Dialog.run(self)

    def do_response_ok(self):
        """Call to insert citation when pressing ok."""
        text = self.textentry.get_text()
        buffer = self.pageview.view.get_buffer()
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
        style = self.preferences['bibliography_style']
        format = '&format=' + style
        url = 'http://' + root + '/search?q=' + text + format + method
        try:
            resp = json.loads(urllib2.urlopen(url).read())
            if style == 'bibliography':
                for i in resp:
                    buffer.insert_at_cursor(i)
                    key = i['key']
                    try:
                        zotlink = 'zotero://' + root + '/select?key=' + key
                        bibtext = i['text']
                        buffer.insert_link_at_cursor(bibtext, href=zotlink)
                        buffer.insert_at_cursor("\n")
                    except:
                        pass
            elif style == 'betterbibtexkey':
                for bbtkey in resp:
                    try:
                        zotlink = ('zotero://' + root +
                                   '/select?betterbibtexkey=' + bbtkey)
                        buffer.insert_link_at_cursor(bbtkey, href=zotlink)
                        buffer.insert_at_cursor("\n")
                    except:
                        pass
            else:
                buffer.insert_at_cursor('style unknown: ' + style + "\n")
        except:
            pass
