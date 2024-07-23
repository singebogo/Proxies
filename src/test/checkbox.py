#!/usr/bin/python
# -*- coding: UTF-8 -*-

import tkinter as tk
from tkinter import ttk

top = tk.Tk()
CheckVar1 = tk.IntVar()
CheckVar2 = tk.IntVar()
C1 = tk.Checkbutton(top, text="RUNOOB", variable=CheckVar1, \
                 onvalue=1, offvalue=0, height=5, \
                 width=20)
C2 = tk.Checkbutton(top, text="GOOGLE", variable=CheckVar2, \
                 onvalue=1, offvalue=0, height=5, \
                 width=20)
C1.pack()
C2.pack()
CheckVar2.set(1)
top.mainloop()