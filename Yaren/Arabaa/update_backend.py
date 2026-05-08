import re
import os

backend_path = r'\\ibstsfilesrv01\ismyo$\2500005225\Desktop\Nesne Tabanlı PR\Yaren\arac_backend.py'
with open(backend_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacements
content = content.replace('saatlik_ucret', 'km_ucreti')
content = content.replace('saatlik', 'km')

content = content.replace(
    'def __init__(self, arac_id, marka, model, tip, kilometre, km_ucreti, musait_mi=True):',
    'def __init__(self, arac_id, marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti, musait_mi=True):\n        self._yakit_tipi    = yakit_tipi\n        self._sehir         = sehir'
)
content = content.replace(
    'self._tip           = tip\n        self._kilometre     = kilometre',
    'self._tip           = tip\n        self._yakit_tipi    = yakit_tipi\n        self._sehir         = sehir\n        self._kilometre     = kilometre'
)

content = content.replace(
    'def get_tip(self):           return self._tip',
    'def get_tip(self):           return self._tip\n    def get_yakit_tipi(self):    return self._yakit_tipi\n    def get_sehir(self):         return self._sehir'
)

content = content.replace(
    'def arac_bilgisi_guncelle(self, marka, model, tip, kilometre, km_ucreti):',
    'def arac_bilgisi_guncelle(self, marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti):\n        self._yakit_tipi = yakit_tipi\n        self._sehir = sehir'
)

content = content.replace(
    'def __init__(self, kiralama_id, arac: Arac, kullanici: Kullanici, baslangic_saati: datetime, bitis_saati=None, aktif=True, toplam_ucret=0.0):',
    'def __init__(self, kiralama_id, arac: Arac, kullanici: Kullanici, alis_sehri, birakis_sehri, baslangic_saati: datetime, bitis_saati=None, aktif=True, toplam_ucret=0.0):\n        self._alis_sehri      = alis_sehri\n        self._birakis_sehri   = birakis_sehri'
)
content = content.replace(
    'self._kullanici       = kullanici\n        self._baslangic_saati = baslangic_saati',
    'self._kullanici       = kullanici\n        self._alis_sehri      = alis_sehri\n        self._birakis_sehri   = birakis_sehri\n        self._baslangic_saati = baslangic_saati'
)

content = content.replace(
    'def get_kullanici(self):       return self._kullanici',
    'def get_kullanici(self):       return self._kullanici\n    def get_alis_sehri(self):      return self._alis_sehri\n    def get_birakis_sehri(self):   return self._birakis_sehri'
)

content = content.replace(
    'def kiralama_bitir(self, bitis_saati: datetime, eklenen_km: int = 0):',
    'def kiralama_bitir(self, bitis_saati: datetime):'
)

content = content.replace(
    '"baslangic":  self._baslangic_saati.strftime("%d.%m.%Y %H:%M"),',
    '"alis":       self._alis_sehri,\n            "birakis":    self._birakis_sehri,\n            "baslangic":  self._baslangic_saati.strftime("%d.%m.%Y %H:%M"),'
)

content = content.replace(
    'tip TEXT,\n                kilometre INTEGER,',
    'tip TEXT,\n                yakit_tipi TEXT,\n                sehir TEXT,\n                kilometre INTEGER,'
)

content = content.replace(
    'kullanici_id INTEGER,\n                baslangic TEXT,',
    'kullanici_id INTEGER,\n                alis_sehri TEXT,\n                birakis_sehri TEXT,\n                baslangic TEXT,'
)

content = content.replace(
    'INSERT INTO kiralamalar (arac_id, kullanici_id, baslangic, bitis, aktif, ucret)',
    'INSERT INTO kiralamalar (arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic, bitis, aktif, ucret)'
)

content = content.replace(
    'VALUES (?, ?, ?, ?, ?, ?)',
    'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
)
content = content.replace(
    'VALUES (?, ?, ?, 1, 0.0)',
    'VALUES (?, ?, ?, ?, ?, 1, 0.0)'
)
content = content.replace(
    '(arac_id, kullanici_id, bas.strftime(\'%Y-%m-%d %H:%M:%S\'), None, 1, 0.0)',
    '(arac_id, kullanici_id, "İstanbul", "İstanbul", bas.strftime(\'%Y-%m-%d %H:%M:%S\'), None, 1, 0.0)'
)

dummy_str = '''    def _dummy_veri_olustur(self, conn):
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
        conn.commit()'''

content = re.sub(r'    def _dummy_veri_olustur\(self, conn\):.*?(?=    def _get_arac_from_row)', dummy_str + '\n\n', content, flags=re.DOTALL)

content = content.replace(
    'return Arac(row[0], row[1], row[2], row[3], row[4], row[5], bool(row[6]))',
    'return Arac(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], bool(row[8]))'
)

content = content.replace(
    'INSERT INTO araclar VALUES (?, ?, ?, ?, ?, ?, ?)',
    'INSERT INTO araclar VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
)
content = content.replace(
    'arac.get_arac_id(), arac.get_marka(), arac.get_model(), arac.get_tip(),\n            arac.get_kilometre(), arac.get_km_ucreti(), 1 if arac.get_musait_mi() else 0',
    'arac.get_arac_id(), arac.get_marka(), arac.get_model(), arac.get_tip(), arac.get_yakit_tipi(), arac.get_sehir(),\n            arac.get_kilometre(), arac.get_km_ucreti(), 1 if arac.get_musait_mi() else 0'
)

content = content.replace(
    'def arac_guncelle(self, arac_id, marka, model, tip, kilometre, km_ucreti):',
    'def arac_guncelle(self, arac_id, marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti):'
)
content = content.replace(
    'SET marka=?, model=?, tip=?, kilometre=?, km_ucreti=? WHERE id=?',
    'SET marka=?, model=?, tip=?, yakit_tipi=?, sehir=?, kilometre=?, km_ucreti=? WHERE id=?'
)
content = content.replace(
    'marka, model, tip, kilometre, km_ucreti, arac_id',
    'marka, model, tip, yakit_tipi, sehir, kilometre, km_ucreti, arac_id'
)

content = content.replace(
    'k = Kiralama(kr[0], a, u, bas, bit, bool(kr[5]), kr[6])',
    'k = Kiralama(kr[0], a, u, kr[3], kr[4], bas, bit, bool(kr[7]), kr[8])'
)

content = content.replace(
    'def kiralama_baslat(self, arac_id, kullanici_id, baslangic: datetime):',
    'def kiralama_baslat(self, arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic: datetime):'
)
content = content.replace(
    '(arac_id, kullanici_id, baslangic.strftime("%Y-%m-%d %H:%M:%S"))',
    '(arac_id, kullanici_id, alis_sehri, birakis_sehri, baslangic.strftime("%Y-%m-%d %H:%M:%S"))'
)
content = content.replace(
    'SELECT arac_id, baslangic, aktif FROM kiralamalar WHERE id=?',
    'SELECT arac_id, alis_sehri, birakis_sehri, baslangic, aktif FROM kiralamalar WHERE id=?'
)
content = content.replace(
    'row = cur.fetchone()\n        if not row:\n            conn.close(); return False, "Kiralama bulunamadı."\n        arac_id, bas_str, aktif = row',
    'row = cur.fetchone()\n        if not row:\n            conn.close(); return False, "Kiralama bulunamadı."\n        arac_id, alis_sehri, birakis_sehri, bas_str, aktif = row'
)

k_bitir_logic = '''
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
'''

content = re.sub(r'        cur\.execute\("SELECT km_ucreti FROM araclar WHERE id=\?", \(arac_id,\)\)\n        km_ucreti = cur\.fetchone\(\)\[0\].*?return True, f"✓ Kiralama bitti[^"]+"', k_bitir_logic.strip(), content, flags=re.DOTALL)

with open(backend_path, 'w', encoding='utf-8') as f:
    f.write('''import sqlite3
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
    return 300\n\n''' + content.split('from datetime import datetime\n')[1])
