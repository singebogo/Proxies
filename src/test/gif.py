# -*-coding:utf-8 -*-
"""
GIF 动画文件播放模块
能配合 tkinter.Label 组件播放动态图

实现原理：将gif 动太按帧数分解成独立临时图片，再分别显示
最后再删除临时图片
    """

import tkinter
from PIL import Image, ImageTk
from PIL import ImageSequence
import random  # 随机模块
import os, sys  # 系统模块

STR_FRAME_FILENAME = "frame{}.png"  # 每帧图片的文件名格式


class playGif():
    def __init__(self, file, temporary=""):  # temporary 指临时目录路径，为空时则随机生成
        self.__strPath = file
        self.__index = 1  # 当前显示图片的帧数

        if len(temporary) == 0:
            self.strTemporaryFolder = self.crearteTemporaryFolder()  # 随机得到临时目录
        else:
            self.strTemporaryFolder = temporary  # 指定的临时目录

        self.__intCount = 0  # gif 文件的帧数

        self.decomposePics()  # 开始分解

        #

    def crearteTemporaryFolder(self):  # 生成临时目录名返回
        # 获取当前调用模块主程序的运行目录
        strSelfPath = str(os.path.dirname(os.path.realpath(sys.argv[0])))
        if len(strSelfPath) == 0:
            strSelfPath = os.path.join(os.getcwd())

        def createRandomFolder(strSelfPath):  # 内嵌方法，生成随机目录用
            length = random.randint(5, 10)  # 随机长度
            path = ""
            for i in range(length):
                path = path + chr(random.randint(97, 122))  # 随机生成a-z字母

            return os.path.join(strSelfPath, path)
            #

        # 获取当前软件目录

        folder = createRandomFolder(strSelfPath)
        while os.path.isdir(folder):  # 已存在
            folder = createRandomFolder(strSelfPath)

        return folder
        #

    def decomposePics(self):  # 分解 gif 文件的每一帧到独立的图片文件，存在临时目录中
        i = 0
        img = Image.open(self.__strPath)
        self.__width, self.__height = img.size  # 得到图片的尺寸

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
        self.__index = self.getNextFrameIndex()

        return img  # 返回图片

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
        tk.after(time, self.playGif, tk, widget, time)  # 在 time 时间后调用自身

        #

    def close(self):  # 关闭动画文件，删除临时文件及目录
        files = os.listdir(self.strTemporaryFolder)
        for file in files:
            os.remove(os.path.join(self.strTemporaryFolder, file))

        os.rmdir(self.strTemporaryFolder)

        #


if __name__ == "__main__":
    import tkinter


    def delete():  # 删除临时图
        root.destroy()
        gif.close()


    file = r"move.gif"
    root = tkinter.Tk()
    label = tkinter.Label(root,  bg="#FFFFFF")
    label.pack(side=tkinter.LEFT)
    # button = tkinter.Button(root)
    # button.pack(side=tkinter.LEFT)
    # root.protocol('WM_DELETE_WINDOW', delete)  #####【重要】关闭窗口后的事件：delete

    gif = playGif(file)
    # label.config(image=gif.getPicture())

    gif.playGif(root, label)  # 实现动态插放

    root.mainloop()

