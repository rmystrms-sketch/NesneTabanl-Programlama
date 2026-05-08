import sys
import sqlite3
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# ══════════════════════════════════════════════════════════
#  1. BÖLÜM: VERİ MODELLERİ (BACKEND)
# ══════════════════════════════════════════════════════════

GLOBAL_KUR = 33.0
GLOBAL_VERGI = 20.0

class Urun:
    def __init__(self, urun_id, ad, kategori, stok, fiyat, min_stok=10):
        self._id = urun_id
        self._ad = ad
        self._kategori = kategori
        self._stok = stok
        self._fiyat = fiyat
        self._min_stok = min_stok
        self.tur = "Genel"
        self.tedarikci = ""
        self.teslimat_suresi = ""

    def id_getir(self): return self._id
    def ad_getir(self): return self._ad
    def stok_getir(self): return self._stok
    def fiyat_getir(self): return self._fiyat
    def min_stok_getir(self): return self._min_stok

    def stok_guncelle(self, miktar):
        if self._stok + miktar >= 0:
            self._stok += miktar
            return True
        return False

class YerliUrun(Urun):
    def __init__(self, urun_id, ad, kategori, stok, fiyat, min_stok=10):
        super().__init__(urun_id, ad, kategori, stok, fiyat, min_stok)
        self.tur = "Yerli"
        self.tedarikci = "Yerli Üretici"
        self.teslimat_suresi = "2 Gün"

class IthalUrun(Urun):
    def __init__(self, urun_id, ad, kategori, stok, baz_fiyat, tedarikci="Bilinmiyor", min_stok=10):
        super().__init__(urun_id, ad, kategori, stok, baz_fiyat, min_stok)
        self.tur = "İthal"
        self.tedarikci = tedarikci
        self.teslimat_suresi = "15 Gün"
        
    def fiyat_getir(self):
        return self._fiyat * GLOBAL_KUR * (1 + GLOBAL_VERGI / 100)

class Siparis:
    def __init__(self, s_id, kalemler=None, urun_ad=None, adet=None, toplam=None, zaman=None, durum="Hazırlanıyor"):
        self._s_id = s_id
        if kalemler is not None:
            self._kalemler = kalemler
            self._urun_ad = ", ".join([f"{k['urun'].ad_getir()}" for k in kalemler])
            self._adet = sum([k['adet'] for k in kalemler])
            self._toplam = sum([k['urun'].fiyat_getir() * k['adet'] for k in kalemler])
            self._dt = datetime.now()
            self._zaman = self._dt.strftime("%d/%m/%Y %H:%M")
        else:
            self._kalemler = []
            self._urun_ad = urun_ad
            self._adet = adet
            self._toplam = toplam
            self._zaman = zaman
            
        self._durum = durum

    def durum_getir(self):
        return self._durum
        
    def durum_ilerlet(self):
        if self._durum == "Hazırlanıyor":
            self._durum = "Kargoda"
        elif self._durum == "Kargoda":
            self._durum = "Tamamlandı"

class DepoYonetimi:
    def __init__(self):
        self.__urunler = {}      
        self.__siparisler = []
        self.__ithalat_siparisleri = []
        self.__sepet = {}
        self.db_baglanti_kur()

    def db_baglanti_kur(self):
        self.conn = sqlite3.connect('depo_veritabani.db')
        self.cur = self.conn.cursor()
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY, ad TEXT, kategori TEXT, stok INTEGER, 
            fiyat REAL, min_stok INTEGER, tur TEXT, tedarikci TEXT, teslimat_suresi TEXT
        )''')
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS siparisler (
            s_id TEXT PRIMARY KEY, urun_ad TEXT, adet INTEGER, 
            toplam REAL, zaman TEXT, durum TEXT
        )''')
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS ithalat (
            s_id TEXT PRIMARY KEY, urun_id INTEGER, urun_ad TEXT, 
            adet INTEGER, tarih TEXT, tedarikci TEXT, sure TEXT
        )''')
        
        self.cur.execute('''CREATE TABLE IF NOT EXISTS hareketler (
            id INTEGER PRIMARY KEY AUTOINCREMENT, urun_id INTEGER, 
            islem TEXT, miktar INTEGER, tarih TEXT
        )''')
        
        self.conn.commit()
        self.verileri_yukle()

    def verileri_yukle(self):
        self.cur.execute("SELECT * FROM urunler")
        for satir in self.cur.fetchall():
            u_id, ad, kat, stok, fiyat, min_stok, tur, ted, sure = satir
            if tur == "Yerli":
                self.__urunler[u_id] = YerliUrun(u_id, ad, kat, stok, fiyat, min_stok)
            else:
                self.__urunler[u_id] = IthalUrun(u_id, ad, kat, stok, fiyat, ted, min_stok)

        self.cur.execute("SELECT * FROM siparisler")
        for satir in self.cur.fetchall():
            s_id, urun_ad, adet, toplam, zaman, durum = satir
            s = Siparis(s_id, kalemler=None, urun_ad=urun_ad, adet=adet, toplam=toplam, zaman=zaman, durum=durum)
            self.__siparisler.append(s)

        self.cur.execute("SELECT * FROM ithalat")
        for satir in self.cur.fetchall():
            s_id, urun_id, urun_ad, adet, tarih, tedarikci, sure = satir
            self.__ithalat_siparisleri.append({
                's_id': s_id, 'urun_id': urun_id, 'urun_ad': urun_ad,
                'adet': adet, 'tarih': tarih, 'tedarikci': tedarikci, 'sure': sure
            })

    def kapat(self):
        if self.conn:
            self.conn.close()

    def hareket_kaydet(self, urun_id, islem, miktar):
        zaman = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cur.execute("INSERT INTO hareketler (urun_id, islem, miktar, tarih) VALUES (?, ?, ?, ?)", 
                         (urun_id, islem, miktar, zaman))
        self.conn.commit()

    def hareket_getir(self, urun_id):
        self.cur.execute("SELECT islem, miktar, tarih FROM hareketler WHERE urun_id = ? ORDER BY id DESC LIMIT 10", (urun_id,))
        return self.cur.fetchall()

    def urunler_getir(self): return self.__urunler
    def siparisler_getir(self): return self.__siparisler
    def ithalat_siparisleri_getir(self): return self.__ithalat_siparisleri
    def sepet_getir(self): return self.__sepet

    def urun_kaydet(self, urun, islem="Ürün Eklendi/Güncellendi", miktar=None):
        self.__urunler[urun.id_getir()] = urun
        self.cur.execute('''INSERT OR REPLACE INTO urunler 
            (id, ad, kategori, stok, fiyat, min_stok, tur, tedarikci, teslimat_suresi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (urun.id_getir(), urun.ad_getir(), urun._kategori, urun.stok_getir(), 
             urun._fiyat, urun.min_stok_getir(), urun.tur, urun.tedarikci, urun.teslimat_suresi))
        self.conn.commit()
        if miktar is not None:
            self.hareket_kaydet(urun.id_getir(), islem, miktar)

    def urun_sil(self, urun_id):
        if urun_id in self.__urunler:
            del self.__urunler[urun_id]
            self.cur.execute("DELETE FROM urunler WHERE id=?", (urun_id,))
            self.conn.commit()
            return True
        return False

    def urun_duzenle(self, urun_id, yeni_ad, yeni_kategori, yeni_fiyat):
        if urun_id in self.__urunler:
            u = self.__urunler[urun_id]
            u._ad = yeni_ad
            u._kategori = yeni_kategori
            u._fiyat = yeni_fiyat
            self.cur.execute("UPDATE urunler SET ad=?, kategori=?, fiyat=? WHERE id=?", (yeni_ad, yeni_kategori, yeni_fiyat, urun_id))
            self.conn.commit()
            return True
        return False

    def db_stok_guncelle(self, urun, islem="Stok Güncellendi", miktar=0):
        self.cur.execute("UPDATE urunler SET stok = ? WHERE id = ?", (urun.stok_getir(), urun.id_getir()))
        self.conn.commit()
        if miktar != 0:
            self.hareket_kaydet(urun.id_getir(), islem, miktar)

    def stok_kontrol_ve_ithalat(self, urun):
        if urun.stok_getir() < urun.min_stok_getir():
            bekleyen_var_mi = any(s['urun_id'] == urun.id_getir() for s in self.__ithalat_siparisleri)
            if not bekleyen_var_mi:
                s_id = f"SUP-{len(self.__ithalat_siparisleri)+101}"
                tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
                yeni_siparis = {
                    's_id': s_id, 'urun_id': urun.id_getir(), 'urun_ad': urun.ad_getir(),
                    'adet': 20, 'tarih': tarih, 'tedarikci': urun.tedarikci, 'sure': urun.teslimat_suresi
                }
                self.__ithalat_siparisleri.append(yeni_siparis)
                self.cur.execute('''INSERT INTO ithalat (s_id, urun_id, urun_ad, adet, tarih, tedarikci, sure)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                 (s_id, urun.id_getir(), urun.ad_getir(), 20, tarih, urun.tedarikci, urun.teslimat_suresi))
                self.conn.commit()

    def sepete_ekle(self, urun_id, adet):
        if urun_id in self.__urunler:
            urun = self.__urunler[urun_id]
            mevcut_sepet_adet = self.__sepet.get(urun_id, 0)
            if urun.stok_getir() >= (mevcut_sepet_adet + adet):
                self.__sepet[urun_id] = mevcut_sepet_adet + adet
                return True, "Ürün sepete eklendi."
            return False, "Yetersiz Stok!"
        return False, "Ürün Sistemde Yok!"
        
    def sepeti_onayla(self):
        if not self.__sepet:
            return False, "Sepet boş!"
            
        kalemler = []
        for uid, adet in self.__sepet.items():
            urun = self.__urunler[uid]
            if urun.stok_guncelle(-adet):
                self.db_stok_guncelle(urun, "Sepet Satışı", -adet)
                kalemler.append({"urun": urun, "adet": adet})
                self.stok_kontrol_ve_ithalat(urun)
            else:
                return False, f"{urun.ad_getir()} için stok yetersiz! Sipariş iptal edildi."
                
        s_id = f"TRX-{len(self.__siparisler) + 1001}"
        yeni_siparis = Siparis(s_id, kalemler=kalemler)
        self.__siparisler.append(yeni_siparis)
        self.cur.execute('''INSERT INTO siparisler (s_id, urun_ad, adet, toplam, zaman, durum)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (yeni_siparis._s_id, yeni_siparis._urun_ad, yeni_siparis._adet, 
                          yeni_siparis._toplam, yeni_siparis._zaman, yeni_siparis._durum))
        self.conn.commit()
        self.__sepet.clear()
        return True, "Sipariş başarıyla oluşturuldu."

    def satis_yap(self, urun_id, adet):
        if urun_id in self.__urunler:
            urun = self.__urunler[urun_id]
            if urun.stok_guncelle(-adet):
                self.db_stok_guncelle(urun, "Hızlı Satış", -adet)
                s_id = f"TRX-{len(self.__siparisler) + 1001}"
                yeni_siparis = Siparis(s_id, kalemler=[{"urun": urun, "adet": adet}])
                self.__siparisler.append(yeni_siparis)
                self.cur.execute('''INSERT INTO siparisler (s_id, urun_ad, adet, toplam, zaman, durum)
                                    VALUES (?, ?, ?, ?, ?, ?)''',
                                 (yeni_siparis._s_id, yeni_siparis._urun_ad, yeni_siparis._adet, 
                                  yeni_siparis._toplam, yeni_siparis._zaman, yeni_siparis._durum))
                self.conn.commit()
                self.stok_kontrol_ve_ithalat(urun)
                return True, "Satış Tamamlandı"
            return False, "Yetersiz Stok!"
        return False, "Ürün Sistemde Yok"
        
    def ithalat_teslim_al(self, s_id):
        for idx, imp in enumerate(self.__ithalat_siparisleri):
            if imp['s_id'] == s_id:
                urun = self.__urunler.get(imp['urun_id'])
                if urun:
                    urun.stok_guncelle(imp['adet'])
                    self.db_stok_guncelle(urun, "Tedarik Teslimi", imp['adet'])
                self.__ithalat_siparisleri.pop(idx)
                self.cur.execute("DELETE FROM ithalat WHERE s_id = ?", (s_id,))
                self.conn.commit()
                return True, "Tedarik teslim alındı ve stok güncellendi."
        return False, "Sipariş bulunamadı."
        
    def siparis_durumunu_guncelle(self, siparis):
        siparis.durum_ilerlet()
        self.cur.execute("UPDATE siparisler SET durum = ? WHERE s_id = ?", (siparis._durum, siparis._s_id))
        self.conn.commit()

# ══════════════════════════════════════════════════════════
#  2. BÖLÜM: MODERN MAVİ ARAYÜZ (GUI) ve TEMA MOTORU
# ══════════════════════════════════════════════════════════

TEMALAR = {
    "dark": {
        'arkaplan': '#0B0E14',
        'yan_panel': '#151921',
        'kart': '#1C232E',
        'kenarlik': '#2D3748',
        'vurgu': '#38BDF8',        
        'vurgu_hover': '#0284C7',
        'metin': '#FFFFFF',        
        'metin_gri': '#94A3B8',
        'basari': '#2DD4BF',       
        'basari_hover': '#0D9488',
        'tehlike': '#FB7185',      
        'tehlike_hover': '#E11D48',
        'satir_secili': '#242F3E',
        'input_bg': '#0B0E14'
    },
    "light": {
        'arkaplan': '#F8FAFC',
        'yan_panel': '#FFFFFF',
        'kart': '#FFFFFF',
        'kenarlik': '#E2E8F0',
        'vurgu': '#0EA5E9',        
        'vurgu_hover': '#0284C7',
        'metin': '#0F172A',        
        'metin_gri': '#64748B',
        'basari': '#10B981',       
        'basari_hover': '#059669',
        'tehlike': '#F43F5E',      
        'tehlike_hover': '#E11D48',
        'satir_secili': '#F1F5F9',
        'input_bg': '#FFFFFF'
    }
}

class DashboardKarti(QFrame):
    def __init__(self, baslik, deger, renk_anahtari):
        super().__init__()
        self.renk_anahtari = renk_anahtari
        self.setMinimumHeight(110)
        l = QVBoxLayout(self)
        self.lbl_b = QLabel(baslik.upper())
        self.lbl_d = QLabel(str(deger))
        l.addWidget(self.lbl_b)
        l.addWidget(self.lbl_d)

    def temayi_guncelle(self, t):
        renk = t[self.renk_anahtari]
        self.setStyleSheet(f"QFrame {{ background-color: {t['kart']}; border-radius: 12px; border: 1px solid {t['kenarlik']}; border-top: 4px solid {renk}; }}")
        self.lbl_b.setStyleSheet(f"color: {t['metin_gri']}; font-weight:bold; font-size:11px; border:none;")
        self.lbl_d.setStyleSheet(f"color: {t['metin']}; font-size:26px; font-weight:900; border:none;")

class DepoUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sistem = DepoYonetimi()
        self.aktif_tema = "dark"
        self.setWindowTitle("SkyStock v2 - Modern Yönetim")
        self.resize(1200, 750)

        merkez = QWidget()
        self.setCentralWidget(merkez)
        self.ana_layout = QHBoxLayout(merkez)
        self.ana_layout.setContentsMargins(0, 0, 0, 0)
        self.ana_layout.setSpacing(0)

        self.sayfalar = QStackedWidget()
        self.sidebar_olustur()
        self.dash_sayfasi_tasarla()
        self.stok_sayfasi_tasarla()
        self.urun_siparis_sayfasi_tasarla()
        
        self.ana_layout.addWidget(self.sidebar)
        self.ana_layout.addWidget(self.sayfalar)
        
        self.ornek_veriler()
        self.temayi_uygula()

    def closeEvent(self, event):
        self.sistem.kapat()
        event.accept()

    def tema_getir(self):
        return TEMALAR[self.aktif_tema]

    def buton_stili(self, renk_anahtari):
        t = self.tema_getir()
        return f"""
            QPushButton {{
                background: {t[renk_anahtari]};
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background: {t[renk_anahtari + '_hover']};
            }}
        """

    def input_stili(self):
        t = self.tema_getir()
        return f"background:{t['input_bg']}; color:{t['metin']}; border:1px solid {t['kenarlik']}; border-radius:8px; padding:10px;"

    def tablo_stili(self):
        t = self.tema_getir()
        return f"""
            QTableWidget {{ background-color: {t['kart']}; color: {t['metin']}; border: none; gridline-color: {t['kenarlik']}; }}
            QHeaderView::section {{ background-color: {t['yan_panel']}; color: {t['vurgu']}; border: none; padding: 10px; font-weight: bold; }}
            QScrollBar:vertical {{ background: {t['arkaplan']}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {t['kenarlik']}; border-radius: 5px; }}
            QTableWidget::item:selected {{ background-color: {t['satir_secili']}; }}
        """

    def temayi_uygula(self):
        t = self.tema_getir()
        self.setStyleSheet(f"background-color: {t['arkaplan']}; color: {t['metin']};")
        
        self.sidebar.setStyleSheet(f"background-color: {t['yan_panel']}; border-right: 1px solid {t['kenarlik']};")
        self.logo.setStyleSheet(f"color:{t['vurgu']}; font-size:22px; font-weight:bold; margin:25px;")
        self.btn_tema.setStyleSheet(self.menu_butonu_stili(False))
        self.sayfa_degis(self.sayfalar.currentIndex())
        
        for k in [self.k_urun, self.k_stok, self.k_sip, self.k_kritik, self.k_bekleyen]:
            k.temayi_guncelle(t)
            
        self.lbl_dash_son.setStyleSheet(f"color: {t['metin']}; font-weight:bold; font-size:15px;")
        self.lbl_dash_ithal.setStyleSheet(f"color: {t['metin']}; font-weight:bold; font-size:15px; margin-top:15px;")
        
        self.f_kur.setStyleSheet(f"background:{t['kart']}; border-radius:12px; padding:10px; border: 1px solid {t['kenarlik']};")
        self.lbl_kur.setStyleSheet(f"color:{t['metin']}; font-weight:bold; font-size:14px;")
        self.f_giris.setStyleSheet(f"background:{t['kart']}; border-radius:12px; padding:15px; border: 1px solid {t['kenarlik']};")
        
        self.lbl_sepet_tutar.setStyleSheet(f"color:{t['basari']}; font-weight:bold; font-size:24px;")
        
        istil = self.input_stili()
        if hasattr(self, 'in_arama'):
            self.in_arama.setStyleSheet(istil)
        self.in_kur.setStyleSheet(istil)
        self.in_ad.setStyleSheet(istil)
        self.in_tur.setStyleSheet(istil)
        self.in_tedarikci.setStyleSheet(istil)
        self.in_st.setStyleSheet(istil)
        self.in_min_stok.setStyleSheet(istil)
        self.in_fi.setStyleSheet(istil)
        
        self.btn_kur.setStyleSheet(self.buton_stili('vurgu'))
        self.btn_ekle.setStyleSheet(self.buton_stili('vurgu'))
        self.btn_sepet.setStyleSheet(self.buton_stili('basari'))
        
        self.lbl_siparis_baslik.setStyleSheet(f"color: {t['metin']}; font-weight:bold; font-size:18px;")
        
        if hasattr(self, 'btn_disari_aktar'):
            self.btn_disari_aktar.setStyleSheet(self.buton_stili('basari'))

        tstil = self.tablo_stili()
        self.t_son.setStyleSheet(tstil)
        self.t_ithal.setStyleSheet(tstil)
        self.t_stok.setStyleSheet(tstil)
        self.t_tum_siparisler.setStyleSheet(tstil)
        
        self.arayuz_guncelle()

    def tema_degistir(self):
        self.aktif_tema = "light" if self.aktif_tema == "dark" else "dark"
        self.btn_tema.setText("☀️ Açık Tema" if self.aktif_tema == "dark" else "🌙 Koyu Tema")
        self.temayi_uygula()

    def sidebar_olustur(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        l = QVBoxLayout(self.sidebar)
        self.logo = QLabel("💠 SKY-STOCK")
        l.addWidget(self.logo)
        
        self.btn_dash = self.menu_butonu("  📊  Dashboard")
        self.btn_stok = self.menu_butonu("  📦  Stok Listesi")
        self.btn_urun_siparis = self.menu_butonu("  🛒  Ürün Sipariş")
        self.btn_dash.clicked.connect(lambda: self.sayfa_degis(0))
        self.btn_stok.clicked.connect(lambda: self.sayfa_degis(1))
        self.btn_urun_siparis.clicked.connect(lambda: self.sayfa_degis(2))
        l.addWidget(self.btn_dash); l.addWidget(self.btn_stok); l.addWidget(self.btn_urun_siparis); l.addStretch()
        
        self.btn_tema = QPushButton("☀️ Açık Tema")
        self.btn_tema.setFixedHeight(45)
        self.btn_tema.setCursor(Qt.PointingHandCursor)
        self.btn_tema.clicked.connect(self.tema_degistir)
        l.addWidget(self.btn_tema)

    def menu_butonu(self, metin):
        b = QPushButton(metin)
        b.setFixedHeight(50)
        b.setCursor(Qt.PointingHandCursor)
        return b

    def menu_butonu_stili(self, aktif):
        t = self.tema_getir()
        stil = f"QPushButton {{ text-align:left; border:none; color:{t['metin_gri']}; font-weight:bold; font-size:13px; }}"
        if aktif: stil += f"QPushButton {{ background: rgba(56,189,248,0.1); color:{t['vurgu']}; border-left: 4px solid {t['vurgu']}; }}"
        return stil

    def sayfa_degis(self, index):
        self.sayfalar.setCurrentIndex(index)
        self.btn_dash.setStyleSheet(self.menu_butonu_stili(index==0))
        self.btn_stok.setStyleSheet(self.menu_butonu_stili(index==1))
        self.btn_urun_siparis.setStyleSheet(self.menu_butonu_stili(index==2))

    def dash_sayfasi_tasarla(self):
        sayfa = QWidget(); l = QVBoxLayout(sayfa); l.setContentsMargins(35, 35, 35, 35)
        
        grid = QGridLayout()
        self.k_urun = DashboardKarti("Ürün Çeşidi", "0", 'vurgu')
        self.k_stok = DashboardKarti("Toplam Stok", "0", 'basari')
        self.k_sip = DashboardKarti("İşlem Sayısı", "0", 'vurgu')
        self.k_kritik = DashboardKarti("Kritik Stok", "0", 'tehlike')
        self.k_bekleyen = DashboardKarti("Bekleyen Tedarik", "0", 'vurgu')
        grid.addWidget(self.k_urun, 0, 0)
        grid.addWidget(self.k_stok, 0, 1)
        grid.addWidget(self.k_sip, 0, 2)
        grid.addWidget(self.k_kritik, 0, 3)
        grid.addWidget(self.k_bekleyen, 0, 4)
        l.addLayout(grid); l.addSpacing(20)
        
        self.lbl_dash_son = QLabel("🕒 SON SATIŞ KAYITLARI")
        l.addWidget(self.lbl_dash_son)
        self.t_son = QTableWidget(); self.t_son.setColumnCount(3)
        self.t_son.setHorizontalHeaderLabels(["İŞLEM NO", "ÜRÜN ADI", "TUTAR"])
        self.t_son.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.t_son)
        
        self.lbl_dash_ithal = QLabel("🚢 BEKLEYEN TEDARİK SİPARİŞLERİ")
        l.addWidget(self.lbl_dash_ithal)
        self.t_ithal = QTableWidget(); self.t_ithal.setColumnCount(7)
        self.t_ithal.setHorizontalHeaderLabels(["SİPARİŞ NO", "ÜRÜN ADI", "ADET", "TEDARİKÇİ", "SÜRE", "ZAMAN", "İŞLEM"])
        self.t_ithal.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.t_ithal)
        
        self.sayfalar.addWidget(sayfa)

    def stok_sayfasi_tasarla(self):
        sayfa = QWidget(); l = QVBoxLayout(sayfa); l.setContentsMargins(35, 35, 35, 35)
        
        ust_layout = QHBoxLayout()
        lbl_baslik = QLabel("📦 STOK LİSTESİ")
        lbl_baslik.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.in_arama = QLineEdit()
        self.in_arama.setPlaceholderText("🔍 Ürün Adı veya Kategori Ara...")
        self.in_arama.textChanged.connect(self.arayuz_guncelle)
        self.in_arama.setMinimumWidth(300)
        
        self.btn_disari_aktar = QPushButton("📊 Excel Çıktısı Al")
        self.btn_disari_aktar.clicked.connect(self.stok_disari_aktar)
        ust_layout.addWidget(lbl_baslik)
        ust_layout.addSpacing(20)
        ust_layout.addWidget(self.in_arama)
        ust_layout.addStretch()
        ust_layout.addWidget(self.btn_disari_aktar)
        l.addLayout(ust_layout)
        l.addSpacing(10)

        self.t_stok = QTableWidget(); self.t_stok.setColumnCount(8)
        self.t_stok.setHorizontalHeaderLabels(["ID", "TÜR", "ÜRÜN", "STOK", "FİYAT", "STOK İŞLEMİ", "SEPET", "İŞLEMLER"])
        self.t_stok.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.t_stok); self.sayfalar.addWidget(sayfa)

    def urun_siparis_sayfasi_tasarla(self):
        sayfa = QWidget(); l = QVBoxLayout(sayfa); l.setContentsMargins(35, 35, 35, 35)
        
        self.f_kur = QFrame()
        f_kur_l = QHBoxLayout(self.f_kur)
        self.lbl_kur = QLabel("💵 Anlık USD Kuru:")
        self.in_kur = QDoubleSpinBox(); self.in_kur.setRange(1.0, 500.0); self.in_kur.setValue(GLOBAL_KUR)
        self.btn_kur = QPushButton("KURU GÜNCELLE")
        self.btn_kur.clicked.connect(self.kur_guncelle)
        f_kur_l.addWidget(self.lbl_kur); f_kur_l.addWidget(self.in_kur); f_kur_l.addWidget(self.btn_kur); f_kur_l.addStretch()
        l.addWidget(self.f_kur); l.addSpacing(10)

        self.f_giris = QFrame()
        f_l = QHBoxLayout(self.f_giris)
        self.in_ad = QComboBox(); self.in_ad.setEditable(True); self.in_ad.lineEdit().setPlaceholderText("Ürün İsmi...")
        self.in_tur = QComboBox(); self.in_tur.addItems(["Yerli", "İthal"])
        self.in_tedarikci = QComboBox(); self.in_tedarikci.setEditable(True); self.in_tedarikci.lineEdit().setPlaceholderText("Tedarikçi Firma...")
        self.in_st = QSpinBox(); self.in_st.setRange(1, 9999)
        self.in_min_stok = QSpinBox(); self.in_min_stok.setRange(1, 999); self.in_min_stok.setValue(10); self.in_min_stok.setPrefix("Min: ")
        self.in_fi = QDoubleSpinBox(); self.in_fi.setRange(1, 99999)
        self.btn_ekle = QPushButton("ÜRÜN EKLE")
        self.btn_ekle.clicked.connect(self.is_kaydet)
        
        self.in_tur.currentTextChanged.connect(lambda t: self.in_tedarikci.setVisible(t == "İthal"))
        self.in_tedarikci.setVisible(False)
        
        f_l.addWidget(self.in_ad); f_l.addWidget(self.in_tur); f_l.addWidget(self.in_tedarikci); f_l.addWidget(self.in_st); f_l.addWidget(self.in_min_stok); f_l.addWidget(self.in_fi); f_l.addWidget(self.btn_ekle)
        l.addWidget(self.f_giris); l.addSpacing(10)
        
        sepet_layout = QHBoxLayout()
        self.btn_sepet = QPushButton("🛒 SEPETİ ONAYLA")
        self.btn_sepet.clicked.connect(self.sepeti_onayla_gui)
        
        self.lbl_sepet_tutar = QLabel("Sepet Toplamı: 0.00 TL")
        
        sepet_layout.addWidget(self.btn_sepet)
        sepet_layout.addWidget(self.lbl_sepet_tutar)
        sepet_layout.addStretch()
        l.addLayout(sepet_layout); l.addSpacing(10)
        
        self.lbl_siparis_baslik = QLabel("📝 TÜM SİPARİŞLER")
        l.addWidget(self.lbl_siparis_baslik)
        
        self.t_tum_siparisler = QTableWidget(); self.t_tum_siparisler.setColumnCount(7)
        self.t_tum_siparisler.setHorizontalHeaderLabels(["SİPARİŞ NO", "ÜRÜN ADI", "ADET", "TUTAR", "ZAMAN", "DURUM", "İŞLEM"])
        self.t_tum_siparisler.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.t_tum_siparisler)
        
        self.sayfalar.addWidget(sayfa)

    def is_kaydet(self):
        ad = self.in_ad.currentText().strip()
        if ad:
            urunler_listesi = self.sistem.urunler_getir()
            
            varolan_urun = next((u for u in urunler_listesi.values() if u.ad_getir().lower() == ad.lower()), None)
            if varolan_urun:
                self.stok_degistir(varolan_urun.id_getir(), self.in_st.value())
                self.in_ad.setCurrentText("")
                QMessageBox.information(self, "Bilgi", f"'{ad}' isimli ürün zaten mevcuttu. Doğrudan stoklarına eklendi.")
                return

            u_id = 100 + len(urunler_listesi)
            while u_id in urunler_listesi:
                u_id += 1
                
            if self.in_tur.currentText() == "Yerli":
                yeni_urun = YerliUrun(u_id, ad, "Genel", self.in_st.value(), self.in_fi.value(), self.in_min_stok.value())
            else:
                tedarikci = self.in_tedarikci.currentText() if self.in_tedarikci.currentText() else "Bilinmiyor"
                yeni_urun = IthalUrun(u_id, ad, "Genel", self.in_st.value(), self.in_fi.value(), tedarikci, self.in_min_stok.value())
            self.sistem.urun_kaydet(yeni_urun, "Yeni Ürün", self.in_st.value())
            self.arayuz_guncelle(); self.in_ad.setCurrentText("")

    def is_satis(self, uid):
        basari, mesaj = self.sistem.sepete_ekle(uid, 1)
        if basari:
            self.arayuz_guncelle()
        else:
            QMessageBox.warning(self, "Hata", mesaj)

    def sepeti_onayla_gui(self):
        basari, mesaj = self.sistem.sepeti_onayla()
        if basari:
            QMessageBox.information(self, "Başarılı", mesaj)
            self.arayuz_guncelle()
        else:
            QMessageBox.warning(self, "Uyarı", mesaj)

    def siparis_durumu_degistir(self, siparis):
        self.sistem.siparis_durumunu_guncelle(siparis)
        self.arayuz_guncelle()

    def ithalat_tamamla_gui(self, s_id):
        basari, mesaj = self.sistem.ithalat_teslim_al(s_id)
        if basari:
            self.arayuz_guncelle()

    def stok_degistir(self, uid, miktar):
        urunler = self.sistem.urunler_getir()
        if uid in urunler:
            urun = urunler[uid]
            if urun.stok_guncelle(miktar):
                self.sistem.db_stok_guncelle(urun, "Manuel Değişim", miktar)
                self.sistem.stok_kontrol_ve_ithalat(urun)
                self.arayuz_guncelle()
            else:
                QMessageBox.warning(self, "Hata", "Stok 0'ın altına düşemez!")

    def urun_duzenle_gui(self, uid):
        urun = self.sistem.urunler_getir().get(uid)
        if urun:
            dialog = QDialog(self)
            dialog.setWindowTitle("Ürün Düzenle")
            dialog.setMinimumWidth(350)
            
            t = self.tema_getir()
            dialog.setStyleSheet(f"background-color: {t['arkaplan']}; color: {t['metin']};")
            
            layout = QVBoxLayout(dialog)
            
            layout.addWidget(QLabel("Ürün Adı:"))
            in_ad = QLineEdit(urun.ad_getir())
            in_ad.setStyleSheet(self.input_stili())
            layout.addWidget(in_ad)
            
            layout.addWidget(QLabel("Kategori:"))
            in_kat = QLineEdit(urun._kategori)
            in_kat.setStyleSheet(self.input_stili())
            layout.addWidget(in_kat)
            
            layout.addWidget(QLabel("Fiyat:"))
            in_fiyat = QDoubleSpinBox()
            in_fiyat.setRange(0, 999999)
            in_fiyat.setValue(urun._fiyat)
            in_fiyat.setStyleSheet(self.input_stili())
            layout.addWidget(in_fiyat)
            
            btn_kaydet = QPushButton("Kaydet")
            btn_kaydet.setStyleSheet(self.buton_stili('basari'))
            btn_kaydet.clicked.connect(dialog.accept)
            layout.addWidget(btn_kaydet)
            
            if dialog.exec_() == QDialog.Accepted:
                if in_ad.text():
                    self.sistem.urun_duzenle(uid, in_ad.text(), in_kat.text(), in_fiyat.value())
                    self.arayuz_guncelle()

    def urun_sil_gui(self, uid):
        urun = self.sistem.urunler_getir().get(uid)
        if urun:
            cevap = QMessageBox.question(self, "Onay", f"{urun.ad_getir()} ürününü silmek istediğinize emin misiniz?",
                                         QMessageBox.Yes | QMessageBox.No)
            if cevap == QMessageBox.Yes:
                self.sistem.urun_sil(uid)
                self.arayuz_guncelle()

    def urun_gecmis_gui(self, uid):
        urun = self.sistem.urunler_getir().get(uid)
        hareketler = self.sistem.hareket_getir(uid)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{urun.ad_getir()} - Hareket Geçmişi")
        dialog.setMinimumWidth(400)
        t = self.tema_getir()
        dialog.setStyleSheet(f"background-color: {t['arkaplan']}; color: {t['metin']};")
        
        layout = QVBoxLayout(dialog)
        
        tablo = QTableWidget()
        tablo.setColumnCount(3)
        tablo.setHorizontalHeaderLabels(["İŞLEM", "MİKTAR", "TARİH"])
        tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tablo.setStyleSheet(self.tablo_stili())
        
        tablo.setRowCount(len(hareketler))
        for i, (islem, miktar, tarih) in enumerate(hareketler):
            tablo.setItem(i, 0, QTableWidgetItem(islem))
            m_text = f"+{miktar}" if miktar > 0 else str(miktar)
            item_m = QTableWidgetItem(m_text)
            if miktar > 0:
                item_m.setForeground(QColor(t['basari']))
            elif miktar < 0:
                item_m.setForeground(QColor(t['tehlike']))
            tablo.setItem(i, 1, item_m)
            tablo.setItem(i, 2, QTableWidgetItem(tarih))
            
        layout.addWidget(tablo)
        
        btn_kapat = QPushButton("Kapat")
        btn_kapat.setStyleSheet(self.buton_stili('vurgu'))
        btn_kapat.clicked.connect(dialog.accept)
        layout.addWidget(btn_kapat)
        
        dialog.exec_()

    def stok_disari_aktar(self):
        yol, _ = QFileDialog.getSaveFileName(self, "Excel Çıktısı Kaydet", "", "CSV Dosyaları (*.csv)")
        if yol:
            import csv
            try:
                with open(yol, mode='w', newline='', encoding='utf-8-sig') as f:
                    yazici = csv.writer(f, delimiter=';')
                    yazici.writerow(["ID", "Tür", "Ürün", "Kategori", "Stok", "Fiyat (TL)", "Tedarikçi"])
                    urunler = self.sistem.urunler_getir()
                    for u in urunler.values():
                        yazici.writerow([
                            u.id_getir(),
                            u.tur,
                            u.ad_getir(),
                            u._kategori,
                            u.stok_getir(),
                            round(u.fiyat_getir(), 2),
                            u.tedarikci
                        ])
                QMessageBox.information(self, "Başarılı", "Stok listesi başarıyla dışarı aktarıldı!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")

    def kur_guncelle(self):
        global GLOBAL_KUR
        GLOBAL_KUR = self.in_kur.value()
        self.arayuz_guncelle()
        QMessageBox.information(self, "Bilgi", f"USD Kuru {GLOBAL_KUR} olarak güncellendi.")

    def arayuz_guncelle(self):
        t = self.tema_getir()
        urunler = self.sistem.urunler_getir()
        sepet = self.sistem.sepet_getir()
        ithalatlar = self.sistem.ithalat_siparisleri_getir()
        siparisler = self.sistem.siparisler_getir()

        kritik_sayisi = sum(1 for u in urunler.values() if u.stok_getir() < u.min_stok_getir())

        self.k_urun.lbl_d.setText(str(len(urunler)))
        self.k_stok.lbl_d.setText(str(sum(u.stok_getir() for u in urunler.values())))
        self.k_sip.lbl_d.setText(str(len(siparisler)))
        self.k_kritik.lbl_d.setText(str(kritik_sayisi))
        self.k_bekleyen.lbl_d.setText(str(len(ithalatlar)))
        
        if hasattr(self, 'in_ad') and hasattr(self, 'in_tedarikci'):
            mevcut_ad = self.in_ad.currentText()
            mevcut_ted = self.in_tedarikci.currentText()
            
            self.in_ad.blockSignals(True)
            self.in_tedarikci.blockSignals(True)
            self.in_ad.clear()
            self.in_tedarikci.clear()
            
            adlar = sorted(list(set([u.ad_getir() for u in urunler.values()])))
            tedler = sorted(list(set([u.tedarikci for u in urunler.values() if getattr(u, 'tedarikci', '') and u.tedarikci != "Bilinmiyor"])))
            
            self.in_ad.addItems([""] + adlar)
            self.in_tedarikci.addItems([""] + tedler)
            
            self.in_ad.setCurrentText(mevcut_ad)
            self.in_tedarikci.setCurrentText(mevcut_ted)
            self.in_ad.blockSignals(False)
            self.in_tedarikci.blockSignals(False)
            
        self.t_stok.setRowCount(0)
        
        toplam_sepet_tutari = sum(urunler[uid].fiyat_getir() * adet for uid, adet in sepet.items())
        if hasattr(self, 'lbl_sepet_tutar'):
            self.lbl_sepet_tutar.setText(f"Sepet Toplamı: {toplam_sepet_tutari:.2f} TL")
        
        arama_metni = ""
        if hasattr(self, 'in_arama'):
            arama_metni = self.in_arama.text().lower()
            
        for u in urunler.values():
            if arama_metni:
                if arama_metni not in u.ad_getir().lower() and arama_metni not in getattr(u, '_kategori', '').lower():
                    continue
                    
            r = self.t_stok.rowCount(); self.t_stok.insertRow(r)
            tur = getattr(u, 'tur', 'Genel')
            sepet_adet = sepet.get(u.id_getir(), 0)
            stok_gosterim = f"{u.stok_getir()}" if sepet_adet == 0 else f"{u.stok_getir()} (Sepette: {sepet_adet})"
            
            items = [str(u.id_getir()), tur, u.ad_getir(), stok_gosterim, f"{u.fiyat_getir():.2f} TL"]
            kritik_mi = u.stok_getir() < u.min_stok_getir()
            for i, text in enumerate(items):
                item = QTableWidgetItem(text)
                if kritik_mi:
                    item.setForeground(QColor(t['tehlike']))
                    renk = QColor(t['tehlike'])
                    renk.setAlpha(30)
                    item.setBackground(renk)
                else:
                    item.setForeground(QColor(t['metin']))
                self.t_stok.setItem(r, i, item)
            stok_widget = QWidget()
            stok_layout = QHBoxLayout(stok_widget)
            stok_layout.setContentsMargins(4, 2, 4, 2)
            
            btn_azalt = QPushButton("-")
            btn_azalt.setStyleSheet(self.buton_stili('tehlike'))
            btn_azalt.clicked.connect(lambda ch, id=u.id_getir(): self.stok_degistir(id, -1))
            
            btn_arttir = QPushButton("+")
            btn_arttir.setStyleSheet(self.buton_stili('vurgu'))
            btn_arttir.clicked.connect(lambda ch, id=u.id_getir(): self.stok_degistir(id, 1))
            
            stok_layout.addWidget(btn_azalt)
            stok_layout.addWidget(btn_arttir)
            self.t_stok.setCellWidget(r, 5, stok_widget)

            btn = QPushButton("SEPETE EKLE")
            btn.setStyleSheet(self.buton_stili('vurgu'))
            btn.clicked.connect(lambda ch, id=u.id_getir(): self.is_satis(id))
            self.t_stok.setCellWidget(r, 6, btn)

            islem_widget = QWidget()
            islem_layout = QHBoxLayout(islem_widget)
            islem_layout.setContentsMargins(4, 2, 4, 2)
            
            btn_gecmis = QPushButton("ℹ️")
            btn_gecmis.setToolTip("Hareket Geçmişi")
            btn_gecmis.setStyleSheet(self.buton_stili('basari'))
            btn_gecmis.clicked.connect(lambda ch, id=u.id_getir(): self.urun_gecmis_gui(id))

            btn_duzenle = QPushButton("✏️")
            btn_duzenle.setToolTip("Ürünü Düzenle")
            btn_duzenle.setStyleSheet(self.buton_stili('vurgu'))
            btn_duzenle.clicked.connect(lambda ch, id=u.id_getir(): self.urun_duzenle_gui(id))
            
            btn_sil = QPushButton("🗑️")
            btn_sil.setToolTip("Ürünü Sil")
            btn_sil.setStyleSheet(self.buton_stili('tehlike'))
            btn_sil.clicked.connect(lambda ch, id=u.id_getir(): self.urun_sil_gui(id))
            
            islem_layout.addWidget(btn_gecmis)
            islem_layout.addWidget(btn_duzenle)
            islem_layout.addWidget(btn_sil)
            self.t_stok.setCellWidget(r, 7, islem_widget)
            
        self.t_son.setRowCount(0)
        for s in siparisler[-5:]:
            r = self.t_son.rowCount(); self.t_son.insertRow(r)
            for i, text in enumerate([s._s_id, s._urun_ad, f"{s._toplam:.2f} TL"]):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(t['metin']))
                self.t_son.setItem(r, i, item)
                
        self.t_tum_siparisler.setRowCount(0)
        for s in reversed(siparisler):
            r = self.t_tum_siparisler.rowCount(); self.t_tum_siparisler.insertRow(r)
            durum = s.durum_getir()
            items = [s._s_id, s._urun_ad, str(s._adet), f"{s._toplam:.2f} TL", s._zaman, durum]
            for i, text in enumerate(items):
                item = QTableWidgetItem(text)
                if i == 5:
                    if durum == "Tamamlandı":
                        item.setForeground(QColor(t['basari']))
                    elif durum == "Kargoda":
                        item.setForeground(QColor(t['vurgu']))
                    else:
                        item.setForeground(QColor(t['metin_gri']))
                else:
                    item.setForeground(QColor(t['metin']))
                self.t_tum_siparisler.setItem(r, i, item)
                
            btn_durum = QPushButton("DURUM İLERLET")
            if durum == "Tamamlandı":
                btn_durum.setEnabled(False)
                btn_durum.setStyleSheet(f"background:{t['metin_gri']}; color:{t['kart']}; font-weight:bold; border-radius:4px; padding:8px 15px;")
            else:
                btn_durum.setStyleSheet(self.buton_stili('vurgu'))
            btn_durum.clicked.connect(lambda ch, sip=s: self.siparis_durumu_degistir(sip))
            self.t_tum_siparisler.setCellWidget(r, 6, btn_durum)
                
        self.t_ithal.setRowCount(0)
        for imp in ithalatlar:
            r = self.t_ithal.rowCount(); self.t_ithal.insertRow(r)
            for i, text in enumerate([imp['s_id'], imp['urun_ad'], str(imp['adet']), imp.get('tedarikci', '-'), imp.get('sure', '-'), imp['tarih']]):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(t['metin']))
                self.t_ithal.setItem(r, i, item)
            
            btn_teslim = QPushButton("TESLİM AL")
            btn_teslim.setStyleSheet(self.buton_stili('basari'))
            btn_teslim.clicked.connect(lambda ch, s_id=imp['s_id']: self.ithalat_tamamla_gui(s_id))
            self.t_ithal.setCellWidget(r, 6, btn_teslim)

    def ornek_veriler(self):
        if len(self.sistem.urunler_getir()) > 0:
            return # Zaten DB dolu

        urun_listesi = [
            (101, "Logitech G Pro Mouse", "Çevre Birimi", 25, 60, "İthal", "LogiTech Global"),
            (102, "Asus ROG 27' Monitör", "Ekran", 8, 250, "İthal", "Asus Taiwan"),
            (103, "Razer BlackWidow Klavye", "Çevre Birimi", 15, 120, "İthal", "Razer Inc"),
            (104, "Samsung 980 Pro 1TB M.2", "Depolama", 12, 90, "İthal", "Samsung Korea"),
            (105, "Corsair HS80 Kulaklık", "Ses", 9, 130, "İthal", "Corsair US"),
            (106, "Nvidia RTX 4070 Ekran Kartı", "Bileşen", 5, 600, "İthal", "Nvidia Corp"),
            (107, "Intel Core i7 13700K", "İşlemci", 11, 400, "İthal", "Intel Global"),
            (108, "Elgato Stream Deck", "Aksesuar", 7, 150, "İthal", "Elgato Systems"),
            (109, "Masaüstü Kasa", "Bileşen", 30, 1500, "Yerli", ""),
            (110, "Ofis Monitörü", "Ekran", 40, 2500, "Yerli", "")
        ]

        for u in urun_listesi:
            if u[5] == "Yerli":
                self.sistem.urun_kaydet(YerliUrun(u[0], u[1], u[2], u[3], u[4]), "Sistem Kurulumu", u[3])
            else:
                self.sistem.urun_kaydet(IthalUrun(u[0], u[1], u[2], u[3], u[4], u[6]), "Sistem Kurulumu", u[3])

        self.sistem.satis_yap(105, 1)
        self.sistem.satis_yap(102, 1)
        self.sistem.satis_yap(106, 1)
        self.sistem.satis_yap(108, 1)
        self.sistem.satis_yap(109, 25)
        
        from datetime import timedelta
        siparisler = self.sistem.siparisler_getir()
        if len(siparisler) >= 2:
            for s in siparisler[:2]:
                s._dt = datetime.now() - timedelta(minutes=10)
                s._durum = "Tamamlandı"
                s._zaman = s._dt.strftime("%d/%m/%Y %H:%M")
                self.sistem.siparis_durumunu_guncelle(s)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pencere = DepoUygulamasi()
    pencere.show()
    sys.exit(app.exec_())