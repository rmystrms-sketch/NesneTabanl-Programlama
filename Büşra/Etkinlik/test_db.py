from etkinlik_sistemleri import EtkinlikBackend
import os

try:
    print("Backend başlatılıyor...")
    backend = EtkinlikBackend()
    print("Backend başarıyla başlatıldı.")
    
    if os.path.exists("etkinlik_veritabani.db"):
        print("Veritabanı dosyası oluşturuldu.")
    else:
        print("HATA: Veritabanı dosyası bulunamadı!")
        
    print(f"Toplam etkinlik sayısı: {len(backend.ana_veriler)}")
    for e in backend.ana_veriler:
        print(f"- {e['id']}: {e['ad']} ({e['satilan']}/{e['toplam']})")
        
    print("\nKatılımcı havuzu kontrol ediliyor...")
    for e_id, kisiler in backend.katilimci_havuzu.items():
        print(f"Etkinlik {e_id} için {len(kisiler)} katılımcı var.")

except Exception as e:
    print(f"HATA: {str(e)}")
