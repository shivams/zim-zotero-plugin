zim-zotero-plugin
=================

This ZIM Wiki plugin provides integration between Zotero (Reference Manager) and Zim (Personal Wiki Software).

Clone this repo to your plugins folder and restart your Zim wiki:

    git clone <this-repo> ~/.local/share/zim/plugins/zim-zotero-plugin

Note that you will need to install `zotxt` (https://github.com/egh/zotxt) plugin in your Zotero to make this plugin work.

How does it work?
-----------------

Press `<Shift>-<Control>-I` or go to Insert -> Citations. A dialog will open up, where you can enter your query to search for items in your Zotero collection. After pressing `GO`, all the matching items will be added into your Zim Wiki.

Handling zotero:// Links
------------------------

Items, that are addeed, are linked to Zotero using the `zotero://` identifier. Currently, Zim doesn't handle this identifier. So, you will have to create a custom script. A small such script is available in the repo: `zotero_link_handler.sh`. Copy it somewhere in your PATH.

And then, when in Zim, right click on the Zotero links and click Open With -> Customize, and add this custom script.
