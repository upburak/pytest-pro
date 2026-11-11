# PyTest Pro v2 — Python Giriş Dinamik Ölçme Sistemi

Yerel ağda (okul laboratuvarı) çalışan, her öğrenciye **farklı sorular** üreten Python sınav sistemi.
Konular: `print` (sep/end), `input()`, değişkenler, veri tipleri, `type()`, tip dönüşümleri, f-string.

## Kurulum ve çalıştırma

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

## Ayarlar (isteğe bağlı ortam değişkenleri)

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `PYTEST_SIFRE` | rastgele 6 hane | Sabit öğretmen şifresi |
| `PYTEST_SURE` | `900` | Sınav süresi (saniye) |
| `PYTEST_PORT` | `5000` | Port |
| `PYTEST_DB` | `results.db` | SQLite veritabanı yolu |

Örnek (Windows PowerShell): `$env:PYTEST_SIFRE="1234"; python server.py`

## Özellikler

- **Cevaplar sunucuda:** Sorular ve doğru cevaplar sunucuda üretilir. Tarayıcıya cevap gönderilmez, puanlama sunucuda yapılır.
- **Kod sorusu AST ile kontrol edilir:** Öğrenci kodu çalıştırılmaz. Atamalar ve `print(a * b)` yapısı tek tek denetlenir; ara değişken kullanımı da kabul edilir.
- **Kalıcı kayıt:** Sonuçlar `results.db` (SQLite) dosyasında tutulur, sunucu kapansa da kaybolmaz.
- **Excel uyumlu CSV:** `;` ayırıcı ve UTF-8 BOM kullanılır, Türkçe karakterler bozulmaz.
- **Güvenli gönderim:** Çift gönderim engellenir; sayfa yenilenirse sınav kaldığı yerden devam eder; süre sunucuda da denetlenir.
- **Deneme takibi:** Aynı okul numarasıyla tekrar girenler "Deneme #2" olarak işaretlenir.
- **İnternet gerektirmez:** CDN kullanılmaz, QR kod sunucuda üretilir.

## Dosya yapısı

```
server.py            Flask sunucu, soru üreteçleri, puanlama, API
templates/index.html Öğrenci sınav ekranı
templates/teacher.html Öğretmen paneli
static/style.css     Yerel stil dosyası
```

## Yeni soru şablonu eklemek

`server.py` içinde `q_...()` biçiminde bir fonksiyon yazıp `GENERATORS` listesine ekleyin.
Fonksiyon şu alanları döndürmelidir: `type` (`mc` / `tf` / `short` / `code`), `topic`, `text`, `code`, `options` (yalnızca `mc` için), `answer`, `solution`.

---
BÇ-GKAL
