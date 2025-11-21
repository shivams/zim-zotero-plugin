# -*- coding: utf-8 -*-
#
# Copyright: 2017 Shivam Sharma <shivam.src@gmail.com>
# License: GNU GPL v2 or higher

from zim.plugins import PluginClass
from zim.gui.pageview import PageViewExtension
from zim.actions import action
from zim.gui.widgets import Dialog, ErrorDialog
from gi.repository import Gtk
import json
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    from urllib import urlencode


def get_styles():
    try:
        url = "http://127.0.0.1:23119/zotxt/styles"
        resp = json.loads(urlopen(url, timeout=0.5).read().decode('utf-8'))
        styles = [item['fileName'].replace('.csl', '') for item in resp]
        styles.sort()
        return tuple(styles)
    except Exception:
        return ('apa',)

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

    styles = get_styles()

    plugin_preferences = (
        ('link_format', 'choice', _('Link Format'),
         'betterbibtexkey',
         ('betterbibtexkey', 'key', 'easykey', 'bibliography')),
        ('bibliography_style', 'choice', _('Bibliography Style'), 'apa', styles),
        ('libraries_all', 'bool', _('Include all Zotero libraries (including Group libraries)'), False),
    )


class CitationSelectionDialog(Dialog):
    """Dialog for selecting which citations to insert."""

    def __init__(self, parent, citations, link_format):
        """Initialize the citation selection dialog.
        
        @param parent: parent window
        @param citations: list of citation data (format depends on link_format)
        @param link_format: the format type (betterbibtexkey, key, easykey, bibliography)
        """
        Dialog.__init__(self, parent, _('Select Citations to Insert'),
                        buttons=Gtk.ButtonsType.OK_CANCEL,
                        defaultwindowsize=(600, 400))
        
        self.citations = citations
        self.link_format = link_format
        self.selected_citations = []
        
        # Create the list store: [selected, display_text, citation_data]
        self.liststore = Gtk.ListStore(bool, str, object)
        
        # Populate the list store
        for citation in citations:
            display_text = self._format_citation_display(citation)
            self.liststore.append([True, display_text, citation])  # Default: all selected
        
        # Create the tree view
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_headers_visible(True)
        
        # Add toggle column
        toggle_renderer = Gtk.CellRendererToggle()
        toggle_renderer.connect("toggled", self.on_item_toggled)
        toggle_column = Gtk.TreeViewColumn("Select", toggle_renderer, active=0)
        self.treeview.append_column(toggle_column)
        
        # Add text column
        text_renderer = Gtk.CellRendererText()
        text_column = Gtk.TreeViewColumn("Citation", text_renderer, text=1)
        text_column.set_expand(True)
        self.treeview.append_column(text_column)
        
        # Add scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.treeview)
        
        # Add buttons for select all / deselect all
        button_box = Gtk.HBox(spacing=5)
        select_all_btn = Gtk.Button.new_with_mnemonic(_('Select _All'))
        select_all_btn.connect('clicked', self.on_select_all)
        deselect_all_btn = Gtk.Button.new_with_mnemonic(_('_Deselect All'))
        deselect_all_btn.connect('clicked', self.on_deselect_all)
        button_box.pack_start(select_all_btn, False, True, 0)
        button_box.pack_start(deselect_all_btn, False, True, 0)
        
        # Add widgets to dialog
        self.vbox.pack_start(scrolled_window, True, True, 0)
        self.vbox.pack_start(button_box, False, True, 0)
    
    def _format_citation_display(self, citation):
        """Format citation for display in the list."""
        if self.link_format == 'bibliography':
            # citation is a dict with 'key' and 'text'
            return citation.get('text', str(citation))
        else:
            # citation is just a key/string
            return str(citation)
    
    def on_item_toggled(self, widget, path):
        """Handle toggling of individual items."""
        self.liststore[path][0] = not self.liststore[path][0]
    
    def on_select_all(self, widget):
        """Select all citations."""
        for row in self.liststore:
            row[0] = True
    
    def on_deselect_all(self, widget):
        """Deselect all citations."""
        for row in self.liststore:
            row[0] = False
    
    def do_response_ok(self):
        """Collect selected citations when OK is clicked."""
        self.selected_citations = []
        for row in self.liststore:
            if row[0]:  # If selected
                self.selected_citations.append(row[2])  # Append citation data
        self.result = self.selected_citations  # Set result for Dialog.run() to return
        return True
    
    def get_selected_citations(self):
        """Return the list of selected citations."""
        return self.selected_citations


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
        Will show a selection dialog first, then insert selected citations.
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
        if self.preferences['libraries_all']:
            url = url + '&library=all'
        
        try:
            # Fetch citations from Zotero
            resp = json.loads(urlopen(url).read().decode('utf-8'))
            
            if not resp:
                # No results found
                ErrorDialog(self, 'No citations found matching your query.').run()
                return False
            
            # Show selection dialog
            selection_dialog = CitationSelectionDialog(self, resp, link_format)
            selection_dialog.show_all()
            selected_citations = selection_dialog.run()
            selection_dialog.destroy()
            
            if not selected_citations:
                # User cancelled or no citations selected
                return False
            
            # Insert selected citations based on format
            if link_format == 'bibliography':
                for i in selected_citations:
                    key = i['key']
                    zotlink = (self.linkurl + key)
                    bibtext = i['text']
                    textbuffer.insert_link_at_cursor(bibtext, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            elif link_format == 'betterbibtexkey':
                for key in selected_citations:
                    zotlink = (self.linkurl + '@' + key)
                    textbuffer.insert_link_at_cursor(key, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            elif link_format == 'easykey':
                for key in selected_citations:
                    try:
                        zokey = self.fetchkey(key)
                    except Exception as error:
                        ErrorDialog(self, 'Could not fetch Zotero key: ' + str(error)).run()
                        continue
                    zotlink = (self.linkurl + zokey)
                    textbuffer.insert_link_at_cursor(key, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            elif link_format == 'key':
                for key in selected_citations:
                    zotlink = (self.linkurl + key)
                    textbuffer.insert_link_at_cursor(key, href=zotlink)
                    textbuffer.insert_at_cursor("\n")
            else:
                ErrorDialog(self, 'link format unknown: ' + link_format).run()
                return False
        except Exception as error:
            short_msg = "While executing the request to Zotero, an error happened"
            detailed_msg = "Error: " + str(error) + "\n\nURL: " + url
            ErrorDialog(self, (short_msg, detailed_msg)).run()
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
