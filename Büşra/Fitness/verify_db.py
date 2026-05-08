from fitness_sistemleri import FitnessSistemi
import os

# 1. Başlat
print("Sistem başlatılıyor...")
sistem = FitnessSistemi()

# 2. Veritabanı kontrolü
if os.path.exists("fitness_veritabani.db"):
    print("✅ Veritabanı dosyası oluşturuldu.")
else:
    print("❌ Veritabanı dosyası bulunamadı!")

# 3. Veri çekme testi
sporcular = sistem.sporcular
print(f"📊 Toplam sporcu sayısı: {len(sporcular)}")

if len(sporcular) > 0:
    print(f"✅ İlk sporcu: {sporcular[0]['ad']}")
    print(f"📋 İlk sporcu antrenman geçmişi sayısı: {len(sporcular[0]['antrenman_gecmisi'])}")
else:
    print("❌ Sporcu verisi bulunamadı!")

# 4. Ekleme testi
yeni = sistem.sporcu_ekle("Test Kullanıcısı", "Erkek", 30, "1 Aylık", 180, 80, 75)
if yeni:
    print(f"✅ Yeni sporcu eklendi: {yeni['ad']} (ID: {yeni['id']})")
    
    # 5. Güncelleme testi
    sistem.kilo_guncelle(yeni['id'], 79)
    guncel = sistem.sporcu_getir(yeni['id'])
    if guncel and guncel['kilo'] == 79:
        print("✅ Kilo güncelleme başarılı.")
    else:
        print("❌ Kilo güncelleme başarısız.")
    
    # 6. Silme testi
    sistem.sporcu_sil(yeni['id'])
    silindi_mi = sistem.sporcu_getir(yeni['id'])
    if silindi_mi is None:
        print("✅ Sporcu silme başarılı.")
    else:
        print("❌ Sporcu silme başarısız.")
