# IMU–GPS–Magnetometer Analyzer – Sistem Mimarisi

Bu belge, projenin çekirdek mimarisini ve bileşenler arası veri akışını tanımlar.
Amaç, aviyonik sensör preprocessing zincirinin uçtan uca nasıl işlendiğini teknik doğrulukla göstermektir.

# 1. Genel Veri Akışı

Aşağıdaki şema, ham sensör loglarının GUI veya CLI üzerinden pipeline’a girip analiz çıktısına dönüşmesini göstermektedir:
```
RAW SENSOR LOGS
(accel, gyro, mag, GPS, pressure)
        │
        ▼
CSV Loader
(column validation, timestamp parsing)
        │
        ▼
Time Sync & Resampling
(uniform grid, ffill, optional normalization)
        │
        ▼
Calibration
(hard/soft iron, ellipsoid fitting,
PSD regularization, safe fallback)
        │
        ▼
Orientation Estimation
(tilt compensation, complementary filter,
angle unwrap, stability metrics)
        │
        ▼
FFT Analysis
(frequency domain noise characterization)
        │
        ▼
Visualization & Reporting
(Plotly, Matplotlib, HTML report)

```

# 2. Pipeline Katmanları
2.1. Data Loaders

CSV doğrulama
Eksik kolon kontrolü
Timestamp parse (UTC-aware)

2.2. Preprocessing

Time index oluşturma
Fixed-rate resampling
Opsiyonel z-score normalizasyon

2.3. Calibration

Hard-iron offset çıkarımı
Soft-iron ellipsoid fitting
Positive-semidefinite regularization
Inverse sqrt dönüşümü
Veri yetersiz ise fallback

2.4. Orientation Estimation

Tilt-compensated heading
Gyro integration + complementary fusion
Angle unwrap
Stabilite skoru üretimi

2.5. FFT / Noise Analysis

Per-axis FFT
Titreşim bantlarının çıkarılması
Spektrum genliği ve dağılımı

2.6. Visualization

Zaman serileri
FFT spektrumu
Heading eğrileri
Kalibrasyon öncesi/sonrası dağılımlar

# 3. GUI Entegrasyonu

GUI, pipeline’ın tamamen üstüne oturan bir frontend katmanıdır:

User Input (GUI)
        ↓
PipelineConfig
        ↓
run_basic_pipeline()
        ↓
Artifacts
        ↓
GUI Tabs (Summary, TimeSeries, FFT, Heading, Calibration)


Her tab sadece kendi ihtiyaç duyduğu artifact’leri işler.

İster CLI ister GUI olsun, aynı core işlem hattı kullanılır ve bu modülerlik profesyonel avionik yazılım tasarım prensipleriyle uyumludur.

# 4. Kod Organizasyonu
```
src/
├── pipeline/           # PipelineConfig, run_basic_pipeline
├── orientation/        # Tilt compensation, complementary filter
├── calibration/        # Hard/soft iron + ellipsoid fit
├── preprocessing/      # Time sync, normalization
├── visualization/      # Plotly + Matplotlib grafikleri
├── data_loaders/       # CSV loader
└── gui/                # PyQt5 GUI
```

# 5. Test Yapısı
```

tests/
├── test_normalization.py
├── test_ellipsoid_fit.py
└── test_pipeline.py
```