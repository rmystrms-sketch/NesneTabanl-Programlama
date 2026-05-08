"""
============================================================
  ARAÇ PAYLAŞIM SİSTEMİ
  PyQt5 Arayüzü
============================================================
Kurulum  : pip install PyQt5
Çalıştır : py -3.x arac_paylasim_sistemi.py
============================================================
"""

import sys
from datetime import datetime, date, timedelta

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QGridLayout,
    QDateTimeEdit, QSpinBox, QDoubleSpinBox, QMessageBox,
    QAbstractItemView, QGraphicsDropShadowEffect, QSizePolicy,
    QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette


# ══════════════════════════════════════════════════════════
#  RENK PALETİ — Mavi/gri/beyaz araç teması
# ══════════════════════════════════════════════════════════
C = {
    "bg":        "#F4F7FB",
    "sidebar":   "#FFFFFF",
    "card":      "#FFFFFF",
    "border":    "#D6E4F0",
    "accent":    "#1565C0",
    "accent2":   "#0D47A1",
    "accent3":   "#42A5F5",
    "gold":      "#F57C00",
    "gold2":     "#FFB300",
    "success":   "#2ECC71",
    "warning":   "#F39C12",
    "danger":    "#E74C3C",
    "text":      "#1A2A3A",
    "text_sub":  "#4A6080",
    "text_dim":  "#90A8C0",
    "row_alt":   "#EEF4FB",
    "row_sel":   "#DBEAFE",
    "input_bg":  "#F4F7FB",
    "tag_bg":    "#EBF4FF",
    "sidebar_w": 240,
}

ARAC_TIPLERI = ["Sedan", "SUV", "Hatchback", "Minivan", "Elektrikli", "Kamyonet"]
MARKALAR     = ["Toyota", "Ford", "BMW", "Mercedes", "Tesla", "Renault", "Volkswagen", "Hyundai"]


# ── Stil yardımcıları ─────────────────────────────────────
def card_ss(border_color=None):
    bc = border_color or C['border']
    return f"""
        QFrame{{
            background:{C['card']};
            border:1.5px solid {bc};
            border-radius:16px;
        }}
    """

def btn_primary_ss():
    return f"""
        QPushButton{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['accent2']},stop:1 {C['accent']});
            color:#fff;border:none;border-radius:10px;
            padding:10px 22px;font-size:13px;font-weight:700;
        }}
        QPushButton:hover{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['accent']},stop:1 {C['accent3']});
        }}
        QPushButton:pressed{{background:{C['accent2']};}}
    """

def btn_gold_ss():
    return f"""
        QPushButton{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['gold']},stop:1 {C['gold2']});
            color:#fff;border:none;border-radius:10px;
            padding:10px 22px;font-size:13px;font-weight:700;
        }}
        QPushButton:hover{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C['gold2']},stop:1 #FFD080);
        }}
    """

def btn_success_ss():
    return f"""
        QPushButton{{background:{C['success']};color:#fff;border:none;
            border-radius:10px;padding:10px 22px;font-size:13px;font-weight:700;}}
        QPushButton:hover{{background:#27AE60;}}
    """

def btn_danger_ss():
    return f"""
        QPushButton{{background:{C['danger']};color:#fff;border:none;
            border-radius:10px;padding:10px 22px;font-size:13px;font-weight:700;}}
        QPushButton:hover{{background:#C0392B;}}
    """

def btn_outline_ss():
    return f"""
        QPushButton{{
            background:transparent;color:{C['accent']};
            border:1.5px solid {C['accent']};border-radius:10px;
            padding:9px 20px;font-size:12px;font-weight:600;
        }}
        QPushButton:hover{{background:{C['tag_bg']};}}
    """

def input_ss():
    return f"""
        QLineEdit,QSpinBox,QDoubleSpinBox,QDateTimeEdit,QComboBox{{
            background:{C['input_bg']};color:{C['text']};
            border:1.5px solid {C['border']};border-radius:9px;
            padding:8px 12px;font-size:13px;
        }}
        QLineEdit:focus,QSpinBox:focus,QDoubleSpinBox:focus,
        QDateTimeEdit:focus,QComboBox:focus{{
            border:1.5px solid {C['accent']};
        }}
        QSpinBox::up-button,QSpinBox::down-button,
        QDoubleSpinBox::up-button,QDoubleSpinBox::down-button{{
            background:{C['border']};width:18px;border-radius:3px;
        }}
        QDateTimeEdit::drop-down,QComboBox::drop-down{{
            background:{C['border']};width:22px;border-radius:3px;
        }}
        QComboBox QAbstractItemView{{
            background:{C['card']};color:{C['text']};
            selection-background-color:{C['row_sel']};
            border:1px solid {C['border']};
        }}
    """

TABLE_SS = f"""
    QTableWidget{{
        background:{C['card']};color:{C['text']};border:none;
        gridline-color:{C['border']};font-size:13px;
        selection-background-color:{C['row_sel']};outline:none;
        alternate-background-color:{C['row_alt']};
    }}
    QTableWidget::item{{padding:9px 13px;border-bottom:1px solid {C['border']};}}
    QTableWidget::item:selected{{background:{C['row_sel']};color:{C['accent']};}}
    QHeaderView::section{{
        background:{C['bg']};color:{C['accent2']};
        padding:9px 13px;border:none;
        border-bottom:2px solid {C['accent']};
        font-size:11px;font-weight:700;letter-spacing:0.8px;
    }}
    QScrollBar:vertical{{background:{C['bg']};width:7px;border-radius:4px;}}
    QScrollBar::handle:vertical{{background:{C['border']};border-radius:4px;min-height:20px;}}
    QScrollBar::handle:vertical:hover{{background:{C['accent']};}}
    QScrollBar:horizontal{{background:{C['bg']};height:7px;border-radius:4px;}}
    QScrollBar::handle:horizontal{{background:{C['border']};border-radius:4px;}}
"""

def shadow(widget, blur=20, dy=4, alpha=25):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(blur)
    color = QColor(C['accent2'])
    color.setAlpha(alpha)
    fx.setColor(color)
    fx.setOffset(0, dy)
    widget.setGraphicsEffect(fx)


# ══════════════════════════════════════════════════════════
#  VERİ MODELİ
# ══════════════════════════════════════════════════════════

class Arac:
    """
    Araç sınıfı — sistemdeki her aracı temsil eder.
    Attributes:
        _arac_id   : benzersiz araç kimliği
        _marka     : araç markası (Toyota, BMW vb.)
        _model     : araç modeli (Corolla, X5 vb.)
        _tip       : araç tipi (Sedan, SUV vb.)
        _kilometre : toplam km
        _musait_mi : kiralama için uygun mu (bool)
        _saatlik_ucret : saat başı ücret (TL)
    """
    def __init__(self, arac_id, marka, model, tip, kilometre, saatlik_ucret):
        self._arac_id       = arac_id
        self._marka         = marka
        self._model         = model
        self._tip           = tip
        self._kilometre     = kilometre
        self._musait_mi     = True
        self._saatlik_ucret = saatlik_ucret

    # Getter metodları
    def get_arac_id(self):       return self._arac_id
    def get_marka(self):         return self._marka
    def get_model(self):         return self._model
    def get_tip(self):           return self._tip
    def get_kilometre(self):     return self._kilometre
    def get_musait_mi(self):     return self._musait_mi
    def get_saatlik_ucret(self): return self._saatlik_ucret
    def get_tam_ad(self):        return f"{self._marka} {self._model}"

    def arac_durumu_guncelle(self, musait):
        """Aracın müsaitlik durumunu günceller."""
        self._musait_mi = musait

    def kilometre_guncelle(self, eklenen_km):
        """Kiralama sonrası km değerini artırır."""
        if eklenen_km < 0:
            raise ValueError("Km negatif olamaz.")
        self._kilometre += eklenen_km


class Kullanici:
    """
    Kullanıcı sınıfı — sisteme kayıtlı her müşteriyi temsil eder.
    Attributes:
        _kullanici_id : benzersiz kullanıcı kimliği
        _ad           : kullanıcının adı soyadı
        _ehliyet_no   : ehliyet numarası (benzersiz olmalı)
        _telefon      : iletişim numarası
        _kiralamalar  : bu kullanıcıya ait Kiralama nesneleri listesi
    """
    def __init__(self, kullanici_id, ad, ehliyet_no, telefon=""):
        self._kullanici_id = kullanici_id
        self._ad           = ad
        self._ehliyet_no   = ehliyet_no
        self._telefon      = telefon
        self._kiralamalar  = []   # Kiralama nesneleri listesi

    def get_kullanici_id(self): return self._kullanici_id
    def get_ad(self):           return self._ad
    def get_ehliyet_no(self):   return self._ehliyet_no
    def get_telefon(self):      return self._telefon

    def kiralama_ekle(self, kiralama):
        """Kullanıcının geçmişine yeni kiralama ekler."""
        self._kiralamalar.append(kiralama)

    def kiralama_gecmisi(self):
        """Kullanıcıya ait tüm kiralamaları döndürür."""
        return list(self._kiralamalar)

    def aktif_kiralama(self):
        """Devam eden (bitmemiş) kiralamayı döndürür, yoksa None."""
        for k in self._kiralamalar:
            if k.get_aktif():
                return k
        return None


class Kiralama:
    """
    Kiralama sınıfı — bir araç-kullanıcı kiralama işlemini temsil eder.
    Attributes:
        _kiralama_id    : benzersiz kiralama kimliği
        _arac           : Arac nesnesi
        _kullanici      : Kullanici nesnesi
        _baslangic_saati: datetime — kiralama başlangıcı
        _bitis_saati    : datetime — kiralama bitişi (None ise devam ediyor)
        _aktif          : bool
    """
    def __init__(self, kiralama_id, arac: Arac, kullanici: Kullanici, baslangic_saati: datetime):
        self._kiralama_id     = kiralama_id
        self._arac            = arac
        self._kullanici       = kullanici
        self._baslangic_saati = baslangic_saati
        self._bitis_saati     = None
        self._aktif           = True
        self._toplam_ucret    = 0.0

    def get_kiralama_id(self):     return self._kiralama_id
    def get_arac(self):            return self._arac
    def get_kullanici(self):       return self._kullanici
    def get_baslangic_saati(self): return self._baslangic_saati
    def get_bitis_saati(self):     return self._bitis_saati
    def get_aktif(self):           return self._aktif
    def get_toplam_ucret(self):    return self._toplam_ucret

    def kiralama_baslat(self):
        """Kiralama başlatılır; aracı meşgul durumuna getirir."""
        self._arac.arac_durumu_guncelle(False)
        return True, f"✓ Kiralama #{self._kiralama_id} başlatıldı."

    def kiralama_bitir(self, bitis_saati: datetime, eklenen_km: int = 0):
        """
        Kiralama bitirilir; süre hesaplanır, ücret belirlenir,
        araç tekrar müsait yapılır.
        """
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
        """Kiralama özetini sözlük olarak döndürür."""
        sure = "Devam ediyor"
        if self._bitis_saati:
            dk = int((self._bitis_saati - self._baslangic_saati).total_seconds() / 60)
            sure = f"{dk // 60}s {dk % 60}dk"
        return {
            "id":         self._kiralama_id,
            "arac":       self._arac.get_tam_ad(),
            "kullanici":  self._kullanici.get_ad(),
            "baslangic":  self._baslangic_saati.strftime("%d.%m.%Y %H:%M"),
            "bitis":      self._bitis_saati.strftime("%d.%m.%Y %H:%M") if self._bitis_saati else "—",
            "sure":       sure,
            "ucret":      f"₺{self._toplam_ucret:.2f}",
            "aktif":      self._aktif,
        }


class PaylasimSistemi:
    """
    Ana sistem sınıfı — araçları, kullanıcıları ve kiralamaları yönetir.
    Veri yapıları:
        _araclar    : dict  {arac_id -> Arac}
        _kullanicilar: dict {kullanici_id -> Kullanici}
        _kiralamalar: list  [Kiralama]
    """
    def __init__(self):
        self._araclar       = {}
        self._kullanicilar  = {}
        self._kiralamalar   = []
        self._sonraki_kid   = 1   # otomatik kiralama ID sayacı

    # ── Araç işlemleri ──────────────────────────────────
    def arac_ekle(self, arac: Arac):
        if arac.get_arac_id() in self._araclar:
            return False, f"ID {arac.get_arac_id()} zaten kayıtlı."
        self._araclar[arac.get_arac_id()] = arac
        return True, f"✓ '{arac.get_tam_ad()}' sisteme eklendi."

    def get_araclar(self):       return self._araclar
    def get_musait_araclar(self):
        return {k: v for k, v in self._araclar.items() if v.get_musait_mi()}

    # ── Kullanıcı işlemleri ─────────────────────────────
    def kullanici_ekle(self, kullanici: Kullanici):
        if kullanici.get_kullanici_id() in self._kullanicilar:
            return False, f"ID {kullanici.get_kullanici_id()} zaten kayıtlı."
        for u in self._kullanicilar.values():
            if u.get_ehliyet_no() == kullanici.get_ehliyet_no():
                return False, "Bu ehliyet numarası zaten kayıtlı."
        self._kullanicilar[kullanici.get_kullanici_id()] = kullanici
        return True, f"✓ '{kullanici.get_ad()}' kayıt edildi."

    def get_kullanicilar(self): return self._kullanicilar

    # ── Kiralama işlemleri ──────────────────────────────
    def kiralama_baslat(self, arac_id, kullanici_id, baslangic: datetime):
        if arac_id not in self._araclar:
            return False, "Araç bulunamadı."
        if kullanici_id not in self._kullanicilar:
            return False, "Kullanıcı bulunamadı."
        arac = self._araclar[arac_id]
        if not arac.get_musait_mi():
            return False, "Araç şu an başka bir kullanıcıda."
        kullanici = self._kullanicilar[kullanici_id]
        if kullanici.aktif_kiralama():
            return False, f"'{kullanici.get_ad()}' zaten aktif bir kiralamaya sahip."

        k = Kiralama(self._sonraki_kid, arac, kullanici, baslangic)
        self._sonraki_kid += 1
        ok, msg = k.kiralama_baslat()
        if ok:
            self._kiralamalar.append(k)
            kullanici.kiralama_ekle(k)
        return ok, msg

    def kiralama_bitir(self, kiralama_id, bitis: datetime, eklenen_km: int = 0):
        for k in self._kiralamalar:
            if k.get_kiralama_id() == kiralama_id and k.get_aktif():
                return k.kiralama_bitir(bitis, eklenen_km)
        return False, "Aktif kiralama bulunamadı."

    def get_kiralamalar(self):        return list(self._kiralamalar)
    def get_aktif_kiralamalar(self):  return [k for k in self._kiralamalar if k.get_aktif()]
    def get_gecmis_kiralamalar(self): return [k for k in self._kiralamalar if not k.get_aktif()]

    def toplam_gelir(self):
        return sum(k.get_toplam_ucret() for k in self._kiralamalar if not k.get_aktif())


# ══════════════════════════════════════════════════════════
#  BİLEŞEN: KPI Kartı
# ══════════════════════════════════════════════════════════
class KpiCard(QFrame):
    def __init__(self, ikon, baslik, deger, alt, renk, parent=None):
        super().__init__(parent)
        self.setFixedHeight(118)
        self.setStyleSheet(f"""
            QFrame{{
                background:{C['card']};
                border:1.5px solid {C['border']};
                border-radius:16px;
                border-top:4px solid {renk};
            }}
        """)
        shadow(self, blur=16, dy=3)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 12)
        lay.setSpacing(3)
        top_row = QHBoxLayout()
        lbl_i = QLabel(ikon)
        lbl_i.setStyleSheet("font-size:22px;background:transparent;border:none;")
        lbl_t = QLabel(baslik.upper())
        lbl_t.setStyleSheet(f"color:{C['text_sub']};font-size:10px;font-weight:700;letter-spacing:1px;background:transparent;border:none;")
        top_row.addWidget(lbl_i); top_row.addWidget(lbl_t); top_row.addStretch()
        lay.addLayout(top_row)
        lbl_v = QLabel(str(deger))
        lbl_v.setStyleSheet(f"color:{renk};font-size:27px;font-weight:800;background:transparent;border:none;")
        lbl_a = QLabel(alt)
        lbl_a.setStyleSheet(f"color:{C['text_dim']};font-size:11px;background:transparent;border:none;")
        lay.addWidget(lbl_v); lay.addWidget(lbl_a)


# ══════════════════════════════════════════════════════════
#  BİLEŞEN: Sidebar Butonu
# ══════════════════════════════════════════════════════════
class SideBtn(QPushButton):
    def __init__(self, ikon, metin, parent=None):
        super().__init__(f"  {ikon}  {metin}", parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self._refresh(False)

    def _refresh(self, aktif):
        if aktif:
            self.setStyleSheet(f"""
                QPushButton{{
                    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 rgba(21,101,192,0.10), stop:1 rgba(21,101,192,0.03));
                    color:{C['accent']};
                    border:none;border-left:3px solid {C['accent']};
                    border-radius:0;text-align:left;padding-left:18px;
                    font-size:13px;font-weight:700;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton{{
                    background:transparent;color:{C['text_sub']};
                    border:none;border-left:3px solid transparent;
                    border-radius:0;text-align:left;padding-left:18px;font-size:13px;
                }}
                QPushButton:hover{{
                    background:rgba(21,101,192,0.05);color:{C['text']};
                    border-left:3px solid {C['accent3']};
                }}
            """)

    def setChecked(self, v):
        super().setChecked(v)
        self._refresh(v)


# ══════════════════════════════════════════════════════════
#  EKRAN 1: Dashboard
# ══════════════════════════════════════════════════════════
class DashboardPage(QWidget):
    def __init__(self, sistem: PaylasimSistemi, parent=None):
        super().__init__(parent)
        self.sistem = sistem
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(18)

        ust = QHBoxLayout()
        lbl = QLabel("🚗  Sistem Genel Bakışı")
        lbl.setStyleSheet(f"color:{C['text']};font-size:22px;font-weight:800;")
        ust.addWidget(lbl); ust.addStretch()
        self.lbl_tarih = QLabel()
        self.lbl_tarih.setStyleSheet(f"color:{C['text_sub']};font-size:12px;")
        ust.addWidget(self.lbl_tarih)
        lay.addLayout(ust)

        self.kpi_row = QHBoxLayout(); self.kpi_row.setSpacing(14)
        lay.addLayout(self.kpi_row)

        sub = QLabel("Aktif Kiralamalar")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;letter-spacing:0.5px;")
        lay.addWidget(sub)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(
            ["Kiralama ID", "Araç", "Kullanıcı", "Başlangıç", "Saatlik Ücret", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)
        self.refresh()

    def refresh(self):
        self.lbl_tarih.setText(datetime.now().strftime("%d %B %Y"))
        toplam_arac    = len(self.sistem.get_araclar())
        musait_arac    = len(self.sistem.get_musait_araclar())
        aktif_k        = len(self.sistem.get_aktif_kiralamalar())
        kullanici_say  = len(self.sistem.get_kullanicilar())
        gelir          = self.sistem.toplam_gelir()

        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.kpi_row.addWidget(KpiCard("🚗", "Toplam Araç",      toplam_arac,            "sistemde kayıtlı",      C['accent']))
        self.kpi_row.addWidget(KpiCard("✅", "Müsait Araç",      musait_arac,            "kiralama hazır",         C['success']))
        self.kpi_row.addWidget(KpiCard("🔑", "Aktif Kiralama",   aktif_k,                "devam eden kiralama",    C['warning']))
        self.kpi_row.addWidget(KpiCard("👤", "Kayıtlı Üye",      kullanici_say,          "sisteme kayıtlı",        C['gold']))
        self.kpi_row.addWidget(KpiCard("💰", "Toplam Gelir",      f"₺{gelir:,.0f}",      "tamamlanan kiralamar",   C['accent2']))

        self.tablo.setRowCount(0)
        for k in self.sistem.get_aktif_kiralamalar():
            bilgi = k.kiralama_bilgisi()
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(bilgi["id"])))
            self.tablo.setItem(r, 1, QTableWidgetItem(bilgi["arac"]))
            self.tablo.setItem(r, 2, QTableWidgetItem(bilgi["kullanici"]))
            self.tablo.setItem(r, 3, QTableWidgetItem(bilgi["baslangic"]))
            self.tablo.setItem(r, 4, QTableWidgetItem(f"₺{k.get_arac().get_saatlik_ucret():.2f}/sa"))
            durum = QTableWidgetItem("🔑  Devam Ediyor")
            durum.setForeground(QColor(C['warning']))
            self.tablo.setItem(r, 5, durum)
            self.tablo.setRowHeight(r, 44)


# ══════════════════════════════════════════════════════════
#  EKRAN 2: Araç Yönetimi
# ══════════════════════════════════════════════════════════
class AracPage(QWidget):
    def __init__(self, sistem: PaylasimSistemi, dashboard: DashboardPage, parent=None):
        super().__init__(parent)
        self.sistem    = sistem
        self.dashboard = dashboard
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _lbl(self, txt):
        l = QLabel(txt)
        l.setStyleSheet(f"color:{C['text_sub']};font-size:11px;font-weight:700;letter-spacing:0.3px;")
        return l

    def _section_lbl(self, txt, renk):
        l = QLabel(txt)
        l.setStyleSheet(f"color:{renk};font-size:13px;font-weight:700;background:transparent;")
        return l

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")

        container = QWidget(); container.setStyleSheet(f"background:{C['bg']};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        lbl = QLabel("🚗  Araç Yönetimi")
        lbl.setStyleSheet(f"color:{C['text']};font-size:22px;font-weight:800;")
        lay.addWidget(lbl)

        # ── Yeni araç formu ──────────────────────────────
        kart = QFrame(); kart.setStyleSheet(card_ss(C['accent'] + "44")); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22, 18, 22, 18); klay.setSpacing(12)
        klay.addWidget(self._section_lbl("➕  Yeni Araç Ekle", C['accent']))

        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_id     = QSpinBox();       self.inp_id.setRange(1, 9999)
        self.inp_marka  = QComboBox();      self.inp_marka.addItems(MARKALAR)
        self.inp_model  = QLineEdit();      self.inp_model.setPlaceholderText("örn. Corolla, X5")
        self.inp_tip    = QComboBox();      self.inp_tip.addItems(ARAC_TIPLERI)
        self.inp_km     = QSpinBox();       self.inp_km.setRange(0, 999999); self.inp_km.setSuffix(" km")
        self.inp_ucret  = QDoubleSpinBox(); self.inp_ucret.setRange(10, 9999); self.inp_ucret.setDecimals(2); self.inp_ucret.setSuffix(" ₺/sa"); self.inp_ucret.setValue(150)

        for w in [self.inp_id, self.inp_marka, self.inp_model, self.inp_tip,
                  self.inp_km, self.inp_ucret]:
            w.setStyleSheet(input_ss())

        row0 = [("Araç ID", self.inp_id), ("Marka", self.inp_marka),
                ("Model", self.inp_model), ("Tip", self.inp_tip)]
        row1 = [("Kilometre", self.inp_km), ("Saatlik Ücret", self.inp_ucret)]
        for col, (lt, wid) in enumerate(row0):
            grid.addWidget(self._lbl(lt), 0, col); grid.addWidget(wid, 1, col)
        for col, (lt, wid) in enumerate(row1):
            grid.addWidget(self._lbl(lt), 2, col); grid.addWidget(wid, 3, col)
        klay.addLayout(grid)

        btn_ekle = QPushButton("✚  Araç Ekle")
        btn_ekle.setStyleSheet(btn_primary_ss()); btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.clicked.connect(self._ekle); btn_ekle.setFixedWidth(150)
        klay.addWidget(btn_ekle)
        lay.addWidget(kart)

        # ── Tablo ─────────────────────────────────────────
        sub = QLabel("Tüm Araçlar")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        lay.addWidget(sub)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(
            ["ID", "Marka", "Model", "Tip", "Kilometre", "Saatlik Ücret", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)

        scroll.setWidget(container)
        main = QVBoxLayout(self); main.setContentsMargins(0, 0, 0, 0); main.addWidget(scroll)
        self._tablo_yenile()

    def _tablo_yenile(self):
        self.tablo.setRowCount(0)
        for a in self.sistem.get_araclar().values():
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(a.get_arac_id())))
            self.tablo.setItem(r, 1, QTableWidgetItem(a.get_marka()))
            self.tablo.setItem(r, 2, QTableWidgetItem(a.get_model()))
            self.tablo.setItem(r, 3, QTableWidgetItem(a.get_tip()))
            self.tablo.setItem(r, 4, QTableWidgetItem(f"{a.get_kilometre():,} km"))
            self.tablo.setItem(r, 5, QTableWidgetItem(f"₺{a.get_saatlik_ucret():.2f}/sa"))

            if a.get_musait_mi():
                d = QTableWidgetItem("✓  Müsait"); d.setForeground(QColor(C['success']))
            else:
                d = QTableWidgetItem("✗  Kirada"); d.setForeground(QColor(C['danger']))
            self.tablo.setItem(r, 6, d)
            self.tablo.setRowHeight(r, 44)

    def _bildirim(self, mesaj, ok=True):
        renk = C['success'] if ok else C['danger']
        dlg = QMessageBox(self)
        dlg.setText(mesaj)
        dlg.setWindowTitle("Sistem")
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}} QLabel{{color:{renk};font-size:13px;}}")
        dlg.exec_()

    def _ekle(self):
        try:
            model = self.inp_model.text().strip()
            if not model: raise ValueError("Model adı boş olamaz.")
            a = Arac(
                self.inp_id.value(),
                self.inp_marka.currentText(),
                model,
                self.inp_tip.currentText(),
                self.inp_km.value(),
                self.inp_ucret.value()
            )
            ok, msg = self.sistem.arac_ekle(a)
            self._bildirim(msg, ok)
            if ok: self._tablo_yenile(); self.dashboard.refresh()
        except Exception as e:
            self._bildirim(str(e), False)


# ══════════════════════════════════════════════════════════
#  EKRAN 3: Kullanıcı Yönetimi
# ══════════════════════════════════════════════════════════
class KullaniciPage(QWidget):
    def __init__(self, sistem: PaylasimSistemi, dashboard: DashboardPage, parent=None):
        super().__init__(parent)
        self.sistem    = sistem
        self.dashboard = dashboard
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _lbl(self, txt):
        l = QLabel(txt)
        l.setStyleSheet(f"color:{C['text_sub']};font-size:11px;font-weight:700;")
        return l

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        lbl = QLabel("👤  Kullanıcı Yönetimi")
        lbl.setStyleSheet(f"color:{C['text']};font-size:22px;font-weight:800;")
        lay.addWidget(lbl)

        # ── Yeni kullanıcı formu ─────────────────────────
        kart = QFrame(); kart.setStyleSheet(card_ss(C['gold'] + "66")); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22, 18, 22, 18); klay.setSpacing(12)
        sl = QLabel("➕  Yeni Kullanıcı Kaydı")
        sl.setStyleSheet(f"color:{C['gold']};font-size:13px;font-weight:700;background:transparent;")
        klay.addWidget(sl)

        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_kid    = QSpinBox();  self.inp_kid.setRange(1, 9999)
        self.inp_ad     = QLineEdit(); self.inp_ad.setPlaceholderText("Ad Soyad")
        self.inp_ehliyet= QLineEdit(); self.inp_ehliyet.setPlaceholderText("Ehliyet numarası")
        self.inp_tel    = QLineEdit(); self.inp_tel.setPlaceholderText("Telefon (opsiyonel)")

        for w in [self.inp_kid, self.inp_ad, self.inp_ehliyet, self.inp_tel]:
            w.setStyleSheet(input_ss())

        cols = [("Kullanıcı ID", self.inp_kid), ("Ad Soyad", self.inp_ad),
                ("Ehliyet No", self.inp_ehliyet), ("Telefon", self.inp_tel)]
        for col, (lt, wid) in enumerate(cols):
            grid.addWidget(self._lbl(lt), 0, col); grid.addWidget(wid, 1, col)
        klay.addLayout(grid)

        btn = QPushButton("✚  Kullanıcı Ekle")
        btn.setStyleSheet(btn_gold_ss()); btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._ekle); btn.setFixedWidth(170)
        klay.addWidget(btn)
        lay.addWidget(kart)

        # ── Kiralama geçmişi sorgulama ───────────────────
        kart2 = QFrame(); kart2.setStyleSheet(card_ss()); shadow(kart2)
        k2lay = QVBoxLayout(kart2); k2lay.setContentsMargins(22, 16, 22, 16); k2lay.setSpacing(10)
        sl2 = QLabel("📋  Kullanıcı Kiralama Geçmişi")
        sl2.setStyleSheet(f"color:{C['accent']};font-size:13px;font-weight:700;background:transparent;")
        k2lay.addWidget(sl2)
        row = QHBoxLayout(); row.setSpacing(10)
        self.g_kid = QSpinBox(); self.g_kid.setRange(1, 9999)
        self.g_kid.setStyleSheet(input_ss()); self.g_kid.setFixedWidth(120)
        row.addWidget(self._lbl("Kullanıcı ID")); row.addWidget(self.g_kid)
        b_sor = QPushButton("🔍  Sorgula"); b_sor.setStyleSheet(btn_outline_ss())
        b_sor.setCursor(Qt.PointingHandCursor); b_sor.clicked.connect(self._sorgula)
        row.addWidget(b_sor); row.addStretch()
        k2lay.addLayout(row)
        lay.addWidget(kart2)

        # ── Kullanıcı listesi ─────────────────────────────
        sub = QLabel("Kayıtlı Kullanıcılar")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        lay.addWidget(sub)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(
            ["ID", "Ad Soyad", "Ehliyet No", "Telefon", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)
        self._tablo_yenile()

    def _tablo_yenile(self):
        self.tablo.setRowCount(0)
        for u in self.sistem.get_kullanicilar().values():
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(u.get_kullanici_id())))
            self.tablo.setItem(r, 1, QTableWidgetItem(u.get_ad()))
            self.tablo.setItem(r, 2, QTableWidgetItem(u.get_ehliyet_no()))
            self.tablo.setItem(r, 3, QTableWidgetItem(u.get_telefon() or "—"))
            aktif = u.aktif_kiralama()
            if aktif:
                d = QTableWidgetItem(f"🔑  Araçta ({aktif.get_arac().get_tam_ad()})")
                d.setForeground(QColor(C['warning']))
            else:
                d = QTableWidgetItem("✓  Müsait"); d.setForeground(QColor(C['success']))
            self.tablo.setItem(r, 4, d)
            self.tablo.setRowHeight(r, 44)

    def _bildirim(self, mesaj, ok=True):
        renk = C['success'] if ok else C['danger']
        dlg = QMessageBox(self)
        dlg.setText(mesaj)
        dlg.setWindowTitle("Sistem")
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}} QLabel{{color:{renk};font-size:13px;}}")
        dlg.exec_()

    def _ekle(self):
        try:
            ad = self.inp_ad.text().strip()
            if not ad: raise ValueError("Ad boş olamaz.")
            ehliyet = self.inp_ehliyet.text().strip()
            if not ehliyet: raise ValueError("Ehliyet numarası zorunludur.")
            u = Kullanici(self.inp_kid.value(), ad, ehliyet, self.inp_tel.text().strip())
            ok, msg = self.sistem.kullanici_ekle(u)
            self._bildirim(msg, ok)
            if ok: self._tablo_yenile(); self.dashboard.refresh()
        except Exception as e:
            self._bildirim(str(e), False)

    def _sorgula(self):
        uid = self.g_kid.value()
        kullanicilar = self.sistem.get_kullanicilar()
        if uid not in kullanicilar:
            self._bildirim("Kullanıcı bulunamadı.", False); return
        u     = kullanicilar[uid]
        gecmis = u.kiralama_gecmisi()
        if not gecmis:
            self._bildirim(f"'{u.get_ad()}' için kiralama geçmişi yok."); return

        mesaj_satırlar = [f"📋  {u.get_ad()} — Kiralama Geçmişi\n"]
        for k in gecmis:
            b = k.kiralama_bilgisi()
            mesaj_satırlar.append(
                f"#{b['id']}  {b['arac']}  |  {b['baslangic']} → {b['bitis']}  |  Süre: {b['sure']}  |  Ücret: {b['ucret']}"
            )
        self._bildirim("\n".join(mesaj_satırlar))


# ══════════════════════════════════════════════════════════
#  EKRAN 4: Kiralama İşlemleri
# ══════════════════════════════════════════════════════════
class KiralamePage(QWidget):
    def __init__(self, sistem: PaylasimSistemi, dashboard: DashboardPage, parent=None):
        super().__init__(parent)
        self.sistem    = sistem
        self.dashboard = dashboard
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _lbl(self, txt):
        l = QLabel(txt)
        l.setStyleSheet(f"color:{C['text_sub']};font-size:11px;font-weight:700;")
        return l

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        container = QWidget(); container.setStyleSheet(f"background:{C['bg']};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        lbl = QLabel("🔑  Kiralama İşlemleri")
        lbl.setStyleSheet(f"color:{C['text']};font-size:22px;font-weight:800;")
        lay.addWidget(lbl)

        # ── Kiralama başlat ──────────────────────────────
        kart = QFrame(); kart.setStyleSheet(card_ss(C['success'] + "66")); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22, 18, 22, 18); klay.setSpacing(12)
        sl = QLabel("▶  Kiralama Başlat")
        sl.setStyleSheet(f"color:{C['success']};font-size:13px;font-weight:700;background:transparent;")
        klay.addWidget(sl)
        grid = QGridLayout(); grid.setSpacing(10)
        self.b_arac_id = QSpinBox(); self.b_arac_id.setRange(1, 9999)
        self.b_user_id = QSpinBox(); self.b_user_id.setRange(1, 9999)
        self.b_bas_dt  = QDateTimeEdit(); self.b_bas_dt.setCalendarPopup(True)
        self.b_bas_dt.setDateTime(QDateTime.currentDateTime())
        for w in [self.b_arac_id, self.b_user_id, self.b_bas_dt]: w.setStyleSheet(input_ss())
        cols = [("Araç ID", self.b_arac_id), ("Kullanıcı ID", self.b_user_id),
                ("Başlangıç Saati", self.b_bas_dt)]
        for col, (lt, wid) in enumerate(cols):
            grid.addWidget(self._lbl(lt), 0, col); grid.addWidget(wid, 1, col)
        klay.addLayout(grid)
        btn_bas = QPushButton("▶  Kiralama Başlat"); btn_bas.setStyleSheet(btn_success_ss())
        btn_bas.setCursor(Qt.PointingHandCursor); btn_bas.clicked.connect(self._baslat)
        btn_bas.setFixedWidth(170)
        klay.addWidget(btn_bas)
        lay.addWidget(kart)

        # ── Kiralama bitir ───────────────────────────────
        kart2 = QFrame(); kart2.setStyleSheet(card_ss(C['danger'] + "55")); shadow(kart2)
        k2lay = QVBoxLayout(kart2); k2lay.setContentsMargins(22, 18, 22, 18); k2lay.setSpacing(12)
        sl2 = QLabel("■  Kiralama Bitir")
        sl2.setStyleSheet(f"color:{C['danger']};font-size:13px;font-weight:700;background:transparent;")
        k2lay.addWidget(sl2)
        grid2 = QGridLayout(); grid2.setSpacing(10)
        self.e_kid  = QSpinBox(); self.e_kid.setRange(1, 9999)
        self.e_bit_dt = QDateTimeEdit(); self.e_bit_dt.setCalendarPopup(True)
        self.e_bit_dt.setDateTime(QDateTime.currentDateTime())
        self.e_km   = QSpinBox(); self.e_km.setRange(0, 9999); self.e_km.setSuffix(" km")
        for w in [self.e_kid, self.e_bit_dt, self.e_km]: w.setStyleSheet(input_ss())
        cols2 = [("Kiralama ID", self.e_kid), ("Bitiş Saati", self.e_bit_dt),
                 ("Eklenen KM", self.e_km)]
        for col, (lt, wid) in enumerate(cols2):
            grid2.addWidget(self._lbl(lt), 0, col); grid2.addWidget(wid, 1, col)
        k2lay.addLayout(grid2)
        btn_bit = QPushButton("■  Kiralama Bitir"); btn_bit.setStyleSheet(btn_danger_ss())
        btn_bit.setCursor(Qt.PointingHandCursor); btn_bit.clicked.connect(self._bitir)
        btn_bit.setFixedWidth(170)
        k2lay.addWidget(btn_bit)
        lay.addWidget(kart2)

        # ── Kiralama geçmişi tablosu ──────────────────────
        sub = QLabel("Tüm Kiralamalar")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        lay.addWidget(sub)
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(
            ["ID", "Araç", "Kullanıcı", "Başlangıç", "Bitiş", "Süre", "Ücret"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)
        scroll.setWidget(container)
        main = QVBoxLayout(self); main.setContentsMargins(0, 0, 0, 0); main.addWidget(scroll)
        self._tablo_yenile()

    def _tablo_yenile(self):
        self.tablo.setRowCount(0)
        for k in reversed(self.sistem.get_kiralamalar()):
            b = k.kiralama_bilgisi()
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(b["id"])))
            self.tablo.setItem(r, 1, QTableWidgetItem(b["arac"]))
            self.tablo.setItem(r, 2, QTableWidgetItem(b["kullanici"]))
            self.tablo.setItem(r, 3, QTableWidgetItem(b["baslangic"]))
            self.tablo.setItem(r, 4, QTableWidgetItem(b["bitis"]))
            self.tablo.setItem(r, 5, QTableWidgetItem(b["sure"]))
            ucret_item = QTableWidgetItem(b["ucret"])
            if b["aktif"]:
                ucret_item.setForeground(QColor(C['warning']))
            else:
                ucret_item.setForeground(QColor(C['success']))
            self.tablo.setItem(r, 6, ucret_item)
            self.tablo.setRowHeight(r, 44)

    def _bildirim(self, mesaj, ok=True):
        renk = C['success'] if ok else C['danger']
        dlg = QMessageBox(self)
        dlg.setText(mesaj)
        dlg.setWindowTitle("Kiralama")
        dlg.setStyleSheet(f"QMessageBox{{background:{C['card']};}} QLabel{{color:{renk};font-size:13px;}}")
        dlg.exec_()

    def _qdt_to_dt(self, qdt):
        return datetime(qdt.date().year(), qdt.date().month(), qdt.date().day(),
                        qdt.time().hour(), qdt.time().minute())

    def _baslat(self):
        baslangic = self._qdt_to_dt(self.b_bas_dt.dateTime())
        ok, msg   = self.sistem.kiralama_baslat(
            self.b_arac_id.value(), self.b_user_id.value(), baslangic)
        self._bildirim(msg, ok)
        if ok: self._tablo_yenile(); self.dashboard.refresh()

    def _bitir(self):
        bitis  = self._qdt_to_dt(self.e_bit_dt.dateTime())
        ok, msg = self.sistem.kiralama_bitir(
            self.e_kid.value(), bitis, self.e_km.value())
        self._bildirim(msg, ok)
        if ok: self._tablo_yenile(); self.dashboard.refresh()


# ══════════════════════════════════════════════════════════
#  EKRAN 5: Gelir Raporu
# ══════════════════════════════════════════════════════════
class RaporPage(QWidget):
    def __init__(self, sistem: PaylasimSistemi, parent=None):
        super().__init__(parent)
        self.sistem = sistem
        self.setStyleSheet(f"background:{C['bg']};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        ust = QHBoxLayout()
        lbl = QLabel("📊  Gelir & Performans Raporu")
        lbl.setStyleSheet(f"color:{C['text']};font-size:22px;font-weight:800;")
        ust.addWidget(lbl); ust.addStretch()
        btn = QPushButton("↻  Yenile"); btn.setStyleSheet(btn_outline_ss())
        btn.setCursor(Qt.PointingHandCursor); btn.clicked.connect(self.refresh)
        ust.addWidget(btn)
        lay.addLayout(ust)

        self.kpi_row = QHBoxLayout(); self.kpi_row.setSpacing(14)
        lay.addLayout(self.kpi_row)

        sub = QLabel("Tamamlanan Kiralamalar — Detay")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        lay.addWidget(sub)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(
            ["Araç", "Kullanıcı", "Başlangıç", "Bitiş", "Süre", "Ücret"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)

        self.lbl_toplam = QLabel()
        self.lbl_toplam.setAlignment(Qt.AlignRight)
        self.lbl_toplam.setStyleSheet(f"""
            color:{C['accent']};font-size:15px;font-weight:800;
            padding:12px 18px;background:{C['card']};
            border:1.5px solid {C['border']};border-radius:10px;
        """)
        lay.addWidget(self.lbl_toplam)
        self.refresh()

    def refresh(self):
        gecmis = self.sistem.get_gecmis_kiralamalar()
        aktif_k = len(self.sistem.get_aktif_kiralamalar())
        toplam_gelir = self.sistem.toplam_gelir()
        musait = len(self.sistem.get_musait_araclar())

        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.kpi_row.addWidget(KpiCard("💰", "Toplam Gelir",       f"₺{toplam_gelir:,.2f}", "tüm zamanlar",         C['success']))
        self.kpi_row.addWidget(KpiCard("📋", "Tamamlanan",         len(gecmis),             "kiralama işlemi",       C['accent']))
        self.kpi_row.addWidget(KpiCard("🔑", "Devam Eden",         aktif_k,                 "aktif kiralama",        C['warning']))
        self.kpi_row.addWidget(KpiCard("🚗", "Müsait Araç",        musait,                  "şu an kiralanabilir",   C['gold']))

        self.tablo.setRowCount(0)
        for k in reversed(gecmis):
            b = k.kiralama_bilgisi()
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(b["arac"]))
            self.tablo.setItem(r, 1, QTableWidgetItem(b["kullanici"]))
            self.tablo.setItem(r, 2, QTableWidgetItem(b["baslangic"]))
            self.tablo.setItem(r, 3, QTableWidgetItem(b["bitis"]))
            self.tablo.setItem(r, 4, QTableWidgetItem(b["sure"]))
            ucret = QTableWidgetItem(b["ucret"]); ucret.setForeground(QColor(C['success']))
            self.tablo.setItem(r, 5, ucret)
            self.tablo.setRowHeight(r, 44)

        self.lbl_toplam.setText(f"Toplam Gelir:  ₺{toplam_gelir:,.2f}  |  "
                                 f"İşlem Sayısı: {len(gecmis)}")


# ══════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚗  CarShare — Araç Paylaşım Yönetim Sistemi")
        self.setMinimumSize(1200, 720)
        self.resize(1380, 820)
        self.setStyleSheet(f"QMainWindow{{background:{C['bg']};color:{C['text']};}}")
        self.sistem = self._demo_veri()
        self._build_ui()
        self._saat_timer()

    # ── Demo veri ─────────────────────────────────────────
    def _demo_veri(self):
        s = PaylasimSistemi()

        # Araçlar
        araclar = [
            Arac(1, "Toyota",     "Corolla",    "Sedan",      45000, 180.0),
            Arac(2, "Ford",       "Focus",      "Hatchback",  62000, 150.0),
            Arac(3, "BMW",        "X3",         "SUV",        28000, 350.0),
            Arac(4, "Tesla",      "Model 3",    "Elektrikli",  8000, 420.0),
            Arac(5, "Renault",    "Clio",       "Hatchback",  91000, 120.0),
            Arac(6, "Mercedes",   "Vito",       "Minivan",    55000, 280.0),
        ]
        for a in araclar:
            s.arac_ekle(a)

        # Kullanıcılar
        kullanicilar = [
            Kullanici(1, "Ahmet Yılmaz",   "34ABC001", "0532 111 22 33"),
            Kullanici(2, "Ayşe Kaya",      "06DEF002", "0541 333 44 55"),
            Kullanici(3, "Mehmet Demir",   "35GHI003", "0555 666 77 88"),
            Kullanici(4, "Zeynep Çelik",   "16JKL004", "0544 999 00 11"),
        ]
        for u in kullanicilar:
            s.kullanici_ekle(u)

        # Demo kiralamaları — geçmiş
        bas1 = datetime.now() - timedelta(hours=5)
        bit1 = datetime.now() - timedelta(hours=2)
        s.kiralama_baslat(1, 1, bas1)
        s.kiralama_bitir(1, bit1, 150)

        bas2 = datetime.now() - timedelta(hours=8)
        bit2 = datetime.now() - timedelta(hours=1)
        s.kiralama_baslat(5, 2, bas2)
        s.kiralama_bitir(2, bit2, 320)

        # Aktif kiralamar
        s.kiralama_baslat(3, 3, datetime.now() - timedelta(hours=1, minutes=30))
        s.kiralama_baslat(4, 4, datetime.now() - timedelta(minutes=45))

        return s

    # ── UI ────────────────────────────────────────────────
    def _build_ui(self):
        merkez = QWidget(); merkez.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(merkez)
        ana = QHBoxLayout(merkez); ana.setContentsMargins(0, 0, 0, 0); ana.setSpacing(0)

        # Sidebar
        sidebar = QFrame(); sidebar.setFixedWidth(C['sidebar_w'])
        sidebar.setStyleSheet(f"QFrame{{background:{C['sidebar']};border-right:1.5px solid {C['border']};}}")
        shadow(sidebar, blur=24, dy=0, alpha=18)
        sb = QVBoxLayout(sidebar); sb.setContentsMargins(0, 0, 0, 18); sb.setSpacing(0)

        logo = QFrame(); logo.setFixedHeight(88)
        logo.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {C['accent2']},stop:0.5 {C['accent']},stop:1 {C['accent3']});
        """)
        ll = QVBoxLayout(logo); ll.setContentsMargins(18, 14, 18, 14)
        t1 = QLabel("🚗  CarShare")
        t1.setStyleSheet("color:white;font-size:20px;font-weight:800;background:transparent;letter-spacing:-0.5px;")
        t2 = QLabel("Araç Paylaşım Sistemi")
        t2.setStyleSheet("color:rgba(255,255,255,0.75);font-size:10px;background:transparent;letter-spacing:0.3px;")
        ll.addWidget(t1); ll.addWidget(t2)
        sb.addWidget(logo); sb.addSpacing(14)

        self.nav = []
        pages = [("📊", "Dashboard"), ("🚗", "Araç Yönetimi"),
                 ("👤", "Kullanıcılar"), ("🔑", "Kiralamalar"), ("📊", "Raporlar")]
        for ikon, metin in pages:
            btn = SideBtn(ikon, metin)
            btn.clicked.connect(lambda _, m=metin: self._goto(m))
            sb.addWidget(btn); self.nav.append(btn)

        sb.addStretch()
        self.lbl_saat = QLabel()
        self.lbl_saat.setAlignment(Qt.AlignCenter)
        self.lbl_saat.setStyleSheet(f"color:{C['text_dim']};font-size:11px;background:transparent;padding-bottom:4px;")
        sb.addWidget(self.lbl_saat)
        ana.addWidget(sidebar)

        # İçerik alanı
        icerik = QWidget(); icerik.setStyleSheet(f"background:{C['bg']};")
        il = QVBoxLayout(icerik); il.setContentsMargins(0, 0, 0, 0); il.setSpacing(0)

        topbar = QFrame(); topbar.setFixedHeight(52)
        topbar.setStyleSheet(f"background:{C['sidebar']};border-bottom:1.5px solid {C['border']};")
        tl = QHBoxLayout(topbar); tl.setContentsMargins(24, 0, 24, 0)
        self.lbl_page = QLabel("Dashboard")
        self.lbl_page.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:600;background:transparent;")
        tl.addWidget(self.lbl_page); tl.addStretch()
        badge = QLabel("🚗  Filoya Yönetici")
        badge.setStyleSheet(f"""
            color:{C['accent']};font-size:12px;font-weight:600;
            background:{C['tag_bg']};border:1px solid {C['border']};
            border-radius:14px;padding:3px 12px;
        """)
        tl.addWidget(badge)
        il.addWidget(topbar)

        self.stack = QStackedWidget(); self.stack.setStyleSheet(f"background:{C['bg']};")
        self.p_dash    = DashboardPage(self.sistem)
        self.p_arac    = AracPage(self.sistem, self.p_dash)
        self.p_kullanici = KullaniciPage(self.sistem, self.p_dash)
        self.p_kiralama  = KiralamePage(self.sistem, self.p_dash)
        self.p_rapor     = RaporPage(self.sistem)
        for p in [self.p_dash, self.p_arac, self.p_kullanici, self.p_kiralama, self.p_rapor]:
            self.stack.addWidget(p)
        il.addWidget(self.stack)
        ana.addWidget(icerik)
        self._goto("Dashboard")

    def _goto(self, sayfa):
        idx = {"Dashboard": 0, "Araç Yönetimi": 1, "Kullanıcılar": 2,
               "Kiralamalar": 3, "Raporlar": 4}[sayfa]
        self.stack.setCurrentIndex(idx)
        self.lbl_page.setText(f"Ana Sayfa  ›  {sayfa}")
        for i, b in enumerate(self.nav): b.setChecked(i == idx)
        if idx == 0: self.p_dash.refresh()
        if idx == 4: self.p_rapor.refresh()

    def _saat_timer(self):
        self._saat_guncelle()
        t = QTimer(self); t.timeout.connect(self._saat_guncelle); t.start(1000)

    def _saat_guncelle(self):
        self.lbl_saat.setText(datetime.now().strftime("%d.%m.%Y\n%H:%M:%S"))


# ══════════════════════════════════════════════════════════
#  GİRİŞ NOKTASI
# ══════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    p = QPalette()
    p.setColor(QPalette.Window,          QColor(C['bg']))
    p.setColor(QPalette.WindowText,      QColor(C['text']))
    p.setColor(QPalette.Base,            QColor(C['card']))
    p.setColor(QPalette.AlternateBase,   QColor(C['row_alt']))
    p.setColor(QPalette.Text,            QColor(C['text']))
    p.setColor(QPalette.Button,          QColor(C['card']))
    p.setColor(QPalette.ButtonText,      QColor(C['text']))
    p.setColor(QPalette.Highlight,       QColor(C['accent']))
    p.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(p)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()