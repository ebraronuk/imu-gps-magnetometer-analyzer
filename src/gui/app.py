"""PyQt5 GUI uygulama başlatıcısı."""
import sys
from PyQt5 import QtWidgets

from src.gui.main_window import MainWindow


def run_gui() -> None:
    """GUI uygulamasını başlatır ve ana pencereyi gösterir."""
    app = QtWidgets.QApplication(sys.argv)
    dark_qss = """
    QWidget { background-color: #202225; color: #e0e0e0; }
    QLineEdit, QTextEdit, QPlainTextEdit, QTableWidget, QTabWidget::pane {
        background-color: #2c2f33; color: #e0e0e0; selection-background-color: #5865f2;
    }
    QTabBar::tab { background: #2c2f33; color: #e0e0e0; padding: 8px; }
    QTabBar::tab:selected { background: #5865f2; color: #ffffff; }
    QPushButton { background-color: #5865f2; color: #ffffff; border: 1px solid #4450c7; padding: 8px 14px; min-width: 200px; }
    QPushButton:hover { background-color: #4a56c9; }
    QCheckBox { padding: 4px; }
    QStatusBar { background: #111214; color: #e0e0e0; }
    QToolBar, QMenuBar { background: #111214; color: #e0e0e0; }
    """
    app.setStyleSheet(dark_qss)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
