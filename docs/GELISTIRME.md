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
    codecheck.py             Kod yazma denetleyicileri (AST) ve ortak AST yardımcıları
    fill.py                  Boşluk doldurma: boşluk yerleştirme, cevap okuma, puanlama
    short.py                 Kısa cevap karşılaştırma biçimleri (norm, accept)
    mufredat.py              Müfredat haritası üretici (docs/MUFREDAT.md)
    tracer.py                Adım adım kod izleme motoru (yalnızca şablon kodu çalıştırır)
    units/uNN_*.py           Her ünite ayrı bir dosya
  templates/                 base.html + sayfa şablonları
  static/css, static/js      common.js ortak yardımcılar; sayfa başına bir betik
tests/                       pytest testleri (helpers.py: ortak yardımcılar; test_unit_XX.py: üniteye özel)
docs/                        Belgeler
```

Katmanlar tek yönlü bağımlıdır: `routes` → `exams` / `settings` → `questions`. Soru bankası
Flask'a ve veritabanına bağlı değildir; tek başına içe aktarılıp test edilebilir.

## Yeni soru şablonu eklemek

İlgili ünite dosyasına (`pytest_pro/questions/units/uNN_*.py`) bir fonksiyon ekleyin:

```python
@q("Liste Uzunluğu", verify="output")
def list_len():
    """Kazanım: len() ile eleman sayısını bulur · Bloom: U"""
    nums = random.sample(range(1, 50), random.randint(3, 6))
    return output_question(
        f"liste = {nums}\nprint(len(liste))",      # öğrenciye gösterilen kod
        str(len(nums)),                              # doğru cevap = kodun gerçek çıktısı
        "len() listedeki eleman sayısını verir.",    # açıklama (HTML olabilir)
        wrongs=[Wrong(str(len(nums) + 1), "..."), Wrong(str(sum(nums)), "...")],  # verilirse ÇS, verilmezse kısa cevap
        hint="len() neyi sayar?",
    )
```

Kurallar:

- Fonksiyon her çağrıldığında **farklı değerlerle** soru üretmeli (`random` kullanın).
- **Şablon kimliği** `ünite.fonksiyon_adı`dır (`listeler.list_len`) ve eski sınav kayıtlarında saklanır. Var olan
  bir şablonu düzeltirken fonksiyon adını ve konu adını değiştirmeyin.
- `verify` değeri testlerin cevap anahtarını nasıl doğrulayacağını söyler (testler her şablonu 120 tohumla
  üretip gerçekten Python çalıştırarak doğrular; yalnızca **öğretmenin** kodu çalıştırılır):

| verify | Ne doğrulanır | Yardımcı |
|---|---|---|
| `"output"` | Kodun çıktısı cevapla birebir aynı | `output_question` |
| `"error"` | Kod hata verir, hatanın adı cevapta geçer | `output_question(..., err("TypeError"))` |
| `"outcome"` | Hata yoksa çıktı, varsa `Hata verir (Tür)` cevapla aynı. Aynı şablon hatalı ve hatasız değişkeler üretebilir | `output_question` |
| `"tf_output"` | Hesaplanan D/Y: iddia gerçek sonuca eşitse cevap True | `tf_claim` |
| `"code_one"` | Seçenekleri kod olan ÇS: yalnızca doğru seçenek her durumda beklenen sonucu verir | `code_options_question` |
| `"fill"` | Boşluk doldurma: her kabul edilen cevap (ve takım) koda konup çalıştırılır; açıklamalı yanlışlar farklı sonuç vermeli | `fill_question` |
| `"raises_one"` | Seçenekler ifadedir; yalnızca doğru seçenek hata verir | elle |
| `"identifier"` | Seçenekler ad; yalnızca doğru seçenek geçerli ad | elle |
| `None` | Otomatik doğrulama yok (sabit havuzlu D/Y, kod yazma) | `tf_question` |

- Çoktan seçmelide 4 farklı şık olmalı; her yanlış bir yanılgıyı adlandıran `Wrong(değer, neden)` olmalı.
  `unique_options` yanlışlar yetmezse genel açıklamalı **dolgu şık** ekler; bu bir kusur sayılır ve
  `tests/test_quality.py` dolgu şık oranının %5'i geçmesine izin vermez. Çakışan hesaplanmış yanlışları
  üretimde engelleyin (a ≠ b, n ≥ 4 vb.) ya da 4-5 yanlışlık bir havuz verin: ilk üç farklı olan kullanılır.
- Kod `input()` kullanıyorsa klavye girdisini `stdin=` ile verin, `input()`'a istem metni yazmayın.
- Soru metni ve açıklama HTML'dir; içine değer gömerken `e()` ile kaçışlayın.
- **Türkçe:** Kök, açıklama, ipucu ve ekrana yazılan metinler doğru Türkçe karakterle yazılır ("Geçersiz",
  "Çift", "Başarılı"). Python tanımlayıcıları (değişken, fonksiyon, sınıf adları) ASCII kalır (`ogrenci_no`,
  `Kopek`). Sayıdan sonra ek gerekiyorsa ("5'ten", "6'ya") ek yerine "0 ile 4 arasında" gibi eksiz yazımı seçin.
- Docstring'e kazanım ve Bloom düzeyini yazın: `"""Kazanım: ... · Bloom: An"""`.

### Kalite testleri ve çeşitlilik (her şablona kendiliğinden uygulanır)

| Test | Eşik | Dosya |
|---|---|---|
| Farklı soru sayısı (500 üretim) | en az 12; **yeni şablonlarda hedef 30** | `test_content.py::test_template_variety` |
| Dolgu şıklı soru oranı | en fazla %5 | `test_quality.py` |
| En sık doğru cevap | en fazla %40 (D/Y'de iddia + cevap birlikte sayılır) | `test_quality.py` |
| Hep yanlış olan "Hata verir" şıkkı | soruların en fazla %60'ında (hata cevabı en az %15 doğruysa serbest) | `test_quality.py` |
| İpucu, açıklama | her şablonda ipucu; her yanlış şıkta açıklama; ipucu cevabı içermez | `test_content.py` |

İkili cevap (True/False, iki metinden biri) veren bir ÇS yazmayın: iki ifadeyi birlikte yazdırın (dört birleşim
anlamlı şık olur) ya da `tf_claim` kullanın. Kaçınılmaz bir istisna gerekiyorsa ortak dosyayı değil
**şablonu** işaretleyin; gerekçe zorunludur ve bankanın en fazla %5'i istisna taşıyabilir:

```python
@q("def ve return (Boşluk Doldurma)", verify="fill",
   exempt={"top_answer": "Ölçülen şey anahtar sözcüklerin yeri; cevap doğası gereği sabit."})
```

Geçerli adlar `registry.QUALITY_CHECKS`: `"filler"`, `"top_answer"`, `"error_giveaway"`.

### Hesaplanan doğru/yanlış (`tf_claim`, `verify="tf_output"`)

```python
from ..helpers import Wrong, tf_claim

@q("Operatör İddiası", verify="tf_output")
def op_claim():
    a, b = random.randint(11, 60), random.randint(2, 9)
    return tf_claim(
        f"print({a} // {b})",                      # öğrenciye gösterilen kod
        str(a // b),                               # gerçek sonuç (testte çalıştırılarak doğrulanır)
        [Wrong(str(a % b), "Bu % sonucu; // bölümün tam kısmını verir."),
         Wrong(str(a / b), "Bu / sonucu; // kesir kısmını atar.")],
        "// bölümün tam kısmını verir.",           # açıklama ("Kod çalıştırıldığında ..." kendiliğinden eklenir)
        hint="// ile % arasındaki fark nedir?",
    )
```

- Yarı olasılıkla gerçek sonuç, yarı olasılıkla yanlışlardan biri iddia edilir. Kök kendiliğinden kurulur:
  "Bu kod çalıştırıldığında ekrana `X` yazılır." Çok satırda "ekrana alt alta `A`, `B` yazılır", hata için
  `err("TypeError")` verilirse "`TypeError` hatası oluşur".
- Farklı kök için `text="Kod çalışınca ekranda {claim} görünür."` (`{claim}` yerine `<code>X</code>` konur).
- `true_why=`: iddia doğruyken "Yanlış" diyen öğrenciye gösterilecek açıklama (verilmezse genel bir cümle).
- Yanlış iddialardan biri gerçek sonuca eşit çıkarsa o iddia kendiliğinden atılır; hiç yanlış kalmazsa ValueError.

### Seçenekleri kod olan ÇS (`code_options_question`, `verify="code_one"`)

"Hangisi ekrana `Ali-Can` yazar?", "Hangi ifade 3'e bölünebilmeyi doğru denetler?", "Hangisi sonsuz döngüdür?"
gibi Analiz/Değerlendirme maddeleri için. Her seçenek gizli `harness` kalıbına konup her `cases` durumunda
çalıştırılır; **yalnızca** doğru seçenek her durumda `expect` sonucunu vermelidir.

```python
from ..helpers import LOOP_OUTCOME, Wrong, code_options_question

@q("Bölünebilme Koşulu", verify="code_one")
def divisible_expr():
    d = random.randint(2, 9)
    return code_options_question(
        f"Hangi ifade <code>sayi</code> değişkeninin {d} ile tam bölünüp bölünmediğini <strong>her sayı için</strong> "
        "doğru kontrol eder?",
        f"sayi % {d} == 0",
        [Wrong(f"sayi / {d} == 0", "Yalnızca sayi 0 iken True olur."),
         Wrong(f"sayi // {d} == 0", f"Yalnızca 0 ile {d - 1} arasındaki sayılar için True olur."),
         Wrong(f"sayi % {d} == 1", "Kalanın 1 olması bölünmediğini gösterir.")],
        cases=[{"setup": f"sayi = {v}", "expect": str(v % d == 0)} for v in range(-20, 21)],
        solution="Tam bölünen bir sayının kalanı 0'dır.",
        hint="Tam bölünen bir sayının kalanı kaçtır?",
        harness="print({option})",                 # ifade seçenekleri yazdırılarak karşılaştırılır
    )
```

- Tam kod seçenekleri için `harness` varsayılanı (`"{option}"`) yeterlidir; fonksiyon seçenekleri için
  `harness="{option}\nprint(mutlak(-5), mutlak(0), mutlak(7))"` gibi bir çağrı ekleyin.
- `expect`: sondaki satır sonu atılmış çıktı, `err("ZeroDivisionError")` ya da sonsuz döngü için `LOOP_OUTCOME`
  (testler adım sınırıyla çalıştırır).
- Durumlar seçenekleri **ayırt etmeye yetmeli**: tek bir `sayi = 0` durumu dört ifadeyi de doğru sayar ve test bunu
  yakalar. Sözdizimi hatalı seçenek `err("SyntaxError")` sonucu verir (yani hiçbir durumda geçmez).
- Öğrenciye yalnızca `text`, `code` (isteğe bağlı ortak kod) ve `options` gider.

### Boşluk doldurma soruları (`fill_question`, `verify="fill"`)

```python
@q("int(input()) Boşluğu", verify="fill")
def input_int_blank():
    n, k = random.randint(10, 99), random.randint(1, 9)
    return fill_question(
        f"yas = ____(input())\nprint(yas + {k})",
        [["int"]],                                  # her boşluk için kabul edilen cevaplar
        str(n + k),                                 # doldurulmuş kodun çıktısı (öğrenciye gönderilmez)
        f"Kullanıcı <strong>{n}</strong> yazıyor; kod ekrana <code>{n + k}</code> yazmalı. Boşluğu doldurun.",
        "input() metin döndürür; toplamak için int() ile sayıya çevrilir.",
        hint="input() hangi tipte değer döndürür?",
        wrongs=[[Wrong("str", "Metin + sayı TypeError verir."), Wrong("float", f"{n + k}.0 yazar.")]],
        stdin=str(n),
    )
```

- Koddaki her `____` (dört alt çizgi) bir boşluktur; cevap listesi her boşluk için **kabul edilen cevapların
  listesidir** (`["12", "13", "14"]`). Eşdeğer biçimleri ekleyin; testler her birini koda yerleştirip çalıştırır.
- Karşılaştırma: tırnak dışındaki boşluk farkı ve `'`/`"` farkı önemsenmez; Python ifadesi olarak okunabilen
  cevaplar sözdizimi ağacıyla karşılaştırılır (`b, a` = `(b, a)`; `range(1,6)` = `range(1, 6)`). Operatör ve
  anahtar sözcükler (`>=`, `elif`) metin olarak karşılaştırılır; büyük/küçük harf korunur.
- `wrongs=`: boşluk başına yaygın yanlışlar (`[[Wrong(...)], []]`). Öğrenci bunu yazarsa açıklama gösterilir
  ("2. boşluk: ..."). Testler her açıklamalı yanlışın **farklı sonuç** verdiğini doğrular; kabul edilen bir cevapla
  aynı olan açıklama kendiliğinden atılır.
- `answer_sets=`: birbirine bağlı boşluklar için tam takımlar; bu durumda `answer` yerine `None` yazılır:
  `fill_question("if yas ____ ____:\n    ...", None, ..., answer_sets=[[">=", "18"], [">", "17"]])`.
  Puanlama takımlara göredir (`>=` ile `17` yanlıştır); her takım ayrı çalıştırılarak doğrulanır.
- `stdin=`: kod `input()` kullanıyorsa klavye girdisi.
- Soru metninde beklenen sonucu açıkça yazın ki boşlukların tek bir anlamı olsun. Öğrenci kodu hiçbir zaman
  çalıştırılmaz; puanlama yalnızca metin/ağaç karşılaştırmasıdır.

### Kısa cevap: `accept` ve `norm`

`output_question(..., common_wrongs=[...], accept=[...], norm="...")` (wrongs verilmeden):

| norm | Karşılaştırma | Kullanım |
|---|---|---|
| verilmez | Eski davranış: boşluklar silinir, virgül nokta olur | mevcut sayısal sorular |
| `"sayi"` | Boşluk ve dış tırnak atılır, `,`→`.`, `−`→`-`; **5 ≠ 5.0** | tip ölçen sorular |
| `"sayi_degeri"` | Sayısal değer: 5 = 5.0 = 5,0 = +5 | tip ölçmeyen sorular |
| `"metin"` | Dış boşluk ve bir çift dış tırnak atılır, aradaki boşluklar teke iner; harf ve Türkçe karakter korunur | "Merhaba Ali" |
| `"metin_esnek"` | `metin` + büyük/küçük harf ve Türkçe karakter farkı yok (Çift = cift = CIFT) | tek sözcük cevaplar |
| `"python"` | `ast.literal_eval` değeri ve tipi: `['a', 1]` = `["a",1]`; 5 ≠ 5.0, True ≠ 1 | liste, demet, bool |

`accept=["Merhaba, Ali"]` doğru cevaba ek olarak kabul edilen eşdeğerlerdir (aynı `norm` ile karşılaştırılır).
`common_wrongs` aynı biçimle eşleştirilir; doğru sayılan bir cevaba verilmiş yanlış açıklaması kendiliğinden atılır.

### İpucu ve yanlış şık açıklamaları

Her şablon bir **ipucu** taşır. Her yanlış şık, öğrencinin neden onu seçmiş olabileceğini açıklayan
bir `Wrong` olarak yazılır. Bu içerik pratikte "İpucu" düğmesinde, pratikte ve sınav sonucunda
"Neden yanlış" notunda, öğretmen panelinde de "en sık yanlış" satırında kullanılır.

- **Elle kurulan seçenekli sorular:** `whys` sözlüğü `whys_for_options(doğru, yanlışlar, seçenekler)` ile üretilir.
- **Sabit havuzlu D/Y:** `tf_question` her iki taraf için `(ifade, açıklama)` çiftleri alır; her tarafta en az
  10 ifade yazın. Mümkünse `tf_claim` tercih edin.
- **Ses:** İkinci tekil şahıs. Öğrencinin düşüncesini adlandırın, suçlamayın, en fazla iki cümle yazın.
- **İpucu:** Nereye bakılacağını söyler, sonucu söylemez (3 karakterden uzun cevaplar ipucunda geçmemeli).

### Kod izi

Kod izi `trace` alanından otomatik çıkarılır: `output`, `error`, `outcome`, `tf_output` sorularında sorunun
kodu; kod yazmada örnek çözüm; boşluk doldurmada cevap anahtarı yerleştirilmiş kod. `code_one` sorularında
iz yoktur. `tests/test_tracer.py` izin son çıktısının cevap anahtarıyla aynı olduğunu doğrular. İzlenen kodda
yalnızca `math` içe aktarılabilir.

Ekledikten sonra:

```bash
python -m pytest -q
python -m pytest_pro.questions.mufredat > docs/MUFREDAT.md
```

(Müfredat modülünün adı `catalog` değildir: öyle olsaydı içe aktarılınca `questions.catalog()` fonksiyonunun
üstüne yazılırdı.)

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
   ```

2. `pytest_pro/questions/units/__init__.py` içindeki listeye ekleyin.
3. Testleri çalıştırıp `docs/MUFREDAT.md` dosyasını yeniden üretin.

## Yeni kod yazma denetleyicisi eklemek

Öğrenci kodu **asla çalıştırılmaz** (okul ağında güvenlik riski). Kod `ast.parse` ile ağaca çevrilir ve
incelenir. `codecheck.safe_eval` yalnızca sayı/metin sabitleri, dört işlem, karşılaştırma ve birkaç saf
fonksiyondan (int, float, str, abs, round, min, max, pow, len, bool; yazılı bir liste/demet üzerinde
`sum([a, b, c])`, `min((a, b))`, `max([a, b])`) oluşan **ifadeleri** sınırlı büyüklükte kendi kodumuzla
hesaplar; döngü, fonksiyon çağrısı, modül hesaplanmaz.

Kalıba dayalı denetleyiciler, kalıba uymayan ama doğru çalışan çözümleri haksız reddedebilir. Bunun için
u05'teki sınırlı izleyici (`Sim`, `sim_run`) ile **davranış yedeği** kurulabilir: değişkene birkaç deneme
değeri konup çıktı karşılaştırılır (örnek: `u04_metinler._behaves`). İzleyici de öğrenci kodunu çalıştırmaz;
desteklemediği yapıda `Unknown` verir ve yedek yol yalnızca ek kabul için kullanılır.

Denetleyici, ünitenin kendi dosyasında tanımlanabilir (ünite yüklenince kaydolur; aynı tür iki kez
kaydedilirse ValueError). Soru şablonunda `"check": {"kind": "<tür>", ...parametreler}` kullanılır.

```python
from ..codecheck import OK, Tracker, checker, computes, find_prints, print_values, same_value

@checker("rect_area")
def check_rect_area(tree, p):
    """en ve boy atanır; önce alan, sonra çevre yazdırılır."""
    en, boy = p["en_ad"], p["boy_ad"]
    tr = Tracker(keep={en, boy})          # en/boy sembolik kalır: alan = en * boy diye görülür
    printed = []
    for stmt in tr.run(tree.body):        # her satırdan ÖNCEKİ durumla
        for call in find_prints(stmt):
            for node in print_values(call):   # etiket metinleri atlanır, f-string ve str() açılır
                printed.append((tr.try_value(node), tr.inline(node)))
    if not (same_value(tr.values.get(en), p["en"]) and same_value(tr.values.get(boy), p["boy"])):
        return False, f"<code>{en}</code> ve <code>{boy}</code> değişkenlerine istenen değerler atanmamış."
    if len(printed) != 2:
        return False, "İki değer yazdırılmalı: önce alan, sonra çevre."
    wants = [(p["en"] * p["boy"], lambda a, b: a * b, "Alan"),
             (2 * (p["en"] + p["boy"]), lambda a, b: 2 * (a + b), "Çevre")]
    for (value, expr), (want, func, label) in zip(printed, wants):
        if not same_value(value, want):
            return False, f"{label} değeri beklenen sonucu vermiyor; formülü kontrol et."
        if not computes(expr, [en, boy], func):     # sabit yazılmış cevabı yakalar
            return False, f"{label} değerini elle yazma; <code>{en}</code> ve <code>{boy}</code> ile hesapla."
    return True, OK
```

Bu denetleyici `print(en * boy)`, `print("Alan:", en * boy)`, `print(f"Çevre: {2 * en + 2 * boy}")` ve ara
değişkenli (`alan = en * boy`) çözümleri kabul eder; `print(28)` ve `print(en + boy * 2)` çözümlerini reddeder.

Ortak yardımcılar (hepsi `pytest_pro.questions.codecheck` içinde, belgelenmiş):

| Yardımcı | Ne yapar |
|---|---|
| `safe_eval(düğüm, env)` / `const_value(düğüm, env, default)` | İfadeyi hesaplar; hesaplayamazsa `Unknown` (ya da default) |
| `same_value(a, b)` | Sayıları küçük farkla karşılaştırır (9.0 == 9) |
| `find_prints(düğüm)`, `is_print(düğüm)` | print çağrıları |
| `print_values(call)`, `print_texts(call)`, `print_parts(call)` | print'in yazdırdığı ifadeler / etiketler (f-string, `"a" + str(x)` açılır) |
| `print_keyword(call, "end")` | sep/end değeri (varsayılanlar dahil) |
| `Tracker(values, keep)` | Düz koddaki atamaları sırayla izler: `values`, `value()`, `try_value()`, `inline()`; `run(body)` her satırdan önceki durumu verir |
| `assignments(satır)`, `assigned_names(düğüm)`, `uses_name(düğüm, ad)` | Atamalar, atanan adlar, ad kullanımı |
| `inline(düğüm, defs)` | Ara değişkenleri tanımlarıyla değiştirir |
| `computes(düğüm, adlar, func)`, `is_product_of`, `is_sum_of` | İfade bu değişkenlerin şu fonksiyonu mu? (adlara farklı sayılar konarak) |
| `loop_problems(döngü)` | break/continue/return ya da döngü değişkenine atama varsa öğrenciye gidecek not |
| `find_loops(düğüm)`, `range_values(call, env)` | Döngüler; `range(1, n + 1)` gibi çağrının üreteceği sayılar (en fazla 1000) |
| `find_function(ağaç, ad)`, `function_params(def)`, `function_returns(def)`, `is_called(ağaç, ad)` | Fonksiyon tanımı, parametreler, return satırları, çağrılıyor mu |
| `OK`, `UNREADABLE` | Kabul notu; "otomatik değerlendiremedim, öğretmenine göster" notu |

Denetleyiciden `Unknown` kaçarsa `check_code` bunu yakalar ve öğrenciye `UNREADABLE` notu gider (0 puan, ama
suçlamayan bir mesajla). Ret mesajları neyin eksik olduğunu söyler, çözümü vermez ve öğrenciyi suçlamaz.

**Test:** Her denetleyici için en az **6 kabul** (ara değişken, etiketli print, f-string, `int(7)`, takma ad,
gereksiz ama zararsız satır...) ve **6 ret** (sabit cevap, break/continue, döngü değişkenine atama, fazladan
print, print/return karışıklığı, sınır hatası...) yazın. Örnek çözüm (`answer`) testlerde hem denetleyiciden
geçirilir hem de çalıştırılır.

## Testleri düzenleme (paralel çalışma)

- Ortak testler (`test_questions`, `test_content`, `test_quality`, `test_tracer`) **her şablona kendiliğinden**
  uygulanır; yeni şablon için bu dosyalara dokunmayın.
- Üniteye özel testler ayrı dosyaya yazılır: `tests/test_unit_01.py`, `tests/test_unit_06.py`... Ortak
  yardımcılar `tests/helpers.py` içindedir:

```python
"""Ünite 3 (Operatörler) özel testleri."""
import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples, top_answer_share

DIVMOD = code_q("write_divmod", var="toplam", value=135)

@pytest.mark.parametrize("src", ["toplam = 135\nprint(toplam // 60, toplam % 60)", ...])  # en az 6
def test_write_divmod_accepts(src):
    assert accepts(DIVMOD, src)

@pytest.mark.parametrize("src, reason", [("toplam = 135\nprint(2, 15)", "hesapla"), ...])  # en az 6
def test_write_divmod_rejects(src, reason):
    assert rejects(DIVMOD, src, reason)

def test_missing_op_has_single_answer():
    for q in samples(gen_by_name("operatorler.missing_op_blank"), 50):
        ...
```

| Yardımcı | Ne yapar |
|---|---|
| `run(kod, stdin)`, `outcome(kod, stdin)` | Öğretmen kodunu çalıştırır; `outcome` hata adını ve sonsuz döngüyü (`LOOP_OUTCOME`) da sonuç olarak verir |
| `gens(ünite)`, `gen_by_name("ünite.şablon")`, `samples(gen, n)` | Şablon seçme ve tohumlu üretim |
| `code_q(tür, **parametreler)`, `accepts(q, kod)`, `rejects(q, kod, neden)` | Denetleyici testleri (kod çalıştırılmaz) |
| `passing_options(q)` | `code_one` sorusunda her durumda doğru sonucu veren seçenekler |
| `filler_rate`, `top_answer_share`, `variety` | Kalite ölçüleri |

- Paralel çalışırken çakışmayı önlemek için yalnızca kendi ünite dosyanızı, kendi `tests/test_unit_XX.py`
  dosyanızı ve (gerekiyorsa) ünite dosyanızdaki denetleyicileri değiştirin. `docs/MUFREDAT.md` üretilmiş bir
  dosyadır: birleştirmede çakışırsa elle düzeltmeyin, komutla yeniden üretin.


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
- **Boşluk doldurma:** altyapı ve ilk şablonlar hazır (Ünite 1, 6, 9); diğer ünitelere şablon eklenebilir.
- **Yeni denetleyiciler:** listedeki çift sayıları yazdırma, sözlükte sayma, sınıf tanımlama.
- **Zorluk seviyesi:** şablonlara zorluk etiketi ve sınavda zorluk dağılımı seçimi.
- **Öğrenci geçmişi:** aynı öğrencinin sınavlar boyunca konu bazında gelişimi.
- **Soru havuzu dışa aktarma:** basılı sınav için PDF/Word çıktısı.
