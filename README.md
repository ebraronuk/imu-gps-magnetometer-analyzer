# IMU-GPS-Magnetometer Analyzer

Profesyonel uçuş test sensör logları (IMU, manyetometre, gyro, GPS, baro) için uçtan uca analiz hattı. Zaman senkronizasyonu, manyetometre kalibrasyonu, heading hesaplama, sensör füzyonu, FFT tabanlı gürültü analizi ve raporlama içerir.

Bu çalışma hem öğrenme amaçlıdır hem de gerçek telemetri preprocessing zincirlerinin sadeleştirilmiş fakat mühendislik doğruluğu yüksek bir modelidir.

## Kurulum
- CLI: `pip install -r requirements.txt`
- GUI: `pip install -r requirements-gui.txt`

## GUI Önkoşulları
- PyQt5 + PyQtWebEngine GUI için önerilir (`pip install -r requirements-gui.txt`).
- WebEngine varsa Plotly gömülü açılır; yoksa tarayıcı fallback devreye girer.

## GUI Çalıştırma
```
python -m src.main --gui
```

## Özellikler

- Çoklu sensör log yükleme (CSV)
- Zaman senkronizasyonu ve uniform örnekleme
- Opsiyonel normalizasyon
- Manyetometre kalibrasyonu: hard-iron bias giderimi, soft-iron ellipsoid fitting, PSD regularization
- IMU bias hesaplama
- Sensör füzyonu: tilt-compensated heading, complementary filter (gyro + mag)
- FFT tabanlı frekans analizi
- Plotly ile interaktif grafikler
- HTML rapor üretimi
- Sentetik uçuş verisi simülasyonu

## Uçtan Uca Pipeline
```
RAW SENSOR LOGS (accel, gyro, mag, GPS, baro)
        |
        v
CSV Loader (kolon kontrolü, temizleme, timestamp parse)
        |
        v
Time Sync & Resampling (uniform grid, ffill, opsiyonel z-score)
        |
        v
Calibration (hard/soft iron, ellipsoid fit, PSD reg, fallback)
        |
        v
Orientation Estimation (tilt compensation, complementary filter)
        |
        v
FFT & Noise Analysis
        |
        v
Visualization & Reporting (Plotly, HTML)
```

## GUI

- GUI, pipeline'ın frontend arayüzüdür; tüm analizler backend pipeline'da yapılır.

GUI'yi başlatmak için:
```
python -m src.main --gui
```

## Fallback Davranışı
- WebEngine yüklü değilse FFT/Plotly grafikleri `reports/` altına yazılır ve sistem tarayıcısında açılır.
- Uygulama kapanmaz; status bar ve uyarı kutusu Türkçe bilgi verir.

## Simülasyon Modülü

Gerçek log olmadığında veya algoritmaların doğrulanması gerektiğinde `--simulate-mag` ile sentetik manyetometre + gyro + ivme veri seti üretilir. Simülasyon; dönen platform manyetik vektörleri, hafif drift içeren gyro, hafif gürültülü ivme sensörü, düzenli timestamp grid'i ve referans heading profilini kapsar.

## Manyetometre Kalibrasyonu

- 3D ellipsoid fitting  
- Hard-iron offset  
- Soft-iron deformasyon matrisi  
- PSD regularization  
- Normalize edilmiş küre için inverse sqrt transform  
- Veri yetersiz olduğunda güvenli fallback  

Örnek çıktı:
```
Hard-iron center: [-6.7864, 2.7794, 24.0934]
Soft-iron matrix:
[[ 0.0356 -0.0009  0.0021]
 [-0.0009  0.0355 -0.0021]
 [ 0.0021 -0.0021  0.0236]]
Corrected magnetometer preview:
   mag_x   mag_y   mag_z
0  0.9379  0.0806  0.5387
1  0.9379  0.0806  0.5387
```

## Yönelim (Heading) Hesaplama

### Tilt-Compensated Heading
- Accelerometer'dan roll ve pitch hesaplanır.
- Magnetometreye tilt compensation uygulanır.
- Heading = `atan2(mag_y', mag_x')`

### Complementary Filter (Gyro + Mag Fusion)
```
yaw = alpha * (yaw + gyro_z * dt) + (1 - alpha) * mag_heading
```
İyileştirmeler: ilk seed manyetik heading, angle unwrap ile 360 derece sıçramaları engelleme, senkronize zaman ızgarasında çalışma.

## Görselleştirme

Plotly ile interaktif grafikler: IMU zaman serisi, manyetometre dağılımı, gyro vs fused heading, FFT spektrumu, kalibrasyon öncesi/sonrası manyetik küre.

## Komut Örnekleri

Özet:
```
python -m src.main --input example_logs/heading_demo.csv --summary
```

FFT + Plot:
```
python -m src.main --input example_logs/heading_demo.csv --fft --plot
```

Heading + Kalibrasyon:
```
python -m src.main --input example_logs/heading_demo.csv --heading --mag-calib --plot
```

Sentetik veri:
```
python -m src.main --simulate-mag --heading --fft --plot
```

## Proje Yapısı
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

## Projenin Amacı

Bu proje; aviyonik sensör işleme zincirinin tüm aşamalarını kendi başıma uygulayıp, sensör füzyonu, manyetometre kalibrasyonu, sinyal işleme ve telemetri pipeline tasarımı konularında deneyim kazanmak için hazırlandı. Gerçek R&D projelerinde kullanılan tekniklerin sadeleştirilmiş fakat doğruluğu korunmuş bir modelini içerir.
