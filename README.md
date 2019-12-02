zim-zotero-plugin
=================

This ZIM Wiki plugin provides integration between Zotero (Reference Manager) and zim (Personal Wiki Software).

Clone this repo to your plugins folder and restart your zim wiki:

    git clone https://github.com/shivams/zim-zotero-plugin ~/.local/share/zim/plugins/zim-zotero-plugin

Note that you will need to install `zotxt` (https://github.com/egh/zotxt) plugin in your Zotero to make this plugin work.

How does it work?
-----------------

Press `<Control><Shift>-I` or go to Insert -> Citations. A dialog will open up, where you can enter your query to search for items in your Zotero collection. After pressing `GO`, all the matching items will be added into your zim wiki.

Alternatively you can add a single deliberate item by selecting the option `Easy Key`. To use this option, modify your Zotero preferences to make the “Easy Citekey” exporter your default for Quick Copy `<Control><Shift>-C`. Then you can simply paste the key from your clipboard inside the text input and press `GO` to get the intended item.

A quick way to add citation is using `<Control><Alt>-I` or Insert->Cite Selected. This option will immediately add the item that is currenty selected in your Zotero app. 

Changing the default link display format
------------------------

In zim go to Edit -> Preferences -> Plugins -> Zotero Citations
Under `Configure` you can choose the display format of Zotero links in zim:

- `betterbibtexkey`, e.g. *bloomAreIdeasGetting2017*
- `easykey`, e.g. *bloom:2017are*
- `key`, e.g. *1_MGYAJ483*
- `bibliography`, e.g. *Bloom, Nicholas, Charles Jones, John Van Reenen, and Michael Webb. “Are Ideas Getting Harder to Find?,” 2017. https://doi.org/10.3386/w23782.*

Handling zotero:// Links
------------------------

~~Items, that are added, are linked to Zotero using the `zotero://` identifier. Currently, zim doesn't handle this identifier. So, you will have to create a custom script. A small such script is available in the repo: `zotero_link_handler.sh`. Copy it somewhere in your PATH. And then, when in zim, right click on the Zotero links and click Open With -> Customize, and add this custom script.~~

~~No need of external scripts to handle zotero links. Now, the plugin handles all the links itself. When you click on any Zotero link in your Notebook, the particular reference is highlighted in Zotero.~~

Sad to say, but we are back to the original state, I did not find a way to make zim open `zotero://` links by default in zim 0.70. Hence now you should again take the `zotero_link_handler.sh`, put it on your PATH (and make it executable). Then, when in zim, right click on the Zotero links and click Open With -> Customize, and fill in `zotero_link_handler.sh` as command.

TODOs
-----

- [ ] Intra-page References
  - See this launchpad wishlist: https://bugs.launchpad.net/zim/+bug/380844
  - And this blueprint by Jaap (zim BDFL): https://github.com/jaap-karssenberg/zim-wiki/wiki/Blueprint-anchors
- [ ] Bibtex Support
