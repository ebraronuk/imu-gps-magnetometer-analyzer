# GUI Özeti (GUI Overview)

Bu doküman, IMU-GPS-Magnetometer Analyzer projesindeki PyQt5 arayüzünün ana yapısını ve pipeline entegrasyonunu özetler.

## Kurulum
- CLI: `pip install -r requirements.txt`
- GUI: `pip install -r requirements-gui.txt`

## GUI Önkoşulları
- PyQt5 + PyQtWebEngine GUI için önerilir.
- WebEngine varsa Plotly gömülü; yoksa tarayıcı fallback devreye girer.

## 1. Ana Yerleşim
- Sol panel: dosya seçimi, yeniden örnekleme, modülleri aç/kapa, “Analiz Et” ve “Sentetik Veri Üret” butonları, kaynak etiketi.
- Sağ panel: sekmeli yapı (Özet, Zaman Serisi, FFT, Heading, Kalibrasyon).

## 2. Pipeline Entegrasyonu
- GUI, pipeline’ın frontend katmanıdır; tüm analizler backend’de `run_basic_pipeline` ile yürütülür.
- Akış: GUI → PipelineConfig → run_basic_pipeline() → AnalysisArtifacts → Sekmeler.
- Her sekme sadece ihtiyaç duyduğu artifact’leri tüketir (senkronize veri, FFT çıktısı, heading serileri, kalibrasyon sonuçları).

## 3. Sekmeler
- **Veri Özeti:** İlk satırlar, satır sayısı, medyan örnekleme aralığı, `describe()`.
- **Zaman Serisi:** accel_x/y/z, mag_x/y/z, gyro_z çizimleri (Matplotlib).
- **FFT:** Eksene göre genlik/frekans grafikleri; WebEngine yoksa tarayıcıda açılır.
- **Heading:** Manyetik heading (tilt-compensated), fused heading (complementary), drift/stabilite özetleri.
- **Kalibrasyon:** Ham/kalibre XY dağılımı, hard/soft-iron çıktıları, koşul sayısı ve veri yeterliliği.

## 4. Hata Yönetimi
- Tüm buton eylemleri try/except ile korunur; pencere kapanmaz.
- Hatalar status bar ve QMessageBox üzerinden Türkçe bildirilir.

## 5. Tema
- Koyu tema; grafiklerde kontrastı artırır ve uzun oturumlarda göz yorgunluğunu azaltır.

## 6. GUI Başlatma
- Komut: `python -m src.main --gui`

## 7. Fallback Davranışı
- WebEngine yüklü değilse FFT/Plotly grafikleri `reports/` altına yazılır ve sistem tarayıcısında açılır.
- Uygulama çalışmaya devam eder; status bar ve uyarı kutusu Türkçe bilgilendirir.
