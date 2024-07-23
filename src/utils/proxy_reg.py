import winreg
import ctypes
import logging

logger = logging.getLogger("fileAndConsole")

# 设置刷新
INTERNET_OPTION_REFRESH = 37
INTERNET_OPTION_SETTINGS_CHANGED = 39

Internet_Settings = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings'

def internet_settings():
    global other_view_flag
    try:
        INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                       Internet_Settings,
                                       0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError as e:
        import platform

        bitness = platform.architecture()[0]
        if bitness == '32bit':
            other_view_flag = winreg.KEY_WOW64_64KEY
        elif bitness == '64bit':
            other_view_flag = winreg.KEY_WOW64_32KEY
        INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Internet_Settings, access=winreg.KEY_ALL_ACCESS | other_view_flag)
    return INTERNET_SETTINGS


def set_key(name, value, type=None):
    # 如果从来没有开过代理 有可能健不存在 会报错
    # Software\Microsoft\Windows\CurrentVersion\Internet Settings
    reg_type = None
    INTERNET_SETTINGS = internet_settings()
    # 修改键值
    # try:
    #     _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    # except Exception as e:
    #     # 增加
    #     key = None
    #     try:
    #         # 创建了目录
    #         # key = winreg.CreateKeyEx(INTERNET_SETTINGS, name, reserved=0, access=winreg.KEY_ALL_ACCESS)
    #         key = winreg.CreateKey(INTERNET_SETTINGS, name)
    #     except Exception as e:
    #         logger.error(e)
    #
    #
    #     if key:
    #         try:
    #             _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    #         except Exception as e:
    #             logger.error(e)

    winreg.SetValueEx(INTERNET_SETTINGS, name, 0, type, value)



def setProxy(ProxyServer= u'127.0.0.1:8888', ProxyOverride =  u'*.local;<local>'):
    # 启用代理
    data = False
    try:
        set_key('ProxyEnable', 1, winreg.REG_DWORD)  # 启用
        data = True
        set_key('ProxyOverride', ProxyOverride, winreg.REG_SZ)  # 绕过本地
        set_key('ProxyServer', ProxyServer, winreg.REG_SZ)  # 代理IP及端口，将此代理修改为自己的代理IP
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
        internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
    except Exception as e:
        logger.error(e)
    finally:
        return data

def enable():
    set_key('ProxyEnable', 1, winreg.REG_DWORD)  # 启用
    internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)

def disable():
    # 停用代理
    set_key('ProxyEnable', 0, winreg.REG_DWORD)  # 停用
    internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)


def query(name):
    INTERNET_SETTINGS = internet_settings()
    # 修改键值
    try:
        _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    except Exception as e:
        logger.error("查询注册表失败 {}".format(e))
        return None
    return _

def queryProxyEnable():
    return query('ProxyEnable')

def queryProxyOverride():
    return query('ProxyOverride')

def queryProxyServer():
    return query('ProxyServer')
