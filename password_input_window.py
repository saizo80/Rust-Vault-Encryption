import platform
import ctypes as ct
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

import darkdetect
import sv_ttk


class Password_Input(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__()
        self.title("Password")
        self.geometry('250x250')
        self.var = tk.StringVar()
        self.eval('tk::PlaceWindow . center')

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
        self.mainframe.pack(side='top', pady=(5, 0))
        self.buttonframe = tk.Frame(self)
        self.buttonframe.pack(side='top', pady=5)

        self.pass_label = ttk.Label(self.mainframe, text="Enter Password:")
        self.pass_label.pack(side='top')

        self.password_field = ttk.Entry(self.mainframe, show='*')
        self.password_field.pack(side='top')

        self.enterbutton = ttk.Button(
            self.buttonframe, text='Submit', command=self.enter_password)
        self.quitbutton = ttk.Button(
            self.buttonframe, text='Cancel', command=self.destroy)
        self.enterbutton.pack(side='left')
        self.quitbutton.pack(side='left')

        self.bind('<Return>', self.handler)
        self.bind('<Escape>', self.quit_handler)

    def enter_password(self):
        self.var.set(self.password_field.get())
        self.destroy()

    def handler(self, e):
        self.enter_password()

    def quit_handler(self, e):
        self.destroy()

    def show(self):
        self.deiconify()
        self.wait_window()
        value = self.var.get()
        return value

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
    Password_Input().show()
