import sys
import sqlite3
import datetime
import random
import os
import uuid
import json
import urllib.request

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget, 
                             QFrame, QGridLayout, QComboBox, QCalendarWidget, QScrollArea, QDialog, QDateEdit, QStackedWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

# ==========================================
# VERİLER
# ==========================================
CITIES_DATA = {'Adana': ['Aladağ', 'Ceyhan', 'Çukurova', 'Feke', 'İmamoğlu', 'Karaisalı', 'Karataş', 'Kozan', 'Pozantı', 'Saimbeyli', 'Sarıçam', 'Seyhan', 'Tufanbeyli', 'Yumurtalık', 'Yüreğir'], 'Adıyaman': ['Besni', 'Çelikhan', 'Gerger', 'Gölbaşı', 'Kahta', 'Merkez', 'Samsat', 'Sincik', 'Tut'], 'Afyonkarahisar': ['Başmakçı', 'Bayat', 'Bolvadin', 'Çay', 'Çobanlar', 'Dazkırı', 'Dinar', 'Emirdağ', 'Evciler', 'Hocalar', 'İhsaniye', 'İscehisar', 'Kızılören', 'Merkez', 'Sandıklı', 'Sinanpaşa', 'Sultandağı', 'Şuhut'], 'Ağrı': ['Diyadin', 'Doğubayazıt', 'Eleşkirt', 'Hamur', 'Merkez', 'Patnos', 'Taşlıçay', 'Tutak'], 'Amasya': ['Göynücek', 'Gümüşhacıköy', 'Hamamözü', 'Merkez', 'Merzifon', 'Suluova', 'Taşova'], 'Ankara': ['Akyurt', 'Altındağ', 'Ayaş', 'Bala', 'Beypazarı', 'Çamlıdere', 'Çankaya', 'Çubuk', 'Elmadağ', 'Etimesgut', 'Evren', 'Gölbaşı', 'Güdül', 'Haymana', 'Kahramankazan', 'Kalecik', 'Keçiören', 'Kızılcahamam', 'Mamak', 'Nallıhan', 'Polatlı', 'Pursaklar', 'Sincan', 'Şereflikoçhisar', 'Yenimahalle'], 'Antalya': ['Akseki', 'Aksu', 'Alanya', 'Demre', 'Döşemealtı', 'Elmalı', 'Finike', 'Gazipaşa', 'Gündoğmuş', 'İbradı', 'Kaş', 'Kemer', 'Kepez', 'Konyaaltı', 'Korkuteli', 'Kumluca', 'Manavgat', 'Muratpaşa', 'Serik'], 'Artvin': ['Ardanuç', 'Arhavi', 'Borçka', 'Hopa', 'Kemalpaşa', 'Merkez', 'Murgul', 'Şavşat', 'Yusufeli'], 'Aydın': ['Bozdoğan', 'Buharkent', 'Çine', 'Didim', 'Efeler', 'Germencik', 'İncirliova', 'Karacasu', 'Karpuzlu', 'Koçarlı', 'Köşk', 'Kuşadası', 'Kuyucak', 'Nazilli', 'Söke', 'Sultanhisar', 'Yenipazar'], 'Balıkesir': ['Altıeylül', 'Ayvalık', 'Balya', 'Bandırma', 'Bigadiç', 'Burhaniye', 'Dursunbey', 'Edremit', 'Erdek', 'Gömeç', 'Gönen', 'Havran', 'İvrindi', 'Karesi', 'Kepsut', 'Manyas', 'Marmara', 'Savaştepe', 'Sındırgı', 'Susurluk'], 'Bilecik': ['Bozüyük', 'Gölpazarı', 'İnhisar', 'Merkez', 'Osmaneli', 'Pazaryeri', 'Söğüt', 'Yenipazar'], 'Bingöl': ['Adaklı', 'Genç', 'Karlıova', 'Kiğı', 'Merkez', 'Solhan', 'Yayladere', 'Yedisu'], 'Bitlis': ['Adilcevaz', 'Ahlat', 'Güroymak', 'Hizan', 'Merkez', 'Mutki', 'Tatvan'], 'Bolu': ['Dörtdivan', 'Gerede', 'Göynük', 'Kıbrıscık', 'Mengen', 'Merkez', 'Mudurnu', 'Seben', 'Yeniçağa'], 'Burdur': ['Ağlasun', 'Altınyayla', 'Bucak', 'Çavdır', 'Çeltikçi', 'Gölhisar', 'Karamanlı', 'Kemer', 'Merkez', 'Tefenni', 'Yeşilova'], 'Bursa': ['Büyükorhan', 'Gemlik', 'Gürsu', 'Harmancık', 'İnegöl', 'İznik', 'Karacabey', 'Keles', 'Kestel', 'Mudanya', 'Mustafakemalpaşa', 'Nilüfer', 'Orhaneli', 'Orhangazi', 'Osmangazi', 'Yenişehir', 'Yıldırım'], 'Çanakkale': ['Ayvacık', 'Bayramiç', 'Biga', 'Bozcaada', 'Çan', 'Eceabat', 'Ezine', 'Gelibolu', 'Gökçeada', 'Lapseki', 'Merkez', 'Yenice'], 'Çankırı': ['Atkaracalar', 'Bayramören', 'Çerkeş', 'Eldivan', 'Ilgaz', 'Kızılırmak', 'Korgun', 'Kurşunlu', 'Merkez', 'Orta', 'Şabanözü', 'Yapraklı'], 'Çorum': ['Alaca', 'Bayat', 'Boğazkale', 'Dodurga', 'İskilip', 'Kargı', 'Laçin', 'Mecitözü', 'Merkez', 'Oğuzlar', 'Ortaköy', 'Osmancık', 'Sungurlu', 'Uğurludağ'], 'Denizli': ['Acıpayam', 'Babadağ', 'Baklan', 'Bekilli', 'Beyağaç', 'Bozkurt', 'Buldan', 'Çal', 'Çameli', 'Çardak', 'Çivril', 'Güney', 'Honaz', 'Kale', 'Merkezefendi', 'Pamukkale', 'Sarayköy', 'Serinhisar', 'Tavas'], 'Diyarbakır': ['Bağlar', 'Bismil', 'Çermik', 'Çınar', 'Çüngüş', 'Dicle', 'Eğil', 'Ergani', 'Hani', 'Hazro', 'Kayapınar', 'Kocaköy', 'Kulp', 'Lice', 'Silvan', 'Sur', 'Yenişehir'], 'Edirne': ['Enez', 'Havsa', 'İpsala', 'Keşan', 'Lalapaşa', 'Meriç', 'Merkez', 'Süloğlu', 'Uzunköprü'], 'Elazığ': ['Ağın', 'Alacakaya', 'Arıcak', 'Baskil', 'Karakoçan', 'Keban', 'Kovancılar', 'Maden', 'Merkez', 'Palu', 'Sivrice'], 'Erzincan': ['Çayırlı', 'İliç', 'Kemah', 'Kemaliye', 'Merkez', 'Otlukbeli', 'Refahiye', 'Tercan', 'Üzümlü'], 'Erzurum': ['Aşkale', 'Aziziye', 'Çat', 'Hınıs', 'Horasan', 'İspir', 'Karaçoban', 'Karayazı', 'Köprüköy', 'Narman', 'Oltu', 'Olur', 'Palandöken', 'Pasinler', 'Pazaryolu', 'Şenkaya', 'Tekman', 'Tortum', 'Uzundere', 'Yakutiye'], 'Eskişehir': ['Alpu', 'Beylikova', 'Çifteler', 'Günyüzü', 'Han', 'İnönü', 'Mahmudiye', 'Mihalgazi', 'Mihalıççık', 'Odunpazarı', 'Sarıcakaya', 'Seyitgazi', 'Sivrihisar', 'Tepebaşı'], 'Gaziantep': ['Araban', 'İslahiye', 'Karkamış', 'Nizip', 'Nurdağı', 'Oğuzeli', 'Şahinbey', 'Şehitkamil', 'Yavuzeli'], 'Giresun': ['Alucra', 'Bulancak', 'Çamoluk', 'Çanakçı', 'Dereli', 'Doğankent', 'Espiye', 'Eynesil', 'Görele', 'Güce', 'Keşap', 'Merkez', 'Piraziz', 'Şebinkarahisar', 'Tirebolu', 'Yağlıdere'], 'Gümüşhane': ['Kelkit', 'Köse', 'Kürtün', 'Merkez', 'Şiran', 'Torul'], 'Hakkari': ['Çukurca', 'Derecik', 'Merkez', 'Şemdinli', 'Yüksekova'], 'Hatay': ['Altınözü', 'Antakya', 'Arsuz', 'Belen', 'Defne', 'Dörtyol', 'Erzin', 'Hassa', 'İskenderun', 'Kırıkhan', 'Kumlu', 'Payas', 'Reyhanlı', 'Samandağ', 'Yayladağı'], 'Isparta': ['Aksu', 'Atabey', 'Eğirdir', 'Gelendost', 'Gönen', 'Keçiborlu', 'Merkez', 'Senirkent', 'Sütçüler', 'Şarkikaraağaç', 'Uluborlu', 'Yalvaç', 'Yenişarbademli'], 'Mersin': ['Akdeniz', 'Anamur', 'Aydıncık', 'Bozyazı', 'Çamlıyayla', 'Erdemli', 'Gülnar', 'Mezitli', 'Mut', 'Silifke', 'Tarsus', 'Toroslar', 'Yenişehir'], 'İstanbul': ['Adalar', 'Arnavutköy', 'Ataşehir', 'Avcılar', 'Bağcılar', 'Bahçelievler', 'Bakırköy', 'Başakşehir', 'Bayrampaşa', 'Beşiktaş', 'Beykoz', 'Beylikdüzü', 'Beyoğlu', 'Büyükçekmece', 'Çatalca', 'Çekmeköy', 'Esenler', 'Esenyurt', 'Eyüpsultan', 'Fatih', 'Gaziosmanpaşa', 'Güngören', 'Kadıköy', 'Kağıthane', 'Kartal', 'Küçükçekmece', 'Maltepe', 'Pendik', 'Sancaktepe', 'Sarıyer', 'Silivri', 'Sultanbeyli', 'Sultangazi', 'Şile', 'Şişli', 'Tuzla', 'Ümraniye', 'Üsküdar', 'Zeytinburnu'], 'İzmir': ['Aliağa', 'Balçova', 'Bayındır', 'Bayraklı', 'Bergama', 'Beydağ', 'Bornova', 'Buca', 'Çeşme', 'Çiğli', 'Dikili', 'Foça', 'Gaziemir', 'Güzelbahçe', 'Karabağlar', 'Karaburun', 'Karşıyaka', 'Kemalpaşa', 'Kınık', 'Kiraz', 'Konak', 'Menderes', 'Menemen', 'Narlıdere', 'Ödemiş', 'Seferihisar', 'Selçuk', 'Tire', 'Torbalı', 'Urla'], 'Kars': ['Akyaka', 'Arpaçay', 'Digor', 'Kağızman', 'Merkez', 'Sarıkamış', 'Selim', 'Susuz'], 'Kastamonu': ['Abana', 'Ağlı', 'Araç', 'Azdavay', 'Bozkurt', 'Cide', 'Çatalzeytin', 'Daday', 'Devrekani', 'Doğanyurt', 'Hanönü', 'İhsangazi', 'İnebolu', 'Küre', 'Merkez', 'Pınarbaşı', 'Seydiler', 'Şenpazar', 'Taşköprü', 'Tosya'], 'Kayseri': ['Akkışla', 'Bünyan', 'Develi', 'Felahiye', 'Hacılar', 'İncesu', 'Kocasinan', 'Melikgazi', 'Özvatan', 'Pınarbaşı', 'Sarıoğlan', 'Sarız', 'Talas', 'Tomarza', 'Yahyalı', 'Yeşilhisar'], 'Kırklareli': ['Babaeski', 'Demirköy', 'Kofçaz', 'Lüleburgaz', 'Merkez', 'Pehlivanköy', 'Pınarhisar', 'Vize'], 'Kırşehir': ['Akçakent', 'Akpınar', 'Boztepe', 'Çiçekdağı', 'Kaman', 'Merkez', 'Mucur'], 'Kocaeli': ['Başiskele', 'Çayırova', 'Darıca', 'Derince', 'Dilovası', 'Gebze', 'Gölcük', 'İzmit', 'Kandıra', 'Karamürsel', 'Kartepe', 'Körfez'], 'Konya': ['Ahırlı', 'Akören', 'Akşehir', 'Altınekin', 'Beyşehir', 'Bozkır', 'Cihanbeyli', 'Çeltik', 'Çumra', 'Derbent', 'Derebucak', 'Doğanhisar', 'Emirgazi', 'Ereğli', 'Güneysınır', 'Hadim', 'Halkapınar', 'Hüyük', 'Ilgın', 'Kadınhanı', 'Karapınar', 'Karatay', 'Kulu', 'Meram', 'Sarayönü', 'Selçuklu', 'Seydişehir', 'Taşkent', 'Tuzlukçu', 'Yalıhüyük', 'Yunak'], 'Kütahya': ['Altıntaş', 'Aslanapa', 'Çavdarhisar', 'Domaniç', 'Dumlupınar', 'Emet', 'Gediz', 'Hisarcık', 'Merkez', 'Pazarlar', 'Simav', 'Şaphane', 'Tavşanlı'], 'Malatya': ['Akçadağ', 'Arapgir', 'Arguvan', 'Battalgazi', 'Darende', 'Doğanşehir', 'Doğanyol', 'Hekimhan', 'Kale', 'Kuluncak', 'Pütürge', 'Yazıhan', 'Yeşilyurt'], 'Manisa': ['Ahmetli', 'Akhisar', 'Alaşehir', 'Demirci', 'Gölmarmara', 'Gördes', 'Kırkağaç', 'Köprübaşı', 'Kula', 'Salihli', 'Sarıgöl', 'Saruhanlı', 'Selendi', 'Soma', 'Şehzadeler', 'Turgutlu', 'Yunusemre'], 'Kahramanmaraş': ['Afşin', 'Andırın', 'Çağlayancerit', 'Dulkadiroğlu', 'Ekinözü', 'Elbistan', 'Göksun', 'Nurhak', 'Onikişubat', 'Pazarcık', 'Türkoğlu'], 'Mardin': ['Artuklu', 'Dargeçit', 'Derik', 'Kızıltepe', 'Mazıdağı', 'Midyat', 'Nusaybin', 'Ömerli', 'Savur', 'Yeşilli'], 'Muğla': ['Bodrum', 'Dalaman', 'Datça', 'Fethiye', 'Kavaklıdere', 'Köyceğiz', 'Marmaris', 'Menteşe', 'Milas', 'Ortaca', 'Seydikemer', 'Ula', 'Yatağan'], 'Muş': ['Bulanık', 'Hasköy', 'Korkut', 'Malazgirt', 'Merkez', 'Varto'], 'Nevşehir': ['Acıgöl', 'Avanos', 'Derinkuyu', 'Gülşehir', 'Hacıbektaş', 'Kozaklı', 'Merkez', 'Ürgüp'], 'Niğde': ['Altunhisar', 'Bor', 'Çamardı', 'Çiftlik', 'Merkez', 'Ulukışla'], 'Ordu': ['Akkuş', 'Altınordu', 'Aybastı', 'Çamaş', 'Çatalpınar', 'Çaybaşı', 'Fatsa', 'Gölköy', 'Gülyalı', 'Gürgentepe', 'İkizce', 'Kabadüz', 'Kabataş', 'Korgan', 'Kumru', 'Mesudiye', 'Perşembe', 'Ulubey', 'Ünye'], 'Rize': ['Ardeşen', 'Çamlıhemşin', 'Çayeli', 'Derepazarı', 'Fındıklı', 'Güneysu', 'Hemşin', 'İkizdere', 'İyidere', 'Kalkandere', 'Merkez', 'Pazar'], 'Sakarya': ['Adapazarı', 'Akyazı', 'Arifiye', 'Erenler', 'Ferizli', 'Geyve', 'Hendek', 'Karapürçek', 'Karasu', 'Kaynarca', 'Kocaali', 'Pamukova', 'Sapanca', 'Serdivan', 'Söğütlü', 'Taraklı'], 'Samsun': ['19 Mayıs', 'Alaçam', 'Asarcık', 'Atakum', 'Ayvacık', 'Bafra', 'Canik', 'Çarşamba', 'Havza', 'İlkadım', 'Kavak', 'Ladik', 'Salıpazarı', 'Tekkeköy', 'Terme', 'Vezirköprü', 'Yakakent'], 'Siirt': ['Baykan', 'Eruh', 'Kurtalan', 'Merkez', 'Pervari', 'Şirvan', 'Tillo'], 'Sinop': ['Ayancık', 'Boyabat', 'Dikmen', 'Durağan', 'Erfelek', 'Gerze', 'Merkez', 'Saraydüzü', 'Türkeli'], 'Sivas': ['Akıncılar', 'Altınyayla', 'Divriği', 'Doğanşar', 'Gemerek', 'Gölova', 'Gürün', 'Hafik', 'İmranlı', 'Kangal', 'Koyulhisar', 'Merkez', 'Suşehri', 'Şarkışla', 'Ulaş', 'Yıldızeli', 'Zara'], 'Tekirdağ': ['Çerkezköy', 'Çorlu', 'Ergene', 'Hayrabolu', 'Kapaklı', 'Malkara', 'Marmaraereğlisi', 'Muratlı', 'Saray', 'Süleymanpaşa', 'Şarköy'], 'Tokat': ['Almus', 'Artova', 'Başçiftlik', 'Erbaa', 'Merkez', 'Niksar', 'Pazar', 'Reşadiye', 'Sulusaray', 'Turhal', 'Yeşilyurt', 'Zile'], 'Trabzon': ['Akçaabat', 'Araklı', 'Arsin', 'Beşikdüzü', 'Çarşıbaşı', 'Çaykara', 'Dernekpazarı', 'Düzköy', 'Hayrat', 'Köprübaşı', 'Maçka', 'Of', 'Ortahisar', 'Sürmene', 'Şalpazarı', 'Tonya', 'Vakfıkebir', 'Yomra'], 'Tunceli': ['Çemişgezek', 'Hozat', 'Mazgirt', 'Merkez', 'Nazımiye', 'Ovacık', 'Pertek', 'Pülümür'], 'Şanlıurfa': ['Akçakale', 'Birecik', 'Bozova', 'Ceylanpınar', 'Eyyübiye', 'Halfeti', 'Haliliye', 'Harran', 'Hilvan', 'Karaköprü', 'Siverek', 'Suruç', 'Viranşehir'], 'Uşak': ['Banaz', 'Eşme', 'Karahallı', 'Merkez', 'Sivaslı', 'Ulubey'], 'Van': ['Bahçesaray', 'Başkale', 'Çaldıran', 'Çatak', 'Edremit', 'Erciş', 'Gevaş', 'Gürpınar', 'İpekyolu', 'Muradiye', 'Özalp', 'Saray', 'Tuşba'], 'Yozgat': ['Akdağmadeni', 'Aydıncık', 'Boğazlıyan', 'Çandır', 'Çayıralan', 'Çekerek', 'Kadışehri', 'Merkez', 'Saraykent', 'Sarıkaya', 'Sorgun', 'Şefaatli', 'Yenifakılı', 'Yerköy'], 'Zonguldak': ['Alaplı', 'Çaycuma', 'Devrek', 'Ereğli', 'Gökçebey', 'Kilimli', 'Kozlu', 'Merkez'], 'Aksaray': ['Ağaçören', 'Eskil', 'Gülağaç', 'Güzelyurt', 'Merkez', 'Ortaköy', 'Sarıyahşi', 'Sultanhanı'], 'Bayburt': ['Aydıntepe', 'Demirözü', 'Merkez'], 'Karaman': ['Ayrancı', 'Başyayla', 'Ermenek', 'Kazımkarabekir', 'Merkez', 'Sarıveliler'], 'Kırıkkale': ['Bahşılı', 'Balışeyh', 'Çelebi', 'Delice', 'Karakeçili', 'Keskin', 'Merkez', 'Sulakyurt', 'Yahşihan'], 'Batman': ['Beşiri', 'Gercüş', 'Hasankeyf', 'Kozluk', 'Merkez', 'Sason'], 'Şırnak': ['Beytüşşebap', 'Cizre', 'Güçlükonak', 'İdil', 'Merkez', 'Silopi', 'Uludere'], 'Bartın': ['Amasra', 'Kurucaşile', 'Merkez', 'Ulus'], 'Ardahan': ['Çıldır', 'Damal', 'Göle', 'Hanak', 'Merkez', 'Posof'], 'Iğdır': ['Aralık', 'Karakoyunlu', 'Merkez', 'Tuzluca'], 'Yalova': ['Altınova', 'Armutlu', 'Çınarcık', 'Çiftlikköy', 'Merkez', 'Termal'], 'Karabük': ['Eflani', 'Eskipazar', 'Merkez', 'Ovacık', 'Safranbolu', 'Yenice'], 'Kilis': ['Elbeyli', 'Merkez', 'Musabeyli', 'Polateli'], 'Osmaniye': ['Bahçe', 'Düziçi', 'Hasanbeyli', 'Kadirli', 'Merkez', 'Sumbas', 'Toprakkale'], 'Düzce': ['Akçakoca', 'Cumayeri', 'Çilimli', 'Gölyaka', 'Gümüşova', 'Kaynaşlı', 'Merkez', 'Yığılca']}
CITIES = sorted(list(CITIES_DATA.keys()))

CLINICS = [
    "Dahiliye (İç Hastalıkları)", "Kardiyoloji", "Nöroloji", "Cildiye (Dermatoloji)",
    "Göz Hastalıkları", "Kulak Burun Boğaz", "Ortopedi ve Travmatoloji",
    "Genel Cerrahi", "Üroloji", "Psikiyatri", "Kadın Hastalıkları ve Doğum", "Çocuk Sağlığı ve Hastalıkları",
    "Göğüs Hastalıkları", "Enfeksiyon Hastalıkları", "Beyin ve Sinir Cerrahisi", "Fizik Tedavi ve Rehabilitasyon"
]

SYMPTOMS = {
    "Kalp ağrısı, çarpıntı, nefes darlığı": "Kardiyoloji",
    "Ciltte kaşıntı, döküntü, kızarıklık": "Cildiye (Dermatoloji)",
    "Sürekli baş ağrısı, baş dönmesi, uyuşma": "Nöroloji",
    "Gözde bulanıklık, yanma, görme kaybı": "Göz Hastalıkları",
    "Boğaz ağrısı, kulak çınlaması, burun tıkanıklığı": "Kulak Burun Boğaz",
    "Eklem ağrısı, kemik sızlaması, bel ağrısı": "Ortopedi ve Travmatoloji",
    "Karın ağrısı, şişkinlik, hazımsızlık": "Dahiliye (İç Hastalıkları)",
    "İdrar yaparken yanma, sık idrara çıkma": "Üroloji",
    "Aşırı mutsuzluk, stres, uyku bozukluğu": "Psikiyatri",
    "Vücutta şişlik, apse, şiddetli karın ağrısı": "Genel Cerrahi",
    "Mide yanması, bulantı": "Dahiliye (İç Hastalıkları)",
    "Tansiyon yüksekliği veya düşüklüğü": "Kardiyoloji",
    "Unutkanlık, dikkat dağınıklığı": "Nöroloji",
    "Saç dökülmesi, kepek": "Cildiye (Dermatoloji)",
    "İşitme kaybı": "Kulak Burun Boğaz",
    "Diz kapağında ağrı": "Ortopedi ve Travmatoloji",
    "Böbrek ağrısı": "Üroloji",
    "Göz kanlanması": "Göz Hastalıkları",
    "Sürekli yorgunluk hissi": "Dahiliye (İç Hastalıkları)",
    "Panik atak belirtileri": "Psikiyatri",
    "Ateş, kuru öksürük, halsizlik": "Göğüs Hastalıkları",
    "Çocukta ateş, döküntü": "Çocuk Sağlığı ve Hastalıkları",
    "Gebelik takibi, adet düzensizliği": "Kadın Hastalıkları ve Doğum"
}

# ==========================================
# YARDIMCI FONKSİYONLAR (UTILS)
# ==========================================
def generate_random_sms_code():
    return str(random.randint(100000, 999999))

def generate_barcode(text, filename="temp_barcode"):
    if not BARCODE_AVAILABLE:
        return None
    CODE128 = barcode.get_barcode_class('code128')
    code = CODE128(text, writer=ImageWriter())
    return code.save(filename)

def clear_temp_files():
    if os.path.exists("temp_barcode.png"):
        try: os.remove("temp_barcode.png")
        except: pass

def get_hospitals_by_city_district(city, district):
    return [
        f"{district} Devlet Hastanesi",
        f"Özel {district} Şifa Hastanesi",
        f"Özel {district} Medikal Tıp Merkezi",
        f"{city} Şehir Hastanesi ({district} Polikliniği)",
        f"Özel {district} Hayat Hastanesi",
        f"{district} Eğitim ve Araştırma Hastanesi",
        f"Özel {city} Akademi Hastanesi",
        f"{district} Ağız ve Diş Sağlığı Merkezi"
    ]

def get_doctors_by_clinic(city, district, hospital, clinic):
    first_names = ["Ali", "Ayşe", "Mehmet", "Fatma", "Ahmet", "Zeynep", "Mustafa", "Elif", "Emre", "Esra", "Burak", "Büşra", "Can", "Ceren", "Deniz", "Derya", "Eren", "Eda", "Fatih", "Gizem", "Hakan", "Hatice", "İbrahim", "İrem", "Kaan", "Kübra", "Volkan", "Seda", "Cem", "Nur", "Onur", "Gökhan"]
    last_names = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Öztürk", "Aydın", "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Koç", "Kurt", "Özkan", "Şimşek", "Polat", "Öz", "Korkmaz", "Erdoğan", "Yavuz", "Can", "Güneş", "Tekin", "Turan", "Yücel"]
    
    # Gerçekçi benzersiz doktor dağılımı (hash of all parameters)
    seed_str = f"{city}{district}{hospital}{clinic}"
    seed = sum(ord(c)*i for i, c in enumerate(seed_str))
    random.seed(seed)
    
    doctors = []
    for _ in range(15):
        name = f"Dr. {random.choice(first_names)} {random.choice(last_names)}"
        if name not in doctors:
            doctors.append(name)
        
    random.seed()
    return doctors

def generate_pharmacies(city, district):
    """Günlük nöbetçi eczaneleri oluştur (tarihe ve ilçeye bağlı)"""
    today = datetime.datetime.now().date().strftime("%Y-%m-%d")
    seed_str = f"{today}{city}{district}"
    seed = sum(ord(c)*i for i, c in enumerate(seed_str))
    random.seed(seed)
    
    pharmacy_names = ["Şifa", "Merkez", "Sağlık", "Hayat", "Güneş", "Umut", "Yeni", "Halk", "Yıldız", "Özlem", "Güven", "Doğa"]
    streets = ["Atatürk Cad.", "Cumhuriyet Mah.", "İnönü Sok.", "Mevlana Cad.", "Fatih Mah.", "Yıldız Sok."]
    
    pharmacies = []
    for _ in range(3):
        name = f"{random.choice(pharmacy_names)} Eczanesi"
        address = f"{district}, {random.choice(streets)} No: {random.randint(1, 100)}"
        phone = f"0({random.randint(200, 400)}) {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        pharmacies.append({"name": name, "address": address, "phone": phone})
        
    random.seed()
    return pharmacies

def normalize_text(text):
    if not text: return ""
    return text.replace('I', 'ı').replace('İ', 'i').lower().replace('ş', 's').replace('ç', 'c').replace('ğ', 'g').replace('ü', 'u').replace('ö', 'o').replace('ı', 'i')

def get_current_location():
    try:
        try:
            req = urllib.request.Request("http://ip-api.com/json/")
            response = urllib.request.urlopen(req, timeout=3)
            data = json.loads(response.read().decode('utf-8'))
            city_raw = normalize_text(data.get("city", ""))
            region_raw = normalize_text(data.get("regionName", ""))
        except:
            req = urllib.request.Request("https://ipinfo.io/json")
            response = urllib.request.urlopen(req, timeout=3)
            data = json.loads(response.read().decode('utf-8'))
            city_raw = normalize_text(data.get("city", ""))
            region_raw = normalize_text(data.get("region", ""))
        
        detected_city = "İstanbul"
        
        for c in CITIES:
            c_norm = normalize_text(c)
            if c_norm in region_raw or c_norm in city_raw:
                detected_city = c
                break
                
        detected_district = CITIES_DATA.get(detected_city, ["Merkez"])[0]
        for d in CITIES_DATA.get(detected_city, []):
            if normalize_text(d) in city_raw:
                detected_district = d
                break
                
        return detected_city, detected_district
    except:
        return "İstanbul", "Kadıköy" # Varsayılan hata durumu

# ==========================================
# VERİTABANI YÖNETİMİ (DATABASE)
# ==========================================
DB_NAME = "mhrs_clone.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            tc TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            height REAL,
            weight REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tc TEXT,
            date TEXT,
            time TEXT,
            city TEXT,
            district TEXT,
            hospital TEXT,
            clinic TEXT,
            doctor TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(tc) REFERENCES users(tc)
        )
    ''')
    conn.commit()
    conn.close()

def get_user_count():
    conn = get_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return count

def add_user(tc, password, name, phone="", email="", height=0, weight=0):
    conn = get_connection()
    try:
        conn.cursor().execute(
            "INSERT INTO users (tc, password, name, phone, email, height, weight) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tc, password, name, phone, email, height, weight)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(tc, password=None):
    conn = get_connection()
    if password:
        user = conn.cursor().execute("SELECT * FROM users WHERE tc=? AND password=?", (tc, password)).fetchone()
    else:
        user = conn.cursor().execute("SELECT * FROM users WHERE tc=?", (tc,)).fetchone()
    conn.close()
    return user

def update_user_profile(tc, name, phone, email, height, weight):
    conn = get_connection()
    conn.cursor().execute("UPDATE users SET name=?, phone=?, email=?, height=?, weight=? WHERE tc=?", 
                          (name, phone, email, height, weight, tc))
    conn.commit()
    conn.close()

def update_password(tc, new_password):
    conn = get_connection()
    conn.cursor().execute("UPDATE users SET password=? WHERE tc=?", (new_password, tc))
    conn.commit()
    conn.close()

def check_cooldown(tc):
    conn = get_connection()
    row = conn.cursor().execute("SELECT created_at FROM appointments WHERE tc=? ORDER BY created_at DESC LIMIT 1", (tc,)).fetchone()
    conn.close()
    if row:
        last_time = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        diff = datetime.datetime.now() - last_time
        if diff.total_seconds() < 300:
            return False, 300 - int(diff.total_seconds())
    return True, 0

def add_appointment(tc, date, time, city, district, hospital, clinic, doctor):
    conn = get_connection()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO appointments (tc, date, time, city, district, hospital, clinic, doctor, status, created_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Aktif', ?)''', 
                   (tc, date, time, city, district, hospital, clinic, doctor, now_str))
    conn.commit()
    appt_id = cursor.lastrowid
    conn.close()
    return appt_id

def get_appointments(tc, status=None):
    conn = get_connection()
    if status:
        apps = conn.cursor().execute("SELECT * FROM appointments WHERE tc=? AND status=? ORDER BY date DESC, time DESC", (tc, status)).fetchall()
    else:
        apps = conn.cursor().execute("SELECT * FROM appointments WHERE tc=? ORDER BY date DESC, time DESC", (tc,)).fetchall()
    conn.close()
    return apps

def cancel_appointment(appt_id):
    conn = get_connection()
    conn.cursor().execute("UPDATE appointments SET status='İptal Edildi' WHERE id=?", (appt_id,))
    conn.commit()
    conn.close()

def get_booked_times(date, doctor):
    conn = get_connection()
    times = [row[0] for row in conn.cursor().execute("SELECT time FROM appointments WHERE date=? AND doctor=? AND status='Aktif'", (date, doctor)).fetchall()]
    conn.close()
    
    # Gerçekçi görünmesi için rastgele (ama doktor ve güne özel deterministik) bazı saatleri kırmızı (dolu) yapalım
    seed_str = f"{date}{doctor}"
    seed = sum(ord(c)*i for i, c in enumerate(seed_str))
    random.seed(seed)
    
    all_times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
    pre_booked_count = random.randint(5, 10) # 5 ile 10 arası saat dolu gelsin
    pre_booked = random.sample(all_times, pre_booked_count)
    for t in pre_booked:
        if t not in times:
            times.append(t)
            
    random.seed()
    return times

def get_favorite_hospitals(tc):
    conn = get_connection()
    rows = conn.cursor().execute('''
        SELECT city, district, hospital, COUNT(*) as c 
        FROM appointments 
        WHERE tc=? AND status='Aktif' OR status='Geçmiş'
        GROUP BY hospital 
        ORDER BY c DESC LIMIT 3
    ''', (tc,)).fetchall()
    conn.close()
    return rows

def has_upcoming_appointment(tc):
    conn = get_connection()
    now = datetime.datetime.now()
    apps = conn.cursor().execute("SELECT date, time FROM appointments WHERE tc=? AND status='Aktif'", (tc,)).fetchall()
    conn.close()
    
    for date_str, time_str in apps:
        app_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        diff = app_dt - now
        if 0 <= diff.total_seconds() <= 86400: # 24 hours
            return True, date_str, time_str
    return False, None, None

# ==========================================
# STİLLER (QSS)
# ==========================================
def get_global_style(font_size_modifier=0):
    base_font = 14 + font_size_modifier
    h1_font = 24 + font_size_modifier
    h2_font = 18 + font_size_modifier
    
    return f"""
    QWidget {{ background-color: #EBF5FB; font-family: 'Segoe UI', Arial, sans-serif; color: #2C3E50; }}
    QPushButton {{ background-color: #3498DB; color: white; border: none; border-radius: 8px; padding: 10px; font-weight: bold; font-size: {base_font}px; }}
    QPushButton:hover {{ background-color: #2980B9; }}
    QPushButton:pressed {{ background-color: #1F618D; }}
    QPushButton:disabled {{ background-color: #BDC3C7; color: #7F8C8D; }}
    QPushButton#btn_danger {{ background-color: #E74C3C; }}
    QPushButton#btn_danger:hover {{ background-color: #C0392B; }}
    QLineEdit, QComboBox, QDateEdit {{ background-color: white; border: 2px solid #D6EAF8; border-radius: 8px; padding: 8px; font-size: {base_font}px; color: #34495E; }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{ border: 2px solid #3498DB; }}
    QComboBox::drop-down {{ border: 0px; }}
    QScrollArea {{ border: none; background-color: transparent; }}
    QScrollArea > QWidget > QWidget {{ background-color: transparent; }}
    QFrame#card {{ background-color: white; border-radius: 15px; border: 1px solid #D6EAF8; }}
    QFrame#auth_card {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E1F5FE, stop:1 #FFFFFF);
        border-radius: 20px;
        border: 2px solid #81D4FA;
    }}
    QLabel#h1 {{ font-size: {h1_font}px; font-weight: bold; color: #2C3E50; }}
    QLabel#h2 {{ font-size: {h2_font}px; font-weight: bold; color: #3498DB; }}
    QLabel#info_text {{ font-size: {base_font}px; color: #7F8C8D; }}
    QPushButton#time_btn_green {{ background-color: #2ECC71; color: white; border-radius: 5px; font-weight: bold; }}
    QPushButton#time_btn_green:hover {{ background-color: #27AE60; }}
    QPushButton#time_btn_red {{ background-color: #E74C3C; color: white; border-radius: 5px; font-weight: bold; }}
    QTabWidget::pane {{ border: 1px solid #D6EAF8; background: white; border-radius: 8px; }}
    QTabBar::tab {{ background: #EBF5FB; border: 1px solid #D6EAF8; padding: 10px; border-top-left-radius: 8px; border-top-right-radius: 8px; min-width: 100px; font-size: {base_font}px; }}
    QTabBar::tab:selected {{ background: white; border-bottom-color: white; font-weight: bold; color: #3498DB; }}
    QTabBar::tab:!selected {{ margin-top: 2px; }}
    """

# ==========================================
# ARAYÜZ (GUI) - Sayfalar
# ==========================================
class ProfilePage(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout(self)
        title = QLabel("Profilim"); title.setObjectName("h1")
        layout.addWidget(title)
        form_layout = QGridLayout()
        
        self.val_tc = QLabel(self.main_app.current_user["tc"])
        self.input_name = QLineEdit()
        self.input_phone = QLineEdit()
        self.input_email = QLineEdit()
        self.input_height = QLineEdit()
        self.input_weight = QLineEdit()
        
        form_layout.addWidget(QLabel("TC Kimlik:"), 0, 0); form_layout.addWidget(self.val_tc, 0, 1)
        form_layout.addWidget(QLabel("Ad Soyad:"), 1, 0); form_layout.addWidget(self.input_name, 1, 1)
        form_layout.addWidget(QLabel("Telefon:"), 2, 0); form_layout.addWidget(self.input_phone, 2, 1)
        form_layout.addWidget(QLabel("E-posta:"), 3, 0); form_layout.addWidget(self.input_email, 3, 1)
        form_layout.addWidget(QLabel("Boy (cm):"), 4, 0); form_layout.addWidget(self.input_height, 4, 1)
        form_layout.addWidget(QLabel("Kilo (kg):"), 5, 0); form_layout.addWidget(self.input_weight, 5, 1)
        
        layout.addLayout(form_layout)
        save_btn = QPushButton("Bilgileri Kaydet")
        save_btn.clicked.connect(self.save_profile)
        layout.addWidget(save_btn)
        layout.addStretch()
        self.load_profile()

    def load_profile(self):
        user = get_user(self.main_app.current_user["tc"])
        if user:
            self.input_name.setText(user[2])
            self.input_phone.setText(user[3] if user[3] else "")
            self.input_email.setText(user[4] if user[4] else "")
            self.input_height.setText(str(user[5]) if user[5] else "")
            self.input_weight.setText(str(user[6]) if user[6] else "")

    def save_profile(self):
        try:
            h = float(self.input_height.text()) if self.input_height.text() else 0.0
            w = float(self.input_weight.text()) if self.input_weight.text() else 0.0
        except ValueError:
            QMessageBox.warning(self, "Hata", "Boy ve Kilo sayısal olmalıdır.")
            return
        update_user_profile(self.main_app.current_user["tc"], self.input_name.text(), self.input_phone.text(), self.input_email.text(), h, w)
        self.main_app.current_user["name"] = self.input_name.text()
        QMessageBox.information(self, "Başarılı", "Profiliniz güncellendi.")

class AppointmentPage(QWidget):
    def __init__(self, main_app, initial_clinic=None, initial_hosp=None):
        super().__init__()
        self.main_app = main_app
        self.initial_clinic = initial_clinic
        self.initial_hosp = initial_hosp
        main_layout = QVBoxLayout(self)
        
        title = QLabel("Randevu Al"); title.setObjectName("h1")
        main_layout.addWidget(title)
        
        filter_layout = QGridLayout()
        self.combo_city = QComboBox()
        self.combo_city.addItems(CITIES)
        self.combo_city.currentTextChanged.connect(self.update_districts)
        
        self.combo_district = QComboBox()
        self.combo_clinic = QComboBox()
        self.combo_clinic.addItems(CLINICS)
        if self.initial_clinic:
            self.combo_clinic.setCurrentText(self.initial_clinic)
            
        self.combo_hospital = QComboBox()
        self.combo_doctor = QComboBox()
        
        self.combo_district.currentTextChanged.connect(self.update_hospitals)
        self.combo_hospital.currentTextChanged.connect(self.update_doctors)
        self.combo_clinic.currentTextChanged.connect(self.update_doctors)
        
        filter_layout.addWidget(QLabel("İl:"), 0, 0); filter_layout.addWidget(self.combo_city, 0, 1)
        filter_layout.addWidget(QLabel("İlçe:"), 0, 2); filter_layout.addWidget(self.combo_district, 0, 3)
        filter_layout.addWidget(QLabel("Klinik:"), 1, 0); filter_layout.addWidget(self.combo_clinic, 1, 1)
        filter_layout.addWidget(QLabel("Hastane:"), 1, 2); filter_layout.addWidget(self.combo_hospital, 1, 3)
        filter_layout.addWidget(QLabel("Hekim:"), 2, 0); filter_layout.addWidget(self.combo_doctor, 2, 1)
        
        # Tarih Aralığı
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate())
        self.date_start.setMinimumDate(QDate.currentDate())
        self.date_start.setMaximumDate(QDate.currentDate().addDays(15))
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate().addDays(3))
        self.date_end.setMinimumDate(QDate.currentDate())
        self.date_end.setMaximumDate(QDate.currentDate().addDays(15))
        
        filter_layout.addWidget(QLabel("Başlangıç Tarihi:"), 3, 0); filter_layout.addWidget(self.date_start, 3, 1)
        filter_layout.addWidget(QLabel("Bitiş Tarihi:"), 3, 2); filter_layout.addWidget(self.date_end, 3, 3)
        
        search_btn = QPushButton("Uygun Saatleri Ara")
        search_btn.clicked.connect(self.load_times)
        filter_layout.addWidget(search_btn, 4, 0, 1, 4)
        
        main_layout.addLayout(filter_layout)
        
        # Sonuçlar
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.times_widget = QWidget()
        self.times_layout = QVBoxLayout(self.times_widget)
        self.scroll_area.setWidget(self.times_widget)
        main_layout.addWidget(self.scroll_area)
        
        if self.initial_hosp:
            self.combo_city.setCurrentText(self.initial_hosp[0])
            self.update_districts(self.initial_hosp[0])
            self.combo_district.setCurrentText(self.initial_hosp[1])
            self.combo_hospital.setCurrentText(self.initial_hosp[2])
        else:
            detected_city, detected_district = get_current_location()
            self.combo_city.setCurrentText(detected_city)
            self.update_districts(detected_city)
            self.combo_district.setCurrentText(detected_district)

    def update_districts(self, city):
        self.combo_district.clear()
        if city in CITIES_DATA:
            self.combo_district.addItems(CITIES_DATA[city])

    def update_hospitals(self, district):
        city = self.combo_city.currentText()
        if not district: return
        self.combo_hospital.clear()
        self.combo_hospital.addItems(get_hospitals_by_city_district(city, district))

    def update_doctors(self):
        city = self.combo_city.currentText()
        district = self.combo_district.currentText()
        clinic = self.combo_clinic.currentText()
        hospital = self.combo_hospital.currentText()
        if not clinic or not hospital: return
        self.combo_doctor.clear()
        self.combo_doctor.addItems(get_doctors_by_clinic(city, district, hospital, clinic))

    def load_times(self):
        for i in reversed(range(self.times_layout.count())): 
            w = self.times_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        doctor = self.combo_doctor.currentText()
        if not doctor: return
        
        d_start = self.date_start.date()
        d_end = self.date_end.date()
        
        if d_start > d_end:
            QMessageBox.warning(self, "Hata", "Başlangıç tarihi bitiş tarihinden büyük olamaz.")
            return

        days = d_start.daysTo(d_end)
        
        times_pool = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
        
        for i in range(days + 1):
            curr_date = d_start.addDays(i).toString("yyyy-MM-dd")
            booked_times = get_booked_times(curr_date, doctor)
            
            day_frame = QFrame()
            day_layout = QVBoxLayout(day_frame)
            day_layout.addWidget(QLabel(f"<b>Tarih: {curr_date}</b>"))
            
            grid = QGridLayout()
            row, col = 0, 0
            for t in times_pool:
                btn = QPushButton(t)
                if t in booked_times:
                    btn.setObjectName("time_btn_red")
                    btn.setEnabled(False)
                else:
                    btn.setObjectName("time_btn_green")
                    btn.clicked.connect(lambda checked, c_d=curr_date, time=t: self.book_appointment(c_d, time))
                grid.addWidget(btn, row, col)
                col += 1
                if col > 6: col = 0; row += 1
                
            day_layout.addLayout(grid)
            self.times_layout.addWidget(day_frame)
            
        self.times_layout.addStretch()

    def book_appointment(self, date_str, time):
        tc = self.main_app.current_user["tc"]
        can_book, remaining = check_cooldown(tc)
        if not can_book:
            QMessageBox.warning(self, "Bekleme Süresi", f"Yeni bir randevu almak için {remaining} saniye beklemelisiniz.")
            return

        city = self.combo_city.currentText()
        dist = self.combo_district.currentText()
        hosp = self.combo_hospital.currentText()
        clin = self.combo_clinic.currentText()
        doc = self.combo_doctor.currentText()
        
        reply = QMessageBox.question(self, "Onay", f"{date_str} {time} tarihinde {doc} için randevu almak istiyor musunuz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            appt_id = add_appointment(tc, date_str, time, city, dist, hosp, clin, doc)
            self.load_times()
            self.show_appointment_card(appt_id, date_str, time, hosp, clin, doc)

    def show_appointment_card(self, appt_id, date, time, hosp, clin, doc):
        dialog = QDialog(self)
        dialog.setWindowTitle("MediLife - Bilgi Kartı")
        dialog.setFixedSize(450, 600)
        dialog.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(dialog)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("RANDEVU ONAYLANDI")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #27AE60;")
        
        info_box = QFrame()
        info_box.setStyleSheet("background-color: #EBF5FB; border-radius: 10px; padding: 15px;")
        info_layout = QVBoxLayout(info_box)
        info_layout.addWidget(QLabel(f"<b>Tarih:</b> {date}"))
        info_layout.addWidget(QLabel(f"<b>Saat:</b> {time}"))
        info_layout.addWidget(QLabel(f"<b>Hastane:</b> {hosp}"))
        info_layout.addWidget(QLabel(f"<b>Klinik:</b> {clin}"))
        info_layout.addWidget(QLabel(f"<b>Hekim:</b> {doc}"))
        info_layout.addWidget(QLabel("<b>Kat:</b> 2  <b>Oda:</b> 204"))
        
        barcode_label = QLabel()
        random_hex = uuid.uuid4().hex[:8].upper()
        barcode_str = f"ML-{random_hex}-{appt_id}"
        
        try:
            barcode_path = generate_barcode(barcode_str)
            if barcode_path:
                pixmap = QPixmap(barcode_path).scaled(350, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                barcode_label.setPixmap(pixmap)
                barcode_label.setAlignment(Qt.AlignCenter)
        except Exception as e:
            barcode_label.setText(f"[Barkod Hatası: {e}]")
            barcode_label.setAlignment(Qt.AlignCenter)
            
        ok_btn = QPushButton("Tamam")
        ok_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(title)
        layout.addWidget(info_box)
        layout.addWidget(barcode_label)
        layout.addWidget(QLabel(barcode_str, alignment=Qt.AlignCenter))
        layout.addWidget(ok_btn)
        dialog.exec_()

class MyAppointmentsPage(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout(self)
        title = QLabel("Randevularım"); title.setObjectName("h1")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        self.tab_active = QWidget(); self.tab_cancelled = QWidget(); self.tab_past = QWidget()
        self.tabs.addTab(self.tab_active, "Aktif Randevular")
        self.tabs.addTab(self.tab_cancelled, "İptal Edilenler")
        self.tabs.addTab(self.tab_past, "Geçmiş Randevular")
        layout.addWidget(self.tabs)
        
    def refresh_data(self):
        self.setup_tab(self.tab_active, "Aktif")
        self.setup_tab(self.tab_cancelled, "İptal Edildi")
        self.setup_tab(self.tab_past, "Geçmiş")
        
    def setup_tab(self, tab, status):
        if tab.layout(): QWidget().setLayout(tab.layout())
        layout = QVBoxLayout()
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); content_layout = QVBoxLayout(content)
        
        appointments = get_appointments(self.main_app.current_user["tc"])
        count = 0
        now = datetime.datetime.now()
        
        for app in appointments:
            app_id, tc, date, time, city, dist, hosp, clin, doc, db_status, _ = app
            app_dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            actual_status = "Geçmiş" if (db_status == "Aktif" and app_dt < now) else db_status
                
            if actual_status != status: continue
            count += 1
            card = QFrame(); card.setObjectName("card"); card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(f"<b>Tarih/Saat:</b> {date} - {time}"))
            card_layout.addWidget(QLabel(f"<b>Hastane:</b> {hosp}"))
            card_layout.addWidget(QLabel(f"<b>Klinik:</b> {clin} - {doc}"))
            
            if status == "Aktif":
                cancel_btn = QPushButton("Randevuyu İptal Et")
                cancel_btn.setObjectName("btn_danger")
                cancel_btn.clicked.connect(lambda checked, aid=app_id: self.cancel_appointment(aid))
                card_layout.addWidget(cancel_btn)
                
            content_layout.addWidget(card)
            
        if count == 0: content_layout.addWidget(QLabel("Bu kategoride randevunuz bulunmamaktadır."))
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        tab.setLayout(layout)

    def cancel_appointment(self, appt_id):
        if QMessageBox.question(self, "Emin misiniz?", "Randevuyu iptal etmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            cancel_appointment(appt_id)
            QMessageBox.information(self, "Başarılı", "Randevunuz iptal edildi.")
            self.refresh_data()

class SymptomsPage(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout(self)
        title = QLabel("Neyim Var?"); title.setObjectName("h1")
        layout.addWidget(title)
        
        desc = QLabel("Lütfen yaşadığınız en belirgin semptomu seçiniz. Sistem sizi uygun kliniğe yönlendirecektir.")
        desc.setObjectName("info_text")
        layout.addWidget(desc)
        
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); content_layout = QGridLayout(content)
        
        row, col = 0, 0
        for symptom, clinic in SYMPTOMS.items():
            btn = QPushButton(symptom)
            btn.setStyleSheet("background-color: white; color: #2C3E50; border: 1px solid #D6EAF8; text-align: left;")
            btn.clicked.connect(lambda checked, c=clinic, s=symptom: self.suggest_clinic(s, c))
            content_layout.addWidget(btn, row, col)
            col += 1
            if col > 1: col = 0; row += 1
                
        content_layout.setRowStretch(row + 1, 1)
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def suggest_clinic(self, symptom, clinic):
        if QMessageBox.question(self, "Öneri", f"'{symptom}' şikayetiniz için <b>{clinic}</b> bölümüne görünmeniz önerilir.<br>Hemen randevu almak ister misiniz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) == QMessageBox.Yes:
            self.main_app.open_appointment_with_clinic(clinic)

class PharmaciesPage(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout(self)
        title = QLabel("Nöbetçi Eczaneler"); title.setObjectName("h1")
        layout.addWidget(title)
        
        filter_layout = QHBoxLayout()
        self.combo_city = QComboBox()
        self.combo_city.addItems(CITIES)
        self.combo_city.currentTextChanged.connect(self.update_districts)
        
        self.combo_district = QComboBox()
        self.combo_district.currentTextChanged.connect(self.load_pharmacies)
        
        filter_layout.addWidget(QLabel("İl:")); filter_layout.addWidget(self.combo_city)
        filter_layout.addWidget(QLabel("İlçe:")); filter_layout.addWidget(self.combo_district)
        layout.addLayout(filter_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        
        detected_city, detected_district = get_current_location()
        self.combo_city.setCurrentText(detected_city)
        self.update_districts(detected_city)
        self.combo_district.setCurrentText(detected_district)

    def update_districts(self, city):
        self.combo_district.clear()
        if city in CITIES_DATA:
            self.combo_district.addItems(CITIES_DATA[city])

    def load_pharmacies(self):
        for i in reversed(range(self.content_layout.count())): 
            w = self.content_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        city = self.combo_city.currentText()
        district = self.combo_district.currentText()
        if not district: return
        
        pharms = generate_pharmacies(city, district)
        for p in pharms:
            card = QFrame(); card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            l1 = QLabel(f"<b>{p['name']}</b>"); l1.setObjectName("h2")
            card_layout.addWidget(l1)
            card_layout.addWidget(QLabel(f"📍 {p['address']}"))
            card_layout.addWidget(QLabel(f"📞 {p['phone']}"))
            self.content_layout.addWidget(card)
        self.content_layout.addStretch()



class FavoritesPage(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout(self)
        title = QLabel("Favorilerim"); title.setObjectName("h1")
        layout.addWidget(title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)

    def load_favorites(self):
        for i in reversed(range(self.content_layout.count())): 
            w = self.content_layout.itemAt(i).widget()
            if w: w.setParent(None)
            
        tc = self.main_app.current_user["tc"]
        favs = get_favorite_hospitals(tc)
        
        if not favs:
            self.content_layout.addWidget(QLabel("Henüz yeterli randevu geçmişiniz bulunmuyor."))
        else:
            for city, district, hosp, count in favs:
                card = QFrame(); card.setObjectName("card")
                card_layout = QHBoxLayout(card)
                card_layout.addWidget(QLabel(f"⭐ <b>{hosp}</b> ({count} Randevu)"))
                btn = QPushButton("Randevu Al")
                btn.clicked.connect(lambda checked, c=city, d=district, hs=hosp: self.main_app.open_appointment_with_hospital(c, d, hs))
                card_layout.addStretch()
                card_layout.addWidget(btn)
                self.content_layout.addWidget(card)
                
        self.content_layout.addStretch()

class RatingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MediLife - Puan Ver")
        self.setFixedSize(300, 150)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Lütfen uygulamayı değerlendirin:"))
        
        stars_layout = QHBoxLayout()
        for i in range(1, 6):
            btn = QPushButton("⭐")
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("font-size: 20px; background: transparent; border: 1px solid #BDC3C7; border-radius: 20px;")
            btn.clicked.connect(lambda checked, val=i: self.rate(val))
            stars_layout.addWidget(btn)
        layout.addLayout(stars_layout)
        
    def rate(self, val):
        QMessageBox.information(self, "Teşekkürler", f"Bize {val} yıldız verdiniz. Değerlendirmeniz için teşekkür ederiz!")
        self.accept()

class AboutPage(QWidget):
    def __init__(self, main_app):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("MediLife"); title.setObjectName("h1"); title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel("Modern, hızlı ve güvenilir randevu sistemi.\nTüm hakları saklıdır © 2026")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        btn_rate = QPushButton("⭐ Uygulamayı Puanla")
        btn_rate.clicked.connect(self.show_rating)
        
        btn_share = QPushButton("🔗 Uygulamayı Paylaş")
        btn_share.clicked.connect(self.share_app)
        
        layout.addWidget(btn_rate)
        layout.addWidget(btn_share)

    def show_rating(self):
        dialog = RatingDialog(self)
        dialog.exec_()
        
    def share_app(self):
        QApplication.clipboard().setText("https://medilife.app")
        QMessageBox.information(self, "Paylaş", "Uygulama bağlantısı (https://medilife.app) panoya kopyalandı!")

class SettingsPage(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        layout = QVBoxLayout(self)
        title = QLabel("Ayarlar"); title.setObjectName("h1")
        layout.addWidget(title)
        
        form = QHBoxLayout()
        form.addWidget(QLabel("Metin Boyutu:"))
        self.combo_size = QComboBox()
        self.combo_size.addItems(["Küçük", "Normal", "Büyük"])
        self.combo_size.setCurrentText("Normal")
        self.combo_size.currentTextChanged.connect(self.change_font_size)
        form.addWidget(self.combo_size)
        form.addStretch()
        
        layout.addLayout(form)
        layout.addStretch()

    def change_font_size(self, size_text):
        modifier = 0
        if size_text == "Küçük": modifier = -2
        elif size_text == "Büyük": modifier = 4
        
        self.main_app.app.setStyleSheet(get_global_style(modifier))


# ==========================================
# GİRİŞ / KAYIT EKRANI (AUTH)
# ==========================================
class AuthWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("MediLife - Giriş")
        self.resize(450, 550)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("MediLife Sistemi"); title.setObjectName("h1"); title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title); main_layout.addSpacing(20)
        
        self.card = QFrame(); self.card.setObjectName("auth_card"); self.card.setFixedSize(400, 480)
        card_layout = QVBoxLayout(self.card)
        self.tabs = QTabWidget()
        
        # GİRİŞ TAB
        self.tab_login = QWidget(); login_layout = QVBoxLayout(self.tab_login); login_layout.setAlignment(Qt.AlignTop); login_layout.addSpacing(20)
        self.tc_input = QLineEdit(); self.tc_input.setPlaceholderText("TC Kimlik Numarası"); self.tc_input.setMaxLength(11)
        self.pass_input = QLineEdit(); self.pass_input.setPlaceholderText("Şifre"); self.pass_input.setEchoMode(QLineEdit.Password)
        login_btn = QPushButton("Giriş Yap"); login_btn.clicked.connect(self.handle_login)
        login_layout.addWidget(self.tc_input); login_layout.addSpacing(10); login_layout.addWidget(self.pass_input); login_layout.addSpacing(20); login_layout.addWidget(login_btn)
        login_layout.addStretch()
        self.tabs.addTab(self.tab_login, "Giriş Yap")
        
        # KAYIT TAB (Her zaman açık)
        self.tab_register = QWidget(); reg_layout = QVBoxLayout(self.tab_register); reg_layout.setAlignment(Qt.AlignTop); reg_layout.addSpacing(20)
        self.reg_tc = QLineEdit(); self.reg_tc.setPlaceholderText("TC Kimlik Numarası"); self.reg_tc.setMaxLength(11)
        self.reg_name = QLineEdit(); self.reg_name.setPlaceholderText("Ad Soyad")
        self.reg_phone = QLineEdit(); self.reg_phone.setPlaceholderText("Telefon Numarası")
        self.reg_pass = QLineEdit(); self.reg_pass.setPlaceholderText("Şifre"); self.reg_pass.setEchoMode(QLineEdit.Password)
        
        self.send_reg_sms_btn = QPushButton("Telefonu Doğrula ve Kayıt Ol")
        self.send_reg_sms_btn.clicked.connect(self.send_reg_sms)
        
        self.reg_sms_input = QLineEdit(); self.reg_sms_input.setPlaceholderText("SMS Kodu"); self.reg_sms_input.hide()
        self.reg_confirm_btn = QPushButton("Kaydı Tamamla"); self.reg_confirm_btn.clicked.connect(self.handle_register); self.reg_confirm_btn.hide()
        
        reg_layout.addWidget(self.reg_tc); reg_layout.addWidget(self.reg_name); reg_layout.addWidget(self.reg_phone); reg_layout.addWidget(self.reg_pass)
        reg_layout.addSpacing(10); reg_layout.addWidget(self.send_reg_sms_btn); reg_layout.addWidget(self.reg_sms_input); reg_layout.addWidget(self.reg_confirm_btn)
        reg_layout.addStretch()
        self.tabs.addTab(self.tab_register, "Kayıt Ol")
            
        # ŞİFRE UNUTTUM TAB
        self.tab_forgot = QWidget(); forgot_layout = QVBoxLayout(self.tab_forgot); forgot_layout.setAlignment(Qt.AlignTop); forgot_layout.addSpacing(20)
        self.forgot_tc = QLineEdit(); self.forgot_tc.setPlaceholderText("TC Kimlik Numarası"); self.forgot_tc.setMaxLength(11)
        self.send_sms_btn = QPushButton("SMS Kodu Gönder"); self.send_sms_btn.clicked.connect(self.send_sms)
        self.sms_code_input = QLineEdit(); self.sms_code_input.setPlaceholderText("SMS Kodunu Giriniz"); self.sms_code_input.hide()
        self.new_pass_input = QLineEdit(); self.new_pass_input.setPlaceholderText("Yeni Şifre"); self.new_pass_input.setEchoMode(QLineEdit.Password); self.new_pass_input.hide()
        self.reset_pass_btn = QPushButton("Şifreyi Sıfırla"); self.reset_pass_btn.clicked.connect(self.reset_password); self.reset_pass_btn.hide()
        forgot_layout.addWidget(self.forgot_tc); forgot_layout.addWidget(self.send_sms_btn); forgot_layout.addWidget(self.sms_code_input); forgot_layout.addWidget(self.new_pass_input); forgot_layout.addWidget(self.reset_pass_btn)
        forgot_layout.addStretch()
        self.tabs.addTab(self.tab_forgot, "Şifremi Unuttum")
        
        card_layout.addWidget(self.tabs)
        main_layout.addWidget(self.card)
        self.reg_sms_code = None

    def handle_login(self):
        tc = self.tc_input.text(); password = self.pass_input.text()
        if not tc or not password: return QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
        user = get_user(tc, password)
        if user:
            self.main_app.current_user = {"tc": user[0], "name": user[2]}
            self.main_app.show_main_window()
        else: QMessageBox.warning(self, "Hata", "TC veya Şifre hatalı!")

    def send_reg_sms(self):
        if not self.reg_tc.text() or not self.reg_name.text() or not self.reg_phone.text() or not self.reg_pass.text():
            return QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
        self.reg_sms_code = generate_random_sms_code()
        QMessageBox.information(self, "SMS Gönderildi", f"{self.reg_phone.text()} numarasına onay kodu gönderildi:\n\nKOD: {self.reg_sms_code}")
        self.reg_sms_input.show(); self.reg_confirm_btn.show()
        self.send_reg_sms_btn.hide()

    def handle_register(self):
        if self.reg_sms_input.text() != self.reg_sms_code:
            return QMessageBox.warning(self, "Hata", "SMS Kodu hatalı!")
        tc = self.reg_tc.text(); name = self.reg_name.text(); password = self.reg_pass.text(); phone = self.reg_phone.text()
        if add_user(tc, password, name, phone):
            QMessageBox.information(self, "Başarılı", "Kayıt başarılı! Lütfen giriş yapın.")
            self.tabs.setCurrentIndex(0)
            self.tabs.removeTab(1)
        else: QMessageBox.warning(self, "Hata", "Bu TC ile zaten kayıt olunmuş.")

    def send_sms(self):
        tc = self.forgot_tc.text()
        user = get_user(tc)
        if not user: return QMessageBox.warning(self, "Hata", "Bu TC numarasına ait kullanıcı bulunamadı.")
        self.generated_code = generate_random_sms_code()
        # Phone is user[3]
        phone = user[3] if user[3] else ""
        if len(phone) >= 4:
            phone_masked = f"{phone[:4]} *** ** {phone[-2:]}"
        else:
            phone_masked = "Kayıtlı Numara"
            
        QMessageBox.information(self, "SMS Gönderildi", f"{phone_masked} numaralı telefonunuza doğrulama kodu gönderildi:\n\nKOD: {self.generated_code}")
        self.sms_code_input.show(); self.new_pass_input.show(); self.reset_pass_btn.show()
        self.send_sms_btn.setEnabled(False); self.forgot_tc.setEnabled(False)

    def reset_password(self):
        if self.sms_code_input.text() != self.generated_code: return QMessageBox.warning(self, "Hata", "Girdiğiniz kod hatalı!")
        if not self.new_pass_input.text(): return QMessageBox.warning(self, "Hata", "Lütfen yeni şifre girin.")
        update_password(self.forgot_tc.text(), self.new_pass_input.text())
        QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla sıfırlandı. Giriş yapabilirsiniz.")
        self.tabs.setCurrentIndex(0)
        self.forgot_tc.setEnabled(True); self.send_sms_btn.setEnabled(True)
        self.sms_code_input.hide(); self.new_pass_input.hide(); self.reset_pass_btn.hide()
        self.sms_code_input.clear(); self.new_pass_input.clear()


# ==========================================
# ANA EKRAN (MAIN WINDOW)
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("MediLife - Ana Ekran")
        self.resize(1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        self.stacked_widget = QStackedWidget()
        
        self.page_dashboard = QWidget()
        self.setup_dashboard()
        
        self.page_profile = ProfilePage(self.main_app)
        self.page_appointments = MyAppointmentsPage(self.main_app)
        self.page_book = AppointmentPage(self.main_app)
        self.page_symptoms = SymptomsPage(self.main_app)
        self.page_pharmacies = PharmaciesPage(self.main_app)
        self.page_favs = FavoritesPage(self.main_app)
        self.page_about = AboutPage(self.main_app)
        self.page_settings = SettingsPage(self.main_app)
        
        self.stacked_widget.addWidget(self.page_dashboard)
        self.stacked_widget.addWidget(self.page_profile)
        self.stacked_widget.addWidget(self.page_appointments)
        self.stacked_widget.addWidget(self.page_book)
        self.stacked_widget.addWidget(self.page_symptoms)
        self.stacked_widget.addWidget(self.page_pharmacies)
        self.stacked_widget.addWidget(self.page_favs)
        self.stacked_widget.addWidget(self.page_about)
        self.stacked_widget.addWidget(self.page_settings)
        
        self.top_bar = QFrame()
        top_layout = QHBoxLayout(self.top_bar)
        self.btn_back = QPushButton("🔙 Ana Ekrana Dön")
        self.btn_back.clicked.connect(lambda: self.switch_page(0))
        top_layout.addWidget(self.btn_back); top_layout.addStretch()
        self.top_bar.hide()
        
        self.main_layout.addWidget(self.top_bar)
        self.main_layout.addWidget(self.stacked_widget)
        
        self.check_reminders()

    def setup_dashboard(self):
        layout = QVBoxLayout(self.page_dashboard)
        layout.setAlignment(Qt.AlignCenter)
        
        card = QFrame(); card.setObjectName("card"); card.setFixedSize(800, 550)
        card_layout = QVBoxLayout(card); card_layout.setAlignment(Qt.AlignCenter)
        
        welcome_lbl = QLabel(f"Hoş Geldiniz, {self.main_app.current_user['name']}"); welcome_lbl.setObjectName("h1"); welcome_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(welcome_lbl); card_layout.addSpacing(20)
        
        grid = QGridLayout(); grid.setSpacing(15)
        
        buttons = [
            ("👤\nProfilim", 1), ("📅\nRandevularım", 2), ("➕\nRandevu Al", 3),
            ("❤️\nNeyim Var?", 4), ("💊\nNöbetçi Eczaneler", 5), ("⭐\nFavorilerim", 6),
            ("ℹ️\nHakkında", 7), ("⚙️\nAyarlar", 8)
        ]
        
        row, col = 0, 0
        for text, index in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(220, 100)
            btn.setStyleSheet("background-color: #D6EAF8; color: #2C3E50; border-radius: 15px; font-size: 16px;")
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            grid.addWidget(btn, row, col)
            col += 1
            if col > 3: col = 0; row += 1
            
        card_layout.addLayout(grid); card_layout.addSpacing(20)
        
        btn_logout = QPushButton("Çıkış Yap"); btn_logout.setObjectName("btn_danger"); btn_logout.setFixedHeight(50)
        btn_logout.clicked.connect(self.logout)
        card_layout.addWidget(btn_logout)
        
        layout.addWidget(card)

    def check_reminders(self):
        has_app, d, t = has_upcoming_appointment(self.main_app.current_user["tc"])
        if has_app:
            QMessageBox.information(self, "Yaklaşan Randevu Hatırlatması", f"Sayın {self.main_app.current_user['name']},\n\n{d} {t} tarihinde randevunuz bulunmaktadır. Lütfen randevunuza zamanında gitmeyi unutmayınız.")

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0: self.top_bar.hide()
        else: self.top_bar.show()
        
        if index == 2: self.page_appointments.refresh_data()
        elif index == 6: self.page_favs.load_favorites()

    def logout(self):
        self.main_app.current_user = None
        self.main_app.show_auth_window()

# ==========================================
# ANA UYGULAMA SINIFI
# ==========================================
class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(get_global_style())
        init_db()
        self.current_user = None
        self.auth_win = None
        self.main_win = None

    def run(self):
        self.show_auth_window()
        sys.exit(self.app.exec_())

    def show_auth_window(self):
        if self.main_win: self.main_win.close()
        self.auth_win = AuthWindow(self)
        self.auth_win.show()

    def show_main_window(self):
        if self.auth_win: self.auth_win.close()
        self.main_win = MainWindow(self)
        self.main_win.show()

    def open_appointment_with_clinic(self, clinic_name):
        self.main_win.page_book = AppointmentPage(self, initial_clinic=clinic_name)
        self.main_win.stacked_widget.insertWidget(3, self.main_win.page_book)
        self.main_win.switch_page(3)

    def open_appointment_with_hospital(self, city, district, hospital):
        self.main_win.page_book = AppointmentPage(self, initial_hosp=(city, district, hospital))
        self.main_win.stacked_widget.insertWidget(3, self.main_win.page_book)
        self.main_win.switch_page(3)
        
    def __del__(self):
        clear_temp_files()

if __name__ == '__main__':
    application = MainApp()
    application.run()
