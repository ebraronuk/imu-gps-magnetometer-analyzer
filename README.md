# 📡 IMU–GPS–Magnetometer Analyzer

Profesyonel uçuş testlerinin ihtiyaç duyduğu sensör log analiz hattını (IMU, manyetometre, gyro, GPS, barometrik basınç) yazılım ortamında uçtan uca gerçekleştiren bir araçtır.  
Proje; zaman senkronizasyonu, manyetometre kalibrasyonu, heading hesaplama, sensör füzyonu, FFT tabanlı gürültü analizi ve etkileşimli görselleştirme gibi kritik avionik iş akışlarını içerir.

Bu çalışma hem öğrenme amaçlıdır hem de gerçek telemetri preprocessing zincirlerinin sadeleştirilmiş fakat mühendislik doğruluğu yüksek bir modelidir.

##  Özellikler

- Çoklu sensör loglarını yükleme (CSV)
- Zaman senkronizasyonu ve uniform örnekleme ızgarası
- Opsiyonel normalizasyon
- Manyetometre kalibrasyonu:
  - Hard-iron bias çıkarımı
  - Soft-iron ellipsoid fitting
  - PSD regularization
- IMU bias hesaplama
- Sensör füzyonu:
  - Tilt-compensated heading  
  - Complementary filter (gyro + mag)
- FFT tabanlı frekans analizi
- Plotly ile interaktif grafikler
- HTML rapor üretimi
- Sentetik uçuş verisi simülasyonu

## Uçtan Uca Pipeline Mimarisi
```
┌────────────────────────────────────────────────────────────────────────────┐
│                             RAW SENSOR LOGS                                │
│ accel_x, accel_y, accel_z | mag_x, mag_y, mag_z | gyro_z | GPS | pressure │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           CSV Loader Module                                │
│ • Kolon doğrulama • Temizleme • Timestamp parse                            │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                Time Synchronization & Resampling                           │
│ • Uniform time grid • Eksik örnek doldurma (ffill)                         │
│ • Opsiyonel z-score normalizasyon                                          │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        Magnetometer Calibration                             │
│ • Hard-iron bias çıkarımı                                                  │
│ • Soft-iron ellipsoid fitting                                              │
│ • PSD regularization • Inverse sqrt transform                              │
│ • Veri azsa güvenli fallback                                               │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          Orientation Estimation                             │
│ • Tilt-compensated heading                                                 │
│ • Complementary filter (gyro+mag)                                          │
│ • Angle unwrap                                                             │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         FFT & Noise Analysis                                │
│ • Frekans alanı • Titreşim & gürültü karakterizasyonu                      │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                               Visualization                                 │
│ • Veri Özeti • Zaman Serisi • FFT • Heading • Kalibrasyon                  │
└────────────────────────────────────────────────────────────────────────────┘
```

# GUI Kullanımı

Proje, PyQt5 tabanlı etkileşimli bir arayüz içerir.
Bu arayüz ile:

CSV dosyası yükleme
Zaman senkronizasyonu
Manyetometre kalibrasyonu
Heading hesaplama (tilt-compensated + fused)
FFT gürültü analizi
Sentetik veri üretimi
işlemleri tek tıkla yapılabilir.

GUI’yi başlatmak için:

  python -m src.main --gui


GUI’nin mimarisi, ekran görüntüleri ve sekmelerin teknik açıklamaları için:
  docs/Gui_Overview.md
  
## Simülasyon Modülü

Gerçek log olmadığında veya algoritmaların doğrulanması gerektiğinde:
```
  --simulate-mag
```

ile sentetik manyetometre + gyro + ivme veri seti üretilir.

Simülasyon içerir:

- Dönen platform manyetik vektörleri
- Hafif drift içeren gyro
- Hafif gürültülü ivme sensörü
- Düzenli timestamp grid
- Referans heading profili


## Manyetometre Kalibrasyonu

Projede profesyonel kalibrasyon uygulanır:

- 3D ellipsoid fitting  
- Hard-iron offset  
- Soft-iron deformasyon matrisi  
- PSD regularization  
- Normalize edilmiş küre için inverse sqrt transform  
- Veri yetersiz olduğunda fallback  

**Örnek çıktı:**

Hard-iron center: [-6.7864, 2.7794, 24.0934]

Soft-iron matrix:
[[ 0.0356 -0.0009  0.0021]
 [-0.0009  0.0355 -0.0021]
 [ 0.0021 -0.0021  0.0236]]

Corrected magnetometer preview:
   mag_x   mag_y   mag_z
0  0.9379  0.0806  0.5387
1  0.9379  0.0806  0.5387


## Yönelim (Heading) Hesaplama

### Tilt-Compensated Heading
- Accelerometer → roll & pitch hesaplanır  
- Magnetometer → tilt compensation uygulanır  
- Heading = `atan2(mag_y', mag_x')`

### Complementary Filter (Gyro + Mag Fusion)

```
yaw = α * (yaw + gyro_z * dt) + (1 - α) * mag_heading
```

İyileştirmeler:

- İlk seed manyetik heading  
- Angle unwrap ile 360° sıçramalarını engelleme  
- Senkronize zaman ızgarası üzerinde çalışma  

##  Görselleştirme

Plotly ile interaktif grafikler:

- IMU zaman serisi  
- Manyetometre dağılımı  
- Gyro vs fused heading  
- FFT spektrumu  
- Kalibrasyon öncesi / sonrası manyetik küre  

##  Bilimsel Arka Plan

Proje şu mühendislik alanlarının birleşimidir:

- **Sinyal İşleme:** FFT, filtreler, noise profiling  
- **Sensör Füzyonu:** complementary filter, drift kompanzasyonu  
- **Manyetometre Modelleme:** ellipsoid fitting, soft/hard-iron  
- **Zaman Serileri:** resampling, senkronizasyon  
- **Oryantasyon Matematiği:** tilt compensation, Euler açıları  


##  Komut Örnekleri

### Özet
```
  python -m src.main --input example_logs/heading_demo.csv --summary
```

### FFT + Plot
```
  python -m src.main --input example_logs/heading_demo.csv --fft --plot
```

### Heading + Kalibrasyon
```
  python -m src.main --input example_logs/heading_demo.csv --heading --mag-calib --plot
```

### Sentetik veri
```
  python -m src.main --simulate-mag --heading --fft --plot
```
##  Proje Yapısı
```
src/
  pipeline/
  orientation/
  calibration/
  preprocessing/
  visualization/
  data_loaders/
example_logs/
docs/
tests/
```

##  Projenin Amacı

Bu proje; aviyonik sensör işleme zincirinin tüm aşamalarını kendi başıma uygulayıp, sensör füzyonu, manyetometre kalibrasyonu, sinyal işleme ve telemetri pipeline tasarımı konularında kendimi geliştirmek için hazırlanmıştır.

Gerçek R&D projelerinde kullanılan tekniklerin sadeleştirilmiş fakat doğruluğu korunmuş bir modelini içerir.
