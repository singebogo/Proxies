import tkinter
from PIL import Image, ImageTk
from PIL import ImageSequence
import random  # 随机模块
import os, sys  # 系统模块
from .env import home

STR_FRAME_FILENAME = "frame{}.png"  # 每帧图片的文件名格式


class playGif():
    def __init__(self, file, temporary=""):  # temporary 指临时目录路径，为空时则随机生成
        self.__strPath = file
        self.__index = 1  # 当前显示图片的帧数

        if len(temporary) == 0:
            self.strTemporaryFolder, self.empty = self.crearteTemporaryFolder()  # 随机得到临时目录
        else:
            self.strTemporaryFolder = temporary  # 指定的临时目录

        self.__intCount = 0  # gif 文件的帧数
        self.decomposePics()  # 开始分解

    def crearteTemporaryFolder(self):  # 生成临时目录名返回
        # 获取当前调用模块主程序的运行目录
        h = home()

        def createRandomFolder(strSelfPath):  # 内嵌方法，生成随机目录用
            return os.mkdir(strSelfPath)

        # 获取当前软件目录
        folder = os.path.join(h, "earthGif")
        if not os.path.isdir(folder):  # 已存在
            createRandomFolder(folder)

        return folder, self.is_empty_file(folder)

    def is_empty_file(self, file_path: str):
        return os.stat(file_path).st_size == 0

    def decomposePics(self):  # 分解 gif 文件的每一帧到独立的图片文件，存在临时目录中
        i = 0
        img = Image.open(self.__strPath)
        self.__width, self.__height = img.size  # 得到图片的尺寸

        if not os.path.isdir(self.strTemporaryFolder):  # 已存在
            os.mkdir(self.strTemporaryFolder)  # 创建临时目录
        for frame in ImageSequence.Iterator(img):  # 遍历每帧图片
            frame.save(os.path.join(self.strTemporaryFolder, STR_FRAME_FILENAME.format(i + 1)))  # 保存独立图片
            i += 1

        self.__intCount = i  # 得到 gif 的帧数
        #

    def getPicture(self, frame=0):  # 返回第 frame 帧的图片(width=0,height=0)
        if frame == 0:
            frame = self.__index
        elif frame >= self.__intCount:
            frame = self.__intCount  # 最后一张

        img = tkinter.PhotoImage(file=os.path.join(self.strTemporaryFolder, STR_FRAME_FILENAME.format(frame)))
        # 按比例缩小图像
        resized_image_subsample = img.subsample(3, 3)

        # 按具体缩放级别缩小图像
        # resized_image_zoom = img.zoom(2, 2)
        self.__index = self.getNextFrameIndex()

        return resized_image_subsample  # 返回图片

        #

    def getNextFrameIndex(self, frame=0):  # 返回下一张的帧数序号
        if frame == 0:
            frame = self.__index  # 按当前插入帧数

        if frame == self.__intCount:
            return 1  # 返回第1张，即从新开始播放
        else:
            return frame + 1  # 下一张
        #

    def playGif(self, tk, widget, time=100):  # 开始调用自身实现播放，time 单位为毫秒
        img = self.getPicture()
        widget.config(image=img)
        widget.image = img
        self.timer = tk.after(time, self.playGif, tk, widget, time)  # 在 time 时间后调用自身

    def stop(self, widget):
        widget.after_cancel(self.timer)

    def close(self):  # 关闭动画文件，删除临时文件及目录
        files = os.listdir(self.strTemporaryFolder)
        for file in files:
            os.remove(os.path.join(self.strTemporaryFolder, file))

        os.rmdir(self.strTemporaryFolder)