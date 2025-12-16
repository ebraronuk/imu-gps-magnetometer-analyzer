# IMU-GPS-Magnetometer Analyzer - Sistem Mimarisi

Bu belge, core pipeline mimarisini ve CLI/GUI akışlarının nasıl aynı çekirdeği kullandığını özetler. Amaç, avionik sensör preprocessing zincirinin teknik ayrıştırmasını ve bağımlılık sınırlarını netleştirmektir.

## Genel Akış
```
RAW LOGS -> CSV Loader -> Time Sync/Resample -> Calibration -> Orientation -> FFT -> Visualization/Report
```

## CLI Akışı (src/main.py)
```
argparse -> PipelineConfig (config_builder) -> run_basic_pipeline -> AnalysisArtifacts -> (summary/plots/report)
```

## GUI Akışı
```
PyQt5 GUI -> PipelineConfig (config_builder) -> run_basic_pipeline -> AnalysisArtifacts -> Sekmeler
```
- GUI, pipeline’ın frontend katmanı; hesaplama backend pipeline’da kalır.
- WebEngine sadece GUI’de kullanılır (Plotly embed). CLI bağımsızdır.

## GUI Önkoşulları ve Fallback
- Kurulum: `pip install -r requirements-gui.txt` (PyQt5 + PyQtWebEngine).
- WebEngine varsa Plotly içerde gömülü; yoksa FFT/Plotly `reports/` altına yazılır ve sistem tarayıcısında açılır. Uygulama kapanmaz, status bar/mesaj kutusu Türkçe bilgi verir.

## AnalysisArtifacts
- Pipeline çıktılarının konteyneri: ham ve senkronize DataFrame’ler, normalize edilmiş veri, kalibrasyon çıktıları (center, transform), heading serileri, FFT figürü, görselleştirme tabloları.
- CLI ve GUI aynı nesneyi tüketir; hesaplama tek yerde tutulur.

## Katmanlar ve Modüller
- `data_loaders/csv_loader.py`: CSV doğrulama, timestamp parse.
- `preprocessing/time_sync.py`, `preprocessing/normalization.py`: zaman ızgarası, resample, opsiyonel z-score.
- `calibration/*`: hard/soft-iron, ellipsoid fit, PSD reg, IMU bias.
- `orientation/orientation_estimator.py`: tilt compensation, complementary fusion, unwrap.
- `filters/*`: FIR/IIR yardımcıları, complementary/Kalman.
- `visualization/*`: Plotly zaman serisi/FFT; `reporting/report_generator.py` HTML rapor.
- `simulation/mag_simulator.py`: sentetik mag/gyro/ivme.

## Tasarım Nedenleri
- Test edilebilirlik: her katman ayrı modül, birim testler izole.
- Ayrışma: GUI/CLI sadece `PipelineConfig` + `run_basic_pipeline`; frontend değişse de çekirdek stabil.
- Yeniden kullanım: kalibrasyon, heading, FFT bölümleri bağımsız taşınabilir.
- Hata izolasyonu: katman giriş/çıkışları belirgin, arıza kökü hızlı bulunur.
