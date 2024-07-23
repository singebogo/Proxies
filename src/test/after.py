import tkinter as tk

stop_running = True

def do_something():
    # 执行一些操作
    print("正在执行函数...")
    # 完成后停止 Tkinter 运行
    global stop_running
    stop_running = False

root = tk.Tk()

# 创建按钮，点击时执行 do_something() 函数
button = tk.Button(root, text="点击执行函数", command=do_something)
button.pack()

while stop_running:
    root.update()

root.mainloop()
