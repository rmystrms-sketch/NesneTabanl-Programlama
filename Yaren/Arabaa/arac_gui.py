import sys
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QStackedWidget, QHeaderView, QLineEdit, QGridLayout,
    QDateTimeEdit, QSpinBox, QDoubleSpinBox, QMessageBox,
    QAbstractItemView, QGraphicsDropShadowEffect, QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, QDateTime, QTimer, QRegExp
from PyQt5.QtGui import QColor, QPalette, QRegExpValidator

# ====== IMPORT FROM BACKEND ======
from arac_backend import Arac, Kullanici, PaylasimSistemi, get_mesafe
# =================================

# ══════════════════════════════════════════════════════════
#  RENK PALETİ
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
YAKIT_TIPLERI = ["Benzin", "Dizel", "Elektrik", "Hibrit"]
SEHIRLER = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"]
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
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C['accent2']},stop:1 {C['accent']});
            color:#fff;border:none;border-radius:10px; padding:10px 22px;font-size:13px;font-weight:700;
        }}
        QPushButton:hover{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C['accent']},stop:1 {C['accent3']});
        }}
        QPushButton:pressed{{background:{C['accent2']};}}
    """

def btn_gold_ss():
    return f"""
        QPushButton{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C['gold']},stop:1 {C['gold2']});
            color:#fff;border:none;border-radius:10px; padding:10px 22px;font-size:13px;font-weight:700;
        }}
        QPushButton:hover{{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {C['gold2']},stop:1 #FFD080);
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
        QDateTimeEdit:focus,QComboBox:focus{{ border:1.5px solid {C['accent']}; }}
        QSpinBox::up-button,QSpinBox::down-button,
        QDoubleSpinBox::up-button,QDoubleSpinBox::down-button{{ background:{C['border']};width:18px;border-radius:3px; }}
        QDateTimeEdit::drop-down,QComboBox::drop-down{{ background:{C['border']};width:22px;border-radius:3px; }}
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
                    background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 rgba(21,101,192,0.10), stop:1 rgba(21,101,192,0.03));
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
        self.tablo.setHorizontalHeaderLabels(["Kiralama ID", "Araç", "Kullanıcı", "Başlangıç", "Saatlik Ücret", "Durum"])
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
            self.tablo.setItem(r, 4, QTableWidgetItem(f"₺{k.get_arac().get_km_ucreti():.2f}/km"))
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

        kart = QFrame(); kart.setStyleSheet(card_ss(C['accent'] + "44")); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22, 18, 22, 18); klay.setSpacing(12)
        klay.addWidget(self._section_lbl("➕  Yeni Araç Ekle", C['accent']))

        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_id     = QSpinBox(); self.inp_id.setRange(1, 99999); self.inp_id.setEnabled(False)
        self.inp_marka  = QComboBox(); self.inp_marka.addItems(MARKALAR)
        self.inp_model  = QLineEdit(); self.inp_model.setPlaceholderText("örn. Corolla, X5")
        self.inp_tip    = QComboBox(); self.inp_tip.addItems(ARAC_TIPLERI)
        self.inp_yakit  = QComboBox(); self.inp_yakit.addItems(YAKIT_TIPLERI)
        self.inp_sehir  = QComboBox(); self.inp_sehir.addItems(SEHIRLER)
        self.inp_km     = QSpinBox();       self.inp_km.setRange(0, 999999); self.inp_km.setSuffix(" km")
        self.inp_ucret  = QDoubleSpinBox(); self.inp_ucret.setRange(1, 9999); self.inp_ucret.setDecimals(2); self.inp_ucret.setSuffix(" ₺/km"); self.inp_ucret.setValue(3.5)

        for w in [self.inp_id, self.inp_marka, self.inp_model, self.inp_tip, self.inp_yakit, self.inp_sehir, self.inp_km, self.inp_ucret]:
            w.setStyleSheet(input_ss())

        row0 = [("Araç ID", self.inp_id), ("Marka", self.inp_marka), ("Model", self.inp_model), ("Tip", self.inp_tip)]
        row1 = [("Yakıt", self.inp_yakit), ("Şehir", self.inp_sehir), ("Kilometre", self.inp_km), ("KM Ücreti", self.inp_ucret)]
        for col, (lt, wid) in enumerate(row0):
            grid.addWidget(self._lbl(lt), 0, col); grid.addWidget(wid, 1, col)
        for col, (lt, wid) in enumerate(row1):
            grid.addWidget(self._lbl(lt), 2, col); grid.addWidget(wid, 3, col)
        klay.addLayout(grid)

        btn_lay = QHBoxLayout()
        self.btn_ekle = QPushButton("✚  Ekle")
        self.btn_guncelle = QPushButton("✎  Güncelle")
        self.btn_sil = QPushButton("🗑  Sil")
        self.btn_temizle = QPushButton("⟲  Temizle")

        self.btn_ekle.setStyleSheet(btn_primary_ss())
        self.btn_guncelle.setStyleSheet(btn_gold_ss())
        self.btn_sil.setStyleSheet(btn_danger_ss())
        self.btn_temizle.setStyleSheet(btn_outline_ss())

        for b in [self.btn_ekle, self.btn_guncelle, self.btn_sil, self.btn_temizle]:
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedWidth(120)
            btn_lay.addWidget(b)
        btn_lay.addStretch()

        self.btn_ekle.clicked.connect(self._ekle)
        self.btn_guncelle.clicked.connect(self._guncelle)
        self.btn_sil.clicked.connect(self._sil)
        self.btn_temizle.clicked.connect(self._temizle)

        self.btn_guncelle.setEnabled(False)
        self.btn_sil.setEnabled(False)

        klay.addLayout(btn_lay)
        lay.addWidget(kart)

        arama_lay = QHBoxLayout()
        sub = QLabel("Tüm Araçlar")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        arama_lay.addWidget(sub)
        arama_lay.addStretch()

        arama_lbl = QLabel("🔍  Ara:")
        arama_lbl.setStyleSheet(f"color:{C['accent']};font-size:13px;font-weight:700;")
        self.inp_arama = QLineEdit()
        self.inp_arama.setPlaceholderText("Araç ID veya Adı ile ara...")
        self.inp_arama.setStyleSheet(input_ss())
        self.inp_arama.setFixedWidth(250)
        self.inp_arama.textChanged.connect(self._arama_yap)
        arama_lay.addWidget(arama_lbl)
        arama_lay.addWidget(self.inp_arama)

        lay.addLayout(arama_lay)

        self.tablo = QTableWidget()
        self.tablo.itemSelectionChanged.connect(self._secim_degisti)
        self.tablo.setColumnCount(9)
        self.tablo.setHorizontalHeaderLabels(["ID", "Marka", "Model", "Tip", "Yakıt", "Şehir", "Kilometre", "KM Ücreti", "Durum"])
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
        self._temizle()

    def _tablo_yenile(self):
        self.tablo.setRowCount(0)
        for a in self.sistem.get_araclar().values():
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(a.get_arac_id())))
            self.tablo.setItem(r, 1, QTableWidgetItem(a.get_marka()))
            self.tablo.setItem(r, 2, QTableWidgetItem(a.get_model()))
            self.tablo.setItem(r, 3, QTableWidgetItem(a.get_tip()))
            self.tablo.setItem(r, 4, QTableWidgetItem(a.get_yakit_tipi()))
            self.tablo.setItem(r, 5, QTableWidgetItem(a.get_sehir()))
            self.tablo.setItem(r, 6, QTableWidgetItem(f"{a.get_kilometre():,} km"))
            self.tablo.setItem(r, 7, QTableWidgetItem(f"₺{a.get_km_ucreti():.2f}/km"))

            if a.get_musait_mi():
                d = QTableWidgetItem("✓  Müsait"); d.setForeground(QColor(C['success']))
            else:
                d = QTableWidgetItem("✗  Kirada"); d.setForeground(QColor(C['danger']))
            self.tablo.setItem(r, 8, d)
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
            a = Arac(self.inp_id.value(), self.inp_marka.currentText(), model, self.inp_tip.currentText(), self.inp_yakit.currentText(), self.inp_sehir.currentText(), self.inp_km.value(), self.inp_ucret.value())
            ok, msg = self.sistem.arac_ekle(a)
            self._bildirim(msg, ok)
            if ok: 
                self._tablo_yenile()
                self._temizle()
                self.dashboard.refresh()
        except Exception as e:
            self._bildirim(str(e), False)

    def _secim_degisti(self):
        sel = self.tablo.selectedItems()
        if not sel:
            self._temizle()
            return
        r = sel[0].row()
        try:
            aid = int(self.tablo.item(r, 0).text())
            arac = self.sistem.get_araclar().get(aid)
            if arac:
                self.inp_id.setValue(arac.get_arac_id())
                self.inp_id.setEnabled(False)
                self.inp_marka.setCurrentText(arac.get_marka())
                self.inp_model.setText(arac.get_model())
                self.inp_tip.setCurrentText(arac.get_tip())
                self.inp_yakit.setCurrentText(arac.get_yakit_tipi())
                self.inp_sehir.setCurrentText(arac.get_sehir())
                self.inp_km.setValue(arac.get_kilometre())
                self.inp_ucret.setValue(arac.get_km_ucreti())

                self.btn_ekle.setEnabled(False)
                self.btn_guncelle.setEnabled(True)
                self.btn_sil.setEnabled(True)
        except Exception:
            pass

    def _temizle(self):
        araclar = self.sistem.get_araclar()
        next_id = max(araclar.keys()) + 1 if araclar else 1
        self.inp_id.setEnabled(False)
        self.inp_id.setValue(next_id)
        
        self.inp_marka.setCurrentIndex(0)
        self.inp_model.clear()
        self.inp_tip.setCurrentIndex(0)
        self.inp_yakit.setCurrentIndex(0)
        self.inp_sehir.setCurrentIndex(0)
        self.inp_km.setValue(0)
        self.inp_ucret.setValue(3.5)

        self.btn_ekle.setEnabled(True)
        self.btn_guncelle.setEnabled(False)
        self.btn_sil.setEnabled(False)
        self.tablo.clearSelection()

    def _guncelle(self):
        try:
            model = self.inp_model.text().strip()
            if not model: raise ValueError("Model adı boş olamaz.")
            ok, msg = self.sistem.arac_guncelle(
                self.inp_id.value(),
                self.inp_marka.currentText(),
                model,
                self.inp_tip.currentText(),
                self.inp_yakit.currentText(),
                self.inp_sehir.currentText(),
                self.inp_km.value(),
                self.inp_ucret.value()
            )
            self._bildirim(msg, ok)
            if ok:
                self._tablo_yenile()
                self._temizle()
                self.dashboard.refresh()
        except Exception as e:
            self._bildirim(str(e), False)

    def _sil(self):
        aid = self.inp_id.value()
        ok, msg = self.sistem.arac_sil(aid)
        self._bildirim(msg, ok)
        if ok:
            self._tablo_yenile()
            self._temizle()
            self.dashboard.refresh()

    def _arama_yap(self):
        txt = self.inp_arama.text().lower()
        for r in range(self.tablo.rowCount()):
            id_txt = self.tablo.item(r, 0).text().lower()
            marka_txt = self.tablo.item(r, 1).text().lower()
            model_txt = self.tablo.item(r, 2).text().lower()

            if txt in id_txt or txt in marka_txt or txt in model_txt:
                self.tablo.setRowHidden(r, False)
            else:
                self.tablo.setRowHidden(r, True)

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

        kart = QFrame(); kart.setStyleSheet(card_ss(C['gold'] + "66")); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22, 18, 22, 18); klay.setSpacing(12)
        sl = QLabel("➕  Yeni Kullanıcı Kaydı")
        sl.setStyleSheet(f"color:{C['gold']};font-size:13px;font-weight:700;background:transparent;")
        klay.addWidget(sl)

        grid = QGridLayout(); grid.setSpacing(10)
        self.inp_kid    = QSpinBox(); self.inp_kid.setRange(1, 99999); self.inp_kid.setEnabled(False)
        self.inp_ad     = QLineEdit(); self.inp_ad.setPlaceholderText("Ad Soyad")
        self.inp_ad.setValidator(QRegExpValidator(QRegExp(r"^[A-Za-zÇçĞğİıÖöŞşÜü\s]+$"), self))
        self.inp_ehliyet= QLineEdit(); self.inp_ehliyet.setPlaceholderText("Örn: 34ABC123")
        self.inp_ehliyet.setValidator(QRegExpValidator(QRegExp(r"^\d{2}[A-Za-z]{3}\d{3}$"), self))
        self.inp_tel    = QLineEdit(); self.inp_tel.setPlaceholderText("Telefon")
        self.inp_tel.setMaxLength(14)
        self.inp_tel.textChanged.connect(self._format_tel)

        custom_ss = input_ss() + """
            QLineEdit, QSpinBox {
                border: 1.5px solid #D1D5DB;
                background: #FFFFFF;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1.5px solid #9CA3AF;
            }
        """
        for w in [self.inp_kid, self.inp_ad, self.inp_ehliyet, self.inp_tel]:
            w.setStyleSheet(custom_ss)

        cols = [("Kullanıcı ID", self.inp_kid), ("Ad Soyad", self.inp_ad), ("Ehliyet No", self.inp_ehliyet), ("Telefon", self.inp_tel)]
        for col, (lt, wid) in enumerate(cols):
            grid.addWidget(self._lbl(lt), 0, col); grid.addWidget(wid, 1, col)
        klay.addLayout(grid)

        btn_lay = QHBoxLayout()
        btn = QPushButton("✚  Kullanıcı Ekle")
        btn.setStyleSheet(btn_gold_ss()); btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._ekle); btn.setFixedWidth(170)
        btn_temizle = QPushButton("⟲  Temizle")
        btn_temizle.setStyleSheet(btn_outline_ss()); btn_temizle.setCursor(Qt.PointingHandCursor)
        btn_temizle.clicked.connect(self._temizle); btn_temizle.setFixedWidth(120)
        btn_lay.addWidget(btn)
        btn_lay.addWidget(btn_temizle)
        btn_lay.addStretch()
        klay.addLayout(btn_lay)
        lay.addWidget(kart)

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

        arama_lay = QHBoxLayout()
        sub = QLabel("Kayıtlı Kullanıcılar")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        arama_lay.addWidget(sub)
        arama_lay.addStretch()
        
        arama_lbl = QLabel("🔍  Ara:")
        arama_lbl.setStyleSheet(f"color:{C['accent']};font-size:13px;font-weight:700;")
        self.inp_arama = QLineEdit()
        self.inp_arama.setPlaceholderText("Kullanıcı ID veya Adı ile ara...")
        self.inp_arama.setStyleSheet(input_ss())
        self.inp_arama.setFixedWidth(250)
        self.inp_arama.textChanged.connect(self._arama_yap)
        arama_lay.addWidget(arama_lbl)
        arama_lay.addWidget(self.inp_arama)
        
        lay.addLayout(arama_lay)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Ehliyet No", "Telefon", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        lay.addWidget(self.tablo)
        self._tablo_yenile()
        self._temizle()

    def _format_tel(self, text):
        if self.inp_tel.signalsBlocked(): return
        digits = "".join(filter(str.isdigit, text))
        f = ""
        if len(digits) > 0: f += digits[:4]
        if len(digits) > 4: f += " " + digits[4:7]
        if len(digits) > 7: f += " " + digits[7:9]
        if len(digits) > 9: f += " " + digits[9:11]
        
        self.inp_tel.blockSignals(True)
        self.inp_tel.setText(f)
        self.inp_tel.setCursorPosition(len(f))
        self.inp_tel.blockSignals(False)

    def _temizle(self):
        kullanicilar = self.sistem.get_kullanicilar()
        next_id = max(kullanicilar.keys()) + 1 if kullanicilar else 1
        self.inp_kid.setValue(next_id)
        self.inp_ad.clear()
        self.inp_ehliyet.clear()
        self.inp_tel.clear()
        self.tablo.clearSelection()

    def _arama_yap(self):
        txt = self.inp_arama.text().lower()
        for r in range(self.tablo.rowCount()):
            id_txt = self.tablo.item(r, 0).text().lower()
            ad_txt = self.tablo.item(r, 1).text().lower()
            if txt in id_txt or txt in ad_txt:
                self.tablo.setRowHidden(r, False)
            else:
                self.tablo.setRowHidden(r, True)

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
            if ok: 
                self._tablo_yenile()
                self._temizle()
                self.dashboard.refresh()
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
            mesaj_satırlar.append(f"#{b['id']}  {b['arac']}  |  {b['baslangic']} → {b['bitis']}  |  Süre: {b['sure']}  |  Ücret: {b['ucret']}")
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

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        # Başlat Kartı
        kart = QFrame(); kart.setStyleSheet(card_ss(C['success'] + "66")); shadow(kart)
        klay = QVBoxLayout(kart); klay.setContentsMargins(22, 18, 22, 18); klay.setSpacing(12)
        sl = QLabel("▶  Kiralama Başlat")
        sl.setStyleSheet(f"color:{C['success']};font-size:13px;font-weight:700;background:transparent;")
        klay.addWidget(sl)
        grid = QGridLayout(); grid.setSpacing(10)
        self.b_arac_id = QSpinBox(); self.b_arac_id.setRange(1, 99999)
        self.b_user_id = QSpinBox(); self.b_user_id.setRange(1, 99999)
        self.b_alis_sehri = QComboBox(); self.b_alis_sehri.addItems(SEHIRLER)
        self.b_birakis_sehri = QComboBox(); self.b_birakis_sehri.addItems(SEHIRLER)
        self.b_bas_dt  = QDateTimeEdit(); self.b_bas_dt.setCalendarPopup(True)
        self.b_bas_dt.setDateTime(QDateTime.currentDateTime())

        for w in [self.b_arac_id, self.b_user_id, self.b_alis_sehri, self.b_birakis_sehri, self.b_bas_dt]:
            w.setStyleSheet(input_ss())

        cols = [("Araç ID", self.b_arac_id), ("Kullanıcı ID", self.b_user_id), ("Alış Şehri", self.b_alis_sehri)]
        cols_b = [("Bırakış Şehri", self.b_birakis_sehri), ("Başlangıç", self.b_bas_dt)]
        for col, (lt, wid) in enumerate(cols):
            grid.addWidget(self._lbl(lt), 0, col); grid.addWidget(wid, 1, col)
        for col, (lt, wid) in enumerate(cols_b):
            grid.addWidget(self._lbl(lt), 2, col); grid.addWidget(wid, 3, col)
        
        klay.addLayout(grid)
        btn_bas = QPushButton("▶  Kiralama Başlat"); btn_bas.setStyleSheet(btn_success_ss())
        btn_bas.setCursor(Qt.PointingHandCursor); btn_bas.clicked.connect(self._baslat)
        btn_bas.setFixedWidth(170)
        klay.addWidget(btn_bas)
        top_row.addWidget(kart)

        # Bitir Kartı
        kart2 = QFrame(); kart2.setStyleSheet(card_ss(C['danger'] + "55")); shadow(kart2)
        k2lay = QVBoxLayout(kart2); k2lay.setContentsMargins(22, 18, 22, 18); k2lay.setSpacing(12)
        sl2 = QLabel("■  Kiralama Bitir")
        sl2.setStyleSheet(f"color:{C['danger']};font-size:13px;font-weight:700;background:transparent;")
        k2lay.addWidget(sl2)
        grid2 = QGridLayout(); grid2.setSpacing(10)
        self.e_kid  = QSpinBox(); self.e_kid.setRange(1, 99999)
        self.e_bit_dt = QDateTimeEdit(); self.e_bit_dt.setCalendarPopup(True)
        self.e_bit_dt.setDateTime(QDateTime.currentDateTime())
        self.e_ucret = QLineEdit(); self.e_ucret.setReadOnly(True)
        self.e_ucret.setPlaceholderText("Seçim Bekleniyor...")
        for w in [self.e_kid, self.e_bit_dt, self.e_ucret]: w.setStyleSheet(input_ss())
        cols2 = [("Kiralama ID", self.e_kid), ("Bitiş Saati", self.e_bit_dt)]
        for col, (lt, wid) in enumerate(cols2):
            grid2.addWidget(self._lbl(lt), 0, col); grid2.addWidget(wid, 1, col)
        
        grid2.addWidget(self._lbl("Hesaplanan Ücret"), 2, 0)
        grid2.addWidget(self.e_ucret, 3, 0, 1, 3)
        k2lay.addLayout(grid2)
        
        self.e_kid.valueChanged.connect(self._hesapla_bitis_ucret)
        self.e_bit_dt.dateTimeChanged.connect(self._hesapla_bitis_ucret)
        
        k2lay.addStretch()
        btn_bit = QPushButton("■  Kiralama Bitir"); btn_bit.setStyleSheet(btn_danger_ss())
        btn_bit.setCursor(Qt.PointingHandCursor); btn_bit.clicked.connect(self._bitir)
        btn_bit.setFixedWidth(170)
        k2lay.addWidget(btn_bit)
        top_row.addWidget(kart2)

        lay.addLayout(top_row)

        # Selection Tables Area
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)
        
        arac_lay = QVBoxLayout()
        arac_ara_lbl = QLabel("🚗  Araç Seç")
        arac_ara_lbl.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        self.inp_arac_ara = QLineEdit()
        self.inp_arac_ara.setPlaceholderText("Araç ID veya Adı ile ara...")
        self.inp_arac_ara.setStyleSheet(input_ss())
        self.inp_arac_ara.textChanged.connect(self._arac_ara_yap)
        
        self.arac_tablo = QTableWidget()
        self.arac_tablo.setColumnCount(2)
        self.arac_tablo.setHorizontalHeaderLabels(["ID", "Araç"])
        self.arac_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.arac_tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.arac_tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.arac_tablo.verticalHeader().setVisible(False)
        self.arac_tablo.setAlternatingRowColors(True)
        self.arac_tablo.setStyleSheet(TABLE_SS)
        self.arac_tablo.setFixedHeight(150)
        self.arac_tablo.itemSelectionChanged.connect(self._arac_secildi)
        
        arac_lay.addWidget(arac_ara_lbl)
        arac_lay.addWidget(self.inp_arac_ara)
        arac_lay.addWidget(self.arac_tablo)
        
        kul_lay = QVBoxLayout()
        kul_ara_lbl = QLabel("👤  Kullanıcı Seç")
        kul_ara_lbl.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        self.inp_kul_ara = QLineEdit()
        self.inp_kul_ara.setPlaceholderText("Kullanıcı ID veya Adı ile ara...")
        self.inp_kul_ara.setStyleSheet(input_ss())
        self.inp_kul_ara.textChanged.connect(self._kul_ara_yap)
        
        self.kul_tablo = QTableWidget()
        self.kul_tablo.setColumnCount(2)
        self.kul_tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad"])
        self.kul_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.kul_tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.kul_tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.kul_tablo.verticalHeader().setVisible(False)
        self.kul_tablo.setAlternatingRowColors(True)
        self.kul_tablo.setStyleSheet(TABLE_SS)
        self.kul_tablo.setFixedHeight(150)
        self.kul_tablo.itemSelectionChanged.connect(self._kul_secildi)
        
        kul_lay.addWidget(kul_ara_lbl)
        kul_lay.addWidget(self.inp_kul_ara)
        kul_lay.addWidget(self.kul_tablo)

        mid_row.addLayout(arac_lay)
        mid_row.addLayout(kul_lay)
        lay.addLayout(mid_row)

        bot_lay = QVBoxLayout()
        bot_header = QHBoxLayout()
        sub = QLabel("Tüm Kiralamalar")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        
        genel_ara_lbl = QLabel("🔍  Genel Sorgulama:")
        genel_ara_lbl.setStyleSheet(f"color:{C['accent']};font-size:12px;font-weight:700;")
        self.inp_genel_ara = QLineEdit()
        self.inp_genel_ara.setPlaceholderText("ID, Araç veya Kullanıcı Ara...")
        self.inp_genel_ara.setStyleSheet(input_ss())
        self.inp_genel_ara.setFixedWidth(250)
        self.inp_genel_ara.textChanged.connect(self._genel_ara_yap)
        
        bot_header.addWidget(sub)
        bot_header.addStretch()
        bot_header.addWidget(genel_ara_lbl)
        bot_header.addWidget(self.inp_genel_ara)
        bot_lay.addLayout(bot_header)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(8)
        self.tablo.setHorizontalHeaderLabels(["ID", "Araç", "Kullanıcı", "Alış Şehri", "Bırakış Şehri", "Başlangıç", "Bitiş", "Ücret"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet(TABLE_SS)
        self.tablo.itemSelectionChanged.connect(self._kiralama_secildi)
        bot_lay.addWidget(self.tablo)
        lay.addLayout(bot_lay)

        scroll.setWidget(container)
        main = QVBoxLayout(self); main.setContentsMargins(0, 0, 0, 0); main.addWidget(scroll)
        self._tablo_yenile()

    def _hesapla_bitis_ucret(self):
        kid = self.e_kid.value()
        kiralama = next((k for k in self.sistem.get_aktif_kiralamalar() if k.get_kiralama_id() == kid), None)
        if not kiralama:
            self.e_ucret.setText("Kiralama Bulunamadı")
            return
        
        mesafe = get_mesafe(kiralama.get_alis_sehri(), kiralama.get_birakis_sehri())
        toplam = mesafe * kiralama.get_arac().get_km_ucreti()
        
        self.e_ucret.setText(f"₺{toplam:,.2f} ({mesafe} km)")

    def _arac_secildi(self):
        sel = self.arac_tablo.selectedItems()
        if sel:
            self.b_arac_id.setValue(int(sel[0].text()))

    def _kul_secildi(self):
        sel = self.kul_tablo.selectedItems()
        if sel:
            self.b_user_id.setValue(int(sel[0].text()))

    def _kiralama_secildi(self):
        sel = self.tablo.selectedItems()
        if sel:
            self.e_kid.setValue(int(sel[0].text()))
            self.e_bit_dt.setDateTime(QDateTime.currentDateTime())

    def _arac_ara_yap(self):
        txt = self.inp_arac_ara.text().lower()
        for r in range(self.arac_tablo.rowCount()):
            id_txt = self.arac_tablo.item(r, 0).text().lower()
            ad_txt = self.arac_tablo.item(r, 1).text().lower()
            if txt in id_txt or txt in ad_txt:
                self.arac_tablo.setRowHidden(r, False)
            else:
                self.arac_tablo.setRowHidden(r, True)

    def _kul_ara_yap(self):
        txt = self.inp_kul_ara.text().lower()
        for r in range(self.kul_tablo.rowCount()):
            id_txt = self.kul_tablo.item(r, 0).text().lower()
            ad_txt = self.kul_tablo.item(r, 1).text().lower()
            if txt in id_txt or txt in ad_txt:
                self.kul_tablo.setRowHidden(r, False)
            else:
                self.kul_tablo.setRowHidden(r, True)

    def _genel_ara_yap(self):
        txt = self.inp_genel_ara.text().lower()
        for r in range(self.tablo.rowCount()):
            id_txt = self.tablo.item(r, 0).text().lower()
            arac_txt = self.tablo.item(r, 1).text().lower()
            kul_txt = self.tablo.item(r, 2).text().lower()
            if txt in id_txt or txt in arac_txt or txt in kul_txt:
                self.tablo.setRowHidden(r, False)
            else:
                self.tablo.setRowHidden(r, True)

    def _tablo_yenile(self):
        self.tablo.setRowCount(0)
        for k in reversed(self.sistem.get_aktif_kiralamalar()):
            b = k.kiralama_bilgisi()
            r = self.tablo.rowCount(); self.tablo.insertRow(r)
            self.tablo.setItem(r, 0, QTableWidgetItem(str(b["id"])))
            self.tablo.setItem(r, 1, QTableWidgetItem(b["arac"]))
            self.tablo.setItem(r, 2, QTableWidgetItem(b["kullanici"]))
            self.tablo.setItem(r, 3, QTableWidgetItem(b["alis"]))
            self.tablo.setItem(r, 4, QTableWidgetItem(b["birakis"]))
            self.tablo.setItem(r, 5, QTableWidgetItem(b["baslangic"]))
            self.tablo.setItem(r, 6, QTableWidgetItem(b["bitis"]))
            ucret_item = QTableWidgetItem(b["ucret"])
            if b["aktif"]:
                ucret_item.setForeground(QColor(C['warning']))
            else:
                ucret_item.setForeground(QColor(C['success']))
            self.tablo.setItem(r, 7, ucret_item)
            self.tablo.setRowHeight(r, 44)

        self.arac_tablo.setRowCount(0)
        for a in self.sistem.get_araclar().values():
            if not a.get_musait_mi(): continue
            r = self.arac_tablo.rowCount(); self.arac_tablo.insertRow(r)
            self.arac_tablo.setItem(r, 0, QTableWidgetItem(str(a.get_arac_id())))
            self.arac_tablo.setItem(r, 1, QTableWidgetItem(a.get_tam_ad()))
            self.arac_tablo.setRowHeight(r, 30)

        self.kul_tablo.setRowCount(0)
        for u in self.sistem.get_kullanicilar().values():
            if u.aktif_kiralama(): continue
            r = self.kul_tablo.rowCount(); self.kul_tablo.insertRow(r)
            self.kul_tablo.setItem(r, 0, QTableWidgetItem(str(u.get_kullanici_id())))
            self.kul_tablo.setItem(r, 1, QTableWidgetItem(u.get_ad()))
            self.kul_tablo.setRowHeight(r, 30)

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
            self.b_arac_id.value(), self.b_user_id.value(), self.b_alis_sehri.currentText(), self.b_birakis_sehri.currentText(), baslangic)
        self._bildirim(msg, ok)
        if ok: self._tablo_yenile(); self.dashboard.refresh()

    def _bitir(self):
        bitis  = self._qdt_to_dt(self.e_bit_dt.dateTime())
        ok, msg = self.sistem.kiralama_bitir(
            self.e_kid.value(), bitis)
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

        bot_header = QHBoxLayout()
        sub = QLabel("Tamamlanan Kiralamalar — Detay")
        sub.setStyleSheet(f"color:{C['text_sub']};font-size:12px;font-weight:700;")
        bot_header.addWidget(sub)
        bot_header.addStretch()

        genel_ara_lbl = QLabel("🔍  Ara:")
        genel_ara_lbl.setStyleSheet(f"color:{C['accent']};font-size:12px;font-weight:700;")
        self.inp_rapor_ara = QLineEdit()
        self.inp_rapor_ara.setPlaceholderText("Araç veya Kullanıcı Ara...")
        self.inp_rapor_ara.setStyleSheet(input_ss())
        self.inp_rapor_ara.setFixedWidth(250)
        self.inp_rapor_ara.textChanged.connect(self._arama_yap)
        bot_header.addWidget(genel_ara_lbl)
        bot_header.addWidget(self.inp_rapor_ara)

        lay.addLayout(bot_header)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(["Araç", "Kullanıcı", "Başlangıç", "Bitiş", "Süre", "Ücret"])
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

        self.lbl_toplam.setText(f"Toplam Gelir:  ₺{toplam_gelir:,.2f}  |  İşlem Sayısı: {len(gecmis)}")

    def _arama_yap(self):
        txt = self.inp_rapor_ara.text().lower()
        for r in range(self.tablo.rowCount()):
            arac_txt = self.tablo.item(r, 0).text().lower()
            kul_txt = self.tablo.item(r, 1).text().lower()
            if txt in arac_txt or txt in kul_txt:
                self.tablo.setRowHidden(r, False)
            else:
                self.tablo.setRowHidden(r, True)

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
        self.sistem = PaylasimSistemi()
        self._build_ui()
        self._saat_timer()

    def _demo_veri(self):
        return PaylasimSistemi()

    def _build_ui(self):
        merkez = QWidget(); merkez.setStyleSheet(f"background:{C['bg']};")
        self.setCentralWidget(merkez)
        ana = QHBoxLayout(merkez); ana.setContentsMargins(0, 0, 0, 0); ana.setSpacing(0)

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
        pages = [("📊", "Dashboard"), ("🚗", "Araç Yönetimi"), ("👤", "Kullanıcılar"), ("🔑", "Kiralamalar"), ("📊", "Raporlar")]
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
        idx = {"Dashboard": 0, "Araç Yönetimi": 1, "Kullanıcılar": 2, "Kiralamalar": 3, "Raporlar": 4}[sayfa]
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