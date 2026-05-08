import sqlite3
from datetime import datetime

MESAFELER = {
    ("İstanbul", "Ankara"): 450, ("İstanbul", "İzmir"): 480, ("İstanbul", "Bursa"): 150, ("İstanbul", "Antalya"): 700,
    ("Ankara", "İzmir"): 590, ("Ankara", "Bursa"): 390, ("Ankara", "Antalya"): 480,
    ("İzmir", "Bursa"): 350, ("İzmir", "Antalya"): 460, ("Bursa", "Antalya"): 540
}

def get_mesafe(s1, s2):
    if s1 == s2: return 50
    if (s1, s2) in MESAFELER: return MESAFELER[(s1, s2)]
    if (s2, s1) in MESAFELER: return MESAFELER[(s2, s1)]
    return 300

class Arac:
    def __init__(self, arac_id, marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti, musait_mi=True):
        self._arac_id       = arac_id
        self._marka         = marka
        self._model         = model
        self._tip           = tip
        self._yakit_tipi    = yakit_tipi
        self._sehir         = sehir
        self._kilometre     = kilometre
        self._musait_mi     = musait_mi
        self._km_ucreti     = km_ucreti

    def get_arac_id(self):       return self._arac_id
    def get_marka(self):         return self._marka
    def get_model(self):         return self._model
    def get_tip(self):           return self._tip
    def get_yakit_tipi(self):    return self._yakit_tipi
    def get_sehir(self):         return self._sehir
    def get_kilometre(self):     return self._kilometre
    def get_musait_mi(self):     return self._musait_mi
    def get_km_ucreti(self):     return self._km_ucreti
    def get_tam_ad(self):        return f"{self._marka} {self._model}"

    def arac_bilgisi_guncelle(self, marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti):
        self._marka = marka
        self._model = model
        self._tip = tip
        self._yakit_tipi = yakit_tipi
        self._sehir = sehir
        self._kilometre = kilometre
        self._km_ucreti = km_ucreti

    def arac_durumu_guncelle(self, musait):
        self._musait_mi = musait

    def kilometre_guncelle(self, eklenen_km):
        if eklenen_km < 0:
            raise ValueError("Km negatif olamaz.")
        self._kilometre += eklenen_km

class Kullanici:
    def __init__(self, kullanici_id, ad, ehliyet_no, telefon=""):
        self._kullanici_id = kullanici_id
        self._ad           = ad
        self._ehliyet_no   = ehliyet_no
        self._telefon      = telefon
        self._kiralamalar  = []

    def get_kullanici_id(self): return self._kullanici_id
    def get_ad(self):           return self._ad
    def get_ehliyet_no(self):   return self._ehliyet_no
    def get_telefon(self):      return self._telefon

    def kiralama_ekle(self, kiralama):
        self._kiralamalar.append(kiralama)

    def kiralama_gecmisi(self):
        return list(self._kiralamalar)

    def aktif_kiralama(self):
        for k in self._kiralamalar:
            if k.get_aktif():
                return k
        return None

class Kiralama:
    def __init__(self, kiralama_id, arac: Arac, kullanici: Kullanici, alis_sehri, birakis_sehri, baslangic_saati: datetime, bitis_saati=None, aktif=True, toplam_ucret=0.0):
        self._kiralama_id     = kiralama_id
        self._arac            = arac
        self._kullanici       = kullanici
        self._alis_sehri      = alis_sehri
        self._birakis_sehri   = birakis_sehri
        self._baslangic_saati = baslangic_saati
        self._bitis_saati     = bitis_saati
        self._aktif           = aktif
        self._toplam_ucret    = toplam_ucret

    def get_kiralama_id(self):     return self._kiralama_id
    def get_arac(self):            return self._arac
    def get_kullanici(self):       return self._kullanici
    def get_alis_sehri(self):      return self._alis_sehri
    def get_birakis_sehri(self):   return self._birakis_sehri
    def get_baslangic_saati(self): return self._baslangic_saati
    def get_bitis_saati(self):     return self._bitis_saati
    def get_aktif(self):           return self._aktif
    def get_toplam_ucret(self):    return self._toplam_ucret

    def kiralama_baslat(self):
        self._arac.arac_durumu_guncelle(False)
        return True, f"✓ Kiralama #{self._kiralama_id} başlatıldı."

    def kiralama_bitir(self, bitis_saati: datetime, eklenen_km: int = 0):
        if not self._aktif:
            return False, "Bu kiralama zaten sona ermiş."
        if bitis_saati <= self._baslangic_saati:
            return False, "Bitiş saati başlangıçtan önce olamaz."

        self._bitis_saati = bitis_saati
        self._aktif       = False
        sure_saat         = (bitis_saati - self._baslangic_saati).total_seconds() / 3600
        self._toplam_ucret = round(sure_saat * self._arac.get_saatlik_ucret(), 2)
        self._arac.kilometre_guncelle(eklenen_km)
        self._arac.arac_durumu_guncelle(True)
        return True, f"✓ Kiralama bitti. Süre: {sure_saat:.1f} saat | Ücret: ₺{self._toplam_ucret:.2f}"

    def kiralama_bilgisi(self):
        sure = "Devam ediyor"
        if self._bitis_saati:
            dk = int((self._bitis_saati - self._baslangic_saati).total_seconds() / 60)
            sure = f"{dk // 60}s {dk % 60}dk"
        return {
            "id":         self._kiralama_id,
            "arac":       self._arac.get_tam_ad(),
            "kullanici":  self._kullanici.get_ad(),
            "alis":       self._alis_sehri,
            "birakis":    self._birakis_sehri,
            "baslangic":  self._baslangic_saati.strftime("%d.%m.%Y %H:%M"),
            "bitis":      self._bitis_saati.strftime("%d.%m.%Y %H:%M") if self._bitis_saati else "—",
            "sure":       sure,
            "ucret":      f"₺{self._toplam_ucret:.2f}",
            "aktif":      self._aktif,
        }

class PaylasimSistemi:
    def __init__(self, db_path="carshare.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS araclar (
                id INTEGER PRIMARY KEY,
                marka TEXT,
                model TEXT,
                tip TEXT,
                yakit_tipi TEXT,
                sehir TEXT,
                kilometre INTEGER,
                km_ucreti REAL,
                musait_mi INTEGER
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY,
                ad TEXT,
                ehliyet_no TEXT,
                telefon TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS kiralamalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arac_id INTEGER,
                kullanici_id INTEGER,
                alis_sehri TEXT,
                birakis_sehri TEXT,
                baslangic TEXT,
                bitis TEXT,
                aktif INTEGER,
                ucret REAL,
                eklenen_km INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM araclar")
        if cur.fetchone()[0] == 0:
            self._dummy_veri_olustur(conn)
            
        # Eğer hiç aktif kiralama yoksa, müsait araçlar ve kişiler ile 5 adet aktif kiralama oluştur
        cur.execute("SELECT COUNT(*) FROM kiralamalar WHERE aktif=1")
        if cur.fetchone()[0] == 0:
            cur.execute('SELECT id FROM araclar WHERE musait_mi=1 LIMIT 5')
            cars = [r[0] for r in cur.fetchall()]
            cur.execute('SELECT id FROM kullanicilar WHERE id NOT IN (SELECT kullanici_id FROM kiralamalar WHERE aktif=1) LIMIT 5')
            users = [r[0] for r in cur.fetchall()]
            
            from datetime import datetime, timedelta
            for i in range(min(len(cars), len(users))):
                car_id, user_id = cars[i], users[i]
                bas = datetime.now() - timedelta(hours=(i+1)*6, minutes=i*17)
                cur.execute('SELECT km_ucreti FROM araclar WHERE id=?', (car_id,))
                km_ucreti = cur.fetchone()[0]
                ucret = 50 * km_ucreti
                cur.execute('''
                    INSERT INTO kiralamalar (arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic, bitis, aktif, ucret)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (car_id, user_id, 'İstanbul', 'İstanbul', bas.strftime('%Y-%m-%d %H:%M:%S'), None, 1, ucret))
                cur.execute('UPDATE araclar SET musait_mi=0 WHERE id=?', (car_id,))
            conn.commit()

        conn.close()

    def _dummy_veri_olustur(self, conn):
        cur = conn.cursor()
        araclar = [
            (1, "Toyota", "Corolla", "Sedan", "Benzin", "İstanbul", 45000, 3.5, 1),
            (2, "Ford", "Focus", "Hatchback", "Dizel", "Ankara", 62000, 3.0, 1),
            (3, "BMW", "X3", "SUV", "Dizel", "İzmir", 28000, 5.5, 1),
            (4, "Tesla", "Model 3", "Elektrikli", "Elektrik", "İstanbul", 8000, 4.0, 1),
            (5, "Renault", "Clio", "Hatchback", "Benzin", "Bursa", 91000, 2.5, 1),
            (6, "Mercedes", "Vito", "Minivan", "Dizel", "Antalya", 55000, 6.0, 1),
            (7, "Hyundai", "i20", "Hatchback", "Benzin", "İzmir", 30000, 2.8, 1),
            (8, "Volkswagen", "Golf", "Hatchback", "Benzin", "İstanbul", 42000, 3.2, 1),
            (9, "Honda", "Civic", "Sedan", "Benzin", "Ankara", 21000, 3.5, 1),
            (10, "Audi", "A4", "Sedan", "Dizel", "Bursa", 15000, 5.0, 1),
            (11, "Kia", "Sportage", "SUV", "Dizel", "Antalya", 60000, 4.2, 1),
            (12, "Peugeot", "3008", "SUV", "Dizel", "İstanbul", 48000, 4.5, 1),
            (13, "Toyota", "Yaris", "Hatchback", "Hibrit", "İzmir", 12000, 2.6, 1),
            (14, "Volvo", "XC90", "SUV", "Dizel", "Ankara", 19000, 7.0, 1),
            (15, "Porsche", "Macan", "SUV", "Benzin", "İstanbul", 5000, 9.0, 1),
            (16, "Fiat", "Egea", "Sedan", "Dizel", "Bursa", 15000, 2.5, 1),
            (17, "Renault", "Megane", "Sedan", "Dizel", "İstanbul", 32000, 3.0, 1),
            (18, "Dacia", "Duster", "SUV", "Dizel", "Antalya", 45000, 3.2, 1),
            (19, "Hyundai", "Tucson", "SUV", "Benzin", "İzmir", 22000, 4.0, 1),
            (20, "Nissan", "Qashqai", "SUV", "Benzin", "Ankara", 37000, 4.1, 1),
            (21, "Skoda", "Octavia", "Sedan", "Benzin", "İstanbul", 18000, 3.6, 1),
            (22, "Seat", "Leon", "Hatchback", "Benzin", "Bursa", 29000, 3.4, 1),
            (23, "Volkswagen", "Passat", "Sedan", "Dizel", "Ankara", 54000, 4.5, 1),
            (24, "Opel", "Astra", "Hatchback", "Benzin", "İzmir", 26000, 3.3, 1),
            (25, "Citroen", "C3", "Hatchback", "Dizel", "Antalya", 12000, 2.7, 1),
            (26, "Honda", "CR-V", "SUV", "Hibrit", "İstanbul", 41000, 4.8, 1),
            (27, "BMW", "520i", "Sedan", "Benzin", "Ankara", 15000, 6.5, 1),
            (28, "Mercedes", "C200", "Sedan", "Benzin", "İzmir", 11000, 6.2, 1),
            (29, "Audi", "Q5", "SUV", "Dizel", "Bursa", 33000, 5.8, 1),
            (30, "Kia", "Ceed", "Hatchback", "Dizel", "İstanbul", 21000, 3.1, 1),
            (31, "Ford", "Kuga", "SUV", "Dizel", "Antalya", 47000, 4.3, 1),
            (32, "Tesla", "Model Y", "Elektrikli", "Elektrik", "İstanbul", 5000, 4.5, 1),
            (33, "TOGG", "T10X", "SUV", "Elektrik", "Bursa", 2000, 3.8, 1),
            (34, "MG", "ZS EV", "SUV", "Elektrik", "İzmir", 8000, 3.5, 1),
            (35, "Hyundai", "Ioniq 5", "SUV", "Elektrik", "Ankara", 10000, 4.0, 1),
        ]
        cur.executemany("INSERT INTO araclar VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", araclar)

        kullanicilar = [
            (1, "Ahmet Yılmaz", "12ABC123", "0532 111 22 33"),
            (2, "Ayşe Kaya", "34DEF456", "0541 333 44 55"),
            (3, "Mehmet Demir", "56GHI789", "0555 666 77 88"),
            (4, "Zeynep Çelik", "78JKL012", "0544 999 00 11"),
            (5, "Caner Türk", "90MNO345", "0533 222 33 44"),
            (6, "Elif Can", "11PQR678", "0531 444 55 66"),
            (7, "Emre Şahin", "22STU901", "0530 555 66 77"),
            (8, "Fatma Yıldız", "33VWX234", "0543 666 77 88"),
            (9, "Kemal Kara", "44YZA567", "0542 777 88 99"),
            (10, "Leyla Ak", "55BCD890", "0546 888 99 00"),
            (11, "Murat Boz", "66EFG123", "0532 999 00 11"),
            (12, "Neslihan Yurt", "77HIJ456", "0541 000 11 22"),
            (13, "Orhan Veli", "88KLM789", "0555 111 22 33"),
            (14, "Pelin Su", "99NOP012", "0544 222 33 44"),
            (15, "Rıza Sarraf", "00QRS345", "0533 333 44 55")
        ]
        cur.executemany("INSERT INTO kullanicilar VALUES (?, ?, ?, ?)", kullanicilar)
        
        from datetime import timedelta
        for i in range(1, 11):
            bas = datetime.now() - timedelta(days=i, hours=2)
            bit = bas + timedelta(hours=3)
            ucret = 150 * araclar[i-1][7]
            cur.execute("""
                INSERT INTO kiralamalar (arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic, bitis, aktif, ucret)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (i, i, "İstanbul", "Ankara", bas.strftime("%Y-%m-%d %H:%M:%S"), bit.strftime("%Y-%m-%d %H:%M:%S"), 0, ucret))
        conn.commit()

    def _get_arac_from_row(self, row):
        return Arac(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], bool(row[8]))

    def _get_kullanici_from_row(self, row):
        return Kullanici(row[0], row[1], row[2], row[3])

    def get_araclar(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM araclar")
        araclar = {}
        for r in cur.fetchall():
            araclar[r[0]] = self._get_arac_from_row(r)
        conn.close()
        return araclar

    def get_musait_araclar(self):
        return {k: v for k, v in self.get_araclar().items() if v.get_musait_mi()}

    def arac_ekle(self, arac: Arac):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM araclar WHERE id=?", (arac.get_arac_id(),))
        if cur.fetchone():
            conn.close()
            return False, f"ID {arac.get_arac_id()} zaten kayıtlı."
        cur.execute("INSERT INTO araclar VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            arac.get_arac_id(), arac.get_marka(), arac.get_model(), arac.get_tip(), arac.get_yakit_tipi(), arac.get_sehir(),
            arac.get_kilometre(), arac.get_km_ucreti(), 1 if arac.get_musait_mi() else 0
        ))
        conn.commit()
        conn.close()
        return True, f"✓ '{arac.get_tam_ad()}' sisteme eklendi."

    def arac_guncelle(self, arac_id, marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM araclar WHERE id=?", (arac_id,))
        if not cur.fetchone():
            conn.close()
            return False, "Araç bulunamadı."
        cur.execute("UPDATE araclar SET marka=?, model=?, tip=?, yakit_tipi=?, sehir=?, kilometre=?, km_ucreti=? WHERE id=?", (
            marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti, arac_id
        ))
        conn.commit()
        conn.close()
        return True, "✓ Araç bilgileri güncellendi."

    def arac_sil(self, arac_id):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT musait_mi FROM araclar WHERE id=?", (arac_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False, "Araç bulunamadı."
        if not row[0]:
            conn.close()
            return False, "Araç şu an kirada olduğu için silinemez."
        cur.execute("DELETE FROM araclar WHERE id=?", (arac_id,))
        conn.commit()
        conn.close()
        return True, "✓ Araç başarıyla silindi."

    def get_kullanicilar(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM kullanicilar")
        kullanicilar = {}
        for r in cur.fetchall():
            u = self._get_kullanici_from_row(r)
            cur.execute("SELECT * FROM kiralamalar WHERE kullanici_id=?", (u.get_kullanici_id(),))
            for kr in cur.fetchall():
                cur.execute("SELECT * FROM araclar WHERE id=?", (kr[1],))
                arow = cur.fetchone()
                if arow:
                    a = self._get_arac_from_row(arow)
                    bas = datetime.strptime(kr[5], "%Y-%m-%d %H:%M:%S")
                    bit = datetime.strptime(kr[6], "%Y-%m-%d %H:%M:%S") if kr[6] else None
                    k = Kiralama(kr[0], a, u, kr[3], kr[4], bas, bit, bool(kr[7]), kr[8])
                    u.kiralama_ekle(k)
            kullanicilar[r[0]] = u
        conn.close()
        return kullanicilar

    def kullanici_ekle(self, kullanici: Kullanici):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM kullanicilar WHERE id=?", (kullanici.get_kullanici_id(),))
        if cur.fetchone():
            conn.close()
            return False, f"ID {kullanici.get_kullanici_id()} zaten kayıtlı."
        cur.execute("SELECT id FROM kullanicilar WHERE ehliyet_no=?", (kullanici.get_ehliyet_no(),))
        if cur.fetchone():
            conn.close()
            return False, "Bu ehliyet numarası zaten kayıtlı."
        cur.execute("INSERT INTO kullanicilar VALUES (?, ?, ?, ?)", (
            kullanici.get_kullanici_id(), kullanici.get_ad(), kullanici.get_ehliyet_no(), kullanici.get_telefon()
        ))
        conn.commit()
        conn.close()
        return True, f"✓ '{kullanici.get_ad()}' kayıt edildi."

    def kiralama_baslat(self, arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic: datetime):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT musait_mi, km_ucreti FROM araclar WHERE id=?", (arac_id,))
        arow = cur.fetchone()
        if not arow:
            conn.close(); return False, "Araç bulunamadı."
        if not arow[0]:
            conn.close(); return False, "Araç şu an başka bir kullanıcıda."
        
        km_ucreti = arow[1]
        
        cur.execute("SELECT id FROM kullanicilar WHERE id=?", (kullanici_id,))
        if not cur.fetchone():
            conn.close(); return False, "Kullanıcı bulunamadı."

        cur.execute("SELECT id FROM kiralamalar WHERE kullanici_id=? AND aktif=1", (kullanici_id,))
        if cur.fetchone():
            conn.close(); return False, "Kullanıcı zaten aktif bir kiralamaya sahip."
            
        mesafe = get_mesafe(alis_sehri, birakis_sehri)
        toplam_ucret = round(mesafe * km_ucreti, 2)

        cur.execute("UPDATE araclar SET musait_mi=0 WHERE id=?", (arac_id,))
        cur.execute('''
            INSERT INTO kiralamalar (arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic, aktif, ucret)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic.strftime("%Y-%m-%d %H:%M:%S"), toplam_ucret))
        conn.commit()
        conn.close()
        return True, "✓ Kiralama başlatıldı."

    def kiralama_bitir(self, kiralama_id, bitis: datetime):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT arac_id, alis_sehri, birakis_sehri, baslangic, aktif FROM kiralamalar WHERE id=?", (kiralama_id,))
        row = cur.fetchone()
        if not row:
            conn.close(); return False, "Kiralama bulunamadı."
        arac_id, alis_sehri, birakis_sehri, bas_str, aktif = row
        if not aktif:
            conn.close(); return False, "Bu kiralama zaten sona ermiş."
        
        baslangic = datetime.strptime(bas_str, "%Y-%m-%d %H:%M:%S")
        if bitis <= baslangic:
            conn.close(); return False, "Bitiş saati başlangıçtan önce olamaz."

        cur.execute("SELECT km_ucreti FROM araclar WHERE id=?", (arac_id,))
        km_ucreti = cur.fetchone()[0]

        mesafe = get_mesafe(alis_sehri, birakis_sehri)
        toplam_ucret = round(mesafe * km_ucreti, 2)

        cur.execute("UPDATE kiralamalar SET bitis=?, aktif=0, ucret=? WHERE id=?", 
            (bitis.strftime("%Y-%m-%d %H:%M:%S"), toplam_ucret, kiralama_id))
        cur.execute("UPDATE araclar SET musait_mi=1, kilometre=kilometre+? WHERE id=?", (mesafe, arac_id))
        conn.commit()
        conn.close()
        return True, f"✓ Kiralama bitti. Mesafe: {mesafe} km | Ücret: ₺{toplam_ucret:.2f}"

    def get_kiralamalar(self):
        araclar = self.get_araclar()
        kullanicilar = self.get_kullanicilar()
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM kiralamalar ORDER BY id ASC")
        kiralamalar = []
        for kr in cur.fetchall():
            a = araclar.get(kr[1])
            u = kullanicilar.get(kr[2])
            if not a or not u: continue
            bas = datetime.strptime(kr[5], "%Y-%m-%d %H:%M:%S")
            bit = datetime.strptime(kr[6], "%Y-%m-%d %H:%M:%S") if kr[6] else None
            k = Kiralama(kr[0], a, u, kr[3], kr[4], bas, bit, bool(kr[7]), kr[8])
            kiralamalar.append(k)
        conn.close()
        return kiralamalar

    def get_aktif_kiralamalar(self):
        return [k for k in self.get_kiralamalar() if k.get_aktif()]

    def get_gecmis_kiralamalar(self):
        return [k for k in self.get_kiralamalar() if not k.get_aktif()]

    def toplam_gelir(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT SUM(ucret) FROM kiralamalar WHERE aktif=0")
        val = cur.fetchone()[0]
        conn.close()
        return val if val else 0.0