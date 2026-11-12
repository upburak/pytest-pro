# Geliştirme Rehberi

Bu belge PyTest Pro'yu büyütmek isteyenler içindir: yeni ünite, yeni soru şablonu, yeni kod
denetleyicisi veya veritabanı değişikliği eklemek.

## Mimari

```
server.py                    Başlatıcı (python server.py)
pytest_pro/
  __init__.py                Sürüm numarası, create_app
  app.py                     Uygulama fabrikası, güvenlik başlıkları, sunucu başlatma
  clock.py                   Zaman kaynağı (testlerde değiştirilir)
  db.py                      SQLite bağlantısı ve sürümlü şema göçleri
  settings.py                Öğretmen ayarları: varsayılanlar, doğrulama, kayıt
  exams.py                   Sınav iş mantığı: süre, cevap temizleme, puanlama, kapanış, istatistik
  auth.py                    Öğretmen şifresi ve kaba kuvvet koruması
  practice.py                Pratik modu soru deposu (bellekte, süreli)
  routes/
    pages.py                 HTML sayfaları:  /  /pratik  /ogretmen
    student.py               Öğrenci API'si:  /api/status, start, resume, save, submit
    teacher.py               Öğretmen API'si: /api/info, settings, results, results.csv, qr.svg
    practice.py              Pratik API'si:   /api/practice/units, next, check
  questions/
    __init__.py              Soru üretimi, puanlama, dışa açık arayüz
    registry.py              Ünite ve şablon kaydı (register_unit, @UNIT.question)
    helpers.py               Şablonlarda ortak yardımcılar (output_question, tf_question, ...)
    codecheck.py             Kod yazma sorularının AST denetleyicileri
    catalog.py               Müfredat haritası üretici (docs/MUFREDAT.md)
    tracer.py                Adım adım kod izleme motoru (yalnızca şablon kodu çalıştırır)
    units/uNN_*.py           Her ünite ayrı bir dosya
  templates/                 base.html + sayfa şablonları
  static/css, static/js      common.js ortak yardımcılar; sayfa başına bir betik
tests/                       pytest testleri
docs/                        Belgeler
```

Katmanlar tek yönlü bağımlıdır: `routes` → `exams` / `settings` → `questions`. Soru bankası
Flask'a ve veritabanına bağlı değildir; tek başına içe aktarılıp test edilebilir.

## Yeni soru şablonu eklemek

İlgili ünite dosyasına (`pytest_pro/questions/units/uNN_*.py`) bir fonksiyon ekleyin:

```python
@q("Liste Uzunluğu", verify="output")
def list_len():
    nums = random.sample(range(1, 50), random.randint(3, 6))
    return output_question(
        f"liste = {nums}\nprint(len(liste))",      # öğrenciye gösterilen kod
        str(len(nums)),                              # doğru cevap = kodun gerçek çıktısı
        "len() listedeki eleman sayısını verir.",    # açıklama (HTML olabilir)
        wrongs=[str(len(nums) + 1), str(sum(nums))], # verilirse çoktan seçmeli, verilmezse kısa cevap
    )
```

Kurallar:

- Fonksiyon her çağrıldığında **farklı değerlerle** soru üretmeli (`random` kullanın).
- `verify` değeri testlerin cevap anahtarını nasıl doğrulayacağını söyler:
  - `"output"`: kod çalıştırılır, çıktı cevapla birebir aynı olmalı.
  - `"error"`: kod çalıştırılır, hata vermeli ve hatanın adı cevapta geçmeli.
  - `"raises_one"`: seçenekler birer ifadedir, yalnızca doğru seçenek hata vermeli.
  - `"identifier"`: seçenekler değişken adıdır, yalnızca doğru seçenek geçerli olmalı.
  - `None`: otomatik doğrulama yok (doğru/yanlış ve kod yazma soruları).
- Mümkünse `verify` kullanın. Testler her şablonu 120 farklı tohumla üretip doğrular; yanlış
  cevap anahtarı olan bir şablon test aşamasında yakalanır.
- Çoktan seçmeli sorularda 4 farklı seçenek olmalı. `unique_options` yetersiz yanlışları
  otomatik tamamlar, yine de anlamlı çeldiriciler (öğrencilerin sık yaptığı hatalar) yazın.
- Kod `input()` kullanıyorsa klavye girdisini `stdin=` ile verin.
- Soru metni ve açıklama HTML'dir; içine değer gömerken `e()` ile kaçışlayın.

### İpucu ve yanlış şık açıklamaları

Her şablon bir **ipucu** taşır. Her yanlış şık, öğrencinin neden onu seçmiş olabileceğini açıklayan
bir `Wrong` olarak yazılır. Bu içerik pratikte "İpucu" düğmesinde, pratikte ve sınav sonucunda
"Neden yanlış" notunda, öğretmen panelinde de "en sık yanlış" satırında kullanılır.

```python
from ..helpers import Wrong, output_question

return output_question(
    code, answer, solution,
    wrongs=[Wrong(str(n1 + n2), "Sayı gibi topladın; ama ikisi de tırnak içinde, yani metin..."),
            Wrong(err("TypeError"), "İki metni + ile birleştirmek hata vermez...")],
    hint="a ile b tırnak içinde mi? Öyleyse + ne yapar?",
)
```

- **Kısa cevaplı sorular:** Sık yapılan yanlışlar `common_wrongs=[Wrong(...)]` ile verilir.
  Öğrencinin cevabı puanlamadaki gibi normalleştirilerek eşleştirilir (boşluk, `3,5` = `3.5`).
- **Elle kurulan seçenekli sorular:** Örneğin `type_func`. Bu sorularda `whys` sözlüğü
  `whys_for_options(doğru, yanlışlar, seçenekler)` ile üretilir.
- **Doğru/yanlış soruları:** Yalnızca `hint=` alır.
- **Yedek çeldiriciler:** Seçenekler 4'ten az kalırsa eklenen yedek çeldiricilere genel bir açıklama
  kendiliğinden verilir.
- **Ses:** İkinci tekil şahıs. Öğrencinin düşüncesini adlandırın ("... diye düşünmüş olabilirsin"),
  suçlamayın, en fazla iki cümle yazın.
- **İpucu:** Nereye bakılacağını söyler, sonucu söylemez. Bunu bir test denetler: 3 karakterden uzun
  cevaplar ipucunda geçmemeli.
- **Kapsam:** İçeriği tamamlanmış üniteler `questions/__init__.py` içindeki `CONTENT_UNITS` listesindedir.
  `tests/test_content.py::test_content_complete` bu ünitelerde ipucu ve açıklama eksiğine izin vermez.
  Bir ünitenin içeriğini bitirince listeye ekleyin.

### Kod izi

Kod izi, `trace` alanından otomatik çıkarılır; şablon yazarı bir şey yapmaz:
- `verify="output"` veya `"error"` olan sorularda sorunun kendi kodu izlenir.
- Kod yazma sorularında örnek çözüm izlenir.

`tests/test_tracer.py`, izin son çıktısının cevap anahtarıyla aynı olduğunu her şablon için doğrular.
İzlenen kodda yalnızca `math` modülü içe aktarılabilir; `open`, `eval` gibi işlemler kapalıdır.

Ekledikten sonra:

```bash
python -m pytest
python -m pytest_pro.questions.catalog > docs/MUFREDAT.md
```

## Yeni ünite eklemek

1. `pytest_pro/questions/units/u12_dosyalar.py` gibi bir dosya oluşturun:

   ```python
   import random
   from ..helpers import output_question
   from ..registry import register_unit

   UNIT = register_unit(
       "dosyalar", "Dosya İşlemleri", "İleri",
       "open(), read/write, with bloğu, satır satır okuma.",
       order=12,
   )
   q = UNIT.question

   @q("Dosya Modları")
   def file_modes():
       ...
   ```

2. `pytest_pro/questions/units/__init__.py` içindeki listeye ekleyin.
3. Testleri çalıştırıp `docs/MUFREDAT.md` dosyasını yeniden üretin.

Ünite öğretmen panelinde ve pratik modunda kendiliğinden görünür. Veritabanı değişikliği
gerekmez; sorular sınav anında üretilip sınav kaydıyla birlikte saklanır.

## Yeni kod yazma denetleyicisi eklemek

Öğrenci kodu **asla çalıştırılmaz** (okul ağında güvenlik riski). Kod, Python'un `ast` modülüyle
yapısal olarak incelenir. `pytest_pro/questions/codecheck.py` dosyasına:

```python
@checker("sum_list")
def check_sum_list(tree, p):
    ...
    return True, "Kod tüm kriterleri sağlıyor."   # veya (False, "neden yanlış olduğu")
```

Soru şablonunda `"check": {"kind": "sum_list", ...parametreler}` kullanın. Doğru kabul edilmesi
gereken farklı yazımları ve reddedilmesi gerekenleri `tests/test_codecheck.py` dosyasına ekleyin.
Örnek çözüm (`answer`) testlerde hem denetleyiciden geçirilir hem de gerçekten çalıştırılır.

## Veritabanı şemasını değiştirmek

`pytest_pro/db.py` içindeki `MIGRATIONS` listesinin **sonuna** yeni bir fonksiyon ekleyin.
Var olan göçleri asla değiştirmeyin: öğretmenlerin bilgisayarındaki veritabanları bu sırayla
güncellenir. Şema sürümü `PRAGMA user_version` ile izlenir.

## Ayar eklemek

`pytest_pro/settings.py`: `default_settings` içine varsayılanı, `validate` içine doğrulamayı
ekleyin. Öğretmen panelinde göstermek için `templates/teacher.html` ve `static/js/teacher.js`.

## Kod kuralları

- Kullanıcıya görünen metinler Türkçe; kod adları İngilizce veya Türkçe olabilir ama dosya içinde tutarlı olmalı.
- Sayfalarda satır içi `<script>`, `onclick` veya `style="..."` kullanılmaz (Content-Security-Policy engeller).
  Stil için sınıf, olay için `addEventListener` kullanın.
- Kullanıcıdan gelen her metin `esc()` ile kaçışlanarak HTML'e konur.
- Öğrenciye giden sorularda cevap anahtarı bulunmaz (`public_question`).

## Yol haritası (öneriler)

- **Ünite 12 – Dosya İşlemleri:** `open`, `with`, okuma/yazma (çıktı soruları geçici dosyayla doğrulanabilir).
- **Ünite 13 – Modüller ve Kütüphaneler:** `random`, `datetime`, kendi modülünü yazma.
- **Algoritmalar:** arama, sıralama, sayaç/biriktirici kalıpları; iz sürme (trace table) soruları.
- **Yeni soru tipi – kod tamamlama:** boşluk doldurma (`for i in ____(5):`).
- **Yeni denetleyiciler:** listedeki çift sayıları yazdırma, sözlükte sayma, sınıf tanımlama.
- **Zorluk seviyesi:** şablonlara zorluk etiketi ve sınavda zorluk dağılımı seçimi.
- **Öğrenci geçmişi:** aynı öğrencinin sınavlar boyunca konu bazında gelişimi.
- **Soru havuzu dışa aktarma:** basılı sınav için PDF/Word çıktısı.
