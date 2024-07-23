from src.gui.app import App
from src.gui.gui import Proxies

if __name__ == '__main__':
    app = App()
    Proxies(app)
    app.mainloop()