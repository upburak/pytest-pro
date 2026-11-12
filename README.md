# PyTest Pro — Python Dinamik Ölçme ve Değerlendirme Sistemi

Okul laboratuvarında yerel ağda çalışan, her öğrenciye **kendine özel sorular** üreten Python sınav ve
pratik sistemi. Python öğreniminin başından sonuna **11 ünite** ve **75 soru şablonu** içerir:
temel giriş/çıkıştan nesne yönelimli programlamaya kadar. Ayrıntılı liste: [docs/MUFREDAT.md](docs/MUFREDAT.md)

| # | Ünite | Seviye |
|---|---|---|
| 1 | Temel Giriş/Çıkış ve Değişkenler | Başlangıç |
| 2 | Veri Tipleri ve Dönüşümler | Başlangıç |
| 3 | Operatörler | Başlangıç |
| 4 | Metinler (String) | Başlangıç |
| 5 | Koşullu İfadeler | Başlangıç |
| 6 | Döngüler | Orta |
| 7 | Listeler | Orta |
| 8 | Sözlük, Demet ve Küme | Orta |
| 9 | Fonksiyonlar ve Modüller | Orta |
| 10 | Hata Yönetimi | Orta |
| 11 | Nesne Yönelimli Programlama | İleri |

## Kurulum ve çalıştırma

Python 3.9 veya üstü gerekir.

```bash
pip install -r requirements.txt
python server.py
```

Konsolda şunlar yazar:

```
Öğrenci adresi  : http://192.168.1.25:5000
Pratik modu     : http://192.168.1.25:5000/pratik
Öğretmen paneli : http://192.168.1.25:5000/ogretmen
Öğretmen şifresi: 482913
```

- Öğrenciler adrese tarayıcıdan veya öğretmen panelindeki **QR kod** ile girer.
- Windows'ta ilk çalıştırmada güvenlik duvarı sorarsa **Özel ağlar** için izin verin.

## Öğretmen paneli

| Bölüm | Ne işe yarar |
|---|---|
| **Sınav başlığı** | Örn. "9-A Python 1. Sınav". Sonuçlar başlığa göre filtrelenir ve ayrı dışa aktarılır. |
| **Üniteler** | Sınava girecek üniteler; sorular seçilen ünitelere eşit dağıtılır ve kolaydan zora sıralanır. |
| **Soru sayısı / Süre** | 5–30 soru, 1–180 dakika. Yeni başlayan sınavlara uygulanır. |
| **Sınavı Aç / Yeni Girişleri Kapat** | Kapalıyken yeni öğrenci başlayamaz; sınavdaki öğrenciler devam eder. |
| **Çözümleri göster** | Kapatılırsa öğrenci yalnızca puanını ve hangi soruların doğru olduğunu görür. |
| **Tekrar girişe izin ver** | Kapatılırsa aynı sınavı bitiren numara yeniden giremez. |
| **Pratik modu** | Öğrencilerin `/pratik` adresinden ünite seçip anında geri bildirimle çalışmasını sağlar. Sınav sırasında kapalı tutun. |
| **Sonuç tablosu** | Canlı (3 sn), arama, kalan süre, deneme no, otomatik gönderim; satıra tıklayınca soru soru ayrıntı. |
| **Konu analizi** | Sınıfın ünite/konu bazında doğru oranı; en zayıf konu en üstte. Her konuda en sık verilen yanlış cevap ve bu yanılgının açıklaması. |
| **Excel / CSV** | `;` ayırıcılı, UTF-8 BOM'lu; Türkçe Excel'de doğrudan açılır. |

## Öğrenci tarafı

- **Sınav:** Cevaplar yazıldıkça sunucuya kaydedilir. Sayfa yenilenir, tarayıcı kapanır veya bilgisayar
  değişirse aynı ad ve numarayla girip kaldığı yerden devam eder. Süre dolunca sınav kendiliğinden gönderilir;
  hiç gönderilmese bile son kaydedilen cevaplarla değerlendirilir.
- **Pratik modu:** Ünite seçilir, her soru yeniden üretilir, cevap anında kontrol edilir. Sonuçlar kaydedilmez.
  - **İpucu:** Cevabı söylemeden nereye bakılacağını gösterir.
  - **Neden yanlış:** Seçilen yanlış cevaba özel, öğretmenin kırmızı kalemiyle yazılmış gibi bir açıklama.
  - **Kodu adım adım izle:** Kod satır satır yürütülür; her adımda değişkenler ve ekran çıktısı görünür.
  - **Bu konudan yeni soru:** Yanlıştan sonra aynı kavram farklı değerlerle hemen tekrar sorulur.
  - **Konu tamamlama:** Bir şablonda ipucusuz iki doğru konuyu tamamlar; içindekiler sayfası ilerlemeyi gösterir.
- **Sınav sonucu:** Öğretmen çözümleri açtıysa her yanlışta "neden yanlış" notu ve kodun adım adım izi görünür.
- **Soru tipleri:** çoktan seçmeli, doğru/yanlış, kısa cevap (kod çıktısı) ve kod yazma
  (değişken/aritmetik, `for` döngüsü, fonksiyon tanımlama).

## Ayarlar (isteğe bağlı ortam değişkenleri)

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `PYTEST_SIFRE` | rastgele 6 hane | Sabit öğretmen şifresi |
| `PYTEST_SURE` | `900` | Veritabanı ilk oluşturulurken varsayılan sınav süresi (saniye); sonra panelden değişir |
| `PYTEST_PORT` | `5000` | Port |
| `PYTEST_DB` | `results.db` | SQLite veritabanı yolu |

Örnek (Windows PowerShell): `$env:PYTEST_SIFRE="1234"; python server.py`

## Güvenlik ve güvenilirlik

- **Cevap anahtarı sunucuda:** Sınav sırasında tarayıcıya cevap gönderilmez; puanlama sunucuda yapılır.
- **Öğrenci kodu çalıştırılmaz:** Kod soruları AST ile yapısal olarak denetlenir; farklı doğru yazımlar kabul edilir.
- **Doğrulanmış soru bankası:** Testler her şablonu 120 farklı değerle üretir ve soru kodunu gerçekten
  çalıştırarak cevap anahtarının doğruluğunu kontrol eder.
- **Süre sunucuda denetlenir**, 30 sn ağ toleransıyla.
- **Şifre koruması:** Yalnızca istek başlığıyla; 10 hatalı denemede 1 dakika kilit.
- **Girdi sınırları**, **Content-Security-Policy**, **CSV enjeksiyonu koruması**.
- **Kalıcı kayıt:** SQLite (WAL). Şema sürümlüdür; eski veritabanları ilk açılışta otomatik güncellenir.
- **İnternet gerektirmez:** CDN yok, yazı tipleri sunucuya gömülü, QR kod sunucuda üretilir. `waitress` ile çok
  kullanıcılı çalışır.
- **Kod izi güvenliği:** Yalnızca sunucuda saklanan şablon kodu izlenir; öğrenci kodu hiçbir zaman çalıştırılmaz.
  İz 200 adım ve 5000 karakter çıktıyla sınırlıdır.

## Testler

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Testler şunları da doğrular: her şablonun ipucu ve yanlış şık açıklamaları eksiksiz, ipuçları cevabı ele
vermiyor, her şablon 500 üretimde en az 12 farklı soru veriyor ve kod izinin son çıktısı cevap anahtarıyla aynı.

GitHub Actions her push'ta testleri Linux (Python 3.10, 3.13) ve Windows'ta (Python 3.9, 3.13) çalıştırır.

## Geliştirme

Proje genişlemeye göre tasarlandı: her ünite ayrı bir dosyadır, yeni soru şablonu tek bir fonksiyondur
ve testler yeni şablonları kendiliğinden doğrular. Mimari, yeni ünite/soru/denetleyici ekleme ve yol
haritası için: **[docs/GELISTIRME.md](docs/GELISTIRME.md)**

Görsel dil (renkler, yazı tipleri, bileşenler ve kuralları): **[docs/TASARIM.md](docs/TASARIM.md)**

Sürüm notları: **[CHANGELOG.md](CHANGELOG.md)**

---
BÇ-GKAL
