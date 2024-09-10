import os
import ttkbootstrap as ttk
import ctypes
import logging
import logging.config

from src.utils.env import home
from src.utils.slite import conn
from src.gui.gui import Proxies
from src.utils.trans_imges import pic_transform
from pathlib import Path


class App(ttk.Window):

    def __init__(self):
        super().__init__()

        # 创建home应用目录
        self.home = home()
        # 项目路径解析
        self.PATH = Path(__file__).parent.parent.parent
        self.src_path = self.PATH / 'src'
        self.config_path = self.src_path / 'config'
        self.assets_path = self.src_path / 'assets'

        img_data = pic_transform(self.assets_path / 'Static_Residential_Proxies_64.png')
        self.title('ip proxies-singebogo@163.com')
        self.tk.call("wm", "iconphoto", self._w, ttk.PhotoImage(data=img_data))
        # self.resizable(False, False)

        # 告诉操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # 获取屏幕的缩放因子
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        # 设置程序缩放
        self.tk.call('tk', 'scaling', ScaleFactor / 75)

        self.place_window_center()

        self.init_data()
        self.logger.info('info message')

    def place_window_center(self):
        """Position the toplevel in the center of the screen. Does not
        account for titlebar height."""
        self.update_idletasks()
        w_height = self.winfo_height()
        w_width = self.winfo_width()
        s_height = self.winfo_screenheight()
        s_width = self.winfo_screenwidth()
        xpos = (s_width - w_width) // 5
        ypos = 100
        self.geometry(f'+{xpos}+{ypos}')

    def init_data(self):
        # hotkey win+F10
        # 日志创建
        logging.config.fileConfig(self.config_path / 'logging.ini')
        # create logger
        self.logger = logging.getLogger('fileAndConsole')
        # 数据库创建
        conn()


