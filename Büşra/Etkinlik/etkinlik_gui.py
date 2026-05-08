import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
    QAbstractItemView, QMessageBox, QComboBox, QStackedWidget, QListWidget,
    QHeaderView, QFileDialog, QListWidgetItem, QSpinBox, QDialog, QGridLayout, QScrollArea
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from etkinlik_sistemleri import EtkinlikBackend

# --- PROFESYONEL STİL SÖZLÜĞÜ ---
STIL = {
    "arka_plan": "#121212",
    "yan_panel": "#181818",
    "kart": "#1E1E1E",
    "yazi": "#FFFFFF",
    "vurgu_sari": "#FFD700",
    "kenar": "#333333",
    "arama_bg": "#252D42",
    "input_bg": "#2A2A2A",
    "p_toplam": "#FFFFFF",
    "p_aktif": "#4CAF50",
    "p_gelecek": "#2196F3",
    "p_tukenmis": "#F44336",
    "p_mevcut": "#FFD700",
    "yazi_gri": "#AAAAAA",
    "kaydet_yesil": "#27AE60",
    "sil_kirmizi": "#C0392B",
    "guncelle_mavi": "#2980B9"
}

SEHIRLER = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", 
    "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", 
    "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", 
    "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir", 
    "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", 
    "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş", 
    "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", 
    "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
]

def combo_stil():
    return f"background: {STIL['input_bg']}; color: white; padding: 8px; border-radius: 5px;"

# --- YARDIMCI (UTILS) FONKSİYONLAR ---
def sure_hesapla(bas, bit):
    try:
        b_s, b_d = map(int, bas.split(':'))
        bi_s, bi_d = map(int, bit.split(':'))
        fark = (bi_s + bi_d/60) - (b_s + b_d/60)
        if fark < 0: fark += 24
        return round(fark, 1)
    except: return 2

def standart_tablo_olustur(basliklar):
    tablo = QTableWidget(0, len(basliklar))
    tablo.setHorizontalHeaderLabels(basliklar)
    tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    tablo.verticalHeader().setVisible(False)
    tablo.setSelectionBehavior(QTableWidget.SelectRows)
    tablo.setStyleSheet(f"QTableWidget {{ background-color: {STIL['kart']}; color: white; border: 1px solid {STIL['kenar']}; border-radius: 10px; gridline-color: #333; }} QHeaderView::section {{ background-color: #1A1F2B; color: {STIL['vurgu_sari']}; padding: 8px; font-weight: bold; border: none; border-bottom: 1px solid {STIL['kenar']}; }}")
    return tablo

class KategoriFiltresi(QWidget):
    kategori_degisti = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.btn_layout = QHBoxLayout(self)
        self.btn_layout.setContentsMargins(0, 0, 0, 0)
        self.kategori_butonlari = []
        kategoriler = ["Hepsi", "Konser", "Tiyatro", "Sinema", "Seminer", "Eğitim"]
        for kat in kategoriler:
            btn = QPushButton(kat)
            btn.setStyleSheet(f"background-color: {STIL['kart']}; color: white; padding: 5px 15px; border-radius: 5px; border: 1px solid {STIL['kenar']}; font-weight: bold;")
            btn.setCursor(Qt.PointingHandCursor)
            self.kategori_butonlari.append(btn)
            btn.clicked.connect(lambda checked, k=kat: self.kategori_sec(k))
            self.btn_layout.addWidget(btn)
        self.btn_layout.addStretch()
        
    def kategori_sec(self, kategori):
        for btn in self.kategori_butonlari:
            if btn.text() == kategori:
                btn.setStyleSheet(f"background-color: {STIL['guncelle_mavi']}; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold;")
            else:
                btn.setStyleSheet(f"background-color: {STIL['kart']}; color: white; padding: 5px 15px; border-radius: 5px; border: 1px solid {STIL['kenar']}; font-weight: bold;")
        self.kategori_degisti.emit(kategori)


# --- BİLEŞEN: ANALİZ KARTI ---
class AnalizKarti(QFrame):
    def __init__(self, ikon, baslik, renk):
        super().__init__()
        self.setFixedSize(170, 120)
        self.setStyleSheet(f"background-color: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 15px;")
        layout = QVBoxLayout(self)
        
        lbl_ikon = QLabel(ikon); lbl_ikon.setStyleSheet("font-size: 26px; border: none; background: transparent;")
        lbl_ikon.setAlignment(Qt.AlignCenter)
        
        lbl_baslik = QLabel(baslik); lbl_baslik.setStyleSheet("color: #AAAAAA; font-size: 10px; font-weight: bold; border: none;")
        lbl_baslik.setAlignment(Qt.AlignCenter)
        
        self.lbl_deger = QLabel("0")
        self.lbl_deger.setStyleSheet(f"color: {renk}; font-size: 24px; font-weight: bold; border: none;")
        self.lbl_deger.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(lbl_ikon)
        layout.addWidget(lbl_baslik)
        layout.addWidget(self.lbl_deger)

    def degeri_guncelle(self, yeni_deger):
        self.lbl_deger.setText(str(yeni_deger))

# --- 1. SAYFA: ANALİZ DASHBOARD ---
class AnalizSayfasi(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        layout.addWidget(QLabel("📊 Etkinlik ve Bilet Analiz Dashboard", 
                                styleSheet=f"color: {STIL['vurgu_sari']}; font-size: 24px; font-weight: 800;"))
        
        self.kart_layout = QHBoxLayout()
        self.k_toplam = AnalizKarti("📁", "TOPLAM", STIL['p_toplam'])
        self.k_aktif = AnalizKarti("⚡", "AKTİF", STIL['p_aktif'])
        self.k_gelecek = AnalizKarti("⏳", "GELECEK", STIL['p_gelecek'])
        self.k_tukenmis = AnalizKarti("🚫", "TÜKENMİŞ", STIL['p_tukenmis'])
        self.k_satis = AnalizKarti("🎟️", "SATIŞTA", STIL['p_mevcut'])
        
        for k in [self.k_toplam, self.k_aktif, self.k_gelecek, self.k_tukenmis, self.k_satis]:
            self.kart_layout.addWidget(k)
        layout.addLayout(self.kart_layout)
        
        self.kategori_filtresi = KategoriFiltresi()
        self.kategori_filtresi.kategori_degisti.connect(self.kategori_filtrele)
        layout.addWidget(self.kategori_filtresi)

        self.tablo = standart_tablo_olustur(["TÜR", "AD", "MEKAN", "TARİH", "SAAT", "DOLULUK", "FİYAT", "DURUM"])
        layout.addWidget(self.tablo)

        self.tum_veriler = []
        self.aktif_kategori = "Hepsi"

    def kategori_filtrele(self, kategori):
        self.aktif_kategori = kategori
        self.tabloyu_guncelle()

    def verileri_yansit(self, veriler):
        self.tum_veriler = veriler
        self.kategori_filtrele("Hepsi")

    def tabloyu_guncelle(self):
        veriler = self.tum_veriler
        t, a, g, tu, s = len(veriler), 0, 0, 0, 0
        
        for e in veriler:
            durum = e['durum']
            if durum == "Aktif": a += 1
            elif durum == "Gelecek Etkinlik": g += 1
            elif durum == "Bileti Tükenmiş": tu += 1
            if e['satilan'] < e['toplam'] and durum != "Gelecek Etkinlik": s += 1

        self.k_toplam.degeri_guncelle(t); self.k_aktif.degeri_guncelle(a)
        self.k_gelecek.degeri_guncelle(g); self.k_tukenmis.degeri_guncelle(tu)
        self.k_satis.degeri_guncelle(s)

        if self.aktif_kategori == "Hepsi":
            gosterilecek = veriler
        else:
            gosterilecek = [e for e in veriler if e.get('tur', '') == self.aktif_kategori]

        self.tablo.setRowCount(len(gosterilecek))
        for r, e in enumerate(gosterilecek):
            durum = e['durum']
            saat = f"{e.get('bas', '--:--')} - {e.get('bit', '--:--')}"
            fiyat = e.get('fiyat', 'Ücretsiz')

            vals = [e['tur'], e['ad'], e['mekan'], e['tarih'], saat, f"{e['satilan']}/{e['toplam']}", fiyat, durum]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                
                if durum == "Gelecek Etkinlik":
                    item.setForeground(Qt.gray)
                elif durum == "Bileti Tükenmiş":
                    item.setForeground(Qt.red)
                
                self.tablo.setItem(r, c, item)

# --- 2. SAYFA: YÖNETİM SAYFASI (Katılımcı İzleme) ---
class YonetimSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        layout.addWidget(QLabel("🔍 Katılımcı ve Etkinlik İzleme", styleSheet=f"color: {STIL['vurgu_sari']}; font-weight: bold; font-size: 18px;"))
        self.arama = QLineEdit()
        self.arama.setPlaceholderText("Etkinlik ara...")
        self.arama.setStyleSheet(f"background: {STIL['arama_bg']}; color: white; padding: 10px; border-radius: 8px;")
        self.arama.textChanged.connect(self.etkinlik_filtrele)
        layout.addWidget(self.arama)

        # Kategori Butonları
        self.kategori_filtresi = KategoriFiltresi()
        self.kategori_filtresi.kategori_degisti.connect(self.kategori_sec)
        layout.addWidget(self.kategori_filtresi)

        self.etk_tablo = standart_tablo_olustur(["ID", "AD", "MEKAN", "TARİH", "BİLET", "DURUM"])
        self.etk_tablo.cellClicked.connect(self.etkinlik_tiklandi)
        layout.addWidget(self.etk_tablo)

        layout.addWidget(QFrame(frameShape=QFrame.HLine, styleSheet=f"background: {STIL['kenar']}; margin: 15px 0;"))

        self.lbl_kat_baslik = QLabel("👥 Kayıtlı Katılımcılar")
        self.lbl_kat_baslik.setStyleSheet(f"color: {STIL['vurgu_sari']}; font-weight: bold;")
        layout.addWidget(self.lbl_kat_baslik)

        # Katılımcı Arama Çubuğu
        self.kat_arama = QLineEdit()
        self.kat_arama.setPlaceholderText("Katılımcı isim veya e-posta ile ara...")
        self.kat_arama.setStyleSheet(f"background: {STIL['arama_bg']}; color: white; padding: 8px; border-radius: 8px; margin-bottom: 5px;")
        self.kat_arama.textChanged.connect(self.katilimci_ara)
        layout.addWidget(self.kat_arama)

        self.kat_tablo = standart_tablo_olustur(["BİLET ID", "AD SOYAD", "E-POSTA", "SAHNE/KOLTUK", "ADET", "ÖDENEN"])
        layout.addWidget(self.kat_tablo)

        self.aktif_kategori = "Hepsi"
        self.tum_etkinlikler = []
        self.aktif_katilimcilar = []

    def kategori_sec(self, kategori):
        self.aktif_kategori = kategori
        self.etkinlik_filtrele()

    def verileri_yansit(self, veriler):
        self.tum_etkinlikler = [e for e in veriler if e['durum'] != "Gelecek Etkinlik"]
        self.etkinlik_filtrele()

    def etkinlik_filtrele(self):
        txt = self.arama.text().lower()
        if self.aktif_kategori == "Hepsi":
            filtrelenmis = [e for e in self.tum_etkinlikler if txt in e['ad'].lower() or txt in e['mekan'].lower()]
        else:
            filtrelenmis = [e for e in self.tum_etkinlikler if e.get('tur') == self.aktif_kategori and (txt in e['ad'].lower() or txt in e['mekan'].lower())]
            
        self.etk_tablo.setRowCount(len(filtrelenmis))
        for r, e in enumerate(filtrelenmis):
            v = [e['id'], e['ad'], e['mekan'], e['tarih'], f"{e['satilan']} / {e['toplam']}", e['durum']]
            for c, val in enumerate(v):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.etk_tablo.setItem(r, c, item)

    def etkinlik_tiklandi(self, r, c):
        e_id = self.etk_tablo.item(r, 0).text()
        e_ad = self.etk_tablo.item(r, 1).text()
        self.lbl_kat_baslik.setText(f"👥 {e_ad} - Katılımcı Listesi")
        self.aktif_katilimcilar = self.ana_pencere.get_katilimcilar_by_id(e_id)
        self.kat_arama.clear()
        self.katilimcilari_goster(self.aktif_katilimcilar)

    def katilimci_ara(self):
        txt = self.kat_arama.text().lower()
        filtrelenmis = [k for k in self.aktif_katilimcilar if txt in k[1].lower() or txt in k[2].lower()]
        self.katilimcilari_goster(filtrelenmis)

    def katilimcilari_goster(self, katilimcilar):
        self.kat_tablo.setRowCount(len(katilimcilar))
        for r_idx, row in enumerate(katilimcilar):
            v = [row[0], row[1], row[2], row[3] if len(row)>3 else "", row[4] if len(row)>4 else 1, row[5] if len(row)>5 else ""]
            for c_idx, val in enumerate(v):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.kat_tablo.setItem(r_idx, c_idx, item)

# --- 3. SAYFA: ETKİNLİK EKLEME SAYFASI ---
class EtkinlikEkleSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.secili_id = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        # Üst: Arama
        arama_frame = QFrame()
        arama_frame.setFixedHeight(50)
        arama_frame.setStyleSheet(f"background: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 10px;")
        arama_lay = QHBoxLayout(arama_frame)
        self.input_arama = QLineEdit()
        self.input_arama.setPlaceholderText("🔍 Etkinlik, Şehir veya ID ara...")
        self.input_arama.setStyleSheet("background: transparent; color: white; border: none; padding: 5px;")
        self.input_arama.textChanged.connect(self.etkinlik_ara)
        arama_lay.addWidget(self.input_arama)
        layout.addWidget(arama_frame)

        # Kategori Butonları
        self.kategori_filtresi = KategoriFiltresi()
        self.kategori_filtresi.kategori_degisti.connect(self.kategori_sec)
        layout.addWidget(self.kategori_filtresi)

        # Orta: Tablo (10 Sütun)
        self.tablo = standart_tablo_olustur(["ID", "TÜR", "AD", "ŞEHİR", "MEKAN", "TARİH", "SAAT", "BİLET", "FİYAT", "DURUM"])
        self.tablo.setFixedHeight(180) 
        self.tablo.cellClicked.connect(self.etkinlik_sec)
        layout.addWidget(self.tablo)

        # Alt Paneller (Kayıt & Güncelleme)
        alt_layout = QHBoxLayout()
        
        # Sol: Kayıt
        self.kayit_frame = QFrame()
        self.kayit_frame.setStyleSheet(f"background: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 15px;")
        k_lay = QVBoxLayout(self.kayit_frame)
        k_lay.setAlignment(Qt.AlignTop)
        k_lay.setSpacing(12)
        k_lay.addWidget(self.etiket("➕ YENİ ETKİNLİK TANIMLA", True))
        
        form_h_sol = QHBoxLayout()
        form_v1_sol = QVBoxLayout(); form_v2_sol = QVBoxLayout()
        
        self.k_ad = self.form_input("Etkinlik Adı:", "Örn: Konser", form_v1_sol)
        form_v1_sol.addWidget(self.etiket("Etkinlik Şehri:"))
        self.k_sehir = QComboBox(); self.k_sehir.addItems(SEHIRLER); self.k_sehir.setStyleSheet(combo_stil()); form_v1_sol.addWidget(self.k_sehir)
        self.k_mekan = self.form_input("Mekan Detayı:", "Ataköy", form_v1_sol)
        self.k_tarih = self.form_input("Tarih:", "GG.AA.YYYY", form_v1_sol)
        self.k_tarih.textChanged.connect(self.tarih_formati)
        self.k_tarih.setMaxLength(10)
        
        form_v2_sol.addWidget(self.etiket("Saat (Baş/Bit):"))
        saat_h = QHBoxLayout()
        self.k_saat_bas = QLineEdit(); self.k_saat_bas.setPlaceholderText("00:00")
        self.k_saat_bit = QLineEdit(); self.k_saat_bit.setPlaceholderText("00:00")
        for s in [self.k_saat_bas, self.k_saat_bit]:
            s.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 10px; border-radius: 5px;")
            s.textChanged.connect(lambda text, obj=s: self.saat_formati(text, obj))
            saat_h.addWidget(s)
        form_v2_sol.addLayout(saat_h)
        
        self.k_kapasite = self.form_input("Kapasite:", "Sadece Rakam", form_v2_sol)
        self.k_kapasite.setValidator(QIntValidator())
        
        self.k_fiyat = self.form_input("Fiyat:", "Sadece Rakam (TL)", form_v2_sol)
        self.k_fiyat.setValidator(QIntValidator())
        
        k_tur_durum_h = QHBoxLayout()
        k_tur_v = QVBoxLayout()
        k_tur_v.addWidget(self.etiket("Kategori:"))
        self.k_tur = QComboBox(); self.k_tur.addItems(["Konser", "Tiyatro", "Sinema", "Seminer", "Eğitim"]); self.k_tur.setStyleSheet(combo_stil()); k_tur_v.addWidget(self.k_tur)
        
        k_durum_v = QVBoxLayout()
        k_durum_v.addWidget(self.etiket("Durum:"))
        self.k_durum = QComboBox(); self.k_durum.addItems(["Aktif", "Gelecek Etkinlik", "Bileti Tükenmiş"]); self.k_durum.setStyleSheet(combo_stil()); k_durum_v.addWidget(self.k_durum)
        
        k_tur_durum_h.addLayout(k_tur_v); k_tur_durum_h.addLayout(k_durum_v)
        form_v2_sol.addLayout(k_tur_durum_h)
        
        form_h_sol.addLayout(form_v1_sol); form_h_sol.addLayout(form_v2_sol)
        k_lay.addLayout(form_h_sol)
        k_lay.addStretch()
        
        self.btn_kaydet = QPushButton("SİSTEME KAYDET")
        self.btn_kaydet.setStyleSheet(f"background: {STIL['kaydet_yesil']}; color: white; font-weight: bold; padding: 12px;")
        self.btn_kaydet.clicked.connect(self.yeni_kayit_ekle)
        k_lay.addWidget(self.btn_kaydet)

        # Sağ: Güncelleme (Birebir Aynı Yapı)
        self.yonetim_frame = QFrame()
        self.yonetim_frame.setStyleSheet(f"background: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 15px;")
        y_lay = QVBoxLayout(self.yonetim_frame)
        y_lay.setAlignment(Qt.AlignTop)
        y_lay.setSpacing(12)
        y_lay.addWidget(self.etiket("⚙️ DÜZENLEME PANELİ", True))
        
        form_h_sag = QHBoxLayout()
        form_v1_sag = QVBoxLayout(); form_v2_sag = QVBoxLayout()
        
        self.g_ad = self.form_input("Güncelle Ad:", "", form_v1_sag)
        form_v1_sag.addWidget(self.etiket("Şehir:"))
        self.g_sehir = QComboBox(); self.g_sehir.addItems(SEHIRLER); self.g_sehir.setStyleSheet(combo_stil()); form_v1_sag.addWidget(self.g_sehir)
        self.g_mekan = self.form_input("Mekan Güncelle:", "", form_v1_sag)
        self.g_tarih = self.form_input("Tarih Güncelle:", "GG.AA.YYYY", form_v1_sag)
        self.g_tarih.textChanged.connect(self.tarih_formati_sag)
        self.g_tarih.setMaxLength(10)

        form_v2_sag.addWidget(self.etiket("Saat (Baş/Bit):"))
        saat_h_sag = QHBoxLayout()
        self.g_saat_bas = QLineEdit(); self.g_saat_bas.setPlaceholderText("00:00")
        self.g_saat_bit = QLineEdit(); self.g_saat_bit.setPlaceholderText("00:00")
        for s in [self.g_saat_bas, self.g_saat_bit]:
            s.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 10px; border-radius: 5px;")
            s.textChanged.connect(lambda text, obj=s: self.saat_formati(text, obj))
            saat_h_sag.addWidget(s)
        form_v2_sag.addLayout(saat_h_sag)
        
        self.g_kapasite = self.form_input("Kapasite:", "Sadece Rakam", form_v2_sag)
        self.g_kapasite.setValidator(QIntValidator())
        
        self.g_fiyat = self.form_input("Fiyat:", "Sadece Rakam (TL)", form_v2_sag)
        self.g_fiyat.setValidator(QIntValidator())
        
        tur_durum_h = QHBoxLayout()
        tur_v = QVBoxLayout()
        tur_v.addWidget(self.etiket("Kategori:"))
        self.g_tur = QComboBox(); self.g_tur.addItems(["Konser", "Tiyatro", "Sinema", "Seminer", "Eğitim"]); self.g_tur.setStyleSheet(combo_stil()); tur_v.addWidget(self.g_tur)
        
        durum_v = QVBoxLayout()
        durum_v.addWidget(self.etiket("Durum:"))
        self.g_durum = QComboBox(); self.g_durum.addItems(["Aktif", "Gelecek Etkinlik", "Bileti Tükenmiş"]); self.g_durum.setStyleSheet(combo_stil()); durum_v.addWidget(self.g_durum)
        
        tur_durum_h.addLayout(tur_v); tur_durum_h.addLayout(durum_v)
        form_v2_sag.addLayout(tur_durum_h)
        
        form_h_sag.addLayout(form_v1_sag); form_h_sag.addLayout(form_v2_sag)
        y_lay.addLayout(form_h_sag)
        y_lay.addStretch()
        
        btn_h = QHBoxLayout()
        self.btn_guncelle = QPushButton("GÜNCELLE"); self.btn_guncelle.setStyleSheet(f"background: {STIL['guncelle_mavi']}; color: white; font-weight: bold; padding: 12px;")
        self.btn_sil = QPushButton("SİL"); self.btn_sil.setStyleSheet(f"background: {STIL['sil_kirmizi']}; color: white; font-weight: bold; padding: 12px;")
        self.btn_guncelle.clicked.connect(self.etkinlik_guncelle)
        self.btn_sil.clicked.connect(self.etkinlik_sil)
        btn_h.addWidget(self.btn_guncelle); btn_h.addWidget(self.btn_sil)
        y_lay.addLayout(btn_h)

        alt_layout.addWidget(self.kayit_frame)
        alt_layout.addWidget(self.yonetim_frame)
        layout.addLayout(alt_layout)
        
        self.aktif_kategori = "Hepsi"

    def etiket(self, metin, baslik=False):
        lbl = QLabel(metin); lbl.setStyleSheet(f"color: {STIL['vurgu_sari'] if baslik else STIL['yazi_gri']}; font-weight: {'bold' if baslik else 'normal'}; border:none;")
        if baslik: lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def form_input(self, etiket_adi, placeholder, layout):
        layout.addWidget(self.etiket(etiket_adi))
        inp = QLineEdit(); inp.setPlaceholderText(placeholder)
        inp.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(inp)
        return inp

    def kategori_sec(self, kategori):
        self.aktif_kategori = kategori
        self.etkinlik_ara()

    def tarih_formati(self, text):
        self.k_tarih.blockSignals(True)
        digits = "".join(filter(str.isdigit, text))[:8]
        gun = digits[:2]; ay = digits[2:4]; yil = digits[4:8]
        if gun and int(gun) > 31: gun = "31"
        if gun and gun == "00": gun = "01"
        if ay and int(ay) > 12: ay = "12"
        if ay and ay == "00": ay = "01"
        new_digits = gun + ay + yil
        formatted = ""
        for i, char in enumerate(new_digits):
            if i == 2 or i == 4: formatted += "."
            formatted += char
        self.k_tarih.setText(formatted)
        self.k_tarih.setCursorPosition(len(formatted))
        self.k_tarih.blockSignals(False)
        
    def tarih_formati_sag(self, text):
        self.g_tarih.blockSignals(True)
        digits = "".join(filter(str.isdigit, text))[:8]
        gun = digits[:2]; ay = digits[2:4]; yil = digits[4:8]
        if gun and int(gun) > 31: gun = "31"
        if gun and gun == "00": gun = "01"
        if ay and int(ay) > 12: ay = "12"
        if ay and ay == "00": ay = "01"
        new_digits = gun + ay + yil
        formatted = ""
        for i, char in enumerate(new_digits):
            if i == 2 or i == 4: formatted += "."
            formatted += char
        self.g_tarih.setText(formatted)
        self.g_tarih.setCursorPosition(len(formatted))
        self.g_tarih.blockSignals(False)

    def saat_formati(self, text, obj):
        obj.blockSignals(True)
        digits = "".join(filter(str.isdigit, text))[:4]
        saat = digits[:2]; dakika = digits[2:4]
        if saat and int(saat) > 24: saat = "23"
        if dakika and int(dakika) > 60: dakika = "59"
        new_digits = saat + dakika
        formatted = ""
        for i, char in enumerate(new_digits):
            if i == 2: formatted += ":"
            formatted += char
        obj.setText(formatted)
        obj.setCursorPosition(len(formatted))
        obj.blockSignals(False)

    def tabloyu_doldur(self, veriler):
        self.tablo.setRowCount(len(veriler))
        for r, e in enumerate(veriler):
            saat = f"{e.get('bas', '--:--')} - {e.get('bit', '--:--')}"
            bilet_durumu = f"{e['satilan']} / {e['toplam']}"
            fiyat = str(e.get('fiyat', 'Ücretsiz')).replace(' TL', '') + " TL"
            v_list = [e['id'], e['tur'], e['ad'], e['sehir'], e['mekan'], e['tarih'], saat, bilet_durumu, fiyat, e['durum']]
            for c, val in enumerate(v_list):
                item = QTableWidgetItem(str(val)); item.setTextAlignment(Qt.AlignCenter)
                self.tablo.setItem(r, c, item)

    def etkinlik_ara(self):
        txt = self.input_arama.text().lower()
        if self.aktif_kategori == "Hepsi":
            filtre = [e for e in self.ana_pencere.ana_veriler if txt in e['ad'].lower() or txt in e['sehir'].lower()]
        else:
            filtre = [e for e in self.ana_pencere.ana_veriler if e.get('tur') == self.aktif_kategori and (txt in e['ad'].lower() or txt in e['sehir'].lower())]
        self.tabloyu_doldur(filtre)

    def etkinlik_sec(self, r, c):
        self.secili_id = self.tablo.item(r, 0).text()
        for e in self.ana_pencere.ana_veriler:
            if e['id'] == self.secili_id:
                self.g_ad.setText(e['ad'])
                self.g_sehir.setCurrentText(e.get('sehir', 'İstanbul'))
                self.g_mekan.setText(e['mekan'])
                self.g_tarih.setText(e['tarih'])
                self.g_saat_bas.setText(e.get('bas', ''))
                self.g_saat_bit.setText(e.get('bit', ''))
                self.g_kapasite.setText(str(e['toplam']))
                fiyat_str = str(e.get('fiyat', '150'))
                fiyat_num = ''.join(filter(str.isdigit, fiyat_str))
                self.g_fiyat.setText(fiyat_num)
                self.g_tur.setCurrentText(e.get('tur', 'Konser'))
                self.g_durum.setCurrentText(e['durum'])

    def yeni_kayit_ekle(self):
        if not self.k_kapasite.text() or not self.k_fiyat.text() or not self.k_ad.text():
            QMessageBox.warning(self, "Hata", "Lütfen gerekli alanları doldurun (Ad, Kapasite, Fiyat).")
            return
            
        try:
            fiyat = f"{self.k_fiyat.text()} TL"
            yeni = {"id": self.ana_pencere.yeni_id_uret(), "tur": self.k_tur.currentText(), "ad": self.k_ad.text(), 
                    "sehir": self.k_sehir.currentText(), "mekan": self.k_mekan.text(), "tarih": self.k_tarih.text(), 
                    "bas": self.k_saat_bas.text(), "bit": self.k_saat_bit.text(), "satilan": 0, 
                    "toplam": int(self.k_kapasite.text()), "fiyat": fiyat, "durum": self.k_durum.currentText()}
            
            # Backend üzerinden ekle
            self.ana_pencere.backend.etkinlik_ekle(yeni)
            
            self.etkinlik_ara()
            self.ana_pencere.verileri_senkronize_et()
            QMessageBox.information(self, "Başarılı", f"{yeni['ad']} kaydedildi!")
            
            # Formu temizle
            self.k_ad.clear(); self.k_mekan.clear(); self.k_tarih.clear()
            self.k_saat_bas.clear(); self.k_saat_bit.clear(); self.k_kapasite.clear(); self.k_fiyat.clear()
        except Exception as e: QMessageBox.warning(self, "Hata", f"Hata oluştu: {str(e)}")


    def etkinlik_guncelle(self):
        if not self.secili_id: return
        if not self.g_kapasite.text() or not self.g_fiyat.text() or not self.g_ad.text():
            QMessageBox.warning(self, "Hata", "Ad, Kapasite ve Fiyat boş olamaz.")
            return
            
        guncel_veri = {
            'ad': self.g_ad.text(),
            'sehir': self.g_sehir.currentText(),
            'mekan': self.g_mekan.text(),
            'tarih': self.g_tarih.text(),
            'bas': self.g_saat_bas.text(),
            'bit': self.g_saat_bit.text(),
            'toplam': int(self.g_kapasite.text()),
            'fiyat': f"{self.g_fiyat.text()} TL",
            'tur': self.g_tur.currentText(),
            'durum': self.g_durum.currentText()
        }
        
        # Backend üzerinden güncelle
        self.ana_pencere.backend.etkinlik_guncelle(self.secili_id, guncel_veri)
        
        self.etkinlik_ara()
        self.ana_pencere.verileri_senkronize_et()
        QMessageBox.information(self, "Başarılı", "Etkinlik başarıyla güncellendi!")


    def etkinlik_sil(self):
        if not self.secili_id: return
        if QMessageBox.question(self, "Onay", "Silinsin mi?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            # Backend üzerinden sil
            self.ana_pencere.backend.etkinlik_sil(self.secili_id)
            
            self.secili_id = None
            self.g_ad.clear(); self.g_mekan.clear(); self.g_tarih.clear(); self.g_kapasite.clear(); self.g_fiyat.clear()
            self.etkinlik_ara()
            self.ana_pencere.verileri_senkronize_et()

    
class ModernKoltukSecmeDialog(QDialog):
    def __init__(self, parent, etkinlik, bilet_adedi, dolu_koltuklar, mevcut_secili=None):
        super().__init__(parent)
        self.etkinlik = etkinlik
        self.bilet_adedi = bilet_adedi
        self.dolu_koltuklar = dolu_koltuklar
        self.secilen_koltuklar = list(mevcut_secili) if mevcut_secili else []
        self.butonlar = {}
        
        self.setWindowTitle(f"Koltuk Seçimi - {etkinlik['ad']}")
        self.setMinimumSize(800, 700)
        self.setStyleSheet(f"background-color: {STIL['arka_plan']}; color: white;")
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. SAHNE GÖRSELİ
        sahne_frame = QFrame()
        sahne_frame.setFixedHeight(60)
        sahne_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333, stop:1 #111);
            border: 2px solid gold;
            border-bottom-left-radius: 50px;
            border-bottom-right-radius: 50px;
        """)
        sahne_lay = QVBoxLayout(sahne_frame)
        lbl_sahne = QLabel("S A H N E")
        lbl_sahne.setStyleSheet("color: gold; font-size: 24px; font-weight: bold; border: none; background: transparent;")
        lbl_sahne.setAlignment(Qt.AlignCenter)
        sahne_lay.addWidget(lbl_sahne)
        main_layout.addWidget(sahne_frame)
        
        # 2. BİLGİ PANELİ (Fiyatlar ve Renkler)
        bilgi_lay = QHBoxLayout()
        bilgi_lay.setContentsMargins(0, 15, 0, 15)
        
        legend_items = [
            ("Boş", "#444"),
            ("Seçili", "gold"),
            ("Dolu", "#C0392B"),
            ("Ön (+100 TL)", "#27AE60"),
            ("Orta (Standart)", "#2980B9"),
            ("Arka (-50 TL)", "#7F8C8D")
        ]
        
        for text, color in legend_items:
            dot = QLabel(); dot.setFixedSize(16, 16)
            dot.setStyleSheet(f"background: {color}; border-radius: 8px; border: 1px solid #555;")
            lbl = QLabel(text); lbl.setStyleSheet("font-size: 11px; color: #AAA;")
            bilgi_lay.addWidget(dot); bilgi_lay.addWidget(lbl)
            bilgi_lay.addSpacing(10)
            
        bilgi_lay.addStretch()
        
        self.lbl_secim_bilgi = QLabel(f"Seçilen: 0 / {self.bilet_adedi}")
        self.lbl_secim_bilgi.setStyleSheet(f"color: {STIL['vurgu_sari']}; font-weight: bold; font-size: 14px;")
        bilgi_lay.addWidget(self.lbl_secim_bilgi)
        
        main_layout.addLayout(bilgi_lay)
        
        # 3. KOLTUK IZGARASI (Scroll Area içinde)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(8)
        self.grid.setContentsMargins(20, 20, 20, 20)
        
        self.koltuklari_olustur()
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # 4. ALT PANEL (Tutar ve Onay)
        alt_lay = QHBoxLayout()
        alt_lay.setContentsMargins(0, 15, 0, 0)
        
        self.lbl_ek_ucret = QLabel("Ek Ücret: 0 TL")
        self.lbl_ek_ucret.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        alt_lay.addWidget(self.lbl_ek_ucret)
        
        alt_lay.addStretch()
        
        btn_iptal = QPushButton("İPTAL")
        btn_iptal.setFixedSize(120, 45)
        btn_iptal.setStyleSheet(f"background: #444; color: white; font-weight: bold; border-radius: 8px;")
        btn_iptal.clicked.connect(self.reject)
        
        self.btn_onay = QPushButton("SEÇİMİ ONAYLA")
        self.btn_onay.setFixedSize(200, 45)
        self.btn_onay.setStyleSheet(f"background: {STIL['kaydet_yesil']}; color: white; font-weight: bold; border-radius: 8px;")
        self.btn_onay.clicked.connect(self.onayla)
        
        alt_lay.addWidget(btn_iptal)
        alt_lay.addWidget(self.btn_onay)
        main_layout.addLayout(alt_lay)
        
        self.arayuz_guncelle()

    def koltuklari_olustur(self):
        harfler = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']
        kapasite = self.etkinlik['toplam']
        cols = 10
        rows = (kapasite // cols) + (1 if kapasite % cols > 0 else 0)
        
        for r in range(rows):
            harf = harfler[r] if r < len(harfler) else f"R{r}"
            # Satır etiketi
            lbl_row = QLabel(harf)
            lbl_row.setStyleSheet("color: #777; font-weight: bold; font-size: 14px;")
            self.grid.addWidget(lbl_row, r, 0)
            
            for c in range(1, cols + 1):
                k_no = f"{harf}{c}"
                if (r * cols + (c-1)) >= kapasite: break
                
                btn = QPushButton(str(c))
                btn.setCheckable(True)
                btn.setFixedSize(40, 40)
                btn.setCursor(Qt.PointingHandCursor)
                
                # Bölüm belirleme
                if r < 3: section = "ON"
                elif r < 6: section = "ORTA"
                else: section = "ARKA"
                
                if k_no in self.dolu_koltuklar:
                    btn.setEnabled(False)
                    btn.setStyleSheet("background: #C0392B; color: #444; border: none; border-radius: 5px;")
                    btn.setToolTip("Dolu")
                else:
                    if section == "ON": color = "#27AE60"
                    elif section == "ORTA": color = "#2980B9"
                    else: color = "#7F8C8D"
                    
                    btn.setStyleSheet(f"""
                        QPushButton {{ background: {color}; color: white; font-weight: bold; border-radius: 5px; border: 1px solid #555; }}
                        QPushButton:hover {{ background: gold; color: black; }}
                        QPushButton:checked {{ background: gold; color: black; border: 2px solid white; }}
                    """)
                    
                    if k_no in self.secilen_koltuklar:
                        btn.setChecked(True)
                    
                    btn.clicked.connect(lambda checked, kn=k_no: self.koltuk_tiklandi(kn))
                
                self.grid.addWidget(btn, r, c)
                self.butonlar[k_no] = btn

    def koltuk_tiklandi(self, k_no):
        if self.butonlar[k_no].isChecked():
            if len(self.secilen_koltuklar) >= self.bilet_adedi:
                self.butonlar[k_no].setChecked(False)
                QMessageBox.warning(self, "Sınır", f"En fazla {self.bilet_adedi} koltuk seçebilirsiniz.")
                return
            if k_no not in self.secilen_koltuklar:
                self.secilen_koltuklar.append(k_no)
        else:
            if k_no in self.secilen_koltuklar:
                self.secilen_koltuklar.remove(k_no)
        
        self.arayuz_guncelle()

    def arayuz_guncelle(self):
        count = len(self.secilen_koltuklar)
        self.lbl_secim_bilgi.setText(f"Seçilen: {count} / {self.bilet_adedi}")
        
        # Ek ücret hesapla
        ek = 0
        for k in self.secilen_koltuklar:
            if k.startswith('R'):
                ek -= 100
            else:
                row_idx = "ABCDEFGHIJKLMNO".find(k[0])
                if row_idx != -1:
                    if row_idx < 3: ek += 100
                    elif row_idx >= 6: ek -= 50
        
        self.lbl_ek_ucret.setText(f"Ek Ücret: {ek} TL")
        
        # Onay butonunu sadece tam seçim yapıldığında aktif/vurgulu yapabiliriz
        if count == self.bilet_adedi:
            self.btn_onay.setEnabled(True)
            self.btn_onay.setAlpha = 255
        else:
            # Opsiyonel: Tam seçilmeden onaylanmasın mı? 
            # Kullanıcı bilet adedi kadar koltuk seçimi yapmalı kuralı vardı.
            pass

    def onayla(self):
        if len(self.secilen_koltuklar) != self.bilet_adedi:
            QMessageBox.warning(self, "Eksik Seçim", f"Lütfen tam {self.bilet_adedi} adet koltuk seçin.")
            return
        self.accept()



class KatilimciSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.secili_etkinlik = None
        self.secilen_koltuklar = []
        self.aktif_kategori = "Hepsi"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. ÜST: Arama ve Kategori Filtreleri
        ust_frame = QFrame()
        ust_frame.setStyleSheet(f"background: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 10px;")
        ust_lay = QVBoxLayout(ust_frame)
        
        self.arama_cubugu = QLineEdit()
        self.arama_cubugu.setPlaceholderText("🔍 Etkinlik Ara (Ad, Mekan veya Şehir)...")
        self.arama_cubugu.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 10px; border-radius: 5px; border:none;")
        self.arama_cubugu.textChanged.connect(self.etkinlik_filtrele)
        ust_lay.addWidget(self.arama_cubugu)

        self.kategori_filtresi = KategoriFiltresi()
        self.kategori_filtresi.kategori_degisti.connect(self.kategori_sec)
        ust_lay.addWidget(self.kategori_filtresi)
        
        layout.addWidget(ust_frame)

        # 2. ORTA KISIM
        orta_lay = QHBoxLayout()
        
        # SOL: TABLO
        self.tablo = standart_tablo_olustur(["AD", "ŞEHİR", "MEKAN", "SÜRE", "KALAN", "FİYAT"])
        self.tablo.cellClicked.connect(self.etkinlik_secildi)
        orta_lay.addWidget(self.tablo, 2) # 2 birim
        
        # SAĞ: KAYIT FORMU
        self.sag_kayit_panel = QFrame()
        self.sag_kayit_panel.setStyleSheet(f"background: {STIL['kart']}; border-radius: 15px; border: 1px solid {STIL['kenar']};")
        self.sag_layout = QVBoxLayout(self.sag_kayit_panel)
        self.sag_layout.setAlignment(Qt.AlignTop)
        self.sag_layout.setSpacing(12)

        # Şehir Filtresi Kayıt Formu İçine Taşındı
        sehir_lay = QHBoxLayout()
        lbl_sehir = QLabel("Etkinlik Şehri:")
        lbl_sehir.setStyleSheet(f"color: {STIL['vurgu_sari']}; font-weight: bold; border: none;")
        self.combo_sehir = QComboBox()
        self.combo_sehir.addItems(["Tüm Şehirler"] + SEHIRLER)
        self.combo_sehir.setStyleSheet(combo_stil())
        self.combo_sehir.currentIndexChanged.connect(self.etkinlik_filtrele)
        sehir_lay.addWidget(lbl_sehir)
        sehir_lay.addWidget(self.combo_sehir)
        self.sag_layout.addLayout(sehir_lay)

        self.sag_layout.addWidget(self.cizgi())

        self.lbl_baslik = QLabel("Lütfen Bir Etkinlik Seçin")
        self.lbl_baslik.setStyleSheet("font-size: 18px; font-weight: bold; color: gold; border:none;")
        self.sag_layout.addWidget(self.lbl_baslik)

        self.lbl_detay = QLabel("Şehir: -- | Süre: -- | Mekan: --")
        self.lbl_detay.setStyleSheet("color: #AAA; font-size: 13px; border:none;")
        self.sag_layout.addWidget(self.lbl_detay)
        
        self.sag_layout.addWidget(self.cizgi())

        # Kişisel Bilgiler
        self.input_ad = QLineEdit(); self.input_ad.setPlaceholderText("Ad Soyad")
        # Rakam girişini direkt engelle
        from PyQt5.QtCore import QRegExp
        from PyQt5.QtGui import QRegExpValidator
        regex = QRegExp("^[a-zA-ZğüşıöçĞÜŞİÖÇ\\s]*$")
        self.input_ad.setValidator(QRegExpValidator(regex))
        
        self.input_email = QLineEdit(); self.input_email.setPlaceholderText("E-posta")

        for inp in [self.input_ad, self.input_email]:
            inp.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 10px; border-radius: 5px;")
            self.sag_layout.addWidget(inp)
            
        # Bilet Adedi
        adet_h = QHBoxLayout()
        lbl_adet = QLabel("Bilet Adedi:"); lbl_adet.setStyleSheet("color: white; border:none;")
        self.spin_bilet = QSpinBox()
        self.spin_bilet.setRange(1, 1)
        self.spin_bilet.setEnabled(False)
        self.spin_bilet.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 5px; border-radius: 5px;")
        self.spin_bilet.valueChanged.connect(self.fiyat_hesapla)
        adet_h.addWidget(lbl_adet); adet_h.addWidget(self.spin_bilet)
        self.sag_layout.addLayout(adet_h)

        # Dinamik Alanlar (Konser/Tiyatro)
        self.dinamik_widget = QWidget()
        self.dinamik_lay = QVBoxLayout(self.dinamik_widget)
        self.dinamik_lay.setContentsMargins(0,0,0,0)
        
        self.lbl_alan = QLabel("Alan Seçimi:"); self.lbl_alan.setStyleSheet("color:white; border:none;")
        self.combo_alan = QComboBox()
        self.combo_alan.addItems(["Sahne Ortası", "Sahne Önü (+100 TL)", "Sahne Arkası (-50 TL)"])
        self.combo_alan.setStyleSheet(combo_stil())
        self.combo_alan.currentIndexChanged.connect(self.fiyat_hesapla)
        
        self.btn_koltuk = QPushButton("Koltuk Seç")
        self.btn_koltuk.setStyleSheet(f"background-color: {STIL['guncelle_mavi']}; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.btn_koltuk.clicked.connect(self.koltuk_ekrani_ac)
        
        self.dinamik_lay.addWidget(self.lbl_alan)
        self.dinamik_lay.addWidget(self.combo_alan)
        self.dinamik_lay.addWidget(self.btn_koltuk)
        self.dinamik_widget.hide()
        self.sag_layout.addWidget(self.dinamik_widget)

        self.sag_layout.addStretch()
        
        self.lbl_tutar = QLabel("Toplam Tutar: 0 TL")
        self.lbl_tutar.setStyleSheet("font-size: 16px; font-weight: bold; color: #00FF7F; border:none;")
        self.lbl_tutar.setAlignment(Qt.AlignCenter)
        self.sag_layout.addWidget(self.lbl_tutar)

        self.btn_kayit = QPushButton("✅ SİPARİŞİ TAMAMLA")
        self.btn_kayit.setStyleSheet(f"background: {STIL['vurgu_sari']}; color: black; font-weight: bold; padding: 15px; border-radius: 10px;")
        self.btn_kayit.clicked.connect(self.kayit_tamamla)
        self.sag_layout.addWidget(self.btn_kayit)

        orta_lay.addWidget(self.sag_kayit_panel, 1) # 1 birim
        layout.addLayout(orta_lay)

    def cizgi(self):
        frm = QFrame()
        frm.setFrameShape(QFrame.HLine)
        frm.setStyleSheet(f"background: {STIL['kenar']};")
        return frm

    def kategori_sec(self, kategori):
        self.aktif_kategori = kategori
        self.etkinlik_filtrele()

    def verileri_guncelle(self):
        self.etkinlik_filtrele()

    def etkinlik_filtrele(self):
        txt = self.arama_cubugu.text().lower()
        secilen_sehir = self.combo_sehir.currentText()
        
        veriler = self.ana_pencere.ana_veriler
        if self.aktif_kategori != "Hepsi":
            veriler = [e for e in veriler if e.get('tur') == self.aktif_kategori]
            
        if secilen_sehir != "Tüm Şehirler":
            veriler = [e for e in veriler if e.get('sehir') == secilen_sehir]
            
        veriler = [e for e in veriler if txt in e['ad'].lower() or txt in e.get('mekan','').lower() or txt in e.get('sehir','').lower()]
        
        # Sadece aktif olanları göster
        veriler = [e for e in veriler if e['durum'] == "Aktif"]
        
        self.tablo.setRowCount(len(veriler))
        for r, e in enumerate(veriler):
            sure_saat = sure_hesapla(e.get('bas','00:00'), e.get('bit','00:00'))
            kalan = e['toplam'] - e['satilan']
            fiyat = str(e.get('fiyat', 'Ücretsiz'))
            v_list = [e['ad'], e.get('sehir', 'Belirtilmedi'), e['mekan'], f"{sure_saat} Saat", str(kalan), fiyat]
            
            for c, val in enumerate(v_list):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, e['id'])
                self.tablo.setItem(r, c, item)



    def etkinlik_secildi(self, r, c):
        e_id = self.tablo.item(r, 0).data(Qt.UserRole)
        for e in self.ana_pencere.ana_veriler:
            if e['id'] == e_id:
                self.secili_etkinlik = e
                break
        
        e = self.secili_etkinlik
        self.lbl_baslik.setText(f"🎯 {e['ad']}")
        sure = sure_hesapla(e.get('bas','00:00'), e.get('bit','00:00'))
        self.lbl_detay.setText(f"Şehir: {e.get('sehir', 'Belirtilmedi')} | Süre: {sure} Saat | Mekan: {e['mekan']}")
        
        kalan = e['toplam'] - e['satilan']
        self.spin_bilet.setEnabled(True)
        self.spin_bilet.setRange(1, min(kalan, 10)) # Max 10 bilet ya da kalan bilet kadar
        
        self.secilen_koltuklar = []
        self.dinamik_widget.show()
        if e['tur'] == "Konser":
            self.combo_alan.show()
            self.lbl_alan.show()
            self.btn_koltuk.hide()
        else: # Tiyatro, Sinema vs
            self.combo_alan.hide()
            self.lbl_alan.hide()
            self.btn_koltuk.show()
            self.btn_koltuk.setText("Koltuk Seç")
            
        self.fiyat_hesapla()

    def fiyat_hesapla(self):
        if not self.secili_etkinlik: return
        fiyat_str = str(self.secili_etkinlik.get('fiyat', '150')).replace('TL', '').strip()
        try: taban_fiyat = int(fiyat_str)
        except: taban_fiyat = 0
        
        adet = self.spin_bilet.value()
        ek_ucret = 0
        
        if self.secili_etkinlik['tur'] == "Konser":
            secim = self.combo_alan.currentText()
            if "Önü" in secim: ek_ucret = 100
            elif "Arkası" in secim: ek_ucret = -50
        else:
            # Koltuk bazlı ek ücret hesaplama
            for koltuk in self.secilen_koltuklar:
                if koltuk.startswith('R'):
                    ek_ucret -= 100
                else:
                    harf = koltuk[0]
                    if harf in ['A', 'B', 'C']: ek_ucret += 100
                    elif harf in ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']: ek_ucret -= 50
            # Eğer koltuk seçilmemişse adet bazlı taban fiyattan devam et
            if not self.secilen_koltuklar:
                toplam = taban_fiyat * adet
            else:
                toplam = (taban_fiyat * adet) + ek_ucret
            self.lbl_tutar.setText(f"Toplam Tutar: {max(0, toplam)} TL")
            return
            
        toplam = (taban_fiyat + ek_ucret) * adet
        self.lbl_tutar.setText(f"Toplam Tutar: {max(0, toplam)} TL")


    def koltuk_ekrani_ac(self):
        if not self.secili_etkinlik:
            QMessageBox.warning(self, "Hata", "Lütfen önce bir etkinlik seçin!")
            return
        adet = self.spin_bilet.value()
        kisi_id = getattr(self, 'secili_k_id', None)
        dolu_koltuklar = self.ana_pencere.backend.dolu_koltuklari_getir(self.secili_etkinlik['id'], kisi_id)
        
        dlg = ModernKoltukSecmeDialog(self, self.secili_etkinlik, adet, dolu_koltuklar, self.secilen_koltuklar)
        if dlg.exec_() == QDialog.Accepted:
            self.secilen_koltuklar = dlg.secilen_koltuklar
            self.btn_koltuk.setText(f"Seçildi ({','.join(self.secilen_koltuklar)})")
            self.fiyat_hesapla()


    def kayit_tamamla(self):
        if not self.secili_etkinlik: return
        ad = self.input_ad.text().strip()
        email = self.input_email.text().strip()
        
        if not ad or not email:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        # İsimde rakam girişi direkt engellenmiştir.



        # E-posta @mail.com kontrolü
        if not email.endswith("@mail.com"):
            QMessageBox.warning(self, "Geçersiz E-posta", "Lütfen geçerli bir e-posta adresi girin (@mail.com).")
            return


            
        adet = self.spin_bilet.value()
        
        if self.secili_etkinlik['tur'] != "Konser" and len(self.secilen_koltuklar) != adet:
            QMessageBox.warning(self, "Hata", "Lütfen bilet adedi kadar koltuk seçimi yapın.")
            return

        alan = self.combo_alan.currentText().split('(')[0].strip() if self.secili_etkinlik['tur'] == "Konser" else ""
        
        e_id = self.secili_etkinlik['id']
        if e_id not in self.ana_pencere.katilimci_havuzu:
            self.ana_pencere.katilimci_havuzu[e_id] = []
            
        mevcut_sayi = len(self.ana_pencere.katilimci_havuzu.get(e_id, []))
        k_id = self.ana_pencere.backend.yeni_katilimci_id_uret(e_id)
        if alan:
            durum_str = f"Biletli ({alan}) - {adet} Adet"
        else:
            koltuk_str = ", ".join(self.secilen_koltuklar)
            durum_str = f"Biletli (Koltuk: {koltuk_str}) - {adet} Adet"
        
        yeni_katilimci = (k_id, ad, email, alan if alan else koltuk_str, adet, self.lbl_tutar.text().replace("Toplam Tutar: ", ""), durum_str)
        
        # Backend üzerinden ekle
        self.ana_pencere.backend.katilimci_ekle(e_id, yeni_katilimci)

            
        self.ana_pencere.verileri_senkronize_et()
        QMessageBox.information(self, "Başarılı", f"{adet} bilet başarıyla alındı!\n{self.lbl_tutar.text()}")
        
        self.input_ad.clear(); self.input_email.clear()
        self.secili_etkinlik = None
        self.lbl_baslik.setText("Lütfen Bir Etkinlik Seçin")
        self.lbl_detay.setText("Süre: -- | Mekan: --")
        self.spin_bilet.setEnabled(False)
        self.dinamik_widget.hide()
        self.lbl_tutar.setText("Toplam Tutar: 0 TL")
        self.verileri_guncelle()

# --- YENİ EKLENEN 3 SAYFA ---

# --- 5. SAYFA: KAYIT YÖNETİMİ ---
class KayitYonetimSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.secili_k_id = None
        self.secili_e_id = None
        self.secili_etkinlik = None
        self.secilen_koltuklar = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        layout.addWidget(QLabel("⚙️ Kayıt Yönetimi (Bilgi Düzenleme & İptal)", styleSheet=f"color: {STIL['vurgu_sari']}; font-weight: bold; font-size: 24px; margin-bottom: 10px;"))

        self.combo_filtre = QComboBox()
        self.combo_filtre.setStyleSheet(combo_stil())
        self.combo_filtre.currentIndexChanged.connect(self.tabloyu_doldur)
        layout.addWidget(self.combo_filtre)

        icerik_lay = QHBoxLayout()

        # SOL: TABLO (Daha dar)
        self.tablo = standart_tablo_olustur(["BİLET ID", "AD SOYAD", "E-POSTA", "SEÇİM", "ADET", "ÖDENEN", "E_ID"])
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablo.cellClicked.connect(self.kisi_secildi)
        icerik_lay.addWidget(self.tablo, 2)

        # SAĞ: GÜNCELLEME PANELİ
        self.guncelle_frame = QFrame()
        self.guncelle_frame.setStyleSheet(f"background: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 15px;")
        g_lay = QVBoxLayout(self.guncelle_frame)
        g_lay.setAlignment(Qt.AlignTop)
        g_lay.setSpacing(12)

        self.lbl_panel_baslik = QLabel("Kişi Seçin")
        self.lbl_panel_baslik.setStyleSheet("color: gold; font-weight: bold; font-size: 16px; border:none;")
        g_lay.addWidget(self.lbl_panel_baslik)

        self.lbl_etkinlik_id = QLabel("Etkinlik ID: --")
        self.lbl_etkinlik_id.setStyleSheet("color: #AAA; font-size: 13px; border:none;")
        g_lay.addWidget(self.lbl_etkinlik_id)

        self.g_ad = QLineEdit(); self.g_ad.setPlaceholderText("Ad Soyad")
        
        # Rakam girişini direkt engelle (Sadece harf ve boşluk)
        from PyQt5.QtCore import QRegExp
        from PyQt5.QtGui import QRegExpValidator
        regex = QRegExp("^[a-zA-ZğüşıöçĞÜŞİÖÇ\\s]*$")
        self.g_ad.setValidator(QRegExpValidator(regex))
        
        self.g_email = QLineEdit(); self.g_email.setPlaceholderText("E-posta")


        for inp in [self.g_ad, self.g_email]:
            inp.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 10px; border-radius: 5px;")
            g_lay.addWidget(inp)

        # Bilet Adedi
        adet_h = QHBoxLayout()
        lbl_adet = QLabel("Bilet Adedi:"); lbl_adet.setStyleSheet("color: white; border:none;")
        self.spin_bilet = QSpinBox()
        self.spin_bilet.setRange(1, 100)
        self.spin_bilet.setEnabled(False)
        self.spin_bilet.setStyleSheet(f"background: {STIL['input_bg']}; color: white; padding: 5px; border-radius: 5px;")
        self.spin_bilet.valueChanged.connect(self.fiyat_hesapla)
        adet_h.addWidget(lbl_adet); adet_h.addWidget(self.spin_bilet)
        g_lay.addLayout(adet_h)

        # Dinamik Alanlar (Konser/Tiyatro)
        self.dinamik_widget = QWidget()
        self.dinamik_lay = QVBoxLayout(self.dinamik_widget)
        self.dinamik_lay.setContentsMargins(0,0,0,0)
        
        self.lbl_alan = QLabel("Sahne/Koltuk Seçimi:"); self.lbl_alan.setStyleSheet("color:white; border:none;")
        self.combo_alan = QComboBox()
        self.combo_alan.addItems(["Sahne Ortası", "Sahne Önü (+100 TL)", "Sahne Arkası (-50 TL)"])
        self.combo_alan.setStyleSheet(combo_stil())
        self.combo_alan.currentIndexChanged.connect(self.fiyat_hesapla)
        
        self.btn_koltuk = QPushButton("Koltuk Seç")
        self.btn_koltuk.setStyleSheet(f"background-color: {STIL['guncelle_mavi']}; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.btn_koltuk.clicked.connect(self.koltuk_ekrani_ac)
        
        self.dinamik_lay.addWidget(self.lbl_alan)
        self.dinamik_lay.addWidget(self.combo_alan)
        self.dinamik_lay.addWidget(self.btn_koltuk)
        self.dinamik_widget.hide()
        g_lay.addWidget(self.dinamik_widget)

        self.lbl_odenecek = QLabel("Ödenecek Tutar:")
        self.lbl_odenecek.setStyleSheet("color: white; font-weight: bold; border:none;")
        g_lay.addWidget(self.lbl_odenecek)

        self.g_fiyat = QLineEdit()
        self.g_fiyat.setPlaceholderText("Tutar (TL)")
        self.g_fiyat.setValidator(QIntValidator(0, 999999, self))
        self.g_fiyat.setStyleSheet(f"background: {STIL['input_bg']}; color: #00FF7F; font-weight: bold; padding: 10px; border-radius: 5px;")
        g_lay.addWidget(self.g_fiyat)

        self.lbl_hesaplanan = QLabel("Oto Hesap: 0 TL")
        self.lbl_hesaplanan.setStyleSheet("font-size: 13px; color: #AAAAAA; border:none;")
        self.lbl_hesaplanan.setAlignment(Qt.AlignCenter)
        g_lay.addWidget(self.lbl_hesaplanan)

        g_lay.addStretch()

        btn_h = QHBoxLayout()
        btn_guncelle = QPushButton("Güncelle")
        btn_guncelle.setStyleSheet(f"background: {STIL['guncelle_mavi']}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        btn_guncelle.clicked.connect(self.guncelle)

        btn_sil = QPushButton("Sil")
        btn_sil.setStyleSheet(f"background: {STIL['sil_kirmizi']}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        btn_sil.clicked.connect(self.sil)

        btn_h.addWidget(btn_guncelle); btn_h.addWidget(btn_sil)
        g_lay.addLayout(btn_h)

        icerik_lay.addWidget(self.guncelle_frame, 1)
        layout.addLayout(icerik_lay)

    def verileri_yansit(self, veriler):
        self.combo_filtre.blockSignals(True)
        self.combo_filtre.clear()
        self.combo_filtre.addItem("Tüm Etkinlikler", "TUM")
        for e in veriler:
            self.combo_filtre.addItem(e['ad'], e['id'])
        self.combo_filtre.blockSignals(False)
        self.tabloyu_doldur()

    def tabloyu_doldur(self):
        secili_e = self.combo_filtre.currentData()
        satirlar = []
        for e_id, kisiler in self.ana_pencere.katilimci_havuzu.items():
            if secili_e == "TUM" or secili_e == e_id:
                for kisi in kisiler: 
                    # kisi = (k_id, ad, email, secim, adet, odenen, durum_str)
                    satirlar.append((kisi[0], kisi[1], kisi[2], kisi[3] if len(kisi)>3 else "", kisi[4] if len(kisi)>4 else 1, kisi[5] if len(kisi)>5 else "", e_id))
        
        self.tablo.setRowCount(len(satirlar))
        for r, row in enumerate(satirlar):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.tablo.setItem(r, c, item)

    def kisi_secildi(self, r, c):
        self.secili_k_id = self.tablo.item(r, 0).text()
        self.g_ad.setText(self.tablo.item(r, 1).text())
        self.g_email.setText(self.tablo.item(r, 2).text())
        secim = self.tablo.item(r, 3).text()
        adet_str = self.tablo.item(r, 4).text()
        fiyat_str = self.tablo.item(r, 5).text()
        self.secili_e_id = self.tablo.item(r, 6).text()

        self.lbl_panel_baslik.setText(f"Düzenle: {self.g_ad.text()}")
        self.lbl_etkinlik_id.setText(f"Etkinlik ID: {self.secili_e_id}")

        self.secili_etkinlik = next((e for e in self.ana_pencere.ana_veriler if e['id'] == self.secili_e_id), None)
        if not self.secili_etkinlik: return

        self.spin_bilet.setEnabled(True)
        mevcut_kalan = self.secili_etkinlik['toplam'] - self.secili_etkinlik['satilan']
        su_anki_adet = int(adet_str) if adet_str.isdigit() else 1
        self.spin_bilet.setRange(1, mevcut_kalan + su_anki_adet)
        
        self.spin_bilet.blockSignals(True)
        self.spin_bilet.setValue(su_anki_adet)
        self.spin_bilet.blockSignals(False)

        self.secilen_koltuklar = []
        self.dinamik_widget.show()
        if self.secili_etkinlik['tur'] == "Konser":
            self.combo_alan.show()
            self.lbl_alan.show()
            self.btn_koltuk.hide()
            idx = self.combo_alan.findText(secim, Qt.MatchContains)
            if idx >= 0: self.combo_alan.setCurrentIndex(idx)
        else:
            self.combo_alan.hide()
            self.lbl_alan.hide()
            self.btn_koltuk.show()
            self.secilen_koltuklar = [s.strip() for s in secim.split(',')] if secim else []
            self.btn_koltuk.setText(f"Seçildi ({','.join(self.secilen_koltuklar)})" if self.secilen_koltuklar else "Koltuk Seç")

        self.g_fiyat.setText(fiyat_str.replace(" TL", "").strip())

    def fiyat_hesapla(self):
        if not self.secili_etkinlik: return
        fiyat_str = str(self.secili_etkinlik.get('fiyat', '150')).replace('TL', '').strip()
        try: taban_fiyat = int(fiyat_str)
        except: taban_fiyat = 0
        
        adet = self.spin_bilet.value()
        ek_ucret = 0
        if self.secili_etkinlik['tur'] == "Konser":
            secim = self.combo_alan.currentText()
            if "Önü" in secim: ek_ucret = 100
            elif "Arkası" in secim: ek_ucret = -50
        else:
            for koltuk in self.secilen_koltuklar:
                if koltuk.startswith('R'):
                    ek_ucret -= 100
                else:
                    harf = koltuk[0]
                    if harf in ['A', 'B', 'C']: ek_ucret += 100
                    elif harf in ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']: ek_ucret -= 50
        
        toplam = (taban_fiyat * adet) + ek_ucret if self.secili_etkinlik['tur'] != "Konser" else (taban_fiyat + ek_ucret) * adet
        self.lbl_hesaplanan.setText(f"Hesaplanan: {max(0, toplam)} TL")
        self.g_fiyat.setText(str(max(0, toplam)))

    def koltuk_ekrani_ac(self):
        if not self.secili_etkinlik:
            QMessageBox.warning(self, "Hata", "Lütfen önce bir kayıt seçin!")
            return
        adet = self.spin_bilet.value()
        dolu_koltuklar = self.ana_pencere.backend.dolu_koltuklari_getir(self.secili_etkinlik['id'], self.secili_k_id)
        
        dlg = ModernKoltukSecmeDialog(self, self.secili_etkinlik, adet, dolu_koltuklar, self.secilen_koltuklar)
        if dlg.exec_() == QDialog.Accepted:
            self.secilen_koltuklar = dlg.secilen_koltuklar
            self.btn_koltuk.setText(f"Seçildi ({','.join(self.secilen_koltuklar)})")
            self.fiyat_hesapla()


    def guncelle(self):
        if not self.secili_k_id or not self.secili_etkinlik: return
        yeni_ad = self.g_ad.text(); yeni_email = self.g_email.text()
        adet = self.spin_bilet.value()
        
        if not yeni_ad or not yeni_email:
            QMessageBox.warning(self, "Hata", "Lütfen ad ve e-posta girin.")
            return

        # İsimde rakam girişi direkt engellenmiştir.



        # E-posta @mail.com kontrolü
        if not yeni_email.endswith("@mail.com"):
            QMessageBox.warning(self, "Geçersiz E-posta", "Lütfen geçerli bir e-posta adresi girin (@mail.com).")
            return



        if self.secili_etkinlik['tur'] != "Konser" and len(self.secilen_koltuklar) != adet:
            QMessageBox.warning(self, "Hata", "Lütfen bilet adedi kadar koltuk seçin.")
            return

        alan = self.combo_alan.currentText().split('(')[0].strip() if self.secili_etkinlik['tur'] == "Konser" else ""
        if alan:
            secim = alan
            durum_str = f"Biletli ({alan}) - {adet} Adet"
        else:
            koltuk_str = ", ".join(self.secilen_koltuklar)
            secim = koltuk_str
            durum_str = f"Biletli (Koltuk: {koltuk_str}) - {adet} Adet"

        toplam_fiyat_str = f"{self.g_fiyat.text().strip()} TL"
        
        # Backend üzerinden güncelle
        yeni_veri = (self.secili_k_id, yeni_ad, yeni_email, secim, adet, toplam_fiyat_str, durum_str)
        self.ana_pencere.backend.katilimci_guncelle(self.secili_k_id, self.secili_e_id, yeni_veri)

                
        self.ana_pencere.verileri_senkronize_et()
        self.tabloyu_doldur()
        
        # Seçimi temizle
        self.secili_k_id = None; self.secili_etkinlik = None; self.secilen_koltuklar = []
        self.g_ad.clear(); self.g_email.clear(); self.g_fiyat.clear()
        self.btn_koltuk.setText("Koltuk Seç")
        self.lbl_panel_baslik.setText("Kişi Seçin")
        self.lbl_etkinlik_id.setText("Etkinlik ID: --")
        
        QMessageBox.information(self, "Bilgi", "Katılımcı bilgileri başarıyla güncellendi.")

    def sil(self):
        if not self.secili_k_id: return
        if QMessageBox.question(self, "Onay", "Kayıt silinecek. Emin misiniz?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            # Backend üzerinden sil
            self.ana_pencere.backend.katilimci_sil(self.secili_k_id, self.secili_e_id)
            
            self.ana_pencere.verileri_senkronize_et()

            self.g_ad.clear(); self.g_email.clear(); self.secili_k_id = None
            self.spin_bilet.setEnabled(False)
            self.dinamik_widget.hide()
            self.lbl_hesaplanan.setText("Oto Hesap: 0 TL")
            self.g_fiyat.clear()
            self.lbl_panel_baslik.setText("Kişi Seçin")
            self.lbl_etkinlik_id.setText("Etkinlik ID: --")
            self.tabloyu_doldur()
            QMessageBox.information(self, "Bilgi", "Kayıt başarıyla iptal edildi.")

# --- 6. SAYFA: BİLETLERİM ---
class BiletSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.secili_kisi = None; self.secili_etkinlik = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # ÜST: Arama Çubuğu
        self.arama_cubugu = QLineEdit()
        self.arama_cubugu.setPlaceholderText("🔍 Katılımcı, Etkinlik veya E-posta Ara...")
        self.arama_cubugu.setStyleSheet(f"background: {STIL['arama_bg']}; color: white; padding: 10px; border-radius: 8px;")
        self.arama_cubugu.textChanged.connect(self.filtrele)
        layout.addWidget(self.arama_cubugu)

        # ORTA: Sol Tablo, Sağ Bilet
        orta_lay = QHBoxLayout()
        
        sol_panel = QFrame()
        sol_lay = QVBoxLayout(sol_panel)
        sol_lay.setContentsMargins(0, 0, 0, 0)
        sol_lay.addWidget(QLabel("👥 Katılımcılar", styleSheet=f"color: {STIL['vurgu_sari']}; font-weight: bold; font-size: 18px;"))
        
        self.tablo = standart_tablo_olustur(["Katılımcı ID", "İsim Soyisim", "E-posta", "Etkinlik Adı", "Sahne/Koltuk", "Bilet Sayısı", "Etkinlik ID"])
        self.tablo.cellClicked.connect(self.kisi_secildi)
        sol_lay.addWidget(self.tablo)
        orta_lay.addWidget(sol_panel, 2) # tablo 2 birim alan kaplasın

        sag_panel = QFrame()
        sag_lay = QVBoxLayout(sag_panel)
        sag_lay.setAlignment(Qt.AlignCenter)

        self.bilet_frame = QFrame()
        self.bilet_frame.setFixedSize(500, 300)
        self.bilet_frame.setStyleSheet(f"""
            QFrame {{ background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2C3E50, stop:1 #000000); border: 2px dashed {STIL['vurgu_sari']}; border-radius: 15px; }}
        """)
        
        bilet_ic_lay = QVBoxLayout(self.bilet_frame)
        self.b_logo = QLabel("🎫 BİLET")
        self.b_logo.setStyleSheet(f"color: {STIL['vurgu_sari']}; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        self.b_logo.setAlignment(Qt.AlignCenter)
        self.b_etkinlik_adi = QLabel("Etkinlik Adı")
        self.b_etkinlik_adi.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent; border: none;")
        self.b_etkinlik_adi.setAlignment(Qt.AlignCenter)
        self.b_kisi_adi = QLabel("Katılımcı Adı")
        self.b_kisi_adi.setStyleSheet("color: #AAAAAA; font-size: 16px; background: transparent; border: none;")
        self.b_kisi_adi.setAlignment(Qt.AlignCenter)
        self.b_kisi_id = QLabel("Katılımcı ID: --")
        self.b_kisi_id.setStyleSheet("color: #888888; font-size: 12px; background: transparent; border: none;")
        self.b_kisi_id.setAlignment(Qt.AlignCenter)
        self.b_detay = QLabel("Tarih: -- | Mekan: --")
        self.b_detay.setStyleSheet("color: white; font-size: 14px; background: transparent; border: none;")
        self.b_detay.setAlignment(Qt.AlignCenter)
        self.b_ekstra = QLabel("Kişi: -- | Sahne/Koltuk: --")
        self.b_ekstra.setStyleSheet("color: white; font-size: 14px; background: transparent; border: none;")
        self.b_ekstra.setAlignment(Qt.AlignCenter)

        for l in [self.b_logo, self.b_etkinlik_adi, self.b_kisi_adi, self.b_kisi_id, self.b_detay, self.b_ekstra]: bilet_ic_lay.addWidget(l)
        sag_lay.addWidget(self.bilet_frame)
        sag_lay.addSpacing(20)

        self.btn_indir = QPushButton("Bileti İndir (bilet_olustur)")
        self.btn_indir.setStyleSheet(f"background: {STIL['vurgu_sari']}; color: black; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 8px;")
        self.btn_indir.clicked.connect(self.bilet_indir)
        sag_lay.addWidget(self.btn_indir, alignment=Qt.AlignCenter)
        orta_lay.addWidget(sag_panel, 1)

        layout.addLayout(orta_lay)
        self.tum_veriler = []

    def verileri_yansit(self):
        self.tum_veriler = []
        for e_id, kisiler in self.ana_pencere.katilimci_havuzu.items():
            e = next((e for e in self.ana_pencere.ana_veriler if e['id'] == e_id), None)
            e_ad = e['ad'] if e else "Bilinmeyen"
            for k in kisiler:
                self.tum_veriler.append({
                    "kisi": k,
                    "etkinlik_id": e_id,
                    "etkinlik_adi": e_ad,
                    "etkinlik": e
                })
        self.filtrele()

    def filtrele(self):
        txt = self.arama_cubugu.text().lower()
        filtrelenmis = [v for v in self.tum_veriler if txt in v['kisi'][1].lower() or txt in v['kisi'][2].lower() or txt in v['etkinlik_adi'].lower() or txt in v['kisi'][0].lower()]
        
        self.tablo.setRowCount(len(filtrelenmis))
        for r, v in enumerate(filtrelenmis):
            k = v['kisi']
            secim = k[3] if len(k) > 3 else "-"
            adet = str(k[4]) if len(k) > 4 else "1"
            
            row_data = [k[0], k[1], k[2], v['etkinlik_adi'], secim, adet, v['etkinlik_id']]
            for c, val in enumerate(row_data):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                if c == 0:
                    item.setData(Qt.UserRole, v)
                self.tablo.setItem(r, c, item)

    def kisi_secildi(self, r, c):
        v = self.tablo.item(r, 0).data(Qt.UserRole)
        self.secili_kisi = v['kisi']
        self.secili_etkinlik = v['etkinlik']
        
        if not self.secili_etkinlik: return

        tur = self.secili_etkinlik.get('tur', 'ETKİNLİK')
        self.b_logo.setText(f"🎫 {tur.upper()} BİLETİ")
        self.b_etkinlik_adi.setText(self.secili_etkinlik['ad'])
        self.b_kisi_adi.setText(f"{self.secili_kisi[1]}")
        self.b_kisi_id.setText(f"Katılımcı ID: {self.secili_kisi[0]}")
        self.b_detay.setText(f"Tarih: {self.secili_etkinlik['tarih']} | Mekan: {self.secili_etkinlik['mekan']}")
        
        secim = self.secili_kisi[3] if len(self.secili_kisi) > 3 else "-"
        adet = str(self.secili_kisi[4]) if len(self.secili_kisi) > 4 else "1"
        self.b_ekstra.setText(f"Kişi Sayısı: {adet} | Sahne/Koltuk: {secim}")

    def bilet_indir(self):
        if not self.secili_kisi or not self.secili_etkinlik:
            QMessageBox.warning(self, "Hata", "Lütfen listeden bir bilet seçin.")
            return
        dosya_adi, _ = QFileDialog.getSaveFileName(self, "Bileti Kaydet", f"{self.secili_kisi[0]}_Bilet.txt", "Text Files (*.txt)")
        if dosya_adi:
            tur = self.secili_etkinlik.get('tur', 'ETKİNLİK')
            secim = self.secili_kisi[3] if len(self.secili_kisi)>3 else ''
            adet = self.secili_kisi[4] if len(self.secili_kisi)>4 else 1
            fiyat = self.secili_kisi[5] if len(self.secili_kisi)>5 else ''
            durum = self.secili_kisi[6] if len(self.secili_kisi)>6 else ''
            
            icerik = f"""=====================================
            {tur.upper()} BİLETİ
=====================================
Bilet ID     : {self.secili_kisi[0]}
Katılımcı Adı: {self.secili_kisi[1]}
E-posta      : {self.secili_kisi[2]}
Sahne/Koltuk : {secim}
Bilet Adedi  : {adet}
Ödenen Tutar : {fiyat}
Durum        : {durum}
-------------------------------------
Etkinlik Adı : {self.secili_etkinlik['ad']}
Tarih        : {self.secili_etkinlik['tarih']}
Saat         : {self.secili_etkinlik.get('bas', '19:00')}
Mekan        : {self.secili_etkinlik['mekan']} ({self.secili_etkinlik.get('sehir', '')})
=====================================
Bu bilet EventPro Sisteminden otomatik üretilmiştir.
"""
            with open(dosya_adi, 'w', encoding='utf-8') as f: f.write(icerik)
            QMessageBox.information(self, "Başarılı", "Bilet .txt olarak kaydedildi!")

# --- 7. SAYFA: ANALİZ VE RAPOR ---
class RaporSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        layout.addWidget(QLabel("📊 Akademik Analiz ve Raporlama", styleSheet=f"color: {STIL['vurgu_sari']}; font-weight: bold; font-size: 24px; margin-bottom: 10px;"))

        # Üst Kısım (Tablo ve Özel Etkinlik Analizi)
        ust_lay = QHBoxLayout()
        
        self.tablo = standart_tablo_olustur(["ETKİNLİK", "KAPASİTE", "KATILIMCI", "DOLULUK", "GELİR (Tahmini)"])
        self.tablo.cellClicked.connect(self.etkinlik_secildi)
        ust_lay.addWidget(self.tablo, 2)

        # Seçilen etkinlik analizi
        ozel_analiz_frame = QFrame()
        ozel_analiz_frame.setStyleSheet(f"background-color: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 10px;")
        ozel_lay = QVBoxLayout(ozel_analiz_frame)
        self.lbl_secilen = QLabel("🎯 Seçili Etkinlik Analizi")
        self.lbl_secilen.setStyleSheet(f"color: {STIL['vurgu_sari']}; font-weight: bold; font-size: 16px; border:none;")
        ozel_lay.addWidget(self.lbl_secilen, alignment=Qt.AlignCenter)
        
        self.fig_ozel = Figure(figsize=(4, 3), dpi=100)
        self.fig_ozel.patch.set_facecolor('#1E1E1E')
        self.canvas_ozel = FigureCanvas(self.fig_ozel)
        ozel_lay.addWidget(self.canvas_ozel)
        
        ust_lay.addWidget(ozel_analiz_frame, 1)
        layout.addLayout(ust_lay, 2)

        # Alt Kısım (Genel Grafikler)
        alt_frame = QFrame()
        alt_frame.setStyleSheet(f"background-color: {STIL['kart']}; border: 1px solid {STIL['kenar']}; border-radius: 10px;")
        alt_lay = QVBoxLayout(alt_frame)
        lbl_genel = QLabel("🌍 Tüm Etkinlikler Genel Analizi")
        lbl_genel.setStyleSheet(f"color: {STIL['vurgu_sari']}; font-weight: bold; font-size: 16px; border:none;")
        alt_lay.addWidget(lbl_genel, alignment=Qt.AlignCenter)

        genel_grafik_lay = QHBoxLayout()
        self.fig_genel_doluluk = Figure(figsize=(4, 3), dpi=100)
        self.fig_genel_doluluk.patch.set_facecolor('#1E1E1E')
        self.canvas_genel_doluluk = FigureCanvas(self.fig_genel_doluluk)
        genel_grafik_lay.addWidget(self.canvas_genel_doluluk)

        self.fig_genel_gelir = Figure(figsize=(4, 3), dpi=100)
        self.fig_genel_gelir.patch.set_facecolor('#1E1E1E')
        self.canvas_genel_gelir = FigureCanvas(self.fig_genel_gelir)
        genel_grafik_lay.addWidget(self.canvas_genel_gelir)
        
        alt_lay.addLayout(genel_grafik_lay)
        layout.addWidget(alt_frame, 3)

        # En Alt - Rapor Butonu
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        self.btn_rapor = QPushButton("Sistem Raporunu Dışa Aktar (.txt)")
        self.btn_rapor.setStyleSheet(f"background: {STIL['kaydet_yesil']}; color: white; font-weight: bold; padding: 12px; font-size: 14px; border-radius: 8px;")
        self.btn_rapor.clicked.connect(self.rapor_al)
        btn_lay.addWidget(self.btn_rapor)
        layout.addLayout(btn_lay)
        
        self.tum_veriler = []

    def verileri_yansit(self, veriler):
        self.tum_veriler = veriler
        self.tablo.setRowCount(len(veriler))
        for r, e in enumerate(veriler):
            oran = (e['satilan'] / e['toplam'] * 100) if e['toplam'] > 0 else 0
            fiyat_str = str(e.get('fiyat', '150'))
            fiyat_num = int(''.join(filter(str.isdigit, fiyat_str)) or 150)
            gelir = e['satilan'] * fiyat_num
            
            v = [e['ad'], str(e['toplam']), str(e['satilan']), f"%{oran:.1f}", f"{gelir} TL"]
            for c, val in enumerate(v):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                if c == 0:
                    item.setData(Qt.UserRole, e['id'])
                self.tablo.setItem(r, c, item)
        
        self.genel_grafikleri_ciz()

    def etkinlik_secildi(self, r, c):
        e_id = self.tablo.item(r, 0).data(Qt.UserRole)
        e = next((x for x in self.tum_veriler if x['id'] == e_id), None)
        if not e: return
        
        self.lbl_secilen.setText(f"🎯 {e['ad']} Analizi")
        
        fiyat_str = str(e.get('fiyat', '150'))
        fiyat_num = int(''.join(filter(str.isdigit, fiyat_str)) or 150)
        gelir = e['satilan'] * fiyat_num
        beklenen_gelir = e['toplam'] * fiyat_num
        
        self.fig_ozel.clear()
        
        # 1. Grafik (Doluluk - Pie)
        ax1 = self.fig_ozel.add_subplot(121)
        satilan = e['satilan']
        kalan = max(0, e['toplam'] - satilan)
        if satilan == 0 and kalan == 0:
            ax1.pie([1], labels=['Veri Yok'], colors=['gray'])
        else:
            ax1.pie([satilan, kalan], labels=['Dolu', 'Boş'], colors=['#4CAF50', '#F44336'], autopct='%1.1f%%', textprops={'color':"w", 'fontsize':8})
        ax1.set_title("Doluluk", color="w", fontsize=10)
        
        # 2. Grafik (Gelir - Bar)
        ax2 = self.fig_ozel.add_subplot(122)
        ax2.bar(["Mevcut", "Beklenen"], [gelir, beklenen_gelir], color=['#FFD700', '#2196F3'])
        ax2.set_title("Gelir (TL)", color="w", fontsize=10)
        ax2.tick_params(axis='x', colors='w', labelsize=8)
        ax2.tick_params(axis='y', colors='w', labelsize=8)
        for spine in ax2.spines.values(): spine.set_edgecolor('#555')
        
        self.fig_ozel.tight_layout()
        self.canvas_ozel.draw()

    def genel_grafikleri_ciz(self):
        if not self.tum_veriler: return
        
        self.fig_genel_doluluk.clear()
        self.fig_genel_gelir.clear()
        
        toplam_kapasite = sum(e['toplam'] for e in self.tum_veriler)
        toplam_satilan = sum(e['satilan'] for e in self.tum_veriler)
        toplam_kalan = max(0, toplam_kapasite - toplam_satilan)
        
        # Genel Doluluk Pie Chart
        ax_doluluk = self.fig_genel_doluluk.add_subplot(111)
        if toplam_kapasite > 0:
            ax_doluluk.pie([toplam_satilan, toplam_kalan], labels=['Satılan', 'Kalan'], colors=['#2980B9', '#C0392B'], autopct='%1.1f%%', textprops={'color':"w", 'fontsize':10})
        ax_doluluk.set_title("Tüm Etkinlikler Genel Doluluk", color="w", fontsize=12)
        
        # Genel Gelir Bar Chart (Etkinlik bazlı)
        ax_gelir = self.fig_genel_gelir.add_subplot(111)
        adlar = []
        gelirler = []
        for e in self.tum_veriler:
            fiyat_str = str(e.get('fiyat', '150'))
            fiyat_num = int(''.join(filter(str.isdigit, fiyat_str)) or 150)
            gelirler.append(e['satilan'] * fiyat_num)
            ad = e['ad'] if len(e['ad']) < 10 else e['ad'][:8]+".."
            adlar.append(ad)
            
        ax_gelir.bar(adlar, gelirler, color='#27AE60')
        ax_gelir.set_title("Etkinlik Bazlı Gelirler", color="w", fontsize=12)
        ax_gelir.tick_params(axis='x', colors='w', rotation=30, labelsize=8)
        ax_gelir.tick_params(axis='y', colors='w', labelsize=8)
        for spine in ax_gelir.spines.values(): spine.set_edgecolor('#555')
        
        self.fig_genel_doluluk.tight_layout()
        self.canvas_genel_doluluk.draw()
        
        self.fig_genel_gelir.tight_layout()
        self.canvas_genel_gelir.draw()

    def rapor_al(self):
        dosya_adi, _ = QFileDialog.getSaveFileName(self, "Raporu Kaydet", "Sistem_Raporu.txt", "Text Files (*.txt)")
        if dosya_adi:
            icerik = "=====================================\n       SİSTEM GENEL RAPORU\n=====================================\n\n"
            toplam_e = len(self.ana_pencere.ana_veriler)
            toplam_k = sum(len(k) for k in self.ana_pencere.katilimci_havuzu.values())
            
            icerik += f"Toplam Etkinlik Sayısı : {toplam_e}\nToplam Kayıtlı Kişi    : {toplam_k}\n\nETKİNLİK DETAYLARI:\n-------------------------------------\n"
            for e in self.ana_pencere.ana_veriler:
                icerik += f"Ad: {e['ad']}\nTarih/Saat: {e['tarih']} {e.get('bas', '')}\nMekan: {e['mekan']} ({e.get('sehir', '')})\nKapasite/Katılımcı: {e['toplam']} / {e['satilan']}\nDurum: {e['durum']}\n-\n"
                
            with open(dosya_adi, 'w', encoding='utf-8') as f: f.write(icerik)
            QMessageBox.information(self, "Başarılı", "Rapor .txt olarak başarıyla kaydedildi!")

# --- ANA PENCERE ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EventPro Yönetim Sistemi")
        self.resize(1300, 850)
        self.setStyleSheet(f"background-color: {STIL['arka_plan']};")

        # MERKEZİ VERİLER (BACKEND'DEN ÇEKİLİYOR)
        self.backend = EtkinlikBackend()
        self.backend.verileri_yukle()
        self.backend.veri_hesapla()
        self.ana_veriler = self.backend.ana_veriler
        self.katilimci_havuzu = self.backend.katilimci_havuzu
        self.yeni_id_uret = self.backend.yeni_id_uret
        self.get_katilimcilar_by_id = self.backend.get_katilimcilar_by_id

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)

        # SIDEBAR
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet(f"background-color: {STIL['yan_panel']}; border-right: 1px solid {STIL['kenar']};")
        side_lay = QVBoxLayout(self.sidebar)
        
        logo = QLabel("EVENT PRO"); logo.setStyleSheet(f"color: {STIL['vurgu_sari']}; font-size: 24px; font-weight: bold; margin: 30px 0;")
        side_lay.addWidget(logo, alignment=Qt.AlignCenter)

        self.btn_analiz = self.nav_btn("📊 Dashboard")
        self.btn_yonetim = self.nav_btn("⚙️ Etkinlik Yönetimi")
        self.btn_ekle = self.nav_btn("➕ Yeni Etkinlik Ekle")
        self.btn_katilimci = self.nav_btn("📝 Kayıt Ol (Katılımcı)")
        # YENI SAYFALARIN BUTONLARI
        self.btn_kayit_yonetim = self.nav_btn("⚙️ Kayıt Yönetimi")
        self.btn_biletlerim = self.nav_btn("🎫 Biletlerim")
        self.btn_rapor = self.nav_btn("📊 Analiz ve Rapor")
        
        butonlar = [self.btn_analiz, self.btn_yonetim, self.btn_ekle, self.btn_katilimci, self.btn_kayit_yonetim, self.btn_biletlerim, self.btn_rapor]
        for b in butonlar: side_lay.addWidget(b)
        side_lay.addStretch()

        # STACKED WIDGET (SAYFALAR)
        self.stack = QStackedWidget()
        self.s_analiz = AnalizSayfasi()
        self.s_yonetim = YonetimSayfasi(self)
        self.s_ekle = EtkinlikEkleSayfasi(self)
        self.s_katilimci = KatilimciSayfasi(self)
        # YENI SAYFALAR
        self.s_kayit_yonetim = KayitYonetimSayfasi(self)
        self.s_bilet = BiletSayfasi(self)
        self.s_rapor = RaporSayfasi(self)

        sayfalar = [self.s_analiz, self.s_yonetim, self.s_ekle, self.s_katilimci, self.s_kayit_yonetim, self.s_bilet, self.s_rapor]
        for s in sayfalar: self.stack.addWidget(s)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        # Navigasyon Bağlantıları
        self.btn_analiz.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_yonetim.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_ekle.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_katilimci.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        self.btn_kayit_yonetim.clicked.connect(lambda: self.stack.setCurrentIndex(4))
        self.btn_biletlerim.clicked.connect(lambda: self.stack.setCurrentIndex(5))
        self.btn_rapor.clicked.connect(lambda: self.stack.setCurrentIndex(6))

        self.verileri_senkronize_et()

    def nav_btn(self, t):
        btn = QPushButton(t)
        btn.setStyleSheet("QPushButton { color: white; padding: 15px; text-align: left; border: none; font-size: 14px;} QPushButton:hover { background: #2A2A2A; color: #FFD700; border-left: 3px solid #FFD700; }")
        return btn

    def verileri_senkronize_et(self):
        # Backend verilerini tazele ve hesaplamaları yap
        self.backend.verileri_yukle()
        self.backend.veri_hesapla()
        
        self.ana_veriler = self.backend.ana_veriler
        self.katilimci_havuzu = self.backend.katilimci_havuzu

        
        # Sadece UI güncellemelerini yap
        self.s_analiz.verileri_yansit(self.ana_veriler) 
        self.s_yonetim.verileri_yansit(self.ana_veriler)
        self.s_ekle.tabloyu_doldur(self.ana_veriler)
        self.s_katilimci.verileri_guncelle()
        # Yeni sayfalar
        self.s_kayit_yonetim.verileri_yansit(self.ana_veriler)
        self.s_bilet.verileri_yansit()
        self.s_rapor.verileri_yansit(self.ana_veriler)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMessageBox { background-color: #1E1E1E; } QMessageBox QLabel { color: white; } QMessageBox QPushButton { background-color: #2980B9; color: white; padding: 5px 15px; border-radius: 5px; font-weight: bold; border: 1px solid #1A5276; min-width: 80px; min-height: 25px; outline: none; }")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())