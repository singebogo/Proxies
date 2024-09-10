import logging
import os.path
from datetime import datetime
from random import choices
import sched, time
from tkinter.ttk import Panedwindow
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
from tkinter.filedialog import askdirectory
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from threading import *
from ttkbootstrap.window import Toplevel
from src.utils.env import home

from .collapsingFrame import CollapsingFrame
from ..utils.git_player import playGif
from ..utils.ip_check import check_proxy, domestic, abroad, origin_ip, host_ip
from ..utils.ips import Downloader
from ..utils.proxy_reg import queryProxyEnable, queryProxyOverride, queryProxyServer, enable as proxyEnable, \
    setProxy, disable as proxyDisable
from ..utils.slite import select_sql, select_count_sql, select_count_today_sql, select_lastest_sql, \
    select_speed_today_sql, dele
from PIL import Image, ImageTk

PATH = Path(__file__).parent.parent / 'assets'

logger = logging.Logger("fileAndConsole")


class Proxies(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(fill=BOTH, expand=YES)
        self.lsched = None
        self.count = 5  # 多少分钟循环一次抓取数据
        self.label = 0 # 游标
        self.log_app = None

        self.handlers = logger.handlers
        self.log_file = os.path.join(home(), 'Proxies.log')
        for handle in self.handlers:
            if type('handle') == 'FileHandler':
                self.log_file = handle.baseFilename
                break

        image_files = {
            'properties-dark': 'icons8_settings_24px.png',
            'properties-light': 'icons8_settings_24px_2.png',
            'add-to-backup-dark': 'icons8_add_folder_24px.png',
            'add-to-backup-light': 'icons8_add_book_24px.png',
            'stop-backup-dark': 'icons8_cancel_24px.png',
            'stop-backup-light': 'icons8_cancel_24px_1.png',
            'play_light': 'icons8_play_24px_1.png',
            'play_dark': 'icons8_play_24px.png',
            'refresh': 'icons8_refresh_24px_1.png',
            'stop-dark': 'icons8_stop_24px.png',
            'stop-light': 'icons8_stop_24px_1.png',
            'opened-folder': 'icons8_opened_folder_24px.png',
            'logo': 'backup.png',
            'grap_32_dark': 'grap_32_1.png',
            'grap_32_light': 'grap_32.png',
            'proxyserver_light': 'proxyserver.png',
            'notice': 'ps.png',
            'config': 'config.png',
            'registry_editor_32': 'icons8_registry_editor_32px.png',
            'registry_editor_64': 'icons8_registry_editor_64px.png',
            'proxies_light': 'Static Residential Proxies_light_32.png',
            'proxies_dark': 'Static Residential Proxies_dark_32.png',
            'proxies_stop_light': 'informix.png',
            'proxies_stop_dark': 'informi_red.png',
        }

        self.photoimages = []
        imgpath = Path(__file__).parent.parent / 'assets'
        for key, val in image_files.items():
            _path = imgpath / val
            self.photoimages.append(ttk.PhotoImage(name=key, file=_path))

        self.ip = {}  # 当前可配置的ip (1、初始化：speed最高的，2、treeview 选择 )
        self.init_button_bar()
        self.init_left_panel()
        self.init_right_panel()

        self.event = Event()
        self.downloadId = Thread(target=self.download_flow, daemon=True)
        self.downloadId.start()

        self.log_event = Event()
        self.log_Id = Thread(target=self.refresh_logs_flow, daemon=True)
        self.log_Id.start()

    def countdown(self, c):
        # c 分钟
        c = int(c) * 60
        while self.event.is_set() and c:
            m, s = divmod(c, 60)
            timer = '{:02d}:{:02d}'.format(m, s)
            self.grap.configure(image='grap_32_dark', text='自动抓取中.....倒计时：{}'.format(timer), )
            time.sleep(1)
            c -= 1

    def download_flow(self):
        self.event.wait()
        while self.event.is_set():
            # event clear 后 还在运行
            time.sleep(1)
            Downloader().run()
            self.countdown(self.count)

    def refresh_logs_flow(self):
        self.log_event.wait()
        while self.log_event.is_set():
            # event clear 后 还在运行
            time.sleep(1)
            # 重新加载日志
            fd = open(self.log_file, 'r',encoding='UTF-8')  # 获得一个句柄
            fd.seek(self.label, 0)  # 把文件读取指针移动到之前记录的位置
            self.s_text.insert('end', fd.readlines())  # 接着上次的位置继续向下读取
            self.s_text.see(ttk.END)
            fd.close()
            if not self.log_app:
                self.log_event.clear()

    def init_button_bar(self):
        # buttonbar
        buttonbar = ttk.Frame(self, style='primary.TFrame')
        buttonbar.pack(fill=X, pady=1, side=TOP)

        ## new backup
        self.proxy_btn = ttk.Checkbutton(
            master=buttonbar, text='开始代理',
            image='proxies_light',
            compound=LEFT,
            bootstyle="primary-toolbutton",
            command=self.proxy,
        )
        self.proxy_btn.pack(side=LEFT, ipadx=5, ipady=5, padx=(1, 0), pady=1)

        btn = ttk.Button(
            master=buttonbar,
            text='刷新',
            image='refresh',
            compound=LEFT,
            command=self.refresh
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

        btn = ttk.Button(
            master=buttonbar,
            text='重新加载',
            image='refresh',
            compound=LEFT,
            command=self.reload
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

        # configure style
        self.grap = ttk.Checkbutton(
            master=buttonbar,
            text='自动抓取',
            image='grap_32_light',
            compound=LEFT,
            bootstyle="primary-toolbutton",
            command=self.selected
        )
        self.grap.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

        _func = lambda: Messagebox.ok(message='设置...')
        btn = ttk.Button(
            master=buttonbar,
            text='设置',
            image='properties-light',
            compound=LEFT,
            command=_func
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

        btn = ttk.Button(
            master=buttonbar,
            text='清理缓存',
            image='properties-light',
            compound=LEFT,
            command=self._clearCache
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

        btn = ttk.Button(
            master=buttonbar,
            text='日志',
            image='properties-light',
            compound=LEFT,
            command=self._log
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

    def _log(self):
        self.log_app = Toplevel(title="logs view", size=(950, 600), toolwindow=False)
        self.log_app.place_window_center()
        self.log_app.position_center()

        # 工具栏
        buttonbar = ttk.Frame(self.log_app, style='primary.TFrame')
        buttonbar.pack(fill=BOTH, pady=1, side=TOP)

        btn = ttk.Button(
            master=buttonbar,
            text='刷新',
            image='refresh',
            compound=LEFT,
            command=self.refresh_logs
        )
        btn.pack(side=LEFT, ipadx=5, ipady=5, padx=0, pady=1)

        # 日志区域
        logs_panel = ttk.Frame(self.log_app, style='bg.TFrame', borderwidth=1)
        logs_panel.pack(fill=BOTH, pady=1, side=TOP, expand=YES)
        style = ttk.Style()
        self.s_text = ttk.ScrolledText(logs_panel,
                                  highlightcolor=style.colors.primary,
                                  highlightbackground=style.colors.border,
                                  highlightthickness=1)
        self.s_text.pack(fill=BOTH, expand=True)
        self.log_app.mainloop()

        t1 = Thread(target=self.init_logs, args=())
        t1.daemon = True  # 设置p1为守护进程
        t1.start()

    def init_logs(self):
        # 首次读取文件
        fd = open(self.log_file, 'r', encoding='UTF-8')  # 获得一个句柄
        self.s_text.insert('end', fd.readlines())  # 接着上次的位置继续向下读取
        self.s_text.see(ttk.END)
        self.label = fd.tell()  # 记录读取到的位置
        fd.close()  # 关闭文件

    def refresh_logs(self):
        self.log_event.set()

    def _clearCache(self):
        dele()
        self.reload()

    def refresh(self):
        # 1、当前状态
        enable = queryProxyEnable()
        Override = queryProxyOverride()
        server = queryProxyServer()
        if enable:
            self.pbar.start()
        else:
            self.pbar.stop()
        self.setvar('prog-message', ("<" + server + ">" if server else "<   >") + ' proxing...')
        self.setvar('ProxyEnable', 'ProxyEnable: ' + (str("未开启代理") if not enable else "开启代理"))
        self.setvar('ProxyOverride', "ProxyOverride: " + (str(Override) if Override else "未配置"))
        self.setvar('ProxyServer', 'ProxyServer: ' + (str(server) if server else "未配置"))
        if not enable:
            self.enable_proxy_btn.configure(image='play_dark', text="开启代理")
            self.proxy_btn.configure(image='play_dark', text="开启代理")
        else:
            self.enable_proxy_btn.configure(image='stop-backup-dark', text="停止代理")
            self.proxy_btn.configure(image='stop-backup-dark', text="停止代理")

        # 3、数据加载
        self.reload()

        # toolbar
        # if not enable:
        #     self.proxy_tool_check.set(0)
        # else:
        #     self.proxy_tool_check.set(1)
        self.proxy()

    def reload(self):
        # 2、当前综合
        self.summary()
        # 重新数据库拉取数据
        self.tv.delete_rows()
        self._init_load_ips()

        # 4、当前可代理
        self.fast_speed()

    def selected(self):
        # flag：1 抓取：定时器 开启--》开启一次性守护线程--》多个守护线程--》执行完成
        #       0 停止抓取 定时器 停止 (最近一次抓取行为自动结束)
        state = self.grap.state()
        if "selected" in state:
            self.grap.configure(image='grap_32_dark', text='自动抓取中.....', )
            self.event.set()
        else:
            self.grap.configure(image='grap_32_light', text='停止抓取', )
            self.event.clear()

    def proxy(self):
        state = self.proxy_btn.state()
        if "selected" in state:
            self.proxy_btn.configure(image='proxies_stop_dark', text='停止代理', )
        else:
            self.proxy_btn.configure(image='proxies_light', text='开始代理', )

    def init_left_panel(self):
        # left panel
        left_panel = ttk.Frame(self, style='bg.TFrame')
        left_panel.pack(side=LEFT, fill=Y)

        self.init_proxy_summary_CollapsingFrame(left_panel)
        self.init_proxy_status_CollapsingFrame(left_panel)
        self.init_other_CollapsingFrame(left_panel)

    def init_proxy_summary_CollapsingFrame(self, left_panel):
        ## backup summary (collapsible)
        bus_cf = CollapsingFrame(left_panel)
        bus_cf.pack(fill=X, pady=1)

        ## container
        bus_frm = ttk.Frame(bus_cf, padding=5)
        bus_frm.columnconfigure(1, weight=1)
        bus_cf.add(
            child=bus_frm,
            title='Porxy Summary',
            bootstyle=SECONDARY)

        ## destination
        lbl = ttk.Label(bus_frm, textvariable='all_ips')
        lbl.grid(row=0, column=0, sticky=W, pady=2)

        ## last run
        lbl = ttk.Label(bus_frm, textvariable='last_grap_run')
        lbl.grid(row=1, column=0, sticky=W, pady=2)

        ## files Identical
        lbl = ttk.Label(bus_frm, textvariable='today_ips')
        lbl.grid(row=2, column=0, sticky=W, pady=2)

        ## files Identical
        lbl = ttk.Label(bus_frm, textvariable='origin_ip')
        lbl.grid(row=3, column=0, sticky=W, pady=2)

        lbl = ttk.Label(bus_frm, textvariable='host_ip')
        lbl.grid(row=4, column=0, sticky=W, pady=2)

        self.summary()

        ## section separator
        sep = ttk.Separator(bus_frm, bootstyle=SECONDARY)
        sep.grid(row=5, column=0, columnspan=2, pady=10, sticky=EW)

        # treeView 选中展示

        self.now_lbl = ttk.Label(bus_frm, text='当前可配置代理数据')
        self.now_lbl.grid(row=6, column=0, sticky=W, pady=2)
        # ip
        self.ip_lbl = ttk.Label(bus_frm, text='ip:')
        self.ip_lbl.grid(row=7, column=0, sticky=W, pady=2)
        # port
        self.port_lbl = ttk.Label(bus_frm, text='port:')
        self.port_lbl.grid(row=8, column=0, sticky=W, pady=2)
        # speed
        self.speed_lbl = ttk.Label(bus_frm, text='speed:')
        self.speed_lbl.grid(row=9, column=0, sticky=W, pady=2)
        # local
        self.local_lbl = ttk.Label(bus_frm, text='local:')
        self.local_lbl.grid(row=10, column=0, sticky=W, pady=2)

        self.domestic_lbl = ttk.Label(bus_frm, text='国内代理:')
        self.domestic_lbl.grid(row=11, column=0, sticky=W, pady=2)

        self.abroad_lbl = ttk.Label(bus_frm, text='国际代理:')
        self.abroad_lbl.grid(row=12, column=0, sticky=W, pady=2)

        # 获取最新一条数据
        self.fast_speed()

        sep = ttk.Separator(bus_frm, bootstyle=SECONDARY)
        sep.grid(row=13, column=0, columnspan=2, pady=10, sticky=EW)
        ## 配置注册表代理 button
        bus_prop_btn = ttk.Button(
            master=bus_frm,
            text='配置代理服务器',
            image='config',
            compound=LEFT,
            command=self.setProxySetting,
            bootstyle=LINK
        )
        bus_prop_btn.grid(row=14, column=0, columnspan=2, sticky=W)

    def init_origin_ip(self):
        self.setvar('origin_ip', "当前ip: " + str(origin_ip()))
        self.setvar('host_ip', "本机ip: " + str(host_ip()))

    def summary(self):
        today = select_count_today_sql()
        self.setvar('today_ips', '今日可ip代理总数: ' + str("未抓取" if not today[0] else today[0]))
        self.setvar('last_grap_run', "最后一次抓取时间: " + str(select_lastest_sql()))
        self.setvar('all_ips', "可ip代理总数: " + str(select_count_sql()))

        t1 = Thread(target=self.init_origin_ip, args=())
        t1.daemon = True  # 设置p1为守护进程
        t1.start()

    def fast_speed(self):
        # 当前今日最快一条
        today = select_speed_today_sql()
        if not today:
            ip, port, last_check, speed, local, domestic, abroad, type = "", "", "", "", "", "", "", ""
        else:
            ip, port, last_check, speed, local, domestic, abroad, type = today
        self.ip['ip'] = ip
        self.ip['port'] = port
        self.ip['last_check'] = last_check
        self.ip['speed'] = speed
        self.ip['local'] = local
        self.ip['domestic'] = domestic
        self.ip['abroad'] = abroad
        #
        self.now_lbl.configure(text='当前可配置代理数据->最高speed: ' + speed)
        self.ip_lbl.configure(text="ip: " + ip)
        # port
        self.port_lbl.configure(text="port: " + port)
        # speed
        self.speed_lbl.configure(text="speed: " + speed)
        # local
        self.local_lbl.configure(text="local: " + local)

        t1 = Thread(target=self.invaild_proxy, args=(self.ip['ip'], self.ip['port']))
        t1.daemon = True  # 设置p1为守护进程
        t1.start()

    def invaild_proxy(self, ip, port):
        invaild_domestic = domestic(ip, port)
        invaild_abroad = abroad(ip, port)
        self.domestic_lbl.configure(text='国内代理: ' + str('有效' if invaild_domestic else '无效'))
        self.abroad_lbl.configure(text='国际代理: ' + str('有效' if invaild_abroad else '无效'))

    def setProxySetting(self):
        if self.ip and len(self.ip) > 0 and self.ip['ip'] and self.ip['port']:
            if setProxy(ProxyServer=self.ip['ip'] + ":" + self.ip['port']):
                self.init_status()

    def init_proxy_status_CollapsingFrame(self, left_panel):
        # backup status (collapsible)
        status_cf = CollapsingFrame(left_panel)
        status_cf.pack(fill=BOTH, pady=1)

        status_frm = ttk.Frame(status_cf, padding=10)
        status_frm.columnconfigure(1, weight=1)
        status_cf.add(
            child=status_frm,
            title='Proxy Status',
            bootstyle=SECONDARY
        )
        ## progress message
        lbl = ttk.Label(
            master=status_frm,
            textvariable='prog-message',
            font='Helvetica 10 bold'
        )
        lbl.grid(row=0, column=0, columnspan=2, sticky=W)

        ## progress bar
        self.pbar = ttk.Progressbar(
            master=status_frm,
            variable='prog-value',
            bootstyle=SUCCESS,
            mode='indeterminate',
        )
        self.pbar.grid(row=1, column=0, columnspan=2, sticky=EW, pady=(10, 5))

        ## time remaining
        lbl = ttk.Label(status_frm, textvariable='ProxyEnable')
        lbl.grid(row=2, column=0, columnspan=2, sticky=EW, pady=2)

        ## time started
        lbl = ttk.Label(status_frm, textvariable='ProxyOverride')
        lbl.grid(row=3, column=0, columnspan=2, sticky=EW, pady=2)

        ## time elapsed
        lbl = ttk.Label(status_frm, textvariable='ProxyServer')
        lbl.grid(row=4, column=0, columnspan=2, sticky=EW, pady=2)

        ## section separator
        sep = ttk.Separator(status_frm, bootstyle=SECONDARY)
        sep.grid(row=5, column=0, columnspan=2, pady=10, sticky=EW)

        ## stop button
        self.enable_proxy_btn = ttk.Button(
            master=status_frm,
            text='开启代理',
            # image='stop-backup-dark',
            image='play_dark',
            compound=LEFT,
            command=self.enable_proxy,
            bootstyle=LINK
        )
        self.enable_proxy_btn.grid(row=6, column=0, columnspan=2, sticky=W)

        ## section separator
        sep = ttk.Separator(status_frm, bootstyle=SECONDARY)
        sep.grid(row=7, column=0, columnspan=2, pady=10, sticky=EW)

        # current file message
        lbl = ttk.Label(status_frm, textvariable='current-setting-proxy-msg')
        lbl.grid(row=8, column=0, columnspan=2, pady=2, sticky=EW)

        self.init_status()

    def init_status(self):
        # 状态初始化
        self.init_pbar()
        self.init_enable_proxy_btn()
        self.init_label()

    def init_label(self):
        server = queryProxyServer()
        enable = queryProxyEnable()
        Override = queryProxyOverride()
        server = queryProxyServer()
        self.setvar('ProxyEnable', 'ProxyEnable: ' + (str("未开启代理") if not enable else "开启代理"))
        self.setvar('ProxyOverride', "ProxyOverride: " + (str(Override) if Override else "未配置"))
        self.setvar('ProxyServer', 'ProxyServer: ' + (str(server) if server else "未配置"))
        self.setvar('prog-message', ("<" + server + ">" if server else "<   >") + ' proxing...')

    def enable_proxy(self):
        enable = queryProxyEnable()

        if enable:
            proxyDisable()
        else:
            # 开启代理
            proxyEnable()
        self.init_enable_proxy_btn()
        self.init_pbar()
        self.init_label()

    def init_pbar(self):
        enable = queryProxyEnable()
        if enable:
            self.pbar.start()
        else:
            self.pbar.stop()

    def init_enable_proxy_btn(self):
        # 开启关闭代理
        enable = queryProxyEnable()
        if not enable:
            self.enable_proxy_btn.configure(image='play_dark', text="开启代理")
        else:
            self.enable_proxy_btn.configure(image='stop-backup-dark', text="停止代理")

    def init_other_CollapsingFrame(self, left_panel):
        # logo
        # lbl = ttk.Label(left_panel, image='proxyserver_light', style='bg.TLabel')
        # lbl.pack(side='left')

        # self.earth = ttk.Label(left_panel, width=10)
        # self.earth.pack(side='bottom')
        #
        # t1 = Thread(target=self.init_other, args=(left_panel,))
        # t1.daemon = True  # 设置p1为守护进程
        # t1.start()
        pass

    def init_other(self, left_panel):
        imgpath = Path(__file__).parent.parent / 'assets' / "earth.gif"
        self.gif = playGif(imgpath)
        self.gif.playGif(left_panel, self.earth)  # 实现动态插放

    def init_right_panel(self):
        # right panel
        right_panel = ttk.Frame(self, padding=(2, 1))
        right_panel.pack(side=RIGHT, fill=BOTH, expand=YES)

        self.init_Treeview(right_panel)
        # self.init_scrolling_text_output(right_panel)

    def init_Treeview(self, right_panel):
        ## Treeview
        coldata = [
            {"text": "ip", "stretch": True, "width": 130},
            {"text": "port", "stretch": True, "width": 50},
            {"text": "last_check_time", "stretch": True, "width": 130},
            {"text": "speed", "stretch": True, "width": 50},
            {"text": "location", "stretch": True, },
            {"text": "domestic", "stretch": True, "width": 50},
            {"text": "abroad", "stretch": True, "width": 50},
            {"text": "createTime", "stretch": True, "width": 130},
        ]
        rowdata = []
        self.tv = Tableview(
            master=right_panel,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            pagesize=34,
        )
        self.tv.pack(fill=BOTH, expand=True, pady=1)
        self._init_load_ips()

        self.tv.view.bind("<<TreeviewSelect>>", self.row_selected)

    # bind treeview selected
    def row_selected(self, event):
        try:
            iid = self.tv.get_rows(selected=True)
            ip, port, last_check, speed, local, domestic, abroad, create_time = iid[0].values

            self.ip['ip'] = ip
            self.ip['port'] = port
            self.ip['last_check'] = last_check
            self.ip['speed'] = speed
            self.ip['local'] = local
            self.ip['domestic'] = domestic
            self.ip['abroad'] = abroad

            self.ip_lbl.configure(text="ip: " + ip)
            # port
            self.port_lbl.configure(text="port: " + port)
            # speed
            self.speed_lbl.configure(text="speed: " + speed)
            # local
            self.local_lbl.configure(text="local: " + local)
            self.now_lbl.configure(text='当前可配置代理数据->speed: ' + speed)

            self.domestic_lbl.configure(text='国内代理: ')
            self.abroad_lbl.configure(text='国际代理: ')

            t1 = Thread(target=self.invaild_proxy, args=(self.ip['ip'], self.ip['port']))
            t1.daemon = True  # 设置p1为守护进程
            t1.start()

        except IndexError as e:
            logger.error(e)

    def _init_load_ips(self):
        data = select_sql()
        self.tv.insert_rows('end', data)
        self.tv.load_table_data()

    def init_scrolling_text_output(self, right_panel):
        ## scrolling text output
        scroll_cf = CollapsingFrame(right_panel)
        scroll_cf.pack(fill=BOTH, expand=YES)

        output_container = ttk.Frame(scroll_cf, padding=1)
        _value = 'Log: .........................'
        self.setvar('scroll-message', _value)
        self.st = ScrolledText(output_container)
        self.st.pack(fill=BOTH, expand=YES)
        scroll_cf.add(output_container, textvariable='scroll-message')

    def delete(self):  # 删除临时图
        self.gif.close()

    def quit(self):
        if self.downloadId.is_alive():
            pass
        if self.log_Id.is_alive():
            pass
