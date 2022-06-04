import platform
import ctypes as ct
import os
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import messagebox

import darkdetect
import sv_ttk


class Vault_Window(tk.Tk):
    def __init__(self,  **kwargs):
        super().__init__()
        self.title("Add Vault")
        self.geometry('150x140')
        self.eval('tk::PlaceWindow . center')
        self.var = tk.StringVar()

        self.WINDOWS = 'Windows' in platform.platform()
        self.DARK = darkdetect.isDark()

        if self.WINDOWS:
            if self.DARK:
                sv_ttk.use_dark_theme()
            else:
                sv_ttk.use_light_theme()
        self.resizable(False, False)

        if self.WINDOWS and self.DARK:
            self.dark_title_bar()

        self.mainframe = tk.Frame(self)
        self.mainframe.pack()

        self.create_button = ttk.Button(
            self.mainframe, text="Create Vault", command=self.create_vault)
        self.add_button = ttk.Button(
            self.mainframe, text="Add Vault", command=self.add_vault)
        self.quit_button = ttk.Button(
            self.mainframe, text="Cancel", command=self.destroy)

        self.create_button.pack(side='top', pady=(5, 0))
        self.add_button.pack(side='top', pady=5)
        self.quit_button.pack(side='top')

    def show(self):
        self.deiconify()
        self.wait_window()
        value = self.var.get()
        return value

    def add_vault(self):
        self.var.set('add')
        filepath = askopenfilename(
            filetypes=[('Masterfile', '*.e')])
        if filepath:
            size = os.path.getsize(filepath)
            if size == 192:
                self.var.set(f'{self.var.get()},{filepath}')
                self.destroy()
            else:
                messagebox.showerror(None, "Bad masterfile")

    def create_vault(self):
        self.var.set('create')
        dirpath = askdirectory()
        if dirpath:
            self.var.set(f'{self.var.get()},{dirpath}')
            self.destroy()

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
    Vault_Window().mainloop()
