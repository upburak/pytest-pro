# Tasarım Sistemi: "Editör"

PyTest Pro bir kod editörü gibi görünür: öğrenci Python sınavına girerken gerçekten kod
okuyormuş ve yazıyormuş gibi hisseder. Ekran iki dünyaya ayrılır:

- **Okunacak taraf (solda ve ortada):** editör. Solda dosya listesi (`soru_01.py`, `soru_02.txt` ...),
  ortada satır numaralı, renklendirilmiş kod.
- **Cevaplanacak taraf (kodun hemen altında):** adaçayı yeşili cevap paneli. Soru başlığı, şıklar ve düğmeler burada.
  Göz koddan şıklara kısa bir yol alır; kısa şıklar iki sütunda dizilir.

Ekran boydan boya kaplanmaz: içerik ortalanmış, kendi yüksekliğinde bir pencerededir. Üst şerit (süre,
gönder) ve alt durum çubuğu sayfa kaydırılsa da görünür kalır.

Kaynak: `pytest_pro/static/css/style.css`. Tüm değerler dosyanın başındaki değişkenlerden gelir.

## İlkeler

1. **Önce oku, hemen altında cevapla.** Kodlu soruda kod üstte, soru ve şıklar altta. Kodsuz soruda
   soru metni editörde büyük yazılır, cevap panelinde kısa bir yönerge ("Doğru cevabı seç.") kalır. Kod yazma
   sorusunda görev metni editörün üstünde, yazma alanı hemen altındadır.
2. **Tek vurgu rengi yeşil.** Seçili şık, ilerleme, gönder düğmesi ve durum çubuğu yeşildir. Kırmızı yalnızca
   yanlış cevap ve son dakika uyarısı içindir; sarı yalnızca boş soru uyarısı ve kod izindeki çalışan satır içindir.
3. **Dosya listesi = soru haritası.** `✓` cevaplandı, `●` şu anki soru, `○` boş. Gönderirken boş sorular
   sarıyla işaretlenir; ikinci basış boş haliyle gönderir.
4. **Klavyeyle çalışılabilir.** A–E (ya da 1–5) şık seçer, D/Y doğru/yanlış seçer, ←/→ soru değiştirir.
   Pratikte Ctrl+Enter kontrol eder ve sonraki soruya geçer. Kısayollar durum çubuğunda yazar.
5. **Sade Türkçe.** Cümle düzeninde yazılır. Düğme yaptığı işi söyler: "Sınavı gönder", "Cevabı kontrol et".
6. **İnternetsiz.** Yazı tipleri `static/fonts` içindedir; dış kaynak yüklenmez.
7. **Satır içi stil ve betik yok.** İçerik Güvenlik Politikası (CSP) bunları engeller; görünüm sınıflarla verilir.

## Renkler

| Değişken | Değer | Kullanım |
|---|---|---|
| `--chrome` | `#E4E9F0` | Üst şerit ve pencere zemini |
| `--side` | `#EEF2F6` | Dosya listesi, sekme çubuğu |
| `--editor` | `#FBFCFE` | Kod alanı |
| `--line` | `#D3DAE3` | Editör çizgileri |
| `--ink` | `#1C2733` | Ana metin |
| `--mute` | `#66768A` | İkincil metin |
| `--sage` | `#F1F4EF` | Cevap paneli |
| `--green` | `#2F7D5B` | Tek vurgu: seçim, gönder, ilerleme, durum çubuğu |
| `--forest` | `#1B2A22` | Panel metni, koyu düğme ("Sonraki") |
| `--bad` | `#B3261E` | Yanlış, son dakika |
| `--warn` | `#8A5A00` | Boş soru uyarısı |

Sözdizimi renkleri: anahtar kelime `--tk-kw` mor, metin `--tk-st` yeşil, sayı `--tk-nu` turuncu,
hazır fonksiyon `--tk-fn` mavi, yorum `--tk-cm` gri ve eğik.

## Yazı

| Rol | Yazı tipi | Kullanım |
|---|---|---|
| Arayüz | Atkinson Hyperlegible Next | Gövde metni, düğmeler, etiketler (okunaklılık için tasarlandı) |
| Kod | JetBrains Mono | Kod, şıklar, dosya adları. Bitişik harfler kapalı: `==` iki ayrı işaret görünür |
| Başlık | Fraunces | Cevap panelindeki soru başlığı, puan, sınıf istatistikleri |

Uzun görev metinleri (90 karakteri aşan kodlu ya da kod yazma soruları) başlık yazısıyla değil,
gövde yazısıyla gösterilir.

## Ekranlar

- **Öğrenci girişi:** solda `hosgeldin.py` kodu, sağda giriş formu.
- **Sınav:** solda dosya listesi; sağ sütunda üstte kod, altta cevap paneli; üstte süre ve "Sınavı gönder", altta durum çubuğu
  (cevaplanan sayısı, kayıt durumu, kısayollar).
- **Sonuç:** solda `✓`/`✗` soru listesi (tıklayınca o soruya gider), ortada puan kartı ve çözümler;
  varsayılan olarak yalnız yanlışlar gösterilir.
- **Pratik:** solda üniteler ve tamamlanan konu sayısı; üstte soru ve kod izi, altta cevap ve geri bildirim.
  Kontrolden sonra doğru şık yeşil, seçilen yanlış şık kırmızı olur.
- **Öğretmen:** solda öğrenciler (sınavdakiler ilerleme çubuğuyla, bitirenler puanla), ortada sınıf özeti
  ya da seçilen öğrencinin ayrıntısı (sekme olarak açılır, Esc ile kapanır), sağda adres, QR ve ayarlar.

## Dar ekran

860 pikselin altında sütunlar alt alta dizilir: dosya listesi yatay kaydırılan bir şerit olur,
pencere kenarlıkları kalkar ve şıklar tek sütuna iner.
