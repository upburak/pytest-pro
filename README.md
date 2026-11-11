# PyTest Pro — Python Giriş Dinamik Ölçme Sistemi

Yerel ağda (okul laboratuvarı) çalışan, her öğrenciye **farklı sorular** üreten Python sınav sistemi.
Konular: `print` (sep/end), `input()`, değişkenler ve adlandırma, veri tipleri, `type()`, tip dönüşümleri,
metin işlemleri, aritmetik operatörler, çoklu atama, f-string.

## Kurulum ve çalıştırma

Python 3.9 veya üstü gerekir.

```bash
pip install -r requirements.txt
python server.py
```

Konsolda şunlar yazar:

```
Öğrenci adresi  : http://192.168.1.25:5000
Öğretmen paneli : http://192.168.1.25:5000/ogretmen
Öğretmen şifresi: 482913
```

- Öğrenciler adrese tarayıcıdan veya öğretmen panelindeki **QR kod** ile girer.
- Öğretmen paneli şifreyle açılır ve sonuçları **3 saniyede bir** canlı günceller.
- Windows'ta ilk çalıştırmada güvenlik duvarı sorarsa **Özel ağlar** için izin verin.

## Öğretmen paneli

| Bölüm | Ne işe yarar |
|---|---|
| **Sınavı Aç / Yeni Girişleri Kapat** | Kapalıyken yeni öğrenci başlayamaz; sınavdaki öğrenciler devam eder. Öğrenci ekranı kendiliğinden güncellenir. |
| **Soru sayısı / Süre** | 5, 10, 15 veya 20 soru; 1–180 dakika. Yeni başlayan sınavlara uygulanır. |
| **Çözümleri göster** | Kapatılırsa öğrenci sınav sonunda yalnızca puanını ve hangi soruların doğru olduğunu görür. |
| **Tekrar girişe izin ver** | Kapatılırsa sınavı bitiren numara yeniden sınava giremez. |
| **Sonuç tablosu** | Arama, deneme numarası, kalan süre, otomatik gönderim işareti; satıra tıklayınca soru soru ayrıntı ve tek kayıt silme. |
| **Konu analizi** | Sınıfın konulara göre doğru oranı; en zayıf konu en üstte. |
| **Excel / CSV** | `;` ayırıcılı, UTF-8 BOM'lu; Türkçe Excel'de doğrudan açılır. |

## Öğrenci tarafı

- Cevaplar yazıldıkça **sunucuya otomatik kaydedilir**; bağlantı koparsa cihazda tutulur ve tekrar denenir.
- Sayfa yenilenir, tarayıcı kapanır veya bilgisayar değişirse **aynı ad ve numarayla** girerek kaldığı yerden devam eder.
- Süre dolunca sınav kendiliğinden gönderilir. Öğrenci hiç göndermese bile süresi dolan sınav,
  **süre içinde kaydedilen son cevaplarla** otomatik değerlendirilir (panelde "Otomatik" olarak görünür).

## Ayarlar (isteğe bağlı ortam değişkenleri)

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `PYTEST_SIFRE` | rastgele 6 hane | Sabit öğretmen şifresi |
| `PYTEST_SURE` | `900` | Veritabanı ilk oluşturulurken varsayılan sınav süresi (saniye). Sonrasında süre panelden değiştirilir. |
| `PYTEST_PORT` | `5000` | Port |
| `PYTEST_DB` | `results.db` | SQLite veritabanı yolu |

Örnek (Windows PowerShell): `$env:PYTEST_SIFRE="1234"; python server.py`

## Güvenlik ve güvenilirlik

- **Cevaplar sunucuda:** Sorular ve doğru cevaplar sunucuda üretilir; sınav sırasında tarayıcıya cevap gönderilmez, puanlama sunucuda yapılır.
- **Kod sorusu AST ile kontrol edilir:** Öğrenci kodu asla çalıştırılmaz. Atamalar ve `print(a * b)` yapısı denetlenir; ara değişken, `a, b = 7, 3` gibi çoklu atama ve yorumlar kabul edilir.
- **Süre sunucuda denetlenir:** 30 sn ağ toleransından sonra gelen cevaplar kabul edilmez.
- **Şifre koruması:** Şifre yalnızca istek başlığıyla gönderilir; 10 hatalı denemede 1 dakika kilit.
- **Girdi sınırları:** Cevap başına 2000 karakter, istek başına 256 KB; bilinmeyen alanlar atılır.
- **Tarayıcı güvenliği:** Content-Security-Policy ile satır içi betik çalıştırılamaz; tüm kullanıcı metinleri kaçışlanır.
- **CSV enjeksiyonu:** `=`, `+`, `-`, `@` ile başlayan hücreler Excel'de formül olarak çalışmaz.
- **Kalıcı kayıt:** SQLite (WAL modu). Eski v2 veritabanları ilk açılışta otomatik güncellenir.
- **Üretim sunucusu:** `waitress` kuruluysa onunla, değilse Flask'ın kendi sunucusuyla çalışır.
- **İnternet gerektirmez:** CDN kullanılmaz, QR kod sunucuda üretilir.

## Dosya yapısı

```
server.py              Flask uygulaması, API, veritabanı, ayarlar
questions.py           Soru şablonları ve puanlama
templates/index.html   Öğrenci sınav ekranı
templates/teacher.html Öğretmen paneli
static/student.js      Öğrenci ekranı betiği
static/teacher.js      Öğretmen paneli betiği
static/style.css       Yerel stil dosyası
tests/                 Otomatik testler
```

## Testler

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Testler her soru şablonunu 150 farklı rastgele tohumla üretir ve **soru kodunu gerçekten çalıştırarak**
cevap anahtarının doğru olduğunu doğrular. API testleri sınav akışını, süre aşımını, ayarları,
yetkilendirmeyi ve CSV dışa aktarımını kapsar. GitHub Actions her push'ta Linux ve Windows'ta testleri çalıştırır.

## Yeni soru şablonu eklemek

`questions.py` içinde `q_...()` biçiminde bir fonksiyon yazıp `GENERATORS` listesine ekleyin.
Fonksiyon şu alanları döndürmelidir: `type` (`mc` / `tf` / `short` / `code`), `topic`, `text`, `code`,
`options` (yalnızca `mc` için, 4 farklı seçenek), `answer`, `solution`.

Cevap, kodun ekran çıktısıysa fonksiyonu `tests/test_questions.py` içindeki `OUTPUT_GENERATORS`
listesine ekleyin; testler cevabı kodu çalıştırarak doğrular. Kod `input()` kullanıyorsa klavye
girdisini `stdin` alanında verin.

---
Burak ÇEKİÇ — Gülsefa Kapancıoğlu Anadolu Lisesi
