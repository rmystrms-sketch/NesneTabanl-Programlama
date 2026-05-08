import customtkinter as ctk
import random
import datetime
import locale
import tkinter
from tkinter import messagebox

# --- PYTHON 3.13 RADİKAL ÇÖZÜM (Tcl Float Hatası Fix) ---
def patch_tkinter():
    old_configure = tkinter.Misc.configure
    def new_configure(self, cnf=None, **kw):
        if cnf:
            if isinstance(cnf, dict):
                for k, v in cnf.items():
                    if k in ('width', 'height', 'borderwidth', 'highlightthickness') and isinstance(v, float):
                        cnf[k] = int(v)
        for k, v in kw.items():
            if k in ('width', 'height', 'borderwidth', 'highlightthickness') and isinstance(v, float):
                kw[k] = int(v)
        return old_configure(self, cnf, **kw)
    tkinter.Misc.configure = new_configure

patch_tkinter()

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except: pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- SINIFLAR ---
class Kitap:
    def __init__(self, id, ad, yazar, kategori):
        self.id = id
        self.ad = ad
        self.yazar = yazar
        self.kategori = kategori
        self.durum = "Mevcut"
        self.alinma_sayisi = random.randint(10, 150) # Sıfır olmasın

class Uye:
    def __init__(self, id, ad, tel, email):
        self.id = id
        self.ad = ad
        self.tel = tel
        self.email = email
        self.okunan_sayisi = random.randint(5, 100) # İstatistikler dolsun diye
        self.aktif_odunc = []

class Odunc:
    def __init__(self, id, kitap, uye, alis, iade):
        self.id = id
        self.kitap = kitap
        self.uye = uye
        self.alis = alis
        self.iade = iade
        self.aktif = True
    def gecikme_gun(self):
        diff = (datetime.datetime.now() - self.iade).days
        return max(0, diff)

# --- VERİ HAZIRLIĞI ---
def veri_hazirla():
    kats = ["Roman", "Hikaye", "Çocuk Kitapları", "Bilim Kurgu", "Tarih", "Polisiye", "Felsefe", "Biyografi"]
    yazarlar = ["Ahmet Yılmaz", "Ayşe Demir", "Mehmet Kaya", "Elif Şahin", "Can Türk", "Zeynep Yıldız"]
    sifatlar = ["Gizemli", "Kayıp", "Büyük", "Sonsuz", "Parlak", "Karanlık", "Mavi", "Kadim"]
    isimler = ["Ada", "Zaman", "Yol", "Sır", "Umut", "Şehir", "Yıldız", "Gece", "Gölge", "Işık"]
    
    kitaplar = []
    for i in range(1, 501):
        ad = f"{random.choice(sifatlar)} {random.choice(isimler)}"
        kitaplar.append(Kitap(i, ad, random.choice(yazarlar), random.choice(kats)))
        
    uyeler = []
    adlar = ["Ahmet", "Ayşe", "Mehmet", "Fatma", "Can", "Elif", "Burak", "Selin", "Mert"]
    soyadlar = ["Yılmaz", "Demir", "Kaya", "Şahin", "Çelik", "Yıldız"]
    for i in range(1, 61):
        ad = f"{random.choice(adlar)} {random.choice(soyadlar)}"
        tel = f"0555 {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}"
        email = f"{ad.lower().replace(' ','')}@gmail.com"
        uyeler.append(Uye(i, ad, tel, email))
        
    oduncler, gecmis = [], []
    # İstatistikler için 200 adet kiralama başlat (Bazıları gecikmiş)
    for k in random.sample(kitaplar, 200):
        u = random.choice(uyeler)
        k.durum = "Kirada"
        # Rastgele tarih: 1-40 gün önce alınmış
        gun_once = random.randint(1, 40)
        alis = datetime.datetime.now() - datetime.timedelta(days=gun_once)
        # İade süresi 15 gün
        iade = alis + datetime.timedelta(days=15)
        o = Odunc(len(oduncler)+1, k, u, alis, iade)
        oduncler.append(o); u.aktif_odunc.append(o)
        gecmis.append(f"[{alis.strftime('%d.%m %H:%M')}] {u.ad} -> '{k.ad}' kiraladı.")
        
    return kitaplar, uyeler, oduncler, gecmis

# --- ANA APP ---
class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kütüphane Yönetim & Analiz ERP")
        self.geometry("1300x900")
        self.kitaplar, self.uyeler, self.oduncler, self.gecmis = veri_hazirla()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#1a1a24")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="ADMİN PANELİ", font=("", 24, "bold"), text_color="#f72585").pack(pady=30)
        
        menu = [
            ("📊 Panel Özeti", self.show_stats),
            ("📚 Kitap Envanteri", self.show_lib),
            ("👥 Müşteri Yönetimi", self.show_users),
            ("📩 Hatırlatıcı & Kayıt", self.show_reminder_center),
            ("📜 İşlem Geçmişi", self.show_history)
        ]
        for t, c in menu:
            ctk.CTkButton(self.sidebar, text=t, command=c, height=45, fg_color="transparent", anchor="w", font=("", 15)).pack(fill="x", padx=15, pady=5)
            
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.show_stats()

    def clear(self):
        for w in self.main.winfo_children(): w.destroy()

    def add_history(self, msg):
        self.gecmis.insert(0, f"[{datetime.datetime.now().strftime('%d.%m %H:%M')}] {msg}")

    # --- PANEL ÖZETİ (İSTATİSTİKLER) ---
    def show_stats(self):
        self.clear()
        ctk.CTkLabel(self.main, text="📊 Genel Analiz ve Performans", font=("", 28, "bold")).pack(anchor="w", pady=(0, 20))
        
        grid = ctk.CTkFrame(self.main, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1, 2), weight=1)
        grid.grid_rowconfigure(0, weight=1)
        
        # 1. En Aktif Okurlar
        c1 = ctk.CTkScrollableFrame(grid, label_text="🏆 En Aktif Okurlar", fg_color="#1e1e24")
        c1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        top_u = sorted(self.uyeler, key=lambda x: x.okunan_sayisi, reverse=True)[:30]
        for u in top_u:
            f = ctk.CTkFrame(c1, fg_color="#2b2b36")
            f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(f, text=f"{u.ad}\n{u.okunan_sayisi} Kitap", font=("", 12)).pack(pady=5)

        # 2. Geciktirme Yapanlar
        c2 = ctk.CTkScrollableFrame(grid, label_text="⚠️ Gecikme Yapanlar", fg_color="#1e1e24")
        c2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        late_ones = sorted([o for o in self.oduncler if o.aktif and o.gecikme_gun() > 0], key=lambda x: x.gecikme_gun(), reverse=True)
        for o in late_ones:
            f = ctk.CTkFrame(c2, fg_color="#2b2b36")
            f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(f, text=f"{o.uye.ad}\n{o.gecikme_gun()} Gün Gecikti!", text_color="#ef233c", font=("", 12, "bold")).pack(pady=5)

        # 3. Popüler Kitaplar
        c3 = ctk.CTkScrollableFrame(grid, label_text="🔥 En Popüler Kitaplar", fg_color="#1e1e24")
        c3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        top_k = sorted(self.kitaplar, key=lambda x: x.alinma_sayisi, reverse=True)[:30]
        for k in top_k:
            f = ctk.CTkFrame(c3, fg_color="#2b2b36")
            f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(f, text=f"{k.ad}\n{k.alinma_sayisi} Okunma", font=("", 12)).pack(pady=5)

    def show_lib(self):
        self.clear()
        header = ctk.CTkFrame(self.main, fg_color="transparent"); header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="📚 Kitap Envanteri (500)", font=("", 24, "bold")).pack(side="left")
        self.scroll = ctk.CTkScrollableFrame(self.main); self.scroll.pack(fill="both", expand=True)
        self.scroll.grid_columnconfigure((0,1,2,3), weight=1)
        for i, k in enumerate(self.kitaplar[:100]):
            fr = ctk.CTkFrame(self.scroll, fg_color="#22222b", corner_radius=10)
            fr.grid(row=i//4, column=i%4, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(fr, text=k.ad, font=("", 14, "bold"), text_color="#fca311", wraplength=160).pack(pady=(15, 5))
            ctk.CTkLabel(fr, text=k.yazar, font=("", 11)).pack()
            color = "#06d6a0" if k.durum == "Mevcut" else "#ef233c"
            ctk.CTkLabel(fr, text=k.durum, text_color=color, font=("", 12, "bold")).pack(pady=5)
            if k.durum == "Mevcut":
                ctk.CTkButton(fr, text="Ödünç Ver", height=28, command=lambda kt=k: self.rent_dialog(kt)).pack(pady=10)
            else:
                ctk.CTkButton(fr, text="İade Al", height=28, fg_color="#118ab2", command=lambda kt=k: self.return_book(kt)).pack(pady=10)

    def rent_dialog(self, k):
        dialog = ctk.CTkToplevel(self); dialog.title("Ödünç Ver"); dialog.geometry("400x350"); dialog.attributes('-topmost', True)
        ctk.CTkLabel(dialog, text=f"'{k.ad}' Seçili Müşteri:", font=("", 14)).pack(pady=20)
        u_var = ctk.StringVar(value="Seçiniz")
        u_list = [f"{u.id:02d} - {u.ad}" for u in self.uyeler]
        ctk.CTkOptionMenu(dialog, values=u_list, variable=u_var, width=280).pack(pady=10)
        def confirm():
            if u_var.get() == "Seçiniz": return
            uid = int(u_var.get().split(" - ")[0])
            u = next(x for x in self.uyeler if x.id == uid)
            k.durum = "Kirada"; k.alinma_sayisi += 1; u.okunan_sayisi += 1
            o = Odunc(len(self.oduncler)+1, k, u, datetime.datetime.now(), datetime.datetime.now()+datetime.timedelta(days=15))
            self.oduncler.append(o); u.aktif_odunc.append(o); self.add_history(f"{u.ad} -> '{k.ad}' kiraladı.")
            messagebox.showinfo("OK", "Başarılı!"); dialog.destroy(); self.show_lib()
        ctk.CTkButton(dialog, text="Onayla", fg_color="#06d6a0", text_color="black", command=confirm).pack(pady=20)

    def return_book(self, k):
        o = next((x for x in self.oduncler if x.kitap.id == k.id and x.aktif), None)
        if o:
            o.aktif = False; k.durum = "Mevcut"
            if o in o.uye.aktif_odunc: o.uye.aktif_odunc.remove(o)
            self.add_history(f"{o.uye.ad} -> '{k.ad}' iade etti."); messagebox.showinfo("İade", "Alındı."); self.show_lib()

    def show_users(self):
        self.clear()
        ctk.CTkLabel(self.main, text="👥 Müşteri Yönetimi", font=("", 24, "bold")).pack(anchor="w", pady=10)
        scroll = ctk.CTkScrollableFrame(self.main); scroll.pack(fill="both", expand=True)
        for u in self.uyeler:
            f = ctk.CTkFrame(scroll, fg_color="#1e1e24", corner_radius=10); f.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(f, text=f"ID:{u.id:02d} | {u.ad}", font=("", 16, "bold"), text_color="#f72585").pack(side="left", padx=20, pady=15)
            ctk.CTkLabel(f, text=f"📞 {u.tel} | ✉️ {u.email}", font=("", 11)).pack(side="left", padx=20)
            ctk.CTkButton(f, text="SMS", width=80, command=lambda: messagebox.showinfo("SMS", "Gönderildi")).pack(side="right", padx=20)

    # --- HATIRLATICI VE FULL MÜŞTERİ KAYDI ---
    def show_reminder_center(self):
        self.clear()
        ctk.CTkLabel(self.main, text="📩 Hatırlatıcı ve Müşteri Kayıt Merkezi", font=("", 28, "bold")).pack(anchor="w", pady=(0, 20))
        cont = ctk.CTkFrame(self.main, fg_color="transparent"); cont.pack(fill="both", expand=True)
        
        # SOL: HATIRLATICI
        l = ctk.CTkFrame(cont, fg_color="#1e1e24", corner_radius=15); l.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(l, text="Otomatik Hatırlatıcı", font=("", 18, "bold"), text_color="#4cc9f0").pack(pady=20)
        ctk.CTkButton(l, text="Gecikenlere Toplu SMS At", fg_color="#ef233c", command=lambda: messagebox.showinfo("SMS", "Gönderildi")).pack(pady=10, padx=20, fill="x")
        
        # SAĞ: DETAYLI MÜŞTERİ KAYDI
        r = ctk.CTkFrame(cont, fg_color="#1e1e24", corner_radius=15); r.pack(side="right", fill="both", expand=True, padx=(10, 0))
        ctk.CTkLabel(r, text="👤 Yeni Müşteri Kaydı", font=("", 18, "bold"), text_color="#06d6a0").pack(pady=20)
        e_ad = ctk.CTkEntry(r, placeholder_text="Ad Soyad", height=40); e_ad.pack(pady=10, padx=30, fill="x")
        e_tel = ctk.CTkEntry(r, placeholder_text="Telefon (05...)", height=40); e_tel.pack(pady=10, padx=30, fill="x")
        e_mail = ctk.CTkEntry(r, placeholder_text="Gmail Adresi", height=40); e_mail.pack(pady=10, padx=30, fill="x")
        
        def save_full():
            if e_ad.get() and e_tel.get() and e_mail.get():
                new_u = Uye(len(self.uyeler)+1, e_ad.get(), e_tel.get(), e_mail.get())
                self.uyeler.append(new_u); self.add_history(f"Yeni Müşteri: {e_ad.get()}")
                messagebox.showinfo("Başarılı", f"{e_ad.get()} kaydedildi."); self.show_reminder_center()
            else: messagebox.showwarning("Hata", "Tüm alanları doldurun.")
        ctk.CTkButton(r, text="Müşteriyi Kaydet 💾", fg_color="#06d6a0", text_color="black", height=45, command=save_full).pack(pady=20, padx=30, fill="x")

    def show_history(self):
        self.clear()
        ctk.CTkLabel(self.main, text="📜 İşlem Geçmişi", font=("", 26, "bold")).pack(anchor="w", pady=(0, 20))
        scroll = ctk.CTkScrollableFrame(self.main, fg_color="#1e1e24"); scroll.pack(fill="both", expand=True)
        for log in self.gecmis:
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=log, font=("Courier", 13), text_color="#4cc9f0").pack(side="left", padx=10)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
