# Native imports
import ctypes as ct
import platform
import tkinter as tk
from tkinter import TOP, ttk

# External imports
import darkdetect
import Rust_Vault_Encryption as rve
import sv_ttk

# Workspace imports
import functions
import vault as vobj
from add_vault_window import Vault_Window
from password_input_window import Password_Input
from vault_name_window import Vault_Name


class Base_Window(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__()
        self.title("Test")

        self.WINDOWS = 'Windows' in platform.platform()
        self.DARK = darkdetect.isDark()
        self.LAST_LABEL = None
        self.UNLOCK_BUTTON = None
        self.VAULTS = functions.load_vaults()
        self.LABELS = []
        self.CURRENT_VAULT = None

        ### Create window ###
        if self.WINDOWS:
            if self.DARK:
                sv_ttk.use_dark_theme()
            else:
                sv_ttk.use_light_theme()
            ### Configure window for Windows###
            self.rowconfigure(0, minsize=400, weight=1)
            self.columnconfigure(1, minsize=400, weight=1)
            self.columnconfigure(0, minsize=110, weight=1)
            self.title('Gui Test')
            self.resizable(False, False)
        else:
            ### Configure window for Mac ###
            self.rowconfigure(0, minsize=400, weight=1)
            self.columnconfigure(1, minsize=400, weight=1)
            self.columnconfigure(0, minsize=125, weight=1)
            self.title('Gui Test')
            self.resizable(False, False)

        self.create_vault_frame()
        self.create_left_frame()
        self.create_options_frame()
        self.add_vault_button()
        self.open_folder_button()

        self.pop_vaults()

        # change title bar to dark on windows if os
        # is in dark mode
        if self.WINDOWS and self.DARK:
            self.dark_title_bar()

    def lock_vault(self, vault: vobj.Vault):
        functions.lock_vault(vault)
        self.change_label(vault, self.LAST_LABEL)
        # self.pop_vaults()

    def unlock_vault(self, vault: vobj.Vault):
        functions.unlock_vault(vault)
        self.change_label(vault, self.LAST_LABEL)
        # self.pop_vaults()

    def create_vault(self, result):
        name = Vault_Name().show()
        if name:
            password = Password_Input().show()
            if password:
                rve.create_masterfile(result[1], password)
                self.VAULTS.append(vobj.Vault(
                    name, f'{result[1]}/masterfile.e', rve.hash_password_string(password)))
                functions.write_vaults(self.VAULTS)
                self.pop_vaults()

    def add_vault(self, result):
        name = Vault_Name().show()
        path = result[1]
        if name:
            password = Password_Input().show()
            if password:
                self.VAULTS.append(vobj.Vault(
                    name, path, rve.hash_password_string(password)))
                functions.write_vaults(self.VAULTS)
                self.pop_vaults()

    def vault_stage(self):
        result = Vault_Window().show()
        result = result.split(',')
        if len(result) > 1:
            if result[0] == 'create':
                self.create_vault(result)
            elif result[0] == 'add':
                self.add_vault(result)

    def create_options_frame(self):
        self.options_frm = tk.Frame(
            self.left_frm,
            relief=tk.RAISED,
        )
        self.options_frm.pack(fill='none', expand=True,
                              padx=(150, 0), pady=(0, 100))
        self.lock_unlock_button = ttk.Button(
            self.options_frm,
        )

    def create_vault_frame(self):
        ### Frame for vault list ###
        self.vault_frm = tk.Frame(
            self,
            bg='grey',
            relief=tk.GROOVE,
            bd=2,
        )
        self.vault_frm.grid(
            row=0,
            column=1,
            padx=(10, 0),
            sticky='nse',
        )

    def create_left_frame(self):
        ### Frame for options ###
        self.left_frm = tk.Frame(
            self,
        )
        self.left_frm.grid(
            row=0,
            column=0,
            padx=(10, 0),
            sticky='nsw',
        )

    def add_vault_button(self):
        ### Add Vault button ###
        self.add_vault_button = ttk.Button(
            self,
            text='Add Vault',
            width=27,
            command=self.vault_stage,
        )
        self.add_vault_button.grid(
            row=1,
            column=1,
            sticky='se',
        )

    def open_folder_button(self):
        self.folder_button = ttk.Button(
            self.options_frm
        )
        self.folder_button_label = ttk.Label(
            self.options_frm,
            relief=tk.RIDGE,
        )

    def change_label(self, i: vobj.Vault, label_obj: ttk.Label):
        self.CURRENT_VAULT = i

        # Change last label if not none and not current object
        if self.LAST_LABEL and self.LAST_LABEL != label_obj:
            self.LAST_LABEL.config(background='white')
            self.LAST_LABEL.config(foreground='black')

        # Change colors of clicked label
        label_obj.config(background='#a72145')
        label_obj.config(foreground='white')

        # Change last label to current object
        self.LAST_LABEL = label_obj

        # Pack the unlock button if not already packed
        if not self.UNLOCK_BUTTON:
            self.lock_unlock_button.grid(row=0, column=0)

            # Update unlock button text according to vault status
        if i.status == 0:
            self.lock_unlock_button.config(
                text="Unlock", command=lambda vault=i: self.unlock_vault(vault))
            self.folder_button.grid_forget()
            self.folder_button_label.grid_forget()
        elif i.status == 1:
            self.lock_unlock_button.config(
                text="Lock", command=lambda vault=i: self.lock_vault(vault))
            self.folder_button.config(text=f'Open Folder')
            self.folder_button_label.config(text=f'{i.path}')
            self.folder_button.grid(row=1, column=0, pady=(5, 0))
            self.folder_button_label.grid(row=2, column=0)

    def pop_vaults(self):
        # Use regular tk on mac because of a problem with
        # mac ttk labels and background color
        if len(self.LABELS) > 0:
            for i in self.LABELS:
                i.pack_forget()
                i.destroy()
            self.LABELS = []
            self.LAST_LABEL = None
        for vault in self.VAULTS:
            """if vault.status == 0:
                status = "Locked"
            else:
                status = "Unlocked"""
            status = functions.readable_status(vault.status)
            if self.WINDOWS:
                temp_obj = ttk.Label(self.vault_frm)
            else:
                temp_obj = tk.Label(self.vault_frm)
            temp_obj.config(
                text=f'{vault.name}\n{vault.path}\n{status}',
                width=30,
                background='white',
                foreground='black',
            )
            temp_obj.pack(
                side=TOP,
                pady=2,
            )
            temp_obj.bind(
                '<Button-1>',
                lambda event, pass_vault=vault, pass_label=temp_obj: self.change_label(
                    pass_vault, pass_label)
            )
            self.LABELS.append(temp_obj)

    def dark_title_bar(self):
        """
        Change title bar to dark on windows
        MORE INFO:
        https://docs.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
        """
        self.update()
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ct.windll.user32.GetParent
        hwnd = get_parent(self.winfo_id())
        rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
        value = 2
        value = ct.c_int(value)
        set_window_attribute(hwnd, rendering_policy,
                             ct.byref(value), ct.sizeof(value))


if __name__ == '__main__':
    app = Base_Window()
    app.mainloop()
