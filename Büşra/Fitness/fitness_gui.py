import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import re
from datetime import datetime, timedelta
from fitness_sistemleri import FitnessSistemi

# --- 1. STİL VE YARDIMCI FONKSİYONLAR ---
STIL = {
    'arka': '#141824',           
    'kart': '#1C2237',           
    'vurgu_mavi': '#38BDF8',     
    'kenar': '#2D3548',          
    'yazi': '#E2E8F0',           
    'yazi_ikincil': '#94A3B8',   
    'p_toplam': '#60A5FA',       
    'p_hedef': '#A855F7',        
    'p_aktif': '#4ADE80',       
    'p_biten': '#F87171',
    'p_uyari': '#FBBF24',
}

def etiket_olustur(metin):
    lbl = QLabel(metin)
    lbl.setStyleSheet(f"color: {STIL['yazi_ikincil']}; font-size: 13px; font-weight: bold; border: none; background: transparent;")
    lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return lbl

class MenuButonu(QPushButton):
    def __init__(self, metin):
        super().__init__(metin)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style(False)

    def update_style(self, aktif):
        if aktif:
            self.setStyleSheet(f"background-color: rgba(56, 189, 248, 0.1); color: {STIL['vurgu_mavi']}; border: none; border-left: 4px solid {STIL['vurgu_mavi']}; text-align: left; padding-left: 20px; font-weight: bold;")
        else:
            self.setStyleSheet(f"background-color: transparent; color: {STIL['yazi_ikincil']}; border: none; text-align: left; padding-left: 20px;")

class AnalizKarti(QFrame):
    def __init__(self, ikon, baslik, deger, renk):
        super().__init__()
        self.setFixedHeight(115)
        self.setStyleSheet(f"QFrame {{ background:{STIL['kart']}; border-radius:12px; border: 1px solid {STIL['kenar']}; border-top: 5px solid {renk}; }}")
        layout = QVBoxLayout(self)
        ust = QHBoxLayout()
        lbl_ikon = QLabel(ikon); lbl_ikon.setStyleSheet(f"font-size: 18px; color: {renk}; border:none; background:transparent;")
        lbl_baslik = QLabel(baslik.upper()); lbl_baslik.setStyleSheet(f"color: {STIL['yazi_ikincil']}; font-size: 9px; font-weight: bold; border:none; background:transparent;")
        ust.addWidget(lbl_ikon); ust.addWidget(lbl_baslik); ust.addStretch()
        self.lbl_deger = QLabel(str(deger))
        self.lbl_deger.setStyleSheet(f"color: {STIL['yazi']}; font-size: 28px; font-weight: 800; border:none; background:transparent;")
        layout.addLayout(ust); layout.addWidget(self.lbl_deger)

# --- 2. SAYFALAR ---

class AntrenmanSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.secili_sporcu_id = None
        
        # MERKEZİ STİL SÖZLÜĞÜ
        self.STIL = {
            'arka': '#0F111A',
            'kart': '#161B2E',
            'kenar': '#242C45',
            'vurgu_mavi': '#00D1FF',
            'vurgu_yesil': '#34D399',
            'yazi_ana': '#FFFFFF',
            'yazi_ikincil': '#94A3B8'
        }
        
        self.initUI()
        

    def initUI(self):
        # Ana Dikey Yerleşim
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(15)
        self.setStyleSheet(f"background-color: {self.STIL['arka']};")

        # 1. BÖLÜM: ÜYE ARA
        self.ara_input = QLineEdit()
        self.ara_input.setPlaceholderText("ID VEYA AD SOYAD İLE ÜYE ARA...")
        self.ara_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.STIL['kart']}; color: {self.STIL['vurgu_mavi']}; 
                border: 1px solid {self.STIL['kenar']}; border-radius: 12px; padding: 15px;
            }}
        """)
        self.ara_input.textChanged.connect(self.filtrele)
        layout.addWidget(self.ara_input)

        # 2. BÖLÜM: ÜYE LİSTESİ
        self.tablo_liste = QTableWidget(0, 2)
        self.tablo_liste.setHorizontalHeaderLabels(["ID", "AD SOYAD"])
        self.tablo_liste.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_liste.setFixedHeight(120)
        self.tablo_liste.setShowGrid(False)
        self.tablo_liste.verticalHeader().setVisible(False)
        self.tablo_liste.setSelectionMode(QAbstractItemView.NoSelection) # Beyaz seçimi engeller
        self.tablo_liste.setFocusPolicy(Qt.NoFocus)
        self.tablo_liste.setStyleSheet(f"""
            QTableWidget {{ background: {self.STIL['kart']}; color: {self.STIL['yazi_ikincil']}; border-radius: 12px; border: none; }}
            QHeaderView::section {{ background: {self.STIL['kenar']}; color: {self.STIL['vurgu_mavi']}; padding: 8px; font-weight: bold; border: none; }}
            QTableWidget::item:hover {{ background-color: {self.STIL['kenar']}; }}
        """)
        self.tablo_liste.cellClicked.connect(self.sporcu_sec)
        layout.addWidget(self.tablo_liste)

        # 3. BÖLÜM: YAN YANA TABLOLAR (Ağırlık & Kardiyo)
        orta_layout = QHBoxLayout()
        orta_layout.setSpacing(20)

        # Ağırlık Paneli
        vbox_agirlik = QVBoxLayout()
        self.lbl_agirlik_baslik = QLabel("🏋️ AĞIRLIK PROGRAMI")
        self.lbl_agirlik_baslik.setStyleSheet(f"color: {self.STIL['vurgu_mavi']}; font-weight: 900; font-size: 13px; background-color: #141824;")
        vbox_agirlik.addWidget(self.lbl_agirlik_baslik)
        
        self.tablo_agirlik = self.tablo_taslaği_olustur(["HAREKET", "SET", "TEK.", "KG"])
        self.tablo_doldur(self.tablo_agirlik, ["Bench Press", "Squat", "Deadlift", "Shoulder Press", "Lat Pulldown", "Leg Press", "Bicep Curl", "Tricep Pushdown"])
        vbox_agirlik.addWidget(self.tablo_agirlik)
        orta_layout.addLayout(vbox_agirlik)

        # Kardiyo Paneli
        vbox_kardiyo = QVBoxLayout()
        self.lbl_kardiyo_baslik = QLabel("🏃 KARDİYO PROGRAMI")
        self.lbl_kardiyo_baslik.setStyleSheet(f"color: {self.STIL['vurgu_mavi']}; font-weight: 900; font-size: 13px; background-color: #141824;")
        vbox_kardiyo.addWidget(self.lbl_kardiyo_baslik)
        
        self.tablo_kardiyo = self.tablo_taslaği_olustur(["KARDİYO", "DK", "HIZ", "EĞİM"])
        self.tablo_doldur(self.tablo_kardiyo, ["Koşu Bandı", "Bisiklet", "Eliptik", "Kürek", "Merdiven", "Yürüyüş", "İp Atlama", "Yüzme"])
        vbox_kardiyo.addWidget(self.tablo_kardiyo)
        orta_layout.addLayout(vbox_kardiyo)

        layout.addLayout(orta_layout)

        # 4. BÖLÜM: TOPLAM HARCANAN KALORİ
        self.lbl_toplam_kalori = QLabel("TOPLAM HARCANAN: 0 KCAL")
        self.lbl_toplam_kalori.setAlignment(Qt.AlignCenter)
        self.lbl_toplam_kalori.setStyleSheet(f"""
            QLabel {{
                background: {self.STIL['kart']}; color: {self.STIL['vurgu_mavi']}; 
                border: 1px solid {self.STIL['vurgu_mavi']}; border-radius: 10px; 
                padding: 15px; font-weight: 900; font-size: 15px;
            }}
        """)
        layout.addWidget(self.lbl_toplam_kalori)

        # 5. BÖLÜM: ÜYEYE ÖZEL NOTLAR
        self.txt_not = QTextEdit()
        self.txt_not.setPlaceholderText("ÜYEYE ÖZEL PROGRAM NOTLARI...")
        self.txt_not.setMaximumHeight(80)
        self.txt_not.setStyleSheet(f"""
            QTextEdit {{
                background: {self.STIL['kart']}; color: {self.STIL['yazi_ana']}; 
                border: 1px solid {self.STIL['kenar']}; border-radius: 12px; padding: 10px;
            }}
        """)
        layout.addWidget(self.txt_not)

        # 6. BÖLÜM: KAYDET BUTONU
        self.btn_kaydet = QPushButton("ANTRENMANI SİSTEME KAYDET")
        self.btn_kaydet.setCursor(Qt.PointingHandCursor)
        self.btn_kaydet.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.STIL['vurgu_mavi']}; color: #000; 
                font-weight: 900; height: 50px; border-radius: 15px;
            }}
            QPushButton:hover {{ background-color: #00B8E6; }}
        """)
        self.btn_kaydet.clicked.connect(self.kaydet)
        layout.addWidget(self.btn_kaydet)

    

    def tablo_taslaği_olustur(self, basliklar):
        tablo = QTableWidget(8, 4)
        tablo.setHorizontalHeaderLabels(basliklar)
        tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tablo.verticalHeader().setVisible(False)
        tablo.setShowGrid(False)
        tablo.setSelectionMode(QAbstractItemView.NoSelection) # Beyaz kutuyu engeller
        tablo.setFocusPolicy(Qt.NoFocus)
        tablo.setStyleSheet(f"""
            QTableWidget {{ 
                background: {self.STIL['kart']}; color: {self.STIL['yazi_ana']}; 
                border-radius: 15px; border: 1px solid {self.STIL['kenar']}; 
                outline: none; selection-background-color: transparent;
            }}
            QHeaderView::section {{ 
                background: {self.STIL['kenar']}; color: {self.STIL['yazi_ikincil']}; 
                padding: 10px; font-weight: bold; border: none; 
            }}
        """)
        return tablo

    def tablo_doldur(self, tablo, liste):
        for i, isim in enumerate(liste):
            it = QTableWidgetItem(isim)
            it.setFlags(Qt.ItemIsEnabled)
            it.setForeground(QColor(self.STIL['yazi_ikincil']))
            tablo.setItem(i, 0, it)
            for j in range(1, 4):
                sp = QSpinBox()
                sp.setRange(0, 999)
                sp.setAlignment(Qt.AlignCenter)
                sp.setButtonSymbols(2)
                # BEYAZLIK SORUNU İÇİN KESİN ÇÖZÜM (QLineEdit hedef alındı)
                sp.setStyleSheet(f"""
                    QSpinBox {{ 
                        background: transparent; color: {self.STIL['yazi_ana']}; 
                        border: none; font-weight: bold; 
                    }}
                    QSpinBox QLineEdit {{ 
                        background: transparent; 
                        selection-background-color: transparent; 
                        selection-color: {self.STIL['yazi_ana']};
                        border: none;
                    }}
                """)
                sp.valueChanged.connect(self.analiz_hesapla)
                tablo.setCellWidget(i, j, sp)

    def sporcu_sec(self, row, column):
        try:
            # 1. Hücrelerden veriyi güvenli bir şekilde çek
            item_id = self.tablo_liste.item(row, 0)
            item_ad = self.tablo_liste.item(row, 1)
            
            # 2. Eğer hücreler boş değilse (veri varsa) işleme başla
            if item_id and item_ad:
                self.secili_sporcu_id = item_id.text()
                ad_soyad = item_ad.text()
                
                # 3. Başlıkları görsel olarak güncelle
                self.lbl_agirlik_baslik.setText(f"🏋️ {ad_soyad.upper()} - AĞIRLIK PROGRAMI")
                self.lbl_kardiyo_baslik.setText(f"🏃 {ad_soyad.upper()} - KARDİYO PROGRAMI")
                
                # Seçilen satırı mavi yaparak belli et
                self.tablo_liste.selectRow(row)
                
                print(f"Başarıyla seçildi: {ad_soyad} (ID: {self.secili_sporcu_id})")
            else:
                print("Tıklanan hücrede veri bulunamadı.")

        except Exception as e:
            # Herhangi bir hata durumunda programın kapanmasını engeller
            print(f"HATA: Sporcu seçilirken bir sorun oluştu -> {e}")

    def analiz_hesapla(self):
        ag_kcal = 0

        for i in range(8):
            try:
                s_widget = self.tablo_agirlik.cellWidget(i, 1)
                t_widget = self.tablo_agirlik.cellWidget(i, 2)
                k_widget = self.tablo_agirlik.cellWidget(i, 3)

                s = s_widget.value() if s_widget else 0
                t = t_widget.value() if t_widget else 0
                k = k_widget.value() if k_widget else 0

                ag_kcal += (s * t * k) * 0.07

            except:
                continue

        kr_kcal = 0

        for i in range(8):
            try:
                dk_widget = self.tablo_kardiyo.cellWidget(i, 1)
                hiz_widget = self.tablo_kardiyo.cellWidget(i, 2)
                eg_widget = self.tablo_kardiyo.cellWidget(i, 3)

                dk = dk_widget.value() if dk_widget else 0
                hiz = hiz_widget.value() if hiz_widget else 0
                eg = eg_widget.value() if eg_widget else 0

                if dk > 0 and hiz > 0:
                    hiz_m_dk = (hiz * 1000) / 60
                    vo2 = (0.2 * hiz_m_dk) + (0.9 * hiz_m_dk * (eg / 100)) + 3.5
                    kr_kcal += ((vo2 * 75) / 200) * dk

            except:
                continue

        toplam = int(ag_kcal + kr_kcal)
        self.lbl_toplam_kalori.setText(f"TOPLAM HARCANAN: {toplam} KCAL")

    def filtrele(self):
        txt = self.ara_input.text().lower()
        for i in range(self.tablo_liste.rowCount()):
            ad = self.tablo_liste.item(i, 1).text().lower() if self.tablo_liste.item(i, 1) else ""
            self.tablo_liste.setRowHidden(i, txt not in ad)

    def ekrani_sifirla(self):
        self.secili_sporcu_id = None

        # NOT ALANI
        self.txt_not.clear()

        # KALORİ
        self.lbl_toplam_kalori.setText("TOPLAM HARCANAN: 0 KCAL")

        # BAŞLIKLAR
        self.lbl_agirlik_baslik.setText("🏋️ AĞIRLIK PROGRAMI")
        self.lbl_kardiyo_baslik.setText("🏃 KARDİYO PROGRAMI")

        # TABLOLAR (SPINBOX RESET)
        for tablo in [self.tablo_agirlik, self.tablo_kardiyo]:
            for r in range(tablo.rowCount()):
                for c in range(1, 4):
                    w = tablo.cellWidget(r, c)
                    if w:
                        w.setValue(0)

    def kaydet(self):
        
        try:
            if not self.secili_sporcu_id:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Hata")
                msg.setText("Lütfen önce listeden bir sporcu seçin!")

                msg.setStyleSheet("""
                QMessageBox {
                    background-color: #141824;
                }

                QLabel {
                    color: white;
                    background-color: #141824;
                }

                QPushButton {
                background-color: #38BDF8;
                color: #0F172A;
                padding: 6px 10px;
                border-radius: 6px;
                min-width: 15px;
            }
                """)

                msg.exec_()
                return

            bugun = datetime.now().strftime("%d.%m.%Y")
            
            # --- VERİLERİ TOPLA ---
            agirlik_verisi = ""
            for i in range(8):
                item = self.tablo_agirlik.item(i, 0)
                hareket = item.text() if item else ""
                s = self.tablo_agirlik.cellWidget(i, 1).value()
                t = self.tablo_agirlik.cellWidget(i, 2).value()
                k = self.tablo_agirlik.cellWidget(i, 3).value()
                if s > 0: # Sadece set girilenleri al
                    agirlik_verisi += f"• {hareket}: {s}x{t} {k}kg\n"

            kardiyo_verisi = ""
            kardiyo_verisi = ""
            for i in range(8):
                item = self.tablo_kardiyo.item(i, 0)
                isim = item.text() if item else ""
                dk = self.tablo_kardiyo.cellWidget(i, 1).value()
                hiz = self.tablo_kardiyo.cellWidget(i, 2).value()
                eg = self.tablo_kardiyo.cellWidget(i, 3).value()

                if dk > 0:
                    kardiyo_verisi += f"• {isim}: {dk} dk | {hiz} km/h | %{eg} eğim\n"

                
            text = self.lbl_toplam_kalori.text()
            kalori = text.split(": ")[1] if ": " in text else "0"
            notlar = self.txt_not.toPlainText()

            # --- VERİ PAKETİ ---
            antrenman_ozeti = {
                "tarih": bugun,
                "hareketler": f"AĞIRLIK:\n{agirlik_verisi}\nKARDİYO:\n{kardiyo_verisi}".strip(),
                "kalori": kalori,
                "notlar": notlar
            }

            # --- ANA LİSTEYE YAZ ---
            bulundu = self.ana_pencere.sistem.antrenman_ekle(self.secili_sporcu_id, antrenman_ozeti)

            if bulundu:
                try:
                    # 1. Başarılı Mesajını Oluştur
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Başarılı")
                    msg.setText(f"{bugun} tarihli antrenman kaydedildi!")

                    msg.setStyleSheet("""
                        QMessageBox { background-color: #141824; }
                        QLabel { color: white; background-color: #141824; }
                        QPushButton { 
                            background-color: #38BDF8; 
                            color: #0F172A; 
                            padding: 6px 10px; 
                            border-radius: 6px; 
                            min-width: 15px; 
                        }
                    """)
                    msg.exec_()
                    self.ekrani_sifirla()

                    # 2. Önce Verileri Yenile (Ekranda görünmesi için)
                    if hasattr(self.ana_pencere, 'sayfa_takip'):
                        self.ana_pencere.sayfa_takip.verileri_yukle()
                        return
                    # 3. Sonra Ekranı Sıfırla (Burası hassas noktadır)

                except Exception as ic_hata:
                    # Başarılı mesajından sonra bir şey patlarsa sadece konsola yaz, ekrana hata basma
                    print(f"Kayıt sonrası işlemler hatası: {ic_hata}")

            else:
                # Sporcu ID bulunamadıysa burası çalışır
                QMessageBox.warning(self, "Hata", "Lütfen geçerli bir Sporcu ID seçin!")
                
        except Exception as e:
            # Bu kısım sadece gerçek bir KAYIT hatası (dosya yazma, veri bulma vb.) olursa çalışır
            print(f"Kritik Kaydetme hatası: {e}")
            # Eğer sporcu bulunmuşsa ama başka bir sorun varsa mesaj çıkar
            if 'bugun' in locals():
                QMessageBox.critical(self, "Sistem Hatası", f"Veri işlenemedi: {str(e)}")

class SporcuYonetimSayfasi(QWidget):
    # ... (Stil ve yardımcı fonksiyonlar aynı kalıyor) ...class SporcuYonetimSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(25)

        baslik = QLabel("⚙️ Sporcu ve Üyelik Yönetimi")
        baslik.setStyleSheet(f"color: {STIL['yazi']}; font-size: 24px; font-weight: 700; border:none; background:transparent;")
        layout.addWidget(baslik)

        ust_f = QHBoxLayout(); ust_f.setSpacing(20)

        # --- 1. YENİ ÜYE KAYDI ---
        self.g_ekle = QGroupBox("✨ Yeni Üye Kaydı")
        self.g_ekle.setStyleSheet(self.group_stili(STIL['p_toplam']))
        fe = QFormLayout(self.g_ekle); fe.setSpacing(12); fe.setContentsMargins(25, 35, 25, 25)

        self.in_ad = QLineEdit()
        self.in_cin = QComboBox()
        self.in_yas = QSpinBox() # YAŞ AYRI KUTU
        self.in_paket = QComboBox()
        self.in_boy = QSpinBox()
        self.in_boy.setRange(120, 230)
        self.in_kilo = QDoubleSpinBox()
        self.in_hedef = QDoubleSpinBox()

        self.in_cin.addItems(["Kadın", "Erkek"])
        self.in_paket.addItems(["7 Günlük (Haftalık)", "1 Aylık", "3 Aylık", "6 Aylık", "1 Yıllık"])
        
        # Stil ve Ayarlar
        for s in [self.in_ad, self.in_cin, self.in_yas, self.in_paket, self.in_boy, self.in_kilo, self.in_hedef]: 
            s.setFixedHeight(32); s.setStyleSheet(self.input_stili())
        self.in_boy.setRange(120, 230)
        self.in_kilo.setRange(30, 200)
        self.in_hedef.setRange(30, 200)
        self.in_yas.setRange(18, 100);
         
        self.in_yas.setValue(20)
        self.in_boy.setValue(175); 
        self.in_kilo.setValue(75); 
        self.in_hedef.setValue(70)

        be = QPushButton("KAYDI TAMAMLA"); be.setStyleSheet(self.btn_stili(STIL['p_toplam'])); be.setFixedHeight(40); be.clicked.connect(self.is_ekle)
        
        # FORM DİZİLİMİ
        fe.addRow(etiket_olustur("Ad Soyad:"), self.in_ad)
        fe.addRow(etiket_olustur("Cinsiyet:"), self.in_cin)
        fe.addRow(etiket_olustur("Yaş:"), self.in_yas) # AYRI SATIR
        fe.addRow(etiket_olustur("Paket Seçimi:"), self.in_paket)
        fe.addRow(etiket_olustur("Boy / Kilo:"), self.yatay_layout(self.in_boy, self.in_kilo))
        fe.addRow(etiket_olustur("Hedef Kilo:"), self.in_hedef)
        fe.addRow("", be)

        # --- 2. ÜYELİK GÜNCELLE / SİL ---
        self.g_islem = QGroupBox("🛠️ Üyelik Güncelle / Sil")
        self.g_islem.setStyleSheet(self.group_stili(STIL['p_toplam']))
        self.g_islem.setFixedWidth(450)
        fi = QFormLayout(self.g_islem); 
        fi.setSpacing(12); 
        fi.setContentsMargins(25, 35, 25, 25)

        self.in_id = QSpinBox(); self.in_nad = QLineEdit(); self.in_ncin = QComboBox()
        self.in_nyas = QSpinBox() # GÜNCELLEME İÇİN AYRI YAŞ
        self.in_npaket = QComboBox()
        self.in_nb = QDoubleSpinBox(); self.in_nk = QDoubleSpinBox(); self.in_nh = QDoubleSpinBox()
        
        self.in_id.setRange(0, 999); 
        self.in_ncin.addItems(["Kadın", "Erkek"]); 
        self.in_npaket.addItems(["7 Günlük (Haftalık)", "1 Aylık", "3 Aylık", "6 Aylık", "1 Yıllık"])
        self.in_id.valueChanged.connect(self.bilgileri_otomatik_getir)

        for s in [self.in_id, self.in_nad, self.in_ncin, self.in_nyas, self.in_npaket, self.in_nb, self.in_nk, self.in_nh]:
            s.setFixedHeight(32)
            s.setStyleSheet(self.input_stili())

        # Sadece harf ve boşluk izni (Türkçe karakterler dahil)
        isim_regex = QRegExp("^[a-zA-ZğüşıöçĞÜŞİÖÇ\\s]*$")
        self.in_ad.setValidator(QRegExpValidator(isim_regex))
        self.in_nad.setValidator(QRegExpValidator(isim_regex))

        self.in_boy.setRange(120, 230)
        self.in_kilo.setRange(30, 200)
        self.in_hedef.setRange(30, 200)
        
        self.in_nyas.setRange(18, 100); 
       

        self.in_boy.setValue(175); 
        self.in_kilo.setValue(75); 
        self.in_hedef.setValue(70)
        self.in_nyas.setValue(20)
        

        bg = QPushButton("GÜNCELLE"); bg.setStyleSheet(self.btn_stili(STIL['p_toplam']))
        bs = QPushButton("SİL"); bs.setStyleSheet(self.btn_stili(STIL['p_biten']))
        for b in [bg, bs]: b.setFixedHeight(35); b.clicked.connect(self.is_guncelle if b==bg else self.is_sil)

        # GÜNCELLEME FORM DİZİLİMİ
        fi.addRow(etiket_olustur("Üye ID:"), self.in_id)
        fi.addRow(etiket_olustur("Ad Soyad:"), self.in_nad)
        fi.addRow(etiket_olustur("Cinsiyet:"), self.in_ncin)
        fi.addRow(etiket_olustur("Yaş:"), self.in_nyas) # AYRI SATIR
        fi.addRow(etiket_olustur("Yeni Paket:"), self.in_npaket)
        fi.addRow(etiket_olustur("Boy / Kilo:"), self.yatay_layout(self.in_nb, self.in_nk))
        fi.addRow(etiket_olustur("Hedef Kilo:"), self.in_nh)
        fi.addRow("", bg); fi.addRow("", bs)

        ust_f.addWidget(self.g_ekle, 3); ust_f.addWidget(self.g_islem, 2); layout.addLayout(ust_f)

        # --- 3. TABLO ---
        self.tablo_y = QTableWidget(); self.tablo_y.setColumnCount(11)
        self.tablo_y.setHorizontalHeaderLabels(["ID", "AD SOYAD", "YAŞ", "CİNSİYET", "PAKET", "BOY", "KİLO", "HEDEF KİLO", "ÜYELİK KAYIT", "ÜYELİK BİTİŞ", "ÜYELİK DURUM"])
        
        self.tablo_y.setColumnWidth(0, 40); self.tablo_y.setColumnWidth(2, 40)
        self.tablo_y.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tablo_y.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for i in range(2, 11): self.tablo_y.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.tablo_y.verticalHeader().setVisible(False)
        self.tablo_y.setStyleSheet(f"QTableWidget {{ background: {STIL['kart']}; color: {STIL['yazi']}; border: 1px solid {STIL['kenar']}; }} QHeaderView::section {{ background: #252D42; color: {STIL['vurgu_mavi']}; padding: 10px; font-weight: bold; border: none; }}")
        layout.addWidget(self.tablo_y, 1)

    def group_stili(self, renk): return f"QGroupBox {{ color: {renk}; font-weight: bold; border: 1px solid {STIL['kenar']}; border-radius: 12px; border-top: 3px solid {renk}; margin-top: 20px; background: {STIL['kart']}; }}"
    def input_stili(self): return f"background: {STIL['arka']}; color: white; border: 1px solid {STIL['kenar']}; border-radius: 8px; padding-left: 10px;"
    def btn_stili(self, r): return f"background: {r}; color: {STIL['arka']}; font-weight: bold; border-radius: 8px; border: none;"
    def yatay_layout(self, w1, w2):
        h = QHBoxLayout(); h.addWidget(w1); h.addWidget(w2); h.setContentsMargins(0,0,0,0)
        c = QWidget(); c.setLayout(h); return c
    
    def is_ekle(self): 
        # Formdan verileri alıyoruz
        ad = self.in_ad.text().strip()
        
        # Basit bir boş kontrolü (Uygulamanın çökmesini önler)
        if not ad:
            print("Hata: Ad soyad boş bırakılamaz!")
            return

        # Ana penceredeki global fonksiyonu çağırıyoruz
        # SIRA: ad, cin, yas, paket, boy, kilo, hedef
        self.ana_pencere.global_sporcu_ekle(
            ad, 
            self.in_cin.currentText(), 
            self.in_yas.value(), 
            self.in_paket.currentText(), 
            self.in_boy.value(), 
            self.in_kilo.value(), 
            self.in_hedef.value()
        )

        # Kayıttan sonra formu temizleyelim
        self.in_ad.clear()
        self.in_yas.setValue(20)
        self.in_boy.setValue(175)
        self.in_kilo.setValue(75)
    
    def is_sil(self):
        uye_id = self.in_id.value()
        
        # ID 0 ise işlem yapma (Genelde boş ID 0 olur)
        if uye_id == 0:
            print("Silinecek geçerli bir Üye ID bulunamadı.")
            return
            
        # Ana penceredeki silme fonksiyonunu çağırıyoruz
        # Not: Genelde güvenlik için burada bir onay kutusu (QMessageBox) iyi olur 
        # ama en temel hali şöyledir:
        self.ana_pencere.global_sporcu_sil(uye_id)
        
        # Silme işleminden sonra ID kutusunu ve diğer alanları sıfırlayalım
        self.in_id.setValue(0)
        self.in_nad.clear()
        print(f"ID {uye_id} silindi.")

    def is_guncelle(self):
        # Seçili ID'yi al
        uye_id = self.in_id.value()
        
        # Eğer ID 0 ise veya tabloda yoksa işlemi durdurabilirsiniz
        if uye_id == 0:
            print("Lütfen geçerli bir Üye ID seçin.")
            return

        # Ana penceredeki güncelleme fonksiyonuna verileri gönderiyoruz
        # SIRA ÖNEMLİ: id, ad, yas, cinsiyet, paket, boy, kilo, hedef
        self.ana_pencere.global_sporcu_guncelle(
            uye_id,
            self.in_nad.text(),
            self.in_nyas.value(),
            self.in_ncin.currentText(),
            self.in_npaket.currentText(),
            self.in_nb.value(),
            self.in_nk.value(),
            self.in_nh.value()
        )
        
        print(f"ID {uye_id} başarıyla güncellendi.")

    def bilgileri_otomatik_getir(self, id_no):
       
        bulundu = False
        
        # --- ÖNEMLİ: Limitleri önce genişletiyoruz ki veriyi kabul etsin ---
        self.in_nyas.setRange(0, 120)
        self.in_nb.setRange(0, 250)  # Boy 99'da takılmasın diye 250 yaptık
        self.in_nk.setRange(0, 300)
        self.in_nh.setRange(0, 300)

        for r in range(self.tablo_y.rowCount()):
            item_id = self.tablo_y.item(r, 0)
            
            # Tablodaki ID ile kutudaki ID eşleşirse
            if item_id and item_id.text() == str(id_no):
                bulundu = True
                try:
                    # 1. İsim
                    self.in_nad.setText(self.tablo_y.item(r, 1).text())

                    # 2. Yaş (Sayıyı ayıkla)
                    yas_metni = self.tablo_y.item(r, 2).text()
                    yas_match = re.search(r"\d+", yas_metni)
                    if yas_match:
                        self.in_nyas.setValue(int(yas_match.group()))

                    # 3. Cinsiyet (Tam eşleşme ve temizleme)
                    cin_metni = self.tablo_y.item(r, 3).text().strip()
                    idx = self.in_ncin.findText(cin_metni)
                    if idx >= 0:
                        self.in_ncin.setCurrentIndex(idx)
                    else:
                        self.in_ncin.setCurrentText(cin_metni)

                    # 4. Paket
                    self.in_npaket.setCurrentText(self.tablo_y.item(r, 4).text().strip())

                    # 5. BOY (Burada 99.99 hatası çözülüyor)
                    boy_metni = self.tablo_y.item(r, 5).text()
                    boy_match = re.search(r"[\d.,]+", boy_metni)
                    if boy_match:
                        # Float çevirip kutuya basıyoruz
                        boy_deger = float(boy_match.group().replace(",", "."))
                        self.in_nb.setValue(boy_deger)

                    # 6. Kilo
                    kilo_metni = self.tablo_y.item(r, 6).text()
                    k_match = re.search(r"[\d.,]+", kilo_metni)
                    if k_match:
                        self.in_nk.setValue(float(k_match.group().replace(",", ".")))

                    # 7. Hedef Kilo
                    hedef_metni = self.tablo_y.item(r, 7).text()
                    h_match = re.search(r"[\d.,]+", hedef_metni)
                    if h_match:
                        self.in_nh.setValue(float(h_match.group().replace(",", ".")))

                except Exception as e:
                    print(f"Hata: Veri çekilirken bir problem oluştu: {e}")
                break

        if not bulundu:
            # ID yoksa alanları boşalt (opsiyonel)
            self.in_nad.clear()

class SporcuAnalizSayfasi(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(25)
        baslik = QLabel("📊 Genel Durum Dashboard")
        baslik.setStyleSheet(f"color: {STIL['yazi']}; font-size: 24px; font-weight: 700; border:none; background:transparent;")
        layout.addWidget(baslik)
        self.kart_layout = QHBoxLayout()
        self.k_toplam = AnalizKarti("👥", "Toplam Üye", "0", STIL['p_toplam'])
        self.k_aktif = AnalizKarti("⚡", "Aktif Üye", "0", STIL['p_aktif'])
        self.k_uyari = AnalizKarti("⚠️", "Az Kaldı", "0", STIL['p_uyari'])
        self.k_biten = AnalizKarti("⌛", "Süresi Biten", "0", STIL['p_biten'])
        self.k_hedef_tamam = AnalizKarti("🎯", "Hedefe Ulaşan", "0", STIL['p_hedef'])
        for k in [self.k_toplam, self.k_aktif, self.k_uyari, self.k_biten, self.k_hedef_tamam]: self.kart_layout.addWidget(k)
        layout.addLayout(self.kart_layout)
        self.tablo = QTableWidget(0, 11) 
        self.tablo.setHorizontalHeaderLabels([
            "AD SOYAD", "CİNSİYET", "YAŞ", "BOY", "KİLO", 
            "BMI", "HEDEF KİLO", "KAYIT", "BİTİŞ", "ÜYELİK DURUM", "HEDEF DURUM"
        ])
        self.tablo.setColumnHidden(0, False); self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.tablo.verticalHeader().setVisible(False)
        self.tablo.setStyleSheet(f"QTableWidget {{ background: {STIL['kart']}; color: {STIL['yazi']}; border: 1px solid {STIL['kenar']}; }} QHeaderView::section {{ background: #252D42; color: {STIL['vurgu_mavi']}; padding: 10px; font-weight: bold; border: none; }}")
        layout.addWidget(self.tablo)

class BeslenmeSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        # Stil sözlüğünü ana pencereden güvenli bir şekilde alıyoruz
        self.S = getattr(ana_pencere, 'STIL', {
            'arka': '#0F172A', 'kart': '#1E293B', 'yazi': '#F8FAFC', 
            'vurgu_mavi': '#38BDF8', 'kenar': '#334155', 'p_uyari': '#F59E0B'
        })
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {self.S['arka']}; border: none;")
        self.initUI()
        self.init_veri()
        self.tablo_liste.cellClicked.connect(self.sporcu_sec)

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        S = self.S 

        # ================= SOL PANEL (ÜYE LİSTESİ) =================
        sol_panel = QVBoxLayout()
        self.ara_input = QLineEdit()
        self.ara_input.setPlaceholderText("🔍 Üye ara...")
        self.ara_input.setAlignment(Qt.AlignCenter)
        self.ara_input.setStyleSheet(f"background-color: {S['kart']}; color: {S['vurgu_mavi']}; border: 1px solid {S['kenar']}; padding: 10px; border-radius: 10px;")
        self.ara_input.textChanged.connect(self.filtrele)
        
        self.tablo_liste = QTableWidget(0, 2)
        self.tablo_liste.setHorizontalHeaderLabels(["ID", "AD SOYAD"])
        self.tablo_liste.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_liste.verticalHeader().setVisible(False)
        self.tablo_liste.setFixedWidth(280)
        self.tablo_liste.setStyleSheet(f"""
        QTableWidget {{ background-color: {S['kart']}; color: white; border: 1px solid {S['kenar']}; gridline-color: {S['kenar']}; outline: none; }}

        QHeaderView::section {{ background-color: #1C2237; color: {S['vurgu_mavi']}; padding: 10px; border: 1px solid {S['kenar']}; font-weight: bold; }}

        QTableCornerButton::section {{ background-color: #1C2237; border: none; }}

        QTableWidget::item:selected {{
            background-color: transparent;
            color: white;
        }}

        QTableWidget::item:hover {{
            background-color: #334155;
        }}
    """)
        self.tablo_liste.cellClicked.connect(self.sporcu_yukle)
        
        self.lbl_not_baslik = QLabel("📝 SPORCU ÖZEL NOTLARI")
        self.lbl_not_baslik.setStyleSheet(f"color: {S['vurgu_mavi']}; font-weight: bold; margin-top: 15px;")
        self.txt_notlar = QTextEdit()
        self.txt_notlar.setStyleSheet(f"background-color: {S['kart']}; color: white; border: 1px solid {S['kenar']}; border-radius: 20px; padding: 10px;")
        
        sol_panel.addWidget(self.ara_input)
        sol_panel.addWidget(self.tablo_liste)
        sol_panel.addWidget(self.lbl_not_baslik)
        sol_panel.addWidget(self.txt_notlar)
        layout.addLayout(sol_panel, 1)

        # ================= SAĞ PANEL (GÖSTERGELER VE TABLO) =================
        sag_panel = QVBoxLayout()
        
        # ÜST BİLGİ KARTI
        self.ust_kart = QFrame()
        self.ust_kart.setStyleSheet(f"background-color: {S['kart']}; border: 1px solid {S['kenar']}; border-radius: 15px;")
        self.ust_kart.setFixedHeight(80)
        u_lay = QHBoxLayout(self.ust_kart)
        u_lay.setContentsMargins(25, 0, 25, 0)

        # SOLDAKİ İSİM
        self.lbl_ad = QLabel("LÜTFEN BİR SPORCU SEÇİN")
        self.lbl_ad.setStyleSheet(f"color: {S['vurgu_mavi']}; font-size: 18px; font-weight: 900; border:none;")
        u_lay.addWidget(self.lbl_ad)

        # ORTAYA ESNEK BOŞLUK (Bu isimle kilo bilgisini birbirinden ayırır)
        u_lay.addStretch()

        # SAĞDAKİ KİLO DETAYI
        self.lbl_kilo_detay = QLabel("") 
        self.lbl_kilo_detay.setAlignment(Qt.AlignRight | Qt.AlignVCenter) # Metni sağa yaslar
        self.lbl_kilo_detay.setStyleSheet(f"color: {S['yazi']}; font-size: 14px; font-weight: bold; border:none;")
        self.lbl_kilo_detay.setTextFormat(Qt.RichText) 
        u_lay.addWidget(self.lbl_kilo_detay)

        sag_panel.addWidget(self.ust_kart)

        # GÖSTERGELER
        gosterge_lay = QHBoxLayout()
        self.kart_alinan = QFrame()
        self.kart_alinan.setStyleSheet(f"background-color: {S['kart']}; border: 1px solid {S['kenar']}; border-top: 4px solid {S['p_uyari']}; border-radius: 20px;")
        ka_lay = QVBoxLayout(self.kart_alinan)
        self.lbl_alinan = QLabel("Alınan: 0 kcal"); self.lbl_alinan.setStyleSheet("color: white; font-size: 16px; font-weight: bold; border:none;"); self.lbl_alinan.setAlignment(Qt.AlignCenter)
        ka_lay.addWidget(self.lbl_alinan)
        
        self.kart_makro = QFrame()
        self.kart_makro.setStyleSheet(f"background-color: {S['kart']}; border: 1px solid {S['kenar']}; border-top: 4px solid {S['vurgu_mavi']}; border-radius: 20px;")
        km_lay = QGridLayout(self.kart_makro)
        self.lbl_pro = QLabel("Protein: 0g"); self.lbl_karb = QLabel("Karb: 0g"); self.lbl_yag = QLabel("Yağ: 0g"); self.lbl_hedef = QLabel("Hedef: -")
        for i, lbl in enumerate([self.lbl_pro, self.lbl_karb, self.lbl_yag, self.lbl_hedef]):
            lbl.setStyleSheet("color: white; border:none; font-size: 13px;"); lbl.setAlignment(Qt.AlignCenter)
            km_lay.addWidget(lbl, i // 2, i % 2)
        gosterge_lay.addWidget(self.kart_alinan, 2); gosterge_lay.addWidget(self.kart_makro, 3)
        sag_panel.addLayout(gosterge_lay)

        # ÖĞÜN TABLOSU
        self.ogun_tablo = QTableWidget(4, 3)
        self.ogun_tablo.setVerticalHeaderLabels(["KAHVALTI", "ATIŞTIRMALIK", "ÖĞLE YEMEĞİ", "AKŞAM YEMEĞİ"])
        self.ogun_tablo.setHorizontalHeaderLabels(["ÖĞÜN SEVİYESİ", "KALORİ", "P / K / Y"])
        self.ogun_tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ogun_tablo.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ogun_tablo.setStyleSheet(f"""
            QTableWidget {{ background-color: #1C2237; color: white; border: 1px solid {S['kenar']}; gridline-color: {S['kenar']}; }}
            QHeaderView::section {{ background-color: #1C2237; color: {S['vurgu_mavi']}; padding: 10px; font-weight: bold; }}
            QTableCornerButton::section {{ background-color: #1C2237; border: none; }}
        """)
        
        for r in range(4):
            c_widget = QWidget(); 
            c_lay = QHBoxLayout(c_widget); 
            c_lay.setContentsMargins(15, 2, 15, 2); 
            c_widget.setStyleSheet("background: #1C2237;")
            cmb = QComboBox(); 
            cmb.addItems(["Seçiniz", "Hafif", "Orta", "Ağır"])
            cmb.setStyleSheet(f"""
            QComboBox {{
                background-color: #1C2237;
                color: white;
                border: 1px solid {S['kenar']};
                padding: 5px;
            }}

            QComboBox QAbstractItemView {{
                background-color: #1C2237;
                color: white;
                selection-background-color: {S['vurgu_mavi']};
            }}
            """)
            cmb.currentTextChanged.connect(self.hesapla)
            c_lay.addWidget(cmb); self.ogun_tablo.setCellWidget(r, 0, c_widget)
            for c in range(1, 3):
                it = QTableWidgetItem("0"); it.setTextAlignment(Qt.AlignCenter); self.ogun_tablo.setItem(r, c, it)

        sag_panel.addWidget(self.ogun_tablo)
        self.btn_kaydet = QPushButton("📊 GÜNLÜK VERİLERİ SİSTEME KAYDET")
        self.btn_kaydet.setStyleSheet(f"background-color: {S['vurgu_mavi']}; color: #0F172A; font-weight: 900; height: 50px; border-radius: 20px;")
        self.btn_kaydet.clicked.connect(self.kaydet)
        sag_panel.addWidget(self.btn_kaydet)
        layout.addLayout(sag_panel, 3)

    def init_veri(self):
        self.tablo_liste.setRowCount(0)

        for sp in self.ana_pencere.sistem.sporcular:
            row = self.tablo_liste.rowCount()
            self.tablo_liste.insertRow(row)

            self.tablo_liste.setItem(row, 0, QTableWidgetItem(str(sp["id"])))
            self.tablo_liste.setItem(row, 1, QTableWidgetItem(sp["ad"]))
                
    def sporcu_yukle(self, r, c):
        try:
            # Seçilen sporcu ID'sini al
            sid = int(self.tablo_liste.item(r, 0).text())
            # Listeden sporcuyu bul
            sp = next((x for x in self.ana_pencere.sistem.sporcular if x["id"] == sid), None)
            
            if not sp:
                return

            # Üst paneldeki ismi güncelle
            self.lbl_ad.setText(f"👤 {sp['ad'].upper()}")
            
            # Verileri çek
            kilo = float(sp.get("kilo", 0))
            hedef_kilo = float(sp.get("hedef", 0))
            boy = float(sp.get("boy", 0))
            yas = float(sp.get("yas", 0))
            cinsiyet = str(sp.get("cinsiyet", "Erkek")).capitalize()
            aktivite = str(sp.get("aktivite", "Hareketsiz"))

            # --- BMR VE TDEE HESAPLA ---
            if cinsiyet == "Kadın":
                bmr = 655 + (9.6 * kilo) + (1.8 * boy) - (4.7 * yas)
            else:
                bmr = 66 + (13.7 * kilo) + (5 * boy) - (6.8 * yas)
            
            faktörler = {"Hareketsiz": 1.2, "Hafif Aktif": 1.375, "Orta Aktif": 1.55, "Çok Aktif": 1.725}
            carpan = faktörler.get(aktivite, 1.2)
            self.gunluk_hedef_kalori = int(bmr * carpan)

            # --- 1. ÜST PANEL GÜNCELLEME (Kilo Durumu) ---
            fark = kilo - hedef_kilo
            if fark > 0:
                durum = f"<span style='color:#ff4d4d;'>{fark:.1f} kg vermeli</span>"
            elif fark < 0:
                durum = f"<span style='color:#4cd137;'>{abs(fark):.1f} kg almalı</span>"
            else:
                durum = "<span style='color:#fbc531;'>Hedefte</span>"

            self.lbl_kilo_detay.setText(f"Mevcut: {kilo}kg  |  Hedef: {hedef_kilo}kg  |  {durum}")

            # --- 2. HEDEF KALORİ YAZISINI GÜNCELLEME ---
            # Eğer self.lbl_hedef_kalori isminde bir etiketin yoksa hata almamak için kontrol ekliyoruz
            if hasattr(self, 'lbl_hedef_kalori'):
                self.lbl_hedef_kalori.setText(f"Hedef: {self.gunluk_hedef_kalori} kcal")
            elif hasattr(self, 'lbl_hedef'): # Alternatif isim kontrolü
                self.lbl_hedef.setText(f"Günlük Kalori: {self.gunluk_hedef_kalori} kcal")

            # --- 3. VERİTABANI VE HESAPLAMA TETİKLEME ---
            self.ana_pencere.db_cursor.execute("SELECT ogun_seviyeleri, notlar FROM beslenme_programi WHERE uye_id=?", (sid,))
            b_res = self.ana_pencere.db_cursor.fetchone()
            
            if b_res:
                sev_list = eval(b_res[0])
                self.txt_notlar.setPlainText(b_res[1])
                for i, s in enumerate(sev_list):
                    # ComboBox'ı bul ve seçili seviyeyi ayarla
                    self.ogun_tablo.cellWidget(i, 0).findChild(QComboBox).setCurrentText(s)
            else:
                self.txt_notlar.clear()
                for i in range(4):
                    self.ogun_tablo.cellWidget(i, 0).findChild(QComboBox).setCurrentIndex(0)
            
            self.hesapla() # Alınan kaloriyi ve renkleri güncelle

        except Exception as e:
            print(f"Hata: {e}")
                
    def sporcu_sec(self, row, col):
        """Tablodan sporcu seçildiğinde çalışır"""
        try:
            # 0. sütunda ID olduğunu varsayıyoruz
            item = self.tablo_liste.item(row, 0)
            if item:
                self.secili_sporcu_id = item.text().strip()
                print(f"DEBUG: Sporcu Seçildi! ID: {self.secili_sporcu_id}") # Terminalde bunu görüyorsan çalışıyor demektir
            else:
                print("DEBUG: Tıklanan hücre boş!")
        except Exception as e:
            print(f"Hata: Sporcu seçilemedi -> {e}")
    
    def ekrani_sifirla(self):
        self.secili_sporcu_id = None

        self.lbl_ad.setText("LÜTFEN BİR SPORCU SEÇİN")
        self.lbl_kilo_detay.setText("")

        # ÖĞÜN TABLOSU RESET
        for r in range(self.ogun_tablo.rowCount()):

            # 1. ComboBox reset (öğün seviyesi)
            widget = self.ogun_tablo.cellWidget(r, 0)
            if widget:
                combo = widget.findChild(QComboBox)
                if combo:
                    combo.setCurrentIndex(0)

            # 2. Kalori ve makro hücreleri reset
            for c in range(1, self.ogun_tablo.columnCount()):
                item = self.ogun_tablo.item(r, c)
                if item:
                    item.setText("0")

        # NOTLAR
        self.txt_notlar.clear()

        # GÖSTERGELER
        self.lbl_alinan.setText("Alınan: 0 kcal")
        self.lbl_pro.setText("Protein: 0g")
        self.lbl_karb.setText("Karb: 0g")
        self.lbl_yag.setText("Yağ: 0g")
        self.lbl_hedef.setText("Hedef: -")
        
    

    def kaydet(self):
       
        try:
            if not hasattr(self, 'secili_sporcu_id') or self.secili_sporcu_id is None:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Uyarı")
                msg.setText("Lütfen önce listeden bir üye seçin!")

                msg.setStyleSheet("""
                QMessageBox {
                    background-color: #141824;
                }

                QLabel {
                    color: white;
                    background-color: #141824;
                }

                QPushButton {
                background-color: #38BDF8;
                color: #0F172A;
                padding: 6px 10px;
                border-radius: 6px;
                min-width: 15px;
            }
                """)

                msg.exec_()
                return

            bugun = datetime.now().strftime("%d.%m.%Y")

            beslenme_notu = self.txt_notlar.toPlainText() if hasattr(self, 'txt_notlar') else ""

            rapor = []
            
            # --- AKILLI VERİ TOPLAMA (İsimden Bağımsız) ---
            # Sayfadaki tüm ComboBox'ları ve yanlarındaki kalori yazılarını bulur
            combos = self.findChildren(QComboBox)
            labels = self.findChildren(QLabel)
            
            # Öğünleri sırasıyla eşleştir (Tasarımındaki sıraya göre gelir)
            ogun_isimleri = ["🍳 KAHVALTI", "🍎 ATIŞTIRMALIK", "🍗 ÖĞLE YEMEĞİ", "🥗 AKŞAM YEMEĞİ"]
            
            # Sadece öğün seviyesi seçilen ComboBox'ları filtrele (Üye seçimi vb. hariç)
            ogun_combos = [c for c in combos if c.count() > 0 and "Ağır" in [c.itemText(i) for i in range(c.count())]]
            
            for i, ad in enumerate(ogun_isimleri):
                try:
                    secim = ogun_combos[i].currentText() if i < len(ogun_combos) else "Seçilmedi"
                    rapor.append(f"🔹 {ad}: {secim} ")
                except:
                    rapor.append(f"🔹 {ad}: Seçilmedi ")

            
            
            # Toplam Kalori (Üstteki büyük kırmızı/turuncu kutu)
            toplam_kalori = "0"
            for l in labels:
                if "Alınan:" in l.text():
                    toplam_kalori = "".join(filter(str.isdigit, l.text()))
                    break

            yeni_beslenme = {
                "tarih": bugun,
                "liste": "\n".join(rapor),
                "toplam_kalori": toplam_kalori,
                "notlar": beslenme_notu  # Veri buraya bağlandı
            }

            # Sporcu listesine kaydet
            self.ana_pencere.sistem.beslenme_ekle(self.secili_sporcu_id, yeni_beslenme)
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Başarılı")
            msg.setText("Beslenme verileri kaydedildi!")

            msg.setStyleSheet("""
            QMessageBox {
                background-color: #141824;
            }

            QLabel {
                color: white;
                background-color: #141824;
            }

            QPushButton {
        background-color: #38BDF8;
        color: #0F172A;
        padding: 6px 10px;
        border-radius: 6px;
        min-width: 15px;
        }
            """)

            msg.exec_()
            
            # Takip sayfasını yenile
            if hasattr(self.ana_pencere, 'sayfa_takip'):
                self.ana_pencere.sayfa_takip.verileri_yukle()
                self.ekrani_sifirla() 
            return

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme Hatası: {str(e)}")

    def hesapla(self):
        try:
            # Bilimsel sporcu beslenmesi oranlarına göre güncellenmiş değerler
            # [Kalori, Protein, Karbonhidrat, Yağ]
            besin_ayarlari = {
            "KAHVALTI": {
                "Hafif": [450, 25, 60, 12],
                    "Orta":  [650, 35, 85, 18],
                    "Ağır":  [850, 45, 110, 25]
                },
                "ATIŞTIRMALIK": {
                    "Hafif": [150, 5, 20, 5],
                    "Orta":  [250, 10, 35, 8],
                    "Ağır":  [400, 15, 50, 12]
                },
                "ÖĞLE YEMEĞİ": {
                    "Hafif": [500, 35, 60, 15],
                    "Orta":  [800, 50, 95, 22],
                    "Ağır":  [1100, 65, 130, 32]
                },
                "AKŞAM YEMEĞİ": {
                    "Hafif": [400, 30, 40, 10],
                    "Orta":  [600, 45, 65, 15],
                    "Ağır":  [900, 60, 90, 24]
                }
            }

            toplam = [0, 0, 0, 0] # Kalori, P, K, Y
            ogun_isimleri = ["KAHVALTI", "ATIŞTIRMALIK", "ÖĞLE YEMEĞİ", "AKŞAM YEMEĞİ"]

            for r in range(4):
                # Widget ve ComboBox kontrolü (Çökme koruması)
                widget = self.ogun_tablo.cellWidget(r, 0)
                if not widget: continue
                
                cmb = widget if isinstance(widget, QComboBox) else widget.findChild(QComboBox)
                if not cmb: continue
                
                sev = cmb.currentText()
                ogun_adi = ogun_isimleri[r]
                
                if sev != "Seçiniz":
                    v = besin_ayarlari[ogun_adi][sev]
                    toplam = [toplam[i] + v[i] for i in range(4)]
                    
                    # Tabloyu güncelle
                    if self.ogun_tablo.item(r, 1):
                        self.ogun_tablo.item(r, 1).setText(f"{v[0]} kcal")
                    if self.ogun_tablo.item(r, 2):
                        self.ogun_tablo.item(r, 2).setText(f"{v[1]}P / {v[2]}K / {v[3]}Y")
                else:
                    if self.ogun_tablo.item(r, 1): self.ogun_tablo.item(r, 1).setText("0 kcal")
                    if self.ogun_tablo.item(r, 2): self.ogun_tablo.item(r, 2).setText("0P / 0K / 0Y")

            # Alt Gösterge Kartlarını Güncelle
            alinan_kalori = toplam[0]
            self.lbl_alinan.setText(f"Alınan: {alinan_kalori} kcal")
            self.lbl_pro.setText(f"Protein: {toplam[1]}g")
            self.lbl_karb.setText(f"Karb: {toplam[2]}g")
            self.lbl_yag.setText(f"Yağ: {toplam[3]}g")

            # --- RENK VE HEDEF KONTROLÜ ---
            if hasattr(self, 'gunluk_hedef_kalori') and self.gunluk_hedef_kalori > 0:
                S = self.S
                # Eğer alınan kalori, sporcunun TDEE (günlük ihtiyacını) aşarsa kırmızı olur
                if alinan_kalori > self.gunluk_hedef_kalori:
                    renk = "#ff4d4d" # Kırmızı
                    yazi_rengi = "#ff4d4d"
                else:
                    renk = S['p_uyari'] # Normal (Turuncu/Mavi)
                    yazi_rengi = "white"

                self.kart_alinan.setStyleSheet(f"background-color: {S['kart']}; border: 1px solid {S['kenar']}; border-top: 4px solid {renk}; border-radius: 20px;")
                self.lbl_alinan.setStyleSheet(f"color: {yazi_rengi}; font-size: 16px; font-weight: bold; border:none;")

        except Exception as e:
            print(f"Hesaplama hatası: {e}")

    def filtrele(self):
        kelime = self.ara_input.text().lower()
        for i in range(self.tablo_liste.rowCount()):
            item = self.tablo_liste.item(i, 1)
            self.tablo_liste.setRowHidden(i, kelime not in item.text().lower())
    
    def refresh_beslenme(self):
        self.tablo_liste.setRowCount(0)

        for sp in self.ana_pencere.sistem.sporcular:
            row = self.tablo_liste.rowCount()
            self.tablo_liste.insertRow(row)

            self.tablo_liste.setItem(row, 0, QTableWidgetItem(str(sp.get("id", ""))))
            self.tablo_liste.setItem(row, 1, QTableWidgetItem(sp.get("ad", "")))

            # KRİTİK: veri kaybı yok
            if "beslenme_gecmisi" not in sp:
                sp["beslenme_gecmisi"] = []

class TakipSayfasi(QWidget):
    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.secili_sporcu_id = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. ÜST KISIM: ARAMA MOTORU
        self.ara_input = QLineEdit()
        self.ara_input.setPlaceholderText("🔍 Üye Ara (ID veya İsim)... ")
        self.ara_input.setStyleSheet("background: #161B2E; color: white; border: 1px solid #242C45; border-radius: 10px; padding: 12px;")
        self.ara_input.textChanged.connect(self.verileri_yukle)
        layout.addWidget(self.ara_input)

        # 2. ÜYE LİSTESİ
        self.tablo_sporcular = QTableWidget(0, 4)
        self.tablo_sporcular.setHorizontalHeaderLabels(["ID", "AD SOYAD", "GÜNCEL KİLO", "HEDEF KİLO"])
        self.tablo_sporcular.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_sporcular.setFixedHeight(180)
        
        # --- İSTEDİĞİN DÜZELTMELER BURADA ---
        # En soldaki sayı sütununu (1, 2, 3...) gizler
        self.tablo_sporcular.verticalHeader().setVisible(False) 
        
        # Tablo ve Başlık Stili (Beyazlığı giderir, temaya uydurur)
        self.tablo_sporcular.setStyleSheet("""
            QTableWidget { 
                background: #161B2E; 
                color: white; 
                gridline-color: #242C45;
                border: 1px solid #242C45;
            }
        """)
        self.tablo_sporcular.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #252D42;
                color: #00D1FF;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #242C45;
            }
        """)
        # -----------------------------------

        self.tablo_sporcular.cellClicked.connect(self.sporcu_detay_getir)
        layout.addWidget(self.tablo_sporcular)

        # 3. ANA TAKİP KUTUSU
        self.detay_paneli = QFrame()
        self.detay_paneli.setStyleSheet("background: #1A2035; border-radius: 15px; border: 1px solid #242C45;")
        detay_layout = QVBoxLayout(self.detay_paneli)
        
        self.lbl_baslik_bilgi = QLabel("Lütfen bir sporcu seçin...")
        self.lbl_baslik_bilgi.setStyleSheet("color: #00D1FF; font-weight: bold; font-size: 15px;")
        self.lbl_baslik_bilgi.setAlignment(Qt.AlignCenter)
        detay_layout.addWidget(self.lbl_baslik_bilgi)

        yan_yana = QHBoxLayout()
        self.txt_antrenman_detay = QTextEdit()
        self.txt_antrenman_detay.setReadOnly(True)
        self.txt_antrenman_detay.setStyleSheet("background: #0F111A; color: white; border-radius: 10px;")
        
        self.txt_beslenme_detay = QTextEdit()
        self.txt_beslenme_detay.setReadOnly(True)
        self.txt_beslenme_detay.setStyleSheet("background: #0F111A; color: white; border-radius: 10px;")
        
        yan_yana.addWidget(self.txt_antrenman_detay)
        yan_yana.addWidget(self.txt_beslenme_detay)
        detay_layout.addLayout(yan_yana)

        # 4. KALORİ ANALİZİ
        self.lbl_kalori_analiz = QLabel("Yakılan: 0 kcal | Alınan: 0 kcal | Durum: 0 kcal")
        self.lbl_kalori_analiz.setAlignment(Qt.AlignCenter)
        self.lbl_kalori_analiz.setStyleSheet("color: #34D399; font-weight: bold; font-size: 14px;")
        detay_layout.addWidget(self.lbl_kalori_analiz)
        
        layout.addWidget(self.detay_paneli)

        # 5. GEÇMİŞ
        gecmis_layout = QHBoxLayout()
        self.list_gecmis_ant = QListWidget()
        self.list_gecmis_ant.setStyleSheet("background: #161B2E; color: #94A3B8; border-radius: 10px;")
        
        self.list_gecmis_bes = QListWidget()
        self.list_gecmis_bes.setStyleSheet("background: #161B2E; color: #94A3B8; border-radius: 10px;")

        gecmis_layout.addWidget(self.list_gecmis_ant)
        gecmis_layout.addWidget(self.list_gecmis_bes)
        layout.addLayout(gecmis_layout)
        self.list_gecmis_ant.itemClicked.connect(self.gecmis_veriyi_yukle)
        self.list_gecmis_bes.itemClicked.connect(self.gecmis_veriyi_yukle)

        # 6. BUTON
        self.btn_kilo_guncelle = QPushButton("✅ VERİLERİ İŞLE VE KİLOYU GÜNCELLE")
        self.btn_kilo_guncelle.setStyleSheet("background: #00D1FF; color: black; font-weight: bold; height: 45px; border-radius: 10px;")
        self.btn_kilo_guncelle.clicked.connect(self.kilo_guncelle_mekanizmasi)
        layout.addWidget(self.btn_kilo_guncelle)

    def verileri_yukle(self):
        # HATA VEREN db_cursor SATIRLARI SİLİNDİ, LİSTE KULLANILIYOR
        self.tablo_sporcular.setRowCount(0)
        filtre = self.ara_input.text().lower()
        
        for s in self.ana_pencere.sistem.sporcular:
            if filtre in str(s.get('id')) or filtre in s.get('ad').lower():
                row = self.tablo_sporcular.rowCount()
                self.tablo_sporcular.insertRow(row)
                self.tablo_sporcular.setItem(row, 0, QTableWidgetItem(str(s.get('id'))))
                self.tablo_sporcular.setItem(row, 1, QTableWidgetItem(s.get('ad')))
                self.tablo_sporcular.setItem(row, 2, QTableWidgetItem(f"{s.get('kilo')} kg"))
                self.tablo_sporcular.setItem(row, 3, QTableWidgetItem(f"{s.get('hedef')} kg"))

    def sporcu_detay_getir(self, row, col):
        from datetime import datetime
        try:
            # 1. Seçilen satırdaki ID'yi al (0. sütun ID)
            item_id = self.tablo_sporcular.item(row, 0)
            if item_id is None or not item_id.text():
                return

            self.secili_sporcu_id = item_id.text()

            # 2. Ana listeden sporcuyu bul
            sporcu = next(
                (s for s in self.ana_pencere.sistem.sporcular if str(s.get('id')) == self.secili_sporcu_id),
                None
            )

            if sporcu is None:
                print(f"HATA: ID'si {self.secili_sporcu_id} olan sporcu bulunamadı!")
                return

            # 3. Hazırlık ve Temizlik
            bugun = datetime.now().strftime("%d.%m.%Y")
            self.lbl_baslik_bilgi.setText(f"👤 {sporcu.get('ad')} - {bugun} Programı")

            self.txt_antrenman_detay.clear()
            self.txt_beslenme_detay.clear()
            self.list_gecmis_ant.clear()
            self.list_gecmis_bes.clear()

            yakilan_toplam = 0
            alinan_toplam = 0

            # --- ANTRENMAN VERİLERİNİ ÇEK ---
            for ant in sporcu.get('antrenman_gecmisi', []):
                tarih = ant.get('tarih', '')
                item = QListWidgetItem(f"🏋️ {tarih}")
                item.setData(Qt.UserRole, ant)
                self.list_gecmis_ant.addItem(item)

                if tarih == bugun:
                    detay = ant.get('hareketler') or ant.get('program') or ant.get('detay') or ""
                    ant_notu = ant.get('notlar', "")
                    # NOTU BURADA BİRLEŞTİRİYORUZ
                    if ant_notu:
                        detay += f"\n\n📝 ANTRENMAN NOTU:\n{ant_notu}"
                    
                    self.txt_antrenman_detay.setPlainText(detay)
                    
                    # Kalori hesaplama
                    kcal_val = str(ant.get('kalori', '0'))
                    kcal_str = "".join(filter(str.isdigit, kcal_val))
                    yakilan_toplam = int(kcal_str) if kcal_str else 0

            # --- BESLENME VERİLERİNİ ÇEK ---
            for bes in sporcu.get('beslenme_gecmisi', []):
                tarih = bes.get('tarih', '')
                item = QListWidgetItem(f"🥗 {tarih}")
                item.setData(Qt.UserRole, bes)
                self.list_gecmis_bes.addItem(item)

                if tarih == bugun:
                    # 'liste' metnini al, yoksa boş bırak
                    liste_metni = bes.get('liste', '')
                    
                    # Notu çek (Kaydederken 'notlar' ismini vermiştik)
                    bes_notu = bes.get('notlar', "") 
                    
                    # EĞER NOT VARSA LİSTENİN ALTINA EKLE
                    if bes_notu:
                        liste_metni += f"\n\n📝 BESLENME NOTU:\n{bes_notu}"
                    
                    # Sonucu kutuya yazdır
                    self.txt_beslenme_detay.setPlainText(liste_metni)
                    
                    # Kalori hesaplama
                    val = bes.get('toplam_kalori', 0)
                    alinan_toplam = int("".join(filter(str.isdigit, str(val)))) if str(val) else 0

            # --- KALORİ ANALİZİNİ GÜNCELLE ---
            self.kalori_analiz_guncelle(sporcu, bugun)

        except Exception as e:
            print(f"Detay Getirme Hatası: {e}")
    

    def gecmis_veriyi_yukle(self, item):
        try:
            veri = item.data(Qt.UserRole)
            self.lbl_baslik_bilgi.setText(f"📅 {veri.get('tarih','')}")

            # Eğer tıklanan bir Antrenman verisi ise
            if "hareketler" in veri or "program" in veri:
                detay = veri.get('hareketler') or veri.get('program') or ""
                ant_notu = veri.get('notlar', '')
                
                if ant_notu:
                    detay += f"\n\n📝 ANTRENMAN NOTU:\n{ant_notu}"
                
                self.txt_antrenman_detay.setPlainText(detay)
                self.txt_beslenme_detay.clear()

            # Eğer tıklanan bir Beslenme verisi ise
            elif "liste" in veri:
                liste_metni = veri.get('liste', '')
                bes_notu = veri.get('notlar', '')
                
                if bes_notu:
                    liste_metni += f"\n\n📝 BESLENME NOTU:\n{bes_notu}"
                
                self.txt_beslenme_detay.setPlainText(liste_metni)
                self.txt_antrenman_detay.clear()

        except Exception as e:
            print("Geçmiş yükleme hatası:", e)

    def kalori_analiz_guncelle(self, sporcu, tarih):
        """Kalori hesaplamasını yapar ve ekrana yazar"""
        yakilan = 0
        alinan = 0
        
        # 1. O tarihteki antrenmanı bul (Güvenli Rakam Çekme)
        for ant in sporcu.get('antrenman_gecmisi', []):
            if ant.get('tarih') == tarih:
                try:
                    # split yerine rakam ayıklama kullanıyoruz (Hata vermez)
                    k_str = "".join(filter(str.isdigit, str(ant.get('kalori', '0'))))
                    yakilan = int(k_str) if k_str else 0
                except: yakilan = 0
        
        # 2. O tarihteki beslenmeyi bul
        for bes in sporcu.get('beslenme_gecmisi', []):
            if bes.get('tarih') == tarih:
                try:
                    a_str = "".join(filter(str.isdigit, str(bes.get('toplam_kalori', '0'))))
                    alinan = int(a_str) if a_str else 0
                except: alinan = 0

        # 3. BMH Hesapla ve Net Durumu Bul (Yeni Mantık)
        try:
            kilo = float(str(sporcu.get('kilo', '70')).replace(',', '.'))
        except: kilo = 70.0
        
        bmh = int(kilo * 24)
        durum = alinan - (yakilan + bmh)
        
        # 4. Ekrana Yazdır
        renk = "#34D399" if durum <= 0 else "#FFB800" # Eksideyse Yeşil (Zayıflıyor)
        self.lbl_kalori_analiz.setText(f"Yakılan: {yakilan} | BMH: {bmh} | Alınan: {alinan} | NET: {durum} kcal")
        self.lbl_kalori_analiz.setStyleSheet(f"color: {renk}; font-weight: bold; font-size: 13px;")

    def kilo_guncelle_mekanizmasi(self):
        from datetime import datetime
        try:
            if not self.secili_sporcu_id:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Hata")
                msg.setText("Lütfen önce tablodan bir sporcu seçin!")

                msg.setStyleSheet("""
                QMessageBox {
                    background-color: #141824;
                }

                QLabel {
                    background-color: #141824;
                    color: white;
                }

                QPushButton {
                background-color: #38BDF8;
                color: #0F172A;
                padding: 6px 10px;
                border-radius: 6px;
                min-width: 15px;
            }
                """)

                msg.exec_()
                return

            # 1. Sporcuyu bul
            sporcu_index = -1
            for i, s in enumerate(self.ana_pencere.sistem.sporcular):
                if str(s.get('id')) == str(self.secili_sporcu_id):
                    sporcu_index = i
                    break
            
            if sporcu_index != -1:
                sporcu = self.ana_pencere.sistem.sporcular[sporcu_index]
                bugun = datetime.now().strftime("%d.%m.%Y")
                
                # 2. Kalori Verilerini Topla (Mevcut kodunuz aynı kalabilir)
                yakilan = 0
                alinan = 0
                for ant in sporcu.get('antrenman_gecmisi', []):
                    if ant.get('tarih') == bugun:
                        k = "".join(filter(str.isdigit, str(ant.get('kalori', '0'))))
                        yakilan = int(k) if k else 0
                
                for bes in sporcu.get('beslenme_gecmisi', []):
                    if bes.get('tarih') == bugun:
                        a = "".join(filter(str.isdigit, str(bes.get('toplam_kalori', '0'))))
                        alinan = int(a) if a else 0

                # 3. Kilo Hesapla
                eski_kilo = float(str(sporcu.get('kilo', '70')).replace(',', '.'))
                bmh = eski_kilo * 24
                net_kalori = alinan - (yakilan + bmh)
                yeni_kilo = round(eski_kilo + (net_kalori / 7000), 2)
                
                # --- GÜNCELLEME VE SENKRONİZASYON (BURASI KRİTİK) ---
                
                # A. Ana listedeki veriyi güncelle
                self.ana_pencere.sistem.kilo_guncelle(self.secili_sporcu_id, yeni_kilo)
                
                # B. Tüm tabloları (Yönetim, Dashboard, Antrenman) yeniden çizdir
                # Bu komut Yönetim sayfasındaki tabloyu anında günceller
                self.ana_pencere.tablolari_yenile()
                
                # C. Üstteki özet kartlarını (Toplam Sporcu vb.) tazele
                if hasattr(self.ana_pencere, 'kart_tazele'):
                    self.ana_pencere.kart_tazele()

                # D. Beslenme sayfası varsa oradaki verileri de tazele
                if hasattr(self.ana_pencere, 'sayfa_beslenme'):
                    if hasattr(self.ana_pencere.sayfa_beslenme, 'init_veri'):
                        self.ana_pencere.sayfa_beslenme.init_veri()
                
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Başarılı")
                msg.setText(f"Kilo sistem genelinde güncellendi!\nYeni: {yeni_kilo} kg")

                msg.setStyleSheet("""
                QMessageBox {
                    background-color: #141824;
                }

                QLabel {
                    color: white;
                    background-color: #141824;
                }

                QPushButton {
                background-color: #38BDF8;
                color: #0F172A;
                padding: 6px 10px;
                border-radius: 6px;
                min-width: 15px;
            }
                """)

                msg.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Genel güncelleme hatası: {str(e)}")
# --- 3. ANA UYGULAMA PENCERESİ ---

class FitnessApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sistem = FitnessSistemi()
        

        self.setWindowTitle("🏋️ Fitness Yönetim Paneli")
        self.setMinimumSize(1450, 850)
        self.setStyleSheet(f"background-color: {STIL['arka']};")

        merkez = QWidget()
        self.setCentralWidget(merkez)

        self.ana_layout = QHBoxLayout(merkez)
        self.ana_layout.setContentsMargins(0, 0, 0, 0)
        self.ana_layout.setSpacing(0)

        # ================= SIDEBAR =================
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet(
            f"background-color: {STIL['kart']}; border-right: 1px solid {STIL['kenar']};"
        )

        side_l = QVBoxLayout(self.sidebar)
        side_l.setContentsMargins(15, 20, 15, 20) # Kenar boşlukları
        side_l.setSpacing(0) # İç boşluğu manuel kontrol edeceğiz

        # LOGO (En üstte)
        logo = QLabel("🏋️ FİTNESS")
        logo.setStyleSheet(
            f"color: {STIL['vurgu_mavi']}; font-size: 24px; font-weight: 900; margin-bottom: 30px;"
        )
        logo.setAlignment(Qt.AlignCenter)
        side_l.addWidget(logo)

        # ================= BUTONLAR =================
        # Butonlar için ayrı bir layout oluşturup yukarıya yaslıyoruz
        self.btn_a = MenuButonu("📊 Dashboard")
        self.btn_y = MenuButonu("⚙️ Yönetim")
        self.btn_ant = MenuButonu("🏋️ Antrenman")
        self.btn_bes = MenuButonu("🥗 Beslenme")
        self.btn_tak = MenuButonu("🔍 Takip")

        self.btns = [self.btn_a, self.btn_y, self.btn_ant, self.btn_bes, self.btn_tak]

        # Butonları tek tek ekle ve aralarına küçük boşluklar koy
        for b in self.btns:
            side_l.addWidget(b)
            side_l.addSpacing(10) # Butonlar arası 10px boşluk

        # ALT BOŞLUK (Tüm butonları yukarı iten asıl güç budur)
        side_l.addStretch(1)

        # ================= SAYFALAR =================
        self.sayfalar = QStackedWidget()

        # Sayfaları tanımlarken crash olmaması için self (ana pencere) gönderiyoruz
        self.sayfa_sporcu = SporcuAnalizSayfasi() # Eğer bu sınıf parametre istemiyorsa böyle kalsın
        self.sayfa_yonetim = SporcuYonetimSayfasi(self)
        self.sayfa_antrenman = AntrenmanSayfasi(self)
        self.sayfa_beslenme = BeslenmeSayfasi(self)
        self.sayfa_takip = TakipSayfasi(self)

        self.sayfalar.addWidget(self.sayfa_sporcu)
        self.sayfalar.addWidget(self.sayfa_yonetim)
        self.sayfalar.addWidget(self.sayfa_antrenman)
        self.sayfalar.addWidget(self.sayfa_beslenme)
        self.sayfalar.addWidget(self.sayfa_takip)

        self.ana_layout.addWidget(self.sidebar)
        self.ana_layout.addWidget(self.sayfalar)

        # Sinyal Bağlantıları
        self.btn_a.clicked.connect(lambda: self.set_active(0))
        self.btn_y.clicked.connect(lambda: self.set_active(1))
        self.btn_ant.clicked.connect(lambda: self.set_active(2))
        self.btn_bes.clicked.connect(lambda: self.set_active(3))
        self.btn_tak.clicked.connect(lambda: self.set_active(4))

        # Tabloları ve kartları başlangıç verisiyle doldur
        self.tablolari_yenile()
        self.kart_tazele()

        # Default Aktif Sayfa
        self.set_active(0)

    # ================= SAFE PAGE SWITCH =================
    def set_active(self, index):
        try:
            # Butonların stillerini güncelle
            for i, b in enumerate(self.btns):
                is_active = (i == index)
                b.setChecked(is_active)
                b.update_style(is_active)

            # Sayfayı değiştir
            self.sayfalar.setCurrentIndex(index)
            
            # Eğer Takip sayfasına geçiliyorsa verileri tazele
            if index == 4:
                if hasattr(self, 'sayfa_takip'):
                    self.sayfa_takip.verileri_yukle()
                    
        except Exception as e:
            print(f"Sayfa geçiş hatası: {e}")
    
    # FitnessApp sınıfının içine ekleyin
    def global_kilo_guncelle(self, id_no, yeni_kilo):
        self.sistem.kilo_guncelle(id_no, yeni_kilo)
        self.tablolari_yenile()
        self.kart_tazele()

    def tablolari_yenile(self):

        self.sayfa_yonetim.tablo_y.setRowCount(0)
        self.sayfa_sporcu.tablo.setRowCount(0)
        self.sayfa_antrenman.tablo_liste.setRowCount(0)

        if hasattr(self, 'sayfa_takip'):
            self.sayfa_takip.tablo_sporcular.setRowCount(0)

        if hasattr(self, 'sayfa_beslenme'):
            self.sayfa_beslenme.tablo_liste.setRowCount(0)

        for i, sp in enumerate(self.sistem.sporcular):

            id_no = sp["id"]

            # ---------------- YÖNETİM ----------------
            ry = self.sayfa_yonetim.tablo_y.rowCount()
            self.sayfa_yonetim.tablo_y.insertRow(ry)

            y_vals = [
            str(id_no), 
            sp["ad"], 
            str(sp.get("yas", "")), 
            str(sp.get("cin", "")),
            sp["paket"], 
            f"{sp['boy']} cm",  # Buradaki virgül çok önemli!
            f"{sp['kilo']} kg", # Kilo artık kendi sütununa gidecek
            f"{sp['hedef']} kg", 
            sp["kayit"], 
            sp["bitis"], 
            sp["durum"]
        ]

            for c, val in enumerate(y_vals):
                self.sayfa_yonetim.tablo_y.setItem(ry, c, QTableWidgetItem(val))

            # ---------------- DASHBOARD ----------------
            rd = self.sayfa_sporcu.tablo.rowCount()
            self.sayfa_sporcu.tablo.insertRow(rd)

            bmi = sp["kilo"] / ((sp["boy"]/100)**2)
            hedef_durum = "✅ HEDEFTE" if sp["kilo"] <= sp["hedef"] else "⏳ DEVAM"

            d_vals = [
                sp["ad"], sp["cin"], str(sp["yas"]),
                f'{sp["boy"]} cm', f'{sp["kilo"]} kg',
                f"{bmi:.1f}", f'{sp["hedef"]} kg',
                sp["kayit"], sp["bitis"], sp["durum"], hedef_durum
            ]

            for c, val in enumerate(d_vals):
                self.sayfa_sporcu.tablo.setItem(rd, c, QTableWidgetItem(val))

            # ---------------- ANTRENMAN ----------------
            ra = self.sayfa_antrenman.tablo_liste.rowCount()
            self.sayfa_antrenman.tablo_liste.insertRow(ra)

            self.sayfa_antrenman.tablo_liste.setItem(ra, 0, QTableWidgetItem(str(id_no)))
            self.sayfa_antrenman.tablo_liste.setItem(ra, 1, QTableWidgetItem(sp["ad"]))

            # ---------------- BESLENME ----------------
            if hasattr(self, 'sayfa_beslenme'):
                rb = self.sayfa_beslenme.tablo_liste.rowCount()
                self.sayfa_beslenme.tablo_liste.insertRow(rb)

                self.sayfa_beslenme.tablo_liste.setItem(rb, 0, QTableWidgetItem(str(id_no)))
                self.sayfa_beslenme.tablo_liste.setItem(rb, 1, QTableWidgetItem(sp["ad"]))

            # ---------------- TAKİP ----------------
            if hasattr(self, 'sayfa_takip'):
                rt = self.sayfa_takip.tablo_sporcular.rowCount()
                self.sayfa_takip.tablo_sporcular.insertRow(rt)

                self.sayfa_takip.tablo_sporcular.setItem(rt, 0, QTableWidgetItem(str(id_no)))
                self.sayfa_takip.tablo_sporcular.setItem(rt, 1, QTableWidgetItem(sp["ad"]))
                self.sayfa_takip.tablo_sporcular.setItem(rt, 2, QTableWidgetItem(f"{sp['kilo']} kg"))
                self.sayfa_takip.tablo_sporcular.setItem(rt, 3, QTableWidgetItem(f"{sp['hedef']} kg"))

    def global_sporcu_ekle(self, ad, cin, yas, paket, boy, kilo, hedef):
        self.sistem.sporcu_ekle(ad, cin, yas, paket, boy, kilo, hedef)
        self.tablolari_yenile()
        self.kart_tazele()
        
    def global_sporcu_sil(self, id_no):
        self.sistem.sporcu_sil(id_no)
        self.tablolari_yenile()

    def global_sporcu_guncelle(self, id_no, ad, yas, cin, paket, boy, kilo, hedef):
        self.sistem.sporcu_guncelle(id_no, ad, yas, cin, paket, boy, kilo, hedef)
        self.tablolari_yenile()
        
    def id_tazele(self):
        for r in range(self.sayfa_yonetim.tablo_y.rowCount()): 
            new_id = str(r + 1)
            self.sayfa_yonetim.tablo_y.item(r, 0).setText(new_id)
            self.sayfa_sporcu.tablo.item(r, 0).setText(new_id)
            item = self.sayfa_antrenman.tablo_liste.item(r, 0)
            if item:
                item.setText(new_id)

    def kart_tazele(self):
        toplam = len(self.sistem.sporcular)
        aktif = sum(1 for sp in self.sistem.sporcular if "AKTİF" in sp["durum"])
        hedefte = sum(1 for sp in self.sistem.sporcular if sp["kilo"] <= sp["hedef"])

        self.sayfa_sporcu.k_toplam.lbl_deger.setText(str(toplam))
        self.sayfa_sporcu.k_aktif.lbl_deger.setText(str(aktif))
        self.sayfa_sporcu.k_hedef_tamam.lbl_deger.setText(str(hedefte))

if __name__ == "__main__":
    app = QApplication(sys.argv); ex = FitnessApp(); ex.show(); sys.exit(app.exec_())