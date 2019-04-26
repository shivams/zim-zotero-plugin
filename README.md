zim-zotero-plugin
=================

This ZIM Wiki plugin provides integration between Zotero (Reference Manager) and zim (Personal Wiki Software).

Clone this repo to your plugins folder and restart your zim wiki:

    git clone https://github.com/shivams/zim-zotero-plugin ~/.local/share/zim/plugins/zim-zotero-plugin

Note that you will need to install `zotxt` (https://github.com/egh/zotxt) plugin in your Zotero to make this plugin work.

Warning
-------

This version is not compatible to older ones. **The link format has changed.** 
It follows the direct supported link format of Zotero and therefore it can not 
support the easylink format. The old easylink format will have the Zotero key 
as its address.

###Convert the old link format into Zotero links

The script will do a move of the original txt files and copy the content to the 
original name while rewriting the Zotero links. The backup of original file is 
not changed.

**Warning:** a second run will overwrite the backup files!

	python3 update_links.py path/to/zim-wiki

How does it work?
-----------------

Press `<Control><Alt>-I` or go to Insert -> Citations. A dialog will open up, where you can enter your query to search for items in your Zotero collection. After pressing `GO`, all the matching items will be added into your zim wiki.

Changing the default link display format
------------------------

In zim go to Edit -> Preferences -> Plugins -> Zotero Citations

Under `Configure` you can choose the display format of Zotero links in zim:

- `betterbibtexkey`, e.g. *bloomAreIdeasGetting2017*
- `key`, e.g. *1_MGYAJ483*
- `bibliography`, e.g. *Bloom, Nicholas, Charles Jones, John Van Reenen, and Michael Webb. “Are Ideas Getting Harder to Find?,” 2017. https://doi.org/10.3386/w23782.*

The option `Bibliography Style` can now change the citation style used by the 
option `bibliography`. Be careful as the option shown in Zotero needs mostly to 
be transformed.

    RTF Style -> rft-style

Handling zotero:// Links
------------------------

Under Linux you need now a `zotero.desktop` for handling the links. The link 
should work then in every program. The important part is the 
`MimeType=x-scheme-handler/zotero;`. With it Zotero is used for `zotero://` 
links. Adjust your path to Zotero!

    $ cat .local/share/applications/zotero.desktop
    [Desktop Entry]
    Name=Zotero
    TryExec=zotero
    Exec=zotero -url %U
    Icon=Path_to_Zotero/chrome/icons/default/default256.png
    Type=Application
    Terminal=false
    Categories=Office;
    MimeType=x-scheme-handler/zotero;text/html;text/plain

After updating the mime-database and a zim restart, zim should find Zotero and 
open the links with it.

    update-mime-database ~/.local/share/mime
    update-desktop-database ~/.local/share/applications

If the Zotero handler is in the database, the output of `gio` should look like 
this:

    $ gio mime x-scheme-handler/zotero
    Default application for »x-scheme-handler/zotero«: zotero.desktop
    Registered applications:
            zotero.desktop
    Recommended applications:
            zotero.desktop

If Zotero is not set as default, you can try to set it with

    gio x-scheme-handler/zotero zotero.desktop

In the worst case you need to right click on a Zotero link and click *Open 
with* -> *Customize* and select Zotero as standard application.

TODOs
-----

- [ ] Intra-page References
  - See this launchpad wishlist: https://bugs.launchpad.net/zim/+bug/380844
  - And this blueprint by Jaap (zim BDFL): https://github.com/jaap-karssenberg/zim-wiki/wiki/Blueprint-anchors
- [ ] Bibtex Support
