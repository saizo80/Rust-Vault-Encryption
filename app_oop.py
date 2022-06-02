# Native imports
import ctypes as ct
import platform
import tkinter as tk
from tkinter import CENTER, END, TOP, ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

# External imports
import darkdetect
import sv_ttk
import ttkthemes
import test_obj


class Base_Window(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__()
        self.title("Test")

        self.WINDOWS = 'Windows' in platform.platform()
        self.DARK = darkdetect.isDark()
        self.LAST_LABEL = None
        self.UNLOCK_BUTTON = None

        ### Create window ###
        if self.WINDOWS:
            if self.DARK:
                sv_ttk.use_dark_theme()
            else:
                sv_ttk.use_light_theme()

        ### Configure window ###
        self.rowconfigure(0, minsize=400, weight=1)
        self.columnconfigure(1, minsize=400, weight=1)
        self.columnconfigure(0, minsize=110, weight=1)
        self.title('Gui Test')
        self.resizable(False, False)

        self.create_vault_frame()
        self.create_option_frame()
        self.add_vault_button()

        self.pop_vaults(10)

        # change title bar to dark on windows if os
        # is in dark mode
        if self.WINDOWS and self.DARK:
            self.dark_title_bar()

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

    def create_option_frame(self):
        ### Frame for options ###
        self.options_frm = tk.Frame(
            self,
        )
        self.options_frm.grid(
            row=0,
            column=0,
            padx=(10, 0),
            sticky='nsw',
        )
        self.lock_unlock_button = ttk.Button(
            self.options_frm,
            text='Unlock/Lock',
        )

    def add_vault_button(self):
        ### Add Vault button ###
        self.add_vault_button = ttk.Button(
            self,
            text='Add Vault',
            width=27,
        )
        self.add_vault_button.grid(
            row=1,
            column=1,
            sticky='se',
        )

    def print_name(self, i: test_obj.test_obj, label_obj: ttk.Label):
        if self.LAST_LABEL and self.LAST_LABEL != label_obj:
            self.LAST_LABEL.config(background='white')
            self.LAST_LABEL.config(foreground='black')
        label_obj.config(background='#a72145')
        label_obj.config(foreground='white')
        self.LAST_LABEL = label_obj
        if not self.UNLOCK_BUTTON:
            self.lock_unlock_button.pack(side='left')

    def pop_vaults(self, amount: int):
        objects = []
        objects.append(test_obj.test_obj(0, 'data0'))
        objects.append(test_obj.test_obj(1, 'data1'))
        objects.append(test_obj.test_obj(2, 'data2'))
        objects.append(test_obj.test_obj(3, 'data3'))
        # Use regular tk on mac because of a problem with
        # mac ttk labels and background color
        if self.WINDOWS:
            for i in objects:
                temp_obj = ttk.Label(
                    self.vault_frm,
                    text=f'Object {i.id}\n{i.data}',
                    width=30,
                    background='white',
                    foreground='black',
                )
                temp_obj.pack(
                    side=TOP,
                    pady=2
                )

                temp_obj.bind(
                    '<Button-1>',
                    lambda event, temp=i, temp_label=temp_obj: self.print_name(
                        temp, temp_label)
                )
        else:
            for i in objects:
                temp_obj = tk.Label(
                    self.vault_frm,
                    text=f'Object {i.id}\n{i.data}',
                    width=30,
                    background='white',
                    foreground='black',
                    font='Arial',
                )
                temp_obj.pack(
                    side=TOP,
                    pady=2
                )

                temp_obj.bind(
                    '<Button-1>',
                    lambda event, temp=i, temp_label=temp_obj: self.print_name(
                        temp, temp_label)
                )

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
