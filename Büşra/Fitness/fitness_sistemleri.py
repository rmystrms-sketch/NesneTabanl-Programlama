from datetime import datetime, timedelta
import sqlite3
import os

class FitnessSistemi:
    def __init__(self):
        self.db_yolu = "fitness_veritabani.db"
        self.baglanti = sqlite3.connect(self.db_yolu)
        self.baglanti.row_factory = sqlite3.Row
        self.cursor = self.baglanti.cursor()
        self.tablolari_olustur()
        
        # Eğer veritabanı boşsa başlangıç verilerini ekle
        self.cursor.execute("SELECT COUNT(*) FROM sporcular")
        if self.cursor.fetchone()[0] == 0:
            self.baslangic_verilerini_yukle()

    def tablolari_olustur(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sporcular (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT,
                yas INTEGER,
                cin TEXT,
                boy INTEGER,
                kilo REAL,
                hedef REAL,
                paket TEXT,
                kayit TEXT,
                bitis TEXT,
                durum TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS antrenman_gecmisi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sporcu_id INTEGER,
                tarih TEXT,
                hareketler TEXT,
                notlar TEXT,
                kalori TEXT,
                FOREIGN KEY (sporcu_id) REFERENCES sporcular (id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS beslenme_gecmisi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sporcu_id INTEGER,
                tarih TEXT,
                liste TEXT,
                notlar TEXT,
                toplam_kalori TEXT,
                FOREIGN KEY (sporcu_id) REFERENCES sporcular (id) ON DELETE CASCADE
            )
        """)
        self.baglanti.commit()

    def baslangic_verilerini_yukle(self):
        # Bu veriler sadece veritabanı ilk kez oluşturulduğunda bir kez eklenir.
        sporcular = [
            {
                "ad": "Mert Yılmaz", "yas": 28, "cin": "Erkek", "boy": 180, "kilo": 82, "hedef": 75,
                "paket": "3 Aylık", "kayit": "01.03.2026", "bitis": "01.06.2026", "durum": "AKTİF",
                "antrenman": [
                    {"tarih": "22.04.2026", "hareketler": "Bench Press 3x10 60kg\nSquat 4x12 80kg", "notlar": "Form iyi, ağırlık artırıldı", "kalori": 450},
                    {"tarih": "20.04.2026", "hareketler": "Deadlift 3x8 90kg\nKoşu 15dk", "notlar": "Orta seviye performans", "kalori": 380}
                ],
                "beslenme": [
                    {"tarih": "22.04.2026", "liste": "Kahvaltı: Yulaf\nÖğle: Tavuk\nAkşam: Salata", "notlar": "Diyet düzenli", "toplam_kalori": 1800}
                ]
            },
            {
                "ad": "Selin Aydın", "yas": 24, "cin": "Kadın", "boy": 165, "kilo": 58, "hedef": 55,
                "paket": "6 Aylık", "kayit": "10.02.2026", "bitis": "10.08.2026", "durum": "AKTİF",
                "antrenman": [
                    {"tarih": "21.04.2026", "hareketler": "Pilates 45dk\nKoşu 20dk", "notlar": "Esneklik iyi", "kalori": 300}
                ],
                "beslenme": [
                    {"tarih": "21.04.2026", "liste": "Dengeli beslenme", "notlar": "Şeker azaltıldı", "toplam_kalori": 1600}
                ]
            },
            {
                "ad": "Caner Demir", "yas": 32, "cin": "Erkek", "boy": 175, "kilo": 90, "hedef": 80,
                "paket": "6 Aylık", "kayit": "15.01.2026", "bitis": "15.07.2026", "durum": "AKTİF",
                "antrenman": [
                    {"tarih": "22.04.2026", "hareketler": "Lat Pulldown 4x10 50kg\nRowing 3x12 40kg", "notlar": "Sırt antrenmanı yoğun geçti", "kalori": 410},
                    {"tarih": "19.04.2026", "hareketler": "Kardiyo - Bisiklet 30dk", "notlar": "Hafif tempo", "kalori": 250}
                ],
                "beslenme": [
                    {"tarih": "22.04.2026", "liste": "Kahvaltı: Yumurta ve peynir\nÖğle: Et sote\nAkşam: Izgara tavuk", "notlar": "Protein ağırlıklı", "toplam_kalori": 2100}
                ]
            },
            {
                "ad": "Elif Yıldız", "yas": 29, "cin": "Kadın", "boy": 170, "kilo": 65, "hedef": 60,
                "paket": "1 Aylık", "kayit": "01.04.2026", "bitis": "01.05.2026", "durum": "AKTİF",
                "antrenman": [
                    {"tarih": "21.04.2026", "hareketler": "Zumba 45dk", "notlar": "Eğlenceli ve yüksek tempo", "kalori": 350}
                ],
                "beslenme": [
                    {"tarih": "21.04.2026", "liste": "Kahvaltı: Smoothie\nÖğle: Kinoa Salatası\nAkşam: Sebze çorbası", "notlar": "Detoks günü", "toplam_kalori": 1400}
                ]
            },
            {
                "ad": "Ahmet Koç", "yas": 45, "cin": "Erkek", "boy": 182, "kilo": 88, "hedef": 85,
                "paket": "1 Yıllık", "kayit": "10.01.2026", "bitis": "10.01.2027", "durum": "AKTİF",
                "antrenman": [
                    {"tarih": "20.04.2026", "hareketler": "Yürüyüş 60dk\nHafif Ağırlık 20dk", "notlar": "Eklemler yorulmadan tamamlandı", "kalori": 320}
                ],
                "beslenme": [
                    {"tarih": "20.04.2026", "liste": "Kahvaltı: Klasik Türk\nÖğle: Ev yemekleri\nAkşam: Balık", "notlar": "Öğünler düzenli", "toplam_kalori": 1950}
                ]
            },
            {
                "ad": "Zeynep Arslan", "yas": 22, "cin": "Kadın", "boy": 160, "kilo": 52, "hedef": 50,
                "paket": "3 Aylık", "kayit": "05.03.2026", "bitis": "05.06.2026", "durum": "AKTİF",
                "antrenman": [
                    {"tarih": "22.04.2026", "hareketler": "Yoga 50dk\nEsneme 10dk", "notlar": "Çok rahatlatıcı", "kalori": 200}
                ],
                "beslenme": [
                    {"tarih": "22.04.2026", "liste": "Kahvaltı: Meyve Tabağı\nÖğle: Salata\nAkşam: Izgara Somon", "notlar": "Hafif beslenme", "toplam_kalori": 1300}
                ]
            },
            {
                "ad": "Burak Şahin", "yas": 26, "cin": "Erkek", "boy": 185, "kilo": 75, "hedef": 85,
                "paket": "6 Aylık", "kayit": "12.02.2026", "bitis": "12.08.2026", "durum": "AKTİF",
                "antrenman": [
                    {"tarih": "23.04.2026", "hareketler": "Bench Press 4x8 70kg\nIncline Dumbbell 3x10 25kg\nBicep Curl 3x12 15kg", "notlar": "Hacim (Bulking) programı", "kalori": 550},
                    {"tarih": "21.04.2026", "hareketler": "Squat 4x8 90kg\nLeg Press 3x10 120kg", "notlar": "Bacaklar zorlandı", "kalori": 500}
                ],
                "beslenme": [
                    {"tarih": "23.04.2026", "liste": "Kahvaltı: 5 Yumurta, Yulaf\nÖğle: Pirinç Pilavı, Tavuk Göğsü\nAkşam: Makarna, Kıyma", "notlar": "Kalori fazlası alındı", "toplam_kalori": 3200}
                ]
            }
        ]
        
        for s in sporcular:
            self.cursor.execute("""
                INSERT INTO sporcular (ad, yas, cin, boy, kilo, hedef, paket, kayit, bitis, durum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (s["ad"], s["yas"], s["cin"], s["boy"], s["kilo"], s["hedef"], s["paket"], s["kayit"], s["bitis"], s["durum"]))
            sporcu_id = self.cursor.lastrowid
            
            for ant in s["antrenman"]:
                self.cursor.execute("""
                    INSERT INTO antrenman_gecmisi (sporcu_id, tarih, hareketler, notlar, kalori)
                    VALUES (?, ?, ?, ?, ?)
                """, (sporcu_id, ant["tarih"], ant["hareketler"], ant["notlar"], str(ant["kalori"])))
                
            for bes in s["beslenme"]:
                self.cursor.execute("""
                    INSERT INTO beslenme_gecmisi (sporcu_id, tarih, liste, notlar, toplam_kalori)
                    VALUES (?, ?, ?, ?, ?)
                """, (sporcu_id, bes["tarih"], bes["liste"], bes["notlar"], str(bes["toplam_kalori"])))
        
        self.baglanti.commit()

    @property
    def sporcular(self):
        # GUI'nin beklediği liste yapısını döndürür
        self.cursor.execute("SELECT * FROM sporcular")
        sporcular_rows = self.cursor.fetchall()
        
        sonuc = []
        for row in sporcular_rows:
            sp_dict = dict(row)
            sid = sp_dict["id"]
            
            # Antrenman geçmişini çek
            self.cursor.execute("SELECT tarih, hareketler, notlar, kalori FROM antrenman_gecmisi WHERE sporcu_id = ? ORDER BY id DESC", (sid,))
            sp_dict["antrenman_gecmisi"] = [dict(r) for r in self.cursor.fetchall()]
            
            # Beslenme geçmişini çek
            self.cursor.execute("SELECT tarih, liste, notlar, toplam_kalori FROM beslenme_gecmisi WHERE sporcu_id = ? ORDER BY id DESC", (sid,))
            sp_dict["beslenme_gecmisi"] = [dict(r) for r in self.cursor.fetchall()]
            
            sonuc.append(sp_dict)
        return sonuc

    def tarih_hesapla(self, paket_metni):
        bas = datetime.now()
        if "7" in paket_metni:
            bit = bas + timedelta(days=7)
        else:
            ay = 1 if "1 A" in paket_metni else 3 if "3 A" in paket_metni else 6 if "6 A" in paket_metni else 12
            bit = bas + timedelta(days=ay * 30)
        return bas.strftime("%d.%m.%Y"), bit.strftime("%d.%m.%Y")

    def uyelik_durumu_getir(self, bitis_str):
        try:
            bit = datetime.strptime(bitis_str, "%d.%m.%Y")
            bugun = datetime.now()
            fark = (bit - bugun).days
            if fark < 0: return "❌ BİTTİ"
            if fark <= 3: return "⚠️ AZ KALDI"
            return "✅ AKTİF"
        except:
            return "❓ BİLİNMİYOR"

    def sporcu_ekle(self, ad, cin, yas, paket, boy, kilo, hedef):
        if not ad:
            return None

        kayit, bit = self.tarih_hesapla(paket)
        durum_metin = self.uyelik_durumu_getir(bit)

        self.cursor.execute("""
            INSERT INTO sporcular (ad, yas, cin, boy, kilo, hedef, paket, kayit, bitis, durum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ad, yas, cin, int(float(boy)), kilo, hedef, paket, kayit, bit, durum_metin))
        
        sporcu_id = self.cursor.lastrowid
        self.baglanti.commit()
        
        return self.sporcu_getir(sporcu_id)

    def sporcu_sil(self, id_no):
        self.cursor.execute("DELETE FROM sporcular WHERE id = ?", (id_no,))
        self.baglanti.commit()

    def sporcu_guncelle(self, id_no, ad, yas, cin, paket, boy, kilo, hedef):
        _, bit = self.tarih_hesapla(paket)
        durum_metin = self.uyelik_durumu_getir(bit)
        
        self.cursor.execute("""
            UPDATE sporcular 
            SET ad=?, yas=?, cin=?, paket=?, boy=?, kilo=?, hedef=?, bitis=?, durum=?
            WHERE id=?
        """, (ad, yas, cin, paket, int(float(boy)), kilo, hedef, bit, durum_metin, id_no))
        
        self.baglanti.commit()
        return self.sporcu_getir(id_no)

    def antrenman_ekle(self, id_no, antrenman_ozeti):
        self.cursor.execute("""
            INSERT INTO antrenman_gecmisi (sporcu_id, tarih, hareketler, notlar, kalori)
            VALUES (?, ?, ?, ?, ?)
        """, (id_no, antrenman_ozeti["tarih"], antrenman_ozeti["hareketler"], antrenman_ozeti["notlar"], str(antrenman_ozeti["kalori"])))
        self.baglanti.commit()
        return True

    def beslenme_ekle(self, id_no, beslenme_ozeti):
        self.cursor.execute("""
            INSERT INTO beslenme_gecmisi (sporcu_id, tarih, liste, notlar, toplam_kalori)
            VALUES (?, ?, ?, ?, ?)
        """, (id_no, beslenme_ozeti["tarih"], beslenme_ozeti["liste"], beslenme_ozeti["notlar"], str(beslenme_ozeti["toplam_kalori"])))
        self.baglanti.commit()
        return True

    def kilo_guncelle(self, id_no, yeni_kilo):
        # Önce bitiş tarihini almamız lazım ki durumu güncelleyelim
        self.cursor.execute("SELECT bitis FROM sporcular WHERE id = ?", (id_no,))
        row = self.cursor.fetchone()
        if row:
            bitis = row["bitis"]
            durum_metin = self.uyelik_durumu_getir(bitis)
            self.cursor.execute("""
                UPDATE sporcular SET kilo = ?, durum = ? WHERE id = ?
            """, (yeni_kilo, durum_metin, id_no))
            self.baglanti.commit()
            return self.sporcu_getir(id_no)
        return None

    def sporcu_getir(self, id_no):
        self.cursor.execute("SELECT * FROM sporcular WHERE id = ?", (id_no,))
        row = self.cursor.fetchone()
        if row:
            sp_dict = dict(row)
            # Geçmişleri de ekle
            self.cursor.execute("SELECT tarih, hareketler, notlar, kalori FROM antrenman_gecmisi WHERE sporcu_id = ? ORDER BY id DESC", (id_no,))
            sp_dict["antrenman_gecmisi"] = [dict(r) for r in self.cursor.fetchall()]
            
            self.cursor.execute("SELECT tarih, liste, notlar, toplam_kalori FROM beslenme_gecmisi WHERE sporcu_id = ? ORDER BY id DESC", (id_no,))
            sp_dict["beslenme_gecmisi"] = [dict(r) for r in self.cursor.fetchall()]
            
            return sp_dict
        return None