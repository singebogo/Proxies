import logging
import sqlite3
import time

from .env import local_db

logger = logging.getLogger('fileAndConsole')


def dele():
    """删除数据"""
    Conn = sqlite3.connect(local_db())
    try:
        with Conn:
            Conn.execute('delete from ips')
            logger.info('ips表数据删除成功')
    except Exception as e:
        logger.error("ips表数据删除失败")
        dro_tb()
        conn()
    finally:
        pass


def dro_tb():
    """删除表"""
    """注意这个需要先创建成功后，才能执行"""
    Conn = sqlite3.connect(local_db())
    Cur = Conn.cursor()
    try:
        Cur.execute('drop table ips')
        Conn.commit()
        logger.info('删除表ips成功')
    except Exception as e:
        logger.error("ips表删除失败 {}".format(e))
    finally:
        Cur.close()
        Conn.close()


def conn():
    """创建数据库库"""

    Conn = sqlite3.connect(local_db())  # 连接数据库
    try:
        Conn.execute("""
                        CREATE TABLE if not exists `ips` (
                          `ip` varchar(200) primary key,
                          `port` varchar(200) DEFAULT NULL,
                          `last_check_time` DATETIME(6) NULL DEFAULT NULL,
                          `speed` varchar(200) DEFAULT NULL,
                          `location` varchar(200) DEFAULT NULL,
                          `domestic` INTEGER DEFAULT NULL,
                          `abroad` INTEGER DEFAULT NULL,
                          `createTime` timestamp NULL DEFAULT (strftime('%Y-%m-%dT%H:%M','now', 'localtime')),
                          `updateTime` timestamp NULL DEFAULT NULL
                        )  
                """)
        # 新增字段
        alter_manays()
        logger.info("ips表创建成功")
    except Exception as e:
        logger.error("ips表已经被创建")
    finally:

        Conn.close()


def alter_manays():
    sqls = [
        "ALTER TABLE 'ips' ADD COLUMN  `type` varchar(200) DEFAULT NULL",
        "ALTER TABLE 'ips' ADD COLUMN  `alive` varchar(200) DEFAULT NULL",
    ]
    for sql in sqls:
        alert_sql(sql)


def alert_sql(sql):
    # example:
    # sql = 'insert into filelist (pkgKey, dirname, filenames, filetypes) values (?, ?, ?, ?);'
    # data_list = [(1, '/etc/sysconfig', 'openshift_option', 'f'), (1, '/usr/share/doc', 'adb-utils-1.6', 'd')]
    """添加数据"""
    Conn = sqlite3.connect(local_db())
    try:
        with Conn:
            Conn.execute(sql)
            Conn.commit()
            logger.info("ips表结构更新成功{}".format(sql))
    except Exception as e:
        logger.error("ips结构更新失败 {}, sql:{}".format(e, sql))


def executemany_sql(data_list):
    # example:
    # sql = 'insert into filelist (pkgKey, dirname, filenames, filetypes) values (?, ?, ?, ?);'
    # data_list = [(1, '/etc/sysconfig', 'openshift_option', 'f'), (1, '/usr/share/doc', 'adb-utils-1.6', 'd')]
    """添加数据"""
    Conn = sqlite3.connect(local_db())
    try:
        with Conn:
            sql = """INSERT OR  REPLACE INTO `ips` (`ip`,`port`, `last_check_time`,`speed`, `location`, 
                                `domestic`,`abroad`, type, alive) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            Conn.executemany(sql, data_list)
            Conn.commit()
            logger.info("ips表插入成功{}".format(sql))
    except Exception as e:
        logger.error("ips表插入失败 {}, sql:{}".format(e, sql))


def select_sql():
    # example:
    # sql = 'insert into filelist (pkgKey, dirname, filenames, filetypes) values (?, ?, ?, ?);'
    # data_list = [(1, '/etc/sysconfig', 'openshift_option', 'f'), (1, '/usr/share/doc', 'adb-utils-1.6', 'd')]
    """添加数据"""
    global data
    Conn = sqlite3.connect(local_db())
    try:
        with Conn:
            cur = Conn.cursor()
            sql = """select `ip`,`port`,`last_check_time`,`speed`,`location`,`domestic`,`abroad`, createTime from `ips` order by last_check_time"""
            cur.execute(sql)
            data = cur.fetchall()
            logger.info("ips查询成功{}，结果 {}".format(sql, data))
    except Exception as e:
        logger.error("ips查询失败 {}, sql:{}".format(e, sql))
        data = []
    finally:
        if Conn:
            Conn.close()
        return data


def select_count_sql():
    # example:
    # sql = 'insert into filelist (pkgKey, dirname, filenames, filetypes) values (?, ?, ?, ?);'
    # data_list = [(1, '/etc/sysconfig', 'openshift_option', 'f'), (1, '/usr/share/doc', 'adb-utils-1.6', 'd')]
    """添加数据"""
    global data
    Conn = sqlite3.connect(local_db())
    try:
        with Conn:
            cur = Conn.cursor()
            sql = """select count(1) from `ips`"""
            cur.execute(sql)
            data = cur.fetchone()
            logger.info("ips查询总数成功{}，结果 {}".format(sql, data))
    except Exception as e:
        logger.error("ips查询总数失败 {}, sql:{}".format(e, sql))
        data = []
    finally:
        if Conn:
            Conn.close()
        return data


def select_speed_today_sql():
    # example:
    # sql = 'insert into filelist (pkgKey, dirname, filenames, filetypes) values (?, ?, ?, ?);'
    # data_list = [(1, '/etc/sysconfig', 'openshift_option', 'f'), (1, '/usr/share/doc', 'adb-utils-1.6', 'd')]
    """添加数据"""
    global data
    Conn = sqlite3.connect(local_db())
    today = time.strftime("%Y-%m-%d", time.localtime())
    try:
        with Conn:
            cur = Conn.cursor()
            sql = """select `ip`,`port`,`last_check_time`,`speed`,`location`,`domestic`,`abroad`, `type` from ips where speed in (select max(speed) from `ips`)"""
            cur.execute(sql)
            data = cur.fetchone()
            logger.info("ips查询今日总数成功{}，结果 {}".format(sql, data))
    except Exception as e:
        logger.error("ips查询今日总数失败 {}, sql:{}".format(e, sql))
        data = []
    finally:
        if Conn:
            Conn.close()
        return data


def select_count_today_sql():
    # example:
    # sql = 'insert into filelist (pkgKey, dirname, filenames, filetypes) values (?, ?, ?, ?);'
    # data_list = [(1, '/etc/sysconfig', 'openshift_option', 'f'), (1, '/usr/share/doc', 'adb-utils-1.6', 'd')]
    """添加数据"""
    global data
    Conn = sqlite3.connect(local_db())
    today = time.strftime("%Y-%m-%d", time.localtime())
    try:
        with Conn:
            cur = Conn.cursor()
            sql = """select count(1) from `ips` where last_check_time like '{}%'""".format(today)
            cur.execute(sql)
            data = cur.fetchone()
            logger.info("ips查询今日总数成功{}，结果 {}".format(sql, data))
    except Exception as e:
        logger.error("ips查询今日总数失败 {}, sql:{}".format(e, sql))
        data = []
    finally:
        if Conn:
            Conn.close()
        return data


def select_lastest_sql():
    # example:
    # sql = 'insert into filelist (pkgKey, dirname, filenames, filetypes) values (?, ?, ?, ?);'
    # data_list = [(1, '/etc/sysconfig', 'openshift_option', 'f'), (1, '/usr/share/doc', 'adb-utils-1.6', 'd')]
    """添加数据"""
    global data
    Conn = sqlite3.connect(local_db())
    try:
        with Conn:
            cur = Conn.cursor()
            sql = """select MAX (createTime) AS lastest from `ips` """
            cur.execute(sql)
            data = cur.fetchone()
            logger.info("ips查询最近一次抓取数据时间成功{}，结果 {}".format(sql, data))
    except Exception as e:
        logger.error("ips查询最近一次抓取数据时间失败 {}, sql:{}".format(e, sql))
        data = []
    finally:
        if Conn:
            Conn.close()
        return data
