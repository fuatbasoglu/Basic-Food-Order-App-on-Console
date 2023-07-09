# os Modulunu içeri aktarıyoruz
import os

# Her seçimimizden sonra konsolu temizleyeceğimiz bir fonksiyon olusturuyoruz
def konsol_temizle():
    # İşletim sistemi Windows ise
    if os.name == "nt":
        # cls komutunu çalıştır
        os.system("cls")
    # İşletim sistemi Linux veya Mac ise
    else:
        # clear komutunu çalıştır
        os.system("clear")

# İlk girişte karşımıza çıkacak tanıtım yazısını yazıyoruz
konsol_temizle()
print("Yemek Siparisi Uygulamasına Hoş Geldiniz .")

# Veri tabanı bağlantısı için sqlite3 modülünü içe aktarıyoruz
import sqlite3

# Veri tabanına bağlanıyoruz veya yoksa bu kod ile oluşturulmasını sağlıyoruz
conn = sqlite3.connect("yemek_siparis.db")

cur = conn.cursor()

# Kullanıcıların listeleneceği tablosunu oluşturuyoruz 
cur.execute("""CREATE TABLE IF NOT EXISTS kullanici (
    id INTEGER PRIMARY KEY,
    ad TEXT,
    sifre TEXT,
    tip TEXT
)""")

# Yemeklerin listeleneceği tabloyu oluşturuz
cur.execute("""CREATE TABLE IF NOT EXISTS yemek (
    id INTEGER PRIMARY KEY,
    isim TEXT,
    fiyat REAL
)""")

# Siparislerin listeleneceği tabloyu  oluşturuyoruz 
cur.execute("""CREATE TABLE IF NOT EXISTS siparis (
    id INTEGER PRIMARY KEY,
    kullanici_id INTEGER,
    yemek_id INTEGER,
    adet INTEGER,
    toplam REAL,
    FOREIGN KEY (kullanici_id) REFERENCES kullanici (id),
    FOREIGN KEY (yemek_id) REFERENCES yemek (id)
)""")

# Örnek yemekler ekliyoruz (Listelenen diğer yemekleri tablo üzerinden ekledim)
cur.execute("INSERT INTO yemek (isim, fiyat) VALUES ('Pizza', 25.0)")
cur.execute("INSERT INTO yemek (isim, fiyat) VALUES ('Hamburger', 15.0)")
cur.execute("INSERT INTO yemek (isim, fiyat) VALUES ('Salata', 10.0)")


# Veri tabanında yaptığımız değişiklikleri kaydediyoruz
conn.commit()

# Kullanıcı sınıfının kodları 
class Kullanici:
    # Sınıfın başlangıcını sağlayan fonksiyon
    def __init__(self, id, ad, sifre, tip):
        self.id = id
        self.ad = ad
        self.sifre = sifre
        self.tip = tip

    # Kullanıcıya ait işlemleri listeleme fonksiyonu
    def islem_listele(self):
        print("Yapabileceğiniz işlemler:")
        print("1) Yemek siparişi ver")
        print("2) Sipariş geçmişini görüntüle")
        print("3) Rapor al")
        print("4) Çıkış yap")

    # Yemek siparişi verme fonksiyonu
    def siparis_ver(self):
        # Yemekleri listele
        print("Yemek menüsü:")
        cur.execute("SELECT * FROM yemek")
        yemekler = cur.fetchall()
        for yemek in yemekler:
            print(f"{yemek[0]}) {yemek[1]} - {yemek[2]} TL")

        # Sipariş alma işlemi
        yemek_id = int(input("Sipariş etmek istediğiniz yemeğin numarasını giriniz: "))
        adet = int(input("Kaç adet istiyorsunuz? "))
        
        # Siparişin toplam fiyatını hesaplama işlemi
        cur.execute("SELECT fiyat FROM yemek WHERE id = ?", (yemek_id,))
        fiyat = cur.fetchone()[0]
        toplam = fiyat * adet

        # Siparişi veri tabanına kaydetme işleni
        cur.execute("INSERT INTO siparis (kullanici_id, yemek_id, adet, toplam) VALUES (?, ?, ?, ?)", (self.id, yemek_id, adet, toplam))
        conn.commit()

        # Sipariş bilgisini ekrana yazdırma komutu
        print(f"Siparişiniz başarıyla alındı. Toplam tutar: {toplam} TL")

    # Sipariş geçmişini görüntüleme fonksiyonu
    def siparis_goruntule(self):
        # Kullanıcının verdiği siparişleri görüntüleme fonksiyonu
        cur.execute("SELECT * FROM siparis WHERE kullanici_id = ?", (self.id,))
        siparisler = cur.fetchall()

        # Siparişleri ekrana yazdırma kodları
        print(f"{self.ad} adlı kullanıcının sipariş geçmişi:")
        for siparis in siparisler:
            # Siparişin yemek ismini bul
            cur.execute("SELECT isim FROM yemek WHERE id = ?", (siparis[2],))
            yemek_isim = cur.fetchone()[0]

            # Sipariş bilgisini yazdırma işlemi
            print(f"{siparis[0]}) {yemek_isim} - {siparis[3]} adet - {siparis[4]} TL")

    # Rapor alma işlemi
    def rapor_al(self):
        # Kullanıcının verdiği siparişleri getirme kodları
        cur.execute("SELECT * FROM siparis WHERE kullanici_id = ?", (self.id,))
        siparisler = cur.fetchall()

        # Rapor dosyası oluşturma
        rapor_dosyasi = open(f"{self.ad}_rapor.csv", "w")

        # Rapor dosyasına başlık satırı yazıyoruz
        rapor_dosyasi.write("Sipariş No,Yemek Adı,Adet,Toplam\n")

        # Rapor dosyasına sipariş bilgilerini yazma kodları
        for siparis in siparisler:
            # Siparişin yemek ismini bulma
            cur.execute("SELECT isim FROM yemek WHERE id = ?", (siparis[2],))
            yemek_isim = cur.fetchone()[0]

            # Sipariş bilgisini dosyaya yazma
            rapor_dosyasi.write(f"{siparis[0]},{yemek_isim},{siparis[3]},{siparis[4]}\n")

        # Rapor dosyasını kapatma
        rapor_dosyasi.close()

        # Rapor bilgisini ekrana yazdırma
        print(f"Raporunuz {self.ad}_rapor.csv dosyasına kaydedildi.")

# Yönetici sınıfı tanımı (Kullanıcı sınıfından faydalandım)
class Yonetici(Kullanici):
    # Yöneticiye ait işlemleri listeleme fonksiyonu
    def islem_listele(self):
        # Kullanıcı sınıfındaki fonksiyonları çağırma 
        super().islem_listele()

        # Yöneticiye özel işlemleri ekliyoruz
        print("5) Tüm kullanıcıları görüntüle")
        print("6) Tüm siparişleri görüntüle")
        print("7) Herhangi bir kullanıcının raporunu al")

    # Tüm kullanıcıları görüntüleme fonksiyonu
    def kullanici_goruntule(self):
        # Tüm kullanıcıları getirme işlemi
        cur.execute("SELECT * FROM kullanici")
        kullanicilar = cur.fetchall()

        # Kullanıcıları ekrana yazdırma kodları
        print("Tüm kullanıcılar:")
        for kullanici in kullanicilar:
            print(f"{kullanici[0]}) {kullanici[1]} - {kullanici[3]}")

        # Tüm siparişleri görüntüleme fonksiyonu
    def siparis_goruntule(self):
        # Tüm siparişleri getirme
        cur.execute("SELECT * FROM siparis")
        siparisler = cur.fetchall()

        # Siparişleri ekrana yazdırma
        print("Tüm siparişler:")
        for siparis in siparisler:
            # Siparişin yemek ismini bulma kodları
            cur.execute("SELECT isim FROM yemek WHERE id = ?", (siparis[2],))
            yemek_isim = cur.fetchone()[0]

            # Siparişin kullanıcı adını bulma
            cur.execute("SELECT ad FROM kullanici WHERE id = ?", (siparis[1],))
            kullanici_ad = cur.fetchone()[0]

            # Sipariş bilgisini yazdırma
            print(f"{siparis[0]}) {kullanici_ad} - {yemek_isim} - {siparis[3]} adet - {siparis[4]} TL")

    # Herhangi bir kullanıcının raporunu alma fonksiyonu
    def rapor_al(self):
        # Rapor almak istediğiniz kullanıcının numarasını sorma kodları
        kullanici_id = int(input("Rapor almak istediğiniz kullanıcının numarasını giriniz: "))

        # Kullanıcının verdiği siparişleri görüntüleme
        cur.execute("SELECT * FROM siparis WHERE kullanici_id = ?", (kullanici_id,))
        siparisler = cur.fetchall()

        # Kullanıcının adını bulma
        cur.execute("SELECT ad FROM kullanici WHERE id = ?", (kullanici_id,))
        kullanici_ad = cur.fetchone()[0]

        # Rapor dosyası oluşturma
        rapor_dosyasi = open(f"{kullanici_ad}_rapor.csv", "w")

        # Rapor dosyasına başlık satırı yazma
        rapor_dosyasi.write("Sipariş No,Yemek Adı,Adet,Toplam\n")

        # Rapor dosyasına sipariş bilgilerini yazma
        for siparis in siparisler:
            # Siparişin yemek ismini bulma
            cur.execute("SELECT isim FROM yemek WHERE id = ?", (siparis[2],))
            yemek_isim = cur.fetchone()[0]

            # Sipariş bilgisini dosyaya yazma
            rapor_dosyasi.write(f"{siparis[0]},{yemek_isim},{siparis[3]},{siparis[4]}\n")

        # Rapor dosyasını kapatma kodu
        rapor_dosyasi.close()

        # Rapor bilgisini ekrana yazdırma işlemi
        print(f"Raporunuz {kullanici_ad}_rapor.csv dosyasına kaydedildi.")

# Giriş yapma fonksiyonu
def giris_yap():
    # Konsolu temizleme kodu
    konsol_temizle()

    # Kullanıcı adı ve şifre sorma işlemi
    ad = input("Kullanıcı adınız: ")
    sifre = input("Şifreniz: ")

    # Veri tabanında girilen kullanıcının var olup olmadıgını kontrol ediyoruz
    cur.execute("SELECT * FROM kullanici WHERE ad = ? AND sifre = ?", (ad, sifre))
    kullanici = cur.fetchone()

    if kullanici:
        
        if kullanici[3] == "Yönetici":
            kullanici_nesne = Yonetici(kullanici[0], kullanici[1], kullanici[2], kullanici[3])
        else:
            kullanici_nesne = Kullanici(kullanici[0], kullanici[1], kullanici[2], kullanici[3])

        # Kullanıcıya hoşgeldin dediğimiz işlem
        print(f"Merhaba {kullanici_nesne.ad}!")

        return kullanici_nesne

    # Kullanıcı bulunamadıysa
    else:
        # Hata mesajı verme kodu
        print("Kullanıcı adı veya şifre yanlış. Lütfen tekrar deneyiniz.")
    
    return None

# Yeni kullanıcı oluşturma fonksiyonu
def yeni_kullanici():
    # Konsolu temizleme 
    konsol_temizle()

    # Kullanıcı adı ve şifre sorma
    ad = input("Kullanıcı adınız: ")
    sifre = input("Şifreniz: ")

    # Veri tabanında girilen kullanıcının var olup olmadıgını kontrol etme işlemi
    cur.execute("SELECT * FROM kullanici WHERE ad = ?", (ad,))
    kullanici = cur.fetchone()

    # Kullanıcı varsa
    if kullanici:
        # Hata mesajı verme
        print("Bu kullanıcı adı zaten alınmış. Lütfen başka bir tane seçiniz.")
    
    # Kullanıcı yoksa
    else:
        # Kullanıcı tipini sor (sadece yönetici olan kullanıcılar yönetici hesap oluşturabilir)
        tip = input("Kullanıcı tipiniz (Yönetici veya Standart): ")
        
        # Eğer yönetici olmak istiyorsa şifre sor (önceden belirlenmiş bir şifre olmalı şifre = 1234)
        if tip == "Yönetici":
            yonetici_sifre = input("Yönetici şifresi: ")

            # Şifre doğruysa eğer
            if yonetici_sifre == "1234":
                # Yeni yöneticiyi veri tabanına kaydet
                cur.execute("INSERT INTO kullanici (ad, sifre, tip) VALUES (?, ?, ?)", (ad, sifre, tip))
                conn.commit()

                # Başarılı mesajı ver
                print(f"Yeni yönetici {ad} başarıyla oluşturuldu.")

            # Şifre yanlışsa
            else:
                # Hata mesajı verme
                print("Yanlış yönetici şifresi. Lütfen tekrar deneyiniz.")

        # Eğer standart kullanıcı olmak istiyorsa
        elif tip == "Standart":
            # Yeni standart kullanıcıyı veri tabanına kaydet
            cur.execute("INSERT INTO kullanici (ad, sifre, tip) VALUES (?, ?, ?)", (ad, sifre, tip))
            conn.commit()

            # Başarılı mesajı ver
            print(f"Yeni standart kullanıcı {ad} başarıyla oluşturuldu.")

        # Eğer geçersiz bir kullanıcı tipi girildiyse
        else:
            # Hata mesajı ver
            print("Geçersiz kullanıcı tipi. Lütfen tekrar deneyiniz.")

# Ana program döngüsü
while True:
    # Konsolu temizle
    konsol_temizle()

    # Yapmak istedikleri işleri gösterme ve seçmesi .
    print("Lütfen yapmak istediğiniz işlemi seçiniz.")
    print("1) Giriş yap")
    print("2) Yeni kullanıcı oluştur")
    secim = input("Seçiminiz: ")

    # Seçime göre işlem yapma
    if secim == "1":
        # Giriş yap ve kullanıcıyı getir
        kullanici_nesne = giris_yap()

        # Giriş başarılıysa eğer
        if kullanici_nesne:
            # Kullanıcının seçimini alana kadar döngüye girme işlemi
            while True:
                # Konsolu temizle
                konsol_temizle()

                # Kullanıcıya ait işlemleri listeleme 
                kullanici_nesne.islem_listele()

                # Kullanıcının seçimini alma
                secim = input("Seçiminiz: ")

                # Seçime göre işlem yapma
                if secim == "1":
                    # Yemek siparişi verme
                    kullanici_nesne.siparis_ver()
                    input("Devam etmek için bir tuşa basın.")
                elif secim == "2":
                    # Sipariş geçmişini görüntüleme
                    kullanici_nesne.siparis_goruntule()
                    input("Devam etmek için bir tuşa basın.")
                elif secim == "3":
                    # Rapor alma işlemi
                    kullanici_nesne.rapor_al()
                    input("Devam etmek için bir tuşa basın.")
                elif secim == "4":
                    # Çıkış yapma işlemi
                    print("Güle güle!")
                    break
                elif secim == "5" and isinstance(kullanici_nesne, Yonetici):
                    # Tüm kullanıcıları görüntüle (sadece yöneticiler yapabilir)
                    kullanici_nesne.kullanici_goruntule()
                    input("Devam etmek için bir tuşa basın.")
                elif secim == "6" and isinstance(kullanici_nesne, Yonetici):
                    # Tüm siparişleri görüntüle (sadece yöneticiler görüntüleyebilir)
                    kullanici_nesne.siparis_goruntule()
                    input("Devam etmek için bir tuşa basın.")
                elif secim == "7" and isinstance(kullanici_nesne, Yonetici):
                    # Herhangi bir kullanıcının raporunu al (sadece yöneticiler yapabilir)
                    kullanici_nesne.rapor_al()
                    input("Devam etmek için bir tuşa basın.")
                else:
                    # Geçersiz seçimse eer
                    print("Geçersiz seçim. Lütfen tekrar deneyiniz.")
                    input("Devam etmek için bir tuşa basın.")

    elif secim == "2":
        # Yeni kullanıcı oluştur
        yeni_kullanici()
        input("Devam etmek için bir tuşa basın.")
    else:
        # Geçersiz seçim
        print("Geçersiz seçim. Lütfen tekrar deneyiniz.")
        input("Devam etmek için bir tuşa basın.")
