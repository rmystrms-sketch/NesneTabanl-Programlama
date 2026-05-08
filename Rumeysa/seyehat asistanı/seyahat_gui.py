import sys
import os
import base64
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, QRegExp
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QRegExpValidator
from seyahat_sistemi import SeyahatAcentesi
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

STIL_LIGHT = """
    QMainWindow, QDialog, QStackedWidget { background-color: #F8FAFC; } 
    #Sidebar { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; min-width: 290px; }
    #NavBtn { background-color: transparent; color: #64748B; text-align: left; padding: 18px 22px; font-size: 15px; font-weight: bold; border: none; border-radius: 16px; margin: 4px 15px; }
    #NavBtn:hover { background-color: #F1F5F9; color: #8B5CF6; }
    #NavBtn:checked { background-color: #F5F3FF; color: #7C3AED; border-left: 6px solid #8B5CF6; font-weight: 900;}
    #IslemBtn { background-color: #8B5CF6; color: white; border-radius: 12px; padding: 14px; font-size: 14px; font-weight: bold; border: none; }
    #IslemBtn:hover { background-color: #7C3AED; }
    #IptalBtn { background-color: #F1F5F9; color: #475569; border-radius: 12px; padding: 14px; font-size: 14px; font-weight: bold; border: 1px solid #CBD5E1; }
    #IptalBtn:hover { background-color: #E2E8F0; }
    #SilBtn { background-color: #FEF2F2; color: #EF4444; border-radius: 10px; padding: 10px 15px; font-size: 13px; font-weight: bold; border: 1px solid #FECACA; }
    #SilBtn:hover { background-color: #FEE2E2; color: #DC2626; }
    #DuzenleBtn { background-color: #F0FDF4; color: #16A34A; border-radius: 10px; padding: 10px 15px; font-size: 13px; font-weight: bold; border: 1px solid #BBF7D0; }
    #DuzenleBtn:hover { background-color: #DCFCE7; color: #15803D; }
    #LinkBtn { background-color: transparent; color: #8B5CF6; border: none; font-weight: bold; text-decoration: underline; }
    #LinkBtn:hover { color: #7C3AED; }
    #SayfaBaslik { color: #0F172A; font-size: 28px; font-weight: 900; margin-top: 10px; margin-bottom: 20px; padding: 5px; }
    #PremiumText { color: #334155; }
    QGroupBox { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; margin-top: 25px; padding-top: 25px; padding-bottom: 20px; padding-left: 20px; padding-right: 20px; color: #334155; font-size: 15px; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; color: #8B5CF6; background-color: transparent; font-weight: bold; top: 0px; left: 15px; }
    QLineEdit, QSpinBox, QComboBox, QDateEdit { border: 1px solid #CBD5E1; border-radius: 12px; padding: 14px; background-color: #F8FAFC; color: #0F172A; font-size: 14px; font-weight: bold; }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus { border: 2px solid #8B5CF6; background-color: #FFFFFF; }
    #PlanKarti { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; margin-bottom:15px; }
    #GunlukKutu { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 14px; margin-bottom:15px; }
    QScrollArea { border: none; background-color: transparent; }
"""

class KoltukSecimEkrani(QDialog):
    """
    Ulaşım Modülü: Uçak ve Otobüs biletleri için görsel koltuk seçimi arayüzü.
    Gidiş ve dönüş koltuk seçimleri, yolcu sayısı ile eşleştirilerek kontrol edilir.
    """
    def __init__(self, ulasim_turu: str, bilet_fiyati: float, yolcu_sayisi: int, gidis_secilenler: Optional[List[str]] = None, donus_secilenler: Optional[List[str]] = None) -> None:
        super().__init__()
        self.ulasim_turu = ulasim_turu
        self.bilet_fiyati = bilet_fiyati
        self.yolcu_sayisi = yolcu_sayisi
        self.secili_gidis = gidis_secilenler if gidis_secilenler else []
        self.secili_donus = donus_secilenler if donus_secilenler else []
        self.toplam_maliyet = (len(self.secili_gidis) + len(self.secili_donus)) * self.bilet_fiyati
        
        self.setWindowTitle(f"Koltuk Seçimi - {self.ulasim_turu}")
        self.setFixedSize(550, 700)
        self.setStyleSheet(STIL_LIGHT)
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(f"<h2 style='text-align:center;'>💺 {self.ulasim_turu} Koltuk Seçimi</h2>"))
        self.layout.addWidget(QLabel(f"<p style='text-align:center; color:#64748B;'>Birim Fiyat: {self.bilet_fiyati} ₺ | Yolcu: {self.yolcu_sayisi}</p>"))
        
        self.lbl_uyari = QLabel("")
        self.lbl_uyari.setStyleSheet("color: #DC2626; font-weight: bold; text-align: center; font-size: 13px;")
        self.lbl_uyari.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_uyari)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab { padding: 10px 20px; font-weight: bold; font-size: 14px; }")
        
        self.sekme_gidis = QWidget()
        self.grid_gidis = QGridLayout(self.sekme_gidis)
        self.grid_gidis.setSpacing(10)
        
        self.sekme_donus = QWidget()
        self.grid_donus = QGridLayout(self.sekme_donus)
        self.grid_donus.setSpacing(10)
        
        self.tab_widget.addTab(self.sekme_gidis, "🛫 Gidiş Koltukları")
        self.tab_widget.addTab(self.sekme_donus, "🛬 Dönüş Koltukları")
        
        self.matris_olustur(self.grid_gidis, self.secili_gidis, "Gidis")
        self.matris_olustur(self.grid_donus, self.secili_donus, "Donus")
        
        self.layout.addWidget(self.tab_widget)
        self.uyari_guncelle()
        
        alt_layout = QHBoxLayout()
        self.lbl_toplam = QLabel(f"<b>Seçilen:</b> {len(self.secili_gidis)} Gidiş, {len(self.secili_donus)} Dönüş | <b>Maliyet:</b> {self.toplam_maliyet} ₺")
        self.lbl_toplam.setStyleSheet("font-size: 14px;")
        btn_onay = QPushButton("Seçimi Onayla")
        btn_onay.setObjectName("IslemBtn")
        btn_onay.clicked.connect(self.accept)
        
        alt_layout.addWidget(self.lbl_toplam)
        alt_layout.addWidget(btn_onay)
        self.layout.addStretch()
        self.layout.addLayout(alt_layout)

    def matris_olustur(self, grid: QGridLayout, secili_liste: List[str], tip: str) -> None:
        """Koltuk düzenini matris yapısına uygun şekilde arayüzde oluşturur."""
        satir_sayisi = 10
        sutun_harfleri = ['A', 'B', 'Koridor', 'C'] if self.ulasim_turu == "Otobüs" else ['A', 'B', 'C', 'Koridor', 'D', 'E', 'F']

        for satir in range(1, satir_sayisi + 1):
            sutun_idx = 0
            for harf in sutun_harfleri:
                if harf == 'Koridor':
                    grid.addWidget(QLabel("   "), satir, sutun_idx)
                else:
                    k_no = f"{satir}{harf}"
                    btn = QPushButton(k_no)
                    btn.setFixedSize(45, 45)
                    btn.setCheckable(True)
                    if k_no in secili_liste:
                        btn.setChecked(True)
                        btn.setStyleSheet("background-color: #10B981; color: white; border-radius: 8px; font-weight: bold;")
                    else:
                        btn.setStyleSheet("background-color: #E2E8F0; color: #334155; border-radius: 8px; font-weight: bold;")
                    
                    btn.clicked.connect(lambda checked, b=btn, adi=k_no, l=secili_liste: self.koltuk_tiklandi(b, adi, l))
                    grid.addWidget(btn, satir, sutun_idx)
                sutun_idx += 1

    def koltuk_tiklandi(self, btn: QPushButton, k_no: str, secili_liste: List[str]) -> None:
        """Kullanıcının koltuk butonuna tıklama aksiyonunu işler."""
        if btn.isChecked():
            secili_liste.append(k_no)
            btn.setStyleSheet("background-color: #10B981; color: white; border-radius: 8px; font-weight: bold;")
        else:
            if k_no in secili_liste: secili_liste.remove(k_no)
            btn.setStyleSheet("background-color: #E2E8F0; color: #334155; border-radius: 8px; font-weight: bold;")
            
        self.toplam_maliyet = (len(self.secili_gidis) + len(self.secili_donus)) * self.bilet_fiyati
        self.lbl_toplam.setText(f"<b>Seçilen:</b> {len(self.secili_gidis)} Gidiş, {len(self.secili_donus)} Dönüş | <b>Maliyet:</b> {self.toplam_maliyet} ₺")
        self.uyari_guncelle()

    def uyari_guncelle(self) -> None:
        """Yolcu kapasitesinden fazla koltuk seçilmesi durumunda uyarı mesajını günceller."""
        if len(self.secili_gidis) > self.yolcu_sayisi or len(self.secili_donus) > self.yolcu_sayisi:
            self.lbl_uyari.setText("⚠️ Uyarı: Yolcu sayısından fazla bilet seçtiniz!")
        else:
            self.lbl_uyari.setText("")

class KayitEkrani(QDialog):
    """
    Hesap Oluşturma Modülü: Yeni kullanıcıların sisteme kayıt olması için gerekli formu sunar.
    Veri doğrulamaları ve profil resmi yükleme işlemlerini içerir.
    """
    def __init__(self, sistem: SeyahatAcentesi) -> None:
        super().__init__()
        self.sistem = sistem
        self.secili_resim_yolu = ""
        self.setWindowTitle("Seyahat Asistanı Pro - Kayıt Ol")
        self.setFixedSize(450, 600)
        self.setStyleSheet(STIL_LIGHT) 
        
        layout = QVBoxLayout(self)
        self.ad_soyad = QLineEdit(); self.ad_soyad.setPlaceholderText("Adınız Soyadınız")
        self.ad_soyad.setValidator(QRegExpValidator(QRegExp("^[a-zA-ZğüşıöçĞÜŞİÖÇ ]+$")))
        self.kadi = QLineEdit(); self.kadi.setPlaceholderText("Kullanıcı Adı")
        self.eposta = QLineEdit(); self.eposta.setPlaceholderText("E-Posta (Örn: isim@mail.com)")
        self.sifre = QLineEdit(); self.sifre.setPlaceholderText("Şifre")
        self.sifre.setEchoMode(QLineEdit.Password)
        
        resim_layout = QHBoxLayout()
        self.lbl_resim_yolu = QLabel("Henüz resim seçilmedi.")
        self.lbl_resim_yolu.setStyleSheet("color: #64748B; font-size: 12px; font-style: italic;")
        btn_resim = QPushButton("📷 Profil Resmi Seç")
        btn_resim.setStyleSheet("background-color:#E2E8F0; color:#1E293B; border-radius:10px; padding:10px; font-weight:bold;")
        btn_resim.clicked.connect(self.resim_sec)
        resim_layout.addWidget(btn_resim); resim_layout.addWidget(self.lbl_resim_yolu)
        
        btn_kayit = QPushButton("Hesabımı Oluştur"); btn_kayit.setObjectName("IslemBtn"); btn_kayit.clicked.connect(self.kayit_ol)
        
        layout.addWidget(QLabel("<h2 style='text-align:center;' id='PremiumText'>Aramıza Katıl</h2>"))
        layout.addWidget(self.ad_soyad); layout.addWidget(self.kadi); layout.addWidget(self.eposta); layout.addWidget(self.sifre)
        layout.addSpacing(10); layout.addLayout(resim_layout); layout.addSpacing(20)
        layout.addWidget(btn_kayit); layout.addStretch()

    def resim_sec(self) -> None:
        """Kullanıcının yerel diskinden profil fotoğrafı seçmesini sağlar."""
        dosya, _ = QFileDialog.getOpenFileName(self, "Profil Resmi Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if dosya:
            self.secili_resim_yolu = dosya
            self.lbl_resim_yolu.setText(os.path.basename(dosya))

    def kayit_ol(self) -> None:
        """Formdaki verileri doğrular (Validation) ve veritabanına yeni kullanıcıyı kaydeder."""
        ad = self.ad_soyad.text().strip(); kadi = self.kadi.text().strip(); mail = self.eposta.text().strip().lower(); sifre = self.sifre.text().strip()
        if not all([ad, kadi, mail, sifre]): return QMessageBox.warning(self, "Uyarı", "Lütfen tüm zorunlu alanları doldurun!")
        if " " not in ad or len(ad.split()) < 2: return QMessageBox.warning(self, "Hata", "Lütfen adınızı ve soyadınızı boşluk bırakarak tam giriniz.")
        if not mail.endswith("@mail.com"): return QMessageBox.critical(self, "Hata", "E-posta adresi '@mail.com' ile bitmelidir!")
            
        basarili, msj = self.sistem.kullanici_kayit(ad, kadi, mail, sifre, self.secili_resim_yolu)
        if basarili:
            QMessageBox.information(self, "Başarılı", msj); self.accept()
        else: QMessageBox.warning(self, "Hata", msj)

class GirisEkrani(QDialog):
    """
    Kimlik Doğrulama Modülü: Kullanıcının sisteme giriş yapmasını (Authentication) sağlayan ana ekran.
    """
    def __init__(self, sistem: SeyahatAcentesi) -> None:
        super().__init__()
        self.sistem = sistem
        self.aktif_kul_veri: Dict[str, Any] = {}
        self.setWindowTitle("Seyahat Asistanı Pro")
        self.setFixedSize(450, 450)
        self.setStyleSheet(STIL_LIGHT)
        
        layout = QVBoxLayout(self)
        self.kadi = QLineEdit(); self.kadi.setPlaceholderText("Kullanıcı Adı veya E-Posta")
        self.sifre = QLineEdit(); self.sifre.setPlaceholderText("Şifre"); self.sifre.setEchoMode(QLineEdit.Password)
        
        btn_giris = QPushButton("Oturum Aç"); btn_giris.setObjectName("IslemBtn"); btn_giris.clicked.connect(self.giris)
        btn_kayit = QPushButton("Hesabınız yok mu? Yeni Hesap Oluşturun"); btn_kayit.setObjectName("LinkBtn"); btn_kayit.clicked.connect(lambda: KayitEkrani(self.sistem).exec_())
        btn_sifre_unuttum = QPushButton("Şifremi Unuttum"); btn_sifre_unuttum.setObjectName("LinkBtn"); btn_sifre_unuttum.clicked.connect(lambda: SifremiUnuttumEkrani(self.sistem).exec_())
        
        baslik = QLabel("🧭 Seyahat Asistanı Pro"); baslik.setStyleSheet("font-size: 28px; font-weight: 900; color: #8B5CF6; margin-bottom: 20px;"); baslik.setAlignment(Qt.AlignCenter)
        layout.addStretch(); layout.addWidget(baslik); layout.addWidget(self.kadi); layout.addWidget(self.sifre); layout.addSpacing(10)
        layout.addWidget(btn_giris); layout.addWidget(btn_kayit); layout.addWidget(btn_sifre_unuttum); layout.addStretch()
        
    def giris(self) -> None:
        """Kullanıcının girdiği kimlik bilgilerini doğrulayarak oturumu başlatır."""
        basarili, k_id, ad_soyad, k_adi, eposta, sifre, p_resim = self.sistem.kullanici_giris(self.kadi.text().strip(), self.sifre.text().strip())
        if basarili:
            self.aktif_kul_veri = {"id": k_id, "ad": ad_soyad, "kadi": k_adi, "eposta": eposta, "sifre": sifre, "resim": p_resim}
            self.accept()
        else: QMessageBox.critical(self, "Reddedildi", "Bilgilerinizi kontrol edin.")

class SifremiUnuttumEkrani(QDialog):
    """
    Parola Kurtarma Modülü: Kullanıcıların şifrelerini güvenli bir şekilde sıfırlamalarını sağlar.
    """
    def __init__(self, sistem: SeyahatAcentesi) -> None:
        super().__init__()
        self.sistem = sistem
        self.setWindowTitle("Şifremi Unuttum")
        self.setFixedSize(400, 350)
        self.setStyleSheet(STIL_LIGHT)
        
        layout = QVBoxLayout(self)
        self.kadi = QLineEdit(); self.kadi.setPlaceholderText("Kullanıcı Adı")
        self.eposta = QLineEdit(); self.eposta.setPlaceholderText("Kayıtlı E-Posta")
        self.yeni_sifre = QLineEdit(); self.yeni_sifre.setPlaceholderText("Yeni Şifre")
        self.yeni_sifre.setEchoMode(QLineEdit.Password)
        
        btn_sifirla = QPushButton("Şifremi Sıfırla")
        btn_sifirla.setObjectName("IslemBtn")
        btn_sifirla.clicked.connect(self.sifirla)
        
        layout.addWidget(QLabel("<h2 style='text-align:center;' id='PremiumText'>Şifre Yenileme</h2>"))
        layout.addWidget(self.kadi); layout.addWidget(self.eposta); layout.addWidget(self.yeni_sifre)
        layout.addSpacing(15); layout.addWidget(btn_sifirla); layout.addStretch()

    def sifirla(self) -> None:
        """Gerekli doğrulamaları yaptıktan sonra kullanıcının şifresini günceller."""
        k = self.kadi.text().strip(); m = self.eposta.text().strip(); s = self.yeni_sifre.text().strip()
        if not all([k, m, s]): return QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
        
        basarili, msj = self.sistem.sifre_sifirla(k, m, s)
        if basarili:
            QMessageBox.information(self, "Başarılı", msj)
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", msj)
class ProfilDuzenlemeEkrani(QDialog):
    """
    Hesap Yönetimi Modülü: Kullanıcıların kendi profillerini güncelleyebileceği arayüz.
    """
    def __init__(self, aktif_veri: Dict[str, Any], sistem: SeyahatAcentesi) -> None:
        super().__init__()
        self.sistem = sistem
        self.aktif_veri = aktif_veri
        self.yeni_resim_yolu = aktif_veri.get("resim", "")
        self.islem_basarili = False
        self.setWindowTitle("Hesabı Düzenle"); self.setFixedSize(400, 650); self.setStyleSheet(STIL_LIGHT)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2 style='text-align:center;' id='PremiumText'>Profili Düzenle</h2>"))
        self.in_ad = QLineEdit(); self.in_ad.setText(self.aktif_veri["ad"]); self.in_ad.setPlaceholderText("Ad Soyad")
        self.in_ad.setValidator(QRegExpValidator(QRegExp("^[a-zA-ZğüşıöçĞÜŞİÖÇ ]+$")))
        self.in_kadi = QLineEdit(); self.in_kadi.setText(self.aktif_veri["kadi"]); self.in_kadi.setPlaceholderText("Yeni Kullanıcı Adı")
        self.in_eposta = QLineEdit(); self.in_eposta.setText(self.aktif_veri.get("eposta", "")); self.in_eposta.setPlaceholderText("E-Posta (Örn: isim@mail.com)")
        self.in_sifre = QLineEdit(); self.in_sifre.setPlaceholderText("Şifreyi Güncelle")
        
        self.lbl_resim_durum = QLabel("Mevcut resim korunuyor." if self.yeni_resim_yolu else "Resim seçili değil.")
        self.lbl_resim_durum.setStyleSheet("color:#64748B; font-size:12px; margin-bottom:10px;")
        
        btn_resim = QPushButton("📷 Yeni Profil Resmi Seç"); btn_resim.setStyleSheet("background-color:#E2E8F0; color:#1E293B; border-radius:10px; padding:10px; font-weight:bold;"); btn_resim.clicked.connect(self.resim_sec)
        btn_resim_kaldir = QPushButton("🗑️ Profil Resmini Kaldır"); btn_resim_kaldir.setStyleSheet("background-color:#FEE2E2; color:#DC2626; border-radius:10px; padding:10px; font-weight:bold;"); btn_resim_kaldir.clicked.connect(self.resim_kaldir)
        btn_kaydet = QPushButton("Kaydet"); btn_kaydet.setObjectName("IslemBtn"); btn_kaydet.clicked.connect(self.kaydet)
        btn_iptal = QPushButton("İptal"); btn_iptal.setObjectName("IptalBtn"); btn_iptal.clicked.connect(self.reject)
        
        lbl_ad = QLabel("Ad Soyad:"); lbl_ad.setObjectName("PremiumText")
        lbl_kad = QLabel("Kullanıcı Adı:"); lbl_kad.setObjectName("PremiumText")
        lbl_eposta = QLabel("E-Posta:"); lbl_eposta.setObjectName("PremiumText")
        lbl_sifre = QLabel("Şifre:"); lbl_sifre.setObjectName("PremiumText")

        layout.addWidget(lbl_ad); layout.addWidget(self.in_ad); layout.addWidget(lbl_kad); layout.addWidget(self.in_kadi); layout.addWidget(lbl_eposta); layout.addWidget(self.in_eposta); layout.addWidget(lbl_sifre); layout.addWidget(self.in_sifre)
        layout.addSpacing(10); layout.addWidget(btn_resim); layout.addWidget(btn_resim_kaldir); layout.addWidget(self.lbl_resim_durum)
        layout.addSpacing(15); layout.addWidget(btn_kaydet); layout.addWidget(btn_iptal); layout.addStretch()

    def resim_sec(self) -> None:
        """Sistem dizininden profil resmi seçer."""
        dosya, _ = QFileDialog.getOpenFileName(self, "Yeni Profil Resmi", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if dosya: self.yeni_resim_yolu = dosya; self.lbl_resim_durum.setText(f"Seçildi: {os.path.basename(dosya)}")

    def resim_kaldir(self) -> None: 
        """Seçili olan profil resmini iptal eder/kaldırır."""
        self.yeni_resim_yolu = ""; self.lbl_resim_durum.setText("Resim kaldırılacak.")

    def kaydet(self) -> None:
        """Değiştirilmiş profil verilerini (Veri Entegrasyonu) doğrular ve veritabanına yazar."""
        ad = self.in_ad.text().strip()
        eposta = self.in_eposta.text().strip().lower()
        if " " not in ad or len(ad.split()) < 2: return QMessageBox.warning(self, "Hata", "Lütfen adınızı ve soyadınızı boşluk bırakarak tam giriniz.")
        if eposta and not eposta.endswith("@mail.com"): return QMessageBox.critical(self, "Hata", "E-posta adresi '@mail.com' ile bitmelidir!")

        basarili, msj = self.sistem.kullanici_guncelle(self.aktif_veri["id"], ad, self.in_kadi.text().strip(), eposta, self.in_sifre.text().strip(), self.yeni_resim_yolu)
        if basarili:
            if self.yeni_resim_yolu and os.path.exists(self.yeni_resim_yolu):
                self.yeni_resim_yolu = self.sistem._resim_kaydet(self.yeni_resim_yolu)
            self.aktif_veri.update({"ad": ad, "kadi": self.in_kadi.text().strip(), "eposta": eposta, "resim": self.yeni_resim_yolu})
            self.islem_basarili = True
            QMessageBox.information(self, "Başarılı", msj); self.accept()
        else: QMessageBox.warning(self, "Hata", msj)

class AnaPencere(QMainWindow):
    """
    Sistemin ana yönetim arayüzü (Dashboard). 
    Kullanıcının rota planlama, bütçe yönetimi ve aktiviteleri takip ettiği merkezi paneldir.
    """
    def __init__(self, aktif_veri: Dict[str, Any], sistem: SeyahatAcentesi) -> None:
        super().__init__()
        self.sistem = sistem
        self.aktif_veri = aktif_veri
        self.oturum_kapatilsin_mi = False 
        self.duzenlenen_plan_id = None
        
        self.setWindowTitle("Seyahat Asistanı Pro | Premium Panel")
        self.resize(1350, 850)
        self.setStyleSheet(STIL_LIGHT) 
        self.iller_listesi = self.sistem.illeri_getir()
        
        self.arayuzu_kur()
        self.arayuz_tazele()

    def golge_ekle(self, widget: QWidget) -> None:
        """Arayüz elemanlarına premium bir görünüm katmak için hafif gölge (DropShadow) uygular."""
        golge = QGraphicsDropShadowEffect()
        golge.setBlurRadius(35)
        golge.setColor(QColor(0, 0, 0, 15))
        golge.setOffset(0, 8)
        widget.setGraphicsEffect(golge)

    def dairesel_resim_olustur(self, base64_str: str, isim: str, boyut: int = 90) -> QPixmap:
        """Profil resmini dairesel formata dönüştürür, resim yoksa ismin baş harfini içeren bir avatar üretir."""
        hedef_pixmap = QPixmap(boyut, boyut); hedef_pixmap.fill(Qt.transparent)
        painter = QPainter(hedef_pixmap); painter.setRenderHint(QPainter.Antialiasing)
        yol = QPainterPath(); yol.addEllipse(0, 0, boyut, boyut); painter.setClipPath(yol)

        if base64_str:
            try:
                orijinal = QPixmap()
                orijinal.loadFromData(base64.b64decode(base64_str))
                orijinal = orijinal.scaled(boyut, boyut, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                painter.drawPixmap((boyut - orijinal.width()) // 2, (boyut - orijinal.height()) // 2, orijinal)
            except Exception as e: 
                print(f"Resim yükleme hatası: {e}")
                self._varsayilan_avatar_ciz(painter, hedef_pixmap, isim)
        else: self._varsayilan_avatar_ciz(painter, hedef_pixmap, isim)
        painter.end()
        return hedef_pixmap

    def _varsayilan_avatar_ciz(self, painter: QPainter, hedef_pixmap: QPixmap, isim: str) -> None:
        """Kullanıcının profil fotoğrafı yoksa varsayılan baş harfli avatarı çizer."""
        yol = QPainterPath(); yol.addEllipse(0, 0, hedef_pixmap.width(), hedef_pixmap.height())
        painter.fillPath(yol, QColor("#F5F3FF"))
        painter.setPen(QPen(QColor("#8B5CF6")))
        painter.setFont(QFont("Arial", 36, QFont.Bold))
        painter.drawText(hedef_pixmap.rect(), Qt.AlignCenter, isim[0].upper() if isim else "U")

    def arayuzu_kur(self) -> None:
        """Uygulamanın ana iskeletini ve sayfa geçiş (Navigation) bileşenlerini oluşturur."""
        ana_widget = QWidget(); self.setCentralWidget(ana_widget)
        ana_layout = QHBoxLayout(ana_widget); ana_layout.setContentsMargins(0,0,0,0); ana_layout.setSpacing(0)

        sidebar = QFrame(); sidebar.setObjectName("Sidebar")
        s_layout = QVBoxLayout(sidebar); s_layout.setContentsMargins(0, 40, 0, 30)
        
        self.profil_layout = QVBoxLayout(); self.profil_layout.setAlignment(Qt.AlignCenter)
        self.profil_guncelle_arayuz() 
        s_layout.addLayout(self.profil_layout); s_layout.addSpacing(40)

        self.btn_dash = QPushButton("🏠 Kontrol Merkezi"); self.btn_dash.setObjectName("NavBtn"); self.btn_dash.setCheckable(True)
        self.btn_plan = QPushButton("🗺️ Rota ve Konaklama"); self.btn_plan.setObjectName("NavBtn"); self.btn_plan.setCheckable(True)
        self.btn_akt = QPushButton("🎫 Keşif ve Aktiviteler"); self.btn_akt.setObjectName("NavBtn"); self.btn_akt.setCheckable(True)
        self.btn_dash.setChecked(True)
        s_layout.addWidget(self.btn_dash); s_layout.addWidget(self.btn_plan); s_layout.addWidget(self.btn_akt); s_layout.addStretch()
        
        btn_ayar = QPushButton("⚙️ Hesabı Düzenle"); btn_ayar.setObjectName("NavBtn"); btn_ayar.setStyleSheet(btn_ayar.styleSheet() + "font-size: 13px; color: #64748B;")
        btn_ayar.clicked.connect(lambda: self.profil_guncelle_arayuz() if ProfilDuzenlemeEkrani(self.aktif_veri, self.sistem).exec_() == QDialog.Accepted else None)
        btn_cikis = QPushButton("🚪 Oturumu Kapat"); btn_cikis.setObjectName("NavBtn"); btn_cikis.setStyleSheet(btn_cikis.styleSheet() + "font-size: 13px; color: #EF4444;")
        btn_cikis.clicked.connect(self.oturumu_kapat_aksiyon)
        
        s_layout.addWidget(btn_ayar); s_layout.addWidget(btn_cikis); ana_layout.addWidget(sidebar)

        self.sayfalar = QStackedWidget(); ana_layout.addWidget(self.sayfalar, 1)
        self.sayfa_kur_pano(); self.sayfa_kur_rota_otel(); self.sayfa_kur_aktivite()

        self.btn_dash.clicked.connect(lambda: self._sayfa_degistir(0, self.btn_dash))
        self.btn_plan.clicked.connect(lambda: self._sayfa_degistir(1, self.btn_plan))
        self.btn_akt.clicked.connect(lambda: self._sayfa_degistir(2, self.btn_akt))

    def profil_guncelle_arayuz(self) -> None:
        """Kullanıcı profil verileri değiştiğinde yan paneldeki (Sidebar) avatarı ve ismi günceller."""
        for i in reversed(range(self.profil_layout.count())): 
            w = self.profil_layout.itemAt(i).widget(); 
            if w: w.setParent(None)
        self.lbl_resim = QLabel()
        self.lbl_resim.setPixmap(self.dairesel_resim_olustur(self.aktif_veri["resim"], self.aktif_veri["ad"]))
        self.lbl_resim.setAlignment(Qt.AlignCenter)
        lbl_isim = QLabel(self.aktif_veri["ad"])
        lbl_isim.setStyleSheet("color: #0F172A; font-size: 19px; font-weight: 900; margin-top:12px;"); lbl_isim.setAlignment(Qt.AlignCenter)
        self.profil_layout.addWidget(self.lbl_resim); self.profil_layout.addWidget(lbl_isim)

    def oturumu_kapat_aksiyon(self) -> None:
        """Güvenli çıkış işlemini gerçekleştirir ve giriş ekranına yönlendirir."""
        if QMessageBox.question(self, 'Onay', 'Oturumu kapatıp çıkmak istediğinize emin misiniz?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.oturum_kapatilsin_mi = True; self.close()

    def _sayfa_degistir(self, index: int, aktif_btn: QPushButton) -> None:
        """Yan menüden seçilen sayfaya geçişi sağlar ve ilgili modülü (Rota/Bütçe vb.) yeniler."""
        self.btn_dash.setChecked(False); self.btn_plan.setChecked(False); self.btn_akt.setChecked(False)
        aktif_btn.setChecked(True); self.sayfalar.setCurrentIndex(index)
        if index == 0: self.istatistik_kartlarini_guncelle()
        elif index == 1:
            if self.duzenlenen_plan_id is None: self.duzenleme_modunu_sifirla()
            self.sehir_degisti_otelleri_getir()
        elif index == 2: self.plan_secildi_aktiviteleri_listele()

    def istatistik_kartlarini_guncelle(self) -> None:
        """Kontrol Merkezi (Dashboard) üzerindeki bütçe ve harcama istatistiklerini hesaplayarak günceller."""
        istatistikler = self.sistem.kullanici_istatistikleri_getir(self.aktif_veri["id"])
        
        self.lbl_stat_plan.setText(f"{istatistikler['toplam_plan']} Adet")
        self.lbl_stat_butce.setText(f"{istatistikler['toplam_harcama']:,.0f} ₺")
        
        toplam = istatistikler['toplam_harcama']
        if toplam > 0:
            otel_yuzde = int((istatistikler['otel_harcama'] / toplam) * 100)
            ulasim_yuzde = int((istatistikler.get('ulasim_harcama', 0) / toplam) * 100)
            akt_yuzde = 100 - otel_yuzde - ulasim_yuzde
            
            self.bar_otel.setStretchFactor(self.bar_otel_frame, otel_yuzde if otel_yuzde > 0 else 1)
            self.bar_ulasim.setStretchFactor(self.bar_ulasim_frame, ulasim_yuzde if ulasim_yuzde > 0 else 1)
            self.bar_akt.setStretchFactor(self.bar_akt_frame, akt_yuzde if akt_yuzde > 0 else 1)
            
            self.lbl_oran_text.setText(f"Otel: %{otel_yuzde} | Ulaşım: %{ulasim_yuzde} | Aktiviteler: %{akt_yuzde}")
        else:
            self.bar_otel.setStretchFactor(self.bar_otel_frame, 1)
            self.bar_ulasim.setStretchFactor(self.bar_ulasim_frame, 1)
            self.bar_akt.setStretchFactor(self.bar_akt_frame, 1)
            self.lbl_oran_text.setText("Henüz harcama yok.")
            
        arkaplan = "#FFFFFF"
        for kart in getattr(self, 'stat_kartlari', []):
            kart.setStyleSheet(f"background-color: {arkaplan}; border-radius: 16px; border: 1px solid #E2E8F0;")
            self.golge_ekle(kart)
    def sayfa_kur_pano(self) -> None:
        """Kontrol Merkezi (Dashboard) sekmesinin arayüz bileşenlerini, tablolarını ve grafiklerini oluşturur."""
        s0 = QWidget(); l0 = QVBoxLayout(s0); l0.setContentsMargins(20, 10, 20, 10); l0.setSpacing(10)
        lbl_baslik = QLabel("🏠 Seyahat Kontrol Merkezi", objectName="SayfaBaslik")
        lbl_baslik.setStyleSheet("margin-bottom: 5px;")
        l0.addWidget(lbl_baslik)
        
        stat_layout = QHBoxLayout()
        self.stat_kartlari = []
        
        k1 = QFrame(); l_k1 = QVBoxLayout(k1); l_k1.setContentsMargins(15, 10, 15, 10); l_k1.setSpacing(5)
        k1.setMaximumHeight(120)
        l_k1.addWidget(QLabel("🗺️ Toplam Planlar", styleSheet="color:#64748B; font-weight:bold; font-size:12px;"))
        self.lbl_stat_plan = QLabel("0 Adet"); self.lbl_stat_plan.setObjectName("PremiumText"); self.lbl_stat_plan.setStyleSheet("font-size:20px; font-weight:900;")
        l_k1.addWidget(self.lbl_stat_plan); self.stat_kartlari.append(k1); stat_layout.addWidget(k1)
        
        k2 = QFrame(); l_k2 = QVBoxLayout(k2); l_k2.setContentsMargins(15, 10, 15, 10); l_k2.setSpacing(5)
        k2.setMaximumHeight(120)
        l_k2.addWidget(QLabel("💰 Toplam Harcama", styleSheet="color:#64748B; font-weight:bold; font-size:12px;"))
        self.lbl_stat_butce = QLabel("0 ₺"); self.lbl_stat_butce.setObjectName("PremiumText"); self.lbl_stat_butce.setStyleSheet("font-size:20px; font-weight:900;")
        l_k2.addWidget(self.lbl_stat_butce); self.stat_kartlari.append(k2); stat_layout.addWidget(k2)
        
        k3 = QFrame(); l_k3 = QVBoxLayout(k3); l_k3.setContentsMargins(15, 10, 15, 10); l_k3.setSpacing(5)
        k3.setMaximumHeight(120)
        l_k3.addWidget(QLabel("📊 Harcama Dağılımı (Otel/Ulaşım/Etkinlik)", styleSheet="color:#64748B; font-weight:bold; font-size:12px;"))
        
        # Çok Renkli Dağılım Çubuğu (QFrame'lerle)
        self.bar_container = QFrame()
        self.bar_container.setFixedHeight(12)
        self.bar_container.setStyleSheet("background-color: #E2E8F0; border-radius: 6px;")
        bar_layout = QHBoxLayout(self.bar_container)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)
        
        self.bar_otel_frame = QFrame(); self.bar_otel_frame.setStyleSheet("background-color: #3B82F6; border-top-left-radius: 6px; border-bottom-left-radius: 6px;")
        self.bar_ulasim_frame = QFrame(); self.bar_ulasim_frame.setStyleSheet("background-color: #8B5CF6;")
        self.bar_akt_frame = QFrame(); self.bar_akt_frame.setStyleSheet("background-color: #F59E0B; border-top-right-radius: 6px; border-bottom-right-radius: 6px;")
        
        bar_layout.addWidget(self.bar_otel_frame, 1)
        bar_layout.addWidget(self.bar_ulasim_frame, 1)
        bar_layout.addWidget(self.bar_akt_frame, 1)
        
        self.bar_otel = bar_layout
        self.bar_ulasim = bar_layout
        self.bar_akt = bar_layout
        
        self.lbl_oran_text = QLabel("Henüz harcama yok.", styleSheet="font-size: 11px; color:#64748B;")
        l_k3.addWidget(self.bar_container); l_k3.addWidget(self.lbl_oran_text); self.stat_kartlari.append(k3); stat_layout.addWidget(k3)
        
        l0.addLayout(stat_layout); l0.addSpacing(5)
        
        # BÖLÜNME İŞLEMİ (YATAY / YAN YANA GÖSTERİM)
        ayirici = QSplitter(Qt.Horizontal)
        ayirici.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # SOL KOLON (Planlar Listesi)
        ust_widget = QWidget(); ust_layout = QVBoxLayout(ust_widget); ust_layout.setContentsMargins(0,0,10,0); ust_layout.setAlignment(Qt.AlignTop)
        
        lbl_sol_baslik = QLabel("Mevcut Seyahat Planlarınız", styleSheet="color:#64748B; font-size:16px; font-weight:bold; margin:0px; padding:0px;")
        lbl_sol_baslik.setFixedHeight(30)
        ust_layout.addWidget(lbl_sol_baslik)
        
        self.in_arama = QLineEdit()
        self.in_arama.setPlaceholderText("🔍 Şehir veya Plan ID ile hızlı arama yapın...")
        self.in_arama.textChanged.connect(self.planlari_filtrele)
        ust_layout.addWidget(self.in_arama)
        
        self.scroll_kartlar = QScrollArea(); self.scroll_kartlar.setWidgetResizable(True)
        self.kartlar_icerik = QWidget(); self.kartlar_layout = QVBoxLayout(self.kartlar_icerik); self.kartlar_layout.setAlignment(Qt.AlignTop); self.kartlar_layout.setSpacing(20) 
        self.scroll_kartlar.setWidget(self.kartlar_icerik)
        ust_layout.addWidget(self.scroll_kartlar)
        ayirici.addWidget(ust_widget)
        
        # SAĞ KOLON (Günlük Program ve PDF)
        alt_widget = QWidget(); alt_layout = QVBoxLayout(alt_widget); alt_layout.setContentsMargins(10,0,0,0); alt_layout.setAlignment(Qt.AlignTop)
        
        h_layout = QHBoxLayout(); h_layout.setContentsMargins(0,0,0,0)
        lbl_sag_baslik = QLabel("📅 Seçili Planın Günlük Programı", objectName="SayfaBaslik")
        lbl_sag_baslik.setStyleSheet("font-size:16px; margin:0px; padding:0px;")
        lbl_sag_baslik.setFixedHeight(30)
        h_layout.addWidget(lbl_sag_baslik)
        
        self.btn_pdf_indir = QPushButton("📄 Programı PDF İndir")
        self.btn_pdf_indir.setObjectName("IslemBtn"); self.btn_pdf_indir.setFixedWidth(200); self.btn_pdf_indir.setVisible(False)
        self.btn_pdf_indir.clicked.connect(self.pdf_olustur_aksiyon)
        h_layout.addWidget(self.btn_pdf_indir, 0, Qt.AlignRight)
        
        alt_layout.addLayout(h_layout)
        alt_layout.addSpacing(32) # Arama kutusu ile aynı hizada kalması için boşluk
        
        self.scroll_detay = QScrollArea(); self.scroll_detay.setWidgetResizable(True)
        self.detay_icerik = QWidget(); self.detay_layout = QVBoxLayout(self.detay_icerik); self.detay_layout.setAlignment(Qt.AlignTop); self.detay_layout.setSpacing(20)
        self.scroll_detay.setWidget(self.detay_icerik)
        alt_layout.addWidget(self.scroll_detay); ayirici.addWidget(alt_widget)
        
        # Oranları ayarla
        ayirici.setSizes([600, 600]); l0.addWidget(ayirici); self.sayfalar.addWidget(s0)

    def planlari_filtrele(self, aranan: str) -> None:
        """Kullanıcının girdiği anahtar kelimeye göre seyahat planları listesinde hızlı arama/filtreleme yapar."""
        aranan = aranan.lower().strip()
        for i in range(self.kartlar_layout.count()):
            w = self.kartlar_layout.itemAt(i).widget()
            if w and hasattr(w, 'plan_id'):
                sehir = getattr(w, 'sehir', "").lower()
                pid = str(w.plan_id)
                w.setVisible(aranan in sehir or aranan in pid)

    def gunluk_plan_aktivite_sil_aksiyon(self, akt_id: int, p_id: int) -> None:
        """Günlük plan detayları içinden seçili aktiviteyi veritabanından kalıcı olarak siler."""
        if self.sistem.plandan_aktivite_sil(akt_id)[0]:
            self.kart_secildi_detay_goster(p_id)

    def kart_secildi_detay_goster(self, plan_id: int) -> None:
        """Seçilen rotanın günlük mekan ve etkinlik detaylarını sağ panelde listeler."""
        self.btn_pdf_indir.setVisible(True)
        self.secili_pdf_plan_id = plan_id
        
        for i in reversed(range(self.detay_layout.count())): 
            w = self.detay_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        secili = next((p for p in self.sistem.tum_planlari_getir(self.aktif_veri["id"]) if p['plan_id'] == plan_id), None)
        if not secili: return

        if not secili['aktiviteler']:
            lbl_bos = QLabel("📌 Bu plana henüz aktivite/mekan eklenmemiş.")
            lbl_bos.setStyleSheet("color:#64748B; font-style:italic; margin-top:20px;")
            self.detay_layout.addWidget(lbl_bos)
            self.detay_layout.addStretch()
            return
            
        gunler = {}
        for a in secili['aktiviteler']:
            if a[3] not in gunler: gunler[a[3]] = []
            gunler[a[3]].append(a)
        
        for gun in sorted(gunler.keys()):
            kutu = QFrame(); kutu.setObjectName("GunlukKutu"); self.golge_ekle(kutu)
            kutu_l = QVBoxLayout(kutu); kutu_l.setContentsMargins(20, 20, 20, 20)
            kutu_l.addWidget(QLabel(f"📅 {gun}. GÜN PROGRAMI", styleSheet="color:#8B5CF6; font-size:15px; font-weight:900; margin-bottom:10px;"))
            
            for a in gunler[gun]:
                a_frame = QFrame()
                a_layout = QHBoxLayout(a_frame); a_layout.setContentsMargins(0,0,0,0)
                yazi_renk = "#0F172A"
                detay = f"<b style='color:{yazi_renk};'>{'🏛️' if a[4] == 'Mekan' else '🎭'} {a[1]}</b> <br/><span style='color:#64748B; font-size:13px;'>Tür: {a[4]} | Maliyet: {int(a[2])} ₺</span>"
                lbl_d = QLabel(detay); lbl_d.setTextFormat(Qt.RichText); lbl_d.setStyleSheet("margin-bottom:8px; font-size:14px;")
                
                btn_sil = QPushButton("Sil")
                btn_sil.setObjectName("SilBtn")
                btn_sil.setFixedWidth(60)
                btn_sil.clicked.connect(lambda ch, akt_id=a[0], pid=plan_id: self.gunluk_plan_aktivite_sil_aksiyon(akt_id, pid))
                
                a_layout.addWidget(lbl_d)
                a_layout.addWidget(btn_sil, 0, Qt.AlignRight)
                kutu_l.addWidget(a_frame)
                
            self.detay_layout.addWidget(kutu)
        self.detay_layout.addStretch()

    def pdf_olustur_aksiyon(self) -> None:
        """Seçili seyahat planının ve günlük aktivitelerin detaylarını PDF formatında dışa aktarır."""
        try:
            dosya_yolu, _ = QFileDialog.getSaveFileName(self, "PDF Olarak Kaydet", "Seyahat_Programi.pdf", "PDF Files (*.pdf)")
            if not dosya_yolu: return
            
            p_id = getattr(self, 'secili_pdf_plan_id', None)
            secili = next((p for p in self.sistem.tum_planlari_getir(self.aktif_veri["id"]) if p['plan_id'] == p_id), None)
            if not secili: return
            
            c = canvas.Canvas(dosya_yolu, pagesize=A4)
            y = 800
            
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, y, f"Seyahat Plani: {secili['sehir']}")
            y -= 30
            c.setFont("Helvetica", 12)
            c.drawString(50, y, f"Tarih: {secili['t_bas']} -> {secili['t_bit']} | Kisi Sayisi: {secili['kisi']}")
            y -= 20
            c.drawString(50, y, f"Konaklama: {secili['konaklama']}")
            y -= 20
            
            if secili.get('ulasim_turu'):
                c.drawString(50, y, f"Ulasim: {secili['ulasim_turu']} ({secili.get('ulasim_firmasi','')}) | Maliyet: {int(secili['ulasim_maliyeti'])} TL")
                y -= 20
                c.drawString(50, y, f"Gidis Koltuklar: {secili.get('gidis_koltuklar','')} | Donus Koltuklar: {secili.get('donus_koltuklar','')}")
                y -= 20
                
            c.drawString(50, y, f"Toplam Maliyet: {int(secili['toplam_maliyet'])} TL")
            y -= 40
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Gunluk Program:");
            y -= 20
            c.setFont("Helvetica", 11)
            
            if secili['aktiviteler']:
                for a in secili['aktiviteler']:
                    satir = f"{a[3]}. Gun: [{a[4]}] {a[1]} - {int(a[2])} TL"
                    satir = satir.replace('ı','i').replace('ş','s').replace('ç','c').replace('ğ','g').replace('ö','o').replace('ü','u').replace('İ','I').replace('Ş','S')
                    c.drawString(70, y, satir)
                    y -= 20
                    if y < 50:
                        c.showPage(); y = 800; c.setFont("Helvetica", 11)
            else:
                c.drawString(70, y, "Programa henuz aktivite eklenmemis.")
                
            c.save()
            QMessageBox.information(self, "Başarılı", "PDF başarıyla dışa aktarıldı!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı: {str(e)}")
    def sayfa_kur_rota_otel(self) -> None:
        """Rota ve Konaklama Asistanı sekmesinin form arayüzünü oluşturur (Adım 1-2-3)."""
        s1 = QWidget(); l1 = QVBoxLayout(s1); l1.setContentsMargins(50, 40, 50, 40)
        self.lbl_rota_baslik = QLabel("🗺️ Rota ve Konaklama Asistanı"); self.lbl_rota_baslik.setObjectName("SayfaBaslik")
        l1.addWidget(self.lbl_rota_baslik)
        
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        w = QWidget(); w_layout = QVBoxLayout(w); w_layout.setSpacing(25)
        
        adimlar_layout = QHBoxLayout()
        adimlar_layout.setSpacing(20)
        
        gb1 = QGroupBox("📌 Adım 1: Lokasyon ve Tarih"); form1 = QFormLayout()
        self.lbl_plan_id = QLabel(); self.lbl_plan_id.setStyleSheet("color:#8B5CF6; font-weight:bold; font-size:16px;")
        self.cb_sehir = QComboBox(); self.cb_sehir.addItems(self.iller_listesi); self.cb_sehir.currentIndexChanged.connect(self.sehir_degisti_otelleri_getir)
        
        self.in_t_bas = QDateEdit(QDate.currentDate()); self.in_t_bas.setCalendarPopup(True); self.in_t_bas.setMinimumDate(QDate.currentDate())
        self.in_t_bit = QDateEdit(QDate.currentDate().addDays(1)); self.in_t_bit.setCalendarPopup(True); self.in_t_bit.setMinimumDate(QDate.currentDate())
        self.lbl_gun_hesap = QLabel("Toplam: 1 Gece 2 Gün"); self.lbl_gun_hesap.setStyleSheet("color:#64748B; font-weight:bold;")
        self.in_t_bas.dateChanged.connect(self.tarih_hesapla); self.in_t_bit.dateChanged.connect(self.tarih_hesapla)
        
        self.in_kisi = QSpinBox(); self.in_kisi.setRange(1, 20); self.in_kisi.setSuffix(" Kişi")
        self.in_b_min = QSpinBox(); self.in_b_min.setRange(1, 9999999); self.in_b_min.setSuffix(" ₺"); self.in_b_min.setValue(1000)
        self.in_b_max = QSpinBox(); self.in_b_max.setRange(1, 9999999); self.in_b_max.setSuffix(" ₺"); self.in_b_max.setValue(5000)

        form1.addRow("Plan Referansı:", self.lbl_plan_id); form1.addRow("Hedef Şehir:", self.cb_sehir)
        form1.addRow("Gidiş - Dönüş:", QHBoxLayout()); form1.itemAt(2, QFormLayout.FieldRole).layout().addWidget(self.in_t_bas); form1.itemAt(2, QFormLayout.FieldRole).layout().addWidget(self.in_t_bit)
        form1.addRow("", self.lbl_gun_hesap); form1.addRow("Yolcu Sayısı:", self.in_kisi)
        form1.addRow("Bütçe (Min-Max):", QHBoxLayout()); form1.itemAt(5, QFormLayout.FieldRole).layout().addWidget(self.in_b_min); form1.itemAt(5, QFormLayout.FieldRole).layout().addWidget(self.in_b_max)
        gb1.setLayout(form1)
        self.golge_ekle(gb1)
        
        gb2 = QGroupBox("🏨 Adım 2: Konaklama"); form2 = QFormLayout()
        self.cb_oteller = QComboBox(); form2.addRow("Şehirdeki Tesisler:", self.cb_oteller); gb2.setLayout(form2)
        self.golge_ekle(gb2)

        self.guncel_ulasim_maliyeti = 0.0
        self.secili_gidis_listesi = []
        self.secili_donus_listesi = []
        
        gb3 = QGroupBox("🚀 Adım 3: Ulaşım ve Koltuk")
        form3 = QFormLayout()
        self.cb_ulasim = QComboBox()
        self.cb_ulasim.addItems(["Seçilmedi", "Otobüs (500 ₺)", "Uçak (1500 ₺)"])
        self.cb_ulasim.currentIndexChanged.connect(self._ulasim_degisti)
        
        self.cb_firma = QComboBox()
        self.cb_firma.setEnabled(False)
        self.cb_firma.addItems(["Önce Tür Seçin"])
        
        ulasim_h_layout = QHBoxLayout()
        self.btn_koltuk_sec = QPushButton("💺 Koltuk Seç")
        self.btn_koltuk_sec.setObjectName("IslemBtn")
        self.btn_koltuk_sec.setEnabled(False)
        self.btn_koltuk_sec.clicked.connect(self.koltuk_secimi_ac)
        
        self.lbl_secili_koltuk = QLabel("Henüz koltuk seçilmedi.")
        self.lbl_secili_koltuk.setStyleSheet("color:#64748B; font-weight:bold;")
        
        ulasim_h_layout.addWidget(self.cb_ulasim)
        ulasim_h_layout.addWidget(self.cb_firma)
        ulasim_h_layout.addWidget(self.btn_koltuk_sec)
        
        form3.addRow("Ulaşım & Firma:", ulasim_h_layout)
        form3.addRow("Durum:", self.lbl_secili_koltuk)
        gb3.setLayout(form3)
        self.golge_ekle(gb3)
        
        adimlar_layout.addWidget(gb1)
        adimlar_layout.addWidget(gb2)
        adimlar_layout.addWidget(gb3)
        
        self.btn_rota_kaydet = QPushButton("Rotayı Kaydet ve Planla"); self.btn_rota_kaydet.setObjectName("IslemBtn"); self.btn_rota_kaydet.setFixedHeight(55); self.btn_rota_kaydet.clicked.connect(self.yeni_rota_kaydet_aksiyon)
        
        w_layout.addLayout(adimlar_layout)
        w_layout.addWidget(self.btn_rota_kaydet)
        w_layout.addStretch()
        
        scroll.setWidget(w); l1.addWidget(scroll); self.sayfalar.addWidget(s1)

    def _ulasim_degisti(self) -> None:
        """Seçilen ulaşım türüne göre dinamik olarak firma listesini günceller."""
        secim = self.cb_ulasim.currentText()
        self.cb_firma.clear()
        if "Seçilmedi" in secim:
            self.btn_koltuk_sec.setEnabled(False)
            self.cb_firma.setEnabled(False)
            self.cb_firma.addItem("Önce Tür Seçin")
            self.secili_gidis_listesi = []
            self.secili_donus_listesi = []
            self.guncel_ulasim_maliyeti = 0.0
            self.lbl_secili_koltuk.setText("Ulaşım dahil edilmedi.")
        else:
            self.btn_koltuk_sec.setEnabled(True)
            self.cb_firma.setEnabled(True)
            if "Otobüs" in secim:
                self.cb_firma.addItems(["Kamil Koç", "Pamukkale", "Metro Turizm", "Ali Osman Ulusoy"])
            elif "Uçak" in secim:
                self.cb_firma.addItems(["Türk Hava Yolları", "Pegasus", "SunExpress", "AnadoluJet"])

    def koltuk_secimi_ac(self) -> None:
        """Koltuk seçim diyaloğunu açar ve kullanıcı seçimlerini bellekte tutar."""
        secim = self.cb_ulasim.currentText()
        if "Otobüs" in secim: turu = "Otobüs"; fiyat = 500
        elif "Uçak" in secim: turu = "Uçak"; fiyat = 1500
        else: return
        
        dialog = KoltukSecimEkrani(turu, fiyat, self.in_kisi.value(), self.secili_gidis_listesi, self.secili_donus_listesi)
        if dialog.exec_() == QDialog.Accepted:
            self.secili_gidis_listesi = dialog.secili_gidis
            self.secili_donus_listesi = dialog.secili_donus
            self.guncel_ulasim_maliyeti = dialog.toplam_maliyet
            self.lbl_secili_koltuk.setText(f"<span style='color:#10B981;'>Gidiş: {len(self.secili_gidis_listesi)}, Dönüş: {len(self.secili_donus_listesi)}</span> | 💰 Maliyet: {self.guncel_ulasim_maliyeti} ₺")

    def tarih_hesapla(self) -> None:
        """Gidiş ve dönüş tarihlerine göre otomatik gün sayısı hesabı yapar."""
        bas = self.in_t_bas.date(); bit = self.in_t_bit.date()
        if bit < bas: self.in_t_bit.setDate(bas); bit = bas
        self.lbl_gun_hesap.setText(f"Toplam: {bas.daysTo(bit)} Gece {bas.daysTo(bit) + 1} Gün")

    def sehir_degisti_otelleri_getir(self) -> None:
        """Hedef şehir değiştirildiğinde, o şehre ait konaklama seçeneklerini ComboBox'a yükler."""
        self.cb_oteller.clear()
        sehir = self.cb_sehir.currentText()
        for o in self.sistem.sehire_gore_oteller(sehir):
            self.cb_oteller.addItem(f"{o[3]} | {o[1]} - {int(o[2])} ₺", o[0])

    def plan_duzenleme_moduna_gec(self, plan_dict: Dict[str, Any]) -> None:
        """Mevcut bir planın detaylarını form alanlarına yükleyerek düzenleme modunu aktif eder."""
        self.duzenlenen_plan_id = plan_dict['plan_id']
        self.lbl_rota_baslik.setText("✏️ Plan Düzenleme Modu")
        self.lbl_plan_id.setText(f"#{self.duzenlenen_plan_id} (Düzenleniyor)")
        self.btn_rota_kaydet.setText("Değişiklikleri Veritabanına Kaydet")
        
        self.in_t_bas.clearMinimumDate()
        self.in_t_bit.clearMinimumDate()
        self.cb_sehir.setCurrentText(plan_dict['sehir'])
        self.in_t_bas.setDate(QDate.fromString(plan_dict['t_bas'], "yyyy-MM-dd"))
        self.in_t_bit.setDate(QDate.fromString(plan_dict['t_bit'], "yyyy-MM-dd"))
        
        self.in_kisi.setValue(plan_dict['kisi']); self.in_b_min.setValue(plan_dict['min_butce']); self.in_b_max.setValue(plan_dict['max_butce'])
        self.sehir_degisti_otelleri_getir()
        eski_otel_id = plan_dict['konaklama_id']
        if eski_otel_id:
            for i in range(self.cb_oteller.count()):
                if self.cb_oteller.itemData(i) == eski_otel_id:
                    self.cb_oteller.setCurrentIndex(i); break
                    
        eski_ulasim = plan_dict.get('ulasim_turu', "")
        if "Otobüs" in eski_ulasim: self.cb_ulasim.setCurrentIndex(1)
        elif "Uçak" in eski_ulasim: self.cb_ulasim.setCurrentIndex(2)
        else: self.cb_ulasim.setCurrentIndex(0)
        
        if eski_ulasim and plan_dict.get('ulasim_firmasi'):
            self.cb_firma.setCurrentText(plan_dict['ulasim_firmasi'])
            
        gidis = plan_dict.get('gidis_koltuklar', "")
        donus = plan_dict.get('donus_koltuklar', "")
        self.secili_gidis_listesi = gidis.split(",") if gidis else []
        self.secili_donus_listesi = donus.split(",") if donus else []
        
        self.guncel_ulasim_maliyeti = plan_dict.get('ulasim_maliyeti', 0.0)
        if self.secili_gidis_listesi or self.secili_donus_listesi:
            self.lbl_secili_koltuk.setText(f"<span style='color:#10B981;'>Gidiş: {len(self.secili_gidis_listesi)}, Dönüş: {len(self.secili_donus_listesi)}</span> | 💰 Maliyet: {self.guncel_ulasim_maliyeti} ₺")
            
        self._sayfa_degistir(1, self.btn_plan) 

    def duzenleme_modunu_sifirla(self) -> None:
        """Düzenleme modu iptal edildiğinde veya tamamlandığında form elemanlarını başlangıç haline getirir."""
        self.duzenlenen_plan_id = None
        self.lbl_rota_baslik.setText("🗺️ Rota ve Konaklama Asistanı")
        self.lbl_plan_id.setText(f"#{self.sistem.siradaki_plan_id_getir()}")
        self.btn_rota_kaydet.setText("Rotayı Kaydet ve Planla")
        self.in_t_bas.setMinimumDate(QDate.currentDate())
        self.in_t_bit.setMinimumDate(QDate.currentDate())
        self.in_t_bas.setDate(QDate.currentDate())
        self.in_t_bit.setDate(QDate.currentDate().addDays(1))
        self.cb_ulasim.setCurrentIndex(0)

    def yeni_rota_kaydet_aksiyon(self) -> None:
        """Formdaki tüm verileri derleyerek veritabanına yeni rota kaydeder veya mevcut rotayı günceller."""
        if self.in_b_min.value() > self.in_b_max.value(): return QMessageBox.warning(self, "Hata", "Minimum bütçe maksimumdan büyük olamaz!")
        sehir = self.cb_sehir.currentText()
        t_bas = self.in_t_bas.date().toString("yyyy-MM-dd")
        t_bit = self.in_t_bit.date().toString("yyyy-MM-dd")
        gun = self.in_t_bas.date().daysTo(self.in_t_bit.date()) + 1
        
        ulasim_turu = self.cb_ulasim.currentText().split("(")[0].strip() if "Seçilmedi" not in self.cb_ulasim.currentText() else ""
        ulasim_firmasi = self.cb_firma.currentText() if ulasim_turu else ""
        gidis_str = ",".join(self.secili_gidis_listesi)
        donus_str = ",".join(self.secili_donus_listesi)
        maliyet = self.guncel_ulasim_maliyeti
        
        if self.duzenlenen_plan_id: 
            basarili, msj = self.sistem.plan_guncelle(self.duzenlenen_plan_id, sehir, t_bas, t_bit, gun, self.in_kisi.value(), self.in_b_min.value(), self.in_b_max.value(), self.cb_oteller.currentData(), ulasim_turu, ulasim_firmasi, gidis_str, donus_str, maliyet)
        else: 
            basarili, msj = self.sistem.yeni_rota_ve_otel_kaydet(self.aktif_veri["id"], sehir, t_bas, t_bit, gun, self.in_kisi.value(), self.in_b_min.value(), self.in_b_max.value(), self.cb_oteller.currentData(), ulasim_turu, ulasim_firmasi, gidis_str, donus_str, maliyet)
        
        if basarili: QMessageBox.information(self, "Başarılı", msj); self.duzenleme_modunu_sifirla(); self.arayuz_tazele(); self._sayfa_degistir(0, self.btn_dash)
        else: QMessageBox.warning(self, "Hata", msj)

    def sayfa_kur_aktivite(self) -> None:
        """Keşif ve Aktiviteler modülünün kullanıcı arayüzünü oluşturur."""
        s2 = QWidget(); l2 = QVBoxLayout(s2); l2.setContentsMargins(50, 40, 50, 40)
        l2.addWidget(QLabel("🎫 Keşif ve Aktiviteler", objectName="SayfaBaslik"))
        
        icerik_layout = QHBoxLayout()
        icerik_layout.setSpacing(20)
        
        ust_w = QWidget(); ust_l = QVBoxLayout(ust_w); ust_l.setContentsMargins(0,0,0,0)
        gb = QGroupBox("Seyahatinize Renk Katın"); form = QFormLayout()
        self.cb_plan_akt = QComboBox(); self.cb_plan_akt.currentIndexChanged.connect(self.plan_secildi_kategorileri_doldur)
        self.in_gun_no = QComboBox()
        self.cb_mekanlar = QComboBox(); self.cb_etkinlikler = QComboBox()
        
        btn_mekan_ekle = QPushButton("Mekanı Ekle"); btn_mekan_ekle.setObjectName("IslemBtn"); btn_mekan_ekle.clicked.connect(lambda: self.aktivite_ekle(self.cb_mekanlar))
        btn_etk_ekle = QPushButton("Etkinliği Ekle"); btn_etk_ekle.setObjectName("IslemBtn"); btn_etk_ekle.clicked.connect(lambda: self.aktivite_ekle(self.cb_etkinlikler))
        
        self.lbl_kalan_butce = QLabel("Kalan Bütçe: - ₺"); self.lbl_kalan_butce.setStyleSheet("color:#64748B; font-weight:bold; font-size:16px;")
        
        m_layout = QHBoxLayout(); m_layout.addWidget(self.cb_mekanlar); m_layout.addWidget(btn_mekan_ekle)
        e_layout = QHBoxLayout(); e_layout.addWidget(self.cb_etkinlikler); e_layout.addWidget(btn_etk_ekle)
        
        form.addRow("Plan Seçin:", self.cb_plan_akt)
        form.addRow("Hangi Gün İçin?:", self.in_gun_no)
        form.addRow("Durum:", self.lbl_kalan_butce)
        form.addRow("🏛️ Keşfedilecek Yerler:", m_layout); form.addRow("🎭 Etkinlikler:", e_layout)
        gb.setLayout(form); ust_l.addWidget(gb); ust_l.addStretch()
        self.golge_ekle(gb)
        
        alt_w = QWidget(); alt_l = QVBoxLayout(alt_w); alt_l.setContentsMargins(0,0,0,0)
        gb_liste = QGroupBox("Bu Plana Eklenen Mekan ve Etkinlikler")
        gb_liste_l = QVBoxLayout(gb_liste)
        
        self.scroll_akt_liste = QScrollArea(); self.scroll_akt_liste.setWidgetResizable(True)
        self.akt_liste_icerik = QWidget(); self.akt_liste_layout = QVBoxLayout(self.akt_liste_icerik); self.akt_liste_layout.setAlignment(Qt.AlignTop); self.akt_liste_layout.setSpacing(10)
        self.scroll_akt_liste.setWidget(self.akt_liste_icerik)
        
        gb_liste_l.addWidget(self.scroll_akt_liste)
        self.golge_ekle(gb_liste)
        alt_l.addWidget(gb_liste)
        
        icerik_layout.addWidget(ust_w, 45)
        icerik_layout.addWidget(alt_w, 55)
        
        l2.addLayout(icerik_layout); self.sayfalar.addWidget(s2)

    def plan_secildi_kategorileri_doldur(self) -> None:
        """Yeni bir seyahat planı seçildiğinde günleri ve hedef şehirdeki aktiviteleri yükler."""
        hafiza_gun = self.in_gun_no.currentData()
        self.cb_mekanlar.clear(); self.cb_etkinlikler.clear(); self.in_gun_no.clear()
        sehir = self.cb_plan_akt.currentData()
        if not sehir: return
        
        try: gun = int(self.cb_plan_akt.currentText().split("(")[1].split(" ")[0])
        except: gun = 1
        for i in range(1, gun + 1): self.in_gun_no.addItem(f"{i}. Gün", i)

        for m in self.sistem.sehire_gore_aktiviteler(sehir, "Mekan"): self.cb_mekanlar.addItem(f"{m[1]} ({int(m[2])} ₺)", m)
        for e in self.sistem.sehire_gore_aktiviteler(sehir, "Etkinlik"): self.cb_etkinlikler.addItem(f"{e[1]} ({int(e[2])} ₺)", e)

        if hafiza_gun and self.in_gun_no.findData(hafiza_gun) >= 0: self.in_gun_no.setCurrentIndex(self.in_gun_no.findData(hafiza_gun))
        self.plan_secildi_aktiviteleri_listele()

    def plan_secildi_aktiviteleri_listele(self) -> None:
        """Kullanıcının mevcut rotasına atanmış mekan ve etkinlikleri dinamik olarak listeler."""
        for i in reversed(range(self.akt_liste_layout.count())): 
            w = self.akt_liste_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        p_metin = self.cb_plan_akt.currentText()
        if not p_metin: return
        
        p_id = int(p_metin.split("]")[0][2:])
        secili = next((p for p in self.sistem.tum_planlari_getir(self.aktif_veri["id"]) if p['plan_id'] == p_id), None)
        
        if secili:
            kalan_butce = secili['max_butce'] - secili['toplam_maliyet']
            if kalan_butce < 0: self.lbl_kalan_butce.setStyleSheet("color:#DC2626; font-weight:900;"); self.lbl_kalan_butce.setText(f"BÜTÇE AŞILDI! (Kalan: {int(kalan_butce)} ₺)")
            else: self.lbl_kalan_butce.setStyleSheet("color:#16A34A; font-weight:bold;"); self.lbl_kalan_butce.setText(f"Kalan Bütçe: {int(kalan_butce)} ₺")

            if secili['aktiviteler']:
                for a in secili['aktiviteler']:
                    kart = QFrame(); kart.setStyleSheet("background-color: #F8FAFC; border:1px solid #CBD5E1; border-radius:12px;")
                    k_lay = QHBoxLayout(kart)
                    yazi_renk = "#0F172A"
                    bilgi = QLabel(f"<b style='color:{yazi_renk};'>{a[3]}. Gün:</b> {'🏛️' if a[4] == 'Mekan' else '🎭'} <span style='color:{yazi_renk};'>{a[1]}</span> <span style='color:#64748B;'>({int(a[2])} ₺)</span>"); bilgi.setStyleSheet("border:none;")
                    btn_sil = QPushButton("Kaldır"); btn_sil.setObjectName("SilBtn"); btn_sil.setFixedWidth(80)
                    btn_sil.clicked.connect(lambda ch, akt_id=a[0]: self.tekil_aktivite_sil(akt_id))
                    k_lay.addWidget(bilgi); k_lay.addWidget(btn_sil); self.akt_liste_layout.addWidget(kart)
            else: self.akt_liste_layout.addWidget(QLabel("Bu plana henüz eklenmiş bir mekan veya etkinlik yok.", styleSheet="color:#94A3B8; font-style:italic;"))

    def tekil_aktivite_sil(self, akt_id: int) -> None:
        """Seçili aktiviteyi rotadan kaldırır ve arayüzü günceller."""
        if self.sistem.plandan_aktivite_sil(akt_id)[0]:
            mevcut_plan = self.cb_plan_akt.currentText()
            mevcut_gun = self.in_gun_no.currentData()
            self.arayuz_tazele()
            self.cb_plan_akt.setCurrentText(mevcut_plan)
            self.in_gun_no.setCurrentIndex(self.in_gun_no.findData(mevcut_gun))

    def aktivite_ekle(self, combobox: QComboBox) -> None:
        """Seçili gün için kullanıcı tarafından belirlenen etkinliği/mekanı rotaya dahil eder."""
        p_metin = self.cb_plan_akt.currentText(); veri = combobox.currentData()
        if not p_metin or not veri: return
        p_id = int(p_metin.split("]")[0][2:])
        basarili, msj = self.sistem.plana_aktivite_ekle(p_id, veri[1], veri[2], self.in_gun_no.currentData(), veri[3])
        if basarili:
            mevcut_plan = self.cb_plan_akt.currentText()
            mevcut_gun = self.in_gun_no.currentData()
            self.arayuz_tazele()
            self.cb_plan_akt.setCurrentText(mevcut_plan)
            self.in_gun_no.setCurrentIndex(self.in_gun_no.findData(mevcut_gun))
        else: QMessageBox.warning(self, "Ekleme Başarısız", msj)

    def plan_sil(self, p_id: int) -> None:
        """Kullanıcının seçtiği rotayı ve içindeki tüm etkinlik verilerini siler."""
        if QMessageBox.question(self, 'Onay', 'Planı tamamen silmek istiyor musunuz?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if self.sistem.plani_sil(p_id)[0]: self.arayuz_tazele()

    def arayuz_tazele(self) -> None:
        """Sistem veritabanındaki güncel bilgileri çekerek ekranlardaki plan listelerini yeniler."""
        mevcut_akt_secim = self.cb_plan_akt.currentText()
        mevcut_gun_secim = self.in_gun_no.currentData()
        self.cb_plan_akt.clear()
        
        if hasattr(self, 'stat_kartlari'):
            self.istatistik_kartlarini_guncelle()
        
        for i in reversed(range(self.kartlar_layout.count())): 
            w = self.kartlar_layout.itemAt(i).widget()
            if w: w.setParent(None)
        
        for p in self.sistem.tum_planlari_getir(self.aktif_veri["id"]):
            self.cb_plan_akt.addItem(f"[#{p['plan_id']}] {p['sehir']} ({p['gun']} Gün)", p['sehir'])
            kart = QFrame(); kart.setObjectName("PlanKarti")
            self.golge_ekle(kart)
            kart.plan_id = p['plan_id']
            kart.sehir = p['sehir']
            
            k_l = QVBoxLayout(kart); k_l.setContentsMargins(25, 25, 25, 25); k_l.setSpacing(12)
            
            bas_l = QHBoxLayout()
            yazi_renk = "#0F172A"
            bas_l.addWidget(QLabel(f"<b style='color:{yazi_renk};'>#{p['plan_id']} {p['sehir']}</b>", styleSheet="font-size:18px;"))
            
            btn_duzenle = QPushButton("Planı Düzenle"); btn_duzenle.setObjectName("DuzenleBtn"); btn_duzenle.setFixedWidth(120)
            btn_duzenle.clicked.connect(lambda ch, plan_veri=p: self.plan_duzenleme_moduna_gec(plan_veri))
            btn_sil = QPushButton("Planı Sil"); btn_sil.setObjectName("SilBtn"); btn_sil.setFixedWidth(100)
            btn_sil.clicked.connect(lambda ch, pid=p['plan_id']: self.plan_sil(pid))
            
            bas_l.addWidget(btn_duzenle, 0, Qt.AlignRight); bas_l.addWidget(btn_sil)
            k_l.addLayout(bas_l)
            
            gosterim_t_bas = QDate.fromString(p['t_bas'], "yyyy-MM-dd").toString("dd.MM.yyyy")
            gosterim_t_bit = QDate.fromString(p['t_bit'], "yyyy-MM-dd").toString("dd.MM.yyyy")
            
            ulasim_text = p.get('ulasim_turu', 'Seçilmedi') if p.get('ulasim_turu') else 'Seçilmedi'
            firma_text = p.get('ulasim_firmasi', '') if p.get('ulasim_firmasi') else ''
            tam_ulasim = f"{ulasim_text} ({firma_text})" if firma_text else ulasim_text
            k_l.addWidget(QLabel(f"🗓️ {gosterim_t_bas} - {gosterim_t_bit} | 👥 {p['kisi']} Kişi | 🏨 {p['konaklama']} | 🚀 {tam_ulasim}", styleSheet="font-size:14px; color:#475569;"))
            
            durum = f"<span style='color:{yazi_renk};'>💰 Maliyet: {int(p['toplam_maliyet'])} ₺ / Bütçe: {int(p['max_butce'])} ₺</span>"
            if p['toplam_maliyet'] > p['max_butce']: durum += " - <span style='color:#DC2626; font-weight:900;'>BÜTÇE AŞILDI!</span>"
            k_l.addWidget(QLabel(durum, styleSheet="font-size:14px;"))
            
            btn_detay = QPushButton("Günü Gününe İncele")
            btn_detay.setStyleSheet("background-color:#F5F3FF; color:#8B5CF6; border-radius:12px; padding:12px; font-weight:bold; margin-top:10px;")
            btn_detay.clicked.connect(lambda ch, pid=p['plan_id']: self.kart_secildi_detay_goster(pid))
            k_l.addWidget(btn_detay)
            self.kartlar_layout.addWidget(kart)
            
        self.kartlar_layout.addStretch()
        
        if mevcut_akt_secim: self.cb_plan_akt.setCurrentText(mevcut_akt_secim)
        if mevcut_gun_secim and hasattr(self, 'in_gun_no') and self.in_gun_no.findData(mevcut_gun_secim) >= 0: 
            self.in_gun_no.setCurrentIndex(self.in_gun_no.findData(mevcut_gun_secim))
        
        if hasattr(self, 'in_arama') and self.in_arama.text().strip():
            self.planlari_filtrele(self.in_arama.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    sistem = SeyahatAcentesi()
    
    while True:
        try:
            g = GirisEkrani(sistem)
            if g.exec_() == QDialog.Accepted:
                w = AnaPencere(g.aktif_kul_veri, sistem); w.show(); app.exec_() 
                if hasattr(w, 'oturum_kapatilsin_mi') and w.oturum_kapatilsin_mi: continue 
                else: break 
            else: break 
        except Exception as e: print(f"Hata: {str(e)}"); break