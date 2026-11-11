# Tasarım Sistemi: "Optik form ve kareli defter"

PyTest Pro'nun görsel dili, bir lise öğrencisinin sınav masasından gelir: kareli defter kâğıdı,
optik form, kurşun kalem, tükenmez kalem, öğretmenin kırmızı kalemi ve fosforlu kalem.
Her renk ve şekil bu nesnelerden birine karşılık gelir; o nesnenin sınıftaki anlamını taşır.

Kaynak: `pytest_pro/static/css/style.css`. Tüm değerler dosyanın başındaki değişkenlerden gelir.

## İlkeler

1. **Cesaret tek yerde.** Dikkat çeken iki öğe var: optik yuvarlaklar ve kırmızı kalemle okunmuş sonuç.
   Geri kalan her şey sade kalır. Yeni bir bileşen eklerken bunlarla yarışmamalı.
2. **Renk anlam taşır.** Mavi eylem, kırmızı düzeltme ve yanlış, yeşil doğru, sarı "şimdi" demektir.
   Bir rengi yalnızca süs için kullanmayın.
3. **Kâğıt nesneleri farklı görünür.** Soru kâğıdı (kırmızı kenar çizgili), cevap kâğıdı (kırmızı üst şeritli)
   ve sınıf defteri (çizgili tablo) aynı kartın kopyaları değildir.
4. **Sade Türkçe.** Cümle düzeninde yazılır (yalnızca ilk harf büyük). BÜYÜK HARF etiket, `·` ile bağlanmış
   meta yazıları ve düğmelerde ok işareti kullanılmaz. Düğme, yaptığı işi söyler: "Sınavı bitir ve gönder".
5. **İnternetsiz.** Yazı tipleri `static/fonts` içindedir; dış kaynak yüklenmez.
6. **Satır içi stil ve betik yok.** İçerik Güvenlik Politikası (CSP) bunları engeller; görünüm sınıflarla verilir.

## Renkler

| Değişken | Değer | Karşılığı | Kullanım |
|---|---|---|---|
| `--paper` | `#F6F8FB` | Defter kâğıdı | Sayfa zemini |
| `--grid` | `#DCE5F0` | Defter kareleri | Zemin ızgarası, kod alanı satırları |
| `--sheet` | `#FFFFFF` | Soru kâğıdı | Kâğıt yüzeyleri |
| `--rule` | `#C9D5E6` | Cetvel çizgisi | Kenarlık, tablo satırı |
| `--graphite` | `#2A2F36` | Kurşun kalem | Ana metin, dolu optik yuvarlak |
| `--graphite-soft` | `#5B6472` | Silik kurşun kalem | İkincil metin (beyaz üstünde 5,9:1 kontrast) |
| `--ink` | `#1C3FAA` | Tükenmez mavisi | Düğme, bağlantı, odak halkası |
| `--pen` | `#C8102E` | Öğretmen kırmızısı | Yanlış, düzeltme, puan, optik baskı, kenar çizgisi |
| `--ok` | `#17784A` | Yeşil kalem | Doğru işareti, başarılı durum |
| `--marker` | `#FFE24D` | Fosforlu kalem | Yalnızca "şimdi": bulunulan soru, son dakika, ipucu |

Açık tonlar (`--ink-wash`, `--pen-wash`, `--ok-wash`) seçili veya üzerine gelinen satırlar içindir.

## Yazı

| Rol | Yazı tipi | Not |
|---|---|---|
| Arayüz ve metin | Atkinson Hyperlegible Next | Okunurluk için tasarlandı; 0/O, 1/l/I ayrımı belirgin. Türkçe harflerin tamamını içerir. |
| Kod | JetBrains Mono | Soru kodu, şıklar, öğrenci cevapları |
| El yazısı | Caveat | **Yalnızca** öğretmenin kalemi: puan ve düzeltme notları |

Ölçek (1,25 oranlı): `--fs-xs` 13, `--fs-sm` 15, `--fs-md` 17 (gövde), `--fs-lg` 21, `--fs-xl` 28, `--fs-score` 88 piksel.
Sayılar `font-variant-numeric: tabular-nums` ile hizalanır (sayaç, istatistikler).
Okunan metinler en fazla 62–70 karakter genişliğindedir.

Atkinson Hyperlegible'ın ilk sürümünde büyük "İ" harfi yoktur; bu yüzden **Next** sürümü kullanılır.

## Ölçü

Boşluk: `--s1` 4 · `--s2` 8 · `--s3` 12 · `--s4` 16 · `--s5` 24 · `--s6` 32 · `--s7` 48 piksel.
Köşe: kâğıt `--radius-paper` 3 piksel (kâğıt köşesi neredeyse keskindir), düğme ve giriş `--radius-ctl` 6 piksel.
Gölge: tek bir `--lift` (kâğıdın masadan hafifçe kalkması). Dokunma hedefleri en az 44 piksel.

## Bileşenler

### Soru kâğıdı `.sheet`
Beyaz kâğıt; soldan `--margin-x` kadar içeride kırmızı kenar çizgisi. Soru numarası (`.q-num`)
kenar boşluğunda durur, defterde numaranın yazıldığı yer gibi. Telefonda kenar boşluğu daralır.

### Optik şık `.opt` + `.bubble`
Her şık harfli bir yuvarlaktır (A–D; doğru/yanlış sorularında D ve Y). Yuvarlağın çizgisi optik form
baskısı gibi kırmızıdır. Seçilince kurşun kalemle doldurulmuş gibi koyulaşır ve harf beyaza döner.
Gerçek `<input type="radio">` görünmez ama klavyeyle odaklanabilir; odak halkası yuvarlağın çevresinde görünür.

| Durum | Görünüm |
|---|---|
| Boş | Kırmızı çizgili yuvarlak, kırmızı harf |
| Üzerine gelme | Satırın arkasında açık mavi leke |
| Seçili | Koyu kurşun dolgu, beyaz harf |
| Odak | Mavi odak halkası |

### Cevap kâğıdı `.answer-sheet` + `.nav-grid`
Üstünde kırmızı şerit olan optik form. Her soru bir numara ve yuvarlak; cevaplanan sorunun yuvarlağı dolu,
bulunulan soru fosforlu kalemle işaretli. Masaüstünde sayfa kaydırılırken yerinde kalır; telefonda kalmaz.
Son dakikada sayaç kırmızıya döner ve fosforlu kalemle işaretlenir.

### Sonuç `.grade` + `.score-mark`
Puan, Caveat ile kırmızı el yazısıyla yazılır ve elle çizilmiş bir çemberle çevrilir. Çember sayfa açılırken
bir kez çizilir; uygulamadaki tek kendiliğinden hareket budur. "Hareketi azalt" tercihi olan cihazlarda çizilmiş hâlde gelir.
Soru listesinde (`.sol`) kenar boşluğunda kırmızı ✗ veya yeşil ✓ kalem işareti bulunur; açıklamalar fosforlu
kalemle işaretlenmiş bir not kutusundadır (`.exp`).

### Düğme `.btn`
| Tür | Görünüm | Kullanım |
|---|---|---|
| (varsayılan) | Mavi çizgi, beyaz zemin | İkincil eylem |
| `.primary` | Dolu mavi | Sayfadaki ana eylem (bir tane) |
| `.green` | Dolu yeşil | Bitirme eylemi: "Sınavı bitir ve gönder", "Yeni soru" |
| `.red` | Kırmızı çizgi | Silme |
| `.sm` / `.block` | Küçük / tam genişlik | |

### Rozet `.badge`
Mühür gibi çizgili kutu: `.b-ok` başarılı veya Başlangıç, `.b-no` tekrar etmeli, `.b-live` sınavda veya İleri,
`.b-time` deneme numarası, otomatik gönderim, Orta.

### Sınıf defteri (öğretmen paneli)
Tablo başlığı kalın kurşun çizgiyle ayrılır, satırlar ince cetvel çizgileriyle. İstatistikler ayrı kartlar
değil, dikey çizgilerle bölünmüş tek bir şerittir (`.grid4`). Konu analizi çubukları (`.meter`) elle
taranmış gibidir: yeşil %75 ve üstü, kahverengi %50–74, kırmızı %50'nin altı.

### İçindekiler (pratik modu)
Üniteler kitap içindekileri gibi listelenir: kırmızı ünite numarası, başlık, kısa açıklama ve seviye mührü.
Numara kullanılır, çünkü üniteler gerçekten öğrenme sırasıdır.

## Erişilebilirlik

- Metin kontrastı WCAG AA üstündedir (en düşük ikincil metin 5,9:1).
- Tüm denetimler klavyeyle kullanılabilir; odak her yerde aynı mavi halkayla gösterilir.
- Doğru ve yanlış yalnızca renkle değil, ✓ ve ✗ işaretiyle ve "Doğru" ve "Yanlış" sözcükleriyle de belirtilir.
- Sayaç `role="timer"`, kayıt durumu ve geri bildirim `aria-live` ile duyurulur.
- `prefers-reduced-motion` tüm geçişleri kapatır.

## Yapılmaması gerekenler

| Yapın | Yapmayın |
|---|---|
| Yeni renk gerekiyorsa sınıftaki bir nesneye bağlayın | Süs için degrade veya yeni vurgu rengi eklemek |
| Fosforlu kalemi yalnızca "şimdi" için kullanın | Başlıkları veya düğmeleri sarıyla vurgulamak |
| Caveat'i yalnızca öğretmenin kalemi için kullanın | El yazısını başlık veya gövde metninde kullanmak |
| Cümle düzeninde, eylemi söyleyen düğme metni yazın | BÜYÜK HARF etiket, "Gönder →" gibi oklu düğme |
| Kâğıt nesnelerini farklı tutun | Her şeyi aynı gölgeli, yuvarlak kartlara koymak |

## Yazı tipi lisansları

Üç yazı tipi de SIL Açık Font Lisansı 1.1 ile dağıtılır; lisans metinleri `pytest_pro/static/fonts/OFL-*.txt` dosyalarındadır.
