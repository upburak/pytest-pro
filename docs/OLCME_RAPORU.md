# PyTest Pro Soru Bankası: Ölçme ve Değerlendirme Raporu

Tarih: 25.11.2026 · Kapsam: `pytest_pro/questions/` (11 ünite, 75 şablon), `codecheck.py`, `helpers.py`, kısa cevap puanlaması (`questions/__init__.py`).

Yöntem: Her şablonun kodu satır satır okundu. Her şablon 500 tohumla üretildi; çeşitlilik, cevap dağılımı ve "yedek çeldirici" (genel açıklamalı dolgu şık) oranı ölçüldü. Kod yazma denetleyicileri 28 farklı öğrenci cevabıyla denendi. Önerilerdeki örnek çıktıların hepsi Python'da çalıştırılarak doğrulandı. Mevcut testler (`test_questions`, `test_content`, `test_codecheck`) geçiyor: 362 test.

Kısaltmalar: **ÇS** çoktan seçmeli, **D/Y** doğru-yanlış, **BD** boşluk doldurma, **KC** kısa cevap, **KY** kod yazma (açık uçlu). Bloom düzeyleri: **H** Hatırlama, **A** Anlama, **U** Uygulama (kod izleme, hesaplama), **An** Analiz (hata bulma, karşılaştırma, kodun amacını çıkarma), **D** Değerlendirme (çözümleri kıyaslama), **O** Oluşturma (kod yazma).

---

## 1. Mevcut bankanın denetimi

Bulgular önem sırasına göre dizildi. Satır numaraları şablon fonksiyonunun `def` satırıdır (dosya yolu `pytest_pro/questions/` altındadır).

### 1.1 Kritik: puanlamayı doğrudan bozan sorunlar

**K1. `range_print` denetleyicisi yanlış kodları DOĞRU sayıyor.** `codecheck.py:112-147` (özellikle `:143`). Denetleyici döngü gövdesinde uygun bir `print(i)` bulduğu anda kabul ediyor; gövdedeki diğer satırlara bakmıyor. Denenip **kabul edilen** yanlış cevaplar:

| Öğrenci kodu (hedef: 1'den 5'e kadar alt alta) | Gerçek çıktı | Sonuç |
|---|---|---|
| `for i in range(1, 6):` / `print(i)` / `break` | `1` | Kabul (haksız) |
| `for i in range(1, 6):` / `if i == 3: continue` / `print(i)` | `1 2 4 5` | Kabul (haksız) |
| `for i in range(1, 6):` / `i = 99` / `print(i)` | `99` beş kez | Kabul (haksız) |
| `for i in range(1, 6):` / `print(i)` / `print(i)` | her sayı iki kez | Kabul (haksız) |

Düzeltme: Döngü gövdesinde `print` dışında `Break`, `Continue`, döngü değişkenine atama veya ikinci bir `print` varsa reddedin ("Döngü içinde fazladan komut var; her sayı bir kez yazılmalı"). Kalıcı çözüm için 1.4'teki "güvenli yorumlayıcı" önerisine bakın.

**K2. Kod yazma denetleyicileri doğru ve yaygın çözümleri REDDEDİYOR.** Lise öğrencisinin en doğal yazımları cezalandırılıyor:

| Denetleyici | Reddedilen doğru cevap | Neden reddediliyor | Öneri |
|---|---|---|---|
| `mult` (`codecheck.py:75`) | `print("Sonuç:", a * b)` | Yalnızca `print`'in **ilk** argümanına bakılıyor (`:97`) | Tüm argümanlarda çarpımı arayın; ek metin argümanlarına izin verin |
| `mult` | `print(f"{a * b}")` | f-string içi incelenmiyor | `JoinedStr` içindeki `FormattedValue`'ları da tarayın |
| `mult` | `a = int(7)` | Yalnızca sabit atama tanınıyor | `int(sabit)`/`float(sabit)` çağrısını sabit sayın |
| `range_print` (`:112`) | `n = 5` / `for i in range(1, n + 1):` | Sabit olmayan `range` argümanı reddediliyor (`:124`, mesaj "sabit sayılarla kurulmalı") | Üst düzeydeki sabit atamaları izleyin, `n + 1` gibi basit ifadeleri hesaplayın |
| `range_print` | `for ...:` / `if i > 0:` / `print(i)` | Yalnızca gövdenin ilk düzeyi okunuyor | En azından koşulsuz bloklara izin verin; asıl çözüm yorumlayıcı |
| `range_print` | `print(str(i))` | `print(i)` ve `print(i + sabit)` dışındakiler tanınmıyor | `str(i)` ve `f"{i}"` biçimlerini ekleyin |
| `range_print` | `for` döngüsü bir `if`/fonksiyon içinde | Yalnızca `tree.body` aranıyor (`:115`) | `ast.walk` ile arayın |
| `square_func` (`:169`) | `return x ** 2.0` | `_int_const` yalnızca tam sayı kabul ediyor | `2.0`'ı da kabul edin |
| `square_func` | `y = x` / `return y * y` | Parametrenin takma adı izlenmiyor | `_assignments` ile takma adları izleyin |

Kapsam notu: Sözdizimi hatası, öğrencinin neredeyse doğru kodu için yine 0 puan demek. Öğretmen panelinde "otomatik reddedildi, elle bakılabilir" işareti olması önerilir.

**K3. `square_func`, parametrenin üstüne yazan kodu kabul ediyor.** `codecheck.py:182-196`: `def kare(x):` / `x = 3` / `return x * x` her zaman 9 döndürdüğü hâlde kabul ediliyor. Düzeltme: fonksiyon gövdesinde parametreye atama varsa reddedin.

**K4. Sekiz ÇS şablonu aslında iki seçenekli.** Doğru cevap yalnızca `True`/`False` (ya da iki metinden biri) olabiliyor; diğer iki şık ("None", ifadenin ilk sözcüğü, "True" yazısı gibi) bu yaşta bile kolayca eleniyor. Şans başarısı %25 değil, %50'ye yakın. Ölçülen cevap dağılımı (500 üretim):

| Şablon | Satır | Farklı cevap | Kolayca elenen şık(lar) |
|---|---|---|---|
| `operatorler.logic` | `u03_operatorler.py:83` | 2 | `None`, `not` ya da `7` gibi ifadenin ilk parçası (`:100`) |
| `metinler.in_operator` | `u04_metinler.py:168` | 2 | `None`, aranan metnin kendisi |
| `kosullar.compound_condition` | `u05_kosullar.py:81` | 2 | `True`, iki satırlı çıktı |
| `kosullar.even_odd` | `u05_kosullar.py:106` | 2 | kalan sayısı, iki satırlı çıktı |
| `veri_tipleri.bool_conversion` | `u02_veri_tipleri.py:99` | 2 (%61 `True`) | `Hata verir (ValueError)`, `None` |
| `hatalar.try_finally` | `u10_hatalar.py:88` | 2 (%64 `Hata\nSon`) | — (şıklar iyi, ama doğru cevap iki seçenekten biri) |
| `koleksiyonlar.dict_get` | `u08_koleksiyonlar.py:36` | 2 (`0` ya da `-1`) | — |
| `donguler.loop_string` | `u06_donguler.py:136` | 3 (%85 `1`) | "Hep 1 de" stratejisi %85 başarı sağlıyor |

Düzeltme: (a) Kodu iki ifade yazdıracak biçimde kurun; dört birleşim de anlamlı şık olur: `print(bool(0), bool("0"))` → `False True`. Şıklar `True True`, `True False`, `False True` ve `False False` olur. (b) Ya da bu şablonları D/Y'ye çevirin; ölçtükleri zaten ikili bir karar. (c) `loop_string` için harfi, sayısı ≥ 2 olan harflerden ağırlıklı seçin.

**K5. Dört şablonda doğru cevap HİÇ değişmiyor.** Öğrenci şablonu bir kez tanıyınca soruyu okumadan doğru cevaplıyor:

| Şablon | Satır | Sabit cevap |
|---|---|---|
| `veri_tipleri.str_plus_int` | `u02_veri_tipleri.py:179` | `Hata verir (TypeError)` (%100) |
| `listeler.list_index_error` | `u07_listeler.py:45` | `Hata verir (IndexError)` (%100) |
| `koleksiyonlar.tuple_immutable` | `u08_koleksiyonlar.py:90` | `Hata verir (TypeError)` (%100) |
| `koleksiyonlar.dict_update` | `u08_koleksiyonlar.py:56` | `4` (%100) |

Düzeltme: Üretimlerin %40-50'sinde hatasız bir değişke kullanın (ör. `"Yaşım " + str(yas)`, geçerli son indeks `[k-1]`, demeti listeye çevirip atama). `dict_update` için başlangıç boyutunu (2-5), güncellenen ve eklenen anahtar sayısını (0-2) rastgele seçin. `verify` türü değişkeye göre seçilemediği için hatalı ve hatasız değişkeler ayrı şablon olarak kaydedilmeli ya da `verify="output"` ile hata durumunu yakalayan bir test türü eklenmeli.

### 1.2 Yüksek: madde kalitesini düşüren sorunlar

**Y1. Anlamsız dolgu şıkları ("None", "[]", "Hata verir (TypeError)").** Yazılan yanlışlar yetmeyince `helpers.py:48` (`_fillers`) genel şıklar ekliyor ve bunlara "Bu, kodun gerçek çıktısı değil" gibi genel bir açıklama veriyor. Böyle şıklar hem ipucu veriyor hem de "neden yanlış" geri bildirimi öğretmiyor. Ölçülen oranlar:

| Şablon | Satır | Dolgu şık oranı | Kaynak |
|---|---|---|---|
| `metinler.slicing` | `u04_metinler.py:57` | **%100** (her soruda `None`) | Her değişkede yalnızca 2 yanlış yazılmış |
| `fonksiyonlar.default_param` | `u09_fonksiyonlar.py:33` | %26 | `base=2` iken `2*2 == 2**2` |
| `kosullar.separate_ifs` | `u05_kosullar.py:57` | %22 (`None`) | x 6-10 iken aday listesi tekrar ediyor |
| `donguler.nested` | `u06_donguler.py:109` | %21 | `a == b` ya da `a = b = 2` iken `a+b == a*b` |
| `fonksiyonlar.recursion` | `u09_fonksiyonlar.py:111` | %18 | n=3 iken `3! = 6 = 1+2+3` |
| `fonksiyonlar.call_return` | `u09_fonksiyonlar.py:18` | %15 | `a == b` iken iki yanlış aynı |
| `listeler.comprehension` | `u07_listeler.py:164` | %14 (`None`) | Hesaplanan yanlışlar çakışıyor |
| `donguler.break_continue` | `u06_donguler.py:77` | %13 (`None `) | `stop == n-1` iken "continue sandın" şıkkı doğru cevaba eşit |
| `listeler.sorting` | `u07_listeler.py:119` | %6 (`[]`, TypeError) | Liste zaten sıralı geldiğinde |

Düzeltme: (1) `slicing`'in her değişkesine üçüncü bir anlamlı yanlış ekleyin: `[a:b]` için `word[a:b-1]` ("bitişten bir önceki karakteri de dışarıda bıraktın"); `[:b]` için `word[:b-1]`; `[a:]` için `word[a-1:]` (a>0 iken); `[::-1]` için `word[1:]` ya da `word[::-1][1:]`. (2) Çakışan sayıları üretim aşamasında engelleyin: `nested`'da a≠b ve {a,b}≠{2}, `recursion`'da n≥4, `default_param`'da taban 3-6, `break_continue`'da `stop` için `randint(3, n-2)`, `sorting`'de sıralı ya da ters sıralı listeyi yeniden üretin. (3) Testlere kural ekleyin: **ÇS sorularında dolgu açıklaması (`FILLER_WHY_*`) taşıyan şık oranı %5'i geçmesin.**

**Y2. Doğru-yanlış şablonları ezberlenebilir.** Altı D/Y şablonunun her biri sabit 6 doğru ve 6 yanlış ifadeden birini seçiyor. Çeşitlilik tam 12, yani test sınırında (`u01:80`, `u03:125`, `u05:123`, `u09:176`, `u10:111`, `u11:101`). Bir sınıf birkaç pratik oturumunda havuzun tamamını görür. Düzeltme: (a) Havuzları en az 10 doğru ve 10 yanlış ifadeye çıkarın. (b) Daha önemlisi, **hesaplanan D/Y** türünü ekleyin: ifade rastgele bir kod ve onun hakkında bir iddiadan oluşur ("Bu kod ekrana `7` yazar"), iddianın doğruluğu kod çalıştırılarak belirlenir. Önerilen yardımcı ve test:

```python
def tf_claim(code, true_output, wrong_claims, solution, hint, stdin=None):
    """%50 olasılıkla gerçek çıktıyı, %50 olasılıkla Wrong(değer, neden) iddialarından birini sorar."""
# registry: verify="tf_output" -> test: (run(code) == iddia) == (answer == "True")
```

**Y3. Bilişsel düzey tek tip.** 75 şablonun 61'i (%81) "Bu kodun çıktısı nedir?" sorusu, yani Uygulama düzeyi. Analiz ve Değerlendirme düzeyinde (hatalı satırı bulma, iki çözümü karşılaştırma, istenen çıktıyı veren kodu seçme) hiç şablon yok. Oluşturma düzeyinde yalnızca 3 KY şablonu var ve üçü de tek satırlık işlem. Ayrıntı ve hedef dağılım 2. bölümde.

**Y4. `fstring_format` bazen elle yuvarlamayla çelişiyor.** `u04_metinler.py:193`. Değer 4 ondalıklı rastgele seçiliyor; kesilen basamak tam 5 olduğunda (ör. `17.165`, `98.35`) Python ikili kayan nokta yüzünden aşağı yuvarlıyor (`17.16`, `98.3`). Okulda öğretilen yuvarlamayı yapan öğrenci (`17.17`) kendi cevabını şıklarda bulamıyor. 5000 üretimde 13 kez oluyor (%0,26); seyrek ama doğru bilen öğrenciyi cezalandırıyor. Düzeltme: Kesilen basamağın 5 ve sonrasının 0 olduğu değerleri üretmeyin (`while` ile yeniden seçin).

**Y5. Yanlış "neden" açıklaması.** `u06_donguler.py:16` `range_list`: adım 1'den büyükken `near + [near[-1] + step]` şıkkının açıklaması "Bitiş değerini de dahil ettin" diyor. Oysa `range(0, 7, 3)` için eklenen 9, bitiş değeri olan 7 değil. Düzeltme: Bu şıkkı yalnızca `step == 1` iken kullanın; adım >1 iken "bitişi dahil etmek" yanılgısını `near + [b]` (b adımın katıysa) ile kurun, değilse başka bir yanılgı kullanın.

**Y6. `error_type` ezberlenebilir.** `u10_hatalar.py:39`. Kod parçaları sabit 11 örnek (`SNIPPETS`); çeşitlilik yalnızca şık sırasından geliyor. Düzeltme: Değişken adlarını, sayıları ve metinleri rastgeleleştirin. Örneğin `liste = [..k eleman..]; print(liste[k+r])` veya `d = {anahtar: değer}; print(d[başka_anahtar])`.

### 1.3 Orta: dil, belirsizlik ve seviye

**O1. Türkçe karakter tutarsızlığı.** Kod içindeki metinler bazen Türkçe karaktersiz yazılmış: `u01:63` "yasiniz", `u05:59` "Kucuk/Buyuk", `u05:108` "Cift", `u10:60,92` "Gecersiz/Basarili", `u04:113` "Merhaba Dunya", `u04:153` "Sinav", `helpers.py:6` "Gelisim", "Yazilim". Başka yerlerde ise doğru yazılmış ("Günaydın", "ğüşiöç", "İstanbul"). Python 3 UTF-8 metinleri sorunsuz işler; öğrenciye yanlış yazım örneği gösterilmemeli. Düzeltme: Ekrana yazılan metinlerde doğru Türkçe kullanın ("Çift", "Geçersiz", "Başarılı", "Gelişim", "Yazılım"). Değişken ve sınıf adlarında ASCII kalabilir (`ogrenci_no`, `Kopek`); bu bir kodlama geleneğidir, yönergede belirtilmeli (4. bölüm). Kısa cevap ve boşluk doldurmada öğrencinin yazacağı metinlerde iki yazımı da kabul edin.

**O2. Türkçe büyük harf tuzağı açıklanmıyor.** `u04_metinler.py:112` `methods`: `"python dersi".upper()` → `PYTHON DERSI` (noktalı İ değil). Doğru şık bu, ama Türk öğrenci `DERSİ` bekler ve çözümde bu durum açıklanmıyor. Düzeltme: Çözüme "Python `upper()` ile i harfini İ'ye değil I'ya çevirir" cümlesini ekleyin ya da bu durumu ayrı ve bilinçli bir madde yapın (3. bölümde Ö4.3).

**O3. Muğlak D/Y ifadesi.** `u10_hatalar.py:111` yanlış havuzunda: "SyntaxError (yazım hatası) try / except ile yakalanarak program çalıştırılabilir." `eval`/`exec`/`import` ile oluşan SyntaxError yakalanabildiği için ileri düzey bir öğrenci haklı olarak itiraz eder; "program çalıştırılabilir" ifadesi de belirsiz. Önerilen yazım: "Bir dosyadaki yazım hatası (SyntaxError), aynı dosyadaki bir try / except bloğuyla yakalanabilir." (Yanlış)

**O4. D/Y'de mutlak ifadeler ipucu veriyor.** Yanlış ifadelerin çoğu "her zaman", "yalnızca", "en fazla", "asla" içeriyor (ör. `u09:176` "her zaman değiştirir", "yalnızca bir kez"). Sınavda deneyimli öğrenci içeriği bilmeden de bu sözcüklerden ifadenin yanlış olduğunu tahmin eder. Mutlak sözcükler doğru ifadelerde de aynı sıklıkta kullanılmalı (ör. doğru: "`/` operatörü **her zaman** float döndürür").

**O5. Çok okunaksız değişken adı seçimi.** `u09_fonksiyonlar.py:93` `multi_return`: parametre adı `b` ile sonuç değişkeni `b` aynı (`k, b = kucuk_buyuk(a, b)`). Bu yanıltma kapsam (scope) konusunda kasıtlı değilse ölçmeye gürültü katar. Sonuç değişkenlerini `kucuk, buyuk` yapın.

**O6. Sınırda çeşitlilik.** 500 üretimde 12-16 farklı soru üreten şablonlar: `type_func` (15), `bool_conversion` (12), `str_repeat` (15), `length` (14), `methods` (15), `in_operator` (15), `default_param` (12), `recursion` (12), `input_concat` (16), `for_sum` (16), `comprehension` (16), `inheritance` (16) ve 6 D/Y şablonunun hepsi (12). Her birine en az bir rastgele eksen daha ekleyin (değişken adı, kelime listesi, sayı aralığı).

**O7. Kısa cevap normalleştirmesi gelecek sorular için riskli.** `questions/__init__.py:80` `_norm_short` bütün boşlukları siliyor ve virgülü noktaya çeviriyor. Şimdiki 8 KC şablonunun hepsi sayısal olduğundan bugün sorun yok. Ancak metin ya da liste cevaplı yeni KC'lerde: `"[1, 2]"` ile `"[1.2]"` aynı sayılır (haksız kabul); `"Merhaba Ali"` ile `"MerhabaAli"` aynı sayılır; `True` ile `true` farklı sayılır (haksız ret); `'a'` ile `"a"` farklı sayılır. Öneri: Soru başına `accept` (kabul edilen eşdeğerler listesi) ve `norm` modu (`"sayi"`, `"metin"`, `"python_deger"`) alanları ekleyin. `python_deger` modu `ast.literal_eval` ile karşılaştırır: `['a', 1]` ile `["a",1]` eşit olur. Unicode eksi işareti (−) ve baştaki/sondaki tırnaklar da normalleştirilmeli.

**O8. Hata sorularında "Hata verir (X)" şıkkı her zaman yer alıyor.** Örnek: `metinler.methods` her soruda `Hata verir (AttributeError)` içeriyor ve hiçbir zaman doğru değil. Öğrenciler bu tür hata şıklarının bu şablonlarda hep yanlış olduğunu öğrenir. Hata şıkkını yalnızca gerçekten hata bekleyen bir yanılgıya karşılık geliyorsa kullanın ve bankada hata şıkkının doğru cevap olduğu maddelerin oranını %20-25 civarında dengeleyin.

### 1.4 Kod yazma denetimi: genel değerlendirme ve altyapı önerisi

Mevcut tasarım öğrenci kodunu hiç çalıştırmıyor; denetim yalnızca AST desen eşlemesiyle yapılıyor (`codecheck.py` başlığı). Bu güvenli, ama iki yönde de hata üretiyor (K1-K3). Desen eşleme, öğrencinin yazabileceği doğru çözümlerin çeşitliliğine yetişemez. Döngü, koşul veya fonksiyon içeren her yeni KY sorusu için yeni ve kırılgan bir denetleyici yazmak gerekir.

**Öneri: kısıtlı "güvenli yorumlayıcı" ile çıktı karşılaştırması (`kind: "cases"`).** Bu bir sahip kararıdır; uygulamadan önce onay gerekir.

1. **AST beyaz listesi:** Yalnızca şu düğümler kabul edilir: `Module, Expr, Assign, AugAssign, AnnAssign, Name, Constant, BinOp, UnaryOp, BoolOp, Compare, If, IfExp, For, While, Break, Continue, Pass, List, Tuple, Dict, Set, Subscript, Slice, Call, FunctionDef, Return, ClassDef, Attribute, JoinedStr, FormattedValue, ListComp, comprehension, Try, ExceptHandler, Global`. `Import` yalnızca `math`/`random` için geçerlidir. Alt çizgiyle başlayan nitelik adları yasaktır; tek istisna `__init__` ve `__str__` tanımıdır. `open, eval, exec, compile, __import__, globals, getattr, setattr, type(...)` 3 argümanlı çağrı yasaktır.
2. **Yürütme:** Tercihen saf Python ile yazılmış bir ağaç yorumlayıcısı kullanılmalı. `tracer.py`'deki `settrace` adım sınırı (`MAX_STEPS`) ve çıktı sınırı (`MAX_OUTPUT`) burada da uygulanır. Daha az işçilik isteyen alternatif: beyaz listeden geçen kodu kısıtlı `__builtins__` ile `exec` etmek. Bu yol daha hızlı uygulanır ama güvenlik kararını değiştirir.
3. **Test durumları:** Soru `check = {"kind": "cases", "cases": [{"set": {"n": 5}, "stdin": "", "call": None, "expect_out": "1\n2\n3\n4\n5"}], "require": ["For"], "forbid": ["max"]}` gibi tanımlanır. `set`, öğrencinin kodundaki ilk sabit atamanın değerini değiştirerek farklı girdileri dener; böylece öğrenci sabit cevabı doğrudan yazdırarak geçemez.
4. **Çıktı karşılaştırması (esnek):** Satır sonu boşlukları atılır; ardışık boşluklar teke indirilir; `casefold` ve Türkçe-ASCII katlama (ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u) uygulanır; sayılarda `5` ile `5.0` yalnızca soru tip ölçmüyorsa eşit sayılır.
5. **Yapı şartları:** "döngü kullanarak", "max() kullanmadan" gibi şartlar `require`/`forbid` ile AST üzerinde denetlenir. Mesajlar öğretici olmalı ("Soru `max()` kullanmadan çözmeni istiyor").
6. **Değerlendirilemeyen kod:** Beyaz liste dışı yapı kullanılırsa öğrenci 0 almaz; cevap "öğretmen incelemesi" durumuna düşer.

Yorumlayıcı gelene kadar 3. bölümdeki her KY önerisinde **"AST ölçütleri"** de verildi. Bu durumda en az şu test seti her denetleyici için zorunlu tutulmalı: 6 kabul edilmesi gereken farklı doğru çözüm ve 6 reddedilmesi gereken yanlış çözüm. Bu yanlışların arasında `break`, gereksiz atama ve sabit çıktı yazdırma bulunmalı.

### 1.5 Düşük öncelikli notlar

- `u01:80` `input_type` D/Y'de doğru ifade "input() ... her zaman str" ve yanlış ifade "her zaman int": aynı sözcük iki tarafta da var, iyi örnek. Bu denge diğer D/Y'lere de uygulanmalı (O4).
- `u02:57` `str_to_int` çarpma değişkesinde tek sık yanlış `n1+n2`; `"7" * b` gibi metin tekrarı yanılgısı da eklenebilir.
- `u03:83` `logic` içindeki `f"{a} == {a} or ..."` ifadesi her zaman True; bu ifade seçildiğinde soru ölçme gücünü kaybeder.
- `u05:57` `separate_ifs` sınır değerleri (`x = 10`, `x = 20`) iyi bir ayırt edici; korunmalı.
- `u08:128` `set_ops` küme işlemini listeden kurulan küme üzerinde yapıyor; kod okunurluğu için `a = {..}` küme literali de bir değişke olarak eklenebilir.
- Varsayılan `text` ("Aşağıdaki kodun ekran çıktısı ne olur?") 50'den fazla şablonda aynı. Kök çeşitliliği (ör. "Kod çalıştıktan sonra `x` değişkeninin değeri ne olur?", "Ekrana kaç satır yazılır?") hem ezberi azaltır hem de farklı bilişsel işlem ister.

---

## 2. Kapsam ve denge analizi

### 2.1 Mevcut durum: ünite × soru tipi × Bloom düzeyi

| # | Ünite | ÇS | D/Y | KC | KY | BD | Toplam | H/A | U | An/D | O |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Temel G/Ç ve Değişkenler | 6 | 1 | 0 | 1 | 0 | 8 | 2 | 5 | 0 | 1 |
| 2 | Veri Tipleri | 6 | 0 | 2 | 0 | 0 | 8 | 3 | 5 | 0 | 0 |
| 3 | Operatörler | 2 | 1 | 3 | 0 | 0 | 6 | 1 | 5 | 0 | 0 |
| 4 | Metinler | 7 | 0 | 1 | 0 | 0 | 8 | 0 | 8 | 0 | 0 |
| 5 | Koşullar | 4 | 1 | 0 | 0 | 0 | 5 | 1 | 4 | 0 | 0 |
| 6 | Döngüler | 5 | 0 | 1 | 1 | 0 | 7 | 0 | 6 | 0 | 1 |
| 7 | Listeler | 7 | 0 | 1 | 0 | 0 | 8 | 0 | 8 | 0 | 0 |
| 8 | Sözlük, Demet, Küme | 7 | 0 | 0 | 0 | 0 | 7 | 0 | 7 | 0 | 0 |
| 9 | Fonksiyonlar | 7 | 1 | 0 | 1 | 0 | 9 | 1 | 7 | 0 | 1 |
| 10 | Hata Yönetimi | 3 | 1 | 0 | 0 | 0 | 4 | 2 | 2 | 0 | 0 |
| 11 | Nesne Yönelimli | 4 | 1 | 0 | 0 | 0 | 5 | 1 | 4 | 0 | 0 |
| | **Toplam** | **58** | **6** | **8** | **3** | **0** | **75** | **11** | **61** | **0** | **3** |
| | **Oran** | %77 | %8 | %11 | %4 | %0 | | %15 | %81 | %0 | %4 |

Sınıflandırma: D/Y, `var_name`, `type_func`, `bool_conversion`, `conversion_error` ve `error_type` H/A sayıldı. Kod izleyip çıktı veya hata bulan bütün ÇS/KC maddeleri U sayıldı. Mevcut üç KY maddesi tek işlemli olduğu için alt düzey O sayıldı.

Gözlemler: Sekiz ünitede hiç KY yok. Dört ünitede (2, 4, 7, 8) hiç D/Y yok. Hiçbir ünitede Analiz ve Değerlendirme düzeyinde madde yok. Hata Yönetimi (4) ve Koşullar (5) ünitelerindeki şablon sayısı, her ünitede hiçbir şablonu iki kez görmeden yapılabilecek sınav uzunluğunu sınırlıyor.

### 2.2 Hiç ölçülmeyen konular

Ünite açıklamasında (`register_unit` metni) adı geçtiği hâlde ölçülmeyen konular **kalın** yazıldı:

| Ünite | Ölçülmeyen konular |
|---|---|
| 1 | Yorum satırı (`#`), kaçış karakterleri (`\n`, `\t`), print'e virgülle çok değer verme (varsayılan `sep`), **input() ile program akışı** (yalnızca D/Y'de var), büyük/küçük harf duyarlılığı |
| 2 | **`int(input())` kalıbı** (yalnızca D/Y'de), `round()`, float aritmetiği hassasiyeti (`0.1 + 0.2`), bool'un sayı gibi kullanılması, `str()` ile sayıyı metne çevirme sonucu |
| 3 | `**` sağdan birleşme (`2 ** 3 ** 2`), **`-=`, `//=`, `%=`, `**=`**, kısa devre değerlendirme, zincirleme karşılaştırma (yalnızca D/Y), tam bölünebilme ifadesi kurma |
| 4 | `find`/`index`, `join`, `startswith`/`endswith`, `isdigit`/`isalpha`, **metinlerin değiştirilemezliği**, kaçış karakterleri, negatif adımlı dilim (yalnızca `[::-1]` var), Türkçe İ/I sorunu |
| 5 | **İç içe koşullar** (açıklamada var, şablon yok), koşul sırası hatası (eşiklerin yanlış sıralanması), `in` ile koşul, `if x:` doğruluk değeri (yalnızca D/Y), metin karşılaştırma |
| 6 | Negatif adımlı `range`, gözcü değerli while (`while True` + `break`), sonsuz döngü tanıma, döngü sayısını hesaplama, liste üzerinde döngü, `enumerate` |
| 7 | `index`, `count`, `extend` (append ile karşılaştırma), `del`, iç içe listeler (2B), `in`, `+` ve `*` ile liste, kopyalama (`[:]`, `copy`) |
| 8 | **`keys()`/`values()`** (yalnızca `items` var), sözlükte `in` anahtara bakar, `del`/`pop`, literalde yinelenen anahtar, kümeye `add`, tek elemanlı demet `(5,)`, sözlükle sayma kalıbı |
| 9 | **İsimli (keyword) argüman**, **`global`**, parametre/argüman ayrımı, **modül içe aktarma biçimleri** (`import math as m`, `from ... import`), `random` modülü, fonksiyon içinden fonksiyon çağırma, temel durumu eksik özyineleme |
| 10 | Birden fazla except'in sırası, `except Exception as e`, **hatanın fonksiyondan çağırana yayılması**, girdi doğrulama döngüsü (`while True` + try) |
| 11 | `super().__init__`, örnek ve sınıf niteliği gölgeleme, değer döndüren metot ile yazdıran metot, nesne listeleri, `isinstance`, `__str__` olmadan nesneyi yazdırma |

### 2.3 Hedef dağılım önerisi

Bu rapordaki öneriler uygulandığında ünite başına 13-17 şablon olur (toplam yaklaşık 155).

| Soru tipi | Hedef oran | Ünite başına (yaklaşık) | Not |
|---|---|---|---|
| ÇS | %35-40 | 5-7 | Mevcutlar düzeltilerek korunur; yenilerde An/D düzeyi |
| D/Y | %12-15 | 2 | En az biri hesaplanan D/Y (`tf_claim`) |
| BD | %15-20 | 2-3 | Hepsi `verify="blank_output"` ile doğrulanır |
| KC | %12-15 | 2 | Sayısal ya da tek sözcük cevap |
| KY | %15 | 2-3 | Her ünitede en az 2 |

| Bloom düzeyi | Mevcut | Hedef |
|---|---|---|
| Hatırlama/Anlama | %15 | %20 |
| Uygulama (izleme, hesaplama) | %81 | %40 |
| Analiz/Değerlendirme | %0 | %20-25 |
| Oluşturma (kod yazma) | %4 | %15 |

Seviye (öğretmen paneli) önerisi: Başlangıç ünitelerinde (1-5) KY maddeleri tek kavramlı ve 3-6 satırlık olsun. Orta ünitelerde (6-10) 5-10 satır olsun. İleri ünitede (11) sınıf tanımı 10-15 satırı geçmesin.

---

## 3. Yeni soru önerileri

### 3.0 Tüm öneriler için ortak altyapı notları

1. **Hesaplanan D/Y (`tf_claim`, `verify="tf_output"`):** İfade bir kod ve bir iddiadan oluşur. Doğru cevap kod çalıştırılarak belirlenir. `answer == "True"` ise iddia gerçek çıktıdır; değilse iddia, `Wrong(değer, neden)` listesinden seçilen bir yanılgıdır ve öğrenci "Doğru" derse `neden` gösterilir. Bu türde çeşitlilik koddan gelir, 12 sınırı kolayca aşılır. İddia metni şu kalıpta olmalı: "Bu kod çalıştırıldığında ekrana `X` yazılır." Çok satırlı çıktılarda "ekrana alt alta `A`, `B` yazılır" kalıbı kullanılır.
2. **Boşluk doldurma (BD), altyapı kuran ajana önerilen alanlar:** `code` içinde `____` işaretleri bulunur. `blanks = [{"accept": [...], "match": "ast" | "text"}]` ve isteğe bağlı olarak `expected_output` tanımlanır (öğrenciye "Kodun çıktısı şu olmalı" diye gösterilir).
   - `match: "ast"` için boşluk ifadesi `ast.dump(ast.parse(x, mode="eval"))` ile karşılaştırılır. Böylece `range(1,6)` ile `range(1, 6)`, `'a'` ile `"a"`, `(b, a)` ile `b, a` eşit sayılır. Operatör ve anahtar sözcük boşlukları (`>=`, `elif`, `return`) ifade olmadığı için `match: "text"` kullanılır (baştaki ve sondaki boşluk atılır, büyük/küçük harf korunur).
   - Birbirine bağlı boşluklar için (ör. `>=` ile `18`, `>` ile `17`) `accept_sets: [[">=", "18"], [">", "17"]]` desteği önerilir. Destek yoksa bu tür madde tek boşluklu yazılmalı.
   - **Doğrulama (`verify="blank_output"`):** Test, her kabul edilen cevabı koda yerleştirip çalıştırır ve `expected_output` ile karşılaştırır. Ayrıca tanımlı yaygın yanlışların (`whys`) **farklı** çıktı verdiğini doğrular. Böylece kabul listesi hem eksik hem de yanlış kalamaz.
   - Yaygın yanlış cevaplara `whys` ile açıklama verilir (KC'deki `common_wrongs` gibi).
3. **Kod yazma (KY):** Her öneride iki ölçüt seti var: **Çıktı ölçütleri** (1.4'teki yorumlayıcı için test durumları) ve **AST ölçütleri** (yorumlayıcı yoksa yazılacak özel denetleyici). Her KY'de `answer` alanına örnek çözüm konur; mevcut test (`test_model_code_answers_pass_their_checker`) bunun hem denetleyiciden geçtiğini hem de çalıştığını doğrular.
4. **Çeşitlilik hesabı:** Her önerideki "Rastgele" satırı yaklaşık farklı soru sayısını verir. Testteki eşik 500 üretimde ≥12'dir; hedef ≥30 olmalı.
5. Numaralandırma: **Ö<ünite>.<sıra>**. Önerilen fonksiyon adı köşeli parantez içinde verildi.

---

### Ünite 1: Temel Giriş/Çıkış ve Değişkenler (7 öneri)

**Ö1.1 Yorum Satırları** [`comments`]: KC · H/U · Kazanım: `#` sonrasının çalıştırılmadığını bilir.
- Rastgele: 4 meyve ya da kelimeden hangisinin yorumda olduğu (satır başı yorum, satır sonu yorum, `#` öncesi boşluklu ya da boşluksuz), 7 kelimeden 4'ü seçilir → 7P4 × 3 düzen > 500.
- Örnek kök: "Aşağıdaki kodun ekran çıktısını yazınız:"
  ```python
  # print("Elma")
  print("Armut")  # print("Kiraz")
  #print("Muz")
  ```
  Cevap: `Armut`
- Sık yanlışlar: `Elma` ("`#` ile başlayan satır tamamen yok sayılır"), `Armut Kiraz` ya da `ArmutKiraz` ("Satırdaki `#`'den sonrası yorumdur; print içinde değil, print'ten sonra geliyor"), `Muz` ("`#` ile kod arasında boşluk olmasa da satır yorumdur").
- İpucu: "`#` işaretinden sonra satırın sonuna kadar olan kısım çalışır mı?"
- Kabul: tam metin, büyük/küçük harf duyarlı. Tek kelime cevap olduğu için `"Armut"` (tırnaklı) da kabul edilmeli; normalleştirmede baştaki ve sondaki tırnağı atın.

**Ö1.2 sep ve end Birlikte (hesaplanan D/Y)** [`sep_end_claim`]: D/Y · U · Kazanım: sep ve end parametrelerinin birlikte etkisini izler.
- Rastgele: iki ya da üç kelime (PEOPLE), sep ∈ {"-", "*", "", ", "}, end ∈ {"!", "", " ", "..."}, ikinci print'in kelimesi → yüzlerce farklı soru.
- Örnek: `print("Ali", "Can", sep="-", end="!")` / `print("Ece")`. Doğru iddia: "Bu kod ekrana `Ali-Can!Ece` yazar."
- Yanlış iddialar ve nedenleri: `Ali-Can!` alt satırda `Ece` ("end yeni satırın yerine geçer; `!` sonrası alt satıra inilmez"); `Ali Can!Ece` ("sep verildiği için araya boşluk değil `-` konur"); `Ali-Can-Ece!` ("sep yalnızca aynı print'in değerleri arasına girer"); `Ali-!Can` ("sep değerlerin arasına, end ise en sona gelir").
- İpucu: "sep nereye, end nereye eklenir? İkinci print hangi satırdan başlar?"

**Ö1.3 f-string Tamamlama** [`fstring_blank`]: BD · U · Kazanım: f-string sözdizimini kurar.
- Rastgele: değişken adı (`ad`, `isim`, `kullanici`), kişi (8), yaş (14-18), cümle kalıbı (3) → 360.
- Örnek kod: `ad = "Ece"` / `yas = 15` / `print(____"Benim adım {ad}, yaşım {yas}")`. Beklenen çıktı: `Benim adım Ece, yaşım 15`.
- Kabul (text): `f`, `F`.
- Yaygın yanlışlar: `str` ("str() bir fonksiyondur, tırnağın önüne yazılmaz"), `%` ve `format` ("Burada süslü parantezleri çalıştıran önek isteniyor").
- 2. değişke (iki boşluk): `print(f"Benim adım {____}, yaşım {____}")` → kabul `["ad"]`, `["yas"]` (ast). Yaygın yanlış `"ad"` tırnaklı ("Tırnak metin yazar; süslü parantez içine değişkenin adı yazılır").
- İpucu: "Süslü parantezlerin değişken değerine dönüşmesi için tırnağın önüne ne gelir?"

**Ö1.4 Değer Takası** [`swap_blank`]: BD · U/An · Kazanım: çoklu atamayla değer takası yapar.
- Rastgele: değişken çiftleri (`a,b`, `x,y`, `sol,sag`), başlangıç değerleri (1-30) → 400+.
- Örnek: `a, b = 3, 8` / `a, b = ____` / `print(a, b)`. Beklenen çıktı `8 3`.
- Kabul (ast): `b, a`, `(b, a)`, `[b, a]`.
- Yaygın yanlışlar: `a, b` ("Değerler değişmez"); `8, 3` ("Doğru çıktıyı verir ama değişkenleri değil sabitleri atar; kod başka değerlerle çalışmaz"). Bu ikincisini **reddedin** ve açıklamayı gösterin. Kök "değişken adlarını kullanarak" demeli.
- İpucu: "Sağ taraf önce bütünüyle hesaplanır; sağa hangi sırayla yazarsan sola o sırayla atanır."

**Ö1.5 input() ile Selamlama (Kod Yazma)** [`write_greet`]: KY · O · Kazanım: input() ile alınan değeri çıktıda kullanır.
- Rastgele: selam sözcüğü ("Merhaba", "Selam", "Hoş geldin"), istenen değişken adı (`ad`, `isim`, `kullanici`) → 9 temel × istem metni (4) = 36.
- Kök: "Kullanıcıdan adını <code>input()</code> ile alıp <code>ad</code> değişkenine kaydeden ve ekrana <strong>Merhaba</strong> ile birlikte adı yazdıran (ör. kullanıcı Ece yazarsa: <code>Merhaba Ece</code>) kodu yazınız."
- Örnek çözüm: `ad = input("Adın: ")` / `print("Merhaba", ad)`
- Çıktı ölçütleri: stdin `Ece` ve `Mert`; prompt metni çıktıdan çıkarılır; beklenen `Merhaba Ece`. Karşılaştırmada boşluk katlama uygulanır (`Merhaba Ece` ile `Merhaba  Ece` eşit), noktalama serbesttir (`Merhaba, Ece!` kabul).
- AST ölçütleri: (1) `ad = input(...)` ataması var (istem metni serbest); (2) bir `print` çağrısı içinde `ad` adı geçiyor (argüman, `+` birleştirme ya da f-string içinde); (3) aynı print'te ya da öncesinde selam sözcüğünü içeren bir metin sabiti var (Türkçe katlamayla karşılaştırılır). Ret mesajları: input yoksa "Ad kullanıcıdan alınmalı"; print'te sabit bir ad varsa (`print("Merhaba Ece")`) "Kullanıcının yazdığı ad, değişken üzerinden yazdırılmalı".
- İpucu: "İki satır yeterli: input ile al, print ile yaz."

**Ö1.6 Dikdörtgen Alan ve Çevre (Kod Yazma)** [`write_rect`]: KY · O · Kazanım: değişkenlerle aritmetik ifade kurup sonucu yazdırır.
- Rastgele: en (3-15), boy (2-12), değişken adları (`en, boy` / `a, b` / `kisa, uzun`) → 400+.
- Kök: "`en` değişkenine 7, `boy` değişkenine 4 atayın. Ardından dikdörtgenin alanını ve çevresini **iki ayrı satırda** yazdırın."
- Örnek çözüm: `en = 7` / `boy = 4` / `print(en * boy)` / `print(2 * (en + boy))`
- Çıktı ölçütleri: Satırların sayısal değerleri [28, 22] olmalı. Satırda etiket varsa (`Alan: 28`) son sayı alınır. `set` ile en ve boy değiştirilerek tekrar denenir (sabit yazdırmayı yakalar).
- AST ölçütleri: Atamalar `mult` denetleyicisindeki gibi izlenir. Print argümanlarındaki aritmetik ifade, bilinen sabitlerle **güvenli ifade hesaplayıcısı** ile değerlendirilir (yalnızca `Name`, `Constant`, `BinOp` +−*/ ve `UnaryOp` düğümleri). İfade en az bir değişken adı içermeli. Değerler ve sırası [alan, çevre] olmalı; sıra ters ise kabul edilmeli mi öğretmen ayarına bırakılabilir (öneri: ters sırayı kabul edin, mesajda belirtin). Ret mesajı: değer `en + boy * 2` gibi işlem önceliği hatası verirse "Çevre 2 × (en + boy) olmalı; parantez gerekiyor mu?"
- İpucu: "Alan en × boy, çevre 2 × (en + boy)."

**Ö1.7 Hangi Kod Bu Çıktıyı Verir?** [`which_print`]: ÇS · An · Kazanım: aynı çıktıyı üreten print biçimlerini ayırt eder.
- Rastgele: iki kelime (30 çift), hedef ayırıcı ("-", "", ", ") → 90.
- Kök: "Hangisi ekrana <code>Ali-Can</code> yazar?"
- Doğru: `print("Ali", "Can", sep="-")`. Yanlışlar: `print("Ali", "-", "Can")` ("Varsayılan sep boşluktur: `Ali - Can`"), `print("Ali", "Can", end="-")` ("end araya değil sona eklenir: `Ali Can-`"), `print("Ali" - "Can")` ("Metinler `-` ile çıkarılamaz: TypeError").
- Doğrulama: yeni `verify="output_one"` türü. Seçenekler birer koddur; yalnızca doğru seçeneğin çıktısı hedefe eşit olmalı. Bu tür Ö3.4, Ö9.6 ve diğerlerinde de kullanılır.
- İpucu: "Her seçenekte araya ne konduğunu ve sona ne eklendiğini ayrı ayrı yaz."

---

### Ünite 2: Veri Tipleri ve Dönüşümler (7 öneri)

**Ö2.1 Tip İddiası (hesaplanan D/Y)** [`type_claim`]: D/Y · A · Kazanım: değerin tipini belirler.
- Rastgele: 15 literal (`type_func` listesi) × iddia edilen tip (gerçek tip ya da 3 yanlıştan biri) × değişken adı (3) → 180.
- Örnek: `x = "3.14"` için "`print(type(x))` ekrana `<class 'float'>` yazar." Cevap: Yanlış.
- Yanlış iddiaların nedenleri: `_type_whys` (`u02:18`) açıklamaları aynen kullanılabilir.
- İpucu: "Önce tırnağa, sonra ondalık noktaya bak."

**Ö2.2 int(input()) Boşluğu** [`input_int_blank`]: BD · U · Kazanım: girdiyi sayıya çevirmesi gerektiğini bilir.
- Rastgele: girilen sayı (10-99), eklenen sayı (1-9), hedef tip (tam sayı ya da ondalık çıktı) → 1500+.
- Örnek: `yas = ____(input())` / `print(yas + 1)`. Kullanıcı `15` yazıyor, beklenen çıktı `16`.
- Kabul (text): `int`. Değişkede beklenen çıktı `16.0` ise kabul `float`.
- Yaygın yanlışlar: `str` ("Metin + sayı TypeError verir"); beklenen `16` iken `float` ("`16.0` yazar; çıktı tam sayı istiyor").
- İpucu: "input() hangi tipte döndürür? Toplama için neye çevirmen gerekir?"

**Ö2.3 Dönüşüm Yönü** [`conv_direction_blank`]: BD · An · Kazanım: aynı değerlerle birleştirme ve toplama arasında tip dönüşümüyle seçim yapar.
- Rastgele: a (metin, 10-99), b (sayı, 1-9), hedef işlem (toplama ya da birleştirme) → 1600+.
- Örnek A: `a = "12"` / `b = 3` / `print(____(a) + b)`, beklenen `15` → kabul `int`.
- Örnek B: `print(a + ____(b))`, beklenen `123` → kabul `str`.
- Yaygın yanlışlar: Örnek A için `str` ("Metin + sayı TypeError verir"); Örnek B için `int` ("`int(b)` zaten sayı; metin + sayı yine hata verir").
- İpucu: "Çıktı bir toplam mı, yan yana yazılmış metin mi?"

**Ö2.4 Karışık Dönüşüm Çıktısı** [`mixed_conv`]: KC · U · Kazanım: int, float ve str dönüşümlerinin sonucunu hesaplar.
- Rastgele: üç değişke × sayılar → 300+.
  - (a) `print(int("7") + float("2.5"))` → `9.5`
  - (b) `print(str(3) + "12")` → `312`
  - (c) `print(int(9.99) + int("4"))` → `13`
- Sık yanlışlar: (a) `9` ("float ile toplanan int sonucu float olur") ve `72.5` ("int() ve float() metinleri sayıya çevirir, birleştirme yapılmaz"); (b) `15` ("`str(3)` metindir; + birleştirir"); (c) `14` ("int() yuvarlamaz, keser").
- Kabul: sayı normalleştirmesi (`9,5` = `9.5`). Ancak `9.50` reddedilmeli, çünkü ekran çıktısı soruluyor.
- İpucu: "Her dönüşümün sonucunun tipini ayrı ayrı yaz."

**Ö2.5 bool Aritmetiği** [`bool_arith`]: KC · A/U · Kazanım: True ve False değerlerinin sayısal karşılığını bilir.
- Rastgele: `print(True + n)`, `print(False * n)`, `print(True + True + n)`, `print(sum([True, False, True]))`; n 2-20 → 60+.
- Örnek: `print(True + 4)` → `5`.
- Sık yanlışlar: `True4` ("bool metin değildir, birleştirme yapılmaz"), `Hata verir (TypeError)` ("bool, int'in alt tipidir ve hesaba katılabilir"), `4` ("True 1 değerindedir").
- İpucu: "True ve False hesaplarda hangi sayılar gibi davranır?"

**Ö2.6 İki Sayıyı Topla (Kod Yazma)** [`write_input_sum`]: KY · O · Kazanım: iki girdiyi int'e çevirip toplar.
- Rastgele: değişken adları (`a,b` / `sayi1,sayi2` / `x,y`) × örnek girdiler → 50+.
- Kök: "Kullanıcıdan <code>input()</code> ile iki <strong>tam sayı</strong> alıp toplamlarını ekrana yazdıran kodu yazınız. (Kullanıcı 7 ve 5 girerse çıktı 12 olmalı.)"
- Örnek çözüm: `a = int(input())` / `b = int(input())` / `print(a + b)`
- Çıktı ölçütleri: stdin `7\n5` → `12`; stdin `30\n-4` → `26`. Prompt'lar çıktıdan atılır; etiket varsa son sayı alınır.
- AST ölçütleri: (1) en az iki `input()` çağrısı var; (2) her biri `int(...)` içinde ya da sonradan `x = int(x)` ile çevrilmiş; (3) print argümanı iki girdi değişkeninin toplamı (`a + b`, `b + a` ya da bunu tutan ara değişken). `float` ile çevirmek ret alır ("Tam sayı istendi; float 12.0 yazar"). Çevirme yoksa mesaj: "input() metin döndürür; `7` + `5` metin olarak `75` olur."
- İpucu: "input() metin döndürür; toplamadan önce ne yapmalısın?"

**Ö2.7 Sıcaklık Dönüşümü (Kod Yazma)** [`write_celsius`]: KY · O · Kazanım: formülü Python ifadesine çevirir.
- Rastgele: c ∈ {-10, 0, 15, 20, 25, 30, 37, 40, 100} (sonucun kısa ondalıkla yazıldığı değerler); değişken adı `c`/`celsius`/`derece` → 27.
- Kök: "`c` değişkenine 25 atayın ve Fahrenheit karşılığını (F = C × 9 / 5 + 32) yazdırın."
- Örnek çözüm: `c = 25` / `print(c * 9 / 5 + 32)` → `77.0`
- Çıktı ölçütleri: Sayısal değer 77'ye eşit olmalı (±1e-9). `77` ile `77.0` ikisi de kabul edilir, çünkü bu soru tip ölçmüyor. `set c=0` ile 32 elde edilmeli.
- AST ölçütleri: Güvenli ifade hesaplayıcısı (Ö1.6) ile `c * 9 / 5 + 32`, `1.8 * c + 32`, `(c * 9 / 5) + 32` ve `32 + c * 1.8` gibi biçimlerin hepsi değer üzerinden kabul edilir. İfade `c` adını içermeli.
- İpucu: "Formülü olduğu gibi yaz; Python çarpma ve bölmeyi toplamadan önce yapar."

---

### Ünite 3: Operatörler (7 öneri)

**Ö3.1 Operatör İddiası (hesaplanan D/Y)** [`op_claim`]: D/Y · U · Kazanım: `//`, `%`, `/` ve `**` sonuçlarını ayırt eder.
- Rastgele: a (11-60), b (2-9), işlem (4) × iddia (gerçek sonuç ya da diğer üç işlemin sonucu) → 2000+.
- Örnek: "`print(17 // 5)` ekrana `2` yazar." Cevap: Yanlış (doğrusu 3; 2 kalandır).
- Neden metinleri işleme göre: "Bu `%` sonucudur", "Bu `/` sonucudur; `//` kesir kısmını atar".
- İpucu: "`//` bölümün tam kısmı, `%` kalandır."

**Ö3.2 Eksik Operatör** [`missing_op_blank`]: BD · An · Kazanım: sonuçtan geriye giderek operatörü belirler.
- Rastgele: a, b ve operatör. Üretimde {+, -, *, /, //, %, **} kümesinden yalnızca **bir** operatörün hedef sonucu verdiği (a, b) çiftleri seçilir; tekillik `while` ile denetlenir → 500+.
- Örnek: `print(17 ____ 5)`, beklenen çıktı `2` → kabul (text): `%`.
- Yaygın yanlışlar: `//` ("17 // 5 = 3; bölüm değil kalan isteniyor"), `-` ve `/` için hesaplanmış sonuçlar.
- Ek değişke: beklenen `3.4` → `/`.
- İpucu: "Her operatörü dene: hangisi tam olarak bu sonucu verir?"

**Ö3.3 Birleşik Atama Zinciri** [`augmented2`]: KC · U · Kazanım: `//=`, `**=` ve `%=` operatörlerini izler (bugün yalnızca +=, *=, -= ölçülüyor).
- Rastgele: başlangıç (10-30), üç işlem (`//=` ve `%=` 2-7, `**=` 2) ve işlem sırası (3! = 6) → 1000+.
- Örnek: `x = 17` / `x //= 3` / `x **= 2` / `x %= 7` / `print(x)` → `4` (17 → 5 → 25 → 4).
- Sık yanlışlar: `25` ("son satırı atladın: 25 % 7 = 4"), `5.666...` ya da `32.11` ("`//=` tam bölmedir"), `1` ("`**=` üs alır, `x * 2` değil").
- İpucu: "Her satırdan sonra x'in yeni değerini yaz."

**Ö3.4 Bölünebilme Koşulu** [`divisible_expr`]: ÇS · An/D · Kazanım: tam bölünebilmeyi doğru ifade eder.
- Rastgele: değişken (`sayi`, `n`, `x`), bölen (2-9) ve soru yönü ("tam bölünür" ya da "tek sayıdır") → 50+.
- Kök: "Hangi ifade `sayi` değişkeninin 3'e tam bölünüp bölünmediğini **her sayı için doğru** kontrol eder?"
- Doğru: `sayi % 3 == 0`. Yanlışlar: `sayi / 3 == 0` ("yalnızca sayi 0 ise True olur"); `sayi // 3 == 0` ("yalnızca 0, 1 ve 2 için True olur"); `sayi % 3 == 1` ("kalanın 1 olması bölünmediğini gösterir").
- Doğrulama: `verify="predicate_one"`. Test her seçeneği `sayi` ∈ range(-20, 21) için dener; yalnızca doğru seçenek her durumda `sayi % 3 == 0` ile aynı sonucu vermeli.
- İpucu: "Tam bölünen bir sayının kalanı kaçtır?"

**Ö3.5 Kısa Devre Değerlendirme** [`short_circuit`]: ÇS · An · Kazanım: `and`/`or` operatörlerinin ikinci tarafı ne zaman değerlendirmediğini bilir.
- Rastgele: x (0 ya da 1-9), `and`/`or`, ikinci taraf `10 / x > 1` ya da `len(liste) > 0` → 40+.
- Örnek: `x = 0` / `print(x != 0 and 10 / x > 1)` → `False`.
- Yanlışlar: `Hata verir (ZeroDivisionError)` ("and'in sol tarafı False olunca sağ taraf hiç hesaplanmaz"), `True` ("x != 0 yanlış; and için ikisi de doğru olmalı"), `None` ("Karşılaştırmalar True ya da False verir").
- İpucu: "and'in sol tarafı False ise sağ tarafa bakmaya gerek var mı?"
- Seviye: İleri; Ünite 3 sonunda ya da Ünite 5 ile birlikte kullanılmalı.

**Ö3.6 Saniyeyi Dakikaya Çevir (Kod Yazma)** [`write_divmod`]: KY · O · Kazanım: `//` ve `%` ile birim çevirir.
- Rastgele: saniye (61-3599), değişken adı (`toplam`, `saniye`, `sure`) → 1000+.
- Kök: "`toplam` değişkenine 135 atayın. Bu süreyi dakika ve saniye olarak tek satırda yazdırın (135 için çıktı: `2 15`)."
- Örnek çözüm: `toplam = 135` / `print(toplam // 60, toplam % 60)`
- Çıktı ölçütleri: `set toplam` ∈ {135, 600, 59}; satırdaki iki sayı (dk, sn) olmalı. Ayırıcı serbest (`2 15`, `2:15`, `2 dakika 15 saniye`): satırdaki tam sayılar ayıklanıp karşılaştırılır.
- AST ölçütleri: Print argümanları güvenli hesaplayıcıyla [toplam//60, toplam%60] vermeli ve `toplam` adını içermeli (sabit `2, 15` reddedilir: "Değerleri kodla hesapla; toplam değişince cevap da değişmeli"). `divmod(toplam, 60)` ve ara değişkenler (`dk = toplam // 60`) kabul edilir.
- İpucu: "Dakika için hangi operatör, kalan saniye için hangisi?"

**Ö3.7 Üç Notun Ortalaması (Kod Yazma)** [`write_average`]: KY · O · Kazanım: işlem önceliğini doğru kullanır.
- Rastgele: üç not (40-100), değişken adları → 1000+.
- Kök: "`n1 = 70`, `n2 = 85`, `n3 = 90` atayıp ortalamayı yazdırın."
- Örnek çözüm: `print((n1 + n2 + n3) / 3)` → `81.66666666666667`
- Çıktı ölçütleri: Değer ±0.01 ile karşılaştırılır; `round(..., 2)` ve f-string ile `81.67` kabul edilir.
- AST ölçütleri: Güvenli hesaplayıcı ile değer karşılaştırılır. İfade üç değişkeni de içermeli. `n1 + n2 + n3 / 3` yazılmışsa (değer 185) özel mesaj verilir: "Yalnızca n3 üçe bölündü; toplamı paranteze al."
- İpucu: "Önce toplam, sonra bölme. Python önce hangisini yapar?"

---

### Ünite 4: Metinler (8 öneri)

**Ö4.1 İndeks İddiası (hesaplanan D/Y)** [`index_claim`]: D/Y · U · Kazanım: pozitif ve negatif indeksi doğru okur.
- Rastgele: kelime (12, doğru Türkçe yazımla), indeks (-3…4) × iddia (gerçek karakter ya da ±1 kaydırılmış karakter) → 150+.
- Örnek: `metin = "Bilgisayar"` için "`print(metin[-2])` ekrana `r` yazar." Cevap: Yanlış (`a`; `r` son karakterdir).
- İpucu: "[-1] son karakterdir."

**Ö4.2 Dilimi Tamamla** [`slice_blank`]: BD · An · Kazanım: istenen parçayı verecek dilimi kurar; eşdeğer dilimleri görür.
- Rastgele: kelime (12) × parça başlangıcı ve uzunluğu (2-4) → 200+.
- Örnek: `metin = "Python"` / `print(metin[____])`, beklenen `tho`.
- Kabul (text, boşluksuz karşılaştırma): üretimde **kaba kuvvetle** hesaplanır. `a` ∈ {boş, -n…n}, `b` ∈ {boş, -n…n} olmak üzere `metin[a:b] == hedef` sağlayan tüm `a:b` biçimleri kabul listesine girer. "Python"/"tho" için: `2:5`, `2:-1`, `-4:5`, `-4:-1`. Parça sona dayanıyorsa `2:` biçimi de çıkar.
- Yaygın yanlışlar: `2:4` ("bitiş dahil değildir"), `3:6` ("indeksler 0'dan başlar").
- İpucu: "İlk karakterin indeksi kaç? Bitiş indeksi dahil mi?"
- Not: Adımlı dilimleri (`::2`) kabul listesine almayın; `match: "text"` ile `2 : 5` gibi boşluklu yazımlar boşluk atılarak eşleşir.

**Ö4.3 Metot Bul** [`method_blank`]: BD · An · Kazanım: çıktıdan metodu belirler; Türkçe büyük harf sorununu tanır.
- Rastgele: metin (8, başta/sonda boşluk içerenler dahil), metot ∈ {upper, lower, title, capitalize, strip}. Hedef sonucu **tek** metodun verdiği durumlar seçilir → 30+.
- Örnek: `print("  okul zamanı  ".____())`, beklenen `okul zamanı` (boşluksuz) → kabul `strip`.
- Örnek (Türkçe tuzak): `print("istanbul".____())`, beklenen `ISTANBUL` → kabul `upper`. Çözüme şu not eklenir: "Python i harfini İ'ye değil I'ya çevirir; Türkçe büyük harf için `replace("i", "İ")` gerekir."
- Yaygın yanlışlar: `title` ("Her kelimenin ilk harfini büyütür"), `lstrip` ("yalnızca soldakileri siler").
- İpucu: "Çıktıda ne değişmiş: harfler mi, boşluklar mı?"

**Ö4.4 find() ve index()** [`find_index`]: KC · U · Kazanım: aranan parçanın konumunu bulur; bulunamayınca -1 döndüğünü bilir.
- Rastgele: kelime (12), aranan karakter (var ya da yok), `find`/`index`/`count` → 100+.
- Örnek: `print("Bilgisayar".find("g"))` → `3`. Değişke: `"z"` → `-1`.
- Sık yanlışlar: `4` ("indeks 0'dan başlar"); yok durumunda `None`, `0` ve `Hata` ("find bulamazsa -1 döndürür; hata veren index()'tir"); birden çok geçen harfte son konum ("find ilk geçtiği yeri verir").
- Kabul: tam sayı; `−1` (Unicode eksi) normalleştirilmeli.
- İpucu: "Saymaya 0'dan başla; bulunamazsa find ne döndürür?"

**Ö4.5 Metinler Değiştirilemez** [`str_immutable`]: ÇS · A/U · Kazanım: metnin karakterine atama yapılamayacağını bilir.
- Rastgele: kelime (12), indeks (0-3), yeni harf. %50 hatalı değişke `s[0] = "K"`; %50 doğru düzeltme `s = "K" + s[1:]` (K5'teki sabit cevap sorununu önlemek için) → 200+.
- Hatalı değişkede doğru cevap `Hata verir (TypeError)`. Yanlışlar: `Kalem` ("Metnin tek karakteri değiştirilemez; yeni metin oluşturulmalı"), `kalem` ("Atama satırı hata verdiği için print'e ulaşılmaz"), `Hata verir (IndexError)` ("İndeks geçerli; sorun atamanın kendisinde").
- Doğrulama: iki ayrı şablon (`verify="error"` ve `verify="output"`) ya da 1.1-K5'te önerilen karma test türü.
- İpucu: "Metin oluşturulduktan sonra tek bir karakteri değiştirilebilir mi?"

**Ö4.6 Doğru mu? Metin İşlemleri (hesaplanan D/Y)** [`str_method_claim`]: D/Y · U · Kazanım: `split`, `join` ve `replace` sonuçlarını izler.
- Rastgele: kelimeler, ayırıcı, işlem → 300+.
- Örnek: `print("-".join(["a", "b", "c"]))` → iddia `a-b-c-` (Yanlış; "join ayırıcıyı yalnızca elemanların arasına koyar").
- Diğer yanılgılar: `split()` sonucunu metin sanmak; `replace`'in yalnızca ilk eşleşmeyi değiştirdiğini sanmak.
- İpucu: "join ayırıcıyı nereye koyar?"

**Ö4.7 Kelimeyi Ters Çevir (Kod Yazma)** [`write_reverse`]: KY · O · Kazanım: dilimleme ya da döngüyle metni ters çevirir.
- Rastgele: kelime (12), değişken adı (`kelime`, `metin`, `s`) → 36.
- Kök: "`kelime = "kalem"` satırıyla başlayan ve kelimeyi **ters** çevirip yazdıran kodu yazınız (çıktı: `melak`)."
- Örnek çözüm: `kelime = "kalem"` / `print(kelime[::-1])`
- Çıktı ölçütleri: `set kelime` ∈ {"kalem", "Python", "a"}; beklenen ters metin, büyük/küçük harf korunarak.
- AST ölçütleri: Kabul edilen biçimler (a) print argümanı `kelime[::-1]` ya da bunu tutan değişken; (b) `"".join(reversed(kelime))`; (c) `ters = ""` / `for h in kelime: ters = h + ters` / `print(ters)`, yani boş metinle başlayan, döngüde `h + ters` biçiminde güncellenen ve sonra yazdırılan değişken. Yazılan sabit metin (`print("melak")`) reddedilir: "Kod her kelime için çalışmalı."
- İpucu: "Dilimlemede adım -1 ne yapar?"

**Ö4.8 Sesli Harf Sayısı (Kod Yazma)** [`write_vowels`]: KY · O · Kazanım: döngü, `in` ve sayaçla metin işler.
- Rastgele: kelime (12 Türkçe kelime; büyük harf içermeyen), değişken adları → 36.
- Kök: "`metin = "bilgisayar"` metnindeki sesli harflerin (a, e, ı, i, o, ö, u, ü) sayısını bulup yazdıran kodu yazınız."
- Örnek çözüm: `sayac = 0` / `for h in metin:` / `if h in "aeıioöuü":` / `sayac += 1` / `print(sayac)` → `4`
- Çıktı ölçütleri: `set metin` ∈ {"bilgisayar", "okul", "xyz"} → 4, 2, 0. `sum(1 for ...)` ya da her sesli için `count` kullanmak kabul edilir.
- AST ölçütleri: `metin` üzerinde `For`; gövdede `Compare` + `In` (sesli harf metni ya da listesi); `AugAssign +=1`; döngüden sonra sayacın `print` edilmesi. Sesli harf kümesi Türkçe sesli harflerin en az 8'ini içermeli (eksikse mesaj: "ı, ö, ü harflerini unutma").
- İpucu: "Her harf için 'sesli mi?' diye sor; evetse sayacı artır."

---

### Ünite 5: Koşullu İfadeler (8 öneri)

**Ö5.1 İç İçe Koşul Çıktısı** [`nested_if`]: ÇS · An · Kazanım: girintiden else'in hangi if'e ait olduğunu çıkarır. (Açıklamadaki "iç içe koşullar" konusunu ilk kez ölçer.)
- Rastgele: x (1-40), eşik (5-25), iç koşul (çift/tek, `> eşik2`), etiketler ("A"/"B"/"C" ya da "Çift"/"Tek"/"Küçük") → 300+.
- Örnek:
  ```python
  x = 14
  if x > 10:
      if x % 2 == 0:
          print("A")
      else:
          print("B")
  else:
      print("C")
  ```
  Cevap `A`.
- Yanlışlar: x'e göre hesaplanır. "C" için: "x > 10 doğru; dış else atlanır". "B" için: "İç koşul doğru; iç else çalışmaz". İki satırlı "A\nC" için: "Bir if/else yapısından yalnızca bir blok çalışır".
- İpucu: "Önce dıştaki koşulu kontrol et; içeri girersen içtekine bak."

**Ö5.2 Eşik Sırası Hatası** [`ladder_order_bug`]: ÇS · An/D · Kazanım: if/elif zincirinde koşul sırasının sonucu nasıl değiştirdiğini fark eder.
- Rastgele: eşikler (3 eşik), puan (0-100) ve hatalı sıralamada hangi eşiğin öne alındığı → 200+.
- Kök: "Öğretmen 85 ve üstüne A, 70 ve üstüne B yazdırmak istiyor. Bu kod puan = 92 için ne yazdırır?"
  ```python
  if puan >= 70:
      print("B")
  elif puan >= 85:
      print("A")
  ```
  Cevap `B`.
- Yanlışlar: `A` ("İlk doğru koşul puan >= 70; elif'e hiç bakılmaz"), `B\nA`, `Hiçbir şey yazmaz`.
- İpucu: "Python koşulları hangi sırayla dener ve ne zaman durur?"
- Değişke (Değerlendirme): "Bu kod hangi puanlar için yanlış sonuç verir?" ÇS: "85 ve üstü" doğru; "70-84", "70'in altı" ve "Hiçbir puan" yanlış.

**Ö5.3 Koşulu Tamamla** [`cond_blank`]: BD · U · Kazanım: sözel koşulu karşılaştırma operatörüne çevirir.
- Rastgele: kural ("18 ve üstü", "10'dan küçük", "50'ye eşit değil"…), değişken, eşik → 100+.
- Örnek: "18 ve üstü yaşlar için `Reşit` yazmalı." Kod: `if yas ____ 18:`.
- Kabul (text): `>=`. Bağımlı boşluk desteği varsa sayı da boşluk olur: `accept_sets: [[">=", "18"], [">", "17"]]`.
- Yaygın yanlışlar: `>` ("18 yaşındaki biri dışarıda kalır"), `=>` ("Python'da `>=` yazılır; `=>` sözdizimi hatasıdır").
- İpucu: "'ve üstü' eşitliği de kapsar mı?"

**Ö5.4 Eşitlikte Hangisi?** [`tie_max`]: KC · An · Kazanım: eşitlik durumunda koşul zincirini izler.
- Rastgele: a, b, c (bazı üretimlerde bilinçli eşitlik), etiketlerin sırası → 200+.
- Örnek: `a, b, c = 7, 7, 3`, ardından `if a > b and a > c: print("a")` / `elif b > c: print("b")` / `else: print("c")` → `b`.
- Sık yanlışlar: `a` ("a > b, 7 > 7 olduğu için yanlış; eşit sayılar birbirinden büyük değildir"), `c`.
- Kabul: tek harf, büyük/küçük harfe duyarsız, tırnaklar atılır.
- İpucu: "7 > 7 doğru mu?"

**Ö5.5 Koşullar (hesaplanan D/Y)** [`cond_claim`]: D/Y · U · Kazanım: and, or ve not içeren koşulu değerlendirir.
- Rastgele: `compound_condition` kodu + iddia → 200+.
- Örnek: "yas = 16, izin = True iken `if yas >= 18 and izin:` kodu `Girebilir` yazar." Cevap: Yanlış.
- İpucu: "and için iki tarafın da doğru olması gerekir."

**Ö5.6 Tek mi Çift mi? (Kod Yazma)** [`write_even_odd`]: KY · O · Kazanım: `%` ile koşul kurar.
- Rastgele: değişken adı (`sayi`, `n`, `x`), başlangıç değeri, çıktı sözcükleri ("Çift/Tek", "çift sayı/tek sayı") → 30+.
- Kök: "`sayi = 17` satırıyla başlayan ve sayı çiftse `Çift`, tekse `Tek` yazdıran kodu yazınız."
- Örnek çözüm: `if sayi % 2 == 0:` / `print("Çift")` / `else:` / `print("Tek")`
- Çıktı ölçütleri: `set sayi` ∈ {17, 4, 0, -3}. Karşılaştırma Türkçe katlamayla yapılır (`Cift`, `çift` kabul).
- AST ölçütleri: Bir `If` var. Koşul şu biçimlerden biri: `sayi % 2 == 0`, `sayi % 2 != 0`, `sayi % 2 == 1`, `sayi % 2` (doğruluk değeri) ya da `not sayi % 2`. Dallar koşulun anlamına göre doğru metni yazdırmalı (Türkçe katlama). Dallar ters ise mesaj: "Koşul doğruyken hangi metin yazılmalı?" `else` yerine ikinci bir `if` kullanmak kabul edilir.
- İpucu: "Çift sayının 2'ye bölümünden kalan kaçtır?"

**Ö5.7 Not Harfi (Kod Yazma)** [`write_grade_ladder`]: KY · O · Kazanım: if/elif/else zinciriyle aralık sınıflandırır.
- Rastgele: eşikler (85/70/50 ya da 90/75/60), harfler (A/B/C/F ya da "Pekiyi"/"İyi"/"Orta"/"Geçmez") → 20+. Sınır değerleri test durumlarını değiştirir.
- Kök: "`puan = 77` satırıyla başlayan; 85 ve üstüne A, 70-84 arasına B, 50-69 arasına C, 50'nin altına F yazdıran kodu yazınız."
- Çıktı ölçütleri: `set puan` ∈ {100, 85, 84, 70, 69, 50, 49, 0}. Sınır değerleri (85, 70, 50) zorunlu test durumlarıdır.
- AST ölçütleri (yorumlayıcı yoksa): Koşullar `Compare` düğümlerinden çıkarılıp sembolik değerlendirmeyle 8 test değeri için dal seçilir (yalnızca `puan` ve sabitlerden oluşan koşullar desteklenir). Ters sırayla `<` koşulları kurmak (`if puan < 50: F ...`) da bu yöntemle kabul edilir.
- İpucu: "En yüksek eşikten başla; elif kullan."

**Ö5.8 Hangi Kod Doğru Çalışır?** [`which_condition`]: ÇS · D · Kazanım: aynı amacı güden kodları karşılaştırır.
- Rastgele: amaç ("10 ile 20 arasında mı?" ya da "negatif mi, sıfır mı, pozitif mi?"), değişken adları → 20+.
- Kök: "Hangi kod `x` 10 ile 20 arasındaysa (ikisi dahil) `Evet` yazar, değilse hiçbir şey yazmaz?"
- Doğru: `if 10 <= x <= 20:`. Yanlışlar: `if x >= 10 or x <= 20:` ("or her sayı için True olur"), `if 10 < x < 20:` ("sınırlar dahil değil"), `if x >= 10 and x =< 20:` ("`=<` geçersiz bir operatör").
- Doğrulama: `verify="output_one"`, `x` ∈ range(0, 31) için çıktılar karşılaştırılır. Sözdizimi hatalı seçenek "çalışmaz" sayılır.
- İpucu: "Her seçeneği 9, 10, 20 ve 21 için dene."

---

### Ünite 6: Döngüler (8 öneri)

**Ö6.1 Kaç Tur? (hesaplanan D/Y)** [`loop_count_claim`]: D/Y · U · Kazanım: range ile kurulan döngünün tur sayısını hesaplar.
- Rastgele: başlangıç (0-5), bitiş (6-20), adım (1-4) × iddia (gerçek tur sayısı ya da ±1) → 500+.
- Örnek: "`for i in range(3, 17, 4):` döngüsü 4 kez döner." Cevap: Doğru (3, 7, 11, 15).
- Yanlış iddianın nedeni: "17 dahil değildir; son değer 15'tir" ya da "3 dahildir".
- İpucu: "Üretilen değerleri tek tek yaz."

**Ö6.2 range'i Tamamla** [`range_blank`]: BD · An · Kazanım: istenen diziyi üreten range argümanlarını kurar.
- Rastgele: başlangıç (0-5), adım (1-3, bazen -1/-2), eleman sayısı (4-7) → 300+.
- Örnek: `for i in range(____):` / `print(i, end=" ")`, beklenen `2 4 6 8 10 `.
- Kabul (ast): tüm geçerli üçlüler kaba kuvvetle hesaplanır: `2, 11, 2` ve `2, 12, 2`. Adım 1 ve başlangıç 0 ise tek argümanlı biçim de eklenir (ör. `5` ile `0, 5`). Negatif adımda `10, 0, -2` ve `10, 1, -2` gibi.
- Yaygın yanlışlar: `2, 10, 2` ("10 dahil olmaz"), `1, 11, 2` ("tek sayılar üretir").
- İpucu: "İlk sayı, adım ve bitiş: bitiş dahil değil."

**Ö6.3 while Koşulunu Tamamla** [`while_blank`]: BD · An · Kazanım: döngü koşulunu çıktıya göre kurar.
- Rastgele: başlangıç (0-5), son değer (4-10), artış (1-2) → 100+.
- Örnek: `sayac = 1` / `while sayac ____ 5:` / `print(sayac)` / `sayac += 1`, beklenen çıktı 1'den 5'e alt alta.
- Kabul (text): koda yerleştirilince beklenen çıktıyı veren operatörler, kaba kuvvetle {<, <=, !=, >, >=, ==} denenerek bulunur; bu örnekte yalnızca `<=`. Sayıyı da içeren bağımlı boşluk desteği varsa `< 6` ve `!= 6` de kabul edilir.
- Yaygın yanlışlar: `<` ("5 yazdırılmaz"), `!=` ("sayac 5 olunca durur; 5 yazdırılmaz"), `>` ("döngü hiç çalışmaz").
- İpucu: "sayac 5 iken döngü bir kez daha çalışmalı mı?"

**Ö6.4 Koşullu Toplam** [`cond_sum`]: KC · U · Kazanım: döngü içinde koşulla biriktirme yapar.
- Rastgele: bitiş (8-20), bölen (2-5), işlem (toplama ya da sayma) → 150+.
- Örnek: `toplam = 0` / `for i in range(1, 13):` / `if i % 3 == 0:` / `toplam += i` / `print(toplam)` → `30`.
- Sık yanlışlar: `18` ("12 de dahil; range(1, 13) 12'yi üretir"), `4` ("toplam'a 1 değil i ekleniyor"), `78` ("yalnızca 3'e bölünenler eklenir").
- İpucu: "Hangi i değerlerinde koşul doğru? Onları topla."

**Ö6.5 while True ve break** [`sentinel_break`]: KC · U · Kazanım: sonsuz döngünün break ile nasıl bittiğini izler.
- Rastgele: x (15-40), azalış (3-7), koşul (`< 0` ya da `<= 0`) → 200+.
- Örnek: `x = 23` / `while True:` / `x -= 5` / `if x < 0:` / `break` / `print(x)` → `-2`.
- Sık yanlışlar: `3` ("x = 3 iken koşul yanlış; bir tur daha döner"), `0`, `-7`.
- Kabul: tam sayı; Unicode eksi normalleştirilmeli.
- İpucu: "x'in her turdaki değerini yaz; break hangi değerde çalışıyor?"

**Ö6.6 Hangi Döngü Hiç Bitmez?** [`infinite_loop`]: ÇS · An · Kazanım: sonsuz döngüye yol açan hatayı fark eder.
- Rastgele: değişken adı, sınır, hata türü (artış unutulmuş, ters yönde artış, koşulda yanlış değişken) → 50+.
- Doğru (sonsuz olan): `i = 0` / `while i < 5:` / `print(i)` (artış yok). Diğer üç seçenek sonlanır ve her birinin "neden" açıklaması kaç tur döndüğünü söyler.
- Doğrulama: `verify="halts_one"`. Test, `tracer.py`'deki adım sınırıyla her seçeneği çalıştırır; yalnızca doğru seçenek sınıra takılmalı.
- İpucu: "Her döngüde koşulu yanlış yapacak bir değişiklik var mı?"

**Ö6.7 1'den n'e Toplam (Kod Yazma)** [`write_sum_loop`]: KY · O · Kazanım: biriktirici değişkenle döngü kurar.
- Rastgele: n (5-30), döngü türü şartı ("for ile" ya da "while ile"), değişken adı → 100+.
- Kök: "`n = 10` satırıyla başlayan ve **döngü kullanarak** 1'den n'e kadar (n dahil) sayıların toplamını yazdıran kodu yazınız."
- Örnek çözüm: `toplam = 0` / `for i in range(1, n + 1):` / `toplam += i` / `print(toplam)`
- Çıktı ölçütleri: `set n` ∈ {10, 1, 7} → 55, 1, 28. `require: ["For" | "While"]`; `sum(range(...))` kullanılırsa mesaj: "Soru döngü kullanmanı istiyor" (öğretmen ayarıyla kabul edilebilir).
- AST ölçütleri: Sıfır ile başlayan bir biriktirici var; döngü `range(1, n + 1)` ya da `range(n + 1)` (sabitlerle ya da `n` ile kurulabilir; K2'deki ifade hesaplama). Gövdede `toplam += i` ya da `toplam = toplam + i` var; `break` ve `continue` yok; döngüden **sonra** `print(toplam)` var. Print döngü içindeyse mesaj: "Ara toplamları değil, yalnızca sonucu yazdır."
- İpucu: "Döngüden önce toplamı 0 yap; her turda i'yi ekle."

**Ö6.8 Çarpım Tablosu Satırı (Kod Yazma)** [`write_times_table`]: KY · O · Kazanım: döngü değişkenini biçimli çıktıda kullanır.
- Rastgele: n (2-9), aralık (1-5 ya da 1-10), işaret (`x` ya da `*`) → 50+.
- Kök: "`n = 7` için `7 x 1 = 7` … `7 x 5 = 35` satırlarını alt alta yazdıran kodu yazınız."
- Örnek çözüm: `for i in range(1, 6):` / `print(n, "x", i, "=", n * i)`
- Çıktı ölçütleri: Satır sayısı 5. Her satırda çıkarılan tam sayılar [n, i, n*i] olmalı. Boşluklar ve işaret (`x`, `X`, `*`, `×`) serbest.
- AST ölçütleri: `For` + `range` (bitiş dahil olacak biçimde). Gövdede bir print, argümanlarında `n`, döngü değişkeni ve `n * i` (ya da `i * n`) bulunur. Argümanlar virgülle, f-string ile ya da `str()` birleştirmeyle verilebilir.
- İpucu: "Her satırda değişen tek şey i."

---

### Ünite 7: Listeler (8 öneri)

**Ö7.1 append ile extend (hesaplanan D/Y)** [`append_extend_claim`]: D/Y · A/U · Kazanım: append ve extend farkını bilir.
- Rastgele: başlangıç listesi (2-4 eleman), eklenen liste (2-3 eleman), metot × iddia → 200+.
- Örnek: `a = [1, 2]` / `a.append([3, 4])` / `print(len(a))` için iddia "ekrana 4 yazar". Cevap: Yanlış (3; liste tek eleman olarak eklenir).
- İpucu: "append kaç eleman ekler?"

**Ö7.2 Liste Metodunu Bul** [`list_method_blank`]: BD · An · Kazanım: liste değişiminden metodu çıkarır.
- Rastgele: liste (4 sayı), metot ∈ {append, remove, pop, sort, reverse, insert}. Argümanlar kodda gösterilir; hedefi tek metodun verdiği durumlar seçilir → 500+.
- Örnek: `liste = [5, 9, 2]` / `liste.____(9)` / `print(liste)`, beklenen `[5, 2]` → kabul `remove`.
- Yaygın yanlışlar: `pop` ("pop(9) indeks 9'u çıkarmaya çalışır ve IndexError verir"), `del` ("del bir metot değil, deyimdir").
- İpucu: "Değere göre mi, indekse göre mi çıkarıldı?"

**Ö7.3 Liste Üreteci İfadesi** [`comp_blank`]: BD · U/O · Kazanım: liste üretecinin ifade kısmını yazar.
- Rastgele: dönüşüm (kare, 2 katı, 1 fazlası, 10 ile mod), range bitişi (4-7) → 30+. Variety için değişken adı da (`x`, `n`, `i`) rastgele seçilir.
- Örnek: `kareler = [____ for x in range(1, 5)]` / `print(kareler)`, beklenen `[1, 4, 9, 16]`.
- Kabul (ast): `x * x`, `x ** 2`, `pow(x, 2)`. Doğrulama `blank_output` ile her kabul edilen cevap çalıştırılarak yapılır.
- Yaygın yanlışlar: `x * 2` ("2 katını alır; kare değil"), `x ^ 2` ("Python'da `^` üs değil, XOR'dur").
- İpucu: "Her x'ten ne üretiliyor? 2 → 4, 3 → 9."

**Ö7.4 index() ve count()** [`index_count`]: KC · U · Kazanım: liste içinde konum ve tekrar sayısı bulur.
- Rastgele: tekrar içeren liste (5-7 eleman), aranan değer → 500+.
- Örnek: `liste = [12, 7, 25, 7, 3]` / `print(liste.index(7), liste.count(7))` → `1 2`.
- Sık yanlışlar: `2 2` ("index 0'dan sayar"), `1 1` ("count tüm tekrarları sayar"), `3 2` ("index ilk geçtiği yeri verir").
- Kabul: boşluklar atılarak karşılaştırılır (`12` olarak). Bu bir sorundur: `1 2` ile `12` aynı olur. Bu yüzden KC'de tek değer sorulmalı (`print(liste.index(7))`) ya da kök "aralarında bir boşluk bırakarak" demeli ve `norm` modu boşlukları korumalı (O7).
- İpucu: "İlk 7 hangi indekste?"

**Ö7.5 İç İçe Liste** [`nested_list`]: ÇS · U · Kazanım: 2 boyutlu listede satır ve sütun indeksini kullanır.
- Rastgele: 3×3 matris (1-9 karışık), i, j (negatif dahil) → 500+.
- Örnek: `m = [[4, 9, 2], [7, 5, 1], [8, 3, 6]]` / `print(m[2][0])` → `8`.
- Yanlışlar: `2` ("ilk indeks satırı, ikinci sütunu seçer; m[0][2] değil"), `7` ("indeksler 0'dan başlar"), `[8, 3, 6]` ("ikinci indeks satırdan bir eleman seçer").
- İpucu: "Önce m[2] satırını bul, sonra o satırın [0] elemanını."

**Ö7.6 Listeyi Kopyalama** [`list_copy`]: ÇS · An · Kazanım: takma ad (alias) ile kopya farkını ayırt eder.
- Rastgele: kopyalama yolu (`b = a`, `b = a[:]`, `b = a.copy()`, `b = list(a)`), değişiklik (append, `b[0] = ...`) → 100+.
- Örnek: `a = [1, 2, 3]` / `b = a[:]` / `b.append(9)` / `print(a)` → `[1, 2, 3]`.
- Yanlışlar: `[1, 2, 3, 9]` ("`[:]` yeni bir liste oluşturur; a etkilenmez"); diğer ikisi hesaplanır.
- Not: Mevcut `aliasing` (`u07:146`) yalnızca `b = a` durumunu soruyor; bu öneri onu dengeler, çünkü cevap kopyalama yoluna göre değişir.
- İpucu: "b ile a aynı liste mi, yoksa yeni bir liste mi?"

**Ö7.7 max() Kullanmadan En Büyük (Kod Yazma)** [`write_max_loop`]: KY · O · Kazanım: döngü ve karşılaştırmayla en büyüğü bulur.
- Rastgele: liste (5-7 sayı, negatifler dahil), değişken adı → 1000+.
- Kök: "`sayilar = [...]` listesindeki en büyük sayıyı **max() ve sort() kullanmadan** bulup yazdıran kodu yazınız."
- Örnek çözüm: `en_buyuk = sayilar[0]` / `for s in sayilar:` / `if s > en_buyuk:` / `en_buyuk = s` / `print(en_buyuk)`
- Çıktı ölçütleri: `set sayilar` ∈ {verilen liste, `[-5, -2, -9]`, `[7]`}. Tüm sayılar negatif olan durum zorunludur; `en_buyuk = 0` ile başlayan hatalı çözümü yakalar. Bu durumda mesaj: "Başlangıç değeri 0 olursa tüm sayılar negatifken yanlış sonuç çıkar; listenin ilk elemanıyla başla."
- `forbid`: `max`, `sorted`, `.sort`.
- AST ölçütleri: `For` liste üzerinde; gövdede `If` + `Compare(>)` ve en büyük değişkenine atama var. Başlangıç değeri `sayilar[0]` olmalı (0 ya da başka bir sabit ise yukarıdaki mesaj verilir). Döngüden sonra print var.
- İpucu: "İlk elemanı en büyük kabul et, sonra her elemanla karşılaştır."

**Ö7.8 Çift Sayıları Ayıkla (Kod Yazma)** [`write_filter_even`]: KY · O · Kazanım: koşullu eklemeyle yeni liste oluşturur.
- Rastgele: liste (6-8 sayı), filtre (çift, 10'dan büyük, 3'e bölünen) → 1000+.
- Kök: "`sayilar` listesindeki **çift** sayılardan `ciftler` adında yeni bir liste oluşturup yazdırın."
- Örnek çözüm: `ciftler = []` / `for s in sayilar:` / `if s % 2 == 0:` / `ciftler.append(s)` / `print(ciftler)`
- Çıktı ölçütleri: Yazdırılan liste beklenen listeye eşit olmalı (`ast.literal_eval` ile). `set sayilar` ile en az iki durum denenir. Liste üreteci (`[s for s in sayilar if s % 2 == 0]`) kabul edilir.
- AST ölçütleri: Kabul edilen iki yapı var. (a) `ciftler = []`; `For`; gövdede `If` ile `% 2 == 0` (ya da eşdeğer) ve `ciftler.append(s)`; ardından `print(ciftler)`. (b) `ciftler = [s for s in sayilar if ...]` ve `print(ciftler)`. Orijinal listeden `remove` ile silmek reddedilir: "Yeni liste istendi; ayrıca döngüde silme eleman atlatır."
- İpucu: "Boş listeyle başla; koşulu sağlayanı append ile ekle."

---

### Ünite 8: Sözlük, Demet ve Küme (8 öneri)

**Ö8.1 `in` Sözlükte Neye Bakar? (hesaplanan D/Y)** [`dict_in_claim`]: D/Y · A · Kazanım: `in` operatörünün sözlükte anahtarlara baktığını bilir.
- Rastgele: sözlük (`_grades`), aranan (bir anahtar, bir değer ya da olmayan bir ad) × iddia → 500+.
- Örnek: `notlar = {"Ali": 80, "Can": 65}` için iddia "`print(80 in notlar)` ekrana True yazar." Cevap: Yanlış ("in anahtarlara bakar; değerlerde aramak için `80 in notlar.values()`").
- İpucu: "in sözlüğün anahtarlarına mı, değerlerine mi bakar?"

**Ö8.2 keys / values / items** [`dict_view_blank`]: BD · U/An · Kazanım: çıktıya göre doğru sözlük görünümünü seçer.
- Rastgele: sözlük, istenen çıktı (yalnızca adlar, yalnızca notlar, "ad: not" satırları) → 500+.
- Örnek: `for x in notlar.____():` / `print(x)`, çıktıda yalnızca notlar → kabul `values`. Değişke: `for ad, puan in notlar.____():` → `items`.
- Yaygın yanlışlar: `keys` ("anahtarları, yani adları verir"), `items` (tek değişkenle kullanılırsa demet yazdırır: `('Ali', 80)`).
- İpucu: "Çıktıda adlar mı, notlar mı, ikisi birden mi var?"

**Ö8.3 Sözlükle Sayma** [`dict_count`]: KC · U/An · Kazanım: `get(k, 0) + 1` sayma kalıbını izler.
- Rastgele: kelime (12), sorulan harf → 100+.
- Örnek: `sayim = {}` / `for h in "programlama":` / `sayim[h] = sayim.get(h, 0) + 1` / `print(sayim["a"])` → `3`.
- Sık yanlışlar: `2`, `1` ("get, harf daha önce görüldüyse eski sayıyı döndürür; her seferinde 1 eklenir").
- Ek değişke: `print(len(sayim))` → `7` (farklı harf sayısı). Sık yanlış `11` ("aynı anahtar ikinci kez eklenmez, güncellenir").
- İpucu: "Her harf ilk görüldüğünde 1, sonra her görüldüğünde bir fazlası olur."

**Ö8.4 Yinelenen Anahtar** [`dict_dup_key`]: ÇS · A/U · Kazanım: sözlükte anahtarların tekil olduğunu bilir.
- Rastgele: anahtarlar, değerler, yinelenen anahtarın konumu → 300+.
- Örnek: `d = {"a": 1, "b": 2, "a": 3}` / `print(len(d), d["a"])` → `2 3`.
- Yanlışlar: `3 3` ("aynı anahtar iki kez bulunamaz"), `2 1` ("sonraki değer öncekinin üstüne yazılır"), `Hata verir (KeyError)` ("yinelenen anahtar hata vermez; sonuncusu geçerlidir").
- İpucu: "Bir sözlükte aynı anahtar iki kez bulunabilir mi?"

**Ö8.5 Sözlük Boyutu (dict_update'in yerine)** [`dict_size_ops`]: KC · U · Kazanım: ekleme, güncelleme ve silme sonrası boyutu hesaplar.
- Rastgele: başlangıç boyutu (2-5), işlem dizisi (2-4 işlem: var olana atama, yeni anahtara atama, `del`, `pop`) → 1000+. Bu şablon K5'teki sabit cevap sorununu çözer.
- Örnek: `d` 3 elemanlı; `d["Ali"] = 90` (var), `d["Ece"] = 70` (yeni), `del d["Can"]`, ardından `print(len(d))` → `3`.
- Sık yanlışlar: Her işlemi "ekleme" saymak, `del`'i atlamak.
- İpucu: "Hangi atama yeni anahtar ekler, hangisi günceller?"

**Ö8.6 Küme Davranışı (hesaplanan D/Y)** [`set_claim`]: D/Y · A · Kazanım: kümenin tekrarsız ve sırasız olduğunu bilir; tek elemanlı demeti tanır.
- Rastgele: değişkeler:
  - (a) `s = {3, 1, 3, 2}` / `print(len(s))` → iddia `4` (Yanlış: tekrar sayılmaz).
  - (b) `s.add(x)` (x kümede var ya da yok) → yeni uzunluk.
  - (c) `t = (5)` / `print(type(t))` → iddia `<class 'tuple'>` (Yanlış: parantez tek başına demet yapmaz, `(5,)` gerekir).
  
  → 200+.
- İpucu: "Kümede aynı eleman kaç kez bulunur? Tek elemanlı demet nasıl yazılır?"

**Ö8.7 En Yüksek Notlu Öğrenci (Kod Yazma)** [`write_dict_max`]: KY · O · Kazanım: sözlüğü items() ile dolaşıp en büyük değerin anahtarını bulur.
- Rastgele: 3-5 öğrenci, notlar (en yüksek not tekil olacak biçimde) → 1000+.
- Kök: "`notlar` sözlüğünde en yüksek notu alan öğrencinin **adını** yazdıran kodu yazınız."
- Örnek çözüm: `en_iyi = ""` / `en_yuksek = -1` / `for ad, puan in notlar.items():` / `if puan > en_yuksek:` / `en_yuksek = puan` / `en_iyi = ad` / `print(en_iyi)`
- Çıktı ölçütleri: Çıktı (Türkçe katlamayla) beklenen ada eşit. `set notlar` ile ikinci bir sözlük denenir. `max(notlar, key=notlar.get)` kabul edilir (forbid yok).
- AST ölçütleri: `For` + `items()` (ya da anahtarlar üzerinde dönüp `notlar[ad]` okuma). Gövdede `If` + `Compare(>)`, ardından ad değişkenine atama; döngüden sonra print. Notun kendisini yazdırmak (`print(en_yuksek)`) reddedilir: "Notu değil, öğrencinin adını yazdır."
- İpucu: "Hem en yüksek notu hem de o notun sahibini aklında tut."

**Ö8.8 Kelime Frekansı (Kod Yazma)** [`write_freq`]: KY · O · Kazanım: listedeki öğeleri sözlükle sayar.
- Rastgele: meyve listesi (6-9 eleman, tekrarlı), sorulan meyve → 1000+.
- Kök: "`meyveler` listesindeki her meyvenin kaç kez geçtiğini `sayim` sözlüğünde tutun ve `sayim` sözlüğünü yazdırın."
- Örnek çözüm: `sayim = {}` / `for m in meyveler:` / `sayim[m] = sayim.get(m, 0) + 1` / `print(sayim)`
- Çıktı ölçütleri: Yazdırılan sözlük `ast.literal_eval` ile beklenen sözlüğe eşit (anahtar sırası önemsiz). `if m in sayim: ... else: ...` biçimi kabul edilir. `collections.Counter` kabul edilmez (öğretmen ayarına bağlı), çünkü import beyaz listede yok.
- AST ölçütleri: `sayim = {}`; `For`; gövdede `sayim[m] = sayim.get(m, 0) + 1` ya da `If`/`In` + `+= 1` ve `= 1` dalları; döngüden sonra print.
- İpucu: "Meyve sözlükte yoksa 1 ile başlat, varsa 1 artır."

---

### Ünite 9: Fonksiyonlar ve Modüller (9 öneri)

**Ö9.1 print mi return mü? (hesaplanan D/Y)** [`print_return_claim`]: D/Y · An · Kazanım: return ile print farkının çıktıya etkisini izler.
- Rastgele: fonksiyonun print ya da return kullanması, çağrının print içinde olup olmaması, sayılar → 300+.
- Örnek: `def iki_kat(x): print(x * 2)` / `sonuc = iki_kat(4) + 1` için iddia "ekrana 9 yazar". Cevap: Yanlış (önce 8 yazılır, sonra `None + 1` TypeError verir).
- Neden metinleri: "Fonksiyon değer döndürmüyor; None + 1 hata verir."
- Doğrulama: `tf_output` hata durumunu da desteklemeli; iddia "hata verir (TypeError)" biçiminde olabilir.
- İpucu: "Fonksiyon bir değer döndürüyor mu, yoksa yalnızca yazıyor mu?"

**Ö9.2 Çağrıyı Tamamla** [`call_args_blank`]: BD · U/An · Kazanım: konumsal ve isimli argümanlarla çağrı kurar.
- Rastgele: fonksiyon (`us(taban, kuvvet=2)`, `alan(en, boy)`, `selam(ad, unvan="")`), hedef çıktı → 100+.
- Örnek: `def us(taban, kuvvet=2): return taban ** kuvvet` / `print(us(____))`, beklenen `27`.
- Kabul (ast + `blank_output` doğrulaması): `3, 3`, `3, kuvvet=3`, `taban=3, kuvvet=3`, `kuvvet=3, taban=3`. Kabul listesi şablonda elle yazılmamalı: küçük bir aday kümesi (taban 1-5, kuvvet 1-4, konumsal/isimli biçimler) koda yerleştirilip çalıştırılarak üretilmeli.
- Yaygın yanlışlar: `3` ("varsayılan kuvvet 2'dir: 9"), `9, 3` ("9 ** 3 = 729"), `27`.
- İpucu: "Hangi taban hangi kuvvetle 27 eder?"

**Ö9.3 global Anahtar Sözcüğü** [`global_blank`]: BD · A · Kazanım: fonksiyon içinden global değişkeni değiştirmenin yolunu bilir.
- Rastgele: değişken adı (`sayac`, `puan`, `toplam`), artış (1-5), çağrı sayısı (2-4) → 36+.
- Örnek: `sayac = 0` / `def artir():` / `____ sayac` / `sayac += 1` / `artir()` / `artir()` / `print(sayac)`, beklenen `2`.
- Kabul (text): `global`.
- Yaygın yanlışlar: `return` ("return değer döndürür; dışarıdaki sayacı bağlamaz"), `def`, `local`.
- İpucu: "Fonksiyon içinden dışarıdaki değişkeni değiştirmek için Python'a ne söylemelisin?"
- Ek D/Y (aynı şablonda değil, Ö9.1 havuzunda): "`global` satırı silinirse kod UnboundLocalError verir." (Doğru)

**Ö9.4 İsimli Argümanlar** [`keyword_args`]: KC · U · Kazanım: isimli argümanların sırayı değiştirdiğini bilir.
- Rastgele: a, b (bölünen 20-60, bölen 2-9), işlem (`//`, `-`, `%`) → 500+.
- Örnek: `def bolme(a, b): return a // b` / `print(bolme(b=4, a=30))` → `7`.
- Sık yanlışlar: `0` ("isimli argümanda sıra önemsizdir; a = 30, b = 4"), `7.5` ("`//` tam bölmedir").
- İpucu: "b=4, a=30: hangi değer hangi parametreye gidiyor?"

**Ö9.5 Fonksiyon İçinde Fonksiyon Çağırma** [`func_compose`]: KC · U · Kazanım: iç içe fonksiyon çağrılarını izler.
- Rastgele: f ve g'nin işlemleri, sabitler, çağrı değeri → 1000+.
- Örnek: `def f(x): return x + 3` / `def g(x): return f(x) * 2` / `print(g(5))` → `16`.
- Sık yanlışlar: `13` ("önce f(5) = 8 hesaplanır, sonra 2 ile çarpılır; 5 * 2 + 3 değil"), `10`.
- İpucu: "g(5) içinde önce f(5) hesaplanır."

**Ö9.6 Hangi Fonksiyon Doğru?** [`which_function`]: ÇS · D · Kazanım: fonksiyon tanımlarını doğruluk açısından değerlendirir.
- Rastgele: amaç (mutlak değer, çift mi?, iki sayının büyüğü), adlar → 30+.
- Kök: "Hangi fonksiyon verilen sayının mutlak değerini **döndürür**?"
- Doğru: `def mutlak(x):` / `if x < 0:` / `return -x` / `return x`.
- Yanlışlar: `print` kullanan sürüm ("ekrana yazar ama None döndürür"); her zaman `-x` döndüren ("pozitif sayıyı negatife çevirir"); `if x < 0: x = -x` yazıp return'ü unutan ("return yok; None döner").
- Doğrulama: `verify="func_one"`. Test her seçeneği x ∈ {-5, 0, 7} ile çağırıp `abs` ile karşılaştırır; yalnızca doğru seçenek geçmeli.
- İpucu: "Her seçeneği -5 ve 7 ile dene; sonucu yazıyor mu, döndürüyor mu?"

**Ö9.7 Çift mi? Fonksiyonu (Kod Yazma)** [`write_is_even`]: KY · O · Kazanım: bool döndüren fonksiyon yazar.
- Rastgele: fonksiyon adı (`cift_mi`, `cift`, `cift_sayi_mi`), yüklem (çift, pozitif, 5'e bölünür) → 9+. Çeşitlilik için parametre adı ve örnek çağrı da rastgele seçilir (≥27).
- Kök: "`cift_mi` adında, bir sayı alıp sayı çiftse `True`, değilse `False` **döndüren** fonksiyonu yazınız."
- Örnek çözüm: `def cift_mi(n):` / `return n % 2 == 0`
- Çıktı ölçütleri (`call`): `cift_mi(4)` → True, `cift_mi(7)` → False, `cift_mi(0)` → True, `cift_mi(-3)` → False. Dönüş değeri `is True`/`is False` ile değil, `== True` ile karşılaştırılır; ancak 0/1 döndüren çözüm mesajla reddedilir: "True ya da False döndür."
- AST ölçütleri: `FunctionDef` adı ve tek parametresi var. Ya `return <yüklem>` ya da `if <yüklem>: return True` / `else: return False` (ya da else'siz ikinci return) biçiminde. Yüklem `% 2 == 0` ya da eşdeğeri olmalı (Ö5.6'daki liste). Print kullanılırsa: "Sonucu yazdırma, return ile döndür."
- İpucu: "`n % 2 == 0` ifadesi zaten True ya da False verir."

**Ö9.8 Liste Ortalaması Fonksiyonu (Kod Yazma)** [`write_mean_func`]: KY · O · Kazanım: liste parametresi alan ve hesap döndüren fonksiyon yazar.
- Rastgele: fonksiyon adı, örnek liste → 100+.
- Kök: "`ortalama` adında, bir sayı listesi alıp ortalamasını döndüren fonksiyon yazınız (liste boş olmayacak)."
- Örnek çözüm: `def ortalama(liste):` / `return sum(liste) / len(liste)`
- Çıktı ölçütleri (`call`): `[70, 80, 90]` → 80, `[5]` → 5, `[1, 2]` → 1.5 (±1e-9). Döngüyle toplayan çözüm kabul edilir.
- AST ölçütleri: `FunctionDef` + tek parametre + `return`. Dönüş ifadesi (a) `sum(p) / len(p)` ya da (b) döngüde biriktirilen toplam bölü `len(p)` (ya da sayaç) biçiminde. `//` kullanılırsa mesaj: "`//` kesir kısmını atar; ortalama için `/` kullan."
- İpucu: "Toplamı eleman sayısına böl."

**Ö9.9 Faktöriyel (Kod Yazma)** [`write_factorial`]: KY · O · Kazanım: döngüyle ya da özyinelemeyle faktöriyel hesaplar.
- Rastgele: fonksiyon adı (`faktoriyel`, `fakt`), istenen yöntem ("döngüyle", "özyinelemeyle" ya da serbest) → 6. Çeşitlilik için örnek değer de rastgele seçilir (3-8) → 36.
- Kök: "`faktoriyel(n)` fonksiyonunu yazınız; `faktoriyel(5)` 120 döndürmeli, `faktoriyel(0)` 1 döndürmeli."
- Çıktı ölçütleri (`call`): n ∈ {0, 1, 5, 7}; özyineleme derinliği sınırı 50. "Özyinelemeyle" şartı varsa `require`: gövdede fonksiyonun kendi adına `Call` bulunmalı.
- AST ölçütleri: (a) Döngü: `sonuc = 1`, `range(1, n + 1)` ya da `range(2, n + 1)`, `sonuc *= i`, `return sonuc`. (b) Özyineleme: `if n <= 1` (ya da `== 0`, `< 2`) → `return 1`; `return n * ad(n - 1)`. `math.factorial` kullanmak reddedilir: "Fonksiyonu kendin yaz."
- İpucu: "0! = 1; n! = n × (n-1)!."

---

### Ünite 10: Hata Yönetimi (8 öneri)

**Ö10.1 Hata Türü İddiası (hesaplanan D/Y)** [`error_claim`]: D/Y · A/U · Kazanım: kodun hangi hatayı vereceğini öngörür.
- Rastgele: parametreli kod parçaları (Y6: liste uzunluğu, indeks, anahtar adları, sayılar) × iddia edilen hata (gerçek hata ya da `ERROR_CAUSES`'tan bir başkası) → 500+.
- Örnek: `d = {"elma": 3}` / `print(d["armut"])` için iddia "IndexError verir". Cevap: Yanlış ("Sözlükte olmayan anahtar KeyError verir").
- İpucu: "Hata hangi işlemde oluşuyor: indeks mi, anahtar mı, dönüşüm mü?"

**Ö10.2 Doğru except Türü** [`except_blank`]: BD · An · Kazanım: oluşacak hataya uygun except türünü yazar.
- Rastgele: hata kaynağı (dönüşüm, sıfıra bölme, indeks, anahtar), değerler → 200+.
- Örnek: `try:` / `sayi = int("on iki")` / `except ____:` / `print("Geçersiz")`, beklenen `Geçersiz`.
- Kabul (text): `ValueError`. Kök şöyle olmalı: "Yalnızca **bu hatayı** yakalayacak hata türünü yazınız."
- Yaygın yanlışlar: `Exception` ("Bu da yakalar, ama her hatayı yakalar; soru bu hataya özel türü istiyor"; çıktı aynı olduğu için `blank_output` doğrulamasına özel istisna gerekir); `TypeError` ("Tip doğru (str), değer uygun değil"); `valueerror` ("Hata adları büyük/küçük harfe duyarlıdır").
- İpucu: "int() uygun olmayan bir metin alınca hangi hatayı verir?"

**Ö10.3 Birden Fazla except** [`multi_except`]: KC · U/An · Kazanım: ilk hatada try'ın kesildiğini ve eşleşen except'in çalıştığını izler.
- Rastgele: indeks (geçerli ya da geçersiz), bölen (0 ya da sayı), sıra (önce indeks ya da önce bölme) → 100+.
- Örnek:
  ```python
  liste = [1, 2, 3]
  try:
      print(liste[1], end=" ")
      print(10 / 0, end=" ")
  except IndexError:
      print("A", end=" ")
  except ZeroDivisionError:
      print("B", end=" ")
  finally:
      print("C")
  ```
  Cevap `2 B C`.
- Sık yanlışlar: `B C` ("ilk print hatadan önce çalışır"), `2 A B C` ("yalnızca eşleşen except çalışır"), `2 B` ("finally her zaman çalışır").
- Kabul: Boşluk normalleştirmesi yeterli (`2BC`). Bilgiler karışmaz, çünkü tüm parçalar tek karakter. Kök "aralarında boşlukla" demeli.
- İpucu: "Hata hangi satırda oluşuyor? O satırdan sonraki satırlar çalışır mı?"

**Ö10.4 Doğrulama Döngüsü** [`retry_loop`]: KC · An · Kazanım: hata yakalayan döngüde sayaç izler.
- Rastgele: girdi listesi (geçersiz girdiler "abc", "3.5", "x", "" ve bir geçerli sayı; geçerlinin konumu 1-4) → 200+.
- Örnek: `girdiler = ["abc", "3.5", "12", "x"]` / `hata = 0` / `for g in girdiler:` / `try:` / `n = int(g)` / `break` / `except ValueError:` / `hata += 1` / `print(hata)` → `2`.
- Sık yanlışlar: `3` ("break sonrası döngü biter; 'x' denenmez"), `1` ("int('3.5') de ValueError verir").
- İpucu: "Hangi girdide break çalışır?"

**Ö10.5 Hatanın Yayılması** [`error_propagation`]: ÇS · An · Kazanım: fonksiyonda yakalanmayan hatanın çağıran koddaki try ile yakalandığını bilir.
- Rastgele: fonksiyon içi hata türü, çağıranın except türü (eşleşen ya da eşleşmeyen) → 50+.
- Örnek: `def bol(a, b): return a / b` / `try:` / `print(bol(8, 0))` / `print("Devam")` / `except ZeroDivisionError:` / `print("Yakalandı")` / `print("Son")` → `Yakalandı\nSon`.
- Yanlışlar: `Hata verir (ZeroDivisionError)` ("Hata fonksiyondan çağırana iletilir ve oradaki try yakalar"), `Devam\nSon` ("hata oluşunca try'ın geri kalanı atlanır"), `Yakalandı\nDevam\nSon`.
- Eşleşmeyen except değişkesi (except ValueError) cevabı `Hata verir (...)` yapar. Bu değişke ayrı bir şablon olmalı (verify türü farklı).
- İpucu: "Fonksiyonda try yok; hata nereye gider?"

**Ö10.6 Hata Yönetimi Kavramları II (D/Y, sabit havuz)** [`concepts2`]: D/Y · A · Kazanım: `except ... as e`, except sırası ve `raise` kavramlarını bilir.
- Havuz (her biri `(metin, neden)`); ≥10 doğru + ≥10 yanlış önerilir. Örnekler:
  - D: "`except ValueError as e:` satırında `e`, yakalanan hata nesnesidir; `print(e)` hata mesajını yazar."
  - D: "Aynı try için yazılan except blokları yukarıdan aşağı denenir; ilk eşleşen çalışır."
  - Y: "`except Exception:` bloğu daha önce yazılırsa, sonraki `except ValueError:` bloğu yine de ValueError'ı yakalar." Neden: "Exception tüm hataları kapsar ve önce eşleşir; sonraki blok hiç çalışmaz."
  - Y: "finally bloğu yalnızca hata oluştuğunda çalışır." Neden: "finally her durumda çalışır."
- O4 kuralına uyun: mutlak sözcükleri iki tarafa dengeli dağıtın.

**Ö10.7 Güvenli Bölme Fonksiyonu (Kod Yazma)** [`write_safe_div`]: KY · O · Kazanım: try/except ile hatayı yakalayıp anlamlı değer döndürür.
- Rastgele: fonksiyon adı, hata dönüş değeri (`None`, `0`, `"Tanımsız"`) → 9+. Örnek çağrılarla çeşitlilik ≥27.
- Kök: "`guvenli_bol(a, b)` fonksiyonunu yazınız: a / b sonucunu döndürsün; b sıfırsa hata vermek yerine `None` döndürsün. **try / except kullanınız.**"
- Örnek çözüm: `def guvenli_bol(a, b):` / `try:` / `return a / b` / `except ZeroDivisionError:` / `return None`
- Çıktı ölçütleri (`call`): (8, 2) → 4.0, (5, 0) → None, (0, 3) → 0.0. `require: ["Try"]`; `if b == 0` ile çözülmüşse mesaj: "Soru try / except kullanmanı istiyor" (öğretmen ayarıyla kabul edilebilir).
- AST ölçütleri: `FunctionDef` (2 parametre); gövdede `Try`; handler türü `ZeroDivisionError`. `Exception` ya da çıplak `except:` kabul edilir, ancak not eklenir: "Kabul edildi; ama yalnızca beklenen hatayı yakalamak daha iyidir." try içinde `return a / b`; handler'da istenen değerin `return`'ü var.
- İpucu: "Hata çıkabilecek satırı try içine al."

**Ö10.8 Geçerli Girdiyi Yakala (Kod Yazma)** [`write_parse_guard`]: KY · O · Kazanım: dönüşüm hatasını yakalayıp program akışını sürdürür.
- Rastgele: değişken adı, geçersiz ve geçerli örnek değerler → 100+.
- Kök: "`veri = "12"` satırıyla başlayan kod yazınız: veri tam sayıya çevrilebiliyorsa sayının 2 katını, çevrilemiyorsa `Geçersiz` yazdırsın."
- Çıktı ölçütleri: `set veri` ∈ {"12", "abc", "3.5", "-4"} → `24`, `Geçersiz`, `Geçersiz`, `-8`. Metin karşılaştırması Türkçe katlamayla yapılır.
- AST ölçütleri: `Try` içinde `int(veri)`; handler `ValueError` (ya da `Exception`, notla); try ya da else bloğunda `print(<x> * 2)`; handler'da "Geçersiz" metnini içeren print. `veri.isdigit()` ile çözüm `-4` durumunda yanlış sonuç verir; yorumlayıcı bunu yakalar, AST denetleyicisi `require: ["Try"]` ile reddeder.
- İpucu: "int() hata verirse except bloğu çalışır."

---

### Ünite 11: Nesne Yönelimli Programlama (8 öneri)

**Ö11.1 Sınıf mı Nesne mi? (hesaplanan D/Y)** [`attr_shadow_claim`]: D/Y · An · Kazanım: örnek niteliğinin sınıf niteliğini gölgelediğini bilir.
- Rastgele: sınıf adı, sınıf değişkeni değeri, hangi nesneye atama yapıldığı, yazdırılan ifade → 300+.
- Örnek: `class A: x = 1` / `a = A()` / `b = A()` / `a.x = 5` / `print(b.x)` için iddia "ekrana 5 yazar". Cevap: Yanlış ("`a.x = 5` yalnızca a nesnesine özel bir x oluşturur; b ve A sınıfı etkilenmez").
- İpucu: "a.x = 5 sınıfın x'ini mi değiştirir, yoksa a'ya yeni bir özellik mi ekler?"

**Ö11.2 self Boşlukları** [`self_blank`]: BD · H/A · Kazanım: metot tanımında ve nitelik atamasında self'i kullanır.
- Rastgele: sınıf (`Ogrenci`, `Kitap`, `Araba`), nitelikler, değerler → 100+.
- Örnek: `class Kitap:` / `def __init__(____, ad, sayfa):` / `____.ad = ad` / `self.sayfa = sayfa` / `k = Kitap("Simyacı", 184)` / `print(k.ad)`, beklenen `Simyacı`.
- Kabul (text): her iki boşluk için `self`. Not: Teknik olarak ilk parametre başka bir ad da olabilir; iki boşluk birlikte tutarlı bir adla (`bu`, `bu`) doldurulursa kod çalışır. Bu, bağımlı boşluk desteği varsa `accept_sets` ile kabul edilmeli, yoksa kök "Python geleneğine uygun adı yazınız" demeli.
- Yaygın yanlışlar: `Kitap` ("Sınıf adı değil, oluşturulan nesneyi temsil eden parametre"), `this` ("Python'da `this` değil `self` kullanılır").
- İpucu: "Metodun ilk parametresi kimi temsil eder?"

**Ö11.3 super() ile Kalıtım** [`super_blank`]: BD · U · Kazanım: alt sınıfta üst sınıfın `__init__`'ini çağırır.
- Rastgele: sınıf çifti (Kisi/Ogrenci, Arac/Araba, Hayvan/Kedi), nitelikler → 100+.
- Örnek: `class Ogrenci(Kisi):` / `def __init__(self, ad, no):` / `____.__init__(ad)` / `self.no = no` / `o = Ogrenci("Ece", 42)` / `print(o.ad, o.no)`, beklenen `Ece 42`.
- Kabul (text): `super()`.
- Yaygın yanlışlar: `Kisi` ("`Kisi.__init__(ad)` çağrısı self'i iletmez; TypeError verir. Bu biçimde `Kisi.__init__(self, ad)` yazmak gerekir"), `self` ("`self.__init__` alt sınıfın kendi metodunu yeniden çağırır"), `super` ("parantez gerekir: `super()`").
- İpucu: "Üst sınıfa erişmek için hangi hazır fonksiyon kullanılır?"

**Ö11.4 Banka Hesabı** [`account_trace`]: KC · U/An · Kazanım: metot çağrılarıyla nesne durumunun değişimini izler.
- Rastgele: başlangıç bakiyesi, 3-4 işlem (yatırma, çekme; bazı çekmeler bakiyeyi aşar) → 1000+.
- Örnek: `Hesap(100)`, `yatir(50)`, `cek(200)` (yetersiz bakiye, yok sayılır), `cek(30)`, ardından `print(h.bakiye)` → `120`.
- Sık yanlışlar: `-80` ("cek, yetersiz bakiyede işlem yapmaz"), `150`, `100` ("metotlar self.bakiye'yi kalıcı olarak değiştirir").
- İpucu: "Her çağrıdan sonra bakiyeyi yaz; cek'teki koşula dikkat et."

**Ö11.5 isinstance ve Kalıtım** [`isinstance_check`]: ÇS · A/U · Kazanım: alt sınıf nesnesinin üst sınıfın da örneği olduğunu bilir.
- Rastgele: sınıf hiyerarşisi (2-3 düzey), sorgulanan çiftler (2 ifade → 4 birleşim; K4'teki öneriye uygun) → 50+.
- Örnek: `class Hayvan: pass` / `class Kedi(Hayvan): pass` / `k = Kedi()` / `print(isinstance(k, Hayvan), isinstance(Hayvan(), Kedi))` → `True False`.
- Yanlışlar: `True True` ("üst sınıf nesnesi alt sınıfın örneği değildir"), `False False`, `False True` (her biri neden metniyle).
- İpucu: "Her kedi bir hayvan mıdır? Her hayvan bir kedi midir?"

**Ö11.6 Nesne Listesi** [`object_list`]: KC · U · Kazanım: nesne listesinde döngüyle nitelik toplar.
- Rastgele: 3-4 ürün nesnesi (ad, fiyat), koşul (fiyat > eşik) → 1000+.
- Örnek: `urunler = [Urun("kalem", 15), Urun("defter", 40), Urun("silgi", 10)]` / `toplam = 0` / `for u in urunler:` / `if u.fiyat > 12:` / `toplam += u.fiyat` / `print(toplam)` → `55`.
- Sık yanlışlar: `65` ("koşul sağlanmayanlar eklenmez"), `3` ("nesne sayısı değil fiyatlar toplanıyor").
- İpucu: "Her nesnenin fiyatına koşulu uygula."

**Ö11.7 Dikdörtgen Sınıfı (Kod Yazma)** [`write_rect_class`]: KY · O · Kazanım: `__init__` ve değer döndüren metot içeren sınıf yazar.
- Rastgele: sınıf (`Dikdortgen`/`Kare`/`Daire`), metot (`alan`/`cevre`), test değerleri → 20+. Çeşitlilik ≥12 için metot adı ve nitelik adları (`en/boy`, `a/b`) da rastgele seçilir.
- Kök: "`Dikdortgen` adında bir sınıf yazınız: `__init__` metodu `en` ve `boy` değerlerini alıp nesnede saklasın; `alan()` metodu alanı **döndürsün**. (Örnek: `Dikdortgen(3, 4).alan()` → 12)"
- Örnek çözüm: `class Dikdortgen:` / `def __init__(self, en, boy):` / `self.en = en` / `self.boy = boy` / `def alan(self):` / `return self.en * self.boy`
- Çıktı ölçütleri (`call`): `Dikdortgen(3, 4).alan()` → 12, `(5, 5)` → 25, `(1, 7)` → 7. Ek olarak `d = Dikdortgen(2, 3); d.en = 10; d.alan()` → 30 test edilir. Bu, alanı `__init__`'te hesaplayıp saklayan çözümü yakalar; doğru bir yaklaşım değildir ama kabul edilip edilmeyeceği öğretmene bırakılabilir.
- AST ölçütleri: `ClassDef` adı tutar; içinde `__init__` (self + 2 parametre) ve `self.<x> = <param>` atamaları var; `alan(self)` metodu `return self.<a> * self.<b>` döndürüyor ve bu nitelikler `__init__`'te atanmış. Metot print ile yazıyorsa: "alan() değeri döndürmeli (return)." Metotta `self` unutulmuşsa: "Metodun ilk parametresi self olmalı."
- İpucu: "Özellikleri self ile sakla; alan() metodunda self.en ve self.boy'u kullan."

**Ö11.8 Sayaç Sınıfı (Kod Yazma)** [`write_counter_class`]: KY · O · Kazanım: nesne durumunu değiştiren metotlar yazar.
- Rastgele: sınıf adı (`Sayac`, `Tiklayici`), metotlar (`arttir`/`azalt`/`sifirla`), başlangıç değeri (0 ya da parametreli) → 12+. Çeşitlilik için örnek çağrı dizisi de rastgele seçilir.
- Kök: "`Sayac` sınıfı yazınız: nesne oluşturulduğunda `deger` 0 olsun; `arttir()` metodu değeri 1 artırsın; `sifirla()` metodu 0 yapsın."
- Çıktı ölçütleri (`call` dizisi): `s = Sayac(); s.arttir(); s.arttir(); s.deger` → 2; `s.sifirla(); s.deger` → 0. İki ayrı nesnenin bağımsızlığı da test edilir (sınıf değişkeni kullanan hatalı çözümü yakalar). Bu durumda mesaj: "deger her nesneye ait olmalı; self.deger kullan."
- AST ölçütleri: `__init__` içinde `self.deger = 0`; `arttir` içinde `self.deger += 1` (ya da `= self.deger + 1`); `sifirla` içinde `self.deger = 0`. `Sayac.deger` gibi sınıf değişkeni kullanımı reddedilir.
- İpucu: "Değer her nesneye özel olmalı: self.deger."

---

### 3.12 Önerilen yeni şablon sayıları

| Ünite | D/Y | BD | KC | KY | ÇS | Toplam yeni | Mevcut | Sonra |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 2 | 1 | 2 | 1 | 7 | 8 | 15 |
| 2 | 1 | 2 | 2 | 2 | 0 | 7 | 8 | 15 |
| 3 | 1 | 1 | 1 | 2 | 2 | 7 | 6 | 13 |
| 4 | 2 | 2 | 1 | 2 | 1 | 8 | 8 | 16 |
| 5 | 1 | 1 | 1 | 2 | 3 | 8 | 5 | 13 |
| 6 | 1 | 2 | 2 | 2 | 1 | 8 | 7 | 15 |
| 7 | 1 | 2 | 1 | 2 | 2 | 8 | 8 | 16 |
| 8 | 2 | 1 | 2 | 2 | 1 | 8 | 7 | 15 |
| 9 | 1 | 2 | 2 | 3 | 1 | 9 | 9 | 18 |
| 10 | 2 | 1 | 2 | 2 | 1 | 8 | 4 | 12 |
| 11 | 1 | 2 | 2 | 2 | 1 | 8 | 5 | 13 |
| **Toplam** | **14** | **18** | **17** | **23** | **14** | **86** | **75** | **161** |

Uygulama sırası önerisi: (1) K1-K5 ve Y1 düzeltmeleri (puanlama adaleti). (2) `tf_claim` ve `blank_output` doğrulama altyapısı. (3) D/Y ve BD şablonları (altyapı hazır olunca hızlı yazılır). (4) KC şablonları. (5) Yorumlayıcı kararı. (6) KY şablonları. Yorumlayıcı reddedilirse KY'ler AST ölçütleriyle ve her denetleyici için 6+6 test cevabıyla yazılmalı.

---

## 4. Yazım kılavuzu (yazar ajanlar için)

### 4.1 Dil ve biçim

1. **Türkçe doğru yazılır.** Kök, açıklama, ipucu ve ekrana yazdırılan metinlerde Türkçe karakter kullanılır ("Geçersiz", "Çift", "Başarılı"). Değişken, fonksiyon ve sınıf adları ASCII yazılır (`ogrenci_no`, `Ogrenci`, `sayac`); bu Python geleneğidir. Kod içindeki metin değerleri Türkçe olabilir (`"Gelişim"`).
2. **Kök bir soru ya da açık bir yönergedir** ve tek bir şey sorar: "Aşağıdaki kodun ekran çıktısı ne olur?", "Kod çalıştıktan sonra `x` değişkeninin değeri kaçtır?", "Boşluğa gelmesi gereken ifadeyi yazınız." Kökte cevabı ele veren sözcük bulunmaz.
3. **Olumsuz kök** ("hangisi ... **değildir**/**vermez**") yalnızca gerektiğinde kullanılır ve olumsuz sözcük `<strong>` ile vurgulanır. Çift olumsuz ("hangisi hata vermez değildir") yasaktır.
4. **HTML güvenliği:** Köke ve açıklamalara gömülen her değer `e()` ile kaçışlanır; boşluk görünürlüğü önemliyse `shown()` kullanılır. Kod parçaları `<code>` içinde verilir.
5. **Ses ve ton:** Açıklamalar öğrenciyi suçlamaz, ikinci tekil şahısla ve yanılgıyı adlandırarak yazılır: "Bitiş değerini de dahil ettin; range bitişi üretmez." "Yanlış!" gibi ifadeler kullanılmaz.
6. **Uzunluk:** Kök en fazla 2 cümle; kod Başlangıç ünitelerinde en fazla 8 satır, Orta'da 12, İleri'de 16. İpucu tek cümle ve soru biçiminde. Açıklama 1-3 cümle.

### 4.2 Rastgeleleştirme ve çeşitlilik

7. **Çeşitlilik ≥ 30** hedeflenir (test sınırı 12). En az iki bağımsız eksen rastgeleleştirilir: değerler, adlar, işlem ya da değişke.
8. **Doğru cevap da değişmeli.** 500 üretimde en sık cevap %40'ı geçmemeli. Hata cevaplı şablonlarda hatasız değişkeler de bulunmalı (K5).
9. **Çakışmaları üretimde engelleyin.** Hesaplanan yanlışların doğru cevapla ya da birbiriyle aynı çıktığı değerleri `while` ile yeniden seçin (ör. a = b, n = 3, `2*2 == 2**2`). Dolgu şık oranı %5'i geçmemeli (Y1).
10. **Kayan nokta:** Ondalık çıktılar ya kısa ve kesin olmalı (`.5`, `.25`) ya da `round` ile sınırlanmalı. Yuvarlama sorularında kesilen basamak 5 ve ardından 0 olan değerler üretilmemeli (Y4).
11. **input() kullanan kodlarda istem metni kullanmayın** (`input()` boş parantezle). Test çalıştırıcısı istem metnini çıktıya yazmaz, ama gerçek ekranda görünür; bu durum öğrenciyle cevap anahtarını çelişkiye düşürür. Klavye girdisi `stdin=` ile verilir ve kökte açıkça yazılır ("kullanıcı **15** yazıp Enter'a basıyor").

### 4.3 Çoktan seçmeli

12. **Dört şık; hepsi makul.** Her yanlış şık adı konmuş bir yanılgıya karşılık gelir ve `Wrong(değer, neden)` ile yazılır. "None", "[]" ve ifadenin bir parçası gibi şıklar yalnızca gerçek bir yanılgıyı temsil ediyorsa kullanılır (ör. `sort()` sonucunda `None`).
13. **İkili cevap tuzağı:** Doğru cevap yalnızca True/False olabiliyorsa ÇS yazılmaz. Ya iki ifade birden yazdırılır (4 birleşim) ya da D/Y kullanılır (K4).
14. **Şıklar biçimce benzer olmalı:** Uzunluk, satır sayısı ve gösterim tarzı benzer olmalı. Doğru şık en uzun ya da en "ayrıntılı" şık olarak öne çıkmamalı. Liste çıktılarında Python gösterimi kullanılır (`['a', 'b']`, tek tırnak).
15. **"Hata verir (X)" şıkkı** yalnızca öğrencinin gerçekten hata bekleyebileceği bir durumda yer alır. Bankada hata şıkkının doğru olduğu maddelerin oranı %20-25 civarında tutulur.
16. **Seçenekleri kod olan ÇS** (`output_one`, `predicate_one`, `func_one`) Analiz ve Değerlendirme düzeyini ölçmenin ana aracıdır. Her ünitede en az bir tane bulunmalı.

### 4.4 Doğru-yanlış

17. Her ifade **tek bir** iddia içerir; "ve" ile iki iddia bağlanmaz.
18. Mutlak sözcükler ("her zaman", "asla", "yalnızca") doğru ve yanlış ifadelerde **dengeli** kullanılır (O4).
19. Yanlış ifade, yaygın bir yanılgının doğrudan dile getirilişidir. Öğrenci "Doğru" derse gösterilecek `neden` metni yanılgıyı düzeltir.
20. Mümkünse **hesaplanan D/Y** (`tf_claim`) yazılır; sabit havuzlu D/Y'lerde en az 10 doğru ve 10 yanlış ifade bulunur.
21. Teknik olarak tartışmalı ifadelerden kaçının (O3). İfade 10. sınıf düzeyinde ve ders kitabının anlattığı kapsamda kesin doğru ya da kesin yanlış olmalı.

### 4.5 Kısa cevap

22. Cevap **tek satır, tek değer** olur (sayı, tek sözcük ya da kısa Python değeri). Çok değerli cevap gerekiyorsa kök ayırıcıyı açıkça söyler ve normalleştirme modu buna göre seçilir (O7).
23. Kabul edilecek eşdeğerler `accept` listesinde açıkça yazılır: ondalık virgül, baştaki ve sondaki tırnak, Unicode eksi, büyük/küçük harf (soru bunu ölçmüyorsa).
24. **Tip ölçen sorularda** (`5` ile `5.0`) sayısal eşdeğerlik **uygulanmaz**; ölçmeyen sorularda uygulanır. Bu ayrım şablonda `norm` alanıyla belirtilir.
25. En az iki `common_wrongs` yazılır ve her biri bir yanılgıyı adlandırır.

### 4.6 Boşluk doldurma

26. Her boşluk tek bir kavramı ölçer (operatör, anahtar sözcük, metot adı, argüman listesi, ifade). Bir satırın tamamı boşluk yapılmaz.
27. Beklenen çıktı ya da davranış kökte gösterilir; öğrenci neyi hedeflediğini bilmelidir.
28. **Kabul listesi çalıştırılarak üretilir ya da doğrulanır** (`blank_output`). Eşdeğer biçimler (`x * x` ile `x ** 2`, `2:5` ile `-4:-1`, isimli ve konumsal argüman) kabul edilir; mümkün olduğunda kaba kuvvetle hesaplanır.
29. İfade boşlukları `match: "ast"` ile, operatör ve anahtar sözcük boşlukları `match: "text"` ile karşılaştırılır. Python büyük/küçük harfe duyarlı olduğu için ad ve anahtar sözcüklerde harf büyüklüğü korunur ve buna ayrı bir `why` yazılır.
30. Çıktısı doğru olduğu hâlde kavramı atlayan cevaplar (sabit değer yazmak, `Exception` ile her hatayı yakalamak) ya kökte açıkça dışarıda bırakılır ya da kabul edilir; belirsiz bırakılmaz.

### 4.7 Kod yazma (açık uçlu)

31. **Kök, girdiyi, çıktıyı ve yapı şartlarını açıkça söyler.** Değişken ve fonksiyon adları `<code>` ile verilir; somut bir örnek girdi-çıktı çifti eklenir; şartlar ("döngü kullanarak", "max() kullanmadan", "return ile") kalın yazılır.
32. **Çıktıyı biçim yönünden esnek denetleyin:** Etiket metni, boşluk sayısı ve Türkçe karakter farkı ret nedeni olmamalı. Sayı soruluyorsa satırdaki sayı ayıklanır.
33. **Sabit cevabı yakalayın:** Girdi değişkeni farklı değerlerle denenir (`set`) ya da AST'de print argümanının sabit olmadığı denetlenir.
34. **Her denetleyici için en az 6 kabul ve 6 ret test cevabı yazın** (`tests/test_codecheck.py` biçiminde). Kabul listesinde öğrencilerin doğal varyasyonları bulunmalı: ara değişken, f-string, `print` içinde etiket, `while` ya da `for`, gereksiz ama zararsız satırlar. Ret listesinde `break`, `continue`, döngü değişkenine atama, sabit yazdırma, print ile return karışıklığı ve sınır hataları bulunmalı.
35. **Ret mesajları öğreticidir:** Neyin eksik olduğunu söyler, çözümü vermez ("Döngü 5'i yazdırmıyor; range bitişinin dahil olmadığını unutma").
36. **Seviye:** Başlangıç ünitelerinde tek kavram ve en fazla 6 satırlık çözüm; Orta ünitelerde en fazla 10 satır ve en fazla iki kavram (döngü + koşul gibi); İleri ünitede tek sınıf, en fazla iki metot.
37. Örnek çözüm (`answer`) en sade ve ders kitabı üslubuyla yazılır; ileri yapılar (lambda, `Counter`, üretici ifadeler) kullanılmaz.

### 4.8 Bloom ve ölçme dengesi

38. Her ünitede en az bir madde Analiz ya da Değerlendirme düzeyinde olmalı: eksik ya da hatalı satırı bulmak, istenen çıktıyı veren kodu seçmek, iki çözümü karşılaştırmak, çıktıdan geriye giderek kodu tamamlamak.
39. "Çıktı nedir?" maddeleri ünitenin %50'sini geçmemeli. Kök çeşitlendirilir: değişkenin son değeri, döngünün tur sayısı, ekrana kaç satır yazıldığı, hangi satırda hata oluştuğu.
40. Her şablon için `topic`, hedef kazanım ve Bloom düzeyi şablonun docstring'ine yazılır (ör. `"""Kazanım: ... · Bloom: An"""`). Böylece `catalog.py` ileride düzey dağılımını da raporlayabilir.

### 4.9 Kontrol listesi (her yeni şablon için)

- [ ] Kök tek bir şey soruyor, Türkçesi doğru, cevabı ele vermiyor.
- [ ] 500 üretimde çeşitlilik ≥ 30, en sık cevap ≤ %40.
- [ ] Dolgu şık oranı ≤ %5; her yanlışın `Wrong` açıklaması var.
- [ ] İpucu cevabı içermiyor (`test_content` bunu denetler).
- [ ] `verify` türü uygun; yeni tür gerekiyorsa testi de yazıldı.
- [ ] KC/BD'de kabul listesi eşdeğerleri kapsıyor ve çalıştırılarak doğrulanıyor.
- [ ] KY'de 6 kabul ve 6 ret testi var; sabit cevap yakalanıyor.
- [ ] `python -m pytest_pro.questions.mufredat > docs/MUFREDAT.md` ile müfredat belgesi yenilendi.
