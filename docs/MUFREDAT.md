# Müfredat Haritası

Bu dosya koddan otomatik üretilir; elle düzenlemeyin:
`python -m pytest_pro.questions.catalog > docs/MUFREDAT.md`

Toplam **11 ünite**, **75 soru şablonu**. Her şablon her çağrıldığında farklı değerlerle yeni bir soru üretir.

| # | Ünite | Seviye | Şablon |
|---|---|---|---|
| 1 | Temel Giriş/Çıkış ve Değişkenler | Başlangıç | 8 |
| 2 | Veri Tipleri ve Dönüşümler | Başlangıç | 8 |
| 3 | Operatörler | Başlangıç | 6 |
| 4 | Metinler (String) | Başlangıç | 8 |
| 5 | Koşullu İfadeler | Başlangıç | 5 |
| 6 | Döngüler | Orta | 7 |
| 7 | Listeler | Orta | 8 |
| 8 | Sözlük, Demet ve Küme | Orta | 7 |
| 9 | Fonksiyonlar ve Modüller | Orta | 9 |
| 10 | Hata Yönetimi | Orta | 4 |
| 11 | Nesne Yönelimli Programlama | İleri | 5 |

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

## 2. Veri Tipleri ve Dönüşümler

**Seviye:** Başlangıç · **Kimlik:** `veri_tipleri`

int, float, str, bool; type(), int()/float()/str()/bool() dönüşümleri, input() ile sayı alma.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| type() ve Veri Tipleri | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Tip Dönüşümleri (int/str) | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Tip Dönüşümleri (float/int) | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| bool() Dönüşümü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| input() ve Tip Dönüşümü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Metin ve Sayı Birleştirme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Metin ve Sayı Birleştirme | Çoktan seçmeli | Kod çalıştırılıp hata türü karşılaştırılır |
| Dönüşüm Hataları | Çoktan seçmeli | Her seçenek çalıştırılır |

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

## 4. Metinler (String)

**Seviye:** Başlangıç · **Kimlik:** `metinler`

İndeksleme, dilimleme, len(), metin metotları (upper, lower, replace, strip, split, count), in operatörü, metin tekrarı ve biçimlendirme.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Metin Tekrarı | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| İndeksleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Dilimleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| len() Fonksiyonu | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| Metin Metotları | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| split() ve strip() | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| in Operatörü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| f-string Biçimlendirme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |

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

## 7. Listeler

**Seviye:** Orta · **Kimlik:** `listeler`

Liste oluşturma, indeksleme, dilimleme, append/insert/remove/pop, len/sum/max/min, sort ve sorted, listelerin değiştirilebilirliği, liste üreteçleri (list comprehension).

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Liste İndeksleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Liste Sınırları | Çoktan seçmeli | Kod çalıştırılıp hata türü karşılaştırılır |
| Liste Metotları | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Liste Dilimleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Hazır Fonksiyonlar | Kısa cevap | Kod çalıştırılıp çıktı karşılaştırılır |
| sort() ve sorted() | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Listeler Değiştirilebilir | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Liste Üreteçleri | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |

## 8. Sözlük, Demet ve Küme

**Seviye:** Orta · **Kimlik:** `koleksiyonlar`

dict (anahtar-değer, get, keys/values/items, güncelleme), tuple (değiştirilemezlik, açma), set (tekrarsız elemanlar, kesişim/birleşim).

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Sözlükten Değer Okuma | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Olmayan Anahtar | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Sözlük Güncelleme | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Sözlük Üzerinde Döngü | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Demetler Değiştirilemez | Çoktan seçmeli | Kod çalıştırılıp hata türü karşılaştırılır |
| Demet Açma | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Kümeler | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |

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

## 10. Hata Yönetimi

**Seviye:** Orta · **Kimlik:** `hatalar`

Sık karşılaşılan hata türleri (ZeroDivisionError, ValueError, TypeError, IndexError, KeyError, NameError), try / except / else / finally.

| Konu | Soru tipi | Cevap anahtarı doğrulaması |
|---|---|---|
| Hata Türleri | Çoktan seçmeli | Kod çalıştırılıp hata türü karşılaştırılır |
| try / except | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| else ve finally | Çoktan seçmeli | Kod çalıştırılıp çıktı karşılaştırılır |
| Hata Yönetimi Kavramları | Doğru / Yanlış | — |

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
