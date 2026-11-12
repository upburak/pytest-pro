# Sürüm Notları

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
