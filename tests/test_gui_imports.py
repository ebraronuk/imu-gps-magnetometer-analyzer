"""GUI import ve kurulum testi."""
from PyQt5 import QtWidgets

from src.gui.main_window import MainWindow


def test_main_window_constructs():
    """MainWindow örneği oluşturulabilmeli."""
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    assert window is not None
    window.close()
    app.quit()
