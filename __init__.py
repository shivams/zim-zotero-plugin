# -*- coding: utf-8 -*-
#
# Copyright: 2017 Shivam Sharma <grahamrow@gmail.com>
# License: GNU GPL v2 or higher
#
# Uses API code from Zotero's OpenOffice plugin to insert
# reference links that open in Zotero.


import gtk
from zim.plugins import PluginClass, extends, WindowExtension
from zim.errors import Error
from zim.actions import action
from zim.applications import Application, ApplicationError
from zim.gui.widgets import Dialog, Button, InputEntry, ScrolledWindow
import json
import urllib2
# import requests


class ZoteroPlugin(PluginClass):

    plugin_info = {
        'name': _('Zotero Citations'), # T: plugin name
        'description': _('Zotero is a free cross-platform desktop reference and paper management program (http://www.zotero.org/).'
                         'This plugin allows you to insert Zotero citations that link directly to the Zotero desktop application.'
                         'You need to install the "zotxt" plugin in Zotero application, and the Zotero application must be running'
                         ' for this plugin to function.'), # T: plugin description
        'author': 'Shivam Sharma',
        'help': 'Plugins:Zotero Citations',
    }


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

    @action(_('_Citation...'), '', '<Shift><Primary>I') # T: menu item
    def insert_citation(self):
        '''Action called by the menu item or key binding,
        '''
        ZoteroDialog(self.window, self.window.pageview).run()


class ZoteroDialog(Dialog):

    def __init__(self, ui, pageview):
        Dialog.__init__(self, ui, _('Search in Zotero'), # T: Dialog title
                        button=(_('_GO'), 'gtk-ok'),  # T: Button label
                        defaultwindowsize=(350, 200) )

        self.pageview = pageview
        self.textentry = InputEntry()
        self.vbox.pack_start(self.textentry, False)
        first = None
        for text in ["Search in Title, Author and Date","Search in All Fields and Tags","Search Everywhere"]:
            self.radio = gtk.RadioButton( first, text)
            if not first:
                first = self.radio
            self.vbox.pack_start( self.radio, expand=False)
            self.radio.show()

    def run(self):
        Dialog.run(self)

    def do_response_ok(self):
        text = self.textentry.get_text()
        buffer = self.pageview.view.get_buffer()
        active = [r for r in self.radio.get_group() if r.get_active()] #@+
        radiotext = active[0].get_label() #@+
        self.insert_citation(text, radiotext, buffer)
        return True

    def insert_citation(self, text, radiotext, buffer):
        root = "127.0.0.1:23119/zotxt"
        method = '' #Method defaults to titleCreatorYear
        if "Tags" in radiotext:
            method = '&method=fields'
        elif "Everywhere" in radiotext:
            method = '&method=everything'
        url = 'http://' + root + '/search?q=' + text + method
        try:
            # resp = requests.get(url).json()
            resp = json.loads(urllib2.urlopen(url).read())
            refs = []
            for i in resp:
                key = '0_' + i['id'].split('/')[-1]
                #Sometimes, articles may have missing fields, so they can be skipped
                try:
                    href =  'zotero://' + root + '/select?key=' + key
                    title = i['title']
                    refs.append({'title': title, 'href': href})
                    buffer.insert_link_at_cursor(title, href=href)
                    buffer.insert_at_cursor("\n")
                except:
                    pass
        except:
            pass
