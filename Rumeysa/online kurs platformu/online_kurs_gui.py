import sys
import uuid
import re
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import QPrinter

from online_kurs_sistemleri import CourseSystem, Student, Teacher, Admin

# --- TASARIM VE RENKLER ---
FONTLAR = "Segoe UI"

KATEGORILER = ["Algoritma ve Programlama", "Backend Geliştirme", "Veritabanı Yönetimi", "Frontend Geliştirme", "UI/UX Tasarımı", "DevOps", "Mobil Geliştirme", "Kariyer ve Freelance"]

STIL_LIGHT = f"""
    QMainWindow, QDialog {{ background-color: #F5F7FA; font-family: '{FONTLAR}'; }}
    QFrame#Card {{ background-color: #FFFFFF; border-radius: 10px; border: 1px solid #E2E8F0; }}
    QPushButton {{ background-color: #4A90E2; color: white; border-radius: 6px; padding: 10px; font-weight: bold; font-family: '{FONTLAR}'; }}
    QPushButton:hover {{ background-color: #357ABD; }}
    QPushButton:disabled {{ background-color: #A0AEC0; }}
    QPushButton#BtnSuccess {{ background-color: #27AE60; }}
    QPushButton#BtnSuccess:hover {{ background-color: #219653; }}
    QPushButton#BtnWarning {{ background-color: #F39C12; }}
    QPushButton#BtnWarning:hover {{ background-color: #D68910; }}
    QPushButton#BtnError {{ background-color: #E74C3C; }}
    QPushButton#BtnError:hover {{ background-color: #CB4335; }}
    QPushButton#SidebarBtn {{ background-color: transparent; color: #1E2A38; text-align: left; padding: 15px; border-radius: 0px; font-weight: bold; }}
    QPushButton#SidebarBtn:hover {{ background-color: #E2E8F0; color: #4A90E2; border-left: 4px solid #4A90E2; }}
    QLineEdit, QComboBox, QTextEdit, QDateEdit, QSpinBox {{ padding: 10px; border: 1px solid #CBD5E0; border-radius: 6px; font-family: '{FONTLAR}'; }}
    QLineEdit:focus, QComboBox:focus {{ border: 2px solid #4A90E2; }}
    QLabel {{ color: #1E2A38; font-family: '{FONTLAR}'; }}
    QLabel#Title {{ font-size: 22px; font-weight: bold; }}
    QLabel#Subtitle {{ font-size: 16px; font-weight: 600; color: #4A5568; }}
    QLabel#ErrorText {{ color: #E74C3C; font-size: 12px; }}
    QTableWidget {{ background-color: white; alternate-background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; }}
    QHeaderView::section {{ background-color: #EDF2F7; padding: 8px; font-weight: bold; border: none; border-bottom: 2px solid #CBD5E0; }}
"""

STIL_DARK = f"""
    QMainWindow, QDialog {{ background-color: #121212; font-family: '{FONTLAR}'; }}
    QFrame#Card {{ background-color: #1E1E1E; border-radius: 10px; border: 1px solid #333333; }}
    QPushButton {{ background-color: #4A90E2; color: white; border-radius: 6px; padding: 10px; font-weight: bold; font-family: '{FONTLAR}'; }}
    QPushButton:hover {{ background-color: #357ABD; }}
    QPushButton:disabled {{ background-color: #555555; color: #888888; }}
    QPushButton#BtnSuccess {{ background-color: #27AE60; }}
    QPushButton#BtnSuccess:hover {{ background-color: #219653; }}
    QPushButton#BtnWarning {{ background-color: #F39C12; }}
    QPushButton#BtnWarning:hover {{ background-color: #D68910; }}
    QPushButton#BtnError {{ background-color: #E74C3C; }}
    QPushButton#BtnError:hover {{ background-color: #CB4335; }}
    QPushButton#SidebarBtn {{ background-color: transparent; color: #E0E0E0; text-align: left; padding: 15px; border-radius: 0px; font-weight: bold; }}
    QPushButton#SidebarBtn:hover {{ background-color: #333333; color: #4A90E2; border-left: 4px solid #4A90E2; }}
    QLineEdit, QComboBox, QTextEdit, QDateEdit, QSpinBox {{ padding: 10px; border: 1px solid #444444; border-radius: 6px; font-family: '{FONTLAR}'; background-color: #2A2A2A; color: white; }}
    QLineEdit:focus, QComboBox:focus {{ border: 2px solid #4A90E2; }}
    QLabel {{ color: #E0E0E0; font-family: '{FONTLAR}'; }}
    QLabel#Title {{ font-size: 22px; font-weight: bold; color: #FFFFFF; }}
    QLabel#Subtitle {{ font-size: 16px; font-weight: 600; color: #B0B0B0; }}
    QLabel#ErrorText {{ color: #FF6B6B; font-size: 12px; }}
    QTableWidget {{ background-color: #1E1E1E; color: white; alternate-background-color: #2A2A2A; border: 1px solid #333333; border-radius: 8px; }}
    QHeaderView::section {{ background-color: #333333; color: white; padding: 8px; font-weight: bold; border: none; border-bottom: 2px solid #555555; }}
"""

def drop_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setColor(QColor(0, 0, 0, 40))
    shadow.setOffset(0, 4)
    widget.setGraphicsEffect(shadow)

class MiniGraph(QFrame):
    def __init__(self, data_dict):
        super().__init__()
        self.setFixedHeight(150)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignBottom)
        max_val = max(data_dict.values()) if data_dict.values() else 1
        for k, v in data_dict.items():
            bar_container = QVBoxLayout()
            bar = QFrame()
            bar.setStyleSheet("background-color: #4A90E2; border-radius: 4px;")
            h = int((v / max_val) * 120) if max_val > 0 else 10
            bar.setFixedHeight(max(h, 5))
            bar_container.addStretch()
            bar_container.addWidget(bar)
            lbl = QLabel(str(k)); lbl.setStyleSheet("font-size: 10px;"); lbl.setAlignment(Qt.AlignCenter)
            bar_container.addWidget(lbl)
            layout.addLayout(bar_container)

# --- YARDIMCI ARAÇLAR ---
class SafeButton(QPushButton):
    """ Tıklamayı geciktiren ve çoklu tıklamayı önleyen buton """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.clicked.connect(self.disable_temporarily)

    def disable_temporarily(self):
        self.setEnabled(False)
        QTimer.singleShot(1500, lambda: self.setEnabled(True))

class ImageViewer(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Görsel İnceleme")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #121212;")
        l = QVBoxLayout(self)
        lbl = QLabel()
        pix = QPixmap(image_path)
        if not pix.isNull():
            lbl.setPixmap(pix.scaled(780, 580, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            lbl.setAlignment(Qt.AlignCenter)
        else:
            lbl.setText("Görsel yüklenemedi.")
            lbl.setStyleSheet("color: white;")
        l.addWidget(lbl)

# --- GİRİŞ EKRANLARI ---
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 350)
        
        layout = QVBoxLayout(self)
        self.kart = QFrame()
        self.kart.setObjectName("Card")
        self.kart.setStyleSheet("background-color: #1E2A38; border-radius: 15px;")
        drop_shadow(self.kart)
        
        k_layout = QVBoxLayout(self.kart)
        
        baslik = QLabel("Online Kurs Sistemleri")
        baslik.setObjectName("Title")
        baslik.setStyleSheet("color: white; font-size: 28px;")
        baslik.setAlignment(Qt.AlignCenter)
        
        self.info = QLabel("Sistem Başlatılıyor...")
        self.info.setStyleSheet("color: #4A90E2; font-size: 14px;")
        self.info.setAlignment(Qt.AlignCenter)
        
        self.pbar = QProgressBar()
        self.pbar.setTextVisible(False)
        self.pbar.setFixedHeight(10)
        self.pbar.setStyleSheet("QProgressBar { background-color: #2C3E50; border-radius: 5px; } QProgressBar::chunk { background-color: #4A90E2; border-radius: 5px; }")
        
        k_layout.addStretch()
        k_layout.addWidget(baslik)
        k_layout.addSpacing(20)
        k_layout.addWidget(self.info)
        k_layout.addWidget(self.pbar)
        k_layout.addStretch()
        
        layout.addWidget(self.kart)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.ilerle)
        self.progress = 0
        self.timer.start(30) # 30ms * 100 = 3 saniye

    def ilerle(self):
        self.progress += 1
        self.pbar.setValue(self.progress)
        if self.progress >= 100:
            self.timer.stop()
            self.close()
            self.main_app = AuthWindow()
            self.main_app.show()

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sistem = CourseSystem()
        self.setWindowTitle("Sisteme Giriş")
        self.setFixedSize(900, 600)
        self.setStyleSheet(STIL_LIGHT)
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        self.init_login()
        self.init_register()
        self.init_forgot()

    def init_login(self):
        sayfa = QWidget()
        layout = QHBoxLayout(sayfa)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sol Taraf: Görsel / Branding
        sol_frame = QFrame()
        sol_frame.setStyleSheet("background-color: #1E2A38;")
        sol_layout = QVBoxLayout(sol_frame)
        sol_layout.addStretch()
        l_baslik = QLabel("Eğitime\nYön Verin")
        l_baslik.setStyleSheet("color: white; font-size: 42px; font-weight: bold;")
        l_baslik.setAlignment(Qt.AlignCenter)
        sol_layout.addWidget(l_baslik)
        
        l_alt = QLabel("Yeni Nesil\nÖğrenme Platformu")
        l_alt.setStyleSheet("color: #A0AEC0; font-size: 18px; margin-top: 15px;")
        l_alt.setAlignment(Qt.AlignCenter)
        sol_layout.addWidget(l_alt)
        sol_layout.addStretch()
        
        # Sağ Taraf: Form
        sag_frame = QFrame()
        sag_frame.setStyleSheet("background-color: white;")
        sag_layout = QVBoxLayout(sag_frame)
        sag_layout.setContentsMargins(60, 40, 60, 40)
        
        baslik = QLabel("Sisteme Giriş Yapın 🚀")
        baslik.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E2A38;")
        baslik.setAlignment(Qt.AlignCenter)
        
        # Rol Seçimi
        h_rol = QHBoxLayout()
        h_rol.setSpacing(10)
        
        self.btn_rol_ogr = QPushButton("👨‍🎓 Öğrenci")
        self.btn_rol_egt = QPushButton("👨‍🏫 Eğitmen")
        self.btn_rol_adm = QPushButton("🛡️ Yönetici")
        
        rol_grup = QButtonGroup(self)
        for b in [self.btn_rol_ogr, self.btn_rol_egt, self.btn_rol_adm]:
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton { background-color: #EDF2F7; color: #4A5568; border: 1px solid #CBD5E0; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }
                QPushButton:checked { background-color: #3182CE; color: white; border: 1px solid #3182CE; }
                QPushButton:hover:!checked { background-color: #E2E8F0; }
            """)
            rol_grup.addButton(b)
            h_rol.addWidget(b)
            
        self.btn_rol_ogr.setChecked(True)
        
        self.l_eposta = QLineEdit(); self.l_eposta.setPlaceholderText("E-posta Adresiniz")
        self.l_eposta.setStyleSheet("padding: 12px; border-radius: 6px; border: 1px solid #CBD5E0; font-size: 14px; background-color: #F7FAFC;")
        
        self.l_sifre = QLineEdit(); self.l_sifre.setPlaceholderText("Şifreniz"); self.l_sifre.setEchoMode(QLineEdit.Password)
        self.l_sifre.setStyleSheet("padding: 12px; border-radius: 6px; border: 1px solid #CBD5E0; font-size: 14px; background-color: #F7FAFC;")
        
        self.hata_lbl = QLabel(""); self.hata_lbl.setObjectName("ErrorText")
        self.hata_lbl.setAlignment(Qt.AlignCenter)
        
        btn_giris = SafeButton("Giriş Yap")
        btn_giris.setStyleSheet("background-color: #3182CE; color: white; padding: 14px; border-radius: 6px; font-weight: bold; font-size: 15px;")
        btn_giris.clicked.connect(self.giris_yap)
        
        btn_kayit = QPushButton("Hesabınız yok mu? Kayıt Ol")
        btn_kayit.setStyleSheet("background: transparent; color: #4A90E2; text-decoration: underline; font-weight: bold; font-size: 13px;")
        btn_kayit.setCursor(Qt.PointingHandCursor)
        btn_kayit.clicked.connect(lambda: self.central_widget.setCurrentIndex(1))
        
        btn_sifre = QPushButton("Şifremi Unuttum")
        btn_sifre.setStyleSheet("background: transparent; color: #A0AEC0; font-size: 12px;")
        btn_sifre.setCursor(Qt.PointingHandCursor)
        btn_sifre.clicked.connect(lambda: self.central_widget.setCurrentIndex(2))
        
        sag_layout.addStretch()
        sag_layout.addWidget(baslik)
        sag_layout.addSpacing(25)
        sag_layout.addLayout(h_rol)
        sag_layout.addSpacing(15)
        sag_layout.addWidget(QLabel("E-posta:", styleSheet="color: #4A5568; font-weight: bold;"))
        sag_layout.addWidget(self.l_eposta)
        sag_layout.addSpacing(10)
        sag_layout.addWidget(QLabel("Şifre:", styleSheet="color: #4A5568; font-weight: bold;"))
        sag_layout.addWidget(self.l_sifre)
        sag_layout.addWidget(self.hata_lbl)
        sag_layout.addSpacing(15)
        sag_layout.addWidget(btn_giris)
        sag_layout.addSpacing(10)
        sag_layout.addWidget(btn_kayit)
        sag_layout.addWidget(btn_sifre)
        sag_layout.addStretch()
        
        layout.addWidget(sol_frame, 5)
        layout.addWidget(sag_frame, 6)
        self.central_widget.addWidget(sayfa)

    def init_register(self):
        sayfa = QWidget()
        layout = QVBoxLayout(sayfa)
        layout.setAlignment(Qt.AlignCenter)
        
        kart = QFrame(); kart.setObjectName("Card"); kart.setFixedWidth(500)
        k_layout = QVBoxLayout(kart)
        k_layout.setContentsMargins(30, 30, 30, 30)
        
        k_layout.addWidget(QLabel("Kayıt Ol", objectName="Title"))
        
        self.r_isim = QLineEdit(); self.r_isim.setPlaceholderText("Ad Soyad")
        isim_val = QRegularExpressionValidator(QRegularExpression(r"^[A-Za-zçÇğĞıİöÖşŞüÜ \s]+$"))
        self.r_isim.setValidator(isim_val)
        
        self.r_eposta = QLineEdit(); self.r_eposta.setPlaceholderText("E-posta")
        self.r_sifre = QLineEdit(); self.r_sifre.setPlaceholderText("Şifre"); self.r_sifre.setEchoMode(QLineEdit.Password)
        
        self.r_rol = QComboBox()
        self.r_rol.addItems(["Öğrenci", "Eğitmen"])
        
        self.r_soru = QComboBox()
        self.r_soru.addItems(["İlk evcil hayvanınız nedir?", "En sevdiğiniz öğretmen kimdi?", "Doğduğunuz şehir nedir?"])
        self.r_cevap = QLineEdit(); self.r_cevap.setPlaceholderText("Güvenlik Cevabı")
        
        self.r_hata = QLabel(""); self.r_hata.setObjectName("ErrorText")
        
        btn_kayit = SafeButton("Kayıt Ol")
        btn_kayit.clicked.connect(self.kayit_ol)
        
        btn_geri = QPushButton("Geri Dön"); btn_geri.setStyleSheet("background: transparent; color: #4A90E2;")
        btn_geri.clicked.connect(lambda: self.central_widget.setCurrentIndex(0))
        
        k_layout.addWidget(self.r_isim)
        k_layout.addWidget(self.r_eposta)
        k_layout.addWidget(self.r_sifre)
        k_layout.addWidget(self.r_rol)
        k_layout.addWidget(QLabel("Güvenlik Sorusu:"))
        k_layout.addWidget(self.r_soru)
        k_layout.addWidget(self.r_cevap)
        k_layout.addWidget(self.r_hata)
        k_layout.addWidget(btn_kayit)
        k_layout.addWidget(btn_geri)
        
        layout.addWidget(kart)
        self.central_widget.addWidget(sayfa)

    def init_forgot(self):
        sayfa = QWidget()
        layout = QVBoxLayout(sayfa)
        layout.setAlignment(Qt.AlignCenter)
        kart = QFrame(); kart.setObjectName("Card"); kart.setFixedWidth(500)
        k_layout = QVBoxLayout(kart)
        k_layout.setContentsMargins(30,30,30,30)
        
        k_layout.addWidget(QLabel("Şifre Sıfırlama", objectName="Title"))
        
        self.f_eposta = QLineEdit(); self.f_eposta.setPlaceholderText("E-posta")
        self.f_soru = QComboBox()
        self.f_soru.addItems(["İlk evcil hayvanınız nedir?", "En sevdiğiniz öğretmen kimdi?", "Doğduğunuz şehir nedir?"])
        self.f_cevap = QLineEdit(); self.f_cevap.setPlaceholderText("Güvenlik Cevabı")
        self.f_yeni = QLineEdit(); self.f_yeni.setPlaceholderText("Yeni Şifre"); self.f_yeni.setEchoMode(QLineEdit.Password)
        self.f_hata = QLabel(""); self.f_hata.setObjectName("ErrorText")
        
        btn_sifirla = SafeButton("Şifremi Sıfırla")
        btn_sifirla.clicked.connect(self.sifre_sifirla)
        
        btn_geri = QPushButton("Geri Dön"); btn_geri.setStyleSheet("background: transparent; color: #4A90E2;")
        btn_geri.clicked.connect(lambda: self.central_widget.setCurrentIndex(0))
        
        k_layout.addWidget(self.f_eposta)
        k_layout.addWidget(self.f_soru)
        k_layout.addWidget(self.f_cevap)
        k_layout.addWidget(self.f_yeni)
        k_layout.addWidget(self.f_hata)
        k_layout.addWidget(btn_sifirla)
        k_layout.addWidget(btn_geri)
        
        layout.addWidget(kart)
        self.central_widget.addWidget(sayfa)

    def giris_yap(self):
        eposta = self.l_eposta.text().strip()
        sifre = self.l_sifre.text()
        
        secilen_rol = ""
        if self.btn_rol_ogr.isChecked(): secilen_rol = "Student"
        elif self.btn_rol_egt.isChecked(): secilen_rol = "Teacher"
        elif self.btn_rol_adm.isChecked(): secilen_rol = "Admin"
        
        try:
            user = self.sistem.giris_yap(eposta, sifre)
            
            if user.rol != secilen_rol:
                role_names = {"Student": "Öğrenci", "Teacher": "Eğitmen", "Admin": "Yönetici"}
                raise ValueError(f"Bu hesap bir {role_names.get(user.rol, 'Bilinmeyen')} hesabıdır. Lütfen doğru rolü seçerek giriş yapın.")
                
            self.main_app = MainApplication(user, self.sistem)
            self.main_app.show()
            self.close()
        except Exception as e:
            self.hata_lbl.setText(str(e))
            self.hata_lbl.setStyleSheet("color: #E53E3E; font-weight: bold;")

    def kayit_ol(self):
        isim = self.r_isim.text().strip()
        eposta = self.r_eposta.text().strip()
        sifre = self.r_sifre.text()
        rol = "Student" if self.r_rol.currentText() == "Öğrenci" else "Teacher"
        soru = self.r_soru.currentText()
        cevap = self.r_cevap.text().strip()
        
        try:
            # Uzmanlık parametresi kaldırıldı, boş string ("") atandı
            self.sistem.kayit_ol(isim, eposta, sifre, rol, soru, cevap, "")
            QMessageBox.information(self, "Başarılı", "Kayıt işlemi başarılı, lütfen giriş yapın.")
            self.central_widget.setCurrentIndex(0)
        except Exception as e:
            self.r_hata.setText(str(e))

    def sifre_sifirla(self):
        eposta = self.f_eposta.text().strip()
        soru = self.f_soru.currentText()
        cevap = self.f_cevap.text().strip()
        yeni = self.f_yeni.text()
        try:
            self.sistem.sifre_sifirla(eposta, soru, cevap, yeni)
            QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla sıfırlandı!")
            self.central_widget.setCurrentIndex(0)
        except Exception as e:
            self.f_hata.setText(str(e))

class MainApplication(QMainWindow):
    def __init__(self, user, sistem):
        super().__init__()
        self.user = user
        self.sistem = sistem
        self.dark_mode = False
        self.oturum_baslangic = datetime.now()
        
        self.setWindowTitle(f"Online Kurs Sistemleri - {self.user.rol}")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STIL_LIGHT)
        
        self.init_ui()
        self.timer_baslat()

    def init_ui(self):
        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)
        self.ana_layout = QHBoxLayout(ana_widget)
        self.ana_layout.setContentsMargins(0, 0, 0, 0)
        self.ana_layout.setSpacing(0)

        self.sidebar = QFrame(); self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("background-color: #FFFFFF; border-right: 1px solid #E2E8F0;")
        self.s_layout = QVBoxLayout(self.sidebar); self.s_layout.setContentsMargins(0, 20, 0, 20)

        self.avatar_lbl = QLabel(); self.avatar_lbl.setFixedSize(80, 80); self.avatar_lbl.setAlignment(Qt.AlignCenter)
        self.avatar_lbl.setStyleSheet("background-color: #E2E8F0; border-radius: 40px;")
        if self.user.profil_foto:
            self.avatar_lbl.setPixmap(QPixmap(self.user.profil_foto).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            self.avatar_lbl.setText("👤"); self.avatar_lbl.setStyleSheet("background-color: #E2E8F0; border-radius: 40px; font-size: 40px;")
        
        l_app = QLabel(self.user.isim); l_app.setAlignment(Qt.AlignCenter); l_app.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E2A38; margin-top: 10px;")
        alt_bilgi = QLabel(self.user.rol); alt_bilgi.setAlignment(Qt.AlignCenter); alt_bilgi.setStyleSheet("font-size: 12px; color: #4A90E2; font-weight: bold;")
        self.s_layout.addWidget(self.avatar_lbl, alignment=Qt.AlignHCenter); self.s_layout.addWidget(l_app); self.s_layout.addWidget(alt_bilgi); self.s_layout.addSpacing(20)

        self.content_stack = QStackedWidget()
        self.kur_paneller()

        sag_frame = QWidget(); sag_layout = QVBoxLayout(sag_frame); sag_layout.setContentsMargins(0,0,0,0)
        self.navbar = QFrame(); self.navbar.setFixedHeight(70); self.navbar.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #E2E8F0;")
        n_layout = QHBoxLayout(self.navbar); n_layout.setContentsMargins(20, 0, 20, 0)

        n_baslik = QLabel(f"Hoş Geldin, {self.user.isim} ✨"); n_baslik.setObjectName("Title"); n_baslik.setStyleSheet("border: none;")
        n_layout.addWidget(n_baslik); n_layout.addStretch()

        self.btn_bildirim = QPushButton("🔔")
        self.btn_bildirim.setMinimumWidth(80)
        self.btn_bildirim.setFixedHeight(40)
        self.btn_bildirim.setCursor(Qt.PointingHandCursor)
        self.btn_bildirim.setStyleSheet("QPushButton { background: transparent; border: none; font-size: 20px; text-align: right; } QPushButton::menu-indicator { image: none; }")
        
        self.bildirim_menusu = QMenu(self)
        self.btn_bildirim.setMenu(self.bildirim_menusu)
        self.bildirimleri_guncelle()
        n_layout.addWidget(self.btn_bildirim)

        self.l_zaman = QLabel("Oturum: 0 dk"); self.l_zaman.setStyleSheet("color: #4A90E2; font-weight: bold; border: none; margin-left: 10px;")
        n_layout.addWidget(self.l_zaman)

        sag_layout.addWidget(self.navbar)
        sag_layout.addWidget(self.content_stack)
        
        self.ana_layout.addWidget(self.sidebar)
        self.ana_layout.addWidget(sag_frame)

    def bildirimleri_guncelle(self):
        self.bildirim_menusu.clear()
        bildirim_sayisi = 0
        
        # 1. Okunmamış Mesaj Kontrolü
        okunmamis = self.sistem.db.calistir("SELECT COUNT(*) FROM messages WHERE alici_id=? AND okundu=0", (self.user.id,), fetchone=True)[0]
        if okunmamis > 0:
            self.bildirim_menusu.addAction(f"📬 {okunmamis} yeni okunmamış mesajınız var!")
            bildirim_sayisi += okunmamis

        # 2. Güncel Duyurular Kontrolü (Son 3 Duyuru)
        duyurular = self.sistem.db.calistir("SELECT title FROM announcements ORDER BY date DESC LIMIT 3", fetchall=True)
        for d in duyurular:
            self.bildirim_menusu.addAction(f"📢 Duyuru: {d[0]}")
            bildirim_sayisi += 1

        if bildirim_sayisi == 0:
            self.bildirim_menusu.addAction("Bildirim yok.")
            self.btn_bildirim.setText("🔔")
            self.btn_bildirim.setStyleSheet("QPushButton { color: #4A5568; background: transparent; border:none; font-size:20px; text-align: right; } QPushButton::menu-indicator { image: none; }")
        else:
            self.btn_bildirim.setText(f"🔔 ({okunmamis})") if okunmamis > 0 else self.btn_bildirim.setText("🔔")
            self.btn_bildirim.setStyleSheet("QPushButton { color: #E53E3E; background: transparent; border:none; font-size:20px; font-weight:bold; text-align: right; } QPushButton::menu-indicator { image: none; }")
            
        self.bildirim_menusu.addSeparator()
        tmz = self.bildirim_menusu.addAction("Tümünü Okundu İşaretle")
        tmz.triggered.connect(self.bildirim_temizle)

    def bildirim_okundu_isaretle(self):
        # Sadece menü açıldığında görseli koru, temizleme işlemi için butona tıklanmalı.
        pass

    def bildirim_temizle(self):
        # Veritabanındaki tüm okunmamış mesajları okundu olarak işaretle
        self.sistem.db.calistir("UPDATE messages SET okundu=1 WHERE alici_id=?", (self.user.id,))
        self.bildirimleri_guncelle()

    def kur_paneller(self):
        for i in reversed(range(self.s_layout.count())):
            widget = self.s_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.objectName() == "SidebarBtn":
                widget.deleteLater()
        
        if self.user.rol == "Admin":
            self.ekle_sekme("🏠 Dashboard", AdminDashboard(self.sistem, self.user))
            self.ekle_sekme("⏳ Onay Bekleyen", AdminCourses(self.sistem)) 
            self.ekle_sekme("👥 Kullanıcılar", AdminUsers(self.sistem))
            self.ekle_sekme("💳 Ödemeler", AdminPaymentsPanel(self.sistem))
            self.ekle_sekme("🏆 Ayın Öğrencisi", AdminStudentOfMonthPanel(self.sistem, self.user)) 
            self.ekle_sekme("⚙️ Sistem Logları", AdminSystemLogsPanel(self.sistem, self.user))
            self.ekle_sekme("⚠️ Şikayet ve Talepler", AdminComplaintsAndAnnouncements(self.sistem, self.user))
            self.ekle_sekme("💬 Öğretmen Mesajları", AdminMessagePanel(self.sistem, self.user))
            self.ekle_sekme("👤 Profil", UserProfilePanel(self.sistem, self.user))
            
        elif self.user.rol == "Teacher":
            self.ekle_sekme("📊 Dashboard", TeacherDashboard(self.sistem, self.user))
            self.ekle_sekme("📚 Kurs Yönetimi", TeacherCourses(self.sistem, self.user))
            self.ekle_sekme("📝 Kurs & Konu", TeacherCourseManagementPanel(self.sistem, self.user))
            self.ekle_sekme("👥 Öğrenciler", TeacherStudentsPanel(self.sistem, self.user))
            self.ekle_sekme("📈 Öğrenci Durumu", TeacherStudentStatusPanel(self.sistem, self.user))
            self.ekle_sekme("📝 Sınav Notları", TeacherExamGradesPanel(self.sistem, self.user))
            self.ekle_sekme("📁 Ödev Yönetimi", TeacherAssignmentsPanel(self.sistem, self.user)) # EKLENDİ
            self.ekle_sekme("📢 Duyuru Gönder", TeacherAnnouncementsPanel(self.sistem, self.user))
            self.ekle_sekme("💬 İletişim", TeacherMessagePanel(self.sistem, self.user))
            self.ekle_sekme("⚙️ Profil", UserProfilePanel(self.sistem, self.user))
            
        else:
            self.ekle_sekme("🏠 Dashboard", StudentDashboard(self.sistem, self.user))
            self.ekle_sekme("📚 Kurslarım", MyCoursesPanel(self.sistem, self.user))
            self.ekle_sekme("🔍 Tüm Kurslar", StudentCourses(self.sistem, self.user))
            self.ekle_sekme("📅 Yoklama", StudentAttendancePanel(self.sistem, self.user))
            self.ekle_sekme("📊 Notlarım", StudentGradesPanel(self.sistem, self.user))
            self.ekle_sekme("📝 Ödevlerim", StudentAssignmentsPanel(self.sistem, self.user))
            self.ekle_sekme("🏆 Ödüller", StudentRewardPanel(self.sistem, self.user))
            self.ekle_sekme("💬 İletişim", StudentMessagePanel(self.sistem, self.user))
            self.ekle_sekme("⚠️ İstek ve Şikayet", StudentComplaintPanel(self.sistem, self.user))
            self.ekle_sekme("👤 Profil", UserProfilePanel(self.sistem, self.user))
            
        self.s_layout.addStretch()
        btn_cikis = QPushButton("🚪 Çıkış Yap")
        btn_cikis.setObjectName("SidebarBtn")
        btn_cikis.setStyleSheet("color: #E74C3C;")
        btn_cikis.clicked.connect(self.cikis_yap)
        self.s_layout.addWidget(btn_cikis)

    def ekle_sekme(self, isim, widget):
        idx = self.content_stack.addWidget(widget)
        btn = QPushButton(isim); btn.setObjectName("SidebarBtn")
        btn.clicked.connect(lambda ch, i=idx: self.content_stack.setCurrentIndex(i))
        self.s_layout.addWidget(btn)

    def timer_baslat(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.zaman_guncelle)
        self.timer.start(60000)

    def zaman_guncelle(self):
        fark = datetime.now() - self.oturum_baslangic
        dk = fark.total_seconds() // 60
        self.l_zaman.setText(f"Oturum: {int(dk)} dk")
        self.sistem.oturum_suresi_ekle(self.user.id, 1)
        self.bildirimleri_guncelle() # BU SATIRI EKLEYİN

    def tema_degistir(self):
        pass

    def cikis_yap(self):
        fark = datetime.now() - self.oturum_baslangic
        self.sistem.oturum_suresi_ekle(self.user.id, int(fark.total_seconds() // 60))
        self.close()
        self.auth = AuthWindow()
        self.auth.show()

    def arama_yap(self):
        kelime = self.nav_arama.text().strip()
        if kelime:
            QMessageBox.information(self, "Arama Sonuçları", f"Sistemde '{kelime}' ile ilgili sonuç bulunamadı.")
            self.nav_arama.clear()

    def bildirimleri_ac(self):
        pass


# --- PANELLER ---
class AdminDashboard(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(25)
        layout.addWidget(QLabel("📊 Yönetim Özeti", objectName="Title"))

        # Üst İstatistikler (4'lü Grid)
        o_sayi, e_sayi, k_sayi, t_sure = self.sistem.istatistikleri_getir()
        
        h_metrikler = QHBoxLayout(); h_metrikler.setSpacing(20)
        h_metrikler.addWidget(self.kart_yap("👥 Toplam Öğrenci", str(o_sayi), "#3182CE"))
        h_metrikler.addWidget(self.kart_yap("🎓 Toplam Eğitmen", str(e_sayi), "#805AD5"))
        h_metrikler.addWidget(self.kart_yap("📚 Aktif Kurslar", str(k_sayi), "#38A169"))
        h_metrikler.addWidget(self.kart_yap("⏱️ Sistem Kullanımı (Dk)", str(t_sure), "#DD6B20"))
        layout.addLayout(h_metrikler)

        # Alt İki Panel: Grafik ve Hızlı İşlemler
        h_alt = QHBoxLayout(); h_alt.setSpacing(20)
        
        k_plan = QFrame(); k_plan.setObjectName("Card"); drop_shadow(k_plan); l_plan = QVBoxLayout(k_plan)
        h_plan_ust = QHBoxLayout()
        h_plan_ust.addWidget(QLabel("📅 Kişisel Planlayıcı", styleSheet="font-size: 16px; font-weight: bold; color: #2D3748;"))
        l_plan.addLayout(h_plan_ust)
        
        self.takvim = QCalendarWidget(); self.takvim.setFixedHeight(220)
        self.takvim.setStyleSheet("QCalendarWidget QWidget { alternate-background-color: #F7FAFC; } QCalendarWidget QAbstractItemView:enabled { font-size: 13px; color: #4A5568; selection-background-color: #3182CE; selection-color: white; }")
        l_plan.addWidget(self.takvim)
        
        h_gorev = QHBoxLayout()
        self.gorev_input = QLineEdit(); self.gorev_input.setPlaceholderText("Görev ekle...")
        self.gorev_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #CBD5E0;")
        btn_ekle = SafeButton("Ekle"); btn_ekle.setStyleSheet("background-color: #3182CE; color: white; border-radius: 6px; padding: 8px 15px; font-weight: bold;")
        btn_sil = SafeButton("Sil"); btn_sil.setStyleSheet("background-color: #E53E3E; color: white; border-radius: 6px; padding: 8px 15px; font-weight: bold;")
        btn_ekle.clicked.connect(self.ajanda_gonder); btn_sil.clicked.connect(self.ajanda_sil_ui)
        h_gorev.addWidget(self.gorev_input); h_gorev.addWidget(btn_ekle); h_gorev.addWidget(btn_sil)
        l_plan.addLayout(h_gorev)
        
        self.gorev_listesi = QListWidget(); self.gorev_listesi.setStyleSheet("border: 1px solid #E2E8F0; background: #FFFFFF; border-radius: 6px; padding: 5px; outline: none;")
        self.gorev_listesi.itemDoubleClicked.connect(self.ajanda_ciz)
        l_plan.addWidget(self.gorev_listesi); h_alt.addWidget(k_plan, 6)

        k_hizli = QFrame(); k_hizli.setObjectName("Card"); drop_shadow(k_hizli); l_hizli = QVBoxLayout(k_hizli)
        l_hizli.setContentsMargins(25, 25, 25, 25)
        l_hizli.addWidget(QLabel("📢 Güncel Duyurular", styleSheet="font-size: 16px; font-weight:bold; color: #2D3748;"))
        
        duyurular = self.sistem.db.calistir("SELECT title, date FROM announcements ORDER BY date DESC LIMIT 4", fetchall=True)
        if duyurular:
            for d in duyurular:
                d_baslik = d[0] if len(d[0]) < 40 else d[0][:37] + "..."
                tarih = d[1][:10]
                l_hizli.addWidget(QLabel(f"• <b>{tarih}</b>: {d_baslik}", styleSheet="font-size: 14px; color: #4A5568; margin-top: 5px;"))
        else:
            l_hizli.addWidget(QLabel("Henüz bir duyuru bulunmuyor.", styleSheet="font-size: 14px; color: #A0AEC0; font-style: italic; margin-top: 10px;"))
            
        l_hizli.addStretch()
        h_alt.addWidget(k_hizli, 4)

        layout.addLayout(h_alt)
        self.ajanda_yukle()
        layout.addStretch()

    def kart_yap(self, baslik, deger, renk):
        k = QFrame(); k.setObjectName("Card"); drop_shadow(k); l = QVBoxLayout(k)
        l.setContentsMargins(20, 25, 20, 25)
        l.addWidget(QLabel(baslik, styleSheet="font-size: 15px; color: #718096; font-weight: 600;"), alignment=Qt.AlignCenter)
        l.addWidget(QLabel(deger, styleSheet=f"font-size: 32px; color: {renk}; font-weight: bold;"), alignment=Qt.AlignCenter)
        return k

    def ajanda_yukle(self):
        self.gorev_listesi.clear()
        for g in self.sistem.ajanda_getir(self.user.id):
            item = QListWidgetItem(f"{g[1][-2:]}.{g[1][5:7]}.{g[1][:4]} - {g[2]}")
            item.setData(Qt.UserRole, g[0]); item.setData(Qt.UserRole + 1, g[3])
            font = QFont(FONTLAR, 11)
            if g[3] == 1: font.setStrikeOut(True); item.setForeground(QColor("#A0AEC0"))
            else: item.setForeground(QColor("#2D3748"))
            item.setFont(font); self.gorev_listesi.addItem(item)
            
    def ajanda_gonder(self):
        metin = self.gorev_input.text().strip()
        if metin:
            self.sistem.ajanda_ekle(self.user.id, self.takvim.selectedDate().toString("yyyy-MM-dd"), metin)
            self.gorev_input.clear(); self.ajanda_yukle()
            
    def ajanda_ciz(self, item):
        self.sistem.ajanda_durum_degistir(item.data(Qt.UserRole), 1 if item.data(Qt.UserRole + 1) == 0 else 0)
        self.ajanda_yukle()
        
    def ajanda_sil_ui(self):
        secili = self.gorev_listesi.currentItem()
        if secili and QMessageBox.question(self, "Onay", "Silinsin mi?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.sistem.ajanda_sil(secili.data(Qt.UserRole)); self.ajanda_yukle()

class AdminCourses(QWidget):
    def __init__(self, sistem):
        super().__init__()
        self.sistem = sistem
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Tüm Kurs Yönetimi", objectName="Title"))
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels(["ID", "Kurs Adı", "Eğitmen", "Kategori", "Durum", "Onay İşlemi", "Sil"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # TABLO KORUMASI (Yazı Yazılamaz)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setFocusPolicy(Qt.NoFocus)
        self.tablo.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablo.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none;}")
        
        layout.addWidget(self.tablo)
        self.yukle()
        
    def yukle(self):
        self.tablo.setRowCount(0)
        kurslar = self.sistem.admin_tum_kurslar()
        self.tablo.setRowCount(len(kurslar))
        for r, row in enumerate(kurslar):
            for c in range(4): 
                item = QTableWidgetItem(str(row[c]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tablo.setItem(r, c, item)
            drm = "Onaylı" if row[4] == 1 else "Bekliyor"
            drm_item = QTableWidgetItem(drm)
            drm_item.setTextAlignment(Qt.AlignCenter)
            self.tablo.setItem(r, 4, drm_item)
            
            btn_onay = SafeButton("Onayla")
            btn_onay.setObjectName("BtnSuccess")
            if row[4] == 1:
                btn_onay.setDisabled(True)
            else:
                btn_onay.clicked.connect(lambda ch, kid=row[0]: self.onayla(kid))
            self.tablo.setCellWidget(r, 5, btn_onay)
            
            btn = SafeButton("Kursu Sil")
            btn.setObjectName("BtnError")
            btn.clicked.connect(lambda ch, kid=row[0]: self.sil(kid))
            self.tablo.setCellWidget(r, 6, btn)
            
    def onayla(self, kid):
        try:
            self.sistem.kurs_onayla(kid)
            QMessageBox.information(self, "Başarılı", "Kurs başarıyla onaylandı ve yayına alındı.")
            self.yukle()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))
            
    def sil(self, kid):
        cevap = QMessageBox.question(self, "Onay", "Bu kursu silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.sistem.kurs_sil(kid)
            self.yukle()

class AdminUsers(QWidget):
    def __init__(self, sistem):
        super().__init__()
        self.sistem = sistem
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Sistem Kullanıcıları", objectName="Title"))
        
        self.tabs = QTabWidget()
        self.tab_ogrenci = QTableWidget()
        self.tab_egitmen = QTableWidget()
        
        for t in [self.tab_ogrenci, self.tab_egitmen]:
            t.setColumnCount(7)
            t.setHorizontalHeaderLabels(["ID", "İsim", "E-posta", "Rol", "Durum", "Durum Değiştir", "Sil"])
            t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            # TABLO KORUMASI
            t.setEditTriggers(QAbstractItemView.NoEditTriggers)
            t.setFocusPolicy(Qt.NoFocus)
            t.setSelectionMode(QAbstractItemView.NoSelection)
            t.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none;}")
            
        self.tabs.addTab(self.tab_ogrenci, "Öğrenciler")
        self.tabs.addTab(self.tab_egitmen, "Eğitmenler")
        layout.addWidget(self.tabs)
        self.yukle()

    def yukle(self):
        kullanicilar = self.sistem.tum_kullanicilari_getir()
        ogrenciler = [k for k in kullanicilar if k[3] == "Student"]
        egitmenler = [k for k in kullanicilar if k[3] == "Teacher"]
        self._doldur(self.tab_ogrenci, ogrenciler)
        self._doldur(self.tab_egitmen, egitmenler)

    def _doldur(self, tablo, liste):
        tablo.setRowCount(len(liste))
        for r, row in enumerate(liste):
            for c in range(4):
                item = QTableWidgetItem(str(row[c]))
                item.setTextAlignment(Qt.AlignCenter)
                tablo.setItem(r, c, item)
            durum_text = "Aktif" if row[4] == 1 else "Pasif"
            durum_item = QTableWidgetItem(durum_text)
            durum_item.setTextAlignment(Qt.AlignCenter)
            tablo.setItem(r, 4, durum_item)
            
            btn = SafeButton("Durum Değiştir")
            btn.setObjectName("BtnWarning")
            yeni_durum = 0 if row[4] == 1 else 1
            btn.clicked.connect(lambda ch, uid=row[0], d=yeni_durum: self.degistir(uid, d))
            tablo.setCellWidget(r, 5, btn)
            
            btn_sil = SafeButton("Sistemden Sil")
            btn_sil.setObjectName("BtnError")
            btn_sil.clicked.connect(lambda ch, uid=row[0]: self.sil(uid))
            tablo.setCellWidget(r, 6, btn_sil)

    def degistir(self, uid, d):
        try:
            self.sistem.kullanici_durum_degistir(uid, d)
            self.yukle()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def sil(self, uid):
        cevap = QMessageBox.question(self, "Onay", "Bu kullanıcıyı silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.sistem.kullanici_sil(uid)
            self.yukle()

class KursOlusturmaSihirbazi(QWizard):
    def __init__(self, sistem, user, ebeveyn):
        super().__init__(ebeveyn)
        self.sistem = sistem; self.user = user; self.ebeveyn = ebeveyn
        self.setWindowTitle("Yeni Kurs Oluşturma Sihirbazı")
        self.setFixedSize(700, 600) # Ekranı genişlettik ki ezilmesin
        self.setStyleSheet(ebeveyn.window().styleSheet() if ebeveyn else "")
        self.setWizardStyle(QWizard.ModernStyle)
        
        input_style = "padding: 8px; border: 1px solid #CBD5E0; border-radius: 5px; min-height: 25px; background: white;"
        
        # --- ADIM 1: TEMEL BİLGİLER ---
        self.sayfa1 = QWizardPage()
        self.sayfa1.setTitle("Adım 1: Temel Bilgiler")
        self.sayfa1.setSubTitle("Kursunuzun ana hatlarını belirleyin.")
        l1 = QVBoxLayout(self.sayfa1)
        l1.setSpacing(15)
        
        self.ad = QLineEdit(); self.ad.setPlaceholderText("Örn: Sıfırdan İleri Seviye Python")
        self.ad.setStyleSheet(input_style)
        self.sayfa1.registerField("ad*", self.ad) 
        
        self.kurs_id = QLineEdit()
        self.kurs_id.setPlaceholderText("Örn: PYT101 (Boş bırakırsanız sistem 5 haneli atar)")
        self.kurs_id.setStyleSheet(input_style)
        
        self.kat = QComboBox()
        self.kat.setEditable(True) 
        self.kat.setStyleSheet(input_style)
        self.kat.addItems([
            "Algoritma ve Programlama Temelleri", "Backend (Arka Yüz) Geliştirme", 
            "Veritabanı Yönetimi ve İleri Seviye Mimari", "Frontend (Ön Yüz) Geliştirme", 
            "Masaüstü ve Web Uygulamaları Geliştirme", "UI/UX ve Tasarım", 
            "Siber Güvenlik", "Mobil Uygulama Geliştirme"
        ])
        
        self.zorluk = QComboBox(); self.zorluk.addItems(["Başlangıç", "Orta", "İleri Düzey"])
        self.zorluk.setStyleSheet(input_style)
        self.aciklama = QTextEdit(); self.aciklama.setPlaceholderText("Öğrenciler bu kursta neler öğrenecek?")
        self.aciklama.setStyleSheet("padding: 8px; border: 1px solid #CBD5E0; border-radius: 5px; background: white;")
        self.aciklama.setMinimumHeight(100) 
        
        l1.addWidget(QLabel("Özel Kurs ID (Opsiyonel):")); l1.addWidget(self.kurs_id)
        l1.addWidget(QLabel("Kurs Başlığı:")); l1.addWidget(self.ad)
        l1.addWidget(QLabel("Kategori:")); l1.addWidget(self.kat)
        l1.addWidget(QLabel("Zorluk Seviyesi:")); l1.addWidget(self.zorluk)
        l1.addWidget(QLabel("Açıklama:")); l1.addWidget(self.aciklama)
        self.addPage(self.sayfa1)
        
        # --- ADIM 2: FİYAT VE MEDYA ---
        self.sayfa2 = QWizardPage()
        self.sayfa2.setTitle("Adım 2: Fiyatlandırma ve Medya")
        l2 = QVBoxLayout(self.sayfa2)
        l2.setSpacing(15)
        
        self.kapasite = QSpinBox(); self.kapasite.setRange(1, 1000); self.kapasite.setPrefix("Kontenjan: ")
        self.kapasite.setStyleSheet(input_style)
        
        self.fiyat = QSpinBox() # Tam sayı
        self.fiyat.setRange(0, 100000)
        self.fiyat.setPrefix("Fiyat (TL): ")
        self.fiyat.setSuffix(" ₺")
        self.fiyat.setStyleSheet(input_style)
        
        self.lbl_kapak_yolu = QLabel("Henüz bir görsel seçilmedi.")
        self.lbl_kapak_yolu.setStyleSheet("color: #718096; font-style: italic;")
        self.kapak_yolu = ""
        
        h_kapak_btn = QHBoxLayout()
        self.btn_kapak = QPushButton("🖼️ Kapak Görseli Seç")
        self.btn_kapak.setStyleSheet("background-color: #3182CE; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.btn_kapak.clicked.connect(self.kapak_sec)
        
        self.btn_kapak_sil = QPushButton("🗑️ Seçimi Temizle")
        self.btn_kapak_sil.setStyleSheet("background-color: #E53E3E; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        self.btn_kapak_sil.clicked.connect(self.kapak_sil)
        self.btn_kapak_sil.hide() 
        
        h_kapak_btn.addWidget(self.btn_kapak)
        h_kapak_btn.addWidget(self.btn_kapak_sil)
        
        l2.addWidget(QLabel("Maksimum Öğrenci:")); l2.addWidget(self.kapasite)
        l2.addWidget(QLabel("Kurs Ücreti:")); l2.addWidget(self.fiyat)
        l2.addSpacing(10)
        l2.addWidget(QLabel("Kapak Görseli:")); l2.addWidget(self.lbl_kapak_yolu)
        l2.addLayout(h_kapak_btn)
        l2.addStretch()
        self.addPage(self.sayfa2)
        
        # --- ADIM 3: ZAMANLAMA VE GÜNLER (HER GÜNE AYRI SAAT) ---
        self.sayfa3 = QWizardPage()
        self.sayfa3.setTitle("Adım 3: Zamanlama ve Eğitim Süreci")
        l3 = QVBoxLayout(self.sayfa3)
        l3.setSpacing(15)
        
        self.bas = QDateEdit(); self.bas.setDate(QDate.currentDate()); self.bas.setCalendarPopup(True)
        self.bas.setMinimumDate(QDate.currentDate()) # Geçmiş tarih seçimi yasaklandı
        self.bas.setStyleSheet(input_style)
        self.kurs_suresi = QSpinBox(); self.kurs_suresi.setRange(1, 365); self.kurs_suresi.setSuffix(" Gün"); self.kurs_suresi.setValue(30)
        self.kurs_suresi.setStyleSheet(input_style)
        
        l3.addWidget(QLabel("Başlangıç Tarihi:")); l3.addWidget(self.bas)
        l3.addWidget(QLabel("Kursun Toplam Süresi (Gün):")); l3.addWidget(self.kurs_suresi)
        l3.addSpacing(10)
        l3.addWidget(QLabel("Haftalık Ders Programı (Günü Seçin ve Saatini Ayarlayın):"))
        
        # Günler ve Saatler için özel liste
        w_gunler = QWidget()
        l_gunler = QVBoxLayout(w_gunler)
        l_gunler.setContentsMargins(0,0,0,0)
        
        self.gun_verileri = {}
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        
        for gun in gunler:
            h_gun = QHBoxLayout()
            chk = QCheckBox(gun)
            chk.setFixedWidth(100)
            
            t_bas = QTimeEdit(); t_bas.setDisplayFormat("HH:mm"); t_bas.setEnabled(False); t_bas.setStyleSheet(input_style)
            t_bit = QTimeEdit(); t_bit.setDisplayFormat("HH:mm"); t_bit.setEnabled(False); t_bit.setStyleSheet(input_style)
            
            # Checkbox seçildiğinde yanındaki saat kutularını aktifleştir
            chk.toggled.connect(lambda checked, tb=t_bas, tc=t_bit: (tb.setEnabled(checked), tc.setEnabled(checked)))
            
            h_gun.addWidget(chk)
            h_gun.addWidget(QLabel(" Başla:"))
            h_gun.addWidget(t_bas)
            h_gun.addWidget(QLabel(" Bitir:"))
            h_gun.addWidget(t_bit)
            
            self.gun_verileri[gun] = (chk, t_bas, t_bit)
            l_gunler.addLayout(h_gun)
            
        scroll_gunler = QScrollArea()
        scroll_gunler.setWidgetResizable(True)
        scroll_gunler.setWidget(w_gunler)
        scroll_gunler.setStyleSheet("border: 1px solid #CBD5E0; border-radius: 5px; background: white;")
        
        l3.addWidget(scroll_gunler)
        self.addPage(self.sayfa3)

    def kapak_sec(self):
        dosya, _ = QFileDialog.getOpenFileName(self, "Kapak Görseli Seç", "", "Resim (*.png *.jpg *.jpeg)")
        if dosya:
            self.kapak_yolu = dosya
            self.lbl_kapak_yolu.setText(f"Seçildi: {dosya.split('/')[-1]}")
            self.lbl_kapak_yolu.setStyleSheet("color: #38A169; font-weight: bold;")
            self.btn_kapak_sil.show()

    def kapak_sil(self):
        self.kapak_yolu = ""
        self.lbl_kapak_yolu.setText("Henüz bir görsel seçilmedi.")
        self.lbl_kapak_yolu.setStyleSheet("color: #718096; font-style: italic;")
        self.btn_kapak_sil.hide()

    def accept(self):
        try:
            import random
            k_id = self.kurs_id.text().strip()
            if not k_id: k_id = str(random.randint(10000, 99999))
            
            baslangic = self.bas.date()
            bitis = baslangic.addDays(self.kurs_suresi.value())
            
            # Kursu Kaydet
            sorgu = """INSERT INTO courses (id, kurs_adi, egitmen_id, kategori, aciklama, baslangic_tarihi, bitis_tarihi, kapasite, onay_durumu, fiyat, zorluk, kapak_resmi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)"""
            self.sistem.db.calistir(sorgu, (k_id, self.ad.text(), self.user.id, self.kat.currentText(), self.aciklama.toPlainText(), baslangic.toString("yyyy-MM-dd"), bitis.toString("yyyy-MM-dd"), self.kapasite.value(), self.fiyat.value(), self.zorluk.currentText(), self.kapak_yolu))
            
            # Seçili Günlerin Saatlerini Kaydet
            hic_secildi_mi = False
            for gun, veriler in self.gun_verileri.items():
                chk, t_bas, t_bit = veriler
                if chk.isChecked():
                    hic_secildi_mi = True
                    self.sistem.program_ekle(k_id, gun, t_bas.text(), t_bit.text())
            
            if not hic_secildi_mi:
                self.sistem.program_ekle(k_id, "Belirtilmedi", "00:00", "00:00")
                
            QMessageBox.information(self, "Başarılı", "Kurs taslağınız yönetici onayına gönderildi.")
            if hasattr(self.ebeveyn, 'yukle'):
                self.ebeveyn.yukle()
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))
            
class KursDuzenleDialog(QDialog):
    def __init__(self, sistem, kurs_id, parent=None):
        super().__init__(parent)
        self.sistem = sistem; self.kurs_id = kurs_id
        self.setWindowTitle("Kurs Düzenle")
        self.setFixedSize(500, 600)
        self.setStyleSheet(parent.window().styleSheet() if parent else "")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Kurs Bilgilerini Düzenle", objectName="Title"))
        
        kurs = self.sistem.kurs_detay_getir(kurs_id)
        if not kurs:
            QMessageBox.warning(self, "Hata", "Kurs bulunamadı.")
            self.reject()
            return
            
        self.ad = QLineEdit(kurs[1])
        self.kat = QComboBox(); self.kat.setEditable(True)
        self.kat.addItems(["Algoritma ve Programlama Temelleri", "Backend (Arka Yüz) Geliştirme", "Veritabanı Yönetimi ve İleri Seviye Mimari", "Frontend (Ön Yüz) Geliştirme", "Masaüstü ve Web Uygulamaları Geliştirme", "UI/UX ve Premium Kurumsal Kimlik Tasarımı", "Versiyon Kontrol Sistemleri", "Mobil Uygulama Geliştirme", "DevOps ve Canlıya Alma (Deployment)", "Kariyer ve Freelance Platform Stratejileri"])
        self.kat.setCurrentText(kurs[3])
        
        self.aciklama = QTextEdit(kurs[4] if kurs[4] else "")
        self.kapasite = QSpinBox(); self.kapasite.setRange(1, 1000); self.kapasite.setValue(kurs[7] or 1)
        self.fiyat = QSpinBox(); self.fiyat.setRange(0, 100000); self.fiyat.setSuffix(" ₺"); self.fiyat.setValue(int(kurs[10] or 0))
        self.zorluk = QComboBox(); self.zorluk.addItems(["Başlangıç", "Orta", "İleri Düzey"]); self.zorluk.setCurrentText(kurs[11] or "Başlangıç")
        
        layout.addWidget(QLabel("Kurs Adı:")); layout.addWidget(self.ad)
        layout.addWidget(QLabel("Kategori:")); layout.addWidget(self.kat)
        layout.addWidget(QLabel("Açıklama:")); layout.addWidget(self.aciklama)
        h = QHBoxLayout()
        h.addWidget(QLabel("Kapasite:")); h.addWidget(self.kapasite)
        h.addWidget(QLabel("Fiyat:")); h.addWidget(self.fiyat)
        layout.addLayout(h)
        layout.addWidget(QLabel("Zorluk:")); layout.addWidget(self.zorluk)
        
        btn = SafeButton("Kaydet ve Onaya Gönder"); btn.setObjectName("BtnSuccess")
        btn.clicked.connect(self.kaydet)
        layout.addWidget(btn)
        
    def kaydet(self):
        try:
            self.sistem.kurs_guncelle(self.kurs_id, self.ad.text(), self.kat.currentText(), self.aciklama.toPlainText(), self.kapasite.value(), self.fiyat.value(), self.zorluk.currentText())
            QMessageBox.information(self, "Başarılı", "Kurs güncellendi ve tekrar yönetici onayına gönderildi.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

class TeacherCourses(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem
        self.user = user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        hl = QHBoxLayout()
        hl.addWidget(QLabel("📚 Kurslarım (Yönetim)", objectName="Title"))
        btn_ekle = SafeButton("➕ Yeni Kurs Oluştur")
        btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.setStyleSheet("background-color: #3182CE; color: white; padding: 10px 15px; border-radius: 6px; font-weight: bold;")
        btn_ekle.clicked.connect(self.sihirbazi_ac)
        hl.addStretch(); hl.addWidget(btn_ekle)
        layout.addLayout(hl)
        
        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(8)
        self.tablo.setHorizontalHeaderLabels(["ID", "Kurs Adı", "Kategori", "Zorluk", "Fiyat", "Kontenjan", "Durum", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.verticalHeader().setVisible(False); self.tablo.setShowGrid(False); self.tablo.setAlternatingRowColors(True)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers); self.tablo.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablo.setStyleSheet("QTableWidget { border: none; background-color: white; } QHeaderView::section { background-color: #F7FAFC; color: #4A5568; font-weight: bold; border: none; padding: 12px; border-bottom: 2px solid #E2E8F0; }")
        
        f_layout.addWidget(self.tablo)
        layout.addWidget(frame)
        self.yukle()

    def yukle(self):
        self.tablo.setRowCount(0)
        try:
            kurslar = self.sistem.egitmen_kurslari_getir(self.user.id)
            self.tablo.setRowCount(len(kurslar))
            for r, row in enumerate(kurslar):
                self.tablo.setItem(r, 0, QTableWidgetItem(str(row[0])))
                self.tablo.setItem(r, 1, QTableWidgetItem(str(row[1])))
                self.tablo.setItem(r, 2, QTableWidgetItem(str(row[2])))
                self.tablo.setItem(r, 3, QTableWidgetItem(str(row[5])))
                self.tablo.setItem(r, 4, QTableWidgetItem(f"{row[6]} ₺"))
                self.tablo.setItem(r, 5, QTableWidgetItem(str(row[4])))
                
                if row[3] == 2:
                    drm = "Tamamlandı"
                elif row[3] == 1:
                    drm = "Onaylı"
                else:
                    drm = "Bekliyor"
                item_drm = QTableWidgetItem(drm)
                
                if row[3] == 2: item_drm.setForeground(QColor("#8E44AD"))
                elif row[3] == 1: item_drm.setForeground(QColor("#38A169"))
                else: item_drm.setForeground(QColor("#DD6B20"))
                self.tablo.setItem(r, 6, item_drm)
                
                b_widget = QWidget(); b_layout = QHBoxLayout(b_widget); b_layout.setContentsMargins(0,0,0,0)
                btn_duzenle = SafeButton("Düzenle")
                btn_duzenle.setStyleSheet("background-color: #F39C12; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
                btn_duzenle.clicked.connect(lambda ch, kid=row[0]: self.duzenle_modal(kid))
                b_layout.addWidget(btn_duzenle)
                
                if row[3] == 1: # Sadece onaylı aktif kurslara işlem yapılabilir
                    btn_ilerleme = SafeButton("% İlerleme")
                    btn_ilerleme.setStyleSheet("background-color: #3498DB; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
                    btn_ilerleme.clicked.connect(lambda ch, kid=row[0]: self.ilerleme_guncelle_modal(kid))
                    b_layout.addWidget(btn_ilerleme)

                    btn_bitir = SafeButton("Bitir")
                    btn_bitir.setStyleSheet("background-color: #27AE60; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
                    btn_bitir.clicked.connect(lambda ch, kid=row[0]: self.kursu_bitir(kid))
                    b_layout.addWidget(btn_bitir)
                self.tablo.setCellWidget(r, 7, b_widget)
        except Exception as e:
            print("Kurslar yüklenirken hata:", e)
            
    def duzenle_modal(self, kid):
        dialog = KursDuzenleDialog(self.sistem, kid, self)
        if dialog.exec_(): self.yukle()

    def ilerleme_guncelle_modal(self, kid):
        yuzde, ok = QInputDialog.getInt(self, "İlerleme Güncelle", "Öğrencilerin ilerleme yüzdesini girin (0-100):", 0, 0, 100, 5)
        if ok:
            self.sistem.db.calistir("UPDATE enrollments SET ilerleme = ? WHERE kurs_id = ?", (yuzde, kid))
            QMessageBox.information(self, "Başarılı", f"Kurs ilerlemesi %{yuzde} olarak güncellendi.")

    def kursu_bitir(self, kid):
        cevap = QMessageBox.question(self, "Onay", "Bu kursu bitirmek istediğinize emin misiniz?\nÖğrenciler için 'Tamamlananlar' sekmesine düşecektir.", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.sistem.db.calistir("UPDATE enrollments SET ilerleme = 100 WHERE kurs_id = ?", (kid,))
            self.sistem.db.calistir("UPDATE courses SET onay_durumu = 2 WHERE id = ?", (kid,))
            QMessageBox.information(self, "Başarılı", "Kurs tamamlandı! Öğrencilerin ilerlemeleri %100 yapıldı.")
            self.yukle()

    def sihirbazi_ac(self):
        self.wizard = KursOlusturmaSihirbazi(self.sistem, self.user, self)
        self.wizard.show()

class StudentDetailDialog(QDialog):
    def __init__(self, sistem, ogrenci_id, ogrenci_isim, kurs_id, ebeveyn=None):
        super().__init__(ebeveyn)
        self.sistem = sistem
        self.setWindowTitle(f"Öğrenci Profili: {ogrenci_isim}")
        self.setFixedSize(600, 450)
        self.setStyleSheet(ebeveyn.window().styleSheet() if ebeveyn else STIL_LIGHT)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"🎓 {ogrenci_isim} - Başarı ve Not Profili", objectName="Title"))
        
        # Sekme Yapısı ile Düzenli Görünüm
        tabs = QTabWidget()
        
        # 1. Sekme: Ödev Geçmişi
        tab_notlar = QTableWidget()
        tab_notlar.setColumnCount(4)
        tab_notlar.setHorizontalHeaderLabels(["Ödev Başlığı", "Puan", "Geribildirim", "Teslim Tarihi"])
        tab_notlar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        notlar = self.sistem.ogrenci_notlari_getir(ogrenci_id, kurs_id)
        tab_notlar.setRowCount(len(notlar))
        for r, row in enumerate(notlar):
            tab_notlar.setItem(r, 0, QTableWidgetItem(str(row[0])))
            tab_notlar.setItem(r, 1, QTableWidgetItem(str(row[1]) if row[1] is not None else "Bekliyor"))
            tab_notlar.setItem(r, 2, QTableWidgetItem(str(row[2]) or "Yok"))
            tab_notlar.setItem(r, 3, QTableWidgetItem(str(row[3])[:10]))
            
        tabs.addTab(tab_notlar, "📝 Ödev Geçmişi")
        
        layout.addWidget(tabs)
        
        btn_kapat = SafeButton("Kapat")
        btn_kapat.clicked.connect(self.accept)
        layout.addWidget(btn_kapat)

        
class MyCoursesPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("📚 Benim Kurslarım", objectName="Title"))
        
        self.tabs = QTabWidget()
        self.scroll_aktif = QScrollArea(); self.scroll_aktif.setWidgetResizable(True); self.scroll_aktif.setStyleSheet("border: none; background: transparent;")
        self.w_aktif = QWidget(); self.grid_aktif = QGridLayout(self.w_aktif); self.grid_aktif.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_aktif.setWidget(self.w_aktif)
        self.tabs.addTab(self.scroll_aktif, "⏳ Devam Edenler")
        
        self.scroll_tamam = QScrollArea(); self.scroll_tamam.setWidgetResizable(True); self.scroll_tamam.setStyleSheet("border: none; background: transparent;")
        self.w_tamam = QWidget(); self.grid_tamam = QGridLayout(self.w_tamam); self.grid_tamam.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_tamam.setWidget(self.w_tamam)
        self.tabs.addTab(self.scroll_tamam, "✅ Tamamlananlar")
        
        layout.addWidget(self.tabs); self.yukle()

    def showEvent(self, event):
        self.yukle()
        super().showEvent(event)
        
    def yukle(self):
        for i in reversed(range(self.grid_aktif.count())): 
            if self.grid_aktif.itemAt(i).widget(): self.grid_aktif.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.grid_tamam.count())): 
            if self.grid_tamam.itemAt(i).widget(): self.grid_tamam.itemAt(i).widget().setParent(None)

        kurslar = self.sistem.ogrenci_kurslari_getir(self.user.id)
        s_aktif = 0; s_tamam = 0
        import os
        for k in kurslar:
            kart = QFrame(); kart.setObjectName("Card"); drop_shadow(kart); kart.setFixedSize(320, 280)
            kl = QVBoxLayout(kart); kl.setContentsMargins(20, 20, 20, 20)
            
            img = QLabel(); img.setFixedHeight(120); img.setAlignment(Qt.AlignCenter)
            k_detay = self.sistem.kurs_detay_getir(k[0])
            kapak_yolu = k_detay[12] if k_detay and len(k_detay) > 12 else ""
            if kapak_yolu and os.path.exists(kapak_yolu):
                img.setPixmap(QPixmap(kapak_yolu).scaled(300, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                img.setStyleSheet("border-radius: 8px;")
            else:
                img.setStyleSheet("background-color: #EDF2F7; border-radius: 8px;"); img.setText("Resim Yok")
            
            lbl_baslik = QLabel(f"<b>{k[1]}</b><br><span style='font-size:13px; color:#718096;'>Eğitmen: {k[2]}</span>") 
            lbl_baslik.setWordWrap(True); lbl_baslik.setAlignment(Qt.AlignCenter)
            
            pbar = QProgressBar(); pbar.setFixedHeight(16); pbar.setValue(k[3])
            pbar.setFormat(f"%{k[3]} Tamamlandı"); pbar.setAlignment(Qt.AlignCenter)
            pbar.setStyleSheet("QProgressBar { border: 1px solid #CBD5E0; border-radius: 8px; background: #EDF2F7; color: #2D3748; font-weight: bold; font-size: 11px; } QProgressBar::chunk { background: #38A169; border-radius: 8px; }")
            
            btn = SafeButton("Derse Git"); btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("background-color: #3182CE; color: white; border-radius: 6px; padding: 10px; font-weight: bold;")
            btn.clicked.connect(lambda ch, kid=k[0], kadi=k[1]: StudentCourseContentDialog(self.sistem, kid, kadi, self).exec_())
            
            kl.addWidget(img); kl.addWidget(lbl_baslik); kl.addWidget(pbar); kl.addStretch(); kl.addWidget(btn)
            
            if k[3] >= 100:
                self.grid_tamam.addWidget(kart, s_tamam // 3, s_tamam % 3); s_tamam += 1
            else:
                self.grid_aktif.addWidget(kart, s_aktif // 3, s_aktif % 3); s_aktif += 1



class ScheduleExport(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem
        self.user = user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        
        kart = QFrame(); kart.setObjectName("Card"); drop_shadow(kart)
        kl = QVBoxLayout(kart)
        
        kl.addWidget(QLabel("Ders Programı ve PDF Çıktısı", objectName="Title"))
        
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Gün", "Başlangıç", "Bitiş", "Kurs"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        kl.addWidget(self.tablo)
        self.yukle()
        
        btn = SafeButton("PDF Olarak Kaydet")
        btn.setObjectName("BtnSuccess")
        btn.clicked.connect(self.pdf_cikar)
        kl.addWidget(btn)
        
        layout.addWidget(kart)
        layout.addStretch()
    def yukle(self):
        # Öğrenci veya öğretmenin rolüne göre programı veritabanından çeker
        program = self.sistem.program_getir(self.user.id, self.user.rol)
        self.tablo.setRowCount(len(program))
        for r, row in enumerate(program):
            for c in range(4):
                self.tablo.setItem(r, c, QTableWidgetItem(str(row[c])))

    def pdf_cikar(self):
        dosya, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "Program.pdf", "PDF Dosyaları (*.pdf)")
        if dosya:
            try:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(dosya)
                
                doc = QTextDocument()
                html = """
                <h1 style='text-align: center; color: #1E2A38;'>Haftalık Ders Programı</h1>
                <hr>
                <p>Bu doküman Online Kurs Sistemleri tarafından otomatik oluşturulmuştur.</p>
                <table border='1' width='100%' cellpadding='5' cellspacing='0'>
                <tr><th>Gün</th><th>Başlangıç</th><th>Bitiş</th><th>Kurs</th></tr>
                """
                for row in range(self.tablo.rowCount()):
                    html += f"<tr><td>{self.tablo.item(row,0).text()}</td><td>{self.tablo.item(row,1).text()}</td><td>{self.tablo.item(row,2).text()}</td><td>{self.tablo.item(row,3).text()}</td></tr>"
                html += "</table>"
                doc.setHtml(html)
                doc.print_(printer)
                QMessageBox.information(self, "Başarılı", "PDF başarıyla oluşturuldu!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturulamadı: {e}")

class LessonContentDialog(QDialog):
    def __init__(self, sistem, ders_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ders İçeriği")
        self.setFixedSize(600, 500)
        self.setStyleSheet(parent.window().styleSheet() if parent else STIL_LIGHT)
        layout = QVBoxLayout(self)
        ders = sistem.db.calistir("SELECT konu, icerik_pdf, video_link, notes FROM lessons WHERE id=?", (ders_id,), fetchone=True)
        if ders:
            layout.addWidget(QLabel(f"Konu: {ders[0]}", objectName="Title"))
            layout.addWidget(QLabel(f"PDF Linki: {ders[1]}", objectName="Subtitle"))
            layout.addWidget(QLabel(f"Video Linki: {ders[2] or 'Eklenmemiş'}", objectName="Subtitle"))
            layout.addWidget(QLabel("Ders Notları:"))
            notes = QTextEdit(); notes.setPlainText(ders[3] or "Not bulunmuyor."); notes.setReadOnly(True)
            layout.addWidget(notes)
        btn = SafeButton("Kapat"); btn.clicked.connect(self.accept); layout.addWidget(btn)

class ManageLessonsPanel(QDialog):
    def __init__(self, sistem, kurs_id, parent=None):
        super().__init__(parent)
        self.sistem = sistem; self.kurs_id = kurs_id
        self.setWindowTitle("Ders Yönetimi"); self.setFixedSize(500, 600)
        self.setStyleSheet(parent.window().styleSheet() if parent else STIL_LIGHT)
        layout = QVBoxLayout(self)
        self.konu = QLineEdit(); self.konu.setPlaceholderText("Ders Konusu")
        self.hafta = QSpinBox(); self.hafta.setPrefix("Hafta: "); self.hafta.setRange(1, 52)
        self.pdf = QLineEdit(); self.pdf.setPlaceholderText("PDF Linki")
        self.video = QLineEdit(); self.video.setPlaceholderText("Video Linki")
        self.notes = QTextEdit(); self.notes.setPlaceholderText("Ders Notları")
        btn = SafeButton("Ders Ekle"); btn.setObjectName("BtnSuccess"); btn.clicked.connect(self.ekle)
        layout.addWidget(self.konu); layout.addWidget(self.hafta); layout.addWidget(self.pdf); layout.addWidget(self.video); layout.addWidget(self.notes); layout.addWidget(btn)
        self.list = QListWidget(); layout.addWidget(self.list)
        self.yukle()
    def yukle(self):
        self.list.clear()
        for d in self.sistem.db.calistir("SELECT hafta_no, konu FROM lessons WHERE kurs_id=? ORDER BY hafta_no", (self.kurs_id,), fetchall=True): self.list.addItem(f"Hafta {d[0]}: {d[1]}")
    def ekle(self):
        try:
            if not self.konu.text().strip(): raise ValueError("Konu boş olamaz.")
            self.sistem.haftalik_plan_ekle(self.kurs_id, self.hafta.value(), self.konu.text(), self.pdf.text(), self.video.text(), self.notes.toPlainText())
            self.yukle()
        except Exception as e: QMessageBox.warning(self, "Hata", str(e))

class TeacherAssignmentsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        
        # ÜST KISIM: Başlık ve Belirgin Ödev Yayınlama Butonu
        h_ust = QHBoxLayout()
        h_ust.addWidget(QLabel("📝 Ödev Yönetimi ve Değerlendirme", objectName="Title"))
        btn_yeni_odev = SafeButton("➕ Yeni Ödev Yayınla")
        btn_yeni_odev.setCursor(Qt.PointingHandCursor)
        btn_yeni_odev.setStyleSheet("background-color: #27AE60; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold; font-size: 14px;")
        btn_yeni_odev.clicked.connect(self.yeni_odev_modal)
        h_ust.addStretch(); h_ust.addWidget(btn_yeni_odev)
        layout.addLayout(h_ust)
        
        self.tabs = QTabWidget()
        
        self.tab_odevler_widget = QWidget(); l_odev = QVBoxLayout(self.tab_odevler_widget)
        self.tab_odevler = QTableWidget(); self.tab_odevler.setColumnCount(5)
        self.tab_odevler.setHorizontalHeaderLabels(["Kurs", "Ödev Başlığı", "Son Teslim Tarihi", "Açıklama", "İşlemler"])
        self.tab_odevler.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tab_odevler.setEditTriggers(QAbstractItemView.NoEditTriggers); self.tab_odevler.setFocusPolicy(Qt.NoFocus); self.tab_odevler.setSelectionMode(QAbstractItemView.NoSelection)
        self.tab_odevler.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none;}")
        l_odev.addWidget(self.tab_odevler)
        self.tabs.addTab(self.tab_odevler_widget, "📖 Verilen Ödevler")

        self.tab_teslim_widget = QWidget(); l_teslim = QVBoxLayout(self.tab_teslim_widget)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(["Kayıt ID", "Öğrenci", "Yüklenen Dosya", "Not", "Geribildirim", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers); self.tablo.setFocusPolicy(Qt.NoFocus); self.tablo.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablo.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none;}")
        l_teslim.addWidget(self.tablo)
        self.tabs.addTab(self.tab_teslim_widget, "📥 Teslimatlar ve Puanlama")
        
        layout.addWidget(self.tabs); self.yukle()

    def yukle(self):
        self.tab_odevler.setRowCount(0)
        odevler = self.sistem.egitmen_odevleri_getir(self.user.id)
        self.tab_odevler.setRowCount(len(odevler))
        for r, row in enumerate(odevler):
            self.tab_odevler.setItem(r, 0, QTableWidgetItem(str(row[2]))); self.tab_odevler.setItem(r, 1, QTableWidgetItem(str(row[1])))
            self.tab_odevler.setItem(r, 2, QTableWidgetItem(str(row[3]))); self.tab_odevler.setItem(r, 3, QTableWidgetItem(str(row[4])))
            
            b_widget = QWidget(); b_layout = QHBoxLayout(b_widget); b_layout.setContentsMargins(0,0,0,0)
            btn_duzenle = QPushButton("✏️ Düzenle"); btn_duzenle.setCursor(Qt.PointingHandCursor)
            btn_duzenle.setStyleSheet("background-color: #3182CE; color: white; border-radius: 4px; padding: 5px; font-weight:bold;")
            btn_duzenle.clicked.connect(lambda ch, odev=row: self.odev_duzenle_modal(odev))
            
            btn_sil = QPushButton("🗑️ Sil"); btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.setStyleSheet("background-color: #E53E3E; color: white; border-radius: 4px; padding: 5px; font-weight:bold;")
            btn_sil.clicked.connect(lambda ch, oid=row[0]: self.odev_sil_ui(oid))
            
            b_layout.addWidget(btn_duzenle); b_layout.addWidget(btn_sil)
            self.tab_odevler.setCellWidget(r, 4, b_widget)
            
        self.tablo.setRowCount(0)
        sorgu = "SELECT s.id, u.isim, s.dosya_yolu, s.not_degeri, s.geribildirim FROM submissions s JOIN assignments a ON s.assignment_id = a.id JOIN courses c ON a.kurs_id = c.id JOIN users u ON s.ogrenci_id = u.id WHERE c.egitmen_id = ?"
        subs = self.sistem.db.calistir(sorgu, (self.user.id,), fetchall=True)
        self.tablo.setRowCount(len(subs))
        for r, row in enumerate(subs):
            self.tablo.setItem(r, 0, QTableWidgetItem(str(row[0])[:8]))
            self.tablo.setItem(r, 1, QTableWidgetItem(str(row[1])))
            
            # --- 1. DÜZELTME: Dosya Açma Butonu ---
            if row[2]:
                btn_dosya = QPushButton("Dosyayı Aç")
                btn_dosya.setCursor(Qt.PointingHandCursor)
                btn_dosya.setStyleSheet("background-color: #3498DB; color: white; border-radius: 4px; padding: 5px; font-weight:bold;")
                btn_dosya.clicked.connect(lambda ch, yol=row[2]: QDesktopServices.openUrl(QUrl.fromLocalFile(yol)))
                self.tablo.setCellWidget(r, 2, btn_dosya)
            else:
                self.tablo.setItem(r, 2, QTableWidgetItem("Yüklenmedi"))
                
            self.tablo.setItem(r, 3, QTableWidgetItem(str(row[3] if row[3] is not None else "Bekliyor")))
            self.tablo.setItem(r, 4, QTableWidgetItem(str(row[4] if row[4] else "Bekliyor")))

            b_widget = QWidget(); b_layout = QHBoxLayout(b_widget); b_layout.setContentsMargins(0,0,0,0)
            btn = QPushButton("Notlandır"); btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("background-color: #F39C12; color: white; border-radius: 4px; padding: 5px; font-weight:bold;")
            btn.clicked.connect(lambda ch, sid=row[0]: self.notlandir_modal(sid))
            b_layout.addWidget(btn, alignment=Qt.AlignCenter)
            self.tablo.setCellWidget(r, 5, b_widget)

    def odev_sil_ui(self, odev_id):
        if QMessageBox.question(self, "Onay", "Bu ödevi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.sistem.odev_sil(odev_id)
            self.yukle()
            QMessageBox.information(self, "Başarılı", "Ödev başarıyla silindi.")

    def odev_duzenle_modal(self, odev):
        modal = QDialog(self); modal.setWindowTitle("Ödev Düzenle"); modal.setFixedSize(450, 400); modal.setStyleSheet(self.window().styleSheet())
        l = QVBoxLayout(modal)
        
        baslik = QLineEdit(odev[1]); baslik.setPlaceholderText("Ödev Başlığı")
        aciklama = QTextEdit(odev[4]); aciklama.setPlaceholderText("Açıklama")
        son_tarih = QDateEdit(); son_tarih.setCalendarPopup(True)
        try: son_tarih.setDate(QDate.fromString(odev[3], "yyyy-MM-dd"))
        except: son_tarih.setDate(QDate.currentDate())
        
        btn = SafeButton("Güncelle"); btn.setObjectName("BtnSuccess")
        l.addWidget(QLabel("Ödev Başlığı:")); l.addWidget(baslik)
        l.addWidget(QLabel("Son Teslim Tarihi:")); l.addWidget(son_tarih)
        l.addWidget(QLabel("Açıklama:")); l.addWidget(aciklama)
        l.addStretch(); l.addWidget(btn)
        
        def guncelle():
            if not baslik.text().strip(): return QMessageBox.warning(modal, "Hata", "Başlık boş olamaz.")
            self.sistem.odev_guncelle(odev[0], baslik.text().strip(), aciklama.toPlainText().strip(), son_tarih.date().toString("yyyy-MM-dd"))
            modal.accept()
            self.yukle()
            QMessageBox.information(self, "Başarılı", "Ödev güncellendi.")
            
        btn.clicked.connect(guncelle)
        modal.exec_()

    def yeni_odev_modal(self):
        modal = QDialog(self); modal.setWindowTitle("Yeni Ödev Oluştur"); modal.setFixedSize(450, 450); modal.setStyleSheet(self.window().styleSheet())
        l = QVBoxLayout(modal)
        kurs_combo = QComboBox()
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): kurs_combo.addItem(k[1], k[0])
        baslik = QLineEdit(); baslik.setPlaceholderText("Örn: Python Projesi")
        aciklama = QTextEdit(); aciklama.setPlaceholderText("Ödev detaylarını buraya yazın...")
        son_tarih = QDateEdit(); son_tarih.setMinimumDate(QDate.currentDate())
        son_tarih.setDate(QDate.currentDate().addDays(7)); son_tarih.setCalendarPopup(True)
        btn = SafeButton("Ödevi Yayınla"); btn.setObjectName("BtnSuccess")
        def kaydet():
            try:
                kid = kurs_combo.currentData()
                if not kid: raise ValueError("Önce bir kurs oluşturmalısınız!")
                if not baslik.text().strip(): raise ValueError("Ödev başlığı boş olamaz.")
                self.sistem.odev_ekle(kid, baslik.text(), aciklama.toPlainText(), son_tarih.date().toString("yyyy-MM-dd"))
                QMessageBox.information(modal, "Başarılı", "Ödev yayınlandı.")
                modal.accept(); self.yukle()
            except Exception as e: QMessageBox.critical(modal, "Hata", str(e))
        btn.clicked.connect(kaydet)
        l.addWidget(QLabel("Hedef Kurs:")); l.addWidget(kurs_combo); l.addWidget(QLabel("Ödev Başlığı:")); l.addWidget(baslik)
        l.addWidget(QLabel("Son Teslim Tarihi:")); l.addWidget(son_tarih); l.addWidget(QLabel("Açıklama:")); l.addWidget(aciklama); l.addWidget(btn)
        modal.exec_()

    def notlandir_modal(self, sid):
        modal = QDialog(self); modal.setWindowTitle("Notlandır"); modal.setFixedSize(400, 300); modal.setStyleSheet(self.window().styleSheet())
        l = QVBoxLayout(modal)
        puan = QSpinBox(); puan.setRange(0, 100); puan.setPrefix("Puan: ")
        yorum = QTextEdit(); yorum.setPlaceholderText("Geribildirim (Yorumlar)")
        btn = SafeButton("Kaydet"); btn.setObjectName("BtnSuccess")
        def kaydet():
            try:
                self.sistem.db.calistir("UPDATE submissions SET not_degeri=?, geribildirim=? WHERE id=?", (puan.value(), yorum.toPlainText(), sid))
                QMessageBox.information(modal, "Başarılı", "Not sisteme kaydedildi.")
                modal.accept(); self.yukle()
            except Exception as e: QMessageBox.critical(modal, "Hata", str(e))
        btn.clicked.connect(kaydet)
        l.addWidget(QLabel("Not Değeri:")); l.addWidget(puan); l.addWidget(QLabel("Geribildirim:")); l.addWidget(yorum); l.addWidget(btn)
        modal.exec_()

class StudentGradesPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("📊 Notlarım ve Değerlendirmelerim", objectName="Title"))
        
        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        
        self.k_combo = QComboBox()
        self.k_combo.setStyleSheet("padding: 8px; border-radius: 4px;")
        for k in self.sistem.db.calistir("SELECT c.id, c.kurs_adi FROM enrollments e JOIN courses c ON e.kurs_id = c.id WHERE e.ogrenci_id=?", (self.user.id,), fetchall=True):
            self.k_combo.addItem(k[1], k[0])
            
        self.k_combo.currentIndexChanged.connect(self.yukle)
        f_layout.addWidget(QLabel("<b>Kurs Seçimi:</b>"))
        f_layout.addWidget(self.k_combo)
        f_layout.addSpacing(15)
        
        self.detay_text = QTextBrowser()
        self.detay_text.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px; background: #FFFFFF; font-size: 14px;")
        f_layout.addWidget(self.detay_text)
        
        layout.addWidget(frame)
        self.yukle()

    def yukle(self):
        kid = self.k_combo.currentData()
        if not kid: 
            self.detay_text.setText("Henüz bir kursa kayıtlı değilsiniz.")
            return
            
        html = f"<h3>📈 {self.k_combo.currentText()} - Not Detayları</h3>"
        
        odevler = self.sistem.db.calistir("SELECT a.baslik, s.not_degeri, s.geribildirim FROM assignments a LEFT JOIN submissions s ON a.id = s.assignment_id AND s.ogrenci_id = ? WHERE a.kurs_id = ?", (self.user.id, kid), fetchall=True)
        html += "<h4>📚 Ödev Notları</h4><ul>"
        for o in odevler:
            not_deg = o[1] if o[1] is not None else "Değerlendirilmedi"
            html += f"<li><b>{o[0]}:</b> {not_deg} Puan (Yorum: {o[2] if o[2] else '-'})</li>"
        if not odevler: html += "<li>Henüz ödev verilmemiş.</li>"
        html += "</ul>"
        
        haftalar = self.sistem.db.calistir("SELECT hafta, puan, durum_analizi FROM student_points WHERE ogrenci_id=? AND kurs_id=? ORDER BY tarih DESC", (self.user.id, kid), fetchall=True)
        html += "<h4>⭐ Öğretmen Değerlendirmeleri (Haftalık)</h4><ul>"
        for h in haftalar: html += f"<li><b>{h[0]}:</b> {h[1]} Puan - {h[2]}</li>"
        if not haftalar: html += "<li>Henüz değerlendirme yapılmamış.</li>"
        html += "</ul>"
        
        sinavlar = self.sistem.db.calistir("SELECT sinav1, sinav2 FROM enrollments WHERE ogrenci_id=? AND kurs_id=?", (self.user.id, kid), fetchone=True)
        html += "<h4>📝 Sınav Notları</h4><ul>"
        if sinavlar:
            html += f"<li><b>1. Sınav:</b> {sinavlar[0] if sinavlar[0] is not None else 'Açıklanmadı'}</li>"
            html += f"<li><b>2. Sınav:</b> {sinavlar[1] if sinavlar[1] is not None else 'Açıklanmadı'}</li>"
        html += "</ul>"
        
        self.detay_text.setHtml(html)

class StudentAssignmentsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Görevlerim ve Teslimler", objectName="Title"))
        self.tablo = QTableWidget(); self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["Görev Başlığı", "Son Tarih", "Durum", "Not", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()
    def yukle(self):
        gorevler = self.sistem.ogrenci_haftalik_gorevler(self.user.id)
        self.tablo.setRowCount(len(gorevler))
        for r, g in enumerate(gorevler):
            self.tablo.setItem(r, 0, QTableWidgetItem(g[2])); self.tablo.setItem(r, 1, QTableWidgetItem(g[3]))
            sub = self.sistem.db.calistir("SELECT id, not_degeri, geribildirim FROM submissions WHERE assignment_id=? AND ogrenci_id=?", (g[0], self.user.id), fetchone=True)
            durum = "Teslim Edildi" if sub else "Bekliyor"
            not_deg = str(sub[1]) if sub and sub[1] is not None else "-"
            self.tablo.setItem(r, 2, QTableWidgetItem(durum)); self.tablo.setItem(r, 3, QTableWidgetItem(not_deg))
            
            son_tarih = datetime.strptime(g[3], "%Y-%m-%d").date()
            if not sub and son_tarih < datetime.now().date():
                for c in range(5): self.tablo.item(r, c).setBackground(QColor("#FFCDD2")) # Geciken ödev kırmızı
                
            if not sub:
                btn = SafeButton("Dosya Yükle"); btn.setObjectName("BtnSuccess")
                btn.clicked.connect(lambda ch, aid=g[0]: self.teslim_et(aid))
                self.tablo.setCellWidget(r, 4, btn)
            else:
                btn = QPushButton("Detay"); btn.clicked.connect(lambda ch, g=sub[2]: QMessageBox.information(self, "Geribildirim", str(g) or "Geribildirim yok."))
                self.tablo.setCellWidget(r, 4, btn)
    def teslim_et(self, aid):
        dosya, _ = QFileDialog.getOpenFileName(self, "Ödev Dosyası Seç")
        if dosya:
            self.sistem.db.calistir("INSERT INTO submissions (id, assignment_id, ogrenci_id, dosya_yolu) VALUES (?, ?, ?, ?)", (str(uuid.uuid4()), aid, self.user.id, dosya))
            QMessageBox.information(self, "Başarılı", "Ödev teslim edildi."); self.yukle()

class TeacherExamPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        hl = QHBoxLayout(); hl.addWidget(QLabel("Sınav Yönetimi", objectName="Title"))
        btn_ekle = SafeButton("+ Yeni Sınav"); btn_ekle.clicked.connect(self.yeni_sinav_modal); hl.addWidget(btn_ekle)
        layout.addLayout(hl)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["ID", "Sınav Başlığı", "Kurs ID", "Süre (dk)"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()
    def yukle(self):
        sinavlar = self.sistem.egitmen_sinavlari_getir(self.user.id)
        self.tablo.setRowCount(len(sinavlar))
        for r, row in enumerate(sinavlar):
            for c in range(4): self.tablo.setItem(r, c, QTableWidgetItem(str(row[c])))
    def yeni_sinav_modal(self):
        modal = QDialog(self); modal.setWindowTitle("Yeni Sınav Oluştur"); modal.setFixedSize(400, 300)
        l = QVBoxLayout(modal)
        kurs_combo = QComboBox()
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): kurs_combo.addItem(k[1], k[0])
        baslik = QLineEdit(); baslik.setPlaceholderText("Sınav Başlığı")
        sure = QSpinBox(); sure.setRange(5, 180); sure.setSuffix(" dk")
        btn = SafeButton("Sınav Oluştur"); btn.setObjectName("BtnSuccess")
        def kaydet():
            try:
                if not baslik.text().strip(): raise ValueError("Başlık boş olamaz.")
                if baslik.text().strip().isdigit(): raise ValueError("Sınav başlığı sadece rakamlardan oluşamaz.")
                kid = kurs_combo.currentData()
                if not kid: raise ValueError("Kurs seçmelisiniz.")
                self.sistem.sinav_ekle(kid, baslik.text(), sure.value())
                modal.accept(); self.yukle()
            except Exception as e: QMessageBox.critical(modal, "Hata", str(e))
        btn.clicked.connect(kaydet)
        l.addWidget(QLabel("Kurs:")); l.addWidget(kurs_combo); l.addWidget(QLabel("Başlık:")); l.addWidget(baslik); l.addWidget(QLabel("Süre (Dakika):")); l.addWidget(sure); l.addWidget(btn)
        modal.exec_()

class StudentExamsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Sınavlarım", objectName="Title"))
        self.tablo = QTableWidget(); self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Sınav Başlığı", "Kurs Adı", "Süre (dk)", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()
    def yukle(self):
        sinavlar = self.sistem.ogrenci_yaklasan_sinavlar(self.user.id)
        self.tablo.setRowCount(len(sinavlar))
        for r, row in enumerate(sinavlar):
            self.tablo.setItem(r, 0, QTableWidgetItem(row[2])); self.tablo.setItem(r, 1, QTableWidgetItem(row[1])); self.tablo.setItem(r, 2, QTableWidgetItem(str(row[3])))
            zaten = self.sistem.db.calistir("SELECT id FROM exam_results WHERE exam_id=? AND user_id=?", (row[0], self.user.id), fetchone=True)
            if zaten:
                btn = QPushButton("Tamamlandı"); btn.setEnabled(False)
            else:
                btn = SafeButton("Sınava Başla"); btn.setObjectName("BtnSuccess")
                btn.clicked.connect(lambda ch, eid=row[0], sure=row[3]: self.sinava_basla(eid, sure))
            self.tablo.setCellWidget(r, 3, btn)
    def sinava_basla(self, eid, sure):
        modal = QDialog(self); modal.setWindowTitle("Sınav"); modal.setFixedSize(500, 400)
        l = QVBoxLayout(modal); l.addWidget(QLabel("Sınav Devam Ediyor...", objectName="Title"))
        timer_lbl = QLabel(f"Kalan Süre: {sure}:00"); timer_lbl.setStyleSheet("font-size: 20px; color: #E74C3C; font-weight: bold;"); l.addWidget(timer_lbl)
        l.addWidget(QLabel("Sınav soruları burada yer alacaktır.\n(Simülasyon)"))
        btn = SafeButton("Sınavı Bitir"); btn.setObjectName("BtnSuccess"); l.addWidget(btn)
        self.kalan_sn = sure * 60; timer = QTimer(modal)
        def tick():
            self.kalan_sn -= 1; dk = self.kalan_sn // 60; sn = self.kalan_sn % 60
            timer_lbl.setText(f"Kalan Süre: {dk:02d}:{sn:02d}")
            if self.kalan_sn <= 0: timer.stop(); bitir()
        timer.timeout.connect(tick); timer.start(1000)
        def bitir():
            timer.stop(); puan = 85
            self.sistem.db.calistir("INSERT INTO exam_results (id, exam_id, user_id, score) VALUES (?, ?, ?, ?)", (str(uuid.uuid4()), eid, self.user.id, puan))
            modal.accept(); self.yukle(); self.goster_sonuc(puan)
        btn.clicked.connect(bitir); modal.exec_()
    def goster_sonuc(self, puan):
        msg = QDialog(self); msg.setWindowTitle("Sınav Sonucu"); msg.setFixedSize(300, 200)
        ml = QVBoxLayout(msg); lbl = QLabel(f"Puanınız: {puan}"); lbl.setObjectName("Title"); lbl.setAlignment(Qt.AlignCenter)
        eff = QGraphicsOpacityEffect(lbl); lbl.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity"); anim.setDuration(1000); anim.setStartValue(0); anim.setEndValue(1); anim.start()
        ml.addWidget(lbl); ok_btn = QPushButton("Tamam"); ok_btn.clicked.connect(msg.accept); ml.addWidget(ok_btn); msg.exec_()


class LessonContentDialog(QDialog):
    def __init__(self, sistem, ders_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ders İçeriği")
        self.setFixedSize(600, 500)
        self.setStyleSheet(parent.window().styleSheet() if parent else STIL_LIGHT)
        layout = QVBoxLayout(self)
        ders = sistem.db.calistir("SELECT konu, icerik_pdf, video_link, notes FROM lessons WHERE id=?", (ders_id,), fetchone=True)
        if ders:
            layout.addWidget(QLabel(f"Konu: {ders[0]}", objectName="Title"))
            layout.addWidget(QLabel(f"PDF Linki: {ders[1]}", objectName="Subtitle"))
            layout.addWidget(QLabel(f"Video Linki: {ders[2] or 'Eklenmemiş'}", objectName="Subtitle"))
            layout.addWidget(QLabel("Ders Notları:"))
            notes = QTextEdit(); notes.setPlainText(ders[3] or "Not bulunmuyor."); notes.setReadOnly(True)
            layout.addWidget(notes)
        btn = SafeButton("Kapat"); btn.clicked.connect(self.accept); layout.addWidget(btn)

class ManageLessonsPanel(QDialog):
    def __init__(self, sistem, kurs_id, parent=None):
        super().__init__(parent)
        self.sistem = sistem; self.kurs_id = kurs_id
        self.setWindowTitle("Ders Yönetimi"); self.setFixedSize(500, 600)
        self.setStyleSheet(parent.window().styleSheet() if parent else STIL_LIGHT)
        layout = QVBoxLayout(self)
        self.konu = QLineEdit(); self.konu.setPlaceholderText("Ders Konusu")
        self.hafta = QSpinBox(); self.hafta.setPrefix("Hafta: "); self.hafta.setRange(1, 52)
        self.pdf = QLineEdit(); self.pdf.setPlaceholderText("PDF Linki")
        self.video = QLineEdit(); self.video.setPlaceholderText("Video Linki")
        self.notes = QTextEdit(); self.notes.setPlaceholderText("Ders Notları")
        btn = SafeButton("Ders Ekle"); btn.setObjectName("BtnSuccess"); btn.clicked.connect(self.ekle)
        layout.addWidget(self.konu); layout.addWidget(self.hafta); layout.addWidget(self.pdf); layout.addWidget(self.video); layout.addWidget(self.notes); layout.addWidget(btn)
        self.list = QListWidget(); layout.addWidget(self.list)
        self.yukle()
    def yukle(self):
        self.list.clear()
        for d in self.sistem.db.calistir("SELECT hafta_no, konu FROM lessons WHERE kurs_id=? ORDER BY hafta_no", (self.kurs_id,), fetchall=True): self.list.addItem(f"Hafta {d[0]}: {d[1]}")
    def ekle(self):
        try:
            if not self.konu.text().strip(): raise ValueError("Konu boş olamaz.")
            self.sistem.haftalik_plan_ekle(self.kurs_id, self.hafta.value(), self.konu.text(), self.pdf.text(), self.video.text(), self.notes.toPlainText())
            self.yukle()
        except Exception as e: QMessageBox.warning(self, "Hata", str(e))


class StudentAssignmentsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Görevlerim ve Teslimler", objectName="Title"))
        self.tablo = QTableWidget(); self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["Görev Başlığı", "Son Tarih", "Durum", "Not", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()
    def yukle(self):
        gorevler = self.sistem.ogrenci_haftalik_gorevler(self.user.id)
        self.tablo.setRowCount(len(gorevler))
        for r, g in enumerate(gorevler):
            self.tablo.setItem(r, 0, QTableWidgetItem(g[2])); self.tablo.setItem(r, 1, QTableWidgetItem(g[3]))
            sub = self.sistem.db.calistir("SELECT id, not_degeri, geribildirim FROM submissions WHERE assignment_id=? AND ogrenci_id=?", (g[0], self.user.id), fetchone=True)
            durum = "Teslim Edildi" if sub else "Bekliyor"
            not_deg = str(sub[1]) if sub and sub[1] is not None else "-"
            self.tablo.setItem(r, 2, QTableWidgetItem(durum)); self.tablo.setItem(r, 3, QTableWidgetItem(not_deg))
            if not sub:
                btn = SafeButton("Dosya Yükle"); btn.setObjectName("BtnSuccess")
                btn.clicked.connect(lambda ch, aid=g[0]: self.teslim_et(aid))
                self.tablo.setCellWidget(r, 4, btn)
            else:
                btn = QPushButton("Detay"); btn.clicked.connect(lambda ch, g=sub[2]: QMessageBox.information(self, "Geribildirim", str(g) or "Geribildirim yok."))
                self.tablo.setCellWidget(r, 4, btn)
    def teslim_et(self, aid):
        dosya, _ = QFileDialog.getOpenFileName(self, "Ödev Dosyası Seç")
        if dosya:
            self.sistem.db.calistir("INSERT INTO submissions (id, assignment_id, ogrenci_id, dosya_yolu) VALUES (?, ?, ?, ?)", (str(uuid.uuid4()), aid, self.user.id, dosya))
            QMessageBox.information(self, "Başarılı", "Ödev teslim edildi."); self.yukle()

class TeacherExamPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        hl = QHBoxLayout(); hl.addWidget(QLabel("Sınav Yönetimi", objectName="Title"))
        btn_ekle = SafeButton("+ Yeni Sınav"); btn_ekle.clicked.connect(self.yeni_sinav_modal); hl.addWidget(btn_ekle)
        layout.addLayout(hl)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["ID", "Sınav Başlığı", "Kurs ID", "Süre (dk)"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()
    def yukle(self):
        sinavlar = self.sistem.egitmen_sinavlari_getir(self.user.id)
        self.tablo.setRowCount(len(sinavlar))
        for r, row in enumerate(sinavlar):
            for c in range(4): self.tablo.setItem(r, c, QTableWidgetItem(str(row[c])))
    def yeni_sinav_modal(self):
        modal = QDialog(self); modal.setWindowTitle("Yeni Sınav Oluştur"); modal.setFixedSize(400, 300)
        l = QVBoxLayout(modal)
        kurs_combo = QComboBox()
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): kurs_combo.addItem(k[1], k[0])
        baslik = QLineEdit(); baslik.setPlaceholderText("Sınav Başlığı")
        sure = QSpinBox(); sure.setRange(5, 180); sure.setSuffix(" dk")
        btn = SafeButton("Sınav Oluştur"); btn.setObjectName("BtnSuccess")
        def kaydet():
            try:
                if not baslik.text().strip(): raise ValueError("Başlık boş olamaz.")
                kid = kurs_combo.currentData()
                if not kid: raise ValueError("Kurs seçmelisiniz.")
                self.sistem.sinav_ekle(kid, baslik.text(), sure.value())
                modal.accept(); self.yukle()
            except Exception as e: QMessageBox.critical(modal, "Hata", str(e))
        btn.clicked.connect(kaydet)
        l.addWidget(QLabel("Kurs:")); l.addWidget(kurs_combo); l.addWidget(QLabel("Başlık:")); l.addWidget(baslik); l.addWidget(QLabel("Süre (Dakika):")); l.addWidget(sure); l.addWidget(btn)
        modal.exec_()

class StudentExamsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Sınavlarım", objectName="Title"))
        self.tablo = QTableWidget(); self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Sınav Başlığı", "Kurs Adı", "Süre (dk)", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()
    def yukle(self):
        sinavlar = self.sistem.ogrenci_yaklasan_sinavlar(self.user.id)
        self.tablo.setRowCount(len(sinavlar))
        for r, row in enumerate(sinavlar):
            self.tablo.setItem(r, 0, QTableWidgetItem(row[2])); self.tablo.setItem(r, 1, QTableWidgetItem(row[1])); self.tablo.setItem(r, 2, QTableWidgetItem(str(row[3])))
            zaten = self.sistem.db.calistir("SELECT id FROM exam_results WHERE exam_id=? AND user_id=?", (row[0], self.user.id), fetchone=True)
            if zaten:
                btn = QPushButton("Tamamlandı"); btn.setEnabled(False)
            else:
                btn = SafeButton("Sınava Başla"); btn.setObjectName("BtnSuccess")
                btn.clicked.connect(lambda ch, eid=row[0], sure=row[3]: self.sinava_basla(eid, sure))
            self.tablo.setCellWidget(r, 3, btn)
    def sinava_basla(self, eid, sure):
        modal = QDialog(self); modal.setWindowTitle("Sınav"); modal.setFixedSize(500, 400)
        l = QVBoxLayout(modal); l.addWidget(QLabel("Sınav Devam Ediyor...", objectName="Title"))
        timer_lbl = QLabel(f"Kalan Süre: {sure}:00"); timer_lbl.setStyleSheet("font-size: 20px; color: #E74C3C; font-weight: bold;"); l.addWidget(timer_lbl)
        l.addWidget(QLabel("Sınav soruları burada yer alacaktır.\n(Simülasyon)"))
        btn = SafeButton("Sınavı Bitir"); btn.setObjectName("BtnSuccess"); l.addWidget(btn)
        self.kalan_sn = sure * 60; timer = QTimer(modal)
        def tick():
            self.kalan_sn -= 1; dk = self.kalan_sn // 60; sn = self.kalan_sn % 60
            timer_lbl.setText(f"Kalan Süre: {dk:02d}:{sn:02d}")
            if self.kalan_sn <= 0: timer.stop(); bitir()
        timer.timeout.connect(tick); timer.start(1000)
        def bitir():
            timer.stop(); puan = 85
            self.sistem.db.calistir("INSERT INTO exam_results (id, exam_id, user_id, score) VALUES (?, ?, ?, ?)", (str(uuid.uuid4()), eid, self.user.id, puan))
            modal.accept(); self.yukle(); self.goster_sonuc(puan)
        btn.clicked.connect(bitir); modal.exec_()
    def goster_sonuc(self, puan):
        msg = QDialog(self); msg.setWindowTitle("Sınav Sonucu"); msg.setFixedSize(300, 200)
        ml = QVBoxLayout(msg); lbl = QLabel(f"Puanınız: {puan}"); lbl.setObjectName("Title"); lbl.setAlignment(Qt.AlignCenter)
        eff = QGraphicsOpacityEffect(lbl); lbl.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity"); anim.setDuration(1000); anim.setStartValue(0); anim.setEndValue(1); anim.start()
        ml.addWidget(lbl); ok_btn = QPushButton("Tamam"); ok_btn.clicked.connect(msg.accept); ml.addWidget(ok_btn); msg.exec_()

class StudentRewardPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("🏆 Başarılarım ve Rozetlerim", objectName="Title"))
        
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setStyleSheet("border:none;")
        self.container = QWidget(); self.flow_layout = QGridLayout(self.container)
        self.scroll.setWidget(self.container); layout.addWidget(self.scroll)
        self.yukle()

    def yukle(self):
        badges = self.sistem.db.calistir("SELECT badge_name, tarih FROM badges WHERE user_id=? ORDER BY tarih DESC", (self.user.id,), fetchall=True)
        if not badges:
            self.flow_layout.addWidget(QLabel("Henüz bir rozet kazanmadınız. Kurslara aktif katılarak kazanabilirsiniz!"))
            return
            
        for i, b in enumerate(badges):
            kutu = QFrame(); kutu.setObjectName("Card"); kutu.setFixedSize(200, 150); drop_shadow(kutu)
            l = QVBoxLayout(kutu)
            img = QLabel("🎖️"); img.setStyleSheet("font-size: 40px;"); img.setAlignment(Qt.AlignCenter)
            txt = QLabel(f"<b>{b[0]}</b>"); txt.setAlignment(Qt.AlignCenter)
            tar = QLabel(str(b[1])[:10]); tar.setStyleSheet("font-size:10px; color:gray;"); tar.setAlignment(Qt.AlignCenter)
            l.addWidget(img); l.addWidget(txt); l.addWidget(tar)
            self.flow_layout.addWidget(kutu, i // 3, i % 3)


class AdminSettingsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Sistem Ayarları ve Yönetim", objectName="Title"))
        
        # 1. Kutu: Ayarlar
        kart = QFrame(); kart.setObjectName("Card"); drop_shadow(kart)
        kl = QVBoxLayout(kart)
        self.site_adi = QLineEdit(self.sistem.ayar_getir("site_adi", "SaaS Akademi"))
        
        btn_ayar = SafeButton("Ayarları Kaydet"); btn_ayar.setObjectName("BtnSuccess")
        btn_ayar.clicked.connect(lambda: self.sistem.ayar_kaydet("site_adi", self.site_adi.text()) or QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi."))
        
        btn_logo = SafeButton("Sistem Logosu Yükle"); btn_logo.setObjectName("BtnWarning")
        btn_logo.clicked.connect(self.logo_yukle)
        
        # Ödül Sistemi Butonu
        btn_odul = SafeButton("🏆 Ayın Öğrencisini Seç ve Rozet Ver")
        btn_odul.setObjectName("BtnSuccess")
        btn_odul.setToolTip("Sistemde en çok süre geçiren öğrenciyi tespit eder ve ona rozet tanımlar.")
        btn_odul.clicked.connect(self.odul_dagit)

        kl.addWidget(QLabel("Site Adı:")); kl.addWidget(self.site_adi); kl.addWidget(btn_logo); kl.addWidget(btn_ayar)
        kl.addWidget(QLabel("")); kl.addWidget(btn_odul) 
        layout.addWidget(kart)
        
        # 2. Kutu: Duyuru (GİRİNTİ DÜZELTİLDİ)
        kart2 = QFrame(); kart2.setObjectName("Card"); drop_shadow(kart2)
        kl2 = QVBoxLayout(kart2)
        kl2.addWidget(QLabel("Yeni Duyuru Yayınla", objectName="Subtitle"))
        self.d_baslik = QLineEdit(); self.d_baslik.setPlaceholderText("Duyuru Başlığı")
        self.d_mesaj = QTextEdit(); self.d_mesaj.setPlaceholderText("Mesajınız...")
        btn_duyuru = SafeButton("Duyuru Yayınla"); btn_duyuru.setObjectName("BtnSuccess")
        btn_duyuru.clicked.connect(self.duyuru_yayinla)
        kl2.addWidget(self.d_baslik); kl2.addWidget(self.d_mesaj); kl2.addWidget(btn_duyuru)
        layout.addWidget(kart2); layout.addStretch()
        
    def logo_yukle(self):
        dosya, _ = QFileDialog.getOpenFileName(self, "Logo Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if dosya:
            self.sistem.ayar_kaydet("site_logo", dosya)
            QMessageBox.information(self, "Başarılı", "Logo başarıyla güncellendi!")
            
    def odul_dagit(self):
        try:
            self.sistem.ayin_ogrencisini_belirle()
            QMessageBox.information(self, "Başarılı", "Sistem tarandı! Ayın öğrencisi seçildi ve rozetleri başarıyla hesabına tanımlandı.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"İşlem yapılamadı: {str(e)}")

    def duyuru_yayinla(self):
        b = self.d_baslik.text().strip(); m = self.d_mesaj.toPlainText().strip()
        if b and m:
            self.sistem.duyuru_ekle(b, m); QMessageBox.information(self, "Başarılı", "Duyuru yayınlandı.")
            self.d_baslik.clear(); self.d_mesaj.clear()
        else: QMessageBox.warning(self, "Hata", "Başlık ve mesaj boş olamaz.")


# --- YENİ ÖĞRETMEN VE ÖĞRENCİ PANELLERİ ---

class TeacherSessionManager(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem
        self.user = user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("⏰ Ders Oturumu Yönetimi", objectName="Title"))

        frame = QFrame()
        frame.setObjectName("Card")
        drop_shadow(frame)
        f_layout = QVBoxLayout(frame)

        self.kurs_combo = QComboBox()
        for k in self.sistem.egitmen_kurslari_getir(self.user.id):
            self.kurs_combo.addItem(k[1], k[0])

        self.tarih = QDateEdit()
        self.tarih.setDate(QDate.currentDate())
        self.tarih.setCalendarPopup(True)

        self.saat = QTimeEdit()
        self.saat.setDisplayFormat("HH:mm")

        self.lokasyon = QLineEdit()
        self.lokasyon.setPlaceholderText("Örn: Sınıf 101 veya Zoom Linki")

        btn = SafeButton("Oturum Oluştur")
        btn.setObjectName("BtnSuccess")
        btn.clicked.connect(self.olustur)

        f_layout.addWidget(QLabel("Hedef Kurs:"))
        f_layout.addWidget(self.kurs_combo)
        f_layout.addWidget(QLabel("Tarih ve Saat:"))
        h_ts = QHBoxLayout()
        h_ts.addWidget(self.tarih)
        h_ts.addWidget(self.saat)
        f_layout.addLayout(h_ts)
        f_layout.addWidget(QLabel("Lokasyon/Link:"))
        f_layout.addWidget(self.lokasyon)
        f_layout.addWidget(btn)

        layout.addWidget(frame)
        layout.addStretch()

    def olustur(self):
        kid = self.kurs_combo.currentData()
        lok = self.lokasyon.text().strip()
        if kid and lok:
            QMessageBox.information(self, "Başarılı", "Yeni oturum başarıyla oluşturuldu ve öğrencilere bildirildi!")
            self.lokasyon.clear()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurunuz.")

class TeacherNominationPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("🌟 Başarılı Öğrenciyi Aday Göster", objectName="Title"))
        
        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        
        self.ogrenci_combo = QComboBox()
        # Sadece öğretmenin kursundaki öğrencileri getirir
        sorgu = "SELECT DISTINCT u.id, u.isim FROM enrollments e JOIN courses c ON e.kurs_id = c.id JOIN users u ON e.ogrenci_id = u.id WHERE c.egitmen_id = ?"
        ogrenciler = self.sistem.db.calistir(sorgu, (self.user.id,), fetchall=True)
        for ogr in ogrenciler: self.ogrenci_combo.addItem(ogr[1], ogr[0])
        
        self.gerekce = QTextEdit(); self.gerekce.setPlaceholderText("Bu öğrenci neden ayın öğrencisi olmalı? (Yöneticiye iletilecektir)")
        btn = SafeButton("Adaylığı Yönetime Bildir")
        btn.setObjectName("BtnSuccess")
        btn.clicked.connect(self.gonder)
        
        f_layout.addWidget(QLabel("Öğrenci Seçin:")); f_layout.addWidget(self.ogrenci_combo)
        f_layout.addWidget(QLabel("Adaylık Gerekçesi:")); f_layout.addWidget(self.gerekce)
        f_layout.addWidget(btn)
        layout.addWidget(frame); layout.addStretch()

    def gonder(self):
        if self.gerekce.toPlainText().strip():
            # Yöneticiye otomatik şikayet/istek mesajı olarak iletir
            self.sistem.sikayet_olustur(self.user.id, "Öğrenci Ödül Adaylığı", f"Öğrenci: {self.ogrenci_combo.currentText()} - Gerekçe: {self.gerekce.toPlainText()}")
            QMessageBox.information(self, "Başarılı", "Adaylık talebiniz yöneticiye iletildi!")
            self.gerekce.clear()


class StudentAttendancePanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem
        self.user = user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.addWidget(QLabel("📅 Yoklama Geçmişim", objectName="Title"))

        frame = QFrame()
        frame.setObjectName("Card")
        drop_shadow(frame)
        f_layout = QVBoxLayout(frame)
        f_layout.setContentsMargins(20, 20, 20, 20)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(3)
        self.tablo.setHorizontalHeaderLabels(["Kurs Adı", "Yoklama Tarihi", "Durum Bilgisi"])
        
        # Tabloyu genişlet ve stillendir
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.setShowGrid(False)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; background-color: white; border-radius: 8px;} QHeaderView::section { background-color: #F7FAFC; color: #4A5568; font-weight: bold; border: none; border-bottom: 2px solid #E2E8F0; padding: 12px; } QTableWidget::item { padding: 12px; border-bottom: 1px solid #EDF2F7; text-align: center;}")
        
        f_layout.addWidget(self.tablo)
        layout.addWidget(frame)
        self.yukle()

    def yukle(self):
        try:
            sorgu = "SELECT c.kurs_adi, a.tarih, a.durum FROM attendance a JOIN courses c ON a.kurs_id = c.id WHERE a.ogrenci_id=? ORDER BY a.tarih DESC"
            kayitlar = self.sistem.db.calistir(sorgu, (self.user.id,), fetchall=True)
            self.tablo.setRowCount(len(kayitlar))
            for r, row in enumerate(kayitlar):
                
                # Tüm hücreleri ortala
                for c in range(3):
                    item = QTableWidgetItem(str(row[c]))
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    if c == 2:
                        if "Gelmedi" in str(row[c]):
                            item.setForeground(QColor("#E53E3E"))
                            item.setFont(QFont(FONTLAR, -1, QFont.Bold))
                        elif "Geldi" in str(row[c]):
                            item.setForeground(QColor("#38A169")) 
                            item.setFont(QFont(FONTLAR, -1, QFont.Bold))
                            
                    self.tablo.setItem(r, c, item)
        except:
            pass



class StudentDashboard(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(25)

        h_ust = QHBoxLayout(); h_ust.setSpacing(20)
        aktif = self.sistem.db.calistir("SELECT COUNT(*) FROM enrollments WHERE ogrenci_id=? AND ilerleme < 100", (self.user.id,), fetchone=True)[0]
        tamam = self.sistem.db.calistir("SELECT COUNT(*) FROM enrollments WHERE ogrenci_id=? AND ilerleme >= 100", (self.user.id,), fetchone=True)[0]
        
        h_ust.addWidget(self.kart_yap("📘 Aktif Kurslar", str(aktif), "#3182CE"))
        h_ust.addWidget(self.kart_yap("✅ Tamamlanan", str(tamam), "#38A169"))
        h_ust.addWidget(self.kart_yap("⏱️ Sistem Süresi", f"{self.user.toplam_sure_dk} dk", "#DD6B20"))
        layout.addLayout(h_ust)

        h_alt = QHBoxLayout(); h_alt.setSpacing(25)

        k_duyuru = QFrame(); k_duyuru.setObjectName("Card"); drop_shadow(k_duyuru); l_duyuru = QVBoxLayout(k_duyuru)
        l_duyuru.addWidget(QLabel("📢 Güncel Duyurular", styleSheet="font-size: 16px; font-weight: bold; color: #2D3748; padding-bottom: 5px;"))
        self.duyuru_liste = QListWidget(); self.duyuru_liste.setStyleSheet("border: none; background: transparent; outline: none; font-size:13px;")
        for d in self.sistem.duyurulari_getir()[:5]: self.duyuru_liste.addItem(f"• {d[0]} ({d[2][:10]})")
        l_duyuru.addWidget(self.duyuru_liste); h_alt.addWidget(k_duyuru, 5)

        k_plan = QFrame(); k_plan.setObjectName("Card"); drop_shadow(k_plan); l_plan = QVBoxLayout(k_plan)
        h_plan_ust = QHBoxLayout()
        h_plan_ust.addWidget(QLabel("📅 Kişisel Planlayıcı", styleSheet="font-size: 16px; font-weight: bold; color: #2D3748;"))
        l_plan.addLayout(h_plan_ust)
        
        self.takvim = QCalendarWidget(); self.takvim.setFixedHeight(220)
        self.takvim.setStyleSheet("QCalendarWidget QWidget { alternate-background-color: #F7FAFC; } QCalendarWidget QAbstractItemView:enabled { font-size: 13px; color: #4A5568; selection-background-color: #3182CE; selection-color: white; }")
        l_plan.addWidget(self.takvim)
        
        h_gorev = QHBoxLayout()
        self.gorev_input = QLineEdit(); self.gorev_input.setPlaceholderText("Görev ekle...")
        self.gorev_input.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #CBD5E0;")
        btn_ekle = SafeButton("Ekle"); btn_ekle.setStyleSheet("background-color: #3182CE; color: white; border-radius: 6px; padding: 8px 15px; font-weight: bold;")
        btn_sil = SafeButton("Sil"); btn_sil.setStyleSheet("background-color: #E53E3E; color: white; border-radius: 6px; padding: 8px 15px; font-weight: bold;")
        btn_ekle.clicked.connect(self.ajanda_gonder); btn_sil.clicked.connect(self.ajanda_sil_ui)
        h_gorev.addWidget(self.gorev_input); h_gorev.addWidget(btn_ekle); h_gorev.addWidget(btn_sil)
        l_plan.addLayout(h_gorev)
        
        self.gorev_listesi = QListWidget(); self.gorev_listesi.setStyleSheet("border: 1px solid #E2E8F0; background: #FFFFFF; border-radius: 6px; padding: 5px; outline: none;")
        self.gorev_listesi.itemDoubleClicked.connect(self.ajanda_ciz)
        l_plan.addWidget(self.gorev_listesi); h_alt.addWidget(k_plan, 5)

        layout.addLayout(h_alt); self.ajanda_yukle()

    def kart_yap(self, baslik, deger, renk):
        k = QFrame(); k.setObjectName("Card"); drop_shadow(k); l = QVBoxLayout(k); l.setContentsMargins(25, 30, 25, 30)
        lbl_baslik = QLabel(baslik); lbl_baslik.setAlignment(Qt.AlignCenter); lbl_baslik.setStyleSheet("font-size: 15px; color: #718096; font-weight: 600;")
        lbl_deger = QLabel(deger); lbl_deger.setAlignment(Qt.AlignCenter); lbl_deger.setStyleSheet(f"font-size: 36px; color: {renk}; font-weight: bold;")
        l.addWidget(lbl_baslik); l.addWidget(lbl_deger)
        return k

    def ajanda_yukle(self):
        self.gorev_listesi.clear()
        for g in self.sistem.ajanda_getir(self.user.id):
            item = QListWidgetItem(f"{g[1][-2:]}.{g[1][5:7]}.{g[1][:4]} - {g[2]}")
            item.setData(Qt.UserRole, g[0]); item.setData(Qt.UserRole + 1, g[3])
            font = QFont(FONTLAR, 11)
            if g[3] == 1: font.setStrikeOut(True); item.setForeground(QColor("#A0AEC0"))
            else: item.setForeground(QColor("#2D3748"))
            item.setFont(font); self.gorev_listesi.addItem(item)
    def ajanda_gonder(self):
        metin = self.gorev_input.text().strip()
        if metin:
            self.sistem.ajanda_ekle(self.user.id, self.takvim.selectedDate().toString("yyyy-MM-dd"), metin)
            self.gorev_input.clear(); self.ajanda_yukle()
    def ajanda_ciz(self, item):
        self.sistem.ajanda_durum_degistir(item.data(Qt.UserRole), 1 if item.data(Qt.UserRole + 1) == 0 else 0)
        self.ajanda_yukle()
    def ajanda_sil_ui(self):
        secili = self.gorev_listesi.currentItem()
        if secili and QMessageBox.question(self, "Onay", "Silinsin mi?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.sistem.ajanda_sil(secili.data(Qt.UserRole)); self.ajanda_yukle()

class StudentCourses(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("🔍 Tüm Kurslar (Katalog)", objectName="Title"))
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        self.yukle()

    def showEvent(self, event):
        self.yukle()
        super().showEvent(event)

    def yukle(self):
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget: widget.setParent(None)

        import os
        kurslar = self.sistem.tum_kurslari_getir()
        satir = 0; sutun = 0
        for k in kurslar:
            kart = QFrame()
            kart.setObjectName("Card")
            drop_shadow(kart)
            kart.setFixedSize(300, 260) 
            
            kl = QVBoxLayout(kart)
            kl.setContentsMargins(15, 15, 15, 15)
            
            img = QLabel()
            img.setFixedHeight(120)
            img.setAlignment(Qt.AlignCenter)
            
            kapak_yolu = k[7] if len(k) > 7 else ""
            if kapak_yolu and os.path.exists(kapak_yolu):
                pixmap = QPixmap(kapak_yolu).scaled(300, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                img.setPixmap(pixmap)
                img.setStyleSheet("border-radius: 8px;")
            else:
                img.setStyleSheet("background-color: #EDF2F7; border-radius: 8px;")
                img.setText("Resim Yok")
            
            lbl_baslik = QLabel(f"<b>{k[1]}</b><br><span style='font-size:12px; color:#718096;'>{k[3]}</span>") 
            lbl_baslik.setWordWrap(True)
            lbl_baslik.setAlignment(Qt.AlignCenter)
            
            h_btn = QHBoxLayout()
            h_btn.setSpacing(10)
            
            btn_kayit = SafeButton("Kayıt Ol")
            btn_kayit.setObjectName("BtnSuccess")
            btn_kayit.setCursor(Qt.PointingHandCursor)
            btn_kayit.clicked.connect(lambda ch, kid=k[0]: self.kursa_gercek_kayit_yap(kid))
            
            btn_detay = QPushButton("Detayları Gör")
            btn_detay.setCursor(Qt.PointingHandCursor)
            btn_detay.setStyleSheet("background-color: #E2E8F0; color: #2D3748; border-radius: 6px; padding: 10px; font-weight: bold;")
            btn_detay.clicked.connect(lambda ch, kid=k[0], kadi=k[1]: StudentCourseContentDialog(self.sistem, kid, kadi, self).exec_())
            
            h_btn.addWidget(btn_kayit)
            h_btn.addWidget(btn_detay)
            
            kl.addWidget(img); kl.addSpacing(10); kl.addWidget(lbl_baslik); kl.addStretch(); kl.addLayout(h_btn)
            self.grid.addWidget(kart, satir, sutun)
            
            sutun += 1
            if sutun > 2: 
                sutun = 0; satir += 1

    def kursa_gercek_kayit_yap(self, kurs_id):
        try:
            self.sistem.kursa_kaydol(self.user.id, kurs_id)
            QMessageBox.information(self, "Başarılı", "Kursa başarıyla kayıt oldunuz!")
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

# --- ÖĞRETMEN: HAFTALIK KONU VE MATERYAL YÖNETİMİ ---
class TeacherCourseManagementPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30,30,30,30)
        layout.addWidget(QLabel("📚 Haftalık Konu ve Materyal Yönetimi", objectName="Title"))
        
        tabs = QTabWidget()
        
        # Sekme 1: Haftalık Konu Yönetimi (Oturum Yerine Geldi)
        w_konu = QWidget(); l_konu = QVBoxLayout(w_konu)
        h_secim = QHBoxLayout()
        self.k_combo = QComboBox()
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): 
            self.k_combo.addItem(k[1], k[0])
        
        self.hafta_spin = QSpinBox(); self.hafta_spin.setPrefix("Hafta: "); self.hafta_spin.setRange(1, 20)
        h_secim.addWidget(QLabel("Kurs Seçin:")); h_secim.addWidget(self.k_combo)
        h_secim.addWidget(self.hafta_spin); h_secim.addStretch()
        l_konu.addLayout(h_secim)
        
        self.konu_baslik = QLineEdit(); self.konu_baslik.setPlaceholderText("Bu haftanın ana başlığı...")
        self.konu_detay = QTextEdit(); self.konu_detay.setPlaceholderText("Hafta boyunca işlenecek konular, hedefler ve detaylar...")
        
        btn_kaydet = SafeButton("Haftalık Planı Kaydet"); btn_kaydet.setObjectName("BtnSuccess")
        btn_kaydet.clicked.connect(self.plan_kaydet)
        
        l_konu.addWidget(QLabel("Konu Başlığı:")); l_konu.addWidget(self.konu_baslik)
        l_konu.addWidget(QLabel("İşlenecek Detaylar:")); l_konu.addWidget(self.konu_detay)
        l_konu.addWidget(btn_kaydet); l_konu.addStretch()
        tabs.addTab(w_konu, "📅 Haftalık Konu Yönetimi")

        # Sekme 2: Materyal Yükleme (Aynı Kaldı)
        w_mat = QWidget(); l_mat = QVBoxLayout(w_mat)
        self.mat_isim = QLineEdit(); self.mat_isim.setPlaceholderText("Materyal Adı (Örn: Hafta 1 Slayt)")
        btn_dosya = QPushButton("📎 Dosya Seç (PDF/Video)"); btn_dosya.clicked.connect(lambda: QFileDialog.getOpenFileName(self, "Dosya Seç"))
        btn_yukle = SafeButton("Materyali Yükle"); btn_yukle.setObjectName("BtnSuccess")
        btn_yukle.clicked.connect(lambda: self.mat_isim.clear() or QMessageBox.information(self, "Başarılı", "Materyal kursa yüklendi!"))
        l_mat.addWidget(QLabel("Derse Kaynak Ekle:")); l_mat.addWidget(self.mat_isim); l_mat.addWidget(btn_dosya); l_mat.addWidget(btn_yukle)
        l_mat.addStretch()
        tabs.addTab(w_mat, "📂 Materyal Yükleme")

        layout.addWidget(tabs)

    def plan_kaydet(self):
        baslik = self.konu_baslik.text().strip()
        detay = self.konu_detay.toPlainText().strip()
        if baslik and detay:
            QMessageBox.information(self, "Başarılı", f"{self.hafta_spin.text()} planı başarıyla kaydedildi!")
            self.konu_baslik.clear(); self.konu_detay.clear()
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen konu başlığı ve detayları doldurun.")


# --- ÖĞRETMEN VE ÖĞRENCİ: GELİŞMİŞ MESAJLAŞMA ---


# --- ORTAK PROFiL (UZMANLIK EKLENTİLİ) ---
class UserProfilePanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("👤 Profil Ayarları", objectName="Title"))
        
        kart = QFrame(); kart.setObjectName("Card"); drop_shadow(kart)
        kl = QVBoxLayout(kart)
        
        self.isim_input = QLineEdit(self.user.isim)
        self.eposta_input = QLineEdit(self.user.eposta)
        self.sifre_input = QLineEdit(); self.sifre_input.setPlaceholderText("Yeni şifre (Boş bırakırsanız değişmez)"); self.sifre_input.setEchoMode(QLineEdit.Password)
            
        btn_foto_ekle = SafeButton("🖼️ Profil Resmi Yükle")
        btn_foto_ekle.setStyleSheet("background-color: #F39C12; color: white; padding: 8px; border-radius: 4px;")
        btn_foto_ekle.clicked.connect(self.foto_sec)
        
        btn_foto_kaldir = SafeButton("🗑️ Profil Fotoğrafını Kaldır")
        btn_foto_kaldir.setStyleSheet("background-color: #E74C3C; color: white; padding: 8px; border-radius: 4px;")
        btn_foto_kaldir.clicked.connect(lambda: QMessageBox.information(self, "Başarılı", "Fotoğraf kaldırıldı."))
        
        h_foto = QHBoxLayout()
        h_foto.addWidget(btn_foto_ekle); h_foto.addWidget(btn_foto_kaldir); h_foto.addStretch()
        
        btn_kaydet = SafeButton("Değişiklikleri Kaydet"); btn_kaydet.setObjectName("BtnSuccess")
        btn_kaydet.clicked.connect(self.guncelle)
        
        kl.addWidget(QLabel("Ad Soyad:")); kl.addWidget(self.isim_input)
        kl.addWidget(QLabel("İletişim (E-posta):")); kl.addWidget(self.eposta_input)
        kl.addWidget(QLabel("Yeni Şifre:")); kl.addWidget(self.sifre_input)
            
        kl.addWidget(QLabel("Profil Fotoğrafı:")); kl.addLayout(h_foto)
        kl.addWidget(QLabel("")); kl.addWidget(btn_kaydet)
        
        layout.addWidget(kart); layout.addStretch()

    def foto_sec(self):
        dosya, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if dosya:
            self.user.profil_foto = dosya
            QMessageBox.information(self, "Başarılı", "Fotoğraf seçildi. Lütfen kaydet'e basın.")

    def guncelle(self):
        try:
            isim = self.isim_input.text().strip()
            eposta = self.eposta_input.text().strip()
            sifre = self.sifre_input.text() if self.sifre_input.text() else None
            if not isim: raise ValueError("İsim boş olamaz.")
            self.sistem.profil_guncelle(self.user.id, isim, eposta, self.user.profil_foto, sifre)
            self.user.isim = isim
            self.user.eposta = eposta
            QMessageBox.information(self, "Başarılı", "Profil güncellendi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

class TeacherStudentsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Öğrenci Yoklama Yönetimi (Kurs Bazlı)", objectName="Title"))
        
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.container = QWidget(); self.container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(30); self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        self.yukle()

    def yukle(self):
        for i in reversed(range(self.grid.count())): 
            w = self.grid.itemAt(i).widget()
            if w: w.setParent(None)
            
        kurslar = self.sistem.egitmen_kurslari_getir(self.user.id)
        satir = 0; sutun = 0
        for k in kurslar:
            kart = QFrame(); kart.setObjectName("Card"); drop_shadow(kart)
            kart.setMinimumSize(450, 400) 
            
            kl = QVBoxLayout(kart)
            kl.setContentsMargins(20, 20, 20, 20)
            
            h_ust = QHBoxLayout()
            v_baslik = QVBoxLayout()
            baslik = QLabel(f"<b>{k[1]}</b>", objectName="Subtitle")
            baslik.setStyleSheet("font-size: 18px; color: #1E2A38;")
            v_baslik.addWidget(baslik)
            h_ust.addLayout(v_baslik); h_ust.addStretch()
            
            # --- 1. SİYAH TAKVİM HATASI ÇÖZÜMÜ ---
            tarih_secici = QDateEdit()
            tarih_secici.setDate(QDate.currentDate())
            tarih_secici.setCalendarPopup(True)
            tarih_secici.setStyleSheet("padding: 5px; border-radius: 4px; border: 1px solid #CBD5E0; background-color: white; color: black;")
            tarih_secici.calendarWidget().setStyleSheet("QCalendarWidget QWidget { background-color: white; color: black; } QCalendarWidget QAbstractItemView:enabled { color: black; background-color: white; selection-background-color: #3182CE; selection-color: white; }")
            
            h_ust.addWidget(QLabel("Tarih: "))
            h_ust.addWidget(tarih_secici)
            kl.addLayout(h_ust); kl.addSpacing(10)
            
            # --- 2. SADELEŞTİRİLMİŞ YOKLAMA TABLOSU ---
            tablo = QTableWidget()
            tablo.setColumnCount(2)
            tablo.setHorizontalHeaderLabels(["Öğrenci Adı", "Yoklama Durumu"])
            tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tablo.verticalHeader().setVisible(False); tablo.setShowGrid(False); tablo.setAlternatingRowColors(True)
            tablo.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background-color: white; outline: none; } QHeaderView::section { background-color: #F7FAFC; color: #4A5568; font-weight: bold; border: none; border-bottom: 2px solid #E2E8F0; padding: 12px; } QTableWidget::item { padding: 5px; border-bottom: 1px solid #EDF2F7; }")
            
            sorgu = "SELECT u.id, u.isim FROM enrollments e JOIN users u ON e.ogrenci_id = u.id WHERE e.kurs_id=?"
            ogrenciler = self.sistem.db.calistir(sorgu, (k[0],), fetchall=True)
            tablo.setRowCount(len(ogrenciler))
            
            combo_listesi = []
            
            for r, ogr in enumerate(ogrenciler):
                isim_item = QTableWidgetItem(ogr[1]); isim_item.setTextAlignment(Qt.AlignCenter)
                isim_item.setFlags(Qt.ItemIsEnabled); tablo.setItem(r, 0, isim_item)
                
                d_widget = QWidget(); d_layout = QHBoxLayout(d_widget); d_layout.setContentsMargins(5,2,5,2)
                durum_combo = QComboBox()
                durum_combo.addItems(["Seçiniz...", "Geldi", "Gelmedi", "Geç Kaldı"])
                durum_combo.setStyleSheet("QComboBox { padding: 4px; border-radius: 4px; background: white; color: black; border: 1px solid #CBD5E0; } QComboBox QAbstractItemView { background: white; color: black; }")
                
                combo_listesi.append((ogr[0], durum_combo))
                d_layout.addWidget(durum_combo); tablo.setCellWidget(r, 1, d_widget)
                
            kl.addWidget(tablo)
            
            # --- YOKLAMA KAYDET BUTONU GÜNCELLEMESİ ---
            btn_kaydet = QPushButton("Yoklamayı Sisteme Kaydet")
            btn_kaydet.setCursor(Qt.PointingHandCursor)
            btn_kaydet.setFixedHeight(45)
            btn_kaydet.setStyleSheet("""
                QPushButton { 
                    background-color: #27AE60; 
                    color: white; 
                    font-weight: bold; 
                    border-radius: 6px;
                    border: none;
                }
                QPushButton:hover { background-color: #219653; }
            """)
            btn_kaydet.clicked.connect(lambda ch, kid=k[0], cl=combo_listesi, ts=tarih_secici: self.toplu_yoklama_kaydet(kid, ts.date().toString("yyyy-MM-dd"), cl))
            kl.addWidget(btn_kaydet)
            
            # Tarih değiştiğinde o günün verilerini yükle
            tarih_secici.dateChanged.connect(lambda date, kid=k[0], cl=combo_listesi: self.yoklama_verilerini_getir(kid, date.toString("yyyy-MM-dd"), cl))
            # İlk yükleme anında bugünün verilerini çek
            self.yoklama_verilerini_getir(k[0], tarih_secici.date().toString("yyyy-MM-dd"), combo_listesi)
            
            self.grid.addWidget(kart, satir, sutun)
            sutun += 1
            if sutun > 1: sutun = 0; satir += 1

    def yoklama_verilerini_getir(self, kurs_id, tarih, combo_listesi):
        gecmis_veri = self.sistem.yoklama_durumu_getir(kurs_id, tarih)
        for ogr_id, combo in combo_listesi:
            if ogr_id in gecmis_veri:
                combo.setCurrentText(gecmis_veri[ogr_id])
            else:
                combo.setCurrentIndex(0)

    def toplu_yoklama_kaydet(self, kurs_id, tarih, combo_listesi):
        kaydedilen = 0
        for ogr_id, combo in combo_listesi:
            durum = combo.currentText()
            if durum != "Seçiniz...":
                self.sistem.yoklama_kaydet(kurs_id, ogr_id, tarih, durum)
                kaydedilen += 1
        if kaydedilen > 0:
            QMessageBox.information(self, "Başarılı", f"{tarih} tarihi için {kaydedilen} öğrencinin yoklaması kaydedildi.")
        else:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek geçerli bir yoklama durumu seçilmedi.")

class TeacherStudentStatusPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("Öğrenci Durumu ve Değerlendirme", objectName="Title"))

        
        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        h_filtre = QHBoxLayout()
        self.k_combo = QComboBox()
        self.k_combo.setStyleSheet("padding: 8px; border-radius: 4px; min-width: 200px;")
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): self.k_combo.addItem(k[1], k[0])
        
        self.ogr_combo = QComboBox()
        self.ogr_combo.setStyleSheet("padding: 8px; border-radius: 4px; min-width: 200px;")
        
        self.k_combo.currentIndexChanged.connect(self.ogrencileri_yukle)
        self.ogr_combo.currentIndexChanged.connect(self.durum_yukle)
        
        h_filtre.addWidget(QLabel("<b>Kurs:</b>")); h_filtre.addWidget(self.k_combo)
        h_filtre.addSpacing(15)
        h_filtre.addWidget(QLabel("<b>Öğrenci:</b>")); h_filtre.addWidget(self.ogr_combo)
        h_filtre.addStretch()
        
        f_layout.addLayout(h_filtre)
        f_layout.addSpacing(15)
        
        self.detay_text = QTextBrowser()
        self.detay_text.setStyleSheet("border: 1px solid #E2E8F0; border-radius: 6px; padding: 10px; background: #F7FAFC; font-size: 14px;")
        f_layout.addWidget(self.detay_text)
        
        # --- HAFTALIK DEĞERLENDİRME: EKLE / GÜNCELLE / SİL ---
        h_degerlendirme = QHBoxLayout()
        self.hafta_sec = QSpinBox(); self.hafta_sec.setPrefix("Hafta "); self.hafta_sec.setRange(1, 52)
        self.hafta_sec.setStyleSheet("padding: 8px; border-radius: 4px; font-weight: bold;")
        self.hafta_sec.valueChanged.connect(self.hafta_verisi_getir)
        
        self.puan_sec = QSpinBox(); self.puan_sec.setRange(0, 100); self.puan_sec.setSuffix(" Puan")
        self.puan_sec.setStyleSheet("padding: 8px; border-radius: 4px; font-weight: bold;")
        
        self.analiz_input = QLineEdit(); self.analiz_input.setPlaceholderText("Haftalık Durum Analizi / Yorum")
        self.analiz_input.setStyleSheet("padding: 8px; border-radius: 4px; border: 1px solid #CBD5E0;")
        
        self.btn_ekle = SafeButton("Kaydet")
        self.btn_ekle.setStyleSheet("background-color: #38A169; color: white; border-radius: 4px; font-weight: bold; padding: 8px 15px;")
        self.btn_ekle.clicked.connect(self.degerlendirme_kaydet)
        
        self.btn_sil = SafeButton("Sil")
        self.btn_sil.setStyleSheet("background-color: #E53E3E; color: white; border-radius: 4px; font-weight: bold; padding: 8px 15px;")
        self.btn_sil.clicked.connect(self.degerlendirme_sil)
        self.btn_sil.hide()
        
        h_degerlendirme.addWidget(self.hafta_sec); h_degerlendirme.addWidget(self.puan_sec); h_degerlendirme.addWidget(self.analiz_input)
        h_degerlendirme.addWidget(self.btn_ekle); h_degerlendirme.addWidget(self.btn_sil)
        f_layout.addLayout(h_degerlendirme)
        
        layout.addWidget(frame)
        self.ogrencileri_yukle()

    def ogrencileri_yukle(self):
        self.ogr_combo.clear()
        kid = self.k_combo.currentData()
        if kid:
            ogrenciler = self.sistem.db.calistir("SELECT u.id, u.isim FROM enrollments e JOIN users u ON e.ogrenci_id = u.id WHERE e.kurs_id=?", (kid,), fetchall=True)
            for o in ogrenciler: self.ogr_combo.addItem(o[1], o[0])
            
            kurs = self.sistem.db.calistir("SELECT baslangic_tarihi, bitis_tarihi FROM courses WHERE id=?", (kid,), fetchone=True)
            if kurs and kurs[0] and kurs[1]:
                try:
                    bas = datetime.strptime(kurs[0], "%Y-%m-%d")
                    bit = datetime.strptime(kurs[1], "%Y-%m-%d")
                    hafta_sayisi = max(1, ((bit - bas).days // 7) + 1)
                    self.hafta_sec.setRange(1, hafta_sayisi)
                except:
                    self.hafta_sec.setRange(1, 15)
            
            self.durum_yukle()

    def durum_yukle(self):
        kid = self.k_combo.currentData(); oid = self.ogr_combo.currentData()
        if not kid or not oid:
            self.detay_text.setText("Kurs ve öğrenci seçiniz.")
            return
            
        html = "<h3>Öğrenci Durum Özeti</h3>"
        
        odevler = self.sistem.db.calistir("SELECT a.baslik, s.not_degeri, s.geribildirim FROM assignments a LEFT JOIN submissions s ON a.id = s.assignment_id AND s.ogrenci_id = ? WHERE a.kurs_id = ?", (oid, kid), fetchall=True)
        html += "<h4>Ödev Notları</h4><ul>"
        for o in odevler:
            not_deg = o[1] if o[1] is not None else "Bekliyor"
            html += f"<li><b>{o[0]}:</b> {not_deg} Puan (Yorum: {o[2] if o[2] else '-'})</li>"
        if not odevler: html += "<li>Henüz ödev yok.</li>"
        html += "</ul>"
        
        haftalar = self.sistem.db.calistir("SELECT hafta, puan, durum_analizi FROM student_points WHERE ogrenci_id=? AND kurs_id=? ORDER BY CAST(SUBSTR(hafta, 1, INSTR(hafta, '.') - 1) AS INTEGER) DESC", (oid, kid), fetchall=True)
        html += "<h4>Haftalık Değerlendirmeler</h4><ul>"
        for h in haftalar: html += f"<li><b>{h[0]}:</b> {h[1]} Puan - {h[2]}</li>"
        if not haftalar: html += "<li>Henüz değerlendirme yapılmamış.</li>"
        html += "</ul>"
        
        sinavlar = self.sistem.db.calistir("SELECT sinav1, sinav2 FROM enrollments WHERE ogrenci_id=? AND kurs_id=?", (oid, kid), fetchone=True)
        html += "<h4>Sınav Notları</h4><ul>"
        if sinavlar:
            html += f"<li><b>1. Sınav:</b> {sinavlar[0] if sinavlar[0] is not None else 'Girmedi'}</li>"
            html += f"<li><b>2. Sınav:</b> {sinavlar[1] if sinavlar[1] is not None else 'Girmedi'}</li>"
        html += "</ul>"
        
        self.detay_text.setHtml(html)
        self.hafta_verisi_getir()

    def hafta_verisi_getir(self):
        kid = self.k_combo.currentData(); oid = self.ogr_combo.currentData()
        if not kid or not oid: return
        
        hafta = f"{self.hafta_sec.value()}. Hafta"
        kayit = self.sistem.db.calistir("SELECT puan, durum_analizi FROM student_points WHERE ogrenci_id=? AND kurs_id=? AND hafta=?", (oid, kid, hafta), fetchone=True)
        
        if kayit:
            self.puan_sec.setValue(kayit[0])
            self.analiz_input.setText(kayit[1])
            self.btn_ekle.setText("Güncelle")
            self.btn_ekle.setStyleSheet("background-color: #3182CE; color: white; border-radius: 4px; font-weight: bold; padding: 8px 15px;")
            self.btn_sil.show()
        else:
            self.puan_sec.setValue(0)
            self.analiz_input.clear()
            self.btn_ekle.setText("Kaydet")
            self.btn_ekle.setStyleSheet("background-color: #38A169; color: white; border-radius: 4px; font-weight: bold; padding: 8px 15px;")
            self.btn_sil.hide()

    def degerlendirme_kaydet(self):
        kid = self.k_combo.currentData(); oid = self.ogr_combo.currentData()
        if not kid or not oid: return
        import uuid
        hafta = f"{self.hafta_sec.value()}. Hafta"
        puan = self.puan_sec.value()
        yorum = self.analiz_input.text().strip()
        try:
            var_mi = self.sistem.db.calistir("SELECT id FROM student_points WHERE ogrenci_id=? AND kurs_id=? AND hafta=?", (oid, kid, hafta), fetchone=True)
            if var_mi:
                self.sistem.db.calistir("UPDATE student_points SET puan=?, durum_analizi=? WHERE id=?", (puan, yorum, var_mi[0]))
                QMessageBox.information(self, "Başarılı", "Haftalık değerlendirme güncellendi.")
            else:
                self.sistem.db.calistir("INSERT INTO student_points (id, ogrenci_id, egitmen_id, kurs_id, hafta, puan, durum_analizi) VALUES (?, ?, ?, ?, ?, ?, ?)", (str(uuid.uuid4()), oid, self.user.id, kid, hafta, puan, yorum))
                QMessageBox.information(self, "Başarılı", "Haftalık değerlendirme eklendi.")
            self.durum_yukle()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

    def degerlendirme_sil(self):
        kid = self.k_combo.currentData(); oid = self.ogr_combo.currentData()
        if not kid or not oid: return
        hafta = f"{self.hafta_sec.value()}. Hafta"
        
        cevap = QMessageBox.question(self, "Onay", f"{hafta} değerlendirmesini silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            try:
                self.sistem.db.calistir("DELETE FROM student_points WHERE ogrenci_id=? AND kurs_id=? AND hafta=?", (oid, kid, hafta))
                QMessageBox.information(self, "Başarılı", "Değerlendirme silindi.")
                self.durum_yukle()
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))



class TeacherExamGradesPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("📝 Sınav Notu Girişi", objectName="Title"))
        
        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        h_filtre = QHBoxLayout()
        self.k_combo = QComboBox()
        self.k_combo.setStyleSheet("padding: 8px; border-radius: 4px; min-width: 200px;")
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): self.k_combo.addItem(k[1], k[0])
        self.k_combo.currentIndexChanged.connect(self.yukle)
        h_filtre.addWidget(QLabel("<b>Kurs Seçimi:</b>")); h_filtre.addWidget(self.k_combo); h_filtre.addStretch()
        f_layout.addLayout(h_filtre)
        f_layout.addSpacing(15)
        
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Öğrenci Adı", "1. Sınav Notu", "2. Sınav Notu", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none; }")
        f_layout.addWidget(self.tablo)
        layout.addWidget(frame)
        self.yukle()

    def yukle(self):
        kid = self.k_combo.currentData()
        if not kid: return
        self.tablo.setRowCount(0)
        ogrenciler = self.sistem.db.calistir("SELECT u.id, u.isim, e.sinav1, e.sinav2 FROM enrollments e JOIN users u ON e.ogrenci_id = u.id WHERE e.kurs_id=?", (kid,), fetchall=True)
        self.tablo.setRowCount(len(ogrenciler))
        for r, ogr in enumerate(ogrenciler):
            self.tablo.setItem(r, 0, QTableWidgetItem(ogr[1]))
            
            s1_spin = QSpinBox(); s1_spin.setRange(0, 100)
            if ogr[2] is not None: s1_spin.setValue(ogr[2])
            
            s2_spin = QSpinBox(); s2_spin.setRange(0, 100)
            if ogr[3] is not None: s2_spin.setValue(ogr[3])
            
            self.tablo.setCellWidget(r, 1, s1_spin)
            self.tablo.setCellWidget(r, 2, s2_spin)
            
            btn_kaydet = SafeButton("Kaydet")
            btn_kaydet.setStyleSheet("background-color: #3182CE; color: white; border-radius: 4px; padding: 5px; font-weight:bold;")
            btn_kaydet.clicked.connect(lambda ch, oid=ogr[0], s1=s1_spin, s2=s2_spin: self.not_kaydet(kid, oid, s1.value(), s2.value()))
            self.tablo.setCellWidget(r, 3, btn_kaydet)

    def not_kaydet(self, kurs_id, ogrenci_id, s1, s2):
        self.sistem.sinav_notu_kaydet(ogrenci_id, kurs_id, 1, s1)
        self.sistem.sinav_notu_kaydet(ogrenci_id, kurs_id, 2, s2)
        QMessageBox.information(self, "Başarılı", "Sınav notları kaydedildi.")

class TeacherAnnouncementsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("📢 Kurs Bazlı Duyurular", objectName="Title"))
        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        self.kurs_combo = QComboBox()
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): self.kurs_combo.addItem(k[1], k[0])
        
        self.d_baslik = QLineEdit(); self.d_baslik.setPlaceholderText("Duyuru Başlığı")
        self.d_mesaj = QTextEdit(); self.d_mesaj.setPlaceholderText("Mesajınız...")
        btn = SafeButton("Seçili Kursa Duyuru Gönder"); btn.setObjectName("BtnSuccess")
        btn.clicked.connect(self.gercek_duyuru_gonder)
        
        f_layout.addWidget(QLabel("Hedef Kurs:")); f_layout.addWidget(self.kurs_combo)
        f_layout.addWidget(self.d_baslik); f_layout.addWidget(self.d_mesaj); f_layout.addWidget(btn)
        layout.addWidget(frame); layout.addStretch()

    def gercek_duyuru_gonder(self):
        kid = self.kurs_combo.currentData()
        k_ad = self.kurs_combo.currentText()
        b = self.d_baslik.text().strip()
        m = self.d_mesaj.toPlainText().strip()
        
        if kid and b and m:
            self.sistem.duyuru_ekle(f"[{k_ad}] {b}", m)
            QMessageBox.information(self, "Başarılı", "Duyuru kurs öğrencilerine iletildi ve sisteme kaydedildi!")
            self.d_baslik.clear()
            self.d_mesaj.clear()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")

class TeacherComplaintsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("🎧 Kursuma Gelen Şikayet/İstekler", objectName="Title"))

        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Öğrenci", "Kategori", "Açıklama"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        f_layout.addWidget(self.tablo)
        layout.addWidget(frame)
        self.yukle()

    def yukle(self):
        # Sadece bu öğretmenin kurslarındaki öğrencilerin şikayetlerini getirmek için mock (tasarım amaçlı boş)
        self.tablo.setRowCount(0)

# --- YENİLENMİŞ ÖĞRETMEN (EĞİTMEN) PANELLERİ ---

class TeacherDashboard(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(25)
        
        h_ust = QHBoxLayout(); h_ust.setSpacing(25)
        aktif_kurs, toplam_ogr, bekleyen, gelir = self.sistem.egitmen_gelismis_dashboard(self.user.id)
        
        h_ust.addWidget(self.kart_yap("📘 Aktif Kurslarım", str(aktif_kurs), "#3182CE"))
        h_ust.addWidget(self.kart_yap("👥 Toplam Öğrenci", str(toplam_ogr), "#38A169"))
        h_ust.addWidget(self.kart_yap("⏳ Onay Bekleyen", str(bekleyen), "#DD6B20"))
        layout.addLayout(h_ust)
        
        h_alt = QHBoxLayout(); h_alt.setSpacing(25)
        
        k_risk = QFrame(); k_risk.setObjectName("Card"); drop_shadow(k_risk); l_risk = QVBoxLayout(k_risk)
        l_risk.setContentsMargins(25, 25, 25, 25)
        
        lbl_risk_title = QLabel("⚠️ Desteğe İhtiyacı Olan Öğrenciler (Ort. < 50)")
        lbl_risk_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #E53E3E; padding-bottom: 10px;")
        l_risk.addWidget(lbl_risk_title)
        
        self.tablo_risk = QTableWidget()
        self.tablo_risk.setColumnCount(3)
        self.tablo_risk.setHorizontalHeaderLabels(["Öğrenci Adı", "Kurs Adı", "Puan Ort."])
        self.tablo_risk.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_risk.verticalHeader().setVisible(False)
        self.tablo_risk.setShowGrid(False)
        self.tablo_risk.setAlternatingRowColors(True)
        
        # TABLO DÜZENLEME VE ODAKLANMA İPTAL EDİLDİ
        self.tablo_risk.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo_risk.setFocusPolicy(Qt.NoFocus)
        self.tablo_risk.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablo_risk.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background-color: white; outline: none; } QHeaderView::section { background-color: #F7FAFC; color: #4A5568; font-weight: bold; border: none; border-bottom: 2px solid #E2E8F0; padding: 12px; } QTableWidget::item { padding: 10px; border-bottom: 1px solid #EDF2F7; }")
        
        riskli_ogr = self.sistem.egitmen_riskli_ogrenciler(self.user.id)
        self.tablo_risk.setRowCount(len(riskli_ogr))
        for r, row in enumerate(riskli_ogr):
            item_isim = QTableWidgetItem(str(row[0]))
            item_isim.setTextAlignment(Qt.AlignCenter)
            self.tablo_risk.setItem(r, 0, item_isim)
            
            item_kurs = QTableWidgetItem(str(row[1]))
            item_kurs.setTextAlignment(Qt.AlignCenter)
            self.tablo_risk.setItem(r, 1, item_kurs)
            
            puan_item = QTableWidgetItem(f"{row[2]}")
            puan_item.setTextAlignment(Qt.AlignCenter)
            puan_item.setForeground(QColor("#E53E3E"))
            puan_item.setFont(QFont(FONTLAR, -1, QFont.Bold))
            self.tablo_risk.setItem(r, 2, puan_item)
            
        l_risk.addWidget(self.tablo_risk)
        h_alt.addWidget(k_risk, 5)
        
        k_plan = QFrame(); k_plan.setObjectName("Card"); drop_shadow(k_plan); l_plan = QVBoxLayout(k_plan)
        l_plan.setContentsMargins(25, 25, 25, 25)
        
        h_plan_ust = QHBoxLayout()
        lbl_plan_title = QLabel("📅 Ajanda ve Planlama")
        lbl_plan_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2D3748;")
        h_plan_ust.addWidget(lbl_plan_title)
        
        btn_pdf = QPushButton("PDF Al"); btn_pdf.setCursor(Qt.PointingHandCursor)
        btn_pdf.setStyleSheet("background: transparent; color: #3182CE; font-weight: bold; border: none; font-size: 13px;")
        btn_pdf.clicked.connect(lambda: QMessageBox.information(self, "Bilgi", "Planlarınız PDF olarak dışa aktarılacaktır."))
        h_plan_ust.addStretch(); h_plan_ust.addWidget(btn_pdf)
        l_plan.addLayout(h_plan_ust)
        
        self.takvim = QCalendarWidget()
        self.takvim.setFixedHeight(220)
        self.takvim.setStyleSheet("QCalendarWidget QWidget { alternate-background-color: #F7FAFC; } QCalendarWidget QToolButton { background-color: transparent; color: #2D3748; font-weight: bold; font-size: 14px; } QCalendarWidget QAbstractItemView:enabled { font-size: 13px; color: #4A5568; selection-background-color: #3182CE; selection-color: white; }")
        l_plan.addWidget(self.takvim)
        
        h_gorev = QHBoxLayout()
        self.gorev_input = QLineEdit(); self.gorev_input.setPlaceholderText("Seçili tarihe plan ekle...")
        self.gorev_input.setStyleSheet("padding: 10px; border-radius: 8px; border: 1px solid #CBD5E0; background-color: #F7FAFC; color: #2D3748;")
        btn_ekle = SafeButton("Ekle"); btn_ekle.setCursor(Qt.PointingHandCursor)
        btn_ekle.setStyleSheet("background-color: #3182CE; color: white; border-radius: 8px; padding: 10px 20px; font-weight: bold;")
        btn_ekle.clicked.connect(self.ajanda_gonder)
        h_gorev.addWidget(self.gorev_input); h_gorev.addWidget(btn_ekle)
        l_plan.addLayout(h_gorev)
        
        self.gorev_listesi = QListWidget()
        self.gorev_listesi.setStyleSheet("border: 1px solid #E2E8F0; background: #FFFFFF; border-radius: 8px; padding: 8px; outline: none;")
        self.gorev_listesi.itemDoubleClicked.connect(self.ajanda_ciz)
        l_plan.addWidget(self.gorev_listesi)
        
        h_islem = QHBoxLayout()
        btn_sil = SafeButton("Seçili Görevi Sil")
        btn_sil.setCursor(Qt.PointingHandCursor)
        btn_sil.setStyleSheet("background-color: #E53E3E; color: white; border-radius: 8px; padding: 8px 15px; font-weight: bold; font-size: 13px;")
        btn_sil.clicked.connect(self.ajanda_sil_ui)
        h_islem.addStretch(); h_islem.addWidget(btn_sil)
        l_plan.addLayout(h_islem)
        
        h_alt.addWidget(k_plan, 5)
        layout.addLayout(h_alt)
        self.ajanda_yukle()

    def kart_yap(self, baslik, deger, renk):
        k = QFrame(); k.setObjectName("Card"); drop_shadow(k); l = QVBoxLayout(k)
        l.setContentsMargins(25, 30, 25, 30)
        lbl_baslik = QLabel(baslik)
        lbl_baslik.setAlignment(Qt.AlignCenter)
        lbl_baslik.setStyleSheet("font-size: 15px; color: #718096; font-weight: 600;")
        lbl_deger = QLabel(deger)
        lbl_deger.setAlignment(Qt.AlignCenter)
        lbl_deger.setStyleSheet(f"font-size: 36px; color: {renk}; font-weight: bold;")
        l.addWidget(lbl_baslik); l.addWidget(lbl_deger)
        return k

    def ajanda_yukle(self):
        self.gorev_listesi.clear()
        for g in self.sistem.ajanda_getir(self.user.id):
            item = QListWidgetItem(f"{g[1][-2:]}.{g[1][5:7]}.{g[1][:4]} - {g[2]}")
            item.setData(Qt.UserRole, g[0])
            item.setData(Qt.UserRole + 1, g[3])
            font = QFont(FONTLAR, 11)
            if g[3] == 1:
                font.setStrikeOut(True)
                item.setForeground(QColor("#A0AEC0"))
            else:
                item.setForeground(QColor("#2D3748"))
            item.setFont(font)
            self.gorev_listesi.addItem(item)

    def ajanda_gonder(self):
        metin = self.gorev_input.text().strip()
        if not metin: return
        tarih = self.takvim.selectedDate().toString("yyyy-MM-dd")
        self.sistem.ajanda_ekle(self.user.id, tarih, metin)
        self.gorev_input.clear()
        self.ajanda_yukle()

    def ajanda_ciz(self, item):
        aid = item.data(Qt.UserRole)
        mevcut_durum = item.data(Qt.UserRole + 1)
        yeni_durum = 1 if mevcut_durum == 0 else 0
        self.sistem.ajanda_durum_degistir(aid, yeni_durum)
        self.ajanda_yukle()

    def ajanda_sil_ui(self):
        secili = self.gorev_listesi.currentItem()
        if not secili: return QMessageBox.warning(self, "Uyarı", "Lütfen silmek için listeden bir görev seçin.")
        if QMessageBox.question(self, "Onay", "Seçili görevi tamamen silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.sistem.ajanda_sil(secili.data(Qt.UserRole))
            self.ajanda_yukle()

class TeacherCourseManagementPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30,30,30,30)
        layout.addWidget(QLabel("📚 Müfredat ve Materyal Yönetimi", objectName="Title"))
        
        h_secim = QHBoxLayout()
        h_secim.addWidget(QLabel("<b>İşlem Yapılacak Kurs:</b>"))
        self.k_combo = QComboBox()
        for k in self.sistem.egitmen_kurslari_getir(self.user.id): 
            self.k_combo.addItem(k[1], k[0])
        self.k_combo.currentIndexChanged.connect(self.icerik_yukle)
        h_secim.addWidget(self.k_combo); h_secim.addStretch()
        layout.addLayout(h_secim)
        
        self.h_alt = QHBoxLayout(); self.h_alt.setSpacing(20)
        
        # SOL: Form (Başlangıçta kapalı, üstte aç/kapa butonu)
        self.k_form = QFrame(); self.k_form.setObjectName("Card"); drop_shadow(self.k_form); l_form = QVBoxLayout(self.k_form)
        
        h_form_ust = QHBoxLayout()
        h_form_ust.addWidget(QLabel("İçerik Ekle / Güncelle", objectName="Subtitle"))
        btn_kapat = QPushButton("❌ Kapat")
        btn_kapat.setStyleSheet("background: transparent; color: #E53E3E; border: none; font-weight: bold; font-size:12px;")
        btn_kapat.setCursor(Qt.PointingHandCursor)
        btn_kapat.clicked.connect(self.k_form.hide)
        h_form_ust.addStretch(); h_form_ust.addWidget(btn_kapat)
        l_form.addLayout(h_form_ust)

        self.hafta_spin = QSpinBox(); self.hafta_spin.setPrefix("Hafta: "); self.hafta_spin.setRange(1, 20)
        self.konu_baslik = QLineEdit(); self.konu_baslik.setPlaceholderText("Konu Başlığı...")
        self.konu_detay = QTextEdit(); self.konu_detay.setPlaceholderText("İşlenecek alt başlıklar, detaylar...")
        
        h_dosya = QHBoxLayout()
        self.dosya_yolu = QLineEdit(); self.dosya_yolu.setReadOnly(True); self.dosya_yolu.setPlaceholderText("Seçilen dosya")
        btn_dosya = QPushButton("📄 Seç"); btn_dosya.clicked.connect(self.dosya_sec)
        h_dosya.addWidget(self.dosya_yolu); h_dosya.addWidget(btn_dosya)
        
        btn_kaydet = SafeButton("Kaydet"); btn_kaydet.setObjectName("BtnSuccess"); btn_kaydet.clicked.connect(self.kaydet)
        
        l_form.addWidget(self.hafta_spin); l_form.addWidget(self.konu_baslik); l_form.addWidget(self.konu_detay)
        l_form.addWidget(QLabel("Ders Materyali (İsteğe Bağlı):")); l_form.addLayout(h_dosya)
        l_form.addWidget(btn_kaydet); l_form.addStretch()
        
        self.h_alt.addWidget(self.k_form, 4)
        self.k_form.hide() # Açılışta form gizli
        
        # SAĞ: Liste
        k_liste = QFrame(); k_liste.setObjectName("Card"); drop_shadow(k_liste); l_liste = QVBoxLayout(k_liste)
        
        h_liste_ust = QHBoxLayout()
        h_liste_ust.addWidget(QLabel("Mevcut Müfredat (Düzenlemek için satıra çift tıklayın)", objectName="Subtitle"))
        btn_yeni = SafeButton("+ Yeni Hafta Ekle")
        btn_yeni.setCursor(Qt.PointingHandCursor)
        btn_yeni.setStyleSheet("background-color: #3182CE; color: white; border-radius: 4px; padding: 5px 10px; font-weight:bold;")
        btn_yeni.clicked.connect(self.yeni_hafta_ac)
        h_liste_ust.addStretch(); h_liste_ust.addWidget(btn_yeni)
        l_liste.addLayout(h_liste_ust)

        self.tablo = QTableWidget(); self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Hafta", "Konu", "Materyal", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.verticalHeader().setVisible(False); self.tablo.setShowGrid(False); self.tablo.setAlternatingRowColors(True)
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.itemDoubleClicked.connect(self.duzenle_forma_al)
        l_liste.addWidget(self.tablo)
        
        self.h_alt.addWidget(k_liste, 6)
        layout.addLayout(self.h_alt); self.icerik_yukle()

    def yeni_hafta_ac(self):
        self.konu_baslik.clear(); self.konu_detay.clear(); self.dosya_yolu.clear()
        self.hafta_spin.setValue(self.tablo.rowCount() + 1)
        self.k_form.show()

    def dosya_sec(self):
        dosya, _ = QFileDialog.getOpenFileName(self, "Materyal Seç", "", "Tüm Dosyalar (*)")
        if dosya: self.dosya_yolu.setText(dosya)

    def kaydet(self):
        kid = self.k_combo.currentData()
        if not kid: return QMessageBox.warning(self, "Hata", "Kurs seçmediniz.")
        if not self.konu_baslik.text().strip(): return QMessageBox.warning(self, "Hata", "Konu başlığı zorunludur.")
        
        try:
            self.sistem.haftalik_plan_ekle(kid, self.hafta_spin.value(), self.konu_baslik.text().strip(), self.konu_detay.toPlainText().strip(), self.dosya_yolu.text())
            QMessageBox.information(self, "Başarılı", "İçerik kaydedildi/güncellendi!")
            self.k_form.hide()
            self.icerik_yukle()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

    def icerik_yukle(self):
        kid = self.k_combo.currentData()
        if not kid: return
        
        # --- Kurs süresine göre maksimum hafta sınırını belirle ---
        kurs = self.sistem.db.calistir("SELECT baslangic_tarihi, bitis_tarihi FROM courses WHERE id=?", (kid,), fetchone=True)
        if kurs and kurs[0] and kurs[1]:
            try:
                bas = datetime.strptime(kurs[0], "%Y-%m-%d")
                bit = datetime.strptime(kurs[1], "%Y-%m-%d")
                hafta_sayisi = max(1, ((bit - bas).days // 7) + 1)
                self.hafta_spin.setRange(1, hafta_sayisi)
            except:
                self.hafta_spin.setRange(1, 20)
                
        dersler = self.sistem.kursa_ait_dersleri_getir(kid)
        self.tablo.setRowCount(len(dersler))
        for r, d in enumerate(dersler):
            hafta_item = QTableWidgetItem(f"{d[1]}. Hafta")
            hafta_item.setData(Qt.UserRole, d)
            self.tablo.setItem(r, 0, hafta_item)
            self.tablo.setItem(r, 1, QTableWidgetItem(d[2]))
            
            mat_item = QTableWidgetItem("Yüklendi" if d[4] else "-")
            mat_item.setForeground(QColor("#27AE60") if d[4] else QColor("#A0AEC0"))
            self.tablo.setItem(r, 2, mat_item)
            
            btn_sil = SafeButton("Sil"); btn_sil.setObjectName("BtnError")
            btn_sil.setCursor(Qt.PointingHandCursor)
            btn_sil.clicked.connect(lambda ch, did=d[0]: self.sil(did))
            self.tablo.setCellWidget(r, 3, btn_sil)

    def duzenle_forma_al(self, item):
        row = item.row()
        ders_verisi = self.tablo.item(row, 0).data(Qt.UserRole)
        if ders_verisi:
            self.hafta_spin.setValue(ders_verisi[1])
            self.konu_baslik.setText(ders_verisi[2])
            self.konu_detay.setText(ders_verisi[3] if ders_verisi[3] else "")
            self.dosya_yolu.setText(ders_verisi[4] if ders_verisi[4] else "")
            self.k_form.show()

    def sil(self, did):
        cevap = QMessageBox.question(self, "Onay", "Bu hafta içeriğini silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.sistem.ders_sil(did)
            self.icerik_yukle()



class StudentComplaintPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("📬 İstek ve Şikayet Bildirimi", objectName="Title"))
        
        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        self.kategori = QComboBox()
        self.kategori.addItems(["Müfredat Talebi", "Eğitmen Şikayeti", "Teknik Destek", "Materyal Talebi", "Diğer"])
        
        self.aciklama = QTextEdit(); self.aciklama.setPlaceholderText("Lütfen talebinizi detaylıca buraya yazın...")
        btn = SafeButton("Talebi Yönetime İlet"); btn.setObjectName("BtnSuccess")
        btn.clicked.connect(self.gonder)
        
        f_layout.addWidget(QLabel("Kategori:")); f_layout.addWidget(self.kategori)
        f_layout.addWidget(QLabel("Açıklama:")); f_layout.addWidget(self.aciklama); f_layout.addWidget(btn)
        layout.addWidget(frame)
        
        # Geçmiş Talepler Tablosu
        layout.addSpacing(20); layout.addWidget(QLabel("📜 Geçmiş Taleplerim", objectName="Subtitle"))
        self.tablo = QTableWidget(); self.tablo.setColumnCount(3)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Kategori", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()

    def gonder(self):
        desc = self.aciklama.toPlainText().strip()
        if desc:
            tid = self.sistem.sikayet_olustur(self.user.id, self.kategori.currentText(), desc)
            QMessageBox.information(self, "Başarılı", f"Talebiniz iletildi. Takip No: {tid}")
            self.aciklama.clear(); self.yukle()

    def yukle(self):
        self.tablo.setRowCount(0)
        veriler = self.sistem.ogrenci_sikayet_gecmisi(self.user.id)
        self.tablo.setRowCount(len(veriler))
        for r, d in enumerate(veriler):
            self.tablo.setItem(r, 0, QTableWidgetItem(str(d[4])[:10]))
            self.tablo.setItem(r, 1, QTableWidgetItem(d[1]))
            self.tablo.setItem(r, 2, QTableWidgetItem(d[3]))

class AdminComplaintsAndAnnouncements(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("⚠️ Gelen İstek ve Şikayet Yönetimi", objectName="Title"))
        
        self.tablo = QTableWidget(); self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Öğrenci", "Kategori", "Durum", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tablo); self.yukle()

    def yukle(self):
        self.tablo.setRowCount(0)
        veriler = self.sistem.admin_sikayetleri_getir()
        self.tablo.setRowCount(len(veriler))
        for r, d in enumerate(veriler):
            self.tablo.setItem(r, 0, QTableWidgetItem(d[0][:6]))
            self.tablo.setItem(r, 1, QTableWidgetItem(d[1]))
            self.tablo.setItem(r, 2, QTableWidgetItem(d[2]))
            self.tablo.setItem(r, 3, QTableWidgetItem(d[4]))
            btn = SafeButton("Detay/Yanıtla")
            btn.clicked.connect(lambda ch, sid=d[0], desc=d[3]: self.yanitla(sid, desc))
            self.tablo.setCellWidget(r, 4, btn)

    def yanitla(self, sid, desc):
        QMessageBox.information(self, "Şikayet Detayı", f"Öğrenci Notu:\n{desc}")
        cevap, ok = QInputDialog.getText(self, "Yanıtla", "Öğrenciye iletilecek yanıt:")
        if ok and cevap:
            self.sistem.sikayet_durum_guncelle(sid, f"Çözüldü: {cevap}")
            self.yukle()

class StudentMessagePanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30,30,30,30)
        
        # BAŞLIKTAN SAAT SINIRI UYARISI SİLİNDİ
        layout.addWidget(QLabel("💬 Öğretmenlere Mesaj", objectName="Title"))
        
        k_mesaj = QFrame(); k_mesaj.setObjectName("Card"); drop_shadow(k_mesaj); l_mesaj = QVBoxLayout(k_mesaj)
        h_ust = QHBoxLayout(); h_ust.addWidget(QLabel("Kiminle iletişime geçmek istiyorsunuz?"))
        self.hedef_combo = QComboBox()
        
        sorgu = "SELECT DISTINCT u.id, u.isim FROM enrollments e JOIN courses c ON e.kurs_id = c.id JOIN users u ON c.egitmen_id = u.id WHERE e.ogrenci_id = ?"
        hocalar = self.sistem.db.calistir(sorgu, (self.user.id,), fetchall=True)
        for h in hocalar: self.hedef_combo.addItem(f"Öğretmen: {h[1]}", h[0])
        
        self.hedef_combo.currentIndexChanged.connect(self.mesajlari_yukle)
        h_ust.addWidget(self.hedef_combo); h_ust.addStretch(); l_mesaj.addLayout(h_ust)
        
        self.mesaj_alani = QTextBrowser(); self.mesaj_alani.setOpenExternalLinks(True)
        self.mesaj_alani.setOpenLinks(False)
        self.mesaj_alani.anchorClicked.connect(lambda url: ImageViewer(url.toString().replace("file:///", ""), self).exec_())
        self.mesaj_alani.setStyleSheet("background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 6px;")
        l_mesaj.addWidget(self.mesaj_alani)
        
        h_alt = QHBoxLayout(); self.girdi = QLineEdit(); self.girdi.setPlaceholderText("Mesajınızı yazın...")
        btn_resim = QPushButton("📸 Görsel"); btn_resim.clicked.connect(self.resim_ekle)
        btn_gonder = SafeButton("Gönder"); btn_gonder.setObjectName("BtnSuccess")
        btn_gonder.clicked.connect(self.gonder)
        h_alt.addWidget(btn_resim); h_alt.addWidget(self.girdi); h_alt.addWidget(btn_gonder); l_mesaj.addLayout(h_alt)
        layout.addWidget(k_mesaj); self.mesajlari_yukle()

    def resim_ekle(self):
        dosya, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Resim (*.png *.jpg *.jpeg)")
        if dosya:
            alici_id = self.hedef_combo.currentData()
            if not alici_id: return QMessageBox.warning(self, "Uyarı", "Lütfen kişi seçin.")
            html_img = f"<br><a href='{dosya}'><img src='{dosya}' width='200'></a><br>"
            try:
                self.sistem.mesaj_gonder(self.user.id, alici_id, html_img)
                self.mesajlari_yukle() 
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))

    def mesajlari_yukle(self):
        self.mesaj_alani.clear()
        alici_id = self.hedef_combo.currentData()
        if not alici_id: return
        mesajlar = self.sistem.mesajlari_getir(self.user.id, alici_id)
        for m in mesajlar:
            gonderen = "Siz" if m[0] == self.user.id else "Eğitmen"
            renk = "#27AE60" if m[0] == self.user.id else "#1E2A38"
            self.mesaj_alani.append(f"<b style='color: {renk};'>{gonderen}:</b> {m[1]}<br>")

    def gonder(self):
        alici_id = self.hedef_combo.currentData()
        metin = self.girdi.text().strip()
        if alici_id and metin:
            try:
                self.sistem.mesaj_gonder(self.user.id, alici_id, metin)
                self.girdi.clear(); self.mesajlari_yukle()
            except Exception as e: QMessageBox.warning(self, "Hata", str(e))

class TeacherMessagePanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30,30,30,30)
        layout.addWidget(QLabel("💬 İletişim ve Mesajlaşma Merkezi", objectName="Title"))
        k_mesaj = QFrame(); k_mesaj.setObjectName("Card"); drop_shadow(k_mesaj); l_mesaj = QVBoxLayout(k_mesaj)
        
        h_ust = QHBoxLayout(); h_ust.addWidget(QLabel("Kiminle iletişime geçmek istiyorsunuz?"))
        self.hedef_combo = QComboBox()
        
        # Admin'i ekle
        admin = self.sistem.db.calistir("SELECT id FROM users WHERE rol='Admin' LIMIT 1", fetchone=True)
        if admin: self.hedef_combo.addItem("🏢 Yönetici (Admin)", admin[0])
        
        # Kendi öğrencilerini ekle
        ogrenciler = self.sistem.egitmen_ogrencileri_detayli(self.user.id)
        eklenenler = set()
        for ogr in ogrenciler:
            if ogr[0] not in eklenenler:
                self.hedef_combo.addItem(f"👤 Öğrenci: {ogr[1]}", ogr[0])
                eklenenler.add(ogr[0])
                     
        self.hedef_combo.currentIndexChanged.connect(self.mesajlari_yukle)
        h_ust.addWidget(self.hedef_combo); h_ust.addStretch(); l_mesaj.addLayout(h_ust)
        
        self.mesaj_alani = QTextBrowser(); self.mesaj_alani.setOpenExternalLinks(True)
        self.mesaj_alani.setOpenLinks(False)
        self.mesaj_alani.anchorClicked.connect(lambda url: ImageViewer(url.toString().replace("file:///", ""), self).exec_())
        self.mesaj_alani.setStyleSheet("background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px; border-radius: 6px;")
        l_mesaj.addWidget(self.mesaj_alani)
        
        h_alt = QHBoxLayout(); self.girdi = QLineEdit(); self.girdi.setPlaceholderText("Mesajınızı yazın...")
        btn_resim = QPushButton("📷 Görsel"); btn_resim.clicked.connect(self.resim_ekle)
        btn_gonder = SafeButton("Gönder"); btn_gonder.setObjectName("BtnSuccess")
        btn_gonder.clicked.connect(self.gonder)
        h_alt.addWidget(btn_resim); h_alt.addWidget(self.girdi); h_alt.addWidget(btn_gonder); l_mesaj.addLayout(h_alt)
        layout.addWidget(k_mesaj); self.mesajlari_yukle()

    def resim_ekle(self):
        dosya, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Resim (*.png *.jpg *.jpeg)")
        if dosya:
            alici_id = self.hedef_combo.currentData()
            if not alici_id: return QMessageBox.warning(self, "Uyarı", "Lütfen kişi seçin.")
            html_img = f"<br><a href='{dosya}'><img src='{dosya}' width='200'></a><br>"
            try:
                self.sistem.mesaj_gonder(self.user.id, alici_id, html_img)
                self.mesajlari_yukle() 
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))

    def mesajlari_yukle(self):
        self.mesaj_alani.clear()
        alici_id = self.hedef_combo.currentData()
        if not alici_id: return
        mesajlar = self.sistem.mesajlari_getir(self.user.id, alici_id)
        for m in mesajlar:
            gonderen = "Siz" if m[0] == self.user.id else "Kullanıcı"
            renk = "#4A90E2" if m[0] == self.user.id else "#1E2A38"
            self.mesaj_alani.append(f"<b style='color: {renk};'>{gonderen}:</b> {m[1]}<br>")

    def gonder(self):
        alici_id = self.hedef_combo.currentData()
        metin = self.girdi.text().strip()
        if alici_id and metin:
            try:
                self.sistem.mesaj_gonder(self.user.id, alici_id, metin)
                self.girdi.clear(); self.mesajlari_yukle()
            except Exception as e: QMessageBox.warning(self, "Hata", str(e))

class AdminMessagePanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("💬 Eğitmenlerle İletişim (Yönetici)", objectName="Title"))
        
        k_mesaj = QFrame(); k_mesaj.setObjectName("Card"); drop_shadow(k_mesaj); l_mesaj = QVBoxLayout(k_mesaj)
        h_ust = QHBoxLayout(); h_ust.addWidget(QLabel("Kiminle iletişime geçmek istiyorsunuz?"))
        self.hedef_combo = QComboBox()
        
        hocalar = self.sistem.db.calistir("SELECT id, isim FROM users WHERE rol='Teacher'", fetchall=True)
        for h in hocalar: self.hedef_combo.addItem(f"Eğitmen: {h[1]}", h[0])
            
        self.hedef_combo.currentIndexChanged.connect(self.mesajlari_yukle)
        h_ust.addWidget(self.hedef_combo); h_ust.addStretch(); l_mesaj.addLayout(h_ust)
        
        self.mesaj_alani = QTextBrowser(); self.mesaj_alani.setStyleSheet("background: #F8FAFC; padding: 10px; border-radius: 6px;")
        self.mesaj_alani.setOpenLinks(False)
        self.mesaj_alani.anchorClicked.connect(lambda url: ImageViewer(url.toString().replace("file:///", ""), self).exec_())
        l_mesaj.addWidget(self.mesaj_alani)
        
        h_alt = QHBoxLayout(); self.girdi = QLineEdit(); self.girdi.setPlaceholderText("Mesajınızı yazın...")
        btn_resim = QPushButton("📷 Görsel"); btn_resim.clicked.connect(self.resim_ekle)
        btn_gonder = SafeButton("Gönder"); btn_gonder.setObjectName("BtnSuccess")
        btn_gonder.clicked.connect(self.gonder)
        h_alt.addWidget(btn_resim); h_alt.addWidget(self.girdi); h_alt.addWidget(btn_gonder); l_mesaj.addLayout(h_alt)
        layout.addWidget(k_mesaj); self.mesajlari_yukle()

    def resim_ekle(self):
        dosya, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Resim (*.png *.jpg *.jpeg)")
        if dosya:
            alici_id = self.hedef_combo.currentData()
            if not alici_id: return QMessageBox.warning(self, "Uyarı", "Lütfen kişi seçin.")
            html_img = f"<br><a href='{dosya}'><img src='{dosya}' width='200'></a><br>"
            try:
                self.sistem.mesaj_gonder(self.user.id, alici_id, html_img)
                self.mesajlari_yukle() 
            except Exception as e:
                QMessageBox.warning(self, "Hata", str(e))

    def mesajlari_yukle(self):
        self.mesaj_alani.clear()
        alici_id = self.hedef_combo.currentData()
        if not alici_id: return
        mesajlar = self.sistem.mesajlari_getir(self.user.id, alici_id)
        for m in mesajlar:
            gonderen = "Siz" if m[0] == self.user.id else "Eğitmen"
            renk = "#E67E22" if m[0] == self.user.id else "#1E2A38"
            self.mesaj_alani.append(f"<b style='color: {renk};'>{gonderen}:</b> {m[1]}<br>")

    def gonder(self):
        alici_id = self.hedef_combo.currentData()
        metin = self.girdi.text().strip()
        if alici_id and metin:
            try:
                self.sistem.mesaj_gonder(self.user.id, alici_id, metin)
                self.girdi.clear(); self.mesajlari_yukle()
            except Exception as e: QMessageBox.warning(self, "Hata", str(e))
# --- YENİLENMİŞ YÖNETİCİ (ADMIN) PANELLERİ ---


class AdminStudentOfMonthPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(20)
        layout.addWidget(QLabel("🏆 Ayın Öğrencisi ve Ödül Yönetimi", objectName="Title"))

        kart_ust = QFrame(); kart_ust.setObjectName("Card"); drop_shadow(kart_ust); l_ust = QVBoxLayout(kart_ust)
        l_ust.addWidget(QLabel("📊 Puanlara ve Sistem Süresine Göre Sıralama", objectName="Subtitle"))
        
        self.tablo_sirala = QTableWidget(); self.tablo_sirala.setColumnCount(3)
        self.tablo_sirala.setHorizontalHeaderLabels(["Öğrenci Adı", "Puan / Durum", "İşlem"])
        self.tablo_sirala.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_sirala.verticalHeader().setVisible(False)
        self.tablo_sirala.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo_sirala.setFocusPolicy(Qt.NoFocus)
        self.tablo_sirala.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablo_sirala.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none;} QHeaderView::section { background-color: #F7FAFC; color: #4A5568; font-weight: bold; border: none; border-bottom: 2px solid #E2E8F0; padding: 12px; }")
        l_ust.addWidget(self.tablo_sirala)
        
        btn_oto = SafeButton("Sistemi Tara ve Rozet Ver")
        btn_oto.setStyleSheet("background-color: #3182CE; color: white; padding: 10px; font-weight:bold; border-radius: 6px;")
        btn_oto.clicked.connect(self.otomatik_belirle)
        l_ust.addWidget(btn_oto)
        layout.addWidget(kart_ust)

        kart_alt = QFrame(); kart_alt.setObjectName("Card"); drop_shadow(kart_alt); l_alt = QVBoxLayout(kart_alt)
        l_alt.addWidget(QLabel("🎁 Ödül Geçmişi ve Teslimat Durumu", objectName="Subtitle"))
        
        self.tablo_gecmis = QTableWidget(); self.tablo_gecmis.setColumnCount(4)
        self.tablo_gecmis.setHorizontalHeaderLabels(["Tarih", "Öğrenci", "Ödül", "Durum / Aksiyon"])
        self.tablo_gecmis.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo_gecmis.verticalHeader().setVisible(False)
        self.tablo_gecmis.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo_gecmis.setFocusPolicy(Qt.NoFocus)
        self.tablo_gecmis.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablo_gecmis.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none;} QHeaderView::section { background-color: #F7FAFC; color: #4A5568; font-weight: bold; border: none; border-bottom: 2px solid #E2E8F0; padding: 12px; }")
        l_alt.addWidget(self.tablo_gecmis)
        layout.addWidget(kart_alt)
        
        self.yukle()

    def yukle(self):
        self.tablo_sirala.setRowCount(0)
        
        # 1. Normal Öğretmen Puanları
        sorgu_sirala = "SELECT u.isim, AVG(sp.puan) as ort, u.id FROM student_points sp JOIN users u ON sp.ogrenci_id = u.id GROUP BY u.id ORDER BY ort DESC LIMIT 4"
        veriler = self.sistem.db.calistir(sorgu_sirala, fetchall=True)
        gosterilecekler = [(v[0], f"{float(v[1]):.1f} Puan", v[2]) for v in veriler]
        
        # 2. Sistem Otomatik Adayı (Puanı En Yüksek Olan)
        top_sure = self.sistem.db.calistir("SELECT u.isim, u.id FROM student_points sp JOIN users u ON sp.ogrenci_id = u.id GROUP BY u.id ORDER BY AVG(sp.puan) DESC LIMIT 1", fetchone=True)
        if top_sure:
            zaten_var = False
            for i, v in enumerate(gosterilecekler):
                if v[2] == top_sure[1]: # Öğrenci zaten puanla listeye girdiyse
                    gosterilecekler[i] = (v[0] + " 🌟 (Sistem Adayı)", v[1], v[2])
                    zaten_var = True
                    break
            if not zaten_var: # Listede yoksa en başa ekle
                gosterilecekler.insert(0, (top_sure[0] + " 🌟 (Sistem Adayı)", "Yüksek Sistem Süresi", top_sure[1]))
        
        self.tablo_sirala.setRowCount(len(gosterilecekler))
        for r, row in enumerate(gosterilecekler):
            isim_item = QTableWidgetItem(str(row[0])); isim_item.setTextAlignment(Qt.AlignCenter)
            puan_item = QTableWidgetItem(str(row[1])); puan_item.setTextAlignment(Qt.AlignCenter)
            self.tablo_sirala.setItem(r, 0, isim_item)
            self.tablo_sirala.setItem(r, 1, puan_item)
            
            odul_var_mi = self.sistem.db.calistir("SELECT id FROM badges WHERE user_id=? AND badge_name LIKE 'Ayın Öğrencisi%'", (row[2],), fetchone=True)
            b_widget = QWidget(); b_layout = QHBoxLayout(b_widget); b_layout.setContentsMargins(0,0,0,0)
            btn = QPushButton()
            if odul_var_mi:
                btn.setText("Ödül Tanımlandı")
                btn.setStyleSheet("background: #A0AEC0; color:white; border-radius:4px; padding:8px; font-weight:bold;")
                btn.setEnabled(False) 
            else:
                btn.setText("Ödül Tanımla")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet("background: #3182CE; color:white; border-radius:4px; padding:8px; font-weight:bold;")
                btn.clicked.connect(lambda ch, uid=row[2], unam=row[0]: self.odul_tanimla(uid, unam))
                
            b_layout.addWidget(btn, alignment=Qt.AlignCenter)
            self.tablo_sirala.setCellWidget(r, 2, b_widget)

        self.tablo_gecmis.setRowCount(0)
        sorgu_gecmis = "SELECT b.id, b.tarih, u.isim, b.badge_name FROM badges b JOIN users u ON b.user_id = u.id ORDER BY b.tarih DESC"
        gecmis = self.sistem.db.calistir(sorgu_gecmis, fetchall=True)
        self.tablo_gecmis.setRowCount(len(gecmis))
        for r, g in enumerate(gecmis):
            tar_item = QTableWidgetItem(str(g[1])[:10]); tar_item.setTextAlignment(Qt.AlignCenter)
            isim_item = QTableWidgetItem(str(g[2])); isim_item.setTextAlignment(Qt.AlignCenter)
            odul_item = QTableWidgetItem(str(g[3]).replace(" - Teslim Edildi", "")); odul_item.setTextAlignment(Qt.AlignCenter)
            
            self.tablo_gecmis.setItem(r, 0, tar_item)
            self.tablo_gecmis.setItem(r, 1, isim_item)
            self.tablo_gecmis.setItem(r, 2, odul_item)
            
            b_widget = QWidget(); b_layout = QHBoxLayout(b_widget); b_layout.setContentsMargins(0,0,0,0)
            if "Teslim Edildi" in str(g[3]):
                lbl = QLabel("✅ Ödül Verildi")
                lbl.setStyleSheet("color: #38A169; font-weight: bold; font-size: 13px;")
                b_layout.addWidget(lbl, alignment=Qt.AlignCenter)
            else:
                btn_ver = QPushButton("Ödülü Teslim Et")
                btn_ver.setCursor(Qt.PointingHandCursor)
                btn_ver.setStyleSheet("background: #F39C12; color:white; border-radius:4px; padding:8px; font-weight:bold;")
                btn_ver.clicked.connect(lambda ch, bid=g[0], bname=g[3]: self.odul_teslim_et(bid, bname))
                b_layout.addWidget(btn_ver, alignment=Qt.AlignCenter)
                
            self.tablo_gecmis.setCellWidget(r, 3, b_widget)

    def odul_tanimla(self, uid, unam):
        import uuid
        self.sistem.db.calistir("INSERT INTO badges (id, user_id, badge_name) VALUES (?, ?, ?)", (str(uuid.uuid4()), uid, "Ayın Öğrencisi (Kitap Ödülü)"))
        mesaj = "Tebrikler! Ayın öğrencisi seçildiniz ve Kitap Ödülü kazandınız. Lütfen ödülünüzü almak için idareye (yöneticiye) gidiniz."
        self.sistem.mesaj_gonder(self.user.id, uid, mesaj)
        QMessageBox.information(self, "Ödül Tanımlandı", f"Ödül Tanımlandı!\n\nÖğrenciye kitap ödülü tanımlandı ve bilgilendirme mesajı gönderildi.")
        self.yukle()

    def odul_teslim_et(self, badge_id, badge_name):
        yeni_ad = badge_name + " - Teslim Edildi"
        self.sistem.db.calistir("UPDATE badges SET badge_name=? WHERE id=?", (yeni_ad, badge_id))
        QMessageBox.information(self, "Başarılı", "Ödül öğrenciye teslim edildi olarak işaretlendi.")
        self.yukle()

    def otomatik_belirle(self):
        try:
            self.sistem.ayin_ogrencisini_belirle()
            QMessageBox.information(self, "Başarılı", "Sistem tarandı ve en başarılı öğrenciye rozeti verildi!")
            self.yukle()
        except Exception as e:
            QMessageBox.warning(self, "Hata", str(e))

class AdminBookRequestsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("📚 Kitap Talepleri", objectName="Title"))

        h_layout = QHBoxLayout()

        # Sol: Liste
        sol_frame = QFrame(); sol_frame.setObjectName("Card"); drop_shadow(sol_frame); sol_layout = QVBoxLayout(sol_frame)
        sol_layout.addWidget(QLabel("Gelen Talepler", objectName="Subtitle"))
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(4)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Öğrenci", "Talep", "Durum"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        sol_layout.addWidget(self.tablo)
        h_layout.addWidget(sol_frame, 6)

        # Sağ: Detay ve Aksiyon
        sag_frame = QFrame(); sag_frame.setObjectName("Card"); drop_shadow(sag_frame); sag_layout = QVBoxLayout(sag_frame)
        sag_layout.addWidget(QLabel("Durum Güncelle (Seçili Talep İçin)", objectName="Subtitle"))
        
        btn_onay = SafeButton("Talebi Onayla"); btn_onay.setObjectName("BtnSuccess")
        btn_temin = SafeButton("Temin Edildi (Kargoda)"); btn_temin.setStyleSheet("background-color: #3498DB; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        btn_teslim = SafeButton("Teslim Edildi"); btn_teslim.setObjectName("BtnWarning")
        btn_iptal = SafeButton("Talebi İptal Et"); btn_iptal.setObjectName("BtnError")
        
        for b in [btn_onay, btn_temin, btn_teslim, btn_iptal]:
            b.clicked.connect(lambda ch, txt=b.text(): QMessageBox.information(self, "İşlem", f"Talep durumu güncellendi: {txt}"))
            sag_layout.addWidget(b)
        
        sag_layout.addStretch()
        h_layout.addWidget(sag_frame, 4)

        layout.addLayout(h_layout)

class AdminBookCatalogPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("📖 Kitap Kataloğu", objectName="Title"))

        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        
        h = QHBoxLayout()
        self.k_ad = QLineEdit(); self.k_ad.setPlaceholderText("Kitap Adı")
        self.k_isbn = QLineEdit(); self.k_isbn.setPlaceholderText("ISBN")
        btn_ekle = SafeButton("Kataloğa Ekle"); btn_ekle.setObjectName("BtnSuccess")
        btn_ekle.clicked.connect(lambda: self.k_ad.clear() or self.k_isbn.clear() or QMessageBox.information(self, "Eklendi", "Kitap sisteme eklendi!"))
        h.addWidget(self.k_ad); h.addWidget(self.k_isbn); h.addWidget(btn_ekle)
        f_layout.addLayout(h)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(3)
        self.tablo.setHorizontalHeaderLabels(["Kitap Adı", "ISBN", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        f_layout.addWidget(self.tablo)
        layout.addWidget(frame)

class AdminSystemLogsPanel(QWidget):
    def __init__(self, sistem, user):
        super().__init__()
        self.sistem = sistem; self.user = user
        layout = QVBoxLayout(self); layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(20)
        
        h = QHBoxLayout()
        h.addWidget(QLabel("⚙️ Sistem Logları (Hareketlilik)", objectName="Title"))
        h.addStretch()
        btn_csv = SafeButton("📥 CSV İndir"); btn_csv.setCursor(Qt.PointingHandCursor)
        btn_csv.setStyleSheet("background-color: #DD6B20; color: white; border-radius: 8px; padding: 8px 15px; font-weight: bold;")
        btn_csv.clicked.connect(self.csv_aktar)
        h.addWidget(btn_csv)
        layout.addLayout(h)

        frame = QFrame(); frame.setObjectName("Card"); drop_shadow(frame); f_layout = QVBoxLayout(frame)
        self.tablo = QTableWidget(); self.tablo.setColumnCount(3)
        self.tablo.setHorizontalHeaderLabels(["Tarih", "Kullanıcı", "İşlem / Aksiyon"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.verticalHeader().setVisible(False); self.tablo.setShowGrid(False); self.tablo.setAlternatingRowColors(True)
        self.tablo.setStyleSheet("QTableWidget { border: none; background-color: white; } QHeaderView::section { background-color: #F7FAFC; color: #4A5568; font-weight: bold; border: none; padding: 12px; border-bottom: 2px solid #E2E8F0; }")
        f_layout.addWidget(self.tablo)
        layout.addWidget(frame)
        self.yukle()

    def yukle(self):
        self.tablo.setRowCount(0)
        try:
            loglar = self.sistem.loglari_getir()
            self.tablo.setRowCount(len(loglar))
            for r, row in enumerate(loglar):
                self.tablo.setItem(r, 0, QTableWidgetItem(str(row[0])[:16]))
                self.tablo.setItem(r, 1, QTableWidgetItem(str(row[1])))
                self.tablo.setItem(r, 2, QTableWidgetItem(str(row[2])))
        except: pass

    def csv_aktar(self):
        import csv
        dosya, _ = QFileDialog.getSaveFileName(self, "CSV Kaydet", "sistem_loglari.csv", "CSV Dosyaları (*.csv)")
        if dosya:
            try:
                with open(dosya, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Tarih", "Kullanici", "Aksiyon"])
                    for row in range(self.tablo.rowCount()):
                        writer.writerow([self.tablo.item(row, 0).text(), self.tablo.item(row, 1).text(), self.tablo.item(row, 2).text()])
                QMessageBox.information(self, "Başarılı", "Loglar CSV formatında bilgisayarınıza kaydedildi!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Kaydedilemedi: {str(e)}")

# --- ŞİKAYET VE İSTEK PANELLERİ ---
class StudentCourseContentDialog(QDialog):
    def __init__(self, sistem, kurs_id, kurs_adi, parent=None):
        super().__init__(parent)
        self.sistem = sistem
        self.setWindowTitle(f"Kurs Detayı: {kurs_adi}")
        self.setFixedSize(750, 750)  # Pencere yüksekliğini artırdık
        self.setStyleSheet(parent.window().styleSheet() if parent else "")
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"📚 {kurs_adi} - Detaylar ve Müfredat", objectName="Title"))
        
        kurs = self.sistem.kurs_detay_getir(kurs_id)
        if kurs:
            bilgi_kutu = QFrame(); drop_shadow(bilgi_kutu)
            bilgi_kutu.setStyleSheet("background-color: #F7FAFC; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0;")
            bilgi_kutu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # Kutu esnemesini sabitledik
            l_bilgi = QVBoxLayout(bilgi_kutu)
            
            l_bilgi.addWidget(QLabel(f"<b>Eğitmen:</b> {kurs[13]}  |  <b>Kategori:</b> {kurs[3]}"))
            l_bilgi.addWidget(QLabel(f"<b>Süreç:</b> {kurs[5]}  ile  {kurs[6]} Arası"))
            l_bilgi.addWidget(QLabel(f"<b>Zorluk:</b> {kurs[11] if kurs[11] else 'Belirtilmedi'}  |  <b>Kapasite:</b> {kurs[7]} Kişi"))
            l_bilgi.addWidget(QLabel(f"<b>Ücret:</b> {int(kurs[10]) if kurs[10] else 0} ₺"))
            
            lbl_aciklama = QLabel(f"<b>Kurs Hakkında:</b><br>{kurs[4]}")
            lbl_aciklama.setWordWrap(True)
            scroll_aciklama = QScrollArea()
            scroll_aciklama.setWidgetResizable(True); scroll_aciklama.setWidget(lbl_aciklama); scroll_aciklama.setFixedHeight(100)
            scroll_aciklama.setStyleSheet("border: none; background: transparent;")
            l_bilgi.addWidget(scroll_aciklama)
            
            # Üst kutuya stretch=0 veriyoruz ki gereksiz uzamasın
            layout.addWidget(bilgi_kutu, 0)

        layout.addSpacing(10)
        layout.addWidget(QLabel("📋 Haftalık Müfredat / Konular", objectName="Subtitle"))
        
        self.tablo = QTableWidget(); self.tablo.setColumnCount(2)
        self.tablo.setHorizontalHeaderLabels(["Hafta", "İşlenecek Konu ve Detaylar"])
        self.tablo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) 
        self.tablo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) 
        self.tablo.verticalHeader().setVisible(False); self.tablo.setShowGrid(False); self.tablo.setAlternatingRowColors(True)
        self.tablo.setWordWrap(True)
        self.tablo.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tablo.verticalHeader().setDefaultSectionSize(75)
        self.tablo.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background-color: white; } QHeaderView::section { background-color: #EDF2F7; color: #2D3748; font-weight: bold; border: none; border-bottom: 2px solid #CBD5E0; padding: 12px; } QTableWidget::item { padding: 10px; border-bottom: 1px solid #EDF2F7; }")

        # Tabloya stretch=1 veriyoruz ki tüm boşluğu o kaplasın
        layout.addWidget(self.tablo, 1)
        
        dersler = self.sistem.kursa_ait_dersleri_getir(kurs_id)
        if not dersler:
            self.tablo.setRowCount(1)
            self.tablo.setItem(0, 1, QTableWidgetItem("Eğitmen henüz müfredat planı eklememiş."))
        else:
            self.tablo.setRowCount(len(dersler))
            for r, d in enumerate(dersler):
                item_hafta = QTableWidgetItem(f"{d[1]}. Hafta")
                item_hafta.setTextAlignment(Qt.AlignCenter)
                self.tablo.setItem(r, 0, item_hafta)
                
                detay_item = QTableWidgetItem()
                detay_item.setText(f"Konu: {d[2]}\nNotlar: {d[3] if d[3] else '-'}")
                self.tablo.setItem(r, 1, detay_item)
                
        h_btn = QHBoxLayout()
        h_btn.addStretch()
        btn_kapat = SafeButton("Kapat")
        btn_kapat.setCursor(Qt.PointingHandCursor)
        btn_kapat.setStyleSheet("background-color: #E53E3E; color: white; border-radius: 6px; padding: 8px 25px; font-weight: bold;")
        btn_kapat.clicked.connect(self.accept)
        h_btn.addWidget(btn_kapat)
        layout.addLayout(h_btn)

class AdminPaymentsPanel(QWidget):
    def __init__(self, sistem):
        super().__init__()
        self.sistem = sistem
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("💳 Ödeme Onayları", objectName="Title"))
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(["Kayıt ID", "Öğrenci", "Kurs", "Fiyat", "Durum", "İşlem"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablo.setFocusPolicy(Qt.NoFocus)
        self.tablo.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablo.setStyleSheet("QTableWidget { border: 1px solid #E2E8F0; border-radius: 8px; background: white; outline: none;} QHeaderView::section { background-color: #EDF2F7; padding: 8px; font-weight: bold; border: none; border-bottom: 2px solid #CBD5E0; }")
        layout.addWidget(self.tablo)
        self.yukle()

    def yukle(self):
        self.tablo.setRowCount(0)
        sorgu = """
            SELECT e.id, u.isim, c.kurs_adi, c.fiyat, e.odeme_durumu
            FROM enrollments e
            JOIN users u ON e.ogrenci_id = u.id
            JOIN courses c ON e.kurs_id = c.id
            ORDER BY e.odeme_durumu ASC, e.kayit_tarihi DESC
        """
        kayitlar = self.sistem.db.calistir(sorgu, fetchall=True)
        self.tablo.setRowCount(len(kayitlar))
        for r, row in enumerate(kayitlar):
            self.tablo.setItem(r, 0, QTableWidgetItem(str(row[0])[:8]))
            self.tablo.setItem(r, 1, QTableWidgetItem(str(row[1])))
            self.tablo.setItem(r, 2, QTableWidgetItem(str(row[2])))
            self.tablo.setItem(r, 3, QTableWidgetItem(f"{row[3]} TL"))
            durum = "Ödendi" if row[4] == 1 else "Bekliyor"
            durum_item = QTableWidgetItem(durum)
            durum_item.setForeground(QColor("#27AE60") if row[4] == 1 else QColor("#E67E22"))
            self.tablo.setItem(r, 4, durum_item)

            btn = SafeButton("Onayla")
            if row[4] == 1:
                btn.setDisabled(True)
                btn.setText("Onaylandı")
            else:
                btn.setObjectName("BtnSuccess")
                btn.clicked.connect(lambda ch, eid=row[0]: self.onayla(eid))
            self.tablo.setCellWidget(r, 5, btn)

    def onayla(self, eid):
        self.sistem.db.calistir("UPDATE enrollments SET odeme_durumu=1 WHERE id=?", (eid,))
        QMessageBox.information(self, "Başarılı", "Öğrencinin ödemesi onaylandı!")
        self.yukle()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Hata yakalayıcı (Crashes prevention)
    def catch_exceptions(t, val, tb):
        QMessageBox.critical(None, "Kritik Sistem Hatası", f"Bir hata oluştu:\n{val}")
    sys.excepthook = catch_exceptions
    
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_())
