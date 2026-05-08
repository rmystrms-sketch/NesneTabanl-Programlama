import sqlite3
import random
import hashlib
import os
import base64
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional

class Konaklama(ABC):
    """
    Konaklama tesisleri için temel soyut (abstract) sınıf.
    Rota Yönetimi ve Konaklama Planlaması süreçlerinde kalıtım (inheritance) amacı ile kullanılır.
    """
    def __init__(self, konaklama_id: int, ad: str, gecelik_fiyat: float, sehir: str) -> None:
        self.konaklama_id = konaklama_id
        self.ad = ad
        self._gecelik_fiyat = gecelik_fiyat
        self.sehir = sehir

    def get_fiyat(self) -> float:
        """Konaklama tesisinin gecelik fiyatını döndürür."""
        return self._gecelik_fiyat

    @abstractmethod
    def get_tur(self) -> str:
        """Konaklama türünü (Otel, Pansiyon vb.) döndürmesi gereken soyut metot."""
        pass

class Otel(Konaklama):
    """Konaklama sınıfından türetilen Otel entegrasyon sınıfı."""
    def get_tur(self) -> str: 
        return "Otel"

class Pansiyon(Konaklama):
    """Konaklama sınıfından türetilen Pansiyon entegrasyon sınıfı."""
    def get_tur(self) -> str: 
        return "Pansiyon"

class VeritabaniYoneticisi:
    """
    Veri Entegrasyonu ve Veritabanı Yönetimi işlemlerini yürüten temel sınıf.
    Sistem başlatıldığında tabloları oluşturur ve gerekli ise başlangıç (seed) verilerini üretir.
    """
    def __init__(self, db_adi: str = "seyahat_v12_turkiye.db") -> None:
        self.conn = sqlite3.connect(db_adi)
        self.cursor = self.conn.cursor()
        self.tablolari_olustur()
        self.baslangic_verilerini_uret_ve_ekle()

    def tablolari_olustur(self) -> None:
        """Sistemin ihtiyaç duyduğu tüm ilişkisel veritabanı tablolarını (Schema) oluşturur."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Kullanicilar 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, ad_soyad TEXT, kullanici_adi TEXT UNIQUE, eposta TEXT UNIQUE, sifre TEXT, profil_resmi TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Katalog_Konaklama 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, sehir TEXT, ad TEXT, fiyat REAL, tur TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Katalog_Aktivite 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, sehir TEXT, ad TEXT, fiyat REAL, kategori TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Plan 
            (plan_id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_id INTEGER, hedef_sehir TEXT, 
            tarih_bas TEXT, tarih_bit TEXT, gun_sayisi INTEGER, kisi_sayisi INTEGER, 
            min_butce INTEGER, max_butce INTEGER, konaklama_id INTEGER,
            ulasim_turu TEXT, ulasim_firmasi TEXT, gidis_koltuklar TEXT, donus_koltuklar TEXT, ulasim_maliyeti REAL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Plan_Aktivite 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, plan_id INTEGER, ad TEXT, fiyat REAL, gun_no INTEGER, kategori TEXT)''')
        self.conn.commit()

    def baslangic_verilerini_uret_ve_ekle(self) -> None:
        """Eğer veritabanı boş ise test ve geliştirme aşaması için varsayılan sistem verilerini doldurur."""
        self.cursor.execute("SELECT COUNT(*) FROM Katalog_Konaklama")
        if self.cursor.fetchone()[0] > 0: return 

        iller = ["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman", "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"]
        konaklama_kayitlari = []; aktivite_kayitlari = []
        otel_ekleri = ["Merkez Otel", "Palace", "Grand", "Boutique", "Dağ Evi", "Termal Resort", "Sahil Pansiyon", "Konak", "City Hotel", "Suites"]
        mekan_ekleri = ["Tarihi Kalesi", "Kent Müzesi", "Antik Kenti", "Doğa Milli Parkı", "Seyir Terası", "Eski Çarşısı", "Sanat Sokağı", "Yeraltı Şehri", "Şelalesi", "Tarihi Camii"]
        etkinlik_ekleri = ["Yöresel Lezzet Turu", "Doğa Yürüyüşü", "Şehir Merkezi Keşfi", "Gece Eğlencesi", "Kültür Festivali", "Tekne/Fayton Turu", "Macera Parkuru", "Tiyatro Gösterisi", "Kamp Alanı Etkinliği", "Atlı Safari"]

        for il in iller:
            for o_isim in random.sample(otel_ekleri, 5):
                tur = "Pansiyon" if any(x in o_isim for x in ["Pansiyon", "Ev", "Konak"]) else "Otel"
                konaklama_kayitlari.append((il, f"{il} {o_isim}", round(random.uniform(1000, 5000), -1), tur))
            for m_isim in random.sample(mekan_ekleri, 3):
                aktivite_kayitlari.append((il, f"{il} {m_isim}", 0 if random.random() > 0.5 else round(random.uniform(50, 200), -1), "Mekan"))
            for e_isim in random.sample(etkinlik_ekleri, 4):
                aktivite_kayitlari.append((il, f"{il} {e_isim}", round(random.uniform(300, 1500), -1), "Etkinlik"))

        self.cursor.executemany("INSERT INTO Katalog_Konaklama (sehir, ad, fiyat, tur) VALUES (?, ?, ?, ?)", konaklama_kayitlari)
        self.cursor.executemany("INSERT INTO Katalog_Aktivite (sehir, ad, fiyat, kategori) VALUES (?, ?, ?, ?)", aktivite_kayitlari)
        self.conn.commit()

class SeyahatAcentesi:
    """
    Sistemin ana iş mantığını yürüten merkezi yönetim sınıfı.
    Kullanıcı hesapları, rota yönetimi ve bütçe optimizasyonu işlemlerini koordine eder.
    """
    def __init__(self) -> None:
        self.db = VeritabaniYoneticisi()

    def illeri_getir(self) -> List[str]:
        """Sistemde kayıtlı olan şehirlerin sıralı listesini döndürür."""
        return sorted(["Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman", "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"])

    def _sifre_hashle(self, sifre: str) -> str:
        """Güvenlik politikaları gereği kullanıcı şifrelerini SHA-256 ile şifreler."""
        return hashlib.sha256(sifre.encode('utf-8')).hexdigest()

    def _resim_kaydet(self, secili_yol: str) -> str:
        """Kullanıcı profil fotoğraflarını veritabanında saklamak üzere Base64 formatına çevirir."""
        if not secili_yol or not os.path.exists(secili_yol): 
            return ""
        try:
            with open(secili_yol, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            print(f"Resim dönüştürme hatası: {e}")
            return ""

    def kullanici_kayit(self, ad_soyad: str, kullanici_adi: str, eposta: str, sifre: str, profil_resmi: str) -> Tuple[bool, str]:
        """Sisteme yeni kullanıcı kaydeder (Veri Entegrasyonu)."""
        try:
            hashli_sifre = self._sifre_hashle(sifre)
            yeni_resim_yolu = self._resim_kaydet(profil_resmi)
            self.db.cursor.execute("INSERT INTO Kullanicilar (ad_soyad, kullanici_adi, eposta, sifre, profil_resmi) VALUES (?, ?, ?, ?, ?)", 
                                   (ad_soyad, kullanici_adi, eposta, hashli_sifre, yeni_resim_yolu))
            self.db.conn.commit()
            return True, "Hesabınız başarıyla oluşturuldu! Giriş yapabilirsiniz."
        except sqlite3.IntegrityError: return False, "Bu e-posta veya kullanıcı adı sisteme zaten kayıtlı!"
        except Exception as e: return False, f"Hata: {str(e)}"

    def kullanici_giris(self, kimlik: str, sifre: str) -> Tuple[bool, Optional[int], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Kullanıcı kimlik doğrulaması yapar ve oturum verilerini döndürür."""
        try:
            hashli_sifre = self._sifre_hashle(sifre)
            self.db.cursor.execute("SELECT id, ad_soyad, kullanici_adi, eposta, sifre, profil_resmi FROM Kullanicilar WHERE (kullanici_adi = ? OR eposta = ?) AND sifre = ?", (kimlik, kimlik, hashli_sifre))
            sonuc = self.db.cursor.fetchone()
            return (True, sonuc[0], sonuc[1], sonuc[2], sonuc[3], sonuc[4], sonuc[5]) if sonuc else (False, None, None, None, None, None, None)
        except: return False, None, None, None, None, None, None

    def kullanici_guncelle(self, k_id: int, ad_soyad: str, yeni_kadi: str, yeni_eposta: str, yeni_sifre: str, yeni_resim: str) -> Tuple[bool, str]:
        """Mevcut kullanıcının profil bilgilerini günceller."""
        try:
            hashli_sifre = self._sifre_hashle(yeni_sifre)
            guncel_resim = self._resim_kaydet(yeni_resim) if yeni_resim and os.path.exists(yeni_resim) else yeni_resim
            self.db.cursor.execute("UPDATE Kullanicilar SET ad_soyad = ?, kullanici_adi = ?, eposta = ?, sifre = ?, profil_resmi = ? WHERE id = ?", 
                                   (ad_soyad, yeni_kadi, yeni_eposta, hashli_sifre, guncel_resim, k_id))
            self.db.conn.commit()
            return True, "Profil bilgileriniz başarıyla güncellendi!"
        except sqlite3.IntegrityError: return False, "Bu kullanıcı adı veya e-posta başka biri tarafından kullanılıyor!"
        except Exception as e: return False, f"Hata: {str(e)}"

    def sifre_sifirla(self, k_adi: str, eposta: str, yeni_sifre: str) -> Tuple[bool, str]:
        """Kullanıcının unuttuğu şifreyi sıfırlamasını (Password Reset) sağlar."""
        try:
            self.db.cursor.execute("SELECT id FROM Kullanicilar WHERE kullanici_adi = ? AND eposta = ?", (k_adi, eposta))
            kullanici = self.db.cursor.fetchone()
            if not kullanici:
                return False, "Kullanıcı adı ve e-posta eşleşmiyor veya bulunamadı!"
            
            hashli_sifre = self._sifre_hashle(yeni_sifre)
            self.db.cursor.execute("UPDATE Kullanicilar SET sifre = ? WHERE id = ?", (hashli_sifre, kullanici[0]))
            self.db.conn.commit()
            return True, "Şifreniz başarıyla sıfırlandı!"
        except Exception as e:
            return False, f"Hata: {str(e)}"

    def siradaki_plan_id_getir(self) -> int:
        """Yeni eklenecek olan rotanın ID değerini tahmin eder/getirir."""
        self.db.cursor.execute("SELECT MAX(plan_id) FROM Plan")
        sonuc = self.db.cursor.fetchone()[0]
        return 1000 if sonuc is None else sonuc + 1

    def sehire_gore_oteller(self, sehir: str) -> List[Tuple]:
        """Belirtilen şehirdeki konaklama tesislerini fiyatına göre sıralayarak listeler."""
        self.db.cursor.execute("SELECT id, ad, fiyat, tur FROM Katalog_Konaklama WHERE sehir = ? ORDER BY fiyat ASC", (sehir,))
        return self.db.cursor.fetchall()
        
    def sehire_gore_aktiviteler(self, sehir: str, kategori: str) -> List[Tuple]:
        """Belirtilen şehir ve kategorideki (Mekan/Etkinlik) aktiviteleri listeler."""
        self.db.cursor.execute("SELECT id, ad, fiyat, kategori FROM Katalog_Aktivite WHERE sehir = ? AND kategori = ? ORDER BY fiyat ASC", (sehir, kategori))
        return self.db.cursor.fetchall()

    def yeni_rota_ve_otel_kaydet(self, kullanici_id: int, sehir: str, t_bas: str, t_bit: str, gun: int, kisi: int, min_b: int, max_b: int, otel_id: int, ulasim_turu: str = "", ulasim_firmasi: str = "", gidis_koltuklar: str = "", donus_koltuklar: str = "", ulasim_maliyeti: float = 0.0) -> Tuple[bool, str]:
        """Yeni bir seyahat rotası (Plan) oluşturarak veritabanına kaydeder (Rota Yönetimi)."""
        try:
            self.db.cursor.execute('''INSERT INTO Plan (kullanici_id, hedef_sehir, tarih_bas, tarih_bit, gun_sayisi, kisi_sayisi, min_butce, max_butce, konaklama_id, ulasim_turu, ulasim_firmasi, gidis_koltuklar, donus_koltuklar, ulasim_maliyeti) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (kullanici_id, sehir, t_bas, t_bit, gun, kisi, min_b, max_b, otel_id, ulasim_turu, ulasim_firmasi, gidis_koltuklar, donus_koltuklar, ulasim_maliyeti))
            self.db.conn.commit()
            return True, "Seyahat rotanız başarıyla oluşturuldu."
        except Exception as e: return False, f"Hata: {str(e)}"

    def plan_guncelle(self, plan_id: int, sehir: str, t_bas: str, t_bit: str, gun: int, kisi: int, min_b: int, max_b: int, otel_id: int, ulasim_turu: str = "", ulasim_firmasi: str = "", gidis_koltuklar: str = "", donus_koltuklar: str = "", ulasim_maliyeti: float = 0.0) -> Tuple[bool, str]:
        """Mevcut bir seyahat rotasının tüm detaylarını günceller."""
        try:
            self.db.cursor.execute('''UPDATE Plan SET hedef_sehir = ?, tarih_bas = ?, tarih_bit = ?, gun_sayisi = ?, kisi_sayisi = ?, min_butce = ?, max_butce = ?, konaklama_id = ?, ulasim_turu = ?, ulasim_firmasi = ?, gidis_koltuklar = ?, donus_koltuklar = ?, ulasim_maliyeti = ? 
                WHERE plan_id = ?''', (sehir, t_bas, t_bit, gun, kisi, min_b, max_b, otel_id, ulasim_turu, ulasim_firmasi, gidis_koltuklar, donus_koltuklar, ulasim_maliyeti, plan_id))
            self.db.conn.commit()
            return True, "Seyahat planınız başarıyla güncellendi."
        except Exception as e: return False, f"Hata: {str(e)}"

    def plana_aktivite_ekle(self, plan_id: int, ad: str, fiyat: float, gun_no: int, kategori: str) -> Tuple[bool, str]:
        """Rotanın ilgili gününe mekan veya etkinlik ekler."""
        try:
            self.db.cursor.execute("SELECT id FROM Plan_Aktivite WHERE plan_id = ? AND ad = ? AND gun_no = ?", (plan_id, ad, gun_no))
            if self.db.cursor.fetchone(): return False, f"Bu {kategori} zaten planınızın {gun_no}. gününe eklenmiş!"
            self.db.cursor.execute("INSERT INTO Plan_Aktivite (plan_id, ad, fiyat, gun_no, kategori) VALUES (?, ?, ?, ?, ?)", (plan_id, ad, fiyat, gun_no, kategori))
            self.db.conn.commit()
            return True, f"{kategori} plana başarıyla eklendi."
        except Exception as e: return False, f"Hata: {str(e)}"
    
    def plandan_aktivite_sil(self, aktivite_id: int) -> Tuple[bool, str]:
        """Planlanmış bir aktiviteyi rotadan kaldırır."""
        self.db.cursor.execute("DELETE FROM Plan_Aktivite WHERE id = ?", (aktivite_id,))
        self.db.conn.commit()
        return True, "Seçili etkinlik/mekan planınızdan kaldırıldı."

    def plani_sil(self, plan_id: int) -> Tuple[bool, str]:
        """Tüm rotayı ve rotaya bağlı aktiviteleri sistemden tamamen siler."""
        self.db.cursor.execute("DELETE FROM Plan_Aktivite WHERE plan_id = ?", (plan_id,))
        self.db.cursor.execute("DELETE FROM Plan WHERE plan_id = ?", (plan_id,))
        self.db.conn.commit()
        return True, "Plan tamamen silindi."

    def tum_planlari_getir(self, kullanici_id: int) -> List[Dict[str, Any]]:
        """Kullanıcıya ait tüm seyahat rotalarını ve maliyet hesaplamalarını (Bütçe Optimizasyonu) döndürür."""
        self.db.cursor.execute('''SELECT p.plan_id, p.hedef_sehir, p.tarih_bas, p.tarih_bit, p.gun_sayisi, p.kisi_sayisi, p.min_butce, p.max_butce, k.ad, k.fiyat, p.konaklama_id, p.ulasim_turu, p.ulasim_firmasi, p.gidis_koltuklar, p.donus_koltuklar, p.ulasim_maliyeti
            FROM Plan p LEFT JOIN Katalog_Konaklama k ON p.konaklama_id = k.id WHERE p.kullanici_id = ? ORDER BY p.plan_id DESC''', (kullanici_id,))
        planlar = self.db.cursor.fetchall()
        sonuclar = []
        for p in planlar:
            plan_id, gun_sayisi, kisi_sayisi, gecelik_otel_fiyat = p[0], p[4], p[5], p[9] if p[9] else 0
            self.db.cursor.execute("SELECT id, ad, fiyat, gun_no, kategori FROM Plan_Aktivite WHERE plan_id = ? ORDER BY gun_no ASC", (plan_id,))
            aktiviteler = self.db.cursor.fetchall()
            
            akt_maliyet = sum([a[2] for a in aktiviteler]) * kisi_sayisi
            konaklama_maliyeti = gecelik_otel_fiyat * gun_sayisi * kisi_sayisi
            
            ulasim_turu = p[11] if p[11] else ""
            ulasim_firmasi = p[12] if p[12] else ""
            gidis_koltuklar = p[13] if p[13] else ""
            donus_koltuklar = p[14] if p[14] else ""
            ulasim_maliyeti = p[15] if p[15] else 0.0
            
            toplam = akt_maliyet + konaklama_maliyeti + ulasim_maliyeti
            
            sonuclar.append({
                "plan_id": plan_id, "sehir": p[1], "t_bas": p[2], "t_bit": p[3], "gun": gun_sayisi, "kisi": kisi_sayisi,
                "min_butce": p[6], "max_butce": p[7], "konaklama": p[8] if p[8] else "Seçilmedi", "konaklama_id": p[10],
                "ulasim_turu": ulasim_turu, "ulasim_firmasi": ulasim_firmasi, "gidis_koltuklar": gidis_koltuklar, "donus_koltuklar": donus_koltuklar, "ulasim_maliyeti": ulasim_maliyeti,
                "toplam_maliyet": toplam, "aktiviteler": aktiviteler
            })
        return sonuclar

    def kullanici_istatistikleri_getir(self, kullanici_id: int) -> Dict[str, Any]:
        """Kullanıcının yaptığı tüm harcamaları, kategori bazlı olarak hesaplar ve raporlar."""
        planlar = self.tum_planlari_getir(kullanici_id)
        otel_toplam = 0
        aktivite_toplam = 0
        ulasim_toplam = 0
        
        for p in planlar:
            gecelik_fiyat = 0
            if p['konaklama_id']:
                self.db.cursor.execute("SELECT fiyat FROM Katalog_Konaklama WHERE id=?", (p['konaklama_id'],))
                res = self.db.cursor.fetchone()
                if res: gecelik_fiyat = res[0]
            
            otel_toplam += (gecelik_fiyat * p['gun'] * p['kisi'])
            aktivite_toplam += (sum([a[2] for a in p['aktiviteler']]) * p['kisi'])
            ulasim_toplam += p.get('ulasim_maliyeti', 0.0)
            
        toplam_harcama = otel_toplam + aktivite_toplam + ulasim_toplam
        
        return {
            "toplam_plan": len(planlar),
            "toplam_harcama": toplam_harcama,
            "otel_harcama": otel_toplam,
            "aktivite_harcama": aktivite_toplam,
            "ulasim_harcama": ulasim_toplam
        }