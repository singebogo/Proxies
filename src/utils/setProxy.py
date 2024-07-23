import winreg
import ctypes


# 设置刷新
INTERNET_OPTION_REFRESH = 37
INTERNET_OPTION_SETTINGS_CHANGED = 39

def set_key(name, value, type=None):
    # 如果从来没有开过代理 有可能健不存在 会报错
    # Software\Microsoft\Windows\CurrentVersion\Internet Settings
    global reg_type
    INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                       r'\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings',
                                       0, winreg.KEY_ALL_ACCESS)
    # 修改键值
    try:
        _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    except Exception as e:
        # 增加
        key = winreg.CreateKeyEx(INTERNET_SETTINGS, name)
        if key:
            _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    finally:
        winreg.SetValueEx(INTERNET_SETTINGS, name, 0, type if type else reg_type, value)

def enable():
    # 启用代理
    set_key('ProxyEnable', 1)  # 启用
    set_key('ProxyOverride', u'*.local;<local>', winreg.REG_SZ)  # 绕过本地
    set_key('ProxyServer', u'127.0.0.1:8888')  # 代理IP及端口，将此代理修改为自己的代理IP
    internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)

def disable():
    # 停用代理
    set_key('ProxyEnable', 0)  # 停用
    internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
