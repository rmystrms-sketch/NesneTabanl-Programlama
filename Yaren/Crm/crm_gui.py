import sys
import sqlite3
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFrame, QLabel, QTableWidget, 
                             QTableWidgetItem, QPushButton, QStackedWidget,
                             QLineEdit, QMessageBox, QComboBox, QHeaderView,
                             QListWidget, QAbstractItemView, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

# =========================================================================
# VERİTABANI YÖNETİMİ (SQLite PERSISTENT DATA)
# =========================================================================
class VeriDeposu:
    def __init__(self, db_name="crm_veritabani.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.tablolari_olustur()
        self.varsayilan_verileri_yukle()

    def tablolari_olustur(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Musteriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                tel TEXT NOT NULL,
                mail TEXT NOT NULL,
                not_alani TEXT,
                harcama REAL DEFAULT 0
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                alis REAL NOT NULL,
                satis REAL NOT NULL,
                stok INTEGER NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tedarikciler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firma TEXT NOT NULL,
                tel TEXT NOT NULL,
                mail TEXT NOT NULL,
                urunler TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Satislar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_id INTEGER,
                urun_ad TEXT,
                adet INTEGER,
                toplam REAL,
                tarih TEXT,
                FOREIGN KEY (musteri_id) REFERENCES Musteriler(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Destek (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_id INTEGER,
                aciklama TEXT,
                oncelik TEXT,
                durum TEXT,
                cozum TEXT,
                tarih TEXT,
                FOREIGN KEY (musteri_id) REFERENCES Musteriler(id)
            )
        """)
        self.conn.commit()

    def varsayilan_verileri_yukle(self):
        # Eğer tablolar boşsa sahte verileri yükle
        self.cursor.execute("SELECT COUNT(*) FROM Musteriler")
        if self.cursor.fetchone()[0] == 0:
            musteriler = [
                ("Ahmet Yılmaz", "0532 111 22 33", "ahmet@gmail.com", "VIP Müşteri", 0),
                ("Ayşe Demir", "0544 222 33 44", "ayse@gmail.com", "Düzenli müşteri", 0),
                ("Mehmet Kaya", "0555 333 44 55", "mehmet@gmail.com", "Sorunlu", 0),
                ("Elif Şahin", "0533 444 55 66", "elif@gmail.com", "Yeni", 0),
                ("Can Teknoloji", "0532 555 66 77", "can@gmail.com", "Kurumsal", 0),
                ("Zeynep Çelik", "0542 666 77 88", "zeynep@gmail.com", "", 0),
                ("Burak Öz", "0505 777 88 99", "burak@gmail.com", "", 0),
                ("Kemal Sunal", "0532 888 99 00", "kemal@gmail.com", "VIP", 0),
                ("Fatma Gül", "0543 999 00 11", "fatma@gmail.com", "", 0),
                ("Hakan Yılmaz", "0554 000 11 22", "hakan@gmail.com", "", 0)
            ]
            self.cursor.executemany("INSERT INTO Musteriler (ad, tel, mail, not_alani, harcama) VALUES (?, ?, ?, ?, ?)", musteriler)

            urunler = [
                ("Nexora ProBook 16", 25000, 32000, 45),
                ("Vision X Saat", 2000, 3500, 12),
                ("Oyuncu Kulaklığı", 1200, 1800, 80),
                ("Mekanik Klavye", 1500, 2200, 30),
                ("4K Monitör", 8000, 11000, 15),
                ("Ergonomik Mouse", 500, 850, 120),
                ("USB-C Hub", 300, 600, 200),
                ("Laptop Soğutucu", 400, 750, 50),
                ("1TB NVMe SSD", 1800, 2400, 25),
                ("Oyun Konsolu", 15000, 19500, 4)
            ]
            self.cursor.executemany("INSERT INTO Urunler (ad, alis, satis, stok) VALUES (?, ?, ?, ?)", urunler)

            tedarikciler = [
                ("TechSupplies Ltd", "0212 555 44 33", "info@gmail.com", "Nexora ProBook 16, 4K Monitör"),
                ("Aksesuar Dünyası", "0216 444 33 22", "aksesuar@gmail.com", "Oyuncu Kulaklığı, Mekanik Klavye, Ergonomik Mouse"),
                ("DepoTech A.Ş.", "0232 333 22 11", "depo@gmail.com", "1TB NVMe SSD")
            ]
            self.cursor.executemany("INSERT INTO Tedarikciler (firma, tel, mail, urunler) VALUES (?, ?, ?, ?)", tedarikciler)

            satislar = [
                (1, "Nexora ProBook 16", 1, 32000, "15.04.2026"),
                (2, "Vision X Saat", 2, 7000, "16.04.2026"),
                (1, "4K Monitör", 2, 22000, "18.04.2026"),
                (5, "1TB NVMe SSD", 5, 12000, "20.04.2026"),
                (8, "Oyun Konsolu", 1, 19500, "21.04.2026"),
                (3, "Mekanik Klavye", 1, 2200, "22.04.2026")
            ]
            self.cursor.executemany("INSERT INTO Satislar (musteri_id, urun_ad, adet, toplam, tarih) VALUES (?, ?, ?, ?, ?)", satislar)

            destek = [
                (1, "Bilgisayar bazen kapanıyor", "Yüksek", "İşlemde", "Termal macun yenilenecek", "20.04.2026"),
                (3, "Klavye tuşu basmıyor", "Normal", "Açık", "", "22.04.2026"),
                (8, "Konsol disk okumuyor", "Acil", "Açık", "", "23.04.2026"),
                (2, "Saat şarj olmuyor", "Yüksek", "Kapalı (Çözüldü)", "Şarj adaptörü değiştirildi.", "18.04.2026"),
                (5, "SSD hız testi düşük", "Düşük", "Açık", "", "24.04.2026")
            ]
            self.cursor.executemany("INSERT INTO Destek (musteri_id, aciklama, oncelik, durum, cozum, tarih) VALUES (?, ?, ?, ?, ?, ?)", destek)
            
            self.conn.commit()

    def musterileri_getir(self):
        self.cursor.execute("SELECT id, ad, tel, mail, not_alani, harcama FROM Musteriler")
        return self.cursor.fetchall()

    def urunleri_getir(self):
        self.cursor.execute("SELECT id, ad, alis, satis, stok FROM Urunler")
        return self.cursor.fetchall()

    def tedarikcileri_getir(self):
        self.cursor.execute("SELECT id, firma, tel, mail, urunler FROM Tedarikciler")
        return self.cursor.fetchall()

    def satislari_getir(self):
        self.cursor.execute("SELECT id, musteri_id, urun_ad, adet, toplam, tarih FROM Satislar")
        return self.cursor.fetchall()

    def destek_taleplerini_getir(self):
        self.cursor.execute("SELECT id, musteri_id, aciklama, oncelik, durum, cozum, tarih FROM Destek")
        return self.cursor.fetchall()

    def musteri_ekle(self, ad, tel, mail, not_alani):
        self.cursor.execute("INSERT INTO Musteriler (ad, tel, mail, not_alani) VALUES (?, ?, ?, ?)", (ad, tel, mail, not_alani))
        self.conn.commit()

    def urun_ekle(self, ad, alis, satis, stok):
        self.cursor.execute("INSERT INTO Urunler (ad, alis, satis, stok) VALUES (?, ?, ?, ?)", (ad, alis, satis, stok))
        self.conn.commit()

    def tedarikci_ekle(self, firma, tel, mail, urunler):
        self.cursor.execute("INSERT INTO Tedarikciler (firma, tel, mail, urunler) VALUES (?, ?, ?, ?)", (firma, tel, mail, urunler))
        self.conn.commit()

    def satis_ekle(self, musteri_id, urun_ad, adet, toplam, tarih):
        self.cursor.execute("INSERT INTO Satislar (musteri_id, urun_ad, adet, toplam, tarih) VALUES (?, ?, ?, ?, ?)", (musteri_id, urun_ad, adet, toplam, tarih))
        # Stoku düşür
        self.cursor.execute("UPDATE Urunler SET stok = stok - ? WHERE ad = ?", (adet, urun_ad))
        self.conn.commit()

    def destek_talep_ekle(self, musteri_id, aciklama, oncelik, durum, cozum, tarih):
        self.cursor.execute("INSERT INTO Destek (musteri_id, aciklama, oncelik, durum, cozum, tarih) VALUES (?, ?, ?, ?, ?, ?)", (musteri_id, aciklama, oncelik, durum, cozum, tarih))
        self.conn.commit()

    def destek_talep_guncelle(self, id, durum, cozum):
        self.cursor.execute("UPDATE Destek SET durum = ?, cozum = ? WHERE id = ?", (durum, cozum, id))
        self.conn.commit()

    def urun_stok_guncelle(self, id, miktar):
        self.cursor.execute("UPDATE Urunler SET stok = stok + ? WHERE id = ?", (miktar, id))
        self.conn.commit()

    def get_musteri_by_id(self, m_id):
        self.cursor.execute("SELECT id, ad, tel, mail, not_alani, harcama FROM Musteriler WHERE id = ?", (m_id,))
        return self.cursor.fetchone()

    def get_urun_by_id(self, u_id):
        self.cursor.execute("SELECT id, ad, alis, satis, stok FROM Urunler WHERE id = ?", (u_id,))
        return self.cursor.fetchone()

    def get_urun_by_ad(self, ad):
        self.cursor.execute("SELECT id, ad, alis, satis, stok FROM Urunler WHERE ad = ?", (ad,))
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()

# ORTAK TELEFON FORMATLAYICI
def telefon_formatla_ortak(text):
    text = "".join(filter(str.isdigit, text))[:11] # Sadece rakam ve max 11 hane
    formatted = ""
    for i, char in enumerate(text):
        if i == 4 or i == 7 or i == 9: formatted += " "
        formatted += char
    return formatted

# =========================================================================
# 1. SINIF: DASHBOARD (KLASİK CRM RAPORLAMA)
# =========================================================================
class DashboardSayfasi(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("background-color: #0b0e14;")
        self.ana_duzen = QVBoxLayout(self)
        self.ana_duzen.setContentsMargins(25, 20, 25, 20)
        self.ana_duzen.setSpacing(20)
        self.arayuz_kur()

    def arayuz_kur(self):
        ust_bar_duzeni = QHBoxLayout()
        baslik_etiketi = QLabel("📊 CRM RAPORLAMA PANELİ")
        baslik_etiketi.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold; border: none;")
        ust_bar_duzeni.addWidget(baslik_etiketi)
        ust_bar_duzeni.addStretch()
        self.ana_duzen.addLayout(ust_bar_duzeni)

        self.kpi_duzeni = QHBoxLayout()
        self.ana_duzen.addLayout(self.kpi_duzeni)

        orta_layout = QHBoxLayout()
        orta_layout.setSpacing(20)
        
        # Son Satışlar Tablosu
        satis_paneli = self.kutu_olustur("🛒 Son Yapılan Satışlar")
        self.tablo_satis = QTableWidget(0, 3)
        self.tablo_satis.setHorizontalHeaderLabels(["Müşteri", "Ürün", "Tutar"])
        self.tablo_satis.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_satis.verticalHeader().setVisible(False)
        self.tablo_satis.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 13px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 10px; }
            QHeaderView::section { background-color: #161923; color: #3498db; font-weight: bold; border: none; border-bottom: 2px solid #3498db; }
        """)
        satis_paneli.layout().addWidget(self.tablo_satis)
        
        # En Çok Kazandıran Müşteriler
        musteri_paneli = self.kutu_olustur("💎 En Çok Kazandıran Müşteriler")
        self.tablo_musteri = QTableWidget(0, 2)
        self.tablo_musteri.setHorizontalHeaderLabels(["Müşteri", "Toplam Harcama"])
        self.tablo_musteri.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_musteri.verticalHeader().setVisible(False)
        self.tablo_musteri.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 13px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 10px; }
            QHeaderView::section { background-color: #161923; color: #f39c12; font-weight: bold; border: none; border-bottom: 2px solid #f39c12; }
        """)
        musteri_paneli.layout().addWidget(self.tablo_musteri)

        orta_layout.addWidget(satis_paneli)
        orta_layout.addWidget(musteri_paneli)
        self.ana_duzen.addLayout(orta_layout, 2)

        # Alt Layout (Destek)
        alt_layout = QHBoxLayout()
        destek_paneli = self.kutu_olustur("⚠️ Acil ve Açık Destek Talepleri")
        self.tablo_destek = QTableWidget(0, 3)
        self.tablo_destek.setHorizontalHeaderLabels(["Müşteri", "Açıklama", "Durum"])
        self.tablo_destek.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_destek.verticalHeader().setVisible(False)
        self.tablo_destek.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 13px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 10px; }
            QHeaderView::section { background-color: #161923; color: #e74c3c; font-weight: bold; border: none; border-bottom: 2px solid #e74c3c; }
        """)
        destek_paneli.layout().addWidget(self.tablo_destek)
        alt_layout.addWidget(destek_paneli)
        
        self.ana_duzen.addLayout(alt_layout, 1)
        self.verileri_guncelle()

    def kutu_olustur(self, baslik_metni):
        p = QFrame()
        p.setStyleSheet("background-color: #161923; border-radius: 15px; border: 1px solid #1f222d;")
        d = QVBoxLayout(p)
        b = QLabel(baslik_metni)
        b.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none; padding-bottom: 5px;")
        d.addWidget(b)
        return p

    def verileri_guncelle(self):
        while self.kpi_duzeni.count():
            item = self.kpi_duzeni.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        musteriler = self.db.musterileri_getir()
        urunler = self.db.urunleri_getir()
        satislar = self.db.satislari_getir()
        destek_talepleri = self.db.destek_taleplerini_getir()

        m_sayisi = len(musteriler)
        s_sayisi = len(satislar)
        u_sayisi = len(urunler)
        ciro = sum(s[4] for s in satislar)
        d_sayisi = len([d for d in destek_talepleri if d[4] != "Kapalı (Çözüldü)"])

        self.kpi_kart_ekle(self.kpi_duzeni, "Toplam Müşteri", str(m_sayisi), "👥", "#3498db")
        self.kpi_kart_ekle(self.kpi_duzeni, "Toplam Satış", str(s_sayisi), "🛒", "#9b59b6")
        self.kpi_kart_ekle(self.kpi_duzeni, "Toplam Ciro", f"₺{ciro:,}", "💰", "#2ecc71")
        self.kpi_kart_ekle(self.kpi_duzeni, "Açık Talepler", str(d_sayisi), "🎫", "#e74c3c")

        # Satış Tablosu Güncelle (Son 5 Satış)
        self.tablo_satis.setRowCount(0)
        for s in list(reversed(satislar))[:5]:
            r = self.tablo_satis.rowCount()
            self.tablo_satis.insertRow(r)
            m = self.db.get_musteri_by_id(s[1])
            self.tablo_satis.setItem(r, 0, QTableWidgetItem(m[1] if m else "-"))
            self.tablo_satis.setItem(r, 1, QTableWidgetItem(s[2]))
            self.tablo_satis.setItem(r, 2, QTableWidgetItem(f"₺{s[4]:,}"))

        # Müşteri Tablosu (En çok harcayan ilk 5)
        self.tablo_musteri.setRowCount(0)
        m_harcamalar = {}
        for s in satislar:
            m_harcamalar[s[1]] = m_harcamalar.get(s[1], 0) + s[4]
        
        sirali_musteriler = sorted(m_harcamalar.items(), key=lambda x: x[1], reverse=True)[:5]
        for mid, toplam in sirali_musteriler:
            r = self.tablo_musteri.rowCount()
            self.tablo_musteri.insertRow(r)
            m = self.db.get_musteri_by_id(mid)
            self.tablo_musteri.setItem(r, 0, QTableWidgetItem(m[1] if m else "-"))
            self.tablo_musteri.setItem(r, 1, QTableWidgetItem(f"₺{toplam:,}"))

        # Destek Tablosu (Acil veya Açık olanlar)
        self.tablo_destek.setRowCount(0)
        for d in destek_talepleri:
            if d[4] != "Kapalı (Çözüldü)":
                r = self.tablo_destek.rowCount()
                self.tablo_destek.insertRow(r)
                m = self.db.get_musteri_by_id(d[1])
                self.tablo_destek.setItem(r, 0, QTableWidgetItem(m[1] if m else "-"))
                self.tablo_destek.setItem(r, 1, QTableWidgetItem(f"[{d[3]}] {d[2]}"))
                
                durum_it = QTableWidgetItem(d[4])
                durum_it.setForeground(QColor("#e74c3c" if d[4]=="Açık" else "#f39c12"))
                self.tablo_destek.setItem(r, 2, durum_it)

    def kpi_kart_ekle(self, duzen, baslik, deger, ikon, renk):
        kart = QFrame()
        kart.setStyleSheet(f"background-color: #161923; border-radius: 12px; border: 1px solid #1f222d;")
        kart_duzeni = QVBoxLayout(kart)
        ust_satir = QHBoxLayout()
        b_lbl = QLabel(baslik); b_lbl.setStyleSheet("color: #8b8e98; font-size: 13px; border: none; font-weight: bold;")
        i_lbl = QLabel(ikon); i_lbl.setStyleSheet(f"color: {renk}; font-size: 18px; border: none;")
        ust_satir.addWidget(b_lbl); ust_satir.addWidget(i_lbl)
        d_lbl = QLabel(deger); d_lbl.setStyleSheet(f"color: #ffffff; font-size: 22px; font-weight: bold; border: none; padding-top: 5px;")
        kart_duzeni.addLayout(ust_satir); kart_duzeni.addWidget(d_lbl)
        duzen.addWidget(kart)


# =========================================================================
# 2. SINIF: MÜŞTERİ YÖNETİMİ
# =========================================================================
class MusteriKayitSayfasi(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("""
            QMessageBox { background-color: #161923; border: 1px solid #00d2ff; }
            QMessageBox QLabel { color: white; font-size: 14px; min-width: 250px; padding: 10px; } 
            QMessageBox QPushButton { background-color: #00d2ff; color: #0b0e14; font-weight: bold; padding: 6px 15px; border-radius: 5px; }
        """) 
        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(25, 25, 25, 25)
        self.arayuz_kur()

    def arayuz_kur(self):
        ust_bar = QHBoxLayout()
        baslik = QLabel("👥 MÜŞTERİ YÖNETİMİ"); baslik.setStyleSheet("color: white; font-size: 22px; font-weight: 800; letter-spacing: 2px;")
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("🔍 Müşteri ara...")
        self.arama_input.setFixedWidth(380)
        self.arama_input.setStyleSheet("background-color: #161923; color: white; border-radius: 12px; padding: 12px; border: 1px solid #1f222d;")
        self.arama_input.textChanged.connect(self.tablo_filtrele)
        ust_bar.addWidget(baslik); ust_bar.addStretch(); ust_bar.addWidget(self.arama_input)
        self.ana_layout.addLayout(ust_bar)

        govde_layout = QHBoxLayout()
        
        self.sol_panel = QFrame()
        self.sol_panel.setFixedWidth(300)
        self.sol_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #00d2ff;")
        sol_duzen = QVBoxLayout(self.sol_panel)
        sol_duzen.setContentsMargins(20, 20, 20, 20)
        f_baslik = QLabel("MÜŞTERİ EKLE"); f_baslik.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 14px; border: none; margin-bottom: 10px;"); sol_duzen.addWidget(f_baslik)
        
        self.inp_ad = self.form_elemani(sol_duzen, "Ad / Şirket")
        self.inp_tel = self.form_elemani(sol_duzen, "Telefon")
        self.inp_tel.textChanged.connect(lambda: self.inp_tel.setText(telefon_formatla_ortak(self.inp_tel.text())))
        self.inp_mail = self.form_elemani(sol_duzen, "E-posta (@gmail.com)")
        self.inp_not = self.form_elemani(sol_duzen, "Not")
        
        btn_ekle = QPushButton("💾 Müşteriyi Kaydet")
        btn_ekle.setStyleSheet("background-color: #00d2ff; color: #0b0e14; font-weight: bold; padding: 12px; border-radius: 10px; border: none; margin-top:10px;")
        btn_ekle.clicked.connect(self.musteri_ekle)
        sol_duzen.addWidget(btn_ekle); sol_duzen.addStretch()

        self.tablo = QTableWidget(0, 5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ad / Şirket", "Telefon", "E-posta", "Not"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.verticalHeader().setVisible(False) 
        self.tablo.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 13px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 15px; }
            QHeaderView::section { background-color: #161923; color: #00d2ff; font-weight: bold; border: none; border-bottom: 2px solid #00d2ff; height: 50px; }
            QTableWidget::item:selected { background-color: #1f222d; color: #00d2ff; }
        """)
        self.tablo.itemSelectionChanged.connect(self.satir_secildi)

        self.sag_panel = QFrame()
        self.sag_panel.setFixedWidth(320)
        self.sag_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #00d2ff;")
        self.sag_duzen = QVBoxLayout(self.sag_panel)
        self.sag_duzen.setContentsMargins(20, 20, 20, 20)
        
        d_baslik = QLabel("MÜŞTERİ DETAYI"); d_baslik.setStyleSheet("color: #00d2ff; font-weight: bold; font-size: 14px; border: none;"); self.sag_duzen.addWidget(d_baslik)
        self.lbl_ad = QLabel("Seçim Bekleniyor..."); self.lbl_ad.setStyleSheet("color: white; font-size: 16px; font-weight: bold; border: none; margin-top: 10px;")
        self.lbl_iletisim = QLabel("-"); self.lbl_iletisim.setStyleSheet("color: #adb0bb; font-size: 12px; border: none;")
        self.lbl_not = QLabel("-"); self.lbl_not.setStyleSheet("color: #f39c12; font-size: 12px; border: none; font-style: italic;")
        self.lbl_harcama = QLabel("Toplam Alışveriş: ₺0"); self.lbl_harcama.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px; border: none; margin-top: 10px;")
        
        self.sag_duzen.addWidget(self.lbl_ad); self.sag_duzen.addWidget(self.lbl_iletisim); self.sag_duzen.addWidget(self.lbl_not); self.sag_duzen.addWidget(self.lbl_harcama)
        self.sag_duzen.addSpacing(10)
        
        self.sag_duzen.addWidget(self.baslik_uret("🛒 Satış Geçmişi"))
        self.liste_satis = QListWidget()
        self.liste_satis.setStyleSheet("background-color: #0b0e14; color: #adb0bb; border-radius: 10px; border: 1px solid #1f222d;")
        self.sag_duzen.addWidget(self.liste_satis)

        self.sag_duzen.addWidget(self.baslik_uret("🎫 Destek Geçmişi"))
        self.liste_destek = QListWidget()
        self.liste_destek.setStyleSheet("background-color: #0b0e14; color: #adb0bb; border-radius: 10px; border: 1px solid #1f222d;")
        self.sag_duzen.addWidget(self.liste_destek)

        govde_layout.addWidget(self.sol_panel); govde_layout.addWidget(self.tablo); govde_layout.addWidget(self.sag_panel)
        self.ana_layout.addLayout(govde_layout)

    def baslik_uret(self, metin):
        lbl = QLabel(metin); lbl.setStyleSheet("color: #8b8e98; font-size: 12px; font-weight: bold; border: none; margin-top: 5px;"); return lbl

    def form_elemani(self, layout, etiket):
        lbl = QLabel(etiket); lbl.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); layout.addWidget(lbl)
        inp = QLineEdit(); inp.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        layout.addWidget(inp)
        return inp

    def musteri_ekle(self):
        ad = self.inp_ad.text(); tel = self.inp_tel.text(); mail = self.inp_mail.text(); notu = self.inp_not.text()
        if not ad or not tel:
            QMessageBox.warning(self, "Hata", "Ad ve Telefon zorunludur!")
            return
        if not mail.endswith("@gmail.com"):
            QMessageBox.warning(self, "Hata", "E-posta adresi sadece @gmail.com ile bitmelidir!")
            return
            
        self.db.musteri_ekle(ad, tel, mail, notu)
        self.verileri_guncelle()
        QMessageBox.information(self, "Başarılı", "Müşteri eklendi!")
        self.inp_ad.clear(); self.inp_tel.clear(); self.inp_mail.clear(); self.inp_not.clear()

    def verileri_guncelle(self):
        self.tablo.setRowCount(0)
        musteriler = self.db.musterileri_getir()
        for m in musteriler:
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)
            self.tablo.setItem(row, 0, QTableWidgetItem(str(m[0])))
            self.tablo.setItem(row, 1, QTableWidgetItem(m[1]))
            self.tablo.setItem(row, 2, QTableWidgetItem(m[2]))
            self.tablo.setItem(row, 3, QTableWidgetItem(m[3]))
            self.tablo.setItem(row, 4, QTableWidgetItem(m[4]))
            
    def satir_secildi(self):
        row = self.tablo.currentRow()
        if row >= 0:
            m_id = self.tablo.item(row, 0).text()
            m = self.db.get_musteri_by_id(m_id)
            if not m: return
            self.lbl_ad.setText(m[1])
            self.lbl_iletisim.setText(f"{m[2]} | {m[3]}")
            self.lbl_not.setText(f"Not: {m[4]}")
            
            satislar = self.db.satislari_getir()
            toplam = sum(s[4] for s in satislar if str(s[1]) == str(m_id))
            self.lbl_harcama.setText(f"Toplam Alışveriş: ₺{toplam:,}")
            
            self.liste_satis.clear()
            for s in satislar:
                if str(s[1]) == str(m_id):
                    self.liste_satis.addItem(f"{s[5]} - {s[2]} ({s[3]}x)")
                    
            destek = self.db.destek_taleplerini_getir()
            self.liste_destek.clear()
            for d in destek:
                if str(d[1]) == str(m_id):
                    self.liste_destek.addItem(f"[{d[4]}] {d[2]}")

    def tablo_filtrele(self):
        txt = self.arama_input.text().lower()
        for i in range(self.tablo.rowCount()):
            gizle = True
            for j in range(self.tablo.columnCount()):
                if txt in self.tablo.item(i, j).text().lower(): gizle = False; break
            self.tablo.setRowHidden(i, gizle)


# =========================================================================
# 3. SINIF: ÜRÜN & STOK YÖNETİMİ
# =========================================================================
class UrunStokSayfasi(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("""
            QMessageBox { background-color: #161923; border: 1px solid #f39c12; }
            QMessageBox QLabel { color: white; font-size: 14px; min-width: 250px; padding: 10px; } 
            QMessageBox QPushButton { background-color: #f39c12; color: #0b0e14; font-weight: bold; padding: 6px 15px; border-radius: 5px; }
        """)
        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(25, 25, 25, 25)
        self.arayuz_kur()

    def arayuz_kur(self):
        ust_bar = QHBoxLayout()
        baslik = QLabel("📦 ÜRÜN & STOK YÖNETİMİ"); baslik.setStyleSheet("color: white; font-size: 22px; font-weight: 800; letter-spacing: 2px;")
        ust_bar.addWidget(baslik); ust_bar.addStretch()
        self.ana_layout.addLayout(ust_bar)

        govde_layout = QHBoxLayout()

        self.sol_panel = QFrame()
        self.sol_panel.setFixedWidth(300)
        self.sol_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #f39c12;")
        sol_duzen = QVBoxLayout(self.sol_panel)
        sol_duzen.setContentsMargins(20, 20, 20, 20)
        f_baslik = QLabel("YENİ ÜRÜN EKLE"); f_baslik.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 14px; border: none; margin-bottom: 10px;"); sol_duzen.addWidget(f_baslik)
        
        self.inp_ad = self.form_elemani(sol_duzen, "Ürün Adı")
        self.inp_alis = self.form_elemani(sol_duzen, "Alış Fiyatı (₺)")
        self.inp_satis = self.form_elemani(sol_duzen, "Satış Fiyatı (₺)")
        self.inp_stok = self.form_elemani(sol_duzen, "Başlangıç Stoğu")
        
        btn_ekle = QPushButton("➕ Ürünü Ekle")
        btn_ekle.setStyleSheet("background-color: #f39c12; color: #0b0e14; font-weight: bold; padding: 12px; border-radius: 10px; border: none; margin-top:10px;")
        btn_ekle.clicked.connect(self.urun_ekle)
        sol_duzen.addWidget(btn_ekle); sol_duzen.addStretch()

        self.tablo = QTableWidget(0, 6)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ürün Adı", "Alış", "Satış", "Stok", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 13px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 15px; }
            QHeaderView::section { background-color: #161923; color: #f39c12; font-weight: bold; border: none; border-bottom: 2px solid #f39c12; height: 50px; }
            QTableWidget::item:selected { background-color: #1f222d; color: #f39c12; }
        """)
        self.tablo.itemSelectionChanged.connect(self.satir_secildi)

        self.sag_panel = QFrame()
        self.sag_panel.setFixedWidth(300)
        self.sag_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #f39c12;")
        sag_duzen = QVBoxLayout(self.sag_panel)
        sag_duzen.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_id = QLabel(""); self.lbl_id.hide()
        self.lbl_ad = QLabel("Ürün Seçilmedi"); self.lbl_ad.setStyleSheet("color: white; font-size: 18px; font-weight: bold; border: none;")
        self.lbl_stok = QLabel("Stok: -"); self.lbl_stok.setStyleSheet("color: #adb0bb; font-size: 14px; border: none; margin-top: 5px;")
        sag_duzen.addWidget(self.lbl_ad); sag_duzen.addWidget(self.lbl_stok); sag_duzen.addSpacing(20)

        stok_islem_lbl = QLabel("STOK İŞLEMLERİ"); stok_islem_lbl.setStyleSheet("color: #f39c12; font-weight: bold; border: none;"); sag_duzen.addWidget(stok_islem_lbl)

        lbl_t = QLabel("Tedarikçi (Opsiyonel)"); lbl_t.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sag_duzen.addWidget(lbl_t)
        self.combo_tedarikci = QComboBox()
        self.combo_tedarikci.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        sag_duzen.addWidget(self.combo_tedarikci)

        self.inp_stok_islem = QLineEdit(); self.inp_stok_islem.setPlaceholderText("Adet girin...")
        self.inp_stok_islem.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d; margin-top: 5px;")
        sag_duzen.addWidget(self.inp_stok_islem)

        btn_stok_ekle = QPushButton("🟢 Stok Ekle")
        btn_stok_ekle.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px; border-radius: 8px; border: none; margin-top:5px;")
        btn_stok_ekle.clicked.connect(lambda: self.stok_islem(1))
        
        btn_stok_azalt = QPushButton("🔴 Stok Azalt")
        btn_stok_azalt.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px; border-radius: 8px; border: none; margin-top:5px;")
        btn_stok_azalt.clicked.connect(lambda: self.stok_islem(-1))

        sag_duzen.addWidget(btn_stok_ekle); sag_duzen.addWidget(btn_stok_azalt); sag_duzen.addStretch()

        govde_layout.addWidget(self.sol_panel); govde_layout.addWidget(self.tablo); govde_layout.addWidget(self.sag_panel)
        self.ana_layout.addLayout(govde_layout)

    def form_elemani(self, layout, etiket):
        lbl = QLabel(etiket); lbl.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); layout.addWidget(lbl)
        inp = QLineEdit(); inp.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        layout.addWidget(inp)
        return inp

    def verileri_guncelle(self):
        self.tablo.setRowCount(0)
        urunler = self.db.urunleri_getir()
        for u in urunler:
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)
            self.tablo.setItem(row, 0, QTableWidgetItem(str(u[0])))
            self.tablo.setItem(row, 1, QTableWidgetItem(u[1]))
            self.tablo.setItem(row, 2, QTableWidgetItem(f"₺{u[2]}"))
            self.tablo.setItem(row, 3, QTableWidgetItem(f"₺{u[3]}"))
            self.tablo.setItem(row, 4, QTableWidgetItem(str(u[4])))
            self.durum_yaz(row, u[4])
            
        self.combo_tedarikci.clear()
        self.combo_tedarikci.addItem("Seçiniz...")
        tedarikciler = self.db.tedarikcileri_getir()
        for t in tedarikciler:
            self.combo_tedarikci.addItem(t[1])

    def durum_yaz(self, row, stok):
        it = QTableWidgetItem()
        it.setForeground(QColor("white")); it.setTextAlignment(Qt.AlignCenter)
        if stok > 30: it.setText("İyi"); it.setBackground(QColor("#2ecc71"))
        elif stok > 5: it.setText("Kritik"); it.setBackground(QColor("#f39c12"))
        else: it.setText("Tükendi"); it.setBackground(QColor("#e74c3c"))
        self.tablo.setItem(row, 5, it)

    def urun_ekle(self):
        ad = self.inp_ad.text(); alis = self.inp_alis.text(); satis = self.inp_satis.text(); stok = self.inp_stok.text()
        if not (ad and alis and satis and stok) or not stok.isdigit() or not alis.replace('.', '', 1).isdigit() or not satis.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Hata", "Tüm alanları geçerli sayısal değerlerle doldurun!")
            return
        
        self.db.urun_ekle(ad, float(alis), float(satis), int(stok))
        self.verileri_guncelle()
        QMessageBox.information(self, "Başarılı", "Ürün başarıyla eklendi!")
        self.inp_ad.clear(); self.inp_alis.clear(); self.inp_satis.clear(); self.inp_stok.clear()

    def satir_secildi(self):
        row = self.tablo.currentRow()
        if row >= 0:
            u_id = self.tablo.item(row, 0).text()
            u = self.db.get_urun_by_id(u_id)
            if u:
                self.lbl_id.setText(str(u[0]))
                self.lbl_ad.setText(u[1])
                self.lbl_stok.setText(f"Mevcut Stok: {u[4]} Adet")

    def stok_islem(self, carpan):
        u_id = self.lbl_id.text()
        if not u_id:
            QMessageBox.warning(self, "Hata", "Lütfen listeden bir ürün seçin!")
            return
            
        u = self.db.get_urun_by_id(u_id)
        if not u: return
        
        miktar_str = self.inp_stok_islem.text()
        if not miktar_str.isdigit():
            QMessageBox.warning(self, "Hata", "Geçerli bir adet girin!")
            return
            
        miktar = int(miktar_str) * carpan
        if u[4] + miktar < 0:
            QMessageBox.warning(self, "Hata", "Stok 0'ın altına düşemez!")
            return
            
        self.db.urun_stok_guncelle(u_id, miktar)
        self.verileri_guncelle()
        
        # Tedarikçi seçildiyse (Opsiyonel mantık - SQLite tarafında karmaşık olabilir, şimdilik basit tutalım)
        
        self.inp_stok_islem.clear()
        QMessageBox.information(self, "Başarılı", "Stok güncellendi!")


# =========================================================================
# 4. SINIF: TEDARİKÇİ YÖNETİMİ
# =========================================================================
class TedarikciSayfasi(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("""
            QMessageBox { background-color: #161923; border: 1px solid #9b59b6; }
            QMessageBox QLabel { color: white; font-size: 14px; min-width: 250px; padding: 10px; } 
            QMessageBox QPushButton { background-color: #9b59b6; color: white; font-weight: bold; padding: 6px 15px; border-radius: 5px; }
        """)
        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(25, 25, 25, 25)
        self.arayuz_kur()

    def arayuz_kur(self):
        ust_bar = QHBoxLayout()
        baslik = QLabel("🏭 TEDARİKÇİ YÖNETİMİ"); baslik.setStyleSheet("color: white; font-size: 22px; font-weight: 800; letter-spacing: 2px;")
        ust_bar.addWidget(baslik); ust_bar.addStretch()
        self.ana_layout.addLayout(ust_bar)

        govde_layout = QHBoxLayout()

        self.sol_panel = QFrame()
        self.sol_panel.setFixedWidth(320)
        self.sol_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #9b59b6;")
        sol_duzen = QVBoxLayout(self.sol_panel)
        sol_duzen.setContentsMargins(20, 20, 20, 20)
        
        f_baslik = QLabel("YENİ TEDARİKÇİ EKLE"); f_baslik.setStyleSheet("color: #9b59b6; font-weight: bold; font-size: 14px; border: none; margin-bottom: 10px;")
        sol_duzen.addWidget(f_baslik)
        
        self.inp_firma = self.form_elemani(sol_duzen, "Firma Adı")
        self.inp_tel = self.form_elemani(sol_duzen, "Telefon")
        self.inp_tel.textChanged.connect(lambda: self.inp_tel.setText(telefon_formatla_ortak(self.inp_tel.text())))
        self.inp_mail = self.form_elemani(sol_duzen, "E-posta (@gmail.com)")
        
        lbl_u = QLabel("Sağladığı Ürünler (Çoklu Seçim)"); lbl_u.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;")
        sol_duzen.addWidget(lbl_u)
        
        self.list_urunler = QListWidget()
        self.list_urunler.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_urunler.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        sol_duzen.addWidget(self.list_urunler)
        
        btn_ekle = QPushButton("💾 Tedarikçi Kaydet")
        btn_ekle.setStyleSheet("background-color: #9b59b6; color: white; font-weight: bold; padding: 12px; border-radius: 10px; border: none; margin-top:10px;")
        btn_ekle.clicked.connect(self.tedarikci_ekle)
        sol_duzen.addWidget(btn_ekle)

        self.tablo = QTableWidget(0, 5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Firma Adı", "Telefon", "E-posta", "Sağladığı Ürünler"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 13px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 15px; }
            QHeaderView::section { background-color: #161923; color: #9b59b6; font-weight: bold; border: none; border-bottom: 2px solid #9b59b6; height: 50px; }
            QTableWidget::item:selected { background-color: #1f222d; color: #9b59b6; }
        """)

        govde_layout.addWidget(self.sol_panel); govde_layout.addWidget(self.tablo)
        self.ana_layout.addLayout(govde_layout)

    def form_elemani(self, layout, etiket):
        lbl = QLabel(etiket); lbl.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); layout.addWidget(lbl)
        inp = QLineEdit(); inp.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        layout.addWidget(inp)
        return inp

    def verileri_guncelle(self):
        self.list_urunler.clear()
        urunler = self.db.urunleri_getir()
        for u in urunler:
            self.list_urunler.addItem(u[1])
            
        self.tablo.setRowCount(0)
        tedarikciler = self.db.tedarikcileri_getir()
        for t in tedarikciler:
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)
            self.tablo.setItem(row, 0, QTableWidgetItem(str(t[0])))
            self.tablo.setItem(row, 1, QTableWidgetItem(t[1]))
            self.tablo.setItem(row, 2, QTableWidgetItem(t[2]))
            self.tablo.setItem(row, 3, QTableWidgetItem(t[3]))
            self.tablo.setItem(row, 4, QTableWidgetItem(t[4]))

    def tedarikci_ekle(self):
        firma = self.inp_firma.text(); tel = self.inp_tel.text(); mail = self.inp_mail.text()
        secilenler = [item.text() for item in self.list_urunler.selectedItems()]
        
        if not firma or not tel:
            QMessageBox.warning(self, "Hata", "Firma ve Telefon zorunludur!")
            return
        if not mail.endswith("@gmail.com"):
            QMessageBox.warning(self, "Hata", "E-posta adresi sadece @gmail.com ile bitmelidir!")
            return
            
        self.db.tedarikci_ekle(firma, tel, mail, ", ".join(secilenler))
        self.verileri_guncelle()
        QMessageBox.information(self, "Başarılı", "Tedarikçi başarıyla eklendi!")
        self.inp_firma.clear(); self.inp_tel.clear(); self.inp_mail.clear(); self.list_urunler.clearSelection()


# =========================================================================
# 5. SINIF: SATIŞ YÖNETİMİ
# =========================================================================
class SatisSayfasi(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("""
            QMessageBox { background-color: #161923; border: 1px solid #2ecc71; }
            QMessageBox QLabel { color: white; font-size: 14px; min-width: 250px; padding: 10px; } 
            QMessageBox QPushButton { background-color: #2ecc71; color: #0b0e14; font-weight: bold; padding: 6px 15px; border-radius: 5px; }
        """)
        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(25, 25, 25, 25)
        self.arayuz_kur()

    def arayuz_kur(self):
        ust_bar = QHBoxLayout()
        baslik = QLabel("🛒 SATIŞ YÖNETİMİ"); baslik.setStyleSheet("color: white; font-size: 22px; font-weight: 800; letter-spacing: 2px;")
        ust_bar.addWidget(baslik); ust_bar.addStretch()
        self.ana_layout.addLayout(ust_bar)

        govde_layout = QHBoxLayout()

        self.sol_panel = QFrame()
        self.sol_panel.setFixedWidth(320)
        self.sol_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #2ecc71;")
        sol_duzen = QVBoxLayout(self.sol_panel)
        sol_duzen.setContentsMargins(20, 20, 20, 20)
        
        f_baslik = QLabel("YENİ SATIŞ İŞLEMİ"); f_baslik.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px; border: none; margin-bottom: 10px;")
        sol_duzen.addWidget(f_baslik)
        
        lbl_m = QLabel("Müşteri Seç"); lbl_m.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sol_duzen.addWidget(lbl_m)
        self.combo_musteri = QComboBox()
        self.combo_musteri.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        sol_duzen.addWidget(self.combo_musteri)

        u_row = QHBoxLayout()
        lbl_u = QLabel("Ürün Seç"); lbl_u.setStyleSheet("color: #565b6e; font-size: 11px; border: none;")
        self.lbl_stok_gosterge = QLabel("(Stok: -)"); self.lbl_stok_gosterge.setStyleSheet("color: #f39c12; font-size: 11px; font-weight:bold; border: none;")
        u_row.addWidget(lbl_u); u_row.addStretch(); u_row.addWidget(self.lbl_stok_gosterge)
        sol_duzen.addLayout(u_row)
        
        self.combo_urun = QComboBox()
        self.combo_urun.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        self.combo_urun.currentIndexChanged.connect(self.hesapla)
        sol_duzen.addWidget(self.combo_urun)

        lbl_a = QLabel("Adet"); lbl_a.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sol_duzen.addWidget(lbl_a)
        self.inp_adet = QLineEdit("1")
        self.inp_adet.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        self.inp_adet.textChanged.connect(self.hesapla)
        sol_duzen.addWidget(self.inp_adet)

        self.lbl_toplam = QLabel("Toplam: ₺0")
        self.lbl_toplam.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 18px; border: none; margin-top: 15px;")
        sol_duzen.addWidget(self.lbl_toplam)

        btn_ekle = QPushButton("💰 Satışı Tamamla")
        btn_ekle.setStyleSheet("background-color: #2ecc71; color: #0b0e14; font-weight: bold; padding: 12px; border-radius: 10px; border: none; margin-top:10px;")
        btn_ekle.clicked.connect(self.satis_yap)
        sol_duzen.addWidget(btn_ekle); sol_duzen.addStretch()

        self.tablo = QTableWidget(0, 5)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Müşteri", "Ürün", "Adet", "Toplam Fiyat"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 13px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 15px; }
            QHeaderView::section { background-color: #161923; color: #2ecc71; font-weight: bold; border: none; border-bottom: 2px solid #2ecc71; height: 50px; }
            QTableWidget::item:selected { background-color: #1f222d; color: #2ecc71; }
        """)

        govde_layout.addWidget(self.sol_panel); govde_layout.addWidget(self.tablo)
        self.ana_layout.addLayout(govde_layout)

    def verileri_guncelle(self):
        self.combo_musteri.clear()
        musteriler = self.db.musterileri_getir()
        for m in musteriler:
            self.combo_musteri.addItem(m[1], m[0])
            
        self.combo_urun.blockSignals(True)
        self.combo_urun.clear()
        urunler = self.db.urunleri_getir()
        for u in urunler:
            self.combo_urun.addItem(u[1], u[0])
        self.combo_urun.blockSignals(False)
        
        self.hesapla()
        
        self.tablo.setRowCount(0)
        satislar = self.db.satislari_getir()
        for s in reversed(satislar):
            row = self.tablo.rowCount()
            self.tablo.insertRow(row)
            m = self.db.get_musteri_by_id(s[1])
            m_ad = m[1] if m else "Bilinmiyor"
            
            self.tablo.setItem(row, 0, QTableWidgetItem(s[5]))
            self.tablo.setItem(row, 1, QTableWidgetItem(m_ad))
            self.tablo.setItem(row, 2, QTableWidgetItem(s[2]))
            self.tablo.setItem(row, 3, QTableWidgetItem(str(s[3])))
            
            it = QTableWidgetItem(f"₺{s[4]}")
            it.setForeground(QColor("#2ecc71"))
            self.tablo.setItem(row, 4, it)

    def hesapla(self):
        if self.combo_urun.count() == 0: return
        u_id = self.combo_urun.currentData()
        u = self.db.get_urun_by_id(u_id)
        adet_str = self.inp_adet.text()
        
        if u:
            self.lbl_stok_gosterge.setText(f"(Stok: {u[4]} adet)")
            if u[4] == 0: self.lbl_stok_gosterge.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight:bold; border: none;")
            else: self.lbl_stok_gosterge.setStyleSheet("color: #f39c12; font-size: 11px; font-weight:bold; border: none;")
        
        if not u or not adet_str.isdigit() or int(adet_str) <= 0:
            self.lbl_toplam.setText("Toplam: ₺0")
            return
            
        toplam = u[3] * int(adet_str)
        self.lbl_toplam.setText(f"Toplam: ₺{toplam:,}")

    def satis_yap(self):
        if self.combo_musteri.count() == 0 or self.combo_urun.count() == 0:
            QMessageBox.warning(self, "Hata", "Müşteri ve Ürün seçmelisiniz!")
            return
            
        m_id = self.combo_musteri.currentData()
        u_id = self.combo_urun.currentData()
        u = self.db.get_urun_by_id(u_id)
        adet_str = self.inp_adet.text()
        
        if not u or not adet_str.isdigit() or int(adet_str) <= 0:
            QMessageBox.warning(self, "Hata", "Geçerli bir adet girin!")
            return
            
        adet = int(adet_str)
        if u[4] < adet:
            QMessageBox.critical(self, "Stok Yetersiz", f"İşlem Engellendi!\nStokta sadece {u[4]} adet {u[1]} bulunuyor.")
            return
            
        toplam = u[3] * adet
        tarih = QDate.currentDate().toString('dd.MM.yyyy')
        
        self.db.satis_ekle(m_id, u[1], adet, toplam, tarih)
        self.verileri_guncelle()
        QMessageBox.information(self, "Başarılı", f"Satış başarıyla kaydedildi!\nÜrün stoğu {adet} adet düşüldü.")
        self.inp_adet.setText("1")


# =========================================================================
# 6. SINIF: DESTEK TALEPLERİ
# =========================================================================
class DestekSayfasi(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setStyleSheet("""
            QMessageBox { background-color: #161923; border: 1px solid #e74c3c; }
            QMessageBox QLabel { color: white; font-size: 14px; min-width: 250px; padding: 10px; } 
            QMessageBox QPushButton { background-color: #e74c3c; color: white; font-weight: bold; padding: 6px 15px; border-radius: 5px; }
        """)
        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(25, 20, 25, 20)
        self.arayuz_kur()

    def arayuz_kur(self):
        ust_bar = QHBoxLayout()
        baslik = QLabel("🎫 DESTEK TALEPLERİ"); baslik.setStyleSheet("color: white; font-size: 22px; font-weight: 800; letter-spacing: 2px;")
        ust_bar.addWidget(baslik); ust_bar.addStretch()
        self.ana_layout.addLayout(ust_bar)

        govde_layout = QHBoxLayout()
        
        self.sol_panel = QFrame()
        self.sol_panel.setFixedWidth(300)
        self.sol_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #e74c3c;")
        sol_duzen = QVBoxLayout(self.sol_panel)
        sol_duzen.setContentsMargins(20, 20, 20, 20)
        
        f_baslik = QLabel("YENİ TALEP OLUŞTUR"); f_baslik.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px; border: none; margin-bottom: 10px;"); sol_duzen.addWidget(f_baslik)
        
        lbl_m = QLabel("Müşteri Seç"); lbl_m.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sol_duzen.addWidget(lbl_m)
        self.combo_musteri = QComboBox()
        self.combo_musteri.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        sol_duzen.addWidget(self.combo_musteri)

        lbl_a = QLabel("Açıklama"); lbl_a.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sol_duzen.addWidget(lbl_a)
        self.inp_aciklama = QTextEdit()
        self.inp_aciklama.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        self.inp_aciklama.setFixedHeight(80)
        sol_duzen.addWidget(self.inp_aciklama)

        lbl_o = QLabel("Öncelik"); lbl_o.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sol_duzen.addWidget(lbl_o)
        self.combo_oncelik = QComboBox()
        self.combo_oncelik.addItems(["Düşük", "Normal", "Yüksek", "Acil"])
        self.combo_oncelik.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        sol_duzen.addWidget(self.combo_oncelik)

        btn_ekle = QPushButton("📨 Talebi Kaydet")
        btn_ekle.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 12px; border-radius: 10px; border: none; margin-top:10px;")
        btn_ekle.clicked.connect(self.talep_ekle)
        sol_duzen.addWidget(btn_ekle); sol_duzen.addStretch()

        orta_panel = QVBoxLayout()
        orta_panel.setSpacing(10)
        
        orta_panel.addWidget(self.tablo_baslik_uret("🔴 AÇIK TALEPLER"))
        self.tablo_acik = self.tablo_uret()
        orta_panel.addWidget(self.tablo_acik)

        orta_panel.addWidget(self.tablo_baslik_uret("🟠 İŞLEMDE OLANLAR"))
        self.tablo_islemde = self.tablo_uret()
        orta_panel.addWidget(self.tablo_islemde)

        orta_panel.addWidget(self.tablo_baslik_uret("🟢 ÇÖZÜLMÜŞ TALEPLER"))
        self.tablo_cozulmus = self.tablo_uret()
        orta_panel.addWidget(self.tablo_cozulmus)

        self.sag_panel = QFrame()
        self.sag_panel.setFixedWidth(280)
        self.sag_panel.setStyleSheet("background-color: #161923; border-radius: 20px; border: 2px solid #e74c3c;")
        sag_duzen = QVBoxLayout(self.sag_panel)
        sag_duzen.setContentsMargins(20, 20, 20, 20)
        
        g_baslik = QLabel("TALEP GÜNCELLE"); g_baslik.setStyleSheet("color: white; font-size: 14px; font-weight: bold; border: none; margin-bottom: 10px;"); sag_duzen.addWidget(g_baslik)

        self.lbl_secilen_id = QLabel("") 
        self.lbl_secilen_id.hide()
        self.lbl_detay = QLabel("Listeden talep seçin."); self.lbl_detay.setStyleSheet("color: #adb0bb; font-size: 12px; border: none;"); self.lbl_detay.setWordWrap(True)
        sag_duzen.addWidget(self.lbl_detay); sag_duzen.addSpacing(15)

        lbl_d = QLabel("Durum"); lbl_d.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sag_duzen.addWidget(lbl_d)
        self.combo_durum = QComboBox()
        self.combo_durum.addItems(["Açık", "İşlemde", "Kapalı (Çözüldü)"])
        self.combo_durum.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        sag_duzen.addWidget(self.combo_durum)

        lbl_c = QLabel("Çözüm Notu"); lbl_c.setStyleSheet("color: #565b6e; font-size: 11px; margin-top: 5px; border: none;"); sag_duzen.addWidget(lbl_c)
        self.inp_cozum = QTextEdit()
        self.inp_cozum.setStyleSheet("background-color: #0b0e14; color: white; padding: 10px; border-radius: 8px; border: 1px solid #1f222d;")
        self.inp_cozum.setFixedHeight(100)
        sag_duzen.addWidget(self.inp_cozum)

        btn_guncelle = QPushButton("🔄 Durumu Güncelle")
        btn_guncelle.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 12px; border-radius: 10px; border: none; margin-top:10px;")
        btn_guncelle.clicked.connect(self.durum_guncelle_islem)
        sag_duzen.addWidget(btn_guncelle); sag_duzen.addStretch()

        govde_layout.addWidget(self.sol_panel)
        govde_layout.addLayout(orta_panel)
        govde_layout.addWidget(self.sag_panel)
        self.ana_layout.addLayout(govde_layout)

    def tablo_baslik_uret(self, metin):
        lbl = QLabel(metin); lbl.setStyleSheet("color: #8b8e98; font-weight: bold; font-size: 12px;"); return lbl

    def tablo_uret(self):
        t = QTableWidget(0, 7)
        t.setHorizontalHeaderLabels(["ID", "Müşteri", "Telefon", "Açıklama", "Öncelik", "Durum", "Çözüm Notu"])
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setSelectionBehavior(QAbstractItemView.SelectRows)
        t.verticalHeader().setVisible(False)
        t.setStyleSheet("""
            QTableWidget { background-color: transparent; color: #adb0bb; border: none; font-size: 12px; outline: none; }
            QTableWidget::item { border-bottom: 1px solid #1f222d; padding: 5px; }
            QHeaderView::section { background-color: #161923; color: #e74c3c; font-weight: bold; border: none; border-bottom: 2px solid #e74c3c; height: 35px; }
            QTableWidget::item:selected { background-color: #1f222d; color: #e74c3c; }
        """)
        t.itemSelectionChanged.connect(lambda: self.satir_secildi(t))
        return t

    def verileri_guncelle(self):
        self.combo_musteri.clear()
        musteriler = self.db.musterileri_getir()
        for m in musteriler:
            self.combo_musteri.addItem(m[1], m[0])

        self.tablo_acik.setRowCount(0); self.tablo_islemde.setRowCount(0); self.tablo_cozulmus.setRowCount(0)
        
        destek_talepleri = self.db.destek_taleplerini_getir()
        for d in destek_talepleri:
            m = self.db.get_musteri_by_id(d[1])
            m_ad = m[1] if m else "Bilinmiyor"
            m_tel = m[2] if m else "-"
            
            if d[4] == "Açık": t = self.tablo_acik
            elif d[4] == "İşlemde": t = self.tablo_islemde
            else: t = self.tablo_cozulmus
            
            row = t.rowCount()
            t.insertRow(row)
            t.setItem(row, 0, QTableWidgetItem(str(d[0])))
            t.setItem(row, 1, QTableWidgetItem(m_ad))
            t.setItem(row, 2, QTableWidgetItem(m_tel))
            t.setItem(row, 3, QTableWidgetItem(d[2]))
            t.setItem(row, 4, QTableWidgetItem(d[3]))
            t.setItem(row, 5, QTableWidgetItem(d[4]))
            t.setItem(row, 6, QTableWidgetItem(d[5]))

    def talep_ekle(self):
        if self.combo_musteri.count() == 0:
            QMessageBox.warning(self, "Hata", "Önce müşteri eklemelisiniz!")
            return
            
        m_id = self.combo_musteri.currentData()
        aciklama = self.inp_aciklama.toPlainText()
        oncelik = self.combo_oncelik.currentText()
        
        if not aciklama.strip():
            QMessageBox.warning(self, "Hata", "Lütfen bir açıklama girin!")
            return
            
        tarih = QDate.currentDate().toString('dd.MM.yyyy')
        self.db.destek_talep_ekle(m_id, aciklama, oncelik, "Açık", "", tarih)
        
        self.verileri_guncelle()
        QMessageBox.information(self, "Başarılı", "Destek talebi oluşturuldu!")
        self.inp_aciklama.clear()

    def satir_secildi(self, tablo):
        row = tablo.currentRow()
        if row >= 0:
            d_id = tablo.item(row, 0).text()
            self.lbl_secilen_id.setText(d_id)
            
            # DB'den güncel veriyi çek
            self.db.cursor.execute("SELECT id, aciklama, durum, cozum FROM Destek WHERE id = ?", (d_id,))
            d = self.db.cursor.fetchone()
            if not d: return
            
            self.lbl_detay.setText(f"Talep #{d[0]}\nSorun: {d[1]}")
            idx = self.combo_durum.findText(d[2], Qt.MatchContains)
            if idx >= 0: self.combo_durum.setCurrentIndex(idx)
            self.inp_cozum.setPlainText(d[3])

    def durum_guncelle_islem(self):
        d_id = self.lbl_secilen_id.text()
        if not d_id:
            QMessageBox.warning(self, "Hata", "Lütfen listeden bir talep seçin!")
            return
            
        yeni_durum_metin = self.combo_durum.currentText()
        if "Açık" in yeni_durum_metin: durum = "Açık"
        elif "İşlemde" in yeni_durum_metin: durum = "İşlemde"
        else: durum = "Kapalı (Çözüldü)"
        
        cozum = self.inp_cozum.toPlainText()
        self.db.destek_talep_guncelle(d_id, durum, cozum)
        self.verileri_guncelle()
        QMessageBox.information(self, "Başarılı", "Talep durumu güncellendi!")


# =========================================================================
# 7. SINIF: MAIN PENCERE
# =========================================================================
class NexoraAnaEkran(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXORA TECH | Dashboard & CRM")
        self.setGeometry(50, 50, 1600, 950)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #0b0e14; }
            QMessageBox { background-color: #161923; border: 1px solid #00d2ff; }
            QMessageBox QLabel { color: white; font-size: 14px; min-width: 250px; padding: 10px; } 
            QMessageBox QPushButton { background-color: #00d2ff; color: #0b0e14; font-weight: bold; padding: 7px 22px; border-radius: 5px; min-width: 85px; }
        """)

        self.veritabani = VeriDeposu()
        self.merkezi_widget = QWidget()
        self.setCentralWidget(self.merkezi_widget)
        self.ana_layout = QHBoxLayout(self.merkezi_widget)
        self.ana_layout.setContentsMargins(0, 0, 0, 0)
        self.ana_layout.setSpacing(0)

        self.sidebar_kur()

        self.sayfalar = QStackedWidget()
        self.sayfa_dashboard = DashboardSayfasi(self.veritabani)
        self.sayfa_crm = MusteriKayitSayfasi(self.veritabani)
        self.sayfa_urun = UrunStokSayfasi(self.veritabani)
        self.sayfa_tedarik = TedarikciSayfasi(self.veritabani)
        self.sayfa_satis = SatisSayfasi(self.veritabani)
        self.sayfa_destek = DestekSayfasi(self.veritabani)

        self.sayfalar.addWidget(self.sayfa_dashboard)
        self.sayfalar.addWidget(self.sayfa_crm)
        self.sayfalar.addWidget(self.sayfa_urun)
        self.sayfalar.addWidget(self.sayfa_tedarik)
        self.sayfalar.addWidget(self.sayfa_satis)
        self.sayfalar.addWidget(self.sayfa_destek)
        
        self.sayfalar.currentChanged.connect(self.sayfa_degisti)

        self.ana_layout.addWidget(self.sidebar)
        self.ana_layout.addWidget(self.sayfalar)
        
    def sayfa_degisti(self, index):
        widget = self.sayfalar.widget(index)
        if hasattr(widget, 'verileri_guncelle'):
            widget.verileri_guncelle()

    def sidebar_kur(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("background-color: #161923; border-right: 1px solid #1f222d;")
        sidebar_duzen = QVBoxLayout(self.sidebar)
        sidebar_duzen.setContentsMargins(15, 30, 15, 30)

        logo = QLabel("🚀 NEXORA")
        logo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 30px;")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_duzen.addWidget(logo)

        self.nav_butonu_ekle("📊 Dashboard", 0, "#00d2ff")
        self.nav_butonu_ekle("👥 Müşteri Yönetimi", 1, "#00d2ff")
        self.nav_butonu_ekle("📦 Ürün & Stok", 2, "#f39c12")
        self.nav_butonu_ekle("🏭 Tedarikçi Yönetimi", 3, "#9b59b6")
        self.nav_butonu_ekle("🛒 Satış Yönetimi", 4, "#2ecc71")
        self.nav_butonu_ekle("🎫 Destek Talepleri", 5, "#e74c3c")
        
        sidebar_duzen.addStretch()
        v_lbl = QLabel("v5.0 SQL EDITION"); v_lbl.setStyleSheet("color: #565b6e; font-size: 11px;"); v_lbl.setAlignment(Qt.AlignCenter); sidebar_duzen.addWidget(v_lbl)

    def nav_butonu_ekle(self, metin, index, hover_renk):
        btn = QPushButton(metin)
        btn.setStyleSheet(f"""
            QPushButton {{ color: #8b8e98; font-size: 14px; font-weight: bold; text-align: left; padding: 15px; border: none; border-radius: 10px; margin-bottom: 5px; }}
            QPushButton:hover {{ background-color: #1f222d; color: {hover_renk}; }}
        """)
        btn.clicked.connect(lambda: self.sayfalar.setCurrentIndex(index))
        self.sidebar.layout().addWidget(btn)
        return btn

    def closeEvent(self, event):
        self.veritabani.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = NexoraAnaEkran()
    pencere.show()
    sys.exit(app.exec_())