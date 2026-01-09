import sys, os
from PyQt6.QtWidgets import QApplication, QMainWindow

from STUi import STUi

from STController import STController
from UserData import UserData
from SliceTool import MainModel

import qdarktheme
from datetime import datetime
import logging

LOGDIR = "_Log/"


def exception_hook(exc_type, exc_value, exc_traceback):
    print(exc_type, exc_value, exc_traceback)
    exc_traceback.format_exc()
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit()


def set_up_logger():
    "Sets up a Log to write errors to"
    logdir = os.path.join(os.curdir, LOGDIR)
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    timestamp_str = datetime.now().strftime("%d-%b-%Y_%H_%M_%S")
    file_uri = os.path.join(logdir, f"Session-{timestamp_str}.log")
    logging.basicConfig(filename=file_uri)
    sys.excepthook = exception_hook


if __name__ == "__main__":

    # if hasattr(PyQt6.QtCore.Qt, 'AA_EnableHighDpiScaling'):
    #     PyQt6.QtWidgets.QApplication.setAttribute(PyQt6.QtCore.Qt.AA_EnableHighDpiScaling, True)

    # if hasattr(PyQt6.QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    #     PyQt6.QtWidgets.QApplication.setAttribute(PyQt6.QtCore.Qt.AA_UseHighDpiPixmaps, True)

    # logging
    set_up_logger()
    # qdarktheme.enable_hi_dpi()

    app = QApplication(sys.argv)
    # theming/styling
    qdarktheme.setup_theme("auto")

    # initializing the GUI
    main_window = QMainWindow()

    view = STUi(main_window)

    main_window.show()

    # Initialize main Components
    data = UserData()
    model = MainModel(data)
    controller = STController(app=app,model=model, view=view)

    # Splash Screen
    try:
        import pyi_splash

        pyi_splash.update_text("UI Loaded ...")
        pyi_splash.close()
    except:
        pass

    

    sys.exit(app.exec())
