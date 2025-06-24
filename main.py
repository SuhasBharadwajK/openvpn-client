import gi
import os
import tempfile
import json
import subprocess

'''
Resources:
https://pygobject.gnome.org/getting_started.html
https://stackoverflow.com/questions/38869427/openvpn-on-linux-passing-username-and-password-in-command-line
'''

'''
TODO
Find a way to add a tray icon as long as this is running.
'''

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Vte, GLib

CONFIG_PATH = os.path.expanduser("~/.myapp_config.json")

is_connected = False

class MyApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Login App")
        icon_path = os.path.join(os.path.dirname(__file__), "assets/icons/vpn.png")
        self.set_icon_from_file(icon_path)
        self.set_border_width(10)
        self.set_default_size(600, 400)

        self.config = self.load_config()

        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)

        # Input fields
        self.username_entry = Gtk.Entry()
        self.username_entry.set_placeholder_text("Username")
        vbox.pack_start(self.username_entry, False, False, 0)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_placeholder_text("Password")
        self.password_entry.set_visibility(False)
        vbox.pack_start(self.password_entry, False, False, 0)

        # Submit button
        submit_button = Gtk.Button(label="Submit")
        submit_button.connect("clicked", self.on_submit)
        vbox.pack_start(submit_button, False, False, 0)

        # Terminal
        self.terminal = Vte.Terminal()
        vbox.pack_start(self.terminal, True, True, 0)

        # Menu
        self.create_menu()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=4)

    def create_menu(self):
        menubar = Gtk.MenuBar()
        filemenu = Gtk.Menu()
        filem = Gtk.MenuItem(label="Settings")
        filem.set_submenu(filemenu)

        config_item = Gtk.MenuItem(label="Edit Config")
        config_item.connect("activate", self.on_edit_config)
        filemenu.append(config_item)

        menubar.append(filem)

        # Add menu bar to header
        vbox = Gtk.VBox(spacing=6)
        vbox.pack_start(menubar, False, False, 0)
        self.add(vbox)

    def on_edit_config(self, widget):
        dialog = Gtk.Dialog("Edit Config", self, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        box = dialog.get_content_area()
        entry = Gtk.Entry()
        entry.set_text(json.dumps(self.config, indent=2))
        entry.set_size_request(400, 200)
        box.add(entry)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            try:
                self.config = json.loads(entry.get_text())
                self.save_config()
            except Exception as e:
                print("Invalid config:", e)

        dialog.destroy()

    def on_submit(self, widget):
        '''
        TODO
        1. Find out a way to check if the connection is successful.
        2. If it is, hide the Connect button and show the Disconnect button.
        '''
        is_connected = True

        username = self.username_entry.get_text()
        password = self.password_entry.get_text()

        # Write to temp file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
            tmp.write(f"{username}\n{password}\n")
            tmp_path = tmp.name

        # Command to execute
        # For example: cat the file for demo purposes
        cmd = ["cat", tmp_path]  # Replace with your actual command

        # Run the command in the terminal
        self.terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.getcwd(),
            cmd,
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            None,
        )

        os.unlink(tmp_path)

win = MyApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()