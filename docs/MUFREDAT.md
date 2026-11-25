# Müfredat Haritası

Bu dosya koddan otomatik üretilir; elle düzenlemeyin:
`python -m pytest_pro.questions.mufredat > docs/MUFREDAT.md`

Toplam **11 ünite**, **164 soru şablonu**. Her şablon her çağrıldığında farklı değerlerle yeni bir soru üretir.

| # | Ünite | Seviye | Şablon |
|---|---|---|---|
| 1 | Temel Giriş/Çıkış ve Değişkenler | Başlangıç | 16 |
| 2 | Veri Tipleri ve Dönüşümler | Başlangıç | 15 |
| 3 | Operatörler | Başlangıç | 13 |
| 4 | Metinler (String) | Başlangıç | 16 |
| 5 | Koşullu İfadeler | Başlangıç | 13 |
| 6 | Döngüler | Orta | 16 |
| 7 | Listeler | Orta | 16 |
| 8 | Sözlük, Demet ve Küme | Orta | 15 |
| 9 | Fonksiyonlar ve Modüller | Orta | 19 |
| 10 | Hata Yönetimi | Orta | 12 |
| 11 | Nesne Yönelimli Programlama | İleri | 13 |

## 1. Temel Giriş/Çıkış ve Değişkenler

**Seviye:** Başlangıç · **Kimlik:** `temel`

print() ve parametreleri, input(), değişken tanımlama ve adlandırma, f-string, çoklu atama.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Print Parametreleri (sep) | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Print Parametreleri (end) | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| f-string Kullanımı | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| input() Veri Tipi | Doğru / Yanlış | — |
| Değişken Adlandırma | Çoktan seçmeli | Python ad kurallarıyla denetlenir |
| Değişken Atama | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Çoklu Atama | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Değişken & Aritmetik (Kod Yazma) | Kod yazma | — |
| Print Parametreleri (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Yorum Satırları | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| sep ve end Birlikte (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| f-string Tamamlama (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Değer Takası (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Selamlama (Kod Yazma) | Kod yazma | — |
| Dikdörtgen Alan ve Çevre (Kod Yazma) | Kod yazma | — |
| Hangi Kod Bu Çıktıyı Verir? | Çoktan seçmeli | Her seçenek çalıştırılır; yalnızca doğrusu beklenen sonucu vermeli |

## 2. Veri Tipleri ve Dönüşümler

**Seviye:** Başlangıç · **Kimlik:** `veri_tipleri`

int, float, str, bool; type(), int()/float()/str()/bool() dönüşümleri, input() ile sayı alma.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| type() ve Veri Tipleri | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Tip Dönüşümleri (int/str) | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Tip Dönüşümleri (float/int) | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| bool() Dönüşümü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| input() ve Tip Dönüşümü | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Metin ve Sayı Birleştirme | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Metin ve Sayı Birleştirme | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Dönüşüm Hataları | Çoktan seçmeli | Her seçenek çalıştırılır |
| Tip İddiası (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| int(input()) Boşluğu | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Dönüşüm Yönü (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Karışık Dönüşüm Çıktısı | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| bool Aritmetiği | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Metinleri Sayıya Çevirip Toplama (Kod Yazma) | Kod yazma | — |
| Sıcaklık Dönüşümü (Kod Yazma) | Kod yazma | — |

## 3. Operatörler

**Seviye:** Başlangıç · **Kimlik:** `operatorler`

Aritmetik (+ - * / // % **), işlem önceliği, karşılaştırma, mantıksal (and/or/not) ve birleşik atama (+=, -=, *=) operatörleri.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Tam Bölme ve Mod | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Bölme Sonucunun Tipi | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| İşlem Önceliği | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Karşılaştırma ve Mantıksal Operatörler | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Birleşik Atama Operatörleri | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Atama ve Karşılaştırma | Doğru / Yanlış | — |
| Operatör İddiası (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| Eksik Operatör (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Birleşik Atama Zinciri | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Bölünebilme Koşulu | Çoktan seçmeli | Her seçenek çalıştırılır; yalnızca doğrusu beklenen sonucu vermeli |
| Kısa Devre Değerlendirme | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Saniyeyi Dakikaya Çevir (Kod Yazma) | Kod yazma | — |
| Üç Notun Ortalaması (Kod Yazma) | Kod yazma | — |

## 4. Metinler (String)

**Seviye:** Başlangıç · **Kimlik:** `metinler`

İndeksleme, dilimleme, len(), metin metotları (upper, lower, replace, strip, split, count), in operatörü, metin tekrarı ve biçimlendirme.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Metin Tekrarı | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| İndeksleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Dilimleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| len() Fonksiyonu | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Metin Metotları | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| split() ve strip() | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| in Operatörü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| f-string Biçimlendirme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| İndeks İddiası (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| Dilimi Tamamla (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Metot Bul (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| find() ve count() | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Metinler Değiştirilemez | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Metin İşlemleri İddiası (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| Kelimeyi Ters Çevir (Kod Yazma) | Kod yazma | — |
| Sesli Harf Sayısı (Kod Yazma) | Kod yazma | — |

## 5. Koşullu İfadeler

**Seviye:** Başlangıç · **Kimlik:** `kosullar`

if, elif, else blokları, girinti, iç içe koşullar ve mantıksal operatörlerle koşul kurma.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| if / elif / else | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Ayrı if Blokları | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Koşullarda Mantıksal Operatörler | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Tek / Çift Kontrolü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Girinti ve Blok Yapısı | Doğru / Yanlış | — |
| İç İçe Koşullar | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Koşul Sırası Hatası | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Koşulu Tamamla (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Eşitlikte Hangisi? | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Koşullar (Doğru / Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| Tek mi Çift mi? (Kod Yazma) | Kod yazma | — |
| Not Harfi (Kod Yazma) | Kod yazma | — |
| Hangi Kod Doğru Çalışır? | Çoktan seçmeli | Her seçenek çalıştırılır; yalnızca doğrusu beklenen sonucu vermeli |

## 6. Döngüler

**Seviye:** Orta · **Kimlik:** `donguler`

for döngüsü ve range(), while döngüsü, sayaç ve toplam değişkenleri, break, continue, iç içe döngüler.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| range() Fonksiyonu | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| for ile Toplam | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| while Döngüsü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| break ve continue | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| İç İçe Döngüler | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Metin Üzerinde Döngü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| for Döngüsü (Kod Yazma) | Kod yazma | — |
| range() ile Döngü (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Kaç Tur? (Doğru / Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| range'i Tamamla (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| while Koşulunu Tamamla (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Koşullu Toplam | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| while True ve break | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Hangi Döngü Hiç Bitmez? | Çoktan seçmeli | Her seçenek çalıştırılır; yalnızca doğrusu beklenen sonucu vermeli |
| 1'den n'e Toplam (Kod Yazma) | Kod yazma | — |
| Çarpım Tablosu (Kod Yazma) | Kod yazma | — |

## 7. Listeler

**Seviye:** Orta · **Kimlik:** `listeler`

Liste oluşturma, indeksleme, dilimleme, append/insert/remove/pop, len/sum/max/min, sort ve sorted, listelerin değiştirilebilirliği, liste üreteçleri (list comprehension).

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Liste İndeksleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Liste Sınırları | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Liste Metotları | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Liste Dilimleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Hazır Fonksiyonlar | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| sort() ve sorted() | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Listeler Değiştirilebilir | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Liste Üreteçleri | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| append ile extend (Doğru / Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| Liste Metodunu Bul (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Liste Üreteci (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| index() ve count() | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| İç İçe Liste | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Listeyi Kopyalama | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| max() Kullanmadan En Büyük (Kod Yazma) | Kod yazma | — |
| Listeyi Süzme (Kod Yazma) | Kod yazma | — |

## 8. Sözlük, Demet ve Küme

**Seviye:** Orta · **Kimlik:** `koleksiyonlar`

dict (anahtar-değer, get, keys/values/items, güncelleme), tuple (değiştirilemezlik, açma), set (tekrarsız elemanlar, kesişim/birleşim).

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Sözlükten Değer Okuma | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Olmayan Anahtar | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Sözlük Güncelleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Sözlük Üzerinde Döngü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Demetler Değiştirilemez | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Demet Açma | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Kümeler | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| in Sözlükte Neye Bakar? (Doğru / Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| keys / values / items (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Sözlükle Sayma | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Yinelenen Anahtar | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Sözlük Boyutu | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Kümeler ve Tek Elemanlı Demet (Doğru / Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| En Yüksek Notlu Öğrenci (Kod Yazma) | Kod yazma | — |
| Sözlükle Frekans (Kod Yazma) | Kod yazma | — |

## 9. Fonksiyonlar ve Modüller

**Seviye:** Orta · **Kimlik:** `fonksiyonlar`

def ile fonksiyon tanımlama, parametre ve return, varsayılan parametre, yerel/global kapsam, birden fazla değer döndürme, özyineleme, import ve math modülü.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Fonksiyon ve return | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Varsayılan Parametre | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| return Olmayan Fonksiyon | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Yerel ve Global Değişkenler | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Birden Fazla Değer Döndürme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Özyineleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| math Modülü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Fonksiyon Kavramları | Doğru / Yanlış | — |
| Fonksiyon Yazma (Kod Yazma) | Kod yazma | — |
| def ve return (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| print mi return mü? (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| Argümanlarla Çağrı (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| global Anahtar Sözcüğü (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| İsimli Argümanlar | Kısa cevap | — |
| Fonksiyon İçinde Fonksiyon | Kısa cevap | — |
| Hangi Fonksiyon Doğru? | Çoktan seçmeli | Her seçenek çalıştırılır; yalnızca doğrusu beklenen sonucu vermeli |
| True/False Döndüren Fonksiyon (Kod Yazma) | Kod yazma | — |
| Liste Ortalaması Fonksiyonu (Kod Yazma) | Kod yazma | — |
| Faktöriyel Fonksiyonu (Kod Yazma) | Kod yazma | — |

## 10. Hata Yönetimi

**Seviye:** Orta · **Kimlik:** `hatalar`

Sık karşılaşılan hata türleri (ZeroDivisionError, ValueError, TypeError, IndexError, KeyError, NameError), try / except / else / finally.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Hata Türleri | Çoktan seçmeli | Kod çalıştırılıp hata türü karşılaştırılır |
| try / except | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| else ve finally | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Hata Yönetimi Kavramları | Doğru / Yanlış | — |
| Hata Türü İddiası (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| Doğru except Türü (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Birden Fazla except | Kısa cevap | — |
| Doğrulama Döngüsü | Kısa cevap | — |
| Hatanın Yayılması | Çoktan seçmeli | Kod çalıştırılıp çıktı ya da hata türü karşılaştırılır |
| Hata Yönetimi Kavramları II | Doğru / Yanlış | — |
| Güvenli Bölme Fonksiyonu (Kod Yazma) | Kod yazma | — |
| Geçerli Girdiyi Yakala (Kod Yazma) | Kod yazma | — |

## 11. Nesne Yönelimli Programlama

**Seviye:** İleri · **Kimlik:** `nesne`

class, __init__ ve self, nesne özellikleri ve metotları, sınıf değişkenleri, kalıtım ve metot ezme, __str__.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Sınıf ve Nesne | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Sınıf Değişkenleri | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Kalıtım ve Metot Ezme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| __str__ Metodu | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Nesne Yönelimli Kavramlar | Doğru / Yanlış | — |
| Sınıf mı Nesne mi? (Doğru/Yanlış) | Doğru / Yanlış | Kod çalıştırılıp iddia gerçek sonuçla karşılaştırılır |
| self Boşlukları (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| super() ile Kalıtım (Boşluk Doldurma) | Boşluk doldurma | Doldurulmuş kod çalıştırılıp çıktı karşılaştırılır |
| Banka Hesabı | Kısa cevap | — |
| isinstance ve Kalıtım | Çoktan seçmeli | — |
| Nesne Listesi | Kısa cevap | — |
| Şekil Sınıfı (Kod Yazma) | Kod yazma | — |
| Sayaç Sınıfı (Kod Yazma) | Kod yazma | — |
