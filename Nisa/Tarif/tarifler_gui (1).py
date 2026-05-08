import sys
import os
import sqlite3
import json
import urllib.request
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# ══════════════════════════════════════════════════════════
#  1. BÖLÜM: VERİ MODELİ
# ══════════════════════════════════════════════════════════

class Tarif:
    def __init__(self, tarif_id, tarif_adi, kategori, hazirlama_suresi, malzemeler="", favori=False):
        self.tarif_id = tarif_id
        self.tarif_adi = tarif_adi
        self.kategori = kategori
        self.hazirlama_suresi = hazirlama_suresi
        self.malzemeler = malzemeler
        self.favori = favori
        self.puanlar = []

    def favori_gecis(self):
        self.favori = not self.favori

    def tarif_guncelle(self, ad, kat, sure, malzemeler):
        self.tarif_adi = ad
        self.kategori = kat
        self.hazirlama_suresi = sure
        self.malzemeler = malzemeler

    def puan_ekle(self, puan):
        self.puanlar.append(float(puan))
        
    def ortalama_puan(self):
        if not self.puanlar: return 0.0
        return sum(self.puanlar) / len(self.puanlar)

# ══════════════════════════════════════════════════════════
#  2. BÖLÜM: LÜKS RESTORAN TEMALI MODERN ARAYÜZ
# ══════════════════════════════════════════════════════════

RENKLER = {
    'arkaplan': '#0F0F0F',    
    'kart': '#191919',        
    'vurgu': '#D4AF37',       
    'vurgu_hover': '#F3D063', 
    'metin': '#F0F0F0',       
    'metin_ikincil': '#888888',
    'kenarlik': '#2A2A2A',
    'sil': '#E53935',
    'sil_hover': '#FF5252',
    'satir_secili': '#262111' 
}

class LoginEkrani(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlavorPort - Sisteme Giriş")
        self.setFixedSize(400, 250)
        self.setStyleSheet(f"background-color: {RENKLER['arkaplan']}; color: {RENKLER['metin']}; font-family: 'Segoe UI', Arial, sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        baslik_layout = QHBoxLayout()
        
        lbl = QLabel("👋 Hoş Geldiniz")
        lbl.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {RENKLER['vurgu']};")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        lbl_logo = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bjk_logo.png")
        if not os.path.exists(logo_path):
            try:
                url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Be%C5%9Fikta%C5%9F_Jimnastik_Kul%C3%BCb%C3%BC_logo.svg/512px-Be%C5%9Fikta%C5%9F_Jimnastik_Kul%C3%BCb%C3%BC_logo.svg.png"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(logo_path, 'wb') as out_file:
                    out_file.write(response.read())
            except Exception as e:
                pass
                
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_logo.setPixmap(pixmap)
        else:
            lbl_logo.setText("🦅")
            lbl_logo.setStyleSheet("font-size: 24px;")
            
        lbl_logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        baslik_layout.addStretch()
        baslik_layout.addWidget(lbl)
        baslik_layout.addWidget(lbl_logo)
        baslik_layout.addStretch()
        
        layout.addLayout(baslik_layout)
        
        self.in_isim = QLineEdit()
        self.in_isim.setPlaceholderText("Adınızı giriniz...")
        self.in_isim.setFixedHeight(45)
        self.in_isim.setStyleSheet(f"""
            QLineEdit {{ background-color: {RENKLER['kart']}; border: 1px solid {RENKLER['kenarlik']}; border-radius: 10px; padding: 0 15px; color: {RENKLER['metin']}; font-size: 14px; }}
            QLineEdit:focus {{ border: 1px solid {RENKLER['vurgu']}; }}
        """)
        layout.addWidget(self.in_isim)
        
        btn = QPushButton("SİSTEME GİRİŞ YAP")
        btn.setFixedHeight(45)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {RENKLER['vurgu']}; color: {RENKLER['arkaplan']}; font-weight: bold; font-size: 14px; border-radius: 10px; border: none; letter-spacing: 1px; }}
            QPushButton:hover {{ background-color: {RENKLER['vurgu_hover']}; }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.giris_yap)
        layout.addWidget(btn)
        
        self.kullanici_adi = ""
        
    def giris_yap(self):
        if self.in_isim.text().strip():
            self.kullanici_adi = self.in_isim.text().strip()
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen sisteme girmek için adınızı belirtin.")

class LezzetPaneli(QMainWindow):
    def __init__(self, kullanici_adi):
        super().__init__()
        self.kullanici_adi = kullanici_adi
        self.tarifler = {}
        self.son_id = 100
        self.aktif_filtre = "Tümü"
        
        self.setWindowTitle(f"FlavorPort - Şef: {self.kullanici_adi}")
        self.resize(1300, 850)
        self.setStyleSheet(f"background-color: {RENKLER['arkaplan']}; color: {RENKLER['metin']}; font-family: 'Segoe UI', Arial, sans-serif;")

        # DB bağlantısı
        self.db_baglanti_kur()

        ana_widget = QWidget()
        self.setCentralWidget(ana_widget)
        self.layout = QHBoxLayout(ana_widget)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(40)

        # --- SOL PANEL ---
        self.sol_panel = QFrame()
        self.sol_panel.setStyleSheet(f"QFrame {{ background-color: {RENKLER['kart']}; border-radius: 20px; border: 1px solid {RENKLER['kenarlik']}; }}")
        self.sol_panel.setFixedWidth(400)
        self.form_paneli_tasarla()
        self.layout.addWidget(self.sol_panel)
        
        # --- SAĞ PANEL ---
        self.sag_panel = QWidget()
        self.liste_paneli_tasarla()
        self.layout.addWidget(self.sag_panel)

        # Eğer DB boş geldiyse örnek verileri aktar
        if len(self.tarifler) == 0:
            self.ornek_verileri_yukle()
        else:
            self.arayuz_guncelle()

    # --- VERİTABANI İŞLEMLERİ ---
    def db_baglanti_kur(self):
        db_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarifler_veritabani.db")
        self.conn = sqlite3.connect(db_yolu)
        self.cur = self.conn.cursor()
        
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS tarifler (
                id INTEGER PRIMARY KEY,
                ad TEXT,
                kategori TEXT,
                sure TEXT,
                malzemeler TEXT,
                puanlar TEXT
            )
        ''')
        try:
            self.cur.execute("ALTER TABLE tarifler ADD COLUMN favori INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        self.conn.commit()
        
        # Verileri Yükle
        self.cur.execute("SELECT id, ad, kategori, sure, malzemeler, puanlar, favori FROM tarifler")
        satirlar = self.cur.fetchall()
        max_id = 100
        
        for satir in satirlar:
            t_id, ad, kat, sure, malz, puanlar_json, fav_int = satir
            t = Tarif(t_id, ad, kat, sure, malz, bool(fav_int))
            try:
                t.puanlar = json.loads(puanlar_json)
            except:
                t.puanlar = []
            
            self.tarifler[t_id] = t
            if t_id > max_id:
                max_id = t_id
                
        self.son_id = max_id

    def db_tarif_kaydet(self, tarif):
        p_json = json.dumps(tarif.puanlar)
        fav_int = 1 if tarif.favori else 0
        self.cur.execute('''
            INSERT OR REPLACE INTO tarifler 
            (id, ad, kategori, sure, malzemeler, puanlar, favori) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tarif.tarif_id, tarif.tarif_adi, tarif.kategori, tarif.hazirlama_suresi, tarif.malzemeler, p_json, fav_int))
        self.conn.commit()

    def db_tarif_sil(self, t_id):
        self.cur.execute("DELETE FROM tarifler WHERE id=?", (t_id,))
        self.conn.commit()

    def closeEvent(self, event):
        if self.conn:
            self.conn.close()
        event.accept()

    # --- ÖRNEK VERİ AKTARIMI ---
    def ornek_verileri_yukle(self):
        self.tarif_ekle("Mantı", "Ana Yemek", "90", "Malzemeler: Hamur için un, yumurta, su, tuz. İç harcı için kıyma, soğan, karabiber, pul biber. Üzeri için sarımsaklı yoğurt, tereyağı, nane, sumak. Yapılışı: Sert bir hamur yoğurun ve dinlendirin. Hamuru ince açıp küçük kareler halinde kesin. İçlerine kıymalı harçtan koyup bohça veya üçgen şeklinde kapatın. Tuzlu kaynar suda mantılar su yüzüne çıkana kadar haşlayın. Tabaklama: Geniş ve derin bir tabağa alınan mantıların üzerine bol sarımsaklı yoğurt gezdirin. En üste kızdırılmış tereyağlı-naneli sos dökerek sıcak servis yapın.", favori=True)
        self.tarif_ekle("Yağlama", "Ana Yemek", "60", "Malzemeler: Lavaş için 4 su bardağı un, 1 paket kuru maya, 1 tatlı kaşığı tuz, ılık su. Harç için yarım kilo kıyma, 2 soğan, 3 yeşil biber, 2 domates, 1 y.k. salça. Yapılışı: Bezeleri tabak büyüklüğünde açıp yağsız tavada arkalı önlü pişirin. Kıymayı kavurun, sebzeleri ve salçayı ekleyip sulu bir kıvamda pişirin. Tabaklama: Bir lavaşı servis tabağına alın, üzerine harcı yayın. Bu işlemi tüm lavaşlar bitene kadar üst üste yapın. Pastayı dilimler gibi kesin ve tam ortasına bol sarımsaklı yoğurt koyarak servis yapın.")
        self.tarif_ekle("Karnıyarık", "Ana Yemek", "70", "Malzemeler: 6 adet patlıcan, 300g kıyma, 1 soğan, 2 diş sarımsak, 2 sivri biber, 2 domates, salça. Yapılışı: Patlıcanları alacalı soyup kızartın. Ayrı tavada kıyma, soğan, biber ve domatesle harç yapın. Patlıcanların ortasını yarıp harcı doldurun. Salçalı su yapıp tepsiye dökün ve 200 derece fırında pişirin. Tabaklama: Geniş bir servis tabağında patlıcanı bütün olarak alın, üzerine tepsisindeki salçalı sostan gezdirin. Yanında sade pirinç pilavı ile sunun.", favori=True)
        self.tarif_ekle("Ali Nazik Kebabı", "Ana Yemek", "55", "Malzemeler: 4 adet patlıcan, süzme yoğurt, 3 diş sarımsak, 300g kuşbaşı et veya kıyma, tereyağı, salça, biber. Yapılışı: Patlıcanları közleyip soyun ve ince kıyın. Sarımsaklı süzme yoğurtla karıştırın. Etleri tereyağında kavurun, biber ve salça ekleyerek pişirin. Tabaklama: Klasik bir kayık tabağın zeminine yoğurtlu patlıcan ezmesini kalın bir yatak halinde yayın. Tam ortasına sıcak etli harcı tepeleme koyup sızan tereyağıyla sunun.")
        self.tarif_ekle("Tavuk Sote", "Ana Yemek", "35", "Malzemeler: Yarım kilo tavuk göğsü, 1 soğan, 2 çarliston biber, 1 kapya biber, 2 domates, 1 tatlı kaşığı salça, baharatlar. Yapılışı: Tavukları kuşbaşı doğrayıp yüksek ateşte suyunu çekene kadar soteleyin. Sırasıyla soğan ve biberleri ekleyin. En son doğranmış domates, salça ve baharatları ekleyip kısık ateşte pişirin. Tabaklama: Derin bir servis kasesine veya pilav yanına porsiyonlayın. Üzerine biraz ince kıyılmış taze kekik serpiştirin.")
        self.tarif_ekle("Etli Kuru Fasulye", "Ana Yemek", "90", "Malzemeler: 2 su bardağı kuru fasulye, 250g kuşbaşı et, 1 soğan, 1,5 y.k. domates salçası, tereyağı. Yapılışı: Fasulyeyi akşamdan ıslatıp hafif haşlayın. Etleri düdüklü tencerede kavurun, soğan ve salçayı ekleyin. Fasulyeleri ve sıcak suyu ekleyip 30-40 dakika pişirin. Tabaklama: Geleneksel bakır veya çini kaselerde bol suyu ve eti dengeli olacak şekilde servis edin. Yanında mutlaka kuru soğan ve turşu bulundurun.")
        self.tarif_ekle("Fırında Somon", "Ana Yemek", "45", "Malzemeler: Somon dilimleri, 2 patates, 1 soğan. Sos için zeytinyağı, yarım limon suyu, 2 diş sarımsak, tuz, karabiber. Yapılışı: Tepsisinin tabanına halka soğan ve ince patatesleri dizin. Somonları yerleştirin. Hazırladığınız sarımsaklı limonlu zeytinyağı sosunu balıkların ve sebzelerin üzerine fırçayla sürün. 200 derecede 20-25 dakika pişirin. Tabaklama: Dikdörtgen şık bir porselen tabağa önce patatesleri, üzerine kızarmış somonu yerleştirin. Yanında taze roka ve bir dilim ızgara limon ile sunun.")
        self.tarif_ekle("Kuzu Tandır", "Ana Yemek", "150", "Malzemeler: Kuzu but veya kol eti, tuz, karabiber, zeytinyağı, 1 bütün soğan, sarımsak. Yapılışı: Eti bütün halinde zeytinyağı ve baharatla ovun. Döküm tavada mühürleyin. Ardından tencereye alıp yanına bütün soğan ve sarımsakları ekleyin. Çok az suyla kısık ateşte 2-3 saat et kemikten ayrılana dek pişirin. Tabaklama: Büyük bir ahşap sunum tahtasında, didilmiş yumuşacık etleri iç pilav yatağının üzerine yerleştirin. Etin kendi pişme suyundan (jus) üzerine gezdirerek parlatın.")
        
        self.tarif_ekle("Baklava", "Tatlı", "100", "Malzemeler: Baklavalık yufka, çekilmiş ceviz/fıstık, eritilmiş tereyağı. Şerbet için 3 bardak şeker, 3 bardak su, limon. Yapılışı: Şerbeti kaynatıp soğutun. Yufkaları aralarını yağlayarak tepsiye dizin, ortaya ceviz serpin. Kalan yufkaları da dizip dilimleyin ve fırınlayın. Tabaklama: Fırından çıkan sıcak baklavaya soğuk şerbeti dökün. Beyaz şık bir tabakta 2 dilim yan yana, üzerine toz Antep fıstığı dökerek ve yanında bir top sade dondurma ile servis edin.", favori=True)
        self.tarif_ekle("Sütlaç", "Tatlı", "40", "Malzemeler: 1 lt süt, 1 çay bardağı pirinç, 1 sb şeker, 2 y.k. nişasta, vanilya. Yapılışı: Pirinci suda haşlayın. Süt ve şekeri ekleyip kaynatın. Suda açılmış nişastayı ekleyip kıvam alınca vanilyayı katın. Güveçlere pay edip fırında üstleri kızarana kadar pişirin. Tabaklama: Toprak güveç kaseleri soğuduktan sonra bir altlığın üzerine koyun, ortasına ince dövülmüş fındık içi serpin.")
        self.tarif_ekle("Künefe", "Tatlı", "45", "Malzemeler: Tel kadayıf, tuzsuz künefe peyniri, bol tereyağı. Şerbet için şeker, su, limon. Yapılışı: Şerbeti kaynatıp soğutun. Kadayıfı erimiş yağla harmanlayıp tavaya yarısını bastırın. Araya peynir koyup kalan kadayıfla kapatın. İki tarafını da kızartın. Sıcak künefeye soğuk şerbet dökün. Tabaklama: Özel yuvarlak alüminyum künefe sahanıyla birlikte masaya getirin. Ortasına bir rulo kaymak oturtup üzerine fıstık serperek sıcak sıcak uzayan peyniriyle sunun.")
        self.tarif_ekle("Şekerpare", "Tatlı", "35", "Malzemeler: Un, irmik, pudra şekeri, tereyağı, yumurta, kabartma tozu, fındık. Şerbet için şeker, su. Yapılışı: Hamuru yoğurup yuvarlak bezeler yapın, ortalarına fındık batırın. Fırında pembeleşene kadar pişirin. Fırından çıkınca soğuk şerbetle buluşturun. Tabaklama: İki adet şekerpareyi yan yana kayık tabağa koyun, parlak şerbetinden tabağın zeminine hafifçe gezdirin.")
        self.tarif_ekle("Tiramisu", "Tatlı", "25", "Malzemeler: Kedi dili bisküvi, mascarpone peyniri, krema, yumurta sarısı, şeker, sıcak su, granül kahve, kakao. Yapılışı: Yumurta sarısı ve şekeri çırpıp peynir ve kremayla birleştirin. Kahveyi suda çözün. Bisküvileri kahveye banıp dizin, kremayı sürün. İki kat yapıp dolapta bekletin. Tabaklama: Kare şeklinde kesilmiş pürüzsüz dilimi geniş bir tabağa alın. Tabağın boşluklarına çikolata sosu ile noktalar koyarak süsleyin, üzerine bol kakao eleyin.")
        self.tarif_ekle("Profiterol", "Tatlı", "60", "Malzemeler: Hamur için su, tereyağı, un, yumurta. Krema için süt, şeker, un, nişasta. Üzeri için çikolata sos. Yapılışı: Yağ ve suyu kaynatıp un ekleyerek hamur yapın. Ilıyınca yumurtaları yedirin. Sıkıp pişirin. Pişen hamurların içine hazırlanan pastacı kremasını doldurun. Tabaklama: Geniş oval veya kadeh şeklinde bir kaseye kremalı topları tepeleme dizin. Üzerinden aşağı doğru süzülecek şekilde ılık ve yoğun çikolata sosunu gezdirin.")
        self.tarif_ekle("Kazandibi", "Tatlı", "45", "Malzemeler: Süt, toz şeker, pirinç unu, nişasta, vanilya. Yapılışı: Malzemeleri karıştırarak muhallebi yapın. Yağlanmış ve pudra şekeri serpilmiş tepsiye muhallebiyi dökün. Tepsiyi ocakta çevirerek altını karamelize edin. Tabaklama: Dolapta iyice soğuyan kazandibini uzun dikdörtgen şeklinde kesin. Spatulayla rulo halinde sarıp yanık karamelize kısmı üste gelecek şekilde sade beyaz tabakta sunun.")
        self.tarif_ekle("Trileçe", "Tatlı", "50", "Malzemeler: Pandispanya (yumurta, şeker, un), 3 çeşit süt (inek, keçi, manda veya krema), karamel sos (şeker, tereyağı, krema). Yapılışı: Pandispanyayı pişirin, delikler açıp bol sütlü sosu dökün. Üzerine ince kremşanti tabakası ve en üste ev yapımı karamel sosu yayın. Tabaklama: Pürüzsüz kare dilimi servis tabağına alın. Karamelin üzerindeki beyaz çikolata çizgileri görseli tamamlar, yanında taze nane yaprağı ile renk katın.")
        
        self.tarif_ekle("Ezogelin Çorbası", "Çorba", "30", "Malzemeler: Kırmızı mercimek, 2 y.k. bulgur, 2 y.k. pirinç, soğan, domates/biber salçası, nane, pul biber, et suyu. Yapılışı: Soğanı kavurun, salçaları ekleyin. Yıkanmış bakliyatları ekleyip et suyunda iyice yumuşayana kadar pişirin. Blendırdan geçirmeyin. Tabaklama: Çukur bir porselen kaseye tepeleme doldurun. Tereyağında kavrulmuş kırmızı toz biber ve naneyi çorbanın tam ortasına damlatarak halka şeklinde bir iz bırakın.")
        self.tarif_ekle("Mercimek Çorbası", "Çorba", "25", "Malzemeler: Kırmızı mercimek, kuru soğan, 1 havuç, 1 patates, zeytinyağı, et suyu. Yapılışı: Sebzeleri zeytinyağında soteleyin, mercimeği ve suyu ekleyip kaynatın. Tamamen yumuşayınca blendırdan çekerek pürüzsüz yapın. Tabaklama: Sade beyaz bir kasede çorbayı sunun. Tabağın kenarına bir parça limon ve çıtır kıtır ekmek (kruton) yerleştirin. Üzerine çok hafif tereyağı sosu dökün.")
        self.tarif_ekle("Yayla Çorbası", "Çorba", "30", "Malzemeler: Süzme yoğurt, 1 yumurta sarısı, 1 y.k. un, yarım çay bardağı pirinç, su, tuz, nane. Yapılışı: Pirinci haşlayın. Yoğurt, yumurta ve unu çırpıp meyaneyi ılıştırarak tencereye katın. Sürekli karıştırarak kaynatın. Tabaklama: Bakır veya seramik kasede çorbayı alın. Tavada cızırdayan bol naneli tereyağını servis esnasında, masada konuğun önünde dökerek hem görsel hem işitsel bir şov yapın.")
        self.tarif_ekle("Tarhana Çorbası", "Çorba", "25", "Malzemeler: 4 y.k. toz tarhana, 1 y.k. domates salçası, 2 diş sarımsak, tereyağı, su. Yapılışı: Tarhanayı suda ıslatın. Salça ve sarımsağı tereyağında kavurup tarhanayı ekleyin. Kıvam alana dek karıştırarak pişirin. Tabaklama: Koyu renkli nostaljik bir kasede dumanı tüterken servis edin. Ortasına bir parça köy peyniri (beyaz peynir) ufalayabilirsiniz.")
        self.tarif_ekle("Domates Çorbası", "Çorba", "20", "Malzemeler: 5-6 olgun domates (veya domates püresi), 2 y.k. un, tereyağı, 1 bardak süt, kaşar peyniri. Yapılışı: Tereyağında unu kavurun, rendelenmiş domatesleri ekleyin. Su ilave edip kaynatın. İnerken sütünü koyun. Tabaklama: Renkli ve geniş bir kaseye alın. Üzerine bolca rendelenmiş taze kaşar peyniri tepeciği yapın ve kenarına bir fesleğen yaprağı kondurun.")
        self.tarif_ekle("Kelle Paça Çorbası", "Çorba", "60", "Malzemeler: Kelle eti, paça suyu, sarımsak, sirke, tereyağı, un. Yapılışı: Etleri düdüklüde haşlayın ve didikleyin. Unu yağda kavurup haşlama suyuyla açın, etleri ekleyip kaynatın. Tabaklama: Klasik bir bakır tas veya metal kasede sıcak servis edin. Yanında minik şişelerde sirke, ezilmiş sarımsak ve acı biber sosunu bir sunum tahtasında ayrı olarak getirin.")
        
        self.tarif_ekle("Menemen", "Kahvaltılık", "15", "Malzemeler: 4 sivri biber, 3 domates, 3 yumurta, tereyağı. Yapılışı: Biberleri yağda kavurun, kabuğu soyulmuş küp domatesleri ekleyip iyice ezilene kadar pişirin. Yumurtaları kırıp hafifçe dağıtın (fazla karıştırmayın). Tabaklama: Doğrudan piştiği bakır veya döküm sahanda servis edilir. Masanın ortasına konur, ekmek banmak için hafif sulu bırakılır.")
        self.tarif_ekle("Kaşarlı Tost", "Kahvaltılık", "10", "Malzemeler: 2 kalın dilim tost ekmeği, bol taze kaşar dilimleri, tereyağı. Yapılışı: Ekmeğin arasına peyniri koyun, dışını tereyağıyla yağlayıp sıcak makinede basıp kızartın. Tabaklama: Ahşap bir kesme tahtası üzerine tostu çapraz keserek üçgen halinde üst üste dizin. Yanında minik bir kasede zeytin ve çeri domates bulundurun.")
        self.tarif_ekle("Pankek", "Kahvaltılık", "20", "Malzemeler: 1 bardak süt, 1 yumurta, un, 2 y.k. şeker, kabartma tozu, sıvı yağ. Yapılışı: Pürüzsüz bir hamur yapın. Isıtılmış hafif yağlı tavaya küçük kepçeyle döküp arkalı önlü pişirin. Tabaklama: Beyaz geniş bir tabağın tam ortasına 4 adet pankeki kule gibi dizin. Üzerine bir parça tereyağı koyun ve balı tabağın kenarlarından süzülecek şekilde gezdirin. Çileklerle renklendirin.")
        self.tarif_ekle("Sucuklu Yumurta", "Kahvaltılık", "10", "Malzemeler: Yarım kangal kasap sucuk, 2 yumurta, az tereyağı. Yapılışı: Sucukları halka doğrayıp kendi yağında soteleyin. Yumurtaları sarıları bozulmayacak şekilde kırıp pişirin. Tabaklama: Çift saplı otantik sahanda pişirildiği gibi sunulur. Yumurtanın sarısı patlamamış olmalı, üzerine bir tutam taze çekilmiş karabiber serpilmelidir.")
        self.tarif_ekle("Kuymak", "Kahvaltılık", "25", "Malzemeler: 3 y.k. mısır unu, 2 y.k. Trabzon tereyağı, 1 kase telli peynir, sıcak su. Yapılışı: Tereyağını eritip mısır ununu kavurun. Suyu ekleyin. Şişince telli peyniri katıp eriyene dek kısık ateşte demlendirin. Tabaklama: Tavadan servis edilir. Tereyağı tamamen üste çıkmış ve peynir çatalı daldırdığınızda metrelerce uzayacak kıvamda sıcak olmalıdır.")
        self.tarif_ekle("Sigara Böreği", "Kahvaltılık", "20", "Malzemeler: 2 adet yufka, lor peyniri, maydanoz, sıvı yağ. Yapılışı: Yufkaları üçgen kesin. Peynir ve maydanozu karıştırıp harç yapın, sigara gibi sarıp kızgın yağda altın rengi olana dek kızartın. Tabaklama: İnce uzun dikdörtgen bir meze tabağına börekleri çapraz şekiller oluşturarak dizin. Yanına kırmızı toz biberle süslenmiş bir çay tabağında yoğurt sosu koyun.")
        self.tarif_ekle("Pişi", "Kahvaltılık", "30", "Malzemeler: Un, yaş maya, tuz, ılık su, kızartmak için sıvı yağ. Yapılışı: Mayalı yumuşak bir hamur yapıp dinlendirin. Bezeler koparıp elde yuvarlak açın, ortasını delip derin yağda kabarana dek kızartın. Tabaklama: Hasır görünümlü bir sepetin içine temiz bir peçete serin, puf puf kabarmış pişileri içine doldurun. Reçel tabaklarıyla kontrast yaratın.")
        
        self.tarif_ekle("Sezar Salata", "Salata", "15", "Malzemeler: Göbek marul, ızgara tavuk göğsü, kruton (kıtır ekmek), parmesan. Sos için: Mayonez, zeytinyağı, limon, sarımsak. Yapılışı: Marulları iri doğrayın, sosla iyice harmanlayın. Izgara tavuğu jülyen kesin. Tabaklama: Geniş ve derin bir salata kasesinin içine soslu marulu doldurun. Üzerine tavuk dilimlerini yelpaze gibi dizin. Krutonları serpip üzerine taze parmesan tıraşlayın.")
        self.tarif_ekle("Çoban Salata", "Salata", "10", "Malzemeler: 3 domates, 2 salatalık, 1 kuru soğan, yeşil biber, maydanoz, zeytinyağı, nar ekşisi veya limon. Yapılışı: Tüm sebzeleri küçük eşit küpler halinde (brunoise) doğrayın ve sosla harmanlayın. Tabaklama: Renkli, çukur bir seramik kaseye tepeleme doldurun. Salatayı kendi sosuyla iyice ıslatın, en üste birkaç adet siyah zeytin ve taze nane dalı oturtun.")
        self.tarif_ekle("Akdeniz Salatası", "Salata", "12", "Malzemeler: Karışık Akdeniz yeşilliği (lollo rosso, roka vb.), çeri domates, siyah dilim zeytin, mısır, beyaz peynir küpleri, ceviz. Yapılışı: Yeşillikleri elinizle kopararak kaseye alın, diğer malzemelerle hırpalamadan karıştırın. Tabaklama: Düz, beyaz geniş bir porselen tabağa yeşilliklerden hacimli bir dağ yapın. Peynir küplerini ve kırmızı çeri domatesleri en üste çıkartarak renkleri patlatın.")
        self.tarif_ekle("Ton Balıklı Salata", "Salata", "15", "Malzemeler: Ton balığı, kıvırcık marul, roka, mısır, kırmızı soğan piyazı, çeri domates, zeytinyağı, limon. Yapılışı: Yeşillikleri doğrayıp soğan ve domatesle harmanlayın. Limon ve yağ gezdirin. Tabaklama: Geniş oval bir tabakta yeşilliklerden yatak yapın. Ton balığını (çok ezmeden, iri fileto parçalar halinde) salatanın tam ortasına yerleştirin. Limon dilimlerini tabağın kenarına dizin.")
        self.tarif_ekle("Roka Salatası", "Salata", "10", "Malzemeler: Taze körpe roka yaprakları, çeri domates, tulum peyniri, ceviz içi, zeytinyağı, balzamik sirke, nar ekşisi. Yapılışı: Rokaları kesmeden bütün halde kullanın. Domates ve cevizle harmanlayın. Sosu hazırlayın. Tabaklama: Rokalar sönmesin diye servis esnasında sosunu dökün. Tabağın üzerini tulum peyniri (veya eski kaşar) ufalayarak ve iri ceviz parçalarıyla zenginleştirin.")
        self.tarif_ekle("Mevsim Salata", "Salata", "10", "Malzemeler: Havuç, mor lahana, göbek marul, turp, limon, zeytinyağı. Yapılışı: Lahanayı limon ve tuzla ovun. Havucu rendeleyin, marulu doğrayın. Tabaklama: Karıştırmadan! Geniş düz bir kaseye sırasıyla; turuncu havuç, beyaz/yeşil marul ve mor lahanayı yan yana, şeritler (gökkuşağı) halinde dizin. Ortaya çiçek şeklinde kesilmiş kırmızı turp oturtun.")
        
        # İlk eklendiklerinde rastgele puan verebiliriz (veya opsiyonel olarak pasif bırakabiliriz)
        for t in self.tarifler.values():
            t.puan_ekle(5.0)
            t.puan_ekle(4.5)
            self.db_tarif_kaydet(t)
            
        self.arayuz_guncelle()

    def form_paneli_tasarla(self):
        form_vbox = QVBoxLayout(self.sol_panel)
        form_vbox.setContentsMargins(35, 40, 35, 40)
        form_vbox.setSpacing(12)
        
        baslik = QLabel(f"🧑‍🍳 ŞEF {self.kullanici_adi.upper()}")
        baslik.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {RENKLER['vurgu']}; margin-bottom: 20px; border: none;")
        baslik.setAlignment(Qt.AlignCenter)
        form_vbox.addWidget(baslik)

        def etiket_olustur(metin):
            lbl = QLabel(metin)
            lbl.setStyleSheet(f"color: {RENKLER['metin_ikincil']}; font-weight: bold; font-size: 13px; margin-top: 5px; border:none;")
            return lbl

        self.in_ad = self.input_olustur("Tarifin ismini girin...")
        self.in_kat = QComboBox()
        self.in_kat.addItems(["Ana Yemek", "Tatlı", "Çorba", "Kahvaltılık", "Salata"])
        self.in_kat.setStyleSheet(self.input_stili() + f"QComboBox::drop-down {{ border: none; }} QComboBox QAbstractItemView {{ background: {RENKLER['kart']}; selection-background-color: {RENKLER['vurgu']}; }}")
        self.in_sure = self.input_olustur("Örn: 45", sayısal=True)
        
        self.in_malzemeler = QTextEdit()
        self.in_malzemeler.setPlaceholderText("Malzemeleri buraya yazın...")
        self.in_malzemeler.setStyleSheet(f"""
            QTextEdit {{ background-color: {RENKLER['arkaplan']}; border: 1px solid {RENKLER['kenarlik']}; border-radius: 10px; padding: 10px; color: {RENKLER['metin']}; font-size: 14px; }}
            QTextEdit:focus {{ border: 1px solid {RENKLER['vurgu']}; }}
        """)

        form_vbox.addWidget(etiket_olustur("TARİF İSMİ"))
        form_vbox.addWidget(self.in_ad)
        form_vbox.addWidget(etiket_olustur("KATEGORİ"))
        form_vbox.addWidget(self.in_kat)
        form_vbox.addWidget(etiket_olustur("SÜRE (DK)"))
        form_vbox.addWidget(self.in_sure)
        form_vbox.addWidget(etiket_olustur("MALZEMELER"))
        form_vbox.addWidget(self.in_malzemeler)

        form_vbox.addSpacing(15)

        self.btn_ekle = QPushButton("✨ YENİ TARİF EKLE")
        self.btn_ekle.clicked.connect(lambda: self.tarif_ekle(self.in_ad.text(), self.in_kat.currentText(), self.in_sure.text(), self.in_malzemeler.toPlainText()))
        self.btn_ekle.setStyleSheet(self.buton_stili('vurgu_dolu'))
        self.btn_ekle.setCursor(Qt.PointingHandCursor)
        self.btn_ekle.setFixedHeight(45)
        
        self.btn_guncelle = QPushButton("🔄 GÜNCELLE")
        self.btn_guncelle.clicked.connect(self.secili_guncelle)
        self.btn_guncelle.setStyleSheet(self.buton_stili('vurgu_bos'))
        self.btn_guncelle.setCursor(Qt.PointingHandCursor)
        self.btn_guncelle.setFixedHeight(45)
        
        self.btn_sil = QPushButton("🗑️ SİL")
        self.btn_sil.clicked.connect(self.secili_sil)
        self.btn_sil.setStyleSheet(self.buton_stili('tehlike'))
        self.btn_sil.setCursor(Qt.PointingHandCursor)
        self.btn_sil.setFixedHeight(45)
        
        self.btn_favori = QPushButton("❤️ FAVORİ")
        self.btn_favori.clicked.connect(self.secili_favori_yap)
        self.btn_favori.setStyleSheet(self.buton_stili('vurgu_bos'))
        self.btn_favori.setCursor(Qt.PointingHandCursor)
        self.btn_favori.setFixedHeight(45)
        
        yatay_butonlar = QHBoxLayout()
        yatay_butonlar.addWidget(self.btn_guncelle)
        yatay_butonlar.addWidget(self.btn_sil)
        yatay_butonlar.addWidget(self.btn_favori)

        form_vbox.addWidget(self.btn_ekle)
        form_vbox.addLayout(yatay_butonlar)

    def liste_paneli_tasarla(self):
        panel_layout = QVBoxLayout(self.sag_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(25)
        
        filtre_widget = QWidget()
        filtre_layout = QHBoxLayout(filtre_widget)
        filtre_layout.setContentsMargins(0, 0, 0, 0)
        filtre_layout.setSpacing(10)
        
        lbl_filtre = QLabel("Kategoriler:")
        lbl_filtre.setStyleSheet(f"color: {RENKLER['metin_ikincil']}; font-weight: bold; font-size: 15px; margin-right: 10px;")
        filtre_layout.addWidget(lbl_filtre)
        
        butonlar = ["Tümü", "Favorilerim", "Ana Yemek", "Tatlı", "Çorba", "Kahvaltılık", "Salata"]
        self.filtre_butonlari = []
        for metin in butonlar:
            btn = QPushButton(metin)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda ch, text=metin: self.filtre_degistir(text))
            filtre_layout.addWidget(btn)
            self.filtre_butonlari.append(btn)
            
        filtre_layout.addStretch()
        panel_layout.addWidget(filtre_widget)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(["ID", "TARİF ADI", "KATEGORİ", "SÜRE (DK)", "⭐ PUAN", "DURUM"])
        self.tablo.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tablo.setFocusPolicy(Qt.NoFocus)
        self.tablo.setShowGrid(False) 
        self.tablo.setStyleSheet(self.tablo_stili())
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.itemClicked.connect(self.formu_doldur)
        
        panel_layout.addWidget(self.tablo)
        
        puan_widget = QWidget()
        puan_layout = QHBoxLayout(puan_widget)
        puan_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_puan = QLabel("🌟 Seçili Tarife Puan Ver:")
        lbl_puan.setStyleSheet(f"color: {RENKLER['vurgu']}; font-weight: bold; font-size: 15px;")
        
        self.in_puan = QComboBox()
        self.in_puan.addItems(["5 Yıldız - Mükemmel", "4 Yıldız - Çok İyi", "3 Yıldız - Ortalama", "2 Yıldız - Kötü", "1 Yıldız - Berbat"])
        self.in_puan.setStyleSheet(self.input_stili() + f"QComboBox::drop-down {{ border: none; }} QComboBox QAbstractItemView {{ background: {RENKLER['kart']}; selection-background-color: {RENKLER['vurgu']}; }}")
        
        btn_puanla = QPushButton("DEĞERLENDİR")
        btn_puanla.setFixedHeight(45)
        btn_puanla.setCursor(Qt.PointingHandCursor)
        btn_puanla.setStyleSheet(self.buton_stili('vurgu_bos'))
        btn_puanla.clicked.connect(self.seciliye_puan_ver)
        
        puan_layout.addStretch()
        puan_layout.addWidget(lbl_puan)
        puan_layout.addWidget(self.in_puan)
        puan_layout.addWidget(btn_puanla)
        
        panel_layout.addWidget(puan_widget)

        self.filtre_degistir("Tümü")

    # --- METODLAR ---

    def tarif_ekle(self, ad, kat, sure, malzemeler, favori=False):
        if not ad or not sure: return
        self.son_id += 1
        t = Tarif(self.son_id, ad, kat, sure, malzemeler, favori)
        self.tarifler[self.son_id] = t
        
        # DB Kayıt
        self.db_tarif_kaydet(t)
        
        self.arayuz_guncelle(self.aktif_filtre)
        self.alanlari_temizle()

    def secili_guncelle(self):
        secili_satir = self.tablo.currentRow()
        if secili_satir < 0: return
        
        t_id = int(self.tablo.item(secili_satir, 0).text())
        if t_id in self.tarifler:
            t = self.tarifler[t_id]
            t.tarif_guncelle(self.in_ad.text(), self.in_kat.currentText(), self.in_sure.text(), self.in_malzemeler.toPlainText())
            
            # DB Güncelle
            self.db_tarif_kaydet(t)
            
            self.arayuz_guncelle(self.aktif_filtre)

    def secili_sil(self):
        secili_satir = self.tablo.currentRow()
        if secili_satir < 0: 
            QMessageBox.warning(self, "Uyarı", "Silmek için bir tarif seçmelisiniz.")
            return
            
        t_id = int(self.tablo.item(secili_satir, 0).text())
        cevap = QMessageBox.question(self, "Silme Onayı", "Bu tarifi silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if cevap == QMessageBox.Yes:
            if t_id in self.tarifler:
                # DB Sil
                self.db_tarif_sil(t_id)
                del self.tarifler[t_id]
                self.arayuz_guncelle(self.aktif_filtre)
                self.alanlari_temizle()

    def secili_favori_yap(self):
        secili_satir = self.tablo.currentRow()
        if secili_satir < 0: 
            QMessageBox.warning(self, "Uyarı", "İşlem yapmak için bir tarif seçmelisiniz.")
            return
            
        t_id = int(self.tablo.item(secili_satir, 0).text())
        if t_id in self.tarifler:
            t = self.tarifler[t_id]
            t.favori_gecis()
            self.db_tarif_kaydet(t)
            self.arayuz_guncelle(self.aktif_filtre)

    def hizli_favori_gecis(self, t_id):
        if t_id in self.tarifler:
            t = self.tarifler[t_id]
            t.favori_gecis()
            self.db_tarif_kaydet(t)
            self.arayuz_guncelle(self.aktif_filtre)

    def formu_doldur(self, item):
        satir = item.row()
        t_id = int(self.tablo.item(satir, 0).text())
        if t_id in self.tarifler:
            t = self.tarifler[t_id]
            self.in_ad.setText(t.tarif_adi)
            self.in_kat.setCurrentText(t.kategori)
            self.in_sure.setText(str(t.hazirlama_suresi))
            self.in_malzemeler.setText(t.malzemeler)

    def seciliye_puan_ver(self):
        secili_satir = self.tablo.currentRow()
        if secili_satir < 0:
            QMessageBox.warning(self, "Uyarı", "Değerlendirmek için önce listeden bir tarif seçmelisiniz.")
            return
            
        t_id = int(self.tablo.item(secili_satir, 0).text())
        puan_str = self.in_puan.currentText()[0]
        
        if t_id in self.tarifler:
            t = self.tarifler[t_id]
            t.puan_ekle(puan_str)
            
            # DB Güncelle (Puan listesi JSON olarak saklanır)
            self.db_tarif_kaydet(t)
            
            self.arayuz_guncelle(self.aktif_filtre)
            QMessageBox.information(self, "Başarılı", f"Tarife {puan_str} yıldız verdiniz!")

    def filtre_degistir(self, filtre):
        self.aktif_filtre = filtre
        for btn in self.filtre_butonlari:
            if btn.text() == filtre:
                btn.setStyleSheet(f"QPushButton {{ background-color: {RENKLER['vurgu']}; color: {RENKLER['arkaplan']}; font-weight: bold; border-radius: 18px; padding: 0 20px; border: none; }}")
            else:
                btn.setStyleSheet(f"QPushButton {{ background-color: {RENKLER['kart']}; color: {RENKLER['metin_ikincil']}; font-weight: bold; border-radius: 18px; padding: 0 20px; border: 1px solid {RENKLER['kenarlik']}; }} QPushButton:hover {{ color: {RENKLER['vurgu']}; border: 1px solid {RENKLER['vurgu']}; }}")
        self.arayuz_guncelle(filtre)

    def arayuz_guncelle(self, filtre="Tümü"):
        self.tablo.setRowCount(0)
        for t in self.tarifler.values():
            if filtre == "Favorilerim":
                if not t.favori:
                    continue
            elif filtre != "Tümü" and t.kategori != filtre:
                continue
                
            r = self.tablo.rowCount()
            self.tablo.insertRow(r)
            self.tablo.setRowHeight(r, 55)
            
            puan_yazisi = f"⭐ {t.ortalama_puan():.1f}" if t.puanlar else "Değerlendirilmedi"
            
            items = [str(t.tarif_id), t.tarif_adi, t.kategori, f"{t.hazirlama_suresi} dk", puan_yazisi]
            for i, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                if i == 1: 
                    font = QFont()
                    font.setBold(True)
                    font.setPointSize(10)
                    item.setFont(font)
                    item.setForeground(QColor(RENKLER['vurgu']))
                elif i == 4 and t.puanlar:
                    item.setForeground(QColor(RENKLER['vurgu'])) 
                    
                self.tablo.setItem(r, i, item)
                
            btn_fav = QPushButton("❤️ Favori" if t.favori else "🤍 Favori")
            if t.favori:
                btn_fav.setStyleSheet("QPushButton { background-color: transparent; color: #E53935; font-weight: bold; border: none; text-align: left; padding-left: 10px; } QPushButton:hover { color: #FF5252; }")
            else:
                btn_fav.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {RENKLER['metin_ikincil']}; font-weight: bold; border: none; text-align: left; padding-left: 10px; }} QPushButton:hover {{ color: {RENKLER['metin']}; }}")
            btn_fav.setCursor(Qt.PointingHandCursor)
            btn_fav.clicked.connect(lambda ch, uid=t.tarif_id: self.hizli_favori_gecis(uid))
            self.tablo.setCellWidget(r, 5, btn_fav)

    def alanlari_temizle(self):
        self.in_ad.clear()
        self.in_sure.clear()
        self.in_malzemeler.clear()

    # --- STİL ARAÇLARI ---

    def buton_stili(self, tur='vurgu_dolu'):
        if tur == 'vurgu_dolu':
            return f"""
                QPushButton {{ background-color: {RENKLER['vurgu']}; color: {RENKLER['arkaplan']}; font-weight: bold; font-size: 13px; border-radius: 10px; border: none; letter-spacing: 1px; }}
                QPushButton:hover {{ background-color: {RENKLER['vurgu_hover']}; }}
            """
        elif tur == 'vurgu_bos':
            return f"""
                QPushButton {{ background-color: transparent; border: 2px solid {RENKLER['vurgu']}; color: {RENKLER['vurgu']}; font-weight: bold; font-size: 13px; border-radius: 10px; letter-spacing: 1px; }}
                QPushButton:hover {{ background-color: {RENKLER['satir_secili']}; }}
            """
        elif tur == 'tehlike':
            return f"""
                QPushButton {{ background-color: transparent; border: 2px solid {RENKLER['sil']}; color: {RENKLER['sil']}; font-weight: bold; font-size: 13px; border-radius: 10px; letter-spacing: 1px; }}
                QPushButton:hover {{ background-color: rgba(229, 57, 53, 0.1); border: 2px solid {RENKLER['sil_hover']}; color: {RENKLER['sil_hover']};}}
            """

    def input_olustur(self, placeholder, sayısal=False):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(45)
        inp.setStyleSheet(self.input_stili())
        if sayısal: inp.setValidator(QIntValidator(1, 999))
        return inp

    def input_stili(self):
        return f"""
            QLineEdit, QComboBox {{ background-color: {RENKLER['arkaplan']}; border: 1px solid {RENKLER['kenarlik']}; border-radius: 10px; padding: 0 15px; color: {RENKLER['metin']}; font-size: 14px; }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {RENKLER['vurgu']}; }}
        """

    def tablo_stili(self):
        return f"""
            QTableWidget {{ background-color: transparent; border: none; color: {RENKLER['metin']}; font-size: 14px; }}
            QTableWidget::item {{ border-bottom: 1px solid {RENKLER['kenarlik']}; padding-left: 10px; }}
            QTableWidget::item:selected {{ background-color: {RENKLER['satir_secili']}; border-bottom: 1px solid {RENKLER['vurgu']}; color: {RENKLER['metin']}; }}
            QHeaderView::section {{ background-color: transparent; color: {RENKLER['metin_ikincil']}; font-weight: bold; font-size: 12px; border: none; border-bottom: 2px solid {RENKLER['kenarlik']}; padding: 10px; }}
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    login = LoginEkrani()
    if login.exec_() == QDialog.Accepted:
        pencere = LezzetPaneli(login.kullanici_adi)
        pencere.show()
        sys.exit(app.exec_())