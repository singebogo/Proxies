import logging
from pathlib import Path
from appdirs import *

logger = logging.getLogger('fileAndConsole')

def home():
    appauthor = os.getlogin()
    home_path =  user_data_dir("Proxies", appauthor, roaming=True)
    if not os.path.exists(home_path):
        logger.info("home目录下Proxies应用文件夹不存在")
        try:
            os.makedirs(home_path)
            logger.error("home目录下Proxies应用文件夹创建成功")
        except Exception as e:
            logger.error("home目录下Proxies应用文件夹创建失败 {}".format(e))
    return home_path

def local_db():
    return Path(home() + os.sep + "ips.db")