import base64
"""
    将图片转换数据
"""


def pic_transform(picture_name):
    #将图片转换问base64码
    open_pic = open("%s" % picture_name, 'rb')
    b64str = base64.b64encode(open_pic.read())
    open_pic.close()
    return b64str
