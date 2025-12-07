"""PyQt5 ana pencere; pipeline sonuçlarını güvenli şekilde görselleştirir."""
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView  # type: ignore

from src.pipeline.pipeline import AnalysisArtifacts, PipelineConfig, run_basic_pipeline
from src.visualization.plot_fft import compute_fft
from src.simulation.mag_simulator import generate_simulated_rotation


class MatplotlibPane(QtWidgets.QWidget):
    """Matplotlib kanvas ve toolbar taşıyan yardımcı sınıf."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class MainWindow(QtWidgets.QMainWindow):
    """Aviyonik sensör analizi için ana GUI penceresi."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMU–GPS–Magnetometer Analyzer")
        self.setMinimumSize(1200, 700)
        self.resize(1300, 850)
        self.status_bar = self.statusBar()
        self._status("Hazır")
        self.synthetic_label = QtWidgets.QLabel("")
        self.synthetic_label.setStyleSheet("color: darkred;")

        self._build_references()
        self.setup_ui()
        self.connect_buttons()

    def _build_references(self) -> None:
        """Widget referanslarını başlatır."""
        self.input_edit: Optional[QtWidgets.QLineEdit] = None
        self.time_edit: Optional[QtWidgets.QLineEdit] = None
        self.resample_edit: Optional[QtWidgets.QLineEdit] = None
        self.summary_cb: Optional[QtWidgets.QCheckBox] = None
        self.fft_cb: Optional[QtWidgets.QCheckBox] = None
        self.heading_cb: Optional[QtWidgets.QCheckBox] = None
        self.calib_cb: Optional[QtWidgets.QCheckBox] = None
        self.run_btn: Optional[QtWidgets.QPushButton] = None
        self.simulate_btn: Optional[QtWidgets.QPushButton] = None

        self.tabs: Optional[QtWidgets.QTabWidget] = None
        self.summary_table: Optional[QtWidgets.QTableWidget] = None
        self.summary_text: Optional[QtWidgets.QTextEdit] = None
        self.timeseries_tab: Optional[MatplotlibPane] = None
        self.fft_tab: Optional[MatplotlibPane] = None
        self.heading_tab: Optional[MatplotlibPane] = None
        self.heading_text: Optional[QtWidgets.QTextEdit] = None
        self.heading_metrics: Optional[QtWidgets.QTextEdit] = None
        self.calibration_tab: Optional[MatplotlibPane] = None
        self.calib_text: Optional[QtWidgets.QTextEdit] = None
        self.calib_metrics: Optional[QtWidgets.QTextEdit] = None
        self.fft_web: Optional[QWebEngineView] = None

    def setup_ui(self) -> None:
        """Ana yerleşimi kurar."""
        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout()
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_widget.setLayout(control_layout)

        self.input_edit = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Gözat")
        browse_btn.clicked.connect(self._browse_file)
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(QtWidgets.QLabel("Giriş CSV"))
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(browse_btn)
        control_layout.addLayout(input_layout)

        self.time_edit = QtWidgets.QLineEdit("timestamp")
        self.resample_edit = QtWidgets.QLineEdit("10ms")
        control_layout.addWidget(QtWidgets.QLabel("Zaman Kolonu"))
        control_layout.addWidget(self.time_edit)
        control_layout.addWidget(QtWidgets.QLabel("Resample Aralığı"))
        control_layout.addWidget(self.resample_edit)

        self.summary_cb = QtWidgets.QCheckBox("Özet")
        self.summary_cb.setChecked(True)
        self.fft_cb = QtWidgets.QCheckBox("FFT Analizi")
        self.fft_cb.setChecked(True)
        self.heading_cb = QtWidgets.QCheckBox("Heading Hesapla")
        self.heading_cb.setChecked(True)
        self.calib_cb = QtWidgets.QCheckBox("Manyetometre Kalibrasyonu")
        self.calib_cb.setChecked(True)
        control_layout.addWidget(self.summary_cb)
        control_layout.addWidget(self.fft_cb)
        control_layout.addWidget(self.heading_cb)
        control_layout.addWidget(self.calib_cb)

        self.run_btn = QtWidgets.QPushButton("Analizi Çalıştır")
        self.simulate_btn = QtWidgets.QPushButton("Sentetik Veri Üret ve Analiz Et")
        for btn in (self.run_btn, self.simulate_btn):
            btn.setMinimumWidth(200)
        control_layout.addWidget(self.run_btn)
        control_layout.addWidget(self.simulate_btn)
        control_layout.addWidget(self.synthetic_label)
        control_layout.addStretch()

        self.tabs = QtWidgets.QTabWidget()
        self.summary_tab = QtWidgets.QWidget()
        self.timeseries_tab = MatplotlibPane()
        self.fft_tab = MatplotlibPane()
        self.heading_tab = MatplotlibPane()
        self.calibration_tab = MatplotlibPane()
        self.fft_web = QWebEngineView()
        self.fft_web.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.summary_table = QtWidgets.QTableWidget()
        self.summary_text = QtWidgets.QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout = QtWidgets.QVBoxLayout()
        summary_layout.addWidget(self.summary_table)
        summary_layout.addWidget(self.summary_text)
        self.summary_tab.setLayout(summary_layout)

        self.heading_text = QtWidgets.QTextEdit()
        self.heading_text.setReadOnly(True)
        self.heading_text.setMaximumHeight(120)
        self.heading_metrics = QtWidgets.QTextEdit()
        self.heading_metrics.setReadOnly(True)
        self.heading_metrics.setMaximumHeight(120)
        heading_layout = QtWidgets.QVBoxLayout()
        heading_layout.addWidget(self.heading_tab.toolbar)
        heading_layout.addWidget(self.heading_tab.canvas)
        heading_layout.addWidget(self.heading_text)
        heading_layout.addWidget(self.heading_metrics)
        heading_wrapper = QtWidgets.QWidget()
        heading_wrapper.setLayout(heading_layout)

        self.calib_text = QtWidgets.QTextEdit()
        self.calib_text.setReadOnly(True)
        self.calib_text.setMaximumHeight(140)
        self.calib_metrics = QtWidgets.QTextEdit()
        self.calib_metrics.setReadOnly(True)
        self.calib_metrics.setMaximumHeight(120)
        calib_layout = QtWidgets.QVBoxLayout()
        calib_layout.addWidget(self.calibration_tab.toolbar)
        calib_layout.addWidget(self.calibration_tab.canvas)
        calib_layout.addWidget(self.calib_text)
        calib_layout.addWidget(self.calib_metrics)
        calib_wrapper = QtWidgets.QWidget()
        calib_wrapper.setLayout(calib_layout)

        fft_layout = QtWidgets.QVBoxLayout()
        fft_layout.addWidget(self.fft_tab.toolbar)
        fft_layout.addWidget(self.fft_tab.canvas)
        fft_layout.addWidget(self.fft_web)
        fft_wrapper = QtWidgets.QWidget()
        fft_wrapper.setLayout(fft_layout)

        self.tabs.addTab(self.summary_tab, "Veri Özeti")
        self.tabs.addTab(self.timeseries_tab, "Zaman Serisi")
        self.tabs.addTab(fft_wrapper, "FFT")
        self.tabs.addTab(heading_wrapper, "Heading")
        self.tabs.addTab(calib_wrapper, "Kalibrasyon")

        main_layout.addWidget(control_widget, 1)
        main_layout.addWidget(self.tabs, 3)

    def connect_buttons(self) -> None:
        """Buton sinyallerini bağlar."""
        if self.run_btn:
            self.run_btn.clicked.connect(self._safe_run_analysis)
        if self.simulate_btn:
            self.simulate_btn.clicked.connect(self._safe_run_synthetic)

    def _safe_run_analysis(self) -> None:
        """Analiz tetikleyicisini güvenli şekilde çalıştırır."""
        try:
            self.run_analysis()
        except Exception as exc:  # pylint: disable=broad-except
            self._status(f"Hata: {exc}", is_error=True)
            QtWidgets.QMessageBox.critical(self, "Hata", str(exc))

    def _safe_run_synthetic(self) -> None:
        """Sentetik tetikleyicisini güvenli şekilde çalıştırır."""
        try:
            self.run_synthetic()
        except Exception as exc:  # pylint: disable=broad-except
            self._status(f"Hata: {exc}", is_error=True)
            QtWidgets.QMessageBox.critical(self, "Hata", str(exc))

    def _browse_file(self) -> None:
        """CSV dosya seçici."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "CSV seç", "", "CSV Files (*.csv)")
        if path and self.input_edit:
            self.input_edit.setText(path)

    def _status(self, message: str, is_error: bool = False) -> None:
        """Durum mesajı günceller."""
        if is_error:
            self.status_bar.setStyleSheet("color: #ff6b6b;")
        else:
            self.status_bar.setStyleSheet("color: #e0e0e0;")
        self.status_bar.showMessage(message, 7000)

    def _build_config(self, path: Path) -> PipelineConfig:
        """GUI girdilerinden pipeline konfigürasyonu oluşturur."""
        time_col = self.time_edit.text().strip() if self.time_edit else "timestamp"
        resample = self.resample_edit.text().strip() if self.resample_edit else "10ms"
        return PipelineConfig(
            input_path=path,
            time_column=time_col or "timestamp",
            resample_rate=resample or "10ms",
            normalize=True,
            compute_fft=self.fft_cb.isChecked() if self.fft_cb else True,
        )

    def run_analysis(self) -> None:
        """Analiz akışını çalıştırır."""
        if not self.input_edit:
            return
        path_text = self.input_edit.text().strip()
        if not path_text:
            raise ValueError("CSV dosyası seçilmedi.")
        path = Path(path_text)
        if not path.exists():
            raise FileNotFoundError("Seçilen CSV dosyası mevcut değil.")

        cfg = self._build_config(path)
        self._status("Analiz başlatıldı")
        try:
            artifacts = run_basic_pipeline(cfg)
        except Exception as exc:  # pylint: disable=broad-except
            self._status(f"Hata: {exc}", is_error=True)
            QtWidgets.QMessageBox.critical(self, "Hata", str(exc))
            self._status("Hata oluştu.", is_error=True)
            return
        self._status("Analiz tamamlandı")
        self.update_tabs(artifacts, cfg)

    def run_synthetic(self) -> None:
        """Sentetik veri üretip analizi çalıştırır."""
        out_path = Path("example_logs/simulated_rotation.csv")
        try:
            generate_simulated_rotation(out_path=out_path)
        except Exception as exc:  # pylint: disable=broad-except
            self._status(f"Hata: {exc}", is_error=True)
            QtWidgets.QMessageBox.critical(self, "Hata", f"Sentetik veri üretilemedi: {exc}")
            return
        if self.input_edit:
            self.input_edit.setText(str(out_path))
        self.synthetic_label.setText("Kaynak: Sentetik veri")
        self.run_analysis()

    def update_tabs(self, artifacts: Optional[AnalysisArtifacts], cfg: PipelineConfig) -> None:
        """Sekmeleri pipeline çıktısı ile günceller."""
        if artifacts is None:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Analiz çıktısı yok.")
            return
        time_col = cfg.time_column

        try:
            if self.summary_cb and self.summary_cb.isChecked():
                self._update_summary_tab(artifacts, time_col)
        except Exception as exc:
            self._status(f"Özet sekmesi hatası: {exc}", is_error=True)
        try:
            self._update_timeseries_tab(artifacts, time_col)
        except Exception as exc:
            self._status(f"Zaman serisi hatası: {exc}", is_error=True)
        try:
            self._update_fft_tab(artifacts, time_col, cfg.compute_fft)
        except Exception as exc:
            self._status(f"FFT hatası: {exc}", is_error=True)
        try:
            if self.heading_cb and self.heading_cb.isChecked():
                self._update_heading_tab(artifacts, time_col)
            else:
                self._clear_heading_tab("Heading hesaplanmadı.")
        except Exception as exc:
            self._status(f"Heading hatası: {exc}", is_error=True)
        try:
            if self.calib_cb and self.calib_cb.isChecked():
                self._update_calibration_tab(artifacts)
            else:
                self._clear_calibration_tab("Kalibrasyon seçili değil.")
        except Exception as exc:
            self._status(f"Kalibrasyon hatası: {exc}", is_error=True)

    def _update_summary_tab(self, artifacts: AnalysisArtifacts, time_column: str) -> None:
        """Veri özet sekmesini günceller."""
        if artifacts.synced_main_df is None or self.summary_table is None or self.summary_text is None:
            return
        df = artifacts.synced_main_df
        head = df.head(50)
        self.summary_table.setRowCount(len(head))
        self.summary_table.setColumnCount(len(head.columns))
        self.summary_table.setHorizontalHeaderLabels(head.columns)
        for i, (_, row) in enumerate(head.iterrows()):
            for j, val in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(val))
                self.summary_table.setItem(i, j, item)
        self.summary_table.resizeColumnsToContents()

        descr = df.describe(include="all").to_string()
        row_count = len(df)
        dt = pd.to_datetime(df[time_column]).diff().dt.total_seconds().dropna()
        median_dt = dt.median() if not dt.empty else 0
        text = (
            f"Satır sayısı: {row_count}\n"
            f"Medyan örnekleme aralığı (s): {median_dt}\n"
            f"describe():\n{descr}"
        )
        self.summary_text.setPlainText(text)

    def _update_timeseries_tab(self, artifacts: AnalysisArtifacts, time_column: str) -> None:
        """Zaman serisi sekmesini günceller."""
        if artifacts.synced_main_df is None or self.timeseries_tab is None:
            return
        df = artifacts.synced_main_df
        fig = self.timeseries_tab.figure
        fig.clear()
        ax = fig.add_subplot(111)

        candidates = ["accel_x", "accel_y", "accel_z", "mag_x", "mag_y", "mag_z", "gyro_z"]
        time_vals = pd.to_datetime(df[time_column])
        plotted = False
        for col in candidates:
            if col in df.columns:
                ax.plot(time_vals, df[col], label=col)
                plotted = True
        if not plotted:
            ax.text(0.5, 0.5, "Çizilecek kolon yok", ha="center", va="center", transform=ax.transAxes)
        else:
            ax.legend()
        ax.set_xlabel("Zaman")
        ax.set_ylabel("Değer")
        ax.set_title("Zaman Serisi")
        fig.autofmt_xdate()
        self.timeseries_tab.canvas.draw()

    def _update_fft_tab(self, artifacts: AnalysisArtifacts, time_column: str, enabled: bool) -> None:
        """FFT sekmesini günceller ve Plotly çıktısını embed eder."""
        if self.fft_tab is None:
            return
        fig = self.fft_tab.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if not enabled:
            ax.text(0.5, 0.5, "FFT seçilmedi", ha="center", va="center", transform=ax.transAxes)
            self.fft_tab.canvas.draw()
            return
        df = artifacts.synced_main_df
        if df is None:
            ax.text(0.5, 0.5, "Veri yok", ha="center", va="center", transform=ax.transAxes)
            self.fft_tab.canvas.draw()
            return
        numeric_cols = df.select_dtypes(include=["number"]).columns
        try:
            fft_df = compute_fft(df, time_column=time_column, value_columns=numeric_cols)
            for col in numeric_cols:
                if col in fft_df:
                    ax.plot(fft_df["frequency"], fft_df[col], label=col)
            ax.set_xlabel("Frekans (Hz)")
            ax.set_ylabel("Genlik")
            ax.set_title("FFT Spektrumu")
            ax.legend()
        except Exception as exc:  # pylint: disable=broad-except
            ax.text(0.5, 0.5, f"FFT hesaplanamadı: {exc}", ha="center", va="center", transform=ax.transAxes)
        self.fft_tab.canvas.draw()

        if self.fft_web is not None:
            try:
                if artifacts.fft_figure is not None:
                    import plotly.io as pio

                    html = pio.to_html(artifacts.fft_figure, full_html=False)
                    self.fft_web.setHtml(html)
                else:
                    self.fft_web.setHtml("<html><body>Plotly figürü yok</body></html>")
            except Exception as exc:  # pylint: disable=broad-except
                self._status(f"Plotly grafiği yüklenemedi: {exc}", is_error=True)
                QtWidgets.QMessageBox.critical(self, "Hata", f"Plotly grafiği yüklenemedi: {exc}")

    def _clear_heading_tab(self, message: str) -> None:
        """Heading sekmesini temizler."""
        if self.heading_tab is None or self.heading_text is None or self.heading_metrics is None:
            return
        fig = self.heading_tab.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
        self.heading_text.setPlainText(message)
        self.heading_metrics.setPlainText(message)
        self.heading_tab.canvas.draw()

    def _update_heading_tab(self, artifacts: AnalysisArtifacts, time_column: str) -> None:
        """Heading sekmesini günceller."""
        if self.heading_tab is None or self.heading_text is None or self.heading_metrics is None:
            return
        if artifacts.fused_heading is None or artifacts.mag_heading is None or artifacts.synced_main_df is None:
            self._clear_heading_tab("Heading verisi yok")
            return
        df = artifacts.synced_main_df
        time_vals = pd.to_datetime(df[time_column])
        fused = artifacts.fused_heading.reindex(df.index).ffill().bfill()
        mag = artifacts.mag_heading.reindex(df.index).ffill().bfill()

        fig = self.heading_tab.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.plot(time_vals, fused, label="Fused heading")
        ax.plot(time_vals, mag, label="Mag heading", alpha=0.7)
        ax.set_title("Heading")
        ax.set_xlabel("Zaman")
        ax.set_ylabel("Derece")
        ax.legend()
        fig.autofmt_xdate()
        self.heading_tab.canvas.draw()

        try:
            first_vals = fused.head(5).round(2).to_list()
            total_rot = float(np.unwrap(np.deg2rad(fused)).ptp() * 180 / np.pi)
            summary = (
                f"İlk 5 değer: {first_vals}\n"
                f"Min/Max: {fused.min():.2f} / {fused.max():.2f}\n"
                f"Toplam açı değişimi: {total_rot:.2f} derece"
            )
        except Exception:
            summary = "Heading özetlenemedi."
        self.heading_text.setPlainText(summary)

        # Ek metrikler: drift, hata, stabilite
        drift_deg_s = float(df["gyro_z"].mean() * 180 / np.pi) if "gyro_z" in df else np.nan
        avg_err = float((fused - mag).abs().mean()) if len(fused) else np.nan
        stability_score = "Low"
        if not fused.empty:
            std = fused.std()
            if std < 3:
                stability_score = "High"
            elif std < 8:
                stability_score = "Medium"
        metrics_txt = (
            f"Gyro drift tahmini (deg/s): {drift_deg_s:.3f}\n"
            f"Ortalama manyetik hata (deg): {avg_err:.3f}\n"
            f"Fused heading stabilitesi: {stability_score}"
        )
        self.heading_metrics.setPlainText(metrics_txt)

    def _clear_calibration_tab(self, message: str) -> None:
        """Kalibrasyon sekmesini temizler."""
        if self.calibration_tab is None or self.calib_text is None or self.calib_metrics is None:
            return
        fig = self.calibration_tab.figure
        fig.clear()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
        self.calib_text.setPlainText(message)
        self.calib_metrics.setPlainText(message)
        self.calibration_tab.canvas.draw()

    def _update_calibration_tab(self, artifacts: AnalysisArtifacts) -> None:
        """Kalibrasyon sekmesini günceller."""
        if self.calibration_tab is None or self.calib_text is None or self.calib_metrics is None:
            return
        fig = self.calibration_tab.figure
        fig.clear()
        ax = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        raw = artifacts.raw_df
        if raw is None or not all(col in raw.columns for col in ["mag_x", "mag_y", "mag_z"]):
            self._clear_calibration_tab("Manyetometre verisi yok")
            return

        ax.scatter(raw["mag_x"], raw["mag_y"], s=6, alpha=0.6, label="Ham")
        ax.set_title("Ham XY")
        ax.set_xlabel("mag_x")
        ax.set_ylabel("mag_y")

        if artifacts.mag_corrected_df is not None:
            ax2.scatter(
                artifacts.mag_corrected_df["mag_x"],
                artifacts.mag_corrected_df["mag_y"],
                s=6,
                alpha=0.6,
                color="green",
                label="Kalibre",
            )
            ax2.set_title("Kalibre XY")
        else:
            ax2.text(0.5, 0.5, "Kalibre veri yok", ha="center", va="center", transform=ax2.transAxes)
        ax2.set_xlabel("mag_x")
        ax2.set_ylabel("mag_y")
        fig.tight_layout()
        self.calibration_tab.canvas.draw()

        center_txt = (
            f"Hard-iron merkez: {artifacts.mag_center.tolist()}\n"
            if artifacts.mag_center is not None
            else "Hard-iron merkez: Yok\n"
        )
        matrix_txt = (
            f"Soft-iron matris:\n{artifacts.mag_transform_matrix}\n"
            if artifacts.mag_transform_matrix is not None
            else "Soft-iron matris: Yok\n"
        )
        self.calib_text.setPlainText(center_txt + matrix_txt)

        # Kalite kutusu
        cond_num = np.linalg.cond(artifacts.mag_transform_matrix) if artifacts.mag_transform_matrix is not None else np.nan
        offset_mag = float(np.linalg.norm(artifacts.mag_center)) if artifacts.mag_center is not None else np.nan
        sufficiency = "OK" if artifacts.raw_df is not None and len(artifacts.raw_df) >= 50 else "Low"
        metrics = (
            f"Soft-iron koşul sayısı: {cond_num:.2f}\n"
            f"Hard-iron offset büyüklüğü: {offset_mag:.2f}\n"
            f"Veri yeterliliği: {sufficiency}"
        )
        self.calib_metrics.setPlainText(metrics)
