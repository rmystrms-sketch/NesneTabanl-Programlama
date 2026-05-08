import sqlite3
import os

class EtkinlikBackend:
    def __init__(self):
        self.db_path = "etkinlik_veritabani.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        self.ana_veriler = []
        self.katilimci_havuzu = {}
        
        self.veritabanini_kur()
        
        # H11 gibi hatalı verileri düzelt (Eski verilerden kalma)
        self.cursor.execute("UPDATE katilimcilar SET detay = REPLACE(detay, 'H11', 'H9'), durum_str = REPLACE(durum_str, 'H11', 'H9') WHERE detay LIKE '%H11%'")
        
        # E-204 (Geleceğin Teknolojileri) ayakta verilerini koltuğa çevir
        self.cursor.execute("UPDATE katilimcilar SET detay = 'A1', durum_str = 'Biletli (Koltuk: A1)' WHERE id = 'K-301' AND detay = 'Ayakta'")
        self.cursor.execute("UPDATE katilimcilar SET detay = 'A2', durum_str = 'Biletli (Koltuk: A2)' WHERE id = 'K-302' AND detay = 'Ayakta'")
        
        self.conn.commit()
        
        self.verileri_yukle()
        
        # Eğer veritabanı boşsa örnek verileri ekle
        if not self.ana_veriler:
            self.ornek_verileri_ekle()
            self.verileri_yukle()

    def veritabanini_kur(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS etkinlikler (
                id TEXT PRIMARY KEY,
                tur TEXT,
                ad TEXT,
                sehir TEXT,
                mekan TEXT,
                tarih TEXT,
                bas TEXT,
                bit TEXT,
                satilan INTEGER,
                toplam INTEGER,
                fiyat TEXT,
                durum TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS katilimcilar (
                id TEXT PRIMARY KEY,
                etkinlik_id TEXT,
                ad_soyad TEXT,
                email TEXT,
                detay TEXT,
                adet INTEGER,
                tutar TEXT,
                durum_str TEXT,
                FOREIGN KEY (etkinlik_id) REFERENCES etkinlikler (id)
            )
        """)
        self.conn.commit()

    def verileri_yukle(self):
        # Etkinlikleri yükle
        self.cursor.execute("SELECT * FROM etkinlikler")
        columns = [column[0] for column in self.cursor.description]
        self.ana_veriler = []
        for row in self.cursor.fetchall():
            self.ana_veriler.append(dict(zip(columns, row)))
            
        # Katılımcıları yükle
        self.cursor.execute("SELECT * FROM katilimcilar")
        self.katilimci_havuzu = {}
        for row in self.cursor.fetchall():
            # row format: (id, e_id, ad, email, detay, adet, tutar, durum_str)
            e_id = row[1]
            if e_id not in self.katilimci_havuzu:
                self.katilimci_havuzu[e_id] = []
            # GUI'nin beklediği format: (k_id, ad, email, detay, adet, tutar, durum_str)
            self.katilimci_havuzu[e_id].append((row[0], row[2], row[3], row[4], row[5], row[6], row[7]))
            


    def ornek_verileri_ekle(self):
        ornek_etkinlikler = [
            ("E-201", "Konser", "Yaz Konseri", "İstanbul", "Ataköy", "21.06.2026", "20:00", "23:00", 3, 500, "200 TL", "Aktif"),
            ("E-202", "Tiyatro", "Hamlet", "Ankara", "Devlet Tiyatrosu", "15.07.2026", "19:00", "21:30", 2, 150, "120 TL", "Aktif"),
            ("E-203", "Sinema", "Interstellar Gösterimi", "İzmir", "Açık Hava Sineması", "05.08.2026", "21:00", "23:45", 6, 300, "80 TL", "Aktif"),
            ("E-204", "Seminer", "Geleceğin Teknolojileri", "Bursa", "Teknoloji Merkezi", "10.09.2026", "14:00", "17:00", 2, 200, "150 TL", "Aktif"),
            ("E-205", "Eğitim", "Python ile Veri Bilimi", "Antalya", "Bilim Parkı", "25.09.2026", "09:00", "16:00", 0, 50, "500 TL", "Gelecek Etkinlik")
        ]
        self.cursor.executemany("INSERT INTO etkinlikler VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", ornek_etkinlikler)
        
        ornek_katilimcilar = [
            ("K-001", "E-201", "Elvan Yıldız", "elvan@mail.com", "Sahne Önü (+100 TL)", 2, "600 TL", "Biletli (Sahne Önü)"),
            ("K-002", "E-201", "Ahmet Yılmaz", "ahmet@mail.com", "Sahne Ortası", 1, "200 TL", "Biletli"),
            ("K-101", "E-202", "Merve Ay", "merve@mail.com", "A1, A2", 2, "240 TL", "Biletli (Koltuk: A1, A2)"),
            ("K-201", "E-203", "Cem Kaya", "cem@mail.com", "G15", 1, "80 TL", "Biletli (Koltuk: G15)"),
            ("K-202", "E-203", "Deniz Şahin", "deniz@mail.com", "H9, H10", 2, "160 TL", "Biletli (Koltuk: H9, H10)"),
            ("K-203", "E-203", "Burak Çelik", "burak@mail.com", "F4, F5, F6", 3, "240 TL", "Biletli (Koltuk: F4, F5, F6)"),
            ("K-301", "E-204", "Zeynep Demir", "zeynep@mail.com", "A1", 1, "150 TL", "Biletli (Koltuk: A1)"),
            ("K-302", "E-204", "Caner Türk", "caner@mail.com", "A2", 1, "150 TL", "Biletli (Koltuk: A2)")
        ]
        self.cursor.executemany("INSERT INTO katilimcilar VALUES (?,?,?,?,?,?,?,?)", ornek_katilimcilar)
        self.conn.commit()

    def veri_hesapla(self):
        for e in self.ana_veriler:
            kisiler = self.get_katilimcilar_by_id(e['id'])
            e['satilan'] = sum(k[4] if len(k) > 4 else 1 for k in kisiler)
            if e['satilan'] >= e['toplam']:
                e['durum'] = "Bileti Tükenmiş"
            elif e['durum'] == "Bileti Tükenmiş" and e['satilan'] < e['toplam']:
                e['durum'] = "Aktif"
            
            # Veritabanındaki satılan miktarını ve durumu da güncelle
            self.cursor.execute("UPDATE etkinlikler SET satilan = ?, durum = ? WHERE id = ?", (e['satilan'], e['durum'], e['id']))
        self.conn.commit()

    def get_katilimcilar_by_id(self, e_id):
        return self.katilimci_havuzu.get(e_id, [])

    def etkinlik_ekle(self, veri):
        cols = ', '.join(veri.keys())
        placeholders = ':' + ', :'.join(veri.keys())
        query = f"INSERT INTO etkinlikler ({cols}) VALUES ({placeholders})"
        self.cursor.execute(query, veri)
        self.conn.commit()
        self.verileri_yukle()

    def etkinlik_guncelle(self, e_id, veri):
        placeholders = ', '.join([f"{key} = ?" for key in veri.keys()])
        query = f"UPDATE etkinlikler SET {placeholders} WHERE id = ?"
        self.cursor.execute(query, list(veri.values()) + [e_id])
        self.conn.commit()
        self.verileri_yukle()

    def etkinlik_sil(self, e_id):
        self.cursor.execute("DELETE FROM katilimcilar WHERE etkinlik_id = ?", (e_id,))
        self.cursor.execute("DELETE FROM etkinlikler WHERE id = ?", (e_id,))
        self.conn.commit()
        self.verileri_yukle()

    def katilimci_ekle(self, e_id, veri):
        # veri formatı: (k_id, ad, email, detay, adet, tutar, durum_str)
        query = "INSERT INTO katilimcilar VALUES (?,?,?,?,?,?,?,?)"
        # e_id'yi 2. sıraya ekliyoruz
        params = (veri[0], e_id, veri[1], veri[2], veri[3], veri[4], veri[5], veri[6])
        self.cursor.execute(query, params)
        self.conn.commit()
        self.verileri_yukle()

    def katilimci_guncelle(self, k_id, e_id, veri):
        # veri formatı: (k_id, ad, email, detay, adet, tutar, durum_str)
        query = "UPDATE katilimcilar SET ad_soyad=?, email=?, detay=?, adet=?, tutar=?, durum_str=? WHERE id=? AND etkinlik_id=?"
        params = (veri[1], veri[2], veri[3], veri[4], veri[5], veri[6], k_id, e_id)
        self.cursor.execute(query, params)
        self.conn.commit()
        self.verileri_yukle()

    def katilimci_sil(self, k_id, e_id):
        self.cursor.execute("DELETE FROM katilimcilar WHERE id = ? AND etkinlik_id = ?", (k_id, e_id))
        self.conn.commit()
        self.verileri_yukle()

    def yeni_katilimci_id_uret(self, e_id):
        self.cursor.execute("SELECT id FROM katilimcilar")
        ids = self.cursor.fetchall()
        return f"K-{100 + len(ids) + 1}"

    def yeni_id_uret(self):
        self.cursor.execute("SELECT id FROM etkinlikler")
        ids = self.cursor.fetchall()
        return f"E-{200 + len(ids) + 1}"

    def dolu_koltuklari_getir(self, e_id, haric_kisi_id=None):
        query = "SELECT id, detay, durum_str FROM katilimcilar WHERE etkinlik_id = ?"
        self.cursor.execute(query, [e_id])
        dolu_liste = []
        import re
        regex = r'[A-Z]\d+'
        
        for row in self.cursor.fetchall():
            k_id, detay, durum = row
            if haric_kisi_id and str(k_id) == str(haric_kisi_id):
                continue
            
            for metin in [detay, durum]:
                if metin:
                    bulunanlar = re.findall(regex, metin)
                    for k in bulunanlar:
                        if k not in dolu_liste:
                            dolu_liste.append(k)
        return dolu_liste


