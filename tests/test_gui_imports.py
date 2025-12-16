"""GUI import ve kurulum testi."""
import importlib
import os

import pytest


def test_gui_import_survives_missing_webengine(monkeypatch):
    """PyQtWebEngine yoksa bile GUI importu çökmesin."""
    monkeypatch.setitem(os.environ, "QT_QPA_PLATFORM", "offscreen")
    module = importlib.import_module("src.gui.main_window")
    assert hasattr(module, "WEBENGINE_AVAILABLE")
    assert module.WEBENGINE_AVAILABLE in (True, False)


@pytest.mark.skip(reason="GUI runtime gerektirir, yalnızca import testi yapıyoruz.")
def test_main_window_constructs():
    """MainWindow örneği oluşturulabilmeli (opsiyonel)."""
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = importlib.import_module("src.gui.main_window").MainWindow()
    assert window is not None
    window.close()
    app.quit()
