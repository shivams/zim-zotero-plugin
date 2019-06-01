# -*- coding: utf-8 -*-
#
# Copyright: 2017 Shivam Sharma <shivam.src@gmail.com>
# License: GNU GPL v2 or higher

from zim.plugins import PluginClass
from zim.gui.pageview import PageViewExtension
from zim.actions import action
from zim.gui.widgets import Dialog, ErrorDialog
import json
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    from urllib import urlencode


class ZoteroPlugin(PluginClass):
    """plugin info for zim."""

    plugin_info = {
        'name': _('Zotero Citations'),
        'description': _('Zotero is a free cross-platform desktop reference and paper management program (http://www.zotero.org/).'
                         'This plugin allows you to insert Zotero citations that link directly to the Zotero desktop application.'
                         'You need to install the "zotxt" plugin in Zotero application, and the Zotero application must be running'
                         ' for this plugin to function.'),
        'author': 'Shivam Sharma',
        'help': 'Plugins:Zotero Citations',
    }

    plugin_preferences = (
        ('link_format', 'choice', _('Link Format'),
         'betterbibtexkey',
         ('betterbibtexkey', 'key', 'easykey', 'bibliography')),
        ('bibliography_style', 'string', _('Bibliography Style'), ''),
    )


class ZoteroPageViewExtension(PageViewExtension):
    """Define the input window."""

    def __init__(self, plugin, pageview):
        """Window constructor."""
        PageViewExtension.__init__(self, plugin, pageview)
        self.preferences = plugin.preferences

    @action(_('_Citation...'), accelerator='<Primary><Alt>I', menuhints='insert')  # T: menu item
    def insert_citation(self):
        """Will be called by the menu item or key binding."""
        dialog = ZoteroDialog.unique(self, self.pageview, self.preferences)
        dialog.show_all()


class ZoteroDialog(Dialog):
    """The Zotero specific Input Dialog."""

    zotxturl = "http://127.0.0.1:23119/zotxt/"
    zotxturlsearch = zotxturl + 'search?'
    zotxturlitem = zotxturl + 'items?'
    linkurl = "zotero://select/items/"
    forminputs = [
            ('searchtext', 'string', 'Pattern'),
            ('search:titleCreatorYear', 'option', 'Search in Title, Author and Date'),
            ('search:fields', 'option', 'Search in All Fields and Tags'),
            ('search:everything', 'option', 'Search Everywhere')
        ]

    def __init__(self, pageview, preferences):
        """Initialize the Input Box with options."""
        Dialog.__init__(self, pageview, _('Search in Zotero'),  # T: Dialog title
                        button=_('_GO'),  # T: Button label
                        defaultwindowsize=(350, 200))

        self.pageview = pageview
        self.preferences = preferences

        self.add_form(inputs=self.forminputs)

    def run(self):
        """Call the widget.dialog.run method."""
        Dialog.run(self)

    def do_response_ok(self):
        """
        Call to insert citation when pressing ok.
        Will insert the whole bibliography text.
        """
        textbuffer = self.pageview.textview.get_buffer()
        data = {}

        link_format = self.preferences['link_format']
        bibliography_style = self.preferences['bibliography_style']

        if link_format == 'bibliography' and bibliography_style is not None:
            data['style'] = bibliography_style

        data['method'] = self.form['search']
        data['format'] = link_format
        data['q'] = self.form['searchtext']
        urlvalues = urlencode(data)
        url = self.zotxturlsearch + urlvalues
        try:
            resp = json.loads(urlopen(url).read().decode('utf-8'))
            if link_format == 'bibliography':
                for i in resp:
                    key = i['key']
                    zotlink = (self.linkurl + key)
                    bibtext = i['text']
                    textbuffer.insert_link_at_cursor(bibtext, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            elif link_format == 'betterbibtexkey':
                for key in resp:
                    zotlink = (self.linkurl + '@' + key)
                    textbuffer.insert_link_at_cursor(key, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            elif link_format == 'easykey':
                for key in resp:
                    try:
                        zokey = self.fetchkey(key)
                    except Exception as error:
                        ErrorDialog(self, 'Could not fetch Zotero key: ' + str(error)).run()
                        continue
                    zotlink = (self.linkurl + zokey)
                    textbuffer.insert_link_at_cursor(key, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            elif link_format == 'key':
                for key in resp:
                    zotlink = (self.linkurl + key)
                    textbuffer.insert_link_at_cursor(key, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            else:
                ErrorDialog(self, 'link format unknown: ' + link_format).run()
                return False
        except Exception as error:
            ErrorDialog(self, str(error)).run()
            return False
        return True


    def fetchkey(self, easykey):
        data = {
                'easykey':easykey,
                'format': 'key'
               }
        url = self.zotxturlitem + urlencode(data)
        resp = json.loads(urlopen(url).read().decode('utf-8'))
        return resp[0]
