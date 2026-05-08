import sqlite3
import uuid
import hashlib
import bcrypt
from datetime import datetime, timedelta
import re
from abc import ABC, abstractmethod


def sifre_hashle(sifre: str) -> str:
    """Verilen düz metin şifreyi bcrypt algoritmasıyla güvenli biçimde hashler."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(sifre.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def sifre_dogrula(girilen_sifre: str, db_hash: str) -> bool:
    """Kullanıcının girdiği şifreyi veritabanındaki hash ile karşılaştırır.
    Geriye dönük uyumluluk için SHA-256 fallback içerir."""
    try:
        return bcrypt.checkpw(girilen_sifre.encode('utf-8'), db_hash.encode('utf-8'))
    except ValueError:
        # Eski SHA-256 hash formatı için geriye dönük doğrulama
        eski_hash = hashlib.sha256(girilen_sifre.encode('utf-8')).hexdigest()
        return eski_hash == db_hash


def email_gecerli_mi(eposta: str) -> bool:
    """RFC standartlarına uygun e-posta formatı doğrulaması yapar."""
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(regex, eposta) is not None


def sifre_guclu_mu(sifre: str) -> bool:
    """Şifrenin minimum güvenlik gereksinimlerini karşılayıp karşılamadığını denetler.
    Kural: En az 6 karakter, en az bir harf, en az bir rakam."""
    if len(sifre) < 6: return False
    if not any(c.isalpha() for c in sifre): return False
    if not any(c.isdigit() for c in sifre): return False
    return True


def isim_gecerli_mi(isim: str) -> bool:
    """İsim alanının yalnızca rakamlardan oluşmadığını ve boş olmadığını doğrular."""
    if not isim.strip() or isim.replace(" ", "").isdigit(): return False
    return True


def gecmis_tarih_mi(tarih_str: str, format: str = "%Y-%m-%d") -> bool:
    """Verilen tarih dizesinin bugünden önce olup olmadığını kontrol eder.
    Geçersiz format durumunda True döndürerek formu bloke eder."""
    try:
        tarih = datetime.strptime(tarih_str, format).date()
        if tarih < datetime.now().date():
            return True
        return False
    except ValueError:
        return True

# --- VERİTABANI YÖNETİMİ ---
class DatabaseManager:
    """SQLite veritabanı bağlantısını ve tüm ham SQL işlemlerini yöneten katman.

    Parametreler:
        db_name (str): Kullanılacak SQLite dosyasının adı.
    """

    def __init__(self, db_name="online_kurs.db"):
        self.db_name = db_name
        self.baglanti_kur()

    def baglanti_kur(self):
        """Veritabanı bağlantısını açar, şema migrasyonlarını ve tablo kurulumunu tetikler."""
        try:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.tablolari_olustur()
            try: self.calistir("ALTER TABLE enrollments ADD COLUMN sinav1 INTEGER DEFAULT NULL")
            except: pass
            try: self.calistir("ALTER TABLE enrollments ADD COLUMN sinav2 INTEGER DEFAULT NULL")
            except: pass
        except sqlite3.Error as e:
            print(f"Kritik Hata: Veritabanı bağlantısı kurulamadı. {e}")

    def calistir(self, sorgu, parametreler=(), fetchall=False, fetchone=False, commit=True):
        """Parametreli SQL sorgusunu güvenli biçimde çalıştırır.

        Parametreler:
            sorgu (str): Çalıştırılacak SQL ifadesi.
            parametreler (tuple): Sorgu parametreleri (SQL enjeksiyonuna karşı koruma sağlar).
            fetchall (bool): Tüm satırları liste olarak döndürür.
            fetchone (bool): Yalnızca ilk satırı döndürür.
            commit (bool): Başarılı işlemden sonra otomatik commit yapar.

        Döndürür:
            list | tuple | bool: İstenen çıktı formatı ya da işlem başarısını gösteren True.
        """
        try:
            self.cursor.execute(sorgu, parametreler)
            if commit:
                self.conn.commit()
            if fetchall:
                return self.cursor.fetchall()
            if fetchone:
                return self.cursor.fetchone()
            return True
        except sqlite3.Error as e:
            print(f"Veritabanı Hatası: {e}")
            if commit:
                self.conn.rollback()
            raise e

    def tablolari_olustur(self):
        """Tüm veritabanı tablolarını ve eksik sütunları idempotent biçimde oluşturur.
        ALTER TABLE ifadeleri try/except bloğuyla sarılır; sütun zaten mevcutsa hata yok sayılır.
        """
        try:
            try: self.calistir("ALTER TABLE lessons ADD COLUMN video_link TEXT")
            except: pass
            try: self.calistir("ALTER TABLE lessons ADD COLUMN notes TEXT")
            except: pass
            try: self.calistir("ALTER TABLE courses ADD COLUMN fiyat REAL DEFAULT 0")
            except: pass
            try: self.calistir("ALTER TABLE courses ADD COLUMN zorluk TEXT DEFAULT 'Başlangıç'")
            except: pass
            try: self.calistir("ALTER TABLE courses ADD COLUMN kapak_resmi TEXT")
            except: pass
            try: self.calistir("ALTER TABLE enrollments ADD COLUMN odeme_durumu INTEGER DEFAULT 0")
            except: pass
            self.calistir('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    isim TEXT NOT NULL,
                    eposta TEXT UNIQUE NOT NULL,
                    sifre TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    profil_foto TEXT,
                    sec_soru TEXT,
                    sec_cevap TEXT,
                    is_active INTEGER DEFAULT 1,
                    son_giris TIMESTAMP,
                    kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    toplam_sure_dk INTEGER DEFAULT 0,
                    uzmanlik TEXT,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS courses (
                    id TEXT PRIMARY KEY,
                    kurs_adi TEXT NOT NULL,
                    egitmen_id TEXT NOT NULL,
                    kategori TEXT,
                    aciklama TEXT,
                    baslangic_tarihi TEXT,
                    bitis_tarihi TEXT,
                    kapasite INTEGER,
                    onay_durumu INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY(egitmen_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS lessons (
                    id TEXT PRIMARY KEY,
                    kurs_id TEXT NOT NULL,
                    hafta_no INTEGER,
                    konu TEXT NOT NULL,
                    icerik_pdf TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY(kurs_id) REFERENCES courses(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS assignments (
                    id TEXT PRIMARY KEY,
                    kurs_id TEXT NOT NULL,
                    baslik TEXT NOT NULL,
                    aciklama TEXT,
                    son_tarih TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY(kurs_id) REFERENCES courses(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id TEXT PRIMARY KEY,
                    assignment_id TEXT NOT NULL,
                    ogrenci_id TEXT NOT NULL,
                    dosya_yolu TEXT,
                    not_degeri REAL,
                    geribildirim TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(assignment_id) REFERENCES assignments(id),
                    FOREIGN KEY(ogrenci_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS exams (
                    id TEXT PRIMARY KEY,
                    kurs_id TEXT NOT NULL,
                    baslik TEXT NOT NULL,
                    sure_dk INTEGER,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY(kurs_id) REFERENCES courses(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    gonderen_id TEXT NOT NULL,
                    alici_id TEXT NOT NULL,
                    metin TEXT NOT NULL,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    okundu INTEGER DEFAULT 0,
                    FOREIGN KEY(gonderen_id) REFERENCES users(id),
                    FOREIGN KEY(alici_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS students (
                    user_id TEXT PRIMARY KEY,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS teachers (
                    user_id TEXT PRIMARY KEY,
                    uzmanlik TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id TEXT PRIMARY KEY,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS schedules (
                    id TEXT PRIMARY KEY,
                    kurs_id TEXT NOT NULL,
                    gun TEXT,
                    baslangic_saat TEXT,
                    bitis_saat TEXT,
                    FOREIGN KEY(kurs_id) REFERENCES courses(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS enrollments (
                    id TEXT PRIMARY KEY,
                    ogrenci_id TEXT NOT NULL,
                    kurs_id TEXT NOT NULL,
                    durum INTEGER DEFAULT 1,
                    ilerleme INTEGER DEFAULT 0,
                    kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(ogrenci_id) REFERENCES users(id),
                    FOREIGN KEY(kurs_id) REFERENCES courses(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS performance_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    aksiyon TEXT,
                    sure_dk INTEGER DEFAULT 0,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS badges (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    badge_name TEXT NOT NULL,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS evaluations (
                    id TEXT PRIMARY KEY,
                    ogrenci_id TEXT NOT NULL,
                    egitmen_id TEXT NOT NULL,
                    guclu_yonler TEXT,
                    eksikler TEXT,
                    hafta INTEGER
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS complaints (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    aciklama TEXT NOT NULL,
                    durum TEXT DEFAULT 'Bekliyor',
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS exam_results (
                    id TEXT PRIMARY KEY,
                    exam_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    score REAL,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(exam_id) REFERENCES exams(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS announcements (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    message TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS complaints (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    aciklama TEXT NOT NULL,
                    durum TEXT DEFAULT 'Bekliyor',
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS personal_agenda (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    tarih DATE NOT NULL,
                    metin TEXT NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            self.calistir('''
                CREATE TABLE IF NOT EXISTS student_points (
                    id TEXT PRIMARY KEY,
                    ogrenci_id TEXT,
                    egitmen_id TEXT,
                    kurs_id TEXT,
                    hafta TEXT,
                    puan INTEGER,
                    durum_analizi TEXT,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        except sqlite3.Error as e:
            print(f"Tablo oluşturma hatası: {e}")


class User(ABC):
    """Tüm kullanıcı tiplerinin türediği soyut temel sınıf.

    Parametreler:
        id (str): UUID formatında benzersiz tanımlayıcı.
        isim (str): Kullanıcının tam adı.
        eposta (str): Giriş kimlik bilgisi olarak kullanılan e-posta adresi.
        rol (str): Sistemdeki rolü ('Student', 'Teacher', 'Admin').
        profil_foto (str): Profil fotoğrafı dosya yolu.
        toplam_sure_dk (int): Birikimli oturum süresi (dakika).
    """

    def __init__(self, id, isim, eposta, rol, profil_foto="", toplam_sure_dk=0):
        self.id = id
        self.isim = isim
        self.eposta = eposta
        self.rol = rol
        self.profil_foto = profil_foto
        self.toplam_sure_dk = toplam_sure_dk
    @abstractmethod
    def get_dashboard_info(self) -> str:
        """Kullanıcının panel özet bilgisini döndürür."""
        pass


class Student(User):
    """Kurslara kayıt olup eğitim alan öğrenci kullanıcı tipi."""

    def __init__(self, id, isim, eposta, profil_foto="", toplam_sure_dk=0):
        super().__init__(id, isim, eposta, "Student", profil_foto, toplam_sure_dk)

    def get_dashboard_info(self):
        return f"Öğrenci Paneli: {self.isim}"


class Teacher(User):
    """Kurs oluşturan ve öğrencileri değerlendiren eğitmen kullanıcı tipi."""

    def __init__(self, id, isim, eposta, profil_foto="", toplam_sure_dk=0):
        super().__init__(id, isim, eposta, "Teacher", profil_foto, toplam_sure_dk)

    def get_dashboard_info(self):
        return f"Eğitmen Paneli: {self.isim}"


class Admin(User):
    """Sistemi yöneten, kullanıcı ve kurs onaylarını gerçekleştiren yönetici kullanıcı tipi."""

    def __init__(self, id, isim, eposta, profil_foto="", toplam_sure_dk=0):
        super().__init__(id, isim, eposta, "Admin", profil_foto, toplam_sure_dk)

    def get_dashboard_info(self):
        return f"Yönetici Paneli: {self.isim}"


class CourseSystem:
    """Uygulamanın tüm iş mantığını kapsayan merkezi kontrolcü katmanı.
    DatabaseManager üzerinden veritabanı işlemleri yürütür.
    """

    def __init__(self):
        self.db = DatabaseManager()
        self._admin_olustur()

    def _admin_olustur(self):
        """Sistemde yönetici hesabı yoksa varsayılan admin kaydını otomatik oluşturur."""
        try:
            admin_var = self.db.calistir("SELECT id FROM users WHERE eposta='admin@onlinekurs.com'", fetchone=True)
            if not admin_var:
                uid = str(uuid.uuid4())
                sifre = sifre_hashle("Admin123!")
                self.db.calistir("INSERT INTO users (id, isim, eposta, sifre, rol, is_active) VALUES (?, ?, ?, ?, ?, ?)",
                                 (uid, "Sistem Yöneticisi", "admin@onlinekurs.com", sifre, "Admin", 1))
                self.db.calistir("INSERT INTO admins (user_id) VALUES (?)", (uid,))
        except Exception as e:
            print(f"Admin oluşturma hatası: {e}")

    def giris_yap(self, eposta, sifre):
        """Kimlik doğrulaması yapar; başarısız girilen deneme sayısını takip eder.

        5 hatalı girişten sonra hesabı 5 dakika kilitler.

        Döndürür:
            User: Doğrulanan kullanıcının rolüne uygun nesne (Student/Teacher/Admin).

        Hata:
            ValueError: Kimlik bilgileri hatalı veya hesap kilitli/pasif ise.
        """
        try:
            if not eposta or not sifre:
                raise ValueError("E-posta ve şifre boş olamaz.")
                            
            # HATA BURADAYDI: toplam_sure_dk sütunu SQL sorgusuna eklendi
            user_data = self.db.calistir("SELECT id, isim, eposta, rol, profil_foto, is_active, sifre, failed_attempts, locked_until, toplam_sure_dk FROM users WHERE eposta=?", (eposta,), fetchone=True)
            if not user_data:
                raise ValueError("Hatalı e-posta veya şifre.")
                        
            user_id, isim, db_eposta, rol, profil_foto, is_active, db_sifre, failed_attempts, locked_until_str, toplam_sure_dk = user_data
            
            failed_attempts = failed_attempts or 0
            if locked_until_str:
                locked_until = datetime.strptime(locked_until_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() < locked_until:
                    kalan_dk = int((locked_until - datetime.now()).total_seconds() // 60) + 1
                    raise ValueError(f"Çok fazla hatalı giriş yaptınız. Hesabınız güvenlik amacıyla kilitlendi.\nLütfen {kalan_dk} dakika bekleyin.")
                else:
                    self.db.calistir("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?", (user_id,))
                    failed_attempts = 0
                    
            if not sifre_dogrula(sifre, db_sifre):
                yeni_hata = failed_attempts + 1
                if yeni_hata >= 5:
                    kilit_zamani = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
                    self.db.calistir("UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?", (yeni_hata, kilit_zamani, user_id))
                    raise ValueError("5 hatalı giriş yaptınız! Hesabınız 5 dakika süreyle kilitlendi.")
                else:
                    self.db.calistir("UPDATE users SET failed_attempts=? WHERE id=?", (yeni_hata, user_id))
                    raise ValueError(f"Hatalı şifre. Kalan deneme hakkınız: {5 - yeni_hata}")
                    
            if is_active == 0:
                raise ValueError("Hesabınız pasife alınmıştır, lütfen sistem yöneticisiyle iletişime geçin.")
                        
            self.db.calistir("UPDATE users SET failed_attempts=0, locked_until=NULL, son_giris=? WHERE id=?", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
                        
            self.log_ekle(user_id, "Sisteme giriş yaptı")
                        
            if rol == "Student":
                return Student(user_id, isim, db_eposta, profil_foto, toplam_sure_dk)
            elif rol == "Teacher":
                return Teacher(user_id, isim, db_eposta, profil_foto, toplam_sure_dk)
            elif rol == "Admin":
                return Admin(user_id, isim, db_eposta, profil_foto, toplam_sure_dk)
                        
        except Exception as e:
            raise e

    def kayit_ol(self, isim, eposta, sifre, rol, sec_soru, sec_cevap, uzmanlik=""):
        """Yeni kullanıcı kaydı oluşturur; şifre ve e-posta validasyonu uygular.

        Eğitmen kaydında uzmanlık bilgisi 'teachers' tablosuna yazılır.
        """
        try:
            if not isim or not eposta or not sifre or not sec_soru or not sec_cevap:
                raise ValueError("Tüm alanlar zorunludur.")
            if not email_gecerli_mi(eposta):
                raise ValueError("Geçerli bir e-posta adresi giriniz.")
            if not isim_gecerli_mi(isim):
                raise ValueError("İsim sadece sayılardan oluşamaz ve boş bırakılamaz.")
            if not sifre_guclu_mu(sifre):
                raise ValueError("Şifre en az 6 karakter olmalı, harf ve sayı içermelidir.")
                
            var_mi = self.db.calistir("SELECT id FROM users WHERE eposta=?", (eposta,), fetchone=True)
            if var_mi:
                raise ValueError("Bu e-posta adresi zaten kullanımda.")
                
            uid = str(uuid.uuid4())
            hash_sifre = sifre_hashle(sifre)
            hash_cevap = sifre_hashle(sec_cevap.lower().strip())
            
            self.db.calistir("INSERT INTO users (id, isim, eposta, sifre, rol, sec_soru, sec_cevap) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (uid, isim, eposta, hash_sifre, rol, sec_soru, hash_cevap))
                             
            if rol == "Student":
                self.db.calistir("INSERT INTO students (user_id) VALUES (?)", (uid,))
            elif rol == "Teacher":
                self.db.calistir("INSERT INTO teachers (user_id, uzmanlik) VALUES (?, ?)", (uid, uzmanlik))
                
            return True
        except Exception as e:
            raise e

    def sifre_sifirla(self, eposta, sec_soru, sec_cevap, yeni_sifre):
        """Güvenlik sorusu doğrulaması sonrasında kullanıcı şifresini sıfırlar."""
        try:
            user = self.db.calistir("SELECT id, sec_soru, sec_cevap FROM users WHERE eposta=?", (eposta,), fetchone=True)
            if not user:
                raise ValueError("Sistemde böyle bir kullanıcı bulunamadı.")
                
            if user[1] != sec_soru:
                raise ValueError("Güvenlik sorusu hatalı seçildi.")
            
            if not sifre_dogrula(sec_cevap.lower().strip(), user[2]):
                raise ValueError("Güvenlik sorusunun cevabı hatalı.")
                
            if not sifre_guclu_mu(yeni_sifre):
                raise ValueError("Yeni şifre en az 6 karakter olmalı, harf ve sayı içermelidir.")
                
            yeni_hash = sifre_hashle(yeni_sifre)
            self.db.calistir("UPDATE users SET sifre=?, failed_attempts=0, locked_until=NULL WHERE id=?", (yeni_hash, user[0]))
            return True
        except Exception as e:
            raise e

    def profil_guncelle(self, user_id, isim, eposta, profil_foto, yeni_sifre=None):
        """Kullanıcı profil bilgilerini günceller; isteğe bağlı şifre değişikliği destekler."""
        try:
            if not email_gecerli_mi(eposta):
                raise ValueError("Geçerli bir e-posta adresi giriniz.")
                
            baska = self.db.calistir("SELECT id FROM users WHERE eposta=? AND id!=?", (eposta, user_id), fetchone=True)
            if baska:
                raise ValueError("Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.")
                
            if yeni_sifre:
                hash_sifre = sifre_hashle(yeni_sifre)
                self.db.calistir("UPDATE users SET isim=?, eposta=?, profil_foto=?, sifre=? WHERE id=?",
                                 (isim, eposta, profil_foto, hash_sifre, user_id))
            else:
                self.db.calistir("UPDATE users SET isim=?, eposta=?, profil_foto=? WHERE id=?",
                                 (isim, eposta, profil_foto, user_id))
            return True
        except Exception as e:
            raise e

    def oturum_suresi_ekle(self, user_id, sure_dk):
        """Kullanıcının birikimli oturum süresini artırır."""
        try:
            if sure_dk > 0:
                self.db.calistir("UPDATE users SET toplam_sure_dk = toplam_sure_dk + ? WHERE id=?", (sure_dk, user_id))
        except Exception as e:
            print(f"Oturum süresi güncellenirken hata: {e}")

    def kurs_ekle(self, ad, egitmen_id, kategori, aciklama, baslangic, bitis, kapasite, fiyat=0, zorluk="Başlangıç", kapak_resmi=""):
        """Yeni kurs oluşturur; tarih ve kapasite validasyonu uygular.

        Kurs ID'si 5 haneli rastgele sayısal değerdir (karmaşıklığı azaltır).
        Döndürür:
            str: Oluşturulan kursun ID'si.
        """
        try:
            if gecmis_tarih_mi(baslangic): raise ValueError("Başlangıç tarihi geçmişte olamaz.")
            if kapasite < 1: raise ValueError("Kapasite 1'den küçük olamaz.")
            import random
            kurs_id = str(random.randint(10000, 99999))
            sorgu = """INSERT INTO courses (id, kurs_adi, egitmen_id, kategori, aciklama, baslangic_tarihi, bitis_tarihi, kapasite, onay_durumu, fiyat, zorluk, kapak_resmi) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)"""
            self.db.calistir(sorgu, (kurs_id, ad, egitmen_id, kategori, aciklama, baslangic, bitis, kapasite, fiyat, zorluk, kapak_resmi))
            return kurs_id
        except Exception as e: raise e
            
    def kurs_guncelle(self, kurs_id, ad, kategori, aciklama, kapasite, fiyat, zorluk):
        """Kurs meta verilerini günceller ve onay durumunu sıfırlar (yeniden inceleme için)."""
        try:
            sorgu = "UPDATE courses SET kurs_adi=?, kategori=?, aciklama=?, kapasite=?, fiyat=?, zorluk=?, onay_durumu=0 WHERE id=?"
            self.db.calistir(sorgu, (ad, kategori, aciklama, kapasite, fiyat, zorluk, kurs_id))
            return True
        except Exception as e:
            raise e

    def haftalik_plan_ekle(self, kurs_id, hafta_no, konu, detay="", pdf=""):
        """Ders içeriği ekler; aynı hafta için kayıt varsa günceller (upsert mantiği)."""
        try:
            var_mi = self.db.calistir("SELECT id FROM lessons WHERE kurs_id=? AND hafta_no=?", (kurs_id, hafta_no), fetchone=True)
            if var_mi:
                self.db.calistir("UPDATE lessons SET konu=?, notes=?, icerik_pdf=? WHERE id=?", (konu, detay, pdf, var_mi[0]))
            else:
                hid = str(uuid.uuid4())
                self.db.calistir("INSERT INTO lessons (id, kurs_id, hafta_no, konu, notes, icerik_pdf) VALUES (?, ?, ?, ?, ?, ?)",
                                 (hid, kurs_id, hafta_no, konu, detay, pdf))
        except Exception as e:
            raise e

    def kursa_ait_dersleri_getir(self, kurs_id):
        """Kursa ait haftalık ders içeriklerini sıralı biçimde döndürür.
        'notes' sütunu ders detay/açıklaması olarak kullanılmaktadır.
        """
        return self.db.calistir("SELECT id, hafta_no, konu, notes, icerik_pdf FROM lessons WHERE kurs_id=? ORDER BY hafta_no ASC", (kurs_id,), fetchall=True)

    def ders_sil(self, ders_id):
        """Ders kaydını kalıcı olarak siler."""
        self.db.calistir("DELETE FROM lessons WHERE id=?", (ders_id,))

    def tum_kurslari_getir(self, sadece_onayli=True, arama="", kategori="Tüm Kategoriler"):
        """Aktif kursları filtreli biçimde döndürür.

        Parametreler:
            sadece_onayli (bool): True ise yalnızca onaylı kurslar listelenir.
            arama (str): Kurs adı veya açıklamasında arama yapılır.
            kategori (str): Belirli kategoriye göre filtreler.
        """
        try:
            sartlar = ["c.is_active=1"]
            parametreler = []
            if sadece_onayli:
                sartlar.append("c.onay_durumu=1")
            if arama:
                sartlar.append("(c.kurs_adi LIKE ? OR c.aciklama LIKE ?)")
                parametreler.extend([f"%{arama}%", f"%{arama}%"])
            if kategori and kategori != "Tüm Kategoriler":
                sartlar.append("c.kategori=?")
                parametreler.append(kategori)
                            
            sorgu = f"""
                SELECT c.id, c.kurs_adi, u.isim, c.kategori, c.baslangic_tarihi, c.kapasite, c.onay_durumu, c.kapak_resmi
                FROM courses c
                JOIN users u ON c.egitmen_id = u.id
                WHERE {" AND ".join(sartlar)}
            """
            return self.db.calistir(sorgu, tuple(parametreler), fetchall=True)
        except Exception as e:
            print(f"Kursları getirirken hata: {e}")
            return []
            
    def program_ekle(self, kurs_id, gun, baslangic, bitis):
        self.db.calistir("INSERT INTO schedules (id, kurs_id, gun, baslangic_saat, bitis_saat) VALUES (?, ?, ?, ?, ?)",
                         (str(uuid.uuid4()), kurs_id, gun, baslangic, bitis))
                         
    def program_getir(self, user_id, rol):
        if rol == "Teacher":
            sorgu = "SELECT s.gun, s.baslangic_saat, s.bitis_saat, c.kurs_adi FROM schedules s JOIN courses c ON s.kurs_id=c.id WHERE c.egitmen_id=?"
        else:
            sorgu = "SELECT s.gun, s.baslangic_saat, s.bitis_saat, c.kurs_adi FROM schedules s JOIN courses c ON s.kurs_id=c.id JOIN enrollments e ON c.id=e.kurs_id WHERE e.ogrenci_id=?"
        return self.db.calistir(sorgu, (user_id,), fetchall=True)
            
    def egitmen_kurslari_getir(self, egitmen_id):
        """Eğitmenin aktif kurslarını fiyat ve zorluk bilgisiyle birlikte döndürür."""
        try:
            return self.db.calistir("SELECT id, kurs_adi, kategori, onay_durumu, kapasite, zorluk, fiyat FROM courses WHERE egitmen_id=? AND is_active=1", (egitmen_id,), fetchall=True)
        except Exception:
            # Şema güncellemesi henüz veritabanına yansımadıysa güvenli geri dönüş
            return self.db.calistir("SELECT id, kurs_adi, kategori, onay_durumu, kapasite, 'Başlangıç', 0 FROM courses WHERE egitmen_id=? AND is_active=1", (egitmen_id,), fetchall=True)

    def kurs_detay_getir(self, kurs_id):
        try:
            return self.db.calistir("SELECT c.*, u.isim FROM courses c JOIN users u ON c.egitmen_id=u.id WHERE c.id=?", (kurs_id,), fetchone=True)
        except Exception:
            return None

    def kurs_mufredat_getir(self, kurs_id):
        try:
            return self.db.calistir("SELECT hafta_no, konu, icerik_pdf FROM lessons WHERE kurs_id=? ORDER BY hafta_no ASC", (kurs_id,), fetchall=True)
        except Exception:
            return []

    def ogrenci_sikayet_gecmisi(self, ogrenci_id):
        sorgu = "SELECT id, kategori, aciklama, durum, tarih FROM complaints WHERE user_id=? ORDER BY tarih DESC"
        return self.db.calistir(sorgu, (ogrenci_id,), fetchall=True)

    def sikayet_durum_guncelle(self, sikayet_id, yeni_durum):
        try:
            self.db.calistir("UPDATE complaints SET durum=? WHERE id=?", (yeni_durum, sikayet_id))
        except Exception as e:
            raise e

    def log_ekle(self, user_id, aksiyon):
        try:
            self.db.calistir("INSERT INTO performance_logs (id, user_id, aksiyon) VALUES (?, ?, ?)", 
                             (str(uuid.uuid4()), user_id, aksiyon))
        except: pass

    def loglari_getir(self):
        sorgu = "SELECT p.tarih, u.isim, p.aksiyon FROM performance_logs p JOIN users u ON p.user_id = u.id ORDER BY p.tarih DESC LIMIT 100"
        return self.db.calistir(sorgu, fetchall=True)

    def ajanda_ekle(self, user_id, tarih, metin):
        aid = str(uuid.uuid4())
        self.db.calistir("INSERT INTO personal_agenda (id, user_id, tarih, metin) VALUES (?, ?, ?, ?)", (aid, user_id, tarih, metin))
        return aid

    def ajanda_getir(self, user_id):
        return self.db.calistir("SELECT id, tarih, metin, is_completed FROM personal_agenda WHERE user_id=? ORDER BY tarih ASC", (user_id,), fetchall=True)

    def ajanda_durum_degistir(self, ajanda_id, durum):
        self.db.calistir("UPDATE personal_agenda SET is_completed=? WHERE id=?", (durum, ajanda_id))

    def ajanda_sil(self, ajanda_id):
        try:
            self.db.calistir("DELETE FROM personal_agenda WHERE id=?", (ajanda_id,))
            return True
        except Exception as e:
            raise e

    def kursa_kaydol(self, ogrenci_id, kurs_id):
        """Öğrenciyi kursa kaydeder; kontenjan ve mükerrer kayıt kontrolü yapar."""
        try:
            var_mi = self.db.calistir("SELECT id FROM enrollments WHERE ogrenci_id=? AND kurs_id=?", (ogrenci_id, kurs_id), fetchone=True)
            if var_mi:
                raise ValueError("Bu kursa zaten kayıtlısınız.")
                
            kurs_data = self.db.calistir("SELECT kapasite FROM courses WHERE id=?", (kurs_id,), fetchone=True)
            kayit_sayisi = self.db.calistir("SELECT COUNT(*) FROM enrollments WHERE kurs_id=?", (kurs_id,), fetchone=True)[0]
            
            if kayit_sayisi >= kurs_data[0]:
                raise ValueError("Bu kursun kontenjanı dolmuştur.")
                
            eid = str(uuid.uuid4())
            self.db.calistir("INSERT INTO enrollments (id, ogrenci_id, kurs_id) VALUES (?, ?, ?)", (eid, ogrenci_id, kurs_id))
            return True
        except Exception as e:
            raise e
            
    def ogrenci_kurslari_getir(self, ogrenci_id):
        try:
            sorgu = """
                SELECT c.id, c.kurs_adi, u.isim, e.ilerleme 
                FROM enrollments e
                JOIN courses c ON e.kurs_id = c.id
                JOIN users u ON c.egitmen_id = u.id
                WHERE e.ogrenci_id=? AND c.is_active=1
            """
            return self.db.calistir(sorgu, (ogrenci_id,), fetchall=True)
        except Exception:
            return []

    def onay_bekleyen_kurslar(self):
        """Yönetici onayı bekleyen aktif kursları listeler."""
        try:
            sorgu = "SELECT c.id, c.kurs_adi, u.isim, c.kategori FROM courses c JOIN users u ON c.egitmen_id=u.id WHERE c.onay_durumu=0 AND c.is_active=1"
            return self.db.calistir(sorgu, fetchall=True)
        except Exception:
            return []
            
    def kurs_onayla(self, kurs_id, onay_durumu=1):
        """Kursun onay durumunu günceller; 0=reddedildi, 1=onaylandı."""
        try:
            self.db.calistir("UPDATE courses SET onay_durumu=? WHERE id=?", (onay_durumu, kurs_id))
            return True
        except Exception as e:
            raise e

    def tum_kullanicilari_getir(self):
        """Admin rolü hariç tüm aktif kullanıcıları döndürür."""
        try:
            return self.db.calistir("SELECT id, isim, eposta, rol, is_active, toplam_sure_dk FROM users WHERE rol!='Admin'", fetchall=True)
        except Exception:
            return []
            
    def ogrencileri_getir_egitmen(self, egitmen_id):
        sorgu = "SELECT DISTINCT u.id, u.isim, u.eposta, c.kurs_adi FROM enrollments e JOIN users u ON e.ogrenci_id=u.id JOIN courses c ON e.kurs_id=c.id WHERE c.egitmen_id=?"
        return self.db.calistir(sorgu, (egitmen_id,), fetchall=True)
        
    def admin_tum_kurslar(self):
        sorgu = "SELECT c.id, c.kurs_adi, u.isim, c.kategori, c.onay_durumu FROM courses c JOIN users u ON c.egitmen_id=u.id"
        return self.db.calistir(sorgu, fetchall=True)
            
    def kullanici_durum_degistir(self, user_id, durum):
        """Kullanıcı hesabını aktif (1) veya pasif (0) yapar."""
        try:
            self.db.calistir("UPDATE users SET is_active=? WHERE id=?", (durum, user_id))
        except Exception as e:
            raise e

    def kullanici_sil(self, user_id):
        """Kullanıcıyı veritabanından kalıcı olarak siler."""
        self.db.calistir("DELETE FROM users WHERE id=?", (user_id,))

    def kurs_sil(self, kurs_id):
        self.db.calistir("DELETE FROM courses WHERE id=?", (kurs_id,))

    def ayar_getir(self, key, default=""):
        res = self.db.calistir("SELECT value FROM settings WHERE key=?", (key,), fetchone=True)
        return res[0] if res else default

    def ayar_kaydet(self, key, value):
        self.db.calistir("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

    def duyuru_ekle(self, title, message):
        """Sisteme yeni duyuru ekler."""
        self.db.calistir("INSERT INTO announcements (id, title, message) VALUES (?, ?, ?)", (str(uuid.uuid4()), title, message))
        
    def duyurulari_getir(self):
        return self.db.calistir("SELECT title, message, date FROM announcements ORDER BY date DESC", fetchall=True)

    def odev_ekle(self, kurs_id, baslik, aciklama, son_tarih):
        """Kursa ödev ekler; kayıtlı öğrencilerin ajandalarına otomatik not düşer."""
        try:
            if gecmis_tarih_mi(son_tarih):
                raise ValueError("Son tarih geçmişte olamaz.")
            aid = str(uuid.uuid4())
            self.db.calistir("INSERT INTO assignments (id, kurs_id, baslik, aciklama, son_tarih) VALUES (?, ?, ?, ?, ?)",
                             (aid, kurs_id, baslik, aciklama, son_tarih))
            
            # --- 2. DÜZELTME: Derse kayıtlı tüm öğrencilerin ajandasına otomatik ekle ---
            ogrenciler = self.db.calistir("SELECT ogrenci_id FROM enrollments WHERE kurs_id=?", (kurs_id,), fetchall=True)
            for ogr in ogrenciler:
                self.ajanda_ekle(ogr[0], son_tarih, f"Ödev Son Teslim: {baslik}")
                
        except Exception as e:
            raise e
            
    def kursun_odevleri(self, kurs_id):
        try:
            return self.db.calistir("SELECT id, baslik, aciklama, son_tarih FROM assignments WHERE kurs_id=? AND is_active=1", (kurs_id,), fetchall=True)
        except Exception:
            return []

    def egitmen_odevleri_getir(self, egitmen_id):
        """Eğitmenin tüm kurslarındaki aktif ödevleri son tarihe göre listeler."""
        # Eğitmenin kendi kursları için oluşturduğu tüm ödevleri getirir
        sorgu = """
            SELECT a.id, a.baslik, c.kurs_adi, a.son_tarih, a.aciklama
            FROM assignments a
            JOIN courses c ON a.kurs_id = c.id
            WHERE c.egitmen_id = ? AND a.is_active=1
            ORDER BY a.son_tarih DESC
        """
        return self.db.calistir(sorgu, (egitmen_id,), fetchall=True)

    def takvim_getir(self, kurs_id):
        try:
            return self.db.calistir("SELECT gun, baslangic_saat, bitis_saat FROM schedules WHERE kurs_id=?", (kurs_id,), fetchall=True)
        except Exception:
            return []

    def istatistikleri_getir(self):
        """Sistem genelindeki öğrenci, eğitmen, kurs sayısı ve toplam oturum süresini döndürür."""
        try:
            ogr_sayi = self.db.calistir("SELECT COUNT(*) FROM users WHERE rol='Student'", fetchone=True)[0]
            egt_sayi = self.db.calistir("SELECT COUNT(*) FROM users WHERE rol='Teacher'", fetchone=True)[0]
            krs_sayi = self.db.calistir("SELECT COUNT(*) FROM courses WHERE is_active=1", fetchone=True)[0]
            
            toplam_sure = self.db.calistir("SELECT SUM(toplam_sure_dk) FROM users", fetchone=True)[0] or 0
            
            return ogr_sayi, egt_sayi, krs_sayi, toplam_sure
        except Exception:
            return 0, 0, 0, 0

    def egitmen_dashboard_istatistik(self, egitmen_id):
        """Eğitmen paneli için istatistiksel verileri getirir."""
        try:
            ogr_sayisi = self.db.calistir("SELECT COUNT(e.id) FROM enrollments e JOIN courses c ON e.kurs_id = c.id WHERE c.egitmen_id=?", (egitmen_id,), fetchone=True)[0]
            gelir = ogr_sayisi * 150
            return ogr_sayisi, gelir
        except:
            return 0, 0

    def ogrenci_dashboard_istatistik(self, ogrenci_id):
        """Öğrenci paneli için istatistiksel verileri getirir."""
        aktif_kurslar = self.db.calistir("SELECT COUNT(*) FROM enrollments WHERE ogrenci_id=?", (ogrenci_id,), fetchone=True)[0]
        tamamlanan_dersler = self.db.calistir("SELECT COUNT(*) FROM submissions WHERE ogrenci_id=?", (ogrenci_id,), fetchone=True)[0]
        toplam_sure = self.db.calistir("SELECT toplam_sure_dk FROM users WHERE id=?", (ogrenci_id,), fetchone=True)[0] or 0
        ilerleme_avg = self.db.calistir("SELECT AVG(ilerleme) FROM enrollments WHERE ogrenci_id=?", (ogrenci_id,), fetchone=True)[0] or 0
        return aktif_kurslar, tamamlanan_dersler, toplam_sure, int(ilerleme_avg)

    def ogrenci_yaklasan_sinavlar(self, ogrenci_id):
        sorgu = """
            SELECT e.id, c.kurs_adi, e.baslik, e.sure_dk 
            FROM exams e
            JOIN courses c ON e.kurs_id = c.id
            JOIN enrollments en ON c.id = en.kurs_id
            WHERE en.ogrenci_id = ? AND e.is_active=1
        """
        return self.db.calistir(sorgu, (ogrenci_id,), fetchall=True)

    def ogrenci_haftalik_gorevler(self, ogrenci_id):
        sorgu = """
            SELECT a.id, c.kurs_adi, a.baslik, a.son_tarih 
            FROM assignments a
            JOIN courses c ON a.kurs_id = c.id
            JOIN enrollments en ON c.id = en.kurs_id
            WHERE en.ogrenci_id = ? AND a.is_active=1
        """
        return self.db.calistir(sorgu, (ogrenci_id,), fetchall=True)

    def egitmen_sinavlari_getir(self, egitmen_id):
        sorgu = "SELECT e.id, e.baslik, e.kurs_id, e.sure_dk FROM exams e JOIN courses c ON e.kurs_id = c.id WHERE c.egitmen_id = ? AND e.is_active=1"
        return self.db.calistir(sorgu, (egitmen_id,), fetchall=True)

    def sinav_ekle(self, kurs_id, baslik, sure_dk):
        """Kursa yeni sınav ekler."""
        self.db.calistir("INSERT INTO exams (id, kurs_id, baslik, sure_dk) VALUES (?, ?, ?, ?)", (str(uuid.uuid4()), kurs_id, baslik, sure_dk))

    def ayin_ogrencisini_belirle(self):
        top = self.db.calistir("SELECT u.id FROM student_points sp JOIN users u ON sp.ogrenci_id = u.id GROUP BY u.id ORDER BY AVG(sp.puan) DESC LIMIT 1", fetchone=True)
        if top:
            var_mi = self.db.calistir("SELECT id FROM badges WHERE user_id=? AND badge_name='Ayın Öğrencisi'", (top[0],), fetchone=True)
            if not var_mi:
                self.db.calistir("INSERT INTO badges (id, user_id, badge_name) VALUES (?, ?, ?)", (str(uuid.uuid4()), top[0], "Ayın Öğrencisi"))
                self.db.calistir("INSERT INTO badges (id, user_id, badge_name) VALUES (?, ?, ?)", (str(uuid.uuid4()), top[0], "Kitap Ödülü (Sürpriz!)"))

    def kurs_reddet(self, kurs_id):
        try:
            self.db.calistir("DELETE FROM courses WHERE id=?", (kurs_id,))
            return True
        except Exception as e:
            raise e

    def egitmen_degerlendirmeleri_getir(self, egitmen_id):
        sorgu = """
            SELECT u.isim, e.hafta, e.guclu_yonler, e.eksikler 
            FROM evaluations e 
            JOIN users u ON e.ogrenci_id = u.id 
            WHERE e.egitmen_id = ? ORDER BY e.hafta DESC
        """
        return self.db.calistir(sorgu, (egitmen_id,), fetchall=True)

    # --- EĞİTMEN PANELİ YENİ ÖZELLİKLER (PART 1) ---
    def egitmen_gelismis_dashboard(self, egitmen_id):
        # 1. Aktif Kurslar
        aktif_kurs = self.db.calistir("SELECT COUNT(*) FROM courses WHERE egitmen_id=? AND is_active=1 AND onay_durumu=1", (egitmen_id,), fetchone=True)[0] or 0
        # 2. Toplam Öğrenci
        toplam_ogr = self.db.calistir("SELECT COUNT(e.id) FROM enrollments e JOIN courses c ON e.kurs_id = c.id WHERE c.egitmen_id=?", (egitmen_id,), fetchone=True)[0] or 0
        # 3. Onay Bekleyen Kurslar
        bekleyen = self.db.calistir("SELECT COUNT(*) FROM courses WHERE egitmen_id=? AND onay_durumu=0", (egitmen_id,), fetchone=True)[0] or 0
        # 4. Gelir Özeti (Örnek: Öğrenci başı 150 TL)
        gelir = toplam_ogr * 150
        
        return aktif_kurs, toplam_ogr, bekleyen, gelir

    def egitmen_populer_kurslar(self, egitmen_id):
        # En çok kayıt alan 5 kursu getirir
        sorgu = """
            SELECT c.kurs_adi, c.baslangic_tarihi, COUNT(e.id) as kayit_sayisi
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.kurs_id
            WHERE c.egitmen_id = ? AND c.is_active=1 AND c.onay_durumu=1
            GROUP BY c.id
            ORDER BY kayit_sayisi DESC LIMIT 5
        """
        return self.db.calistir(sorgu, (egitmen_id,), fetchall=True)

    def egitmen_riskli_ogrenciler(self, egitmen_id):
        sorgu = """
            SELECT 
                u.isim, 
                c.kurs_adi, 
                IFNULL(CAST(AVG(sp.puan) AS INTEGER), 0) as ortalama
            FROM enrollments e
            JOIN users u ON e.ogrenci_id = u.id
            JOIN courses c ON e.kurs_id = c.id
            LEFT JOIN student_points sp ON (sp.ogrenci_id = u.id AND sp.kurs_id = c.id)
            WHERE c.egitmen_id = ?
            GROUP BY u.id, c.id
            HAVING ortalama < 50
            ORDER BY ortalama ASC
            LIMIT 10
        """
        return self.db.calistir(sorgu, (egitmen_id,), fetchall=True)

    # --- EĞİTMEN PANELİ YENİ ÖZELLİKLER (PART 2) ---
    def egitmen_ogrencileri_detayli(self, egitmen_id):
        # Öğrencilerin kayıt tarihi ve ilerleme durumlarını detaylı olarak getirir
        sorgu = """
            SELECT u.id, u.isim, u.eposta, c.kurs_adi, e.kayit_tarihi, e.ilerleme, c.id
            FROM enrollments e
            JOIN users u ON e.ogrenci_id = u.id
            JOIN courses c ON e.kurs_id = c.id
            WHERE c.egitmen_id = ?
            ORDER BY e.kayit_tarihi DESC
        """
        return self.db.calistir(sorgu, (egitmen_id,), fetchall=True)

    def ogrenci_notlari_getir(self, ogrenci_id, kurs_id):
        # Bir öğrencinin belirli bir kurstaki tüm ödev notlarını ve geribildirimlerini getirir
        sorgu = """
            SELECT a.baslik, s.not_degeri, s.geribildirim, s.tarih
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            WHERE s.ogrenci_id = ? AND a.kurs_id = ?
        """
        return self.db.calistir(sorgu, (ogrenci_id, kurs_id), fetchall=True)

    def ogrencileri_getir_kursa_gore(self, kurs_id):
        """Belirtilen kursa kayıtlı öğrencileri id ve isim olarak döndürür."""
        # Belirli bir kursa kayıtlı olan öğrencilerin listesini getirir
        sorgu = "SELECT u.id, u.isim FROM enrollments e JOIN users u ON e.ogrenci_id = u.id WHERE e.kurs_id=?"
        return self.db.calistir(sorgu, (kurs_id,), fetchall=True)

    def yoklama_kaydet(self, kurs_id, ogrenci_id, tarih, durum):
        """Öğrencinin belirtilen tarihteki yoklama durumunu kaydeder; mevcut kayıt varsa günceller."""
        try:
            self.db.calistir("CREATE TABLE IF NOT EXISTS attendance (id TEXT PRIMARY KEY, kurs_id TEXT, ogrenci_id TEXT, tarih DATE, durum TEXT)")
            
            self.db.calistir("DELETE FROM attendance WHERE kurs_id=? AND ogrenci_id=? AND tarih=?", (kurs_id, ogrenci_id, tarih))
            self.db.calistir("INSERT INTO attendance (id, kurs_id, ogrenci_id, tarih, durum) VALUES (?, ?, ?, ?, ?)", 
                             (str(uuid.uuid4()), kurs_id, ogrenci_id, tarih, durum))
        except Exception as e:
            raise e

    def yoklama_durumu_getir(self, kurs_id, tarih):
        """Seçilen tarihteki yoklama durumlarını {ogrenci_id: durum} sözlüğü olarak döndürür."""
        self.db.calistir("CREATE TABLE IF NOT EXISTS attendance (id TEXT PRIMARY KEY, kurs_id TEXT, ogrenci_id TEXT, tarih DATE, durum TEXT)")
        kayitlar = self.db.calistir("SELECT ogrenci_id, durum FROM attendance WHERE kurs_id=? AND tarih=?", (kurs_id, tarih), fetchall=True)
        return {k[0]: k[1] for k in kayitlar}

    def sikayet_olustur(self, user_id, kategori, aciklama):
        cid = str(uuid.uuid4())
        self.db.calistir("INSERT INTO complaints (id, user_id, kategori, aciklama) VALUES (?, ?, ?, ?)", (cid, user_id, kategori, aciklama))
        return cid[:8].upper()

    def admin_sikayetleri_getir(self):
        sorgu = "SELECT c.id, u.isim, c.kategori, c.aciklama, c.durum, c.tarih FROM complaints c JOIN users u ON c.user_id = u.id ORDER BY c.tarih DESC"
        return self.db.calistir(sorgu, fetchall=True)

    def mesaj_gonder(self, gonderen_id, alici_id, metin):
        """İki kullanıcı arasında mesaj gönderir; rol bazlı iletişim kısıtlamaları uygular."""
        try:
            if not metin.strip():
                raise ValueError("Mesaj boş olamaz.")
                            
            gonderen_rol = self.db.calistir("SELECT rol FROM users WHERE id=?", (gonderen_id,), fetchone=True)
            alici_rol = self.db.calistir("SELECT rol FROM users WHERE id=?", (alici_id,), fetchone=True)
            
            if not gonderen_rol or not alici_rol:
                raise ValueError("Kullanıcı bulunamadı.")
                            
            # Öğrenci → Admin doğrudan iletişimi kısıtlıdır
            if gonderen_rol[0] == "Student" and alici_rol[0] == "Admin":
                raise ValueError("Öğrenciler doğrudan yöneticiye mesaj gönderemez. Lütfen önce öğretmeninizle iletişime geçin.")
            
            if gonderen_id == alici_id:
                raise ValueError("Kendinize mesaj gönderemezsiniz.")
            
            mid = str(uuid.uuid4())
            self.db.calistir("INSERT INTO messages (id, gonderen_id, alici_id, metin) VALUES (?, ?, ?, ?)", (mid, gonderen_id, alici_id, metin))
            return True
        except Exception as e:
            raise e

    def mesajlari_getir(self, user1, user2):
        """İki kullanıcı arasındaki mesaj geçmişini döndürür; okundu durumunu günceller."""
        try:
            self.db.calistir("UPDATE messages SET okundu=1 WHERE alici_id=? AND gonderen_id=?", (user1, user2))
            
            sorgu = """
                SELECT gonderen_id, metin, tarih FROM messages 
                WHERE (gonderen_id=? AND alici_id=?) OR (gonderen_id=? AND alici_id=?) 
                ORDER BY tarih ASC
            """
            return self.db.calistir(sorgu, (user1, user2, user2, user1), fetchall=True)
        except Exception:
            return []
