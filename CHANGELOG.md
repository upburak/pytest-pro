# Sürüm Notları

## 3.3.1

### Kod yazımına uygun gösterim
- Kod yazı tipinin `>=`, `<=`, `==`, `!=` işaretlerini ≥ ≤ gibi tek simgeye dönüştürmesi her yerde kapatıldı
  (kod, şıklar, boşluk kutuları, kod izi, yazma alanı). Önceki sürümde bazı yerlerde açık kalıyordu.
- Soru metni, ipucu ve açıklamalarda matematik defteri yazımı kod yazımına çevrildi: `×` yerine `*`, `n!` yerine
  "faktöriyel", `→` yerine sözle anlatım ("x > 10 ifadesi True olur", "Adım adım: 2, sonra 10, sonra 20"),
  durum anlatırken `i = 3 olduğunda` yerine `i == 3 olduğunda`.
- Bankanın tamamını tarayan bir test bu yazımların yeniden girmesini engeller.

## 3.3.0

### Öğretmen paneli: sınavlar listesi
- "Sınavı aç"a her basış ayrı bir sınavdır. Solda sınavlar listelenir (en yenisi üstte, başlık, tarih-saat,
  öğrenci sayısı, ortalama); bir sınava tıklayınca öğrencileri, istatistikleri ve konu analizi açılır.
- Sınav silme: listedeki ✕ ya da sınavın içindeki "Bu sınavı sil"; süren öğrenci varken silinemez.
  "Tüm kayıtları sil" iki onay ister. Excel çıktısı seçili sınav ya da tümü için.
- Tekrar giriş kuralı ve deneme numarası sınav başınadır. Açık bırakılan sınava ertesi gün girilirse yeni sınav başlar.
- Eski kayıtlar başlık ve güne göre sınavlara dönüştürülür (veritabanı otomatik güncellenir).

### Soru bankası: 75'ten 164 şablona
- Ölçme-değerlendirme denetimi (`docs/OLCME_RAPORU.md`): mevcut bankadaki hatalar düzeltildi, 86 yeni şablon eklendi
  ve yeni şablonlar ayrıca denetlendi. Her ünitede en az 2 kod yazma sorusu (toplam 26).
- Yeni soru tipi **boşluk doldurma**: kodun içindeki kutulara yazılır; her boşluk ayrı denetlenir, kısmi sonuç notta.
- Hesaplanan doğru/yanlış, seçenekleri kod olan çoktan seçmeli ("hangi kod doğru çalışır?") ve hem hatalı hem
  hatasız sonuç verebilen çıktı soruları.
- Kod yazma denetimi: yanlış kodun doğru sayılması (break ile kesilen döngü, parametrenin üstüne yazma…) ve doğal
  doğru çözümlerin reddedilmesi (etiketli print, f-string, `range(1, n + 1)`…) düzeltildi. Öğrenci kodu hâlâ hiç
  çalıştırılmaz; denetim sözdizimi ağacı üzerinde, adım sınırlı kendi izleyicimizle yapılır.
- Ölçme kalitesi: iki değerli ve cevabı hiç değişmeyen şıklı sorular düzeltildi, anlamsız dolgu şıklar kaldırıldı;
  her şablon için çeşitlilik, en sık cevap oranı ve dolgu şık oranı testlerle denetlenir.
- Türkçe: karakter hataları ve sayıdan sonraki ek uyumsuzlukları ("6'e") bankanın tamamında düzeltildi.

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
