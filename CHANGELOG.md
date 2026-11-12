# Sürüm Notları

## 3.2.0

### Editör tasarımı
- Yeni görsel dil: sınav bir kod editörü gibi. Solda soru dosyaları (`soru_01.py`), üstte satır numaralı ve
  renklendirilmiş kod, hemen altında adaçayı yeşili cevap paneli. Ayrıntılar: `docs/TASARIM.md`.
- Kısa şıklar iki sütunda; klavye kısayolları (A–E ya da 1–5 şık, D/Y doğru/yanlış, ←/→ soru değiştir).
- Gönderirken boş sorular listede işaretlenir; ikinci basış boş haliyle gönderir (açılır onay penceresi yok).
- Kod yazma sorusunda görev metni editörün üstünde, yazma alanı satır numaralı.
- Sonuç ekranında soru listesinden çözüme atlama ve "yalnız yanlışlar" filtresi.
- Pratikte kontrol sonrası doğru şık yeşil, seçilen yanlış şık kırmızı.
- Öğretmen paneli: sınavdaki öğrencilerin kaç soru cevapladığı canlı görünür; öğrenci ayrıntısı sekmede açılır,
  adres, QR ve ayarlar yan panelde.
- Kodda bitişik harfler kapalı (`==` iki ayrı işaret görünür). Başlık yazı tipi Fraunces; Caveat kaldırıldı.

### Kolay başlatma
- `baslat.bat` (Windows) ve `baslat.command` (Mac): çift tıklayınca ilk açılışta Python ortamını ve paketleri
  kurar, sunucuyu başlatır ve öğretmen panelini tarayıcıda açar.

## 3.1.0

### Öğrenme yardımları
- **Kodu adım adım izle:** Pratikte, sınav sonucunda ve öğretmen panelinde. Satır satır değişkenler, ekran
  çıktısı ve hata satırı.
- **Neden yanlış:** 75 şablonun her yanlış seçeneği için açıklama; doğru/yanlış sorularında her ifade için.
- **İpucu:** Pratikte, cevap vermeden önce; ipucuyla verilen doğru cevap ayrıca işaretlenir.
- **Bu konudan yeni soru:** Yanlıştan sonra aynı şablondan farklı değerlerle yeni soru.
- **Konu tamamlama:** İpucusuz iki doğruyla; içindekiler sayfasında "3 / 8 konu tamamlandı" ve tamamlanan konular.
- **Öğretmen paneli:** Konu analizinde en sık yanlış cevap ve yanılgının açıklaması.

### Görsel kimlik
- "Optik form ve kareli defter" tasarım sistemi: optik şıklar, kırmızı kenar çizgili soru kâğıdı, kırmızı
  kalemle okunmuş sonuç. Yazı tipleri sunucuya gömülü (internetsiz). Ayrıntılar: `docs/TASARIM.md`.

### Soru bankası
- Az çeşitli 22 şablon zenginleştirildi; her şablon 500 üretimde en az 12 farklı soru veriyor.

### Düzeltmeler
- Konu tamamlama, birden fazla şablonu olan konularda bütün şablonları şart koşuyor.
- Beklenmedik istek gövdesi (liste, metin) sunucu hatası yerine düzgün bir yanıt alıyor.
- Kod izinde tek bir uzun print çıktı sınırını aşamıyor; izin önbelleği çağıranlar arasında paylaşılmıyor.

## 3.0.0
- Paket yapısı (`pytest_pro/`), 11 ünite ve 75 soru şablonu, pratik modu, sınav başlığı ve ünite seçimi,
  sürümlü veritabanı göçleri.
