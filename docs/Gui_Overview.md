# GUI Özeti (GUI Overview)

Bu doküman, IMU–GPS–Magnetometer Analyzer projesinde kullanılan grafiksel arayüzün genel bir özetini sunar.
Arayüz PyQt5 kullanılarak geliştirilmiştir ve aviyonik ile gömülü sistemlerde sık kullanılan sensör analiz iş akışlarını kolaylaştırmak için tasarlanmıştır.

# 1. Ana Yerleşim (Main Layout)

Arayüz iki ana bölümden oluşur:
Sol Kontrol Paneli
Dosya seçimi
Yeniden örnekleme (resampling) seçenekleri
Analiz modülleri (checkbox ile etkinleştirme)
“Analiz Et” ve “Sentetik Veri Üret” butonları
Kaynak göstergeleri (raw / synthetic)
Sağ Görselleştirme Paneli
Sekme tabanlı bir gösterim sistemi içerir:

# Veri Özeti (Summary)

Zaman Serisi (Time Series)
FFT Spektrumu
Heading (Yönelim) Hesabı
Manyetometre Kalibrasyonu

# 2. Pipeline Entegrasyonu

GUI, çekirdek analiz pipeline’ının bir frontend arayüzüdür.

GUI → PipelineConfig → run_basic_pipeline() → Artifacts → GUI sekmeleri

Pipeline’dan dönen artifact’ler şunları içerir:

Senkronize edilmiş veri
FFT sonuçları
Manyetik heading
Füzyonlanmış heading (gyro + mag)
Kalibrasyon çıktıları
Her sekme, yalnızca ihtiyaç duyduğu çıktıları kullanır.

# 3. Sekmeler (Tabs)
Veri Özeti (Data Summary)

Gösterilenler:

Veri setinin ilk satırları
Toplam satır sayısı
Örnekleme aralığının medyanı
Pandas describe() çıktısı
Zaman Serisi (Time Series)

Çizilen veriler:

accel_x / accel_y / accel_z
mag_x / mag_y / mag_z
gyro_z

Grafikler boyutlandırılabilir Matplotlib canvas üzerinde görüntülenir.

FFT Spektrumu

İçerik:

Tüm eksenler için FFT büyüklük grafiği
Frekans alanında gürültü ve titreşim incelemesi
Heading (Yönelim)
Gösterilir:
Manyetik heading (tilt-compensated)
Füzyon heading (complementary filter)
Gyro drift tahmini
Manyetik hata metrikleri
Stabilite sınıflandırması
Kalibrasyon (Mag Calibration)

Sunulanlar:

Ham ve kalibre edilmiş XY manyetik dağılım grafikleri
Hard/soft-iron matrisleri
Condition number ve veri yeterlilik ölçümleri

# 4. Hata Yönetimi (Error Handling)

Tüm buton işlevleri güvenlik kontrollüdür:
Kullanıcıya hata mesaj kutusu
Status bar üzerinden uyarılar
Pencere çökmeleri engellenmiştir.

# 5. Tema (Theme)

GUI, koyu tema (dark theme) kullanır:
Göz yorgunluğunu azaltır
Grafiklerde daha iyi kontrast sağlar
Mühendislik sunumları için profesyonel görünüm oluşturur

# 6. GUI Başlatma

GUI’yi çalıştırmak için:

    python -m src.main --gui