# Öğrenmeyi Derinleştirme: Tasarım

- **Tarih:** 2026-11-11
- **Durum:** Onay bekliyor
- **Dal:** `ogrenme/derinlestirme` (`tasarim/yeni-gorsel-kimlik` üzerine)

## 1. Amaç ve kapsam

### Hedef
Öğrenci yanlışından öğrensin: seçtiği cevabın neden yanlış olduğunu anlasın, kodun nasıl
çalıştığını adım adım görsün ve aynı konuyu hemen tekrar deneyerek pekiştirsin.

### Kullanıcılar
Lise öğrencileri (derste, okul ağında) ve ders öğretmeni.

### Öğretmenin belirlediği kararlar
- Pratik modu **anonim** kalır; sunucuda hiçbir pratik kaydı tutulmaz.
- Dört öğrenme yardımı istenir: **ipucu**, **adım adım kod izleme**, **yanlışı tekrar çözdürme**,
  **yanlışın nedenini söyleme**.
- Kod izleme ve yanlışın nedeni **sınav sonuç ekranında da** görünür.

### Varsayımlar (öğretmen itiraz etmedi)
- İpucu ve tekrar çözdürme yalnızca pratikte vardır; sınavda hiç yoktur.
- Sınav sonucundaki yardımlar yalnızca öğretmen "çözümleri göster" ayarını açtıysa görünür.
- Pratikteki konu tamamlama durumu yalnızca o tarayıcı sekmesinde (`sessionStorage`) tutulur.

### Başarı ölçütleri
1. Yanlış cevaplanan her soruda öğrenci şunları görebilir: seçtiği şıkkın neden yanlış olduğunu,
   kodun adım adım izini (izlenebilir kodu olan sorularda) ve pratikte aynı konudan yeni bir soruyu.
2. Testler, kapsamdaki tüm şablonlarda ipucu ve her yanlış şıkta açıklama bulunduğunu doğrular.
3. Testler, kod izinin son çıktısının her çıktı sorusunun cevap anahtarıyla aynı olduğunu doğrular.

### Kapsam dışı
Öğrenci hesabı veya pratik geçmişi, sınavda ipucu, öğrenci kodunu çalıştırma, yeni ünite veya soru tipi.

## 2. Soru içeriğinin veri yapısı

Soru sözlüğüne üç iç alan eklenir. `public_question()` bunları **hiçbir zaman** öğrenciye göndermez.

| Alan | Tip | Anlam |
|---|---|---|
| `hint` | `str` (HTML) | Cevabı söylemeden yönlendiren tek cümle |
| `whys` | `dict[str, str]` | Yanlış seçenek değeri → "neden yanlış" açıklaması (HTML) |
| `trace` | `{"code": str, "stdin": str} \| None` | Adım adım izlenecek kod |

### Şablon yazımı
- `helpers.Wrong(value, why)` adlı küçük bir `NamedTuple` eklenir.
- `output_question()` ve `unique_options()` hem `Wrong` hem düz `str` kabul eder; `whys` sözlüğünü üretir.
- `output_question(..., hint=...)` ve `tf_question(..., hint=...)` parametresi eklenir.
- Kısa cevaplı sorularda sık yapılan yanlışlar `common_wrongs=[Wrong(...)]` ile verilir. Eşleştirme,
  puanlamadaki normalleştirmeyle aynıdır (`_norm_short`).
- Yedek çeldiricilere (`_fillers`) genel bir açıklama eklenir: sayısal olanlara "Hesaptaki bir adımı
  atlamış ya da fazladan yapmış olabilirsin; kodu adım adım izle.", diğerlerine "Bu, kodun gerçek
  çıktısı değil; kodu adım adım izle."

### `trace` alanının doldurulması
`trace` alanı `Generator.__call__` içinde otomatik doldurulur; şablon yazarı bununla uğraşmaz:
- `verify` değeri `"output"` veya `"error"` olan şablonlarda sorunun kodu ve `stdin` değeri izlenir.
- `type == "code"` olan sorularda örnek çözüm (`answer`) izlenir.
- Diğer sorularda (doğru/yanlış, değişken adı, `raises_one`) değer `None` olur.

### Geriye uyumluluk
Eski sınav kayıtlarındaki sorularda bu alanlar yoktur. Bu durumda:
- "Neden yanlış" satırı gösterilmez.
- Kod izleme, soru kodu kayıtta durduğu için `verify` bilinmese de çalışır. Kayıtta `code` varsa ve
  tip `mc` veya `short` ise iz denenir; kod hata verirse iz, hatayı son adım olarak gösterir.

## 3. Kod izleme motoru

Yeni modül: `pytest_pro/questions/tracer.py`. Bu modül Flask'a bağlı değildir.

```python
trace(code: str, stdin: str = "") -> {
  "lines": [str],
  "steps": [{"line": int, "scope": str | None, "vars": {ad: gösterim},
             "changed": [ad], "output": str}],
  "error": {"type": str, "message": str, "line": int} | None,
  "truncated": bool,
}
```

### Çalışma biçimi
- Kod `compile(code, "<soru>", "exec")` ile derlenir. `sys.settrace` yalnızca dosya adı `<soru>`
  olan çerçevelerde `line` olaylarını kaydeder. `return` olayı da kaydedilir; fonksiyondan dönüş anı
  görünür.
- **Değişkenler:** Modül düzeyinde kullanıcının tanımladığı adlar gösterilir; modüller, `__builtins__`
  ve `__*__` adları gizlenir. Fonksiyon içindeyse o çerçevenin yerel adları gösterilir ve
  `scope = "kare() içinde"` olur.
- **Gösterim:**
  - Python `repr` kullanılır; metinler tırnaklı görünür. 60 karakterden uzun değerler `…` ile kısaltılır.
  - Fonksiyonlar `fonksiyon`, sınıflar `sınıf` olarak yazılır.
  - Kullanıcı sınıflarından nesneler `Ogrenci(ad='Ali', yas=16)` biçiminde gösterilir (`__dict__`'ten).
- **`changed`:** Önceki adıma göre gösterimi değişen adlar.
- **Çıktı:** `print` çıktısı adım adım birikir. `input()`, `stdin` satırlarını döndürür ve girilen değeri çıktıya yazar.
- **Hata:** Kod hata verirse `error` alanı hatanın türünü, mesajını ve satırını içerir. Hata satırı son adım olur.

### Güvenlik ve sınırlar
- Yalnızca sunucuda saklanan, şablonlarca üretilmiş kod izlenir. İstekle gelen kod asla izlenmez.
  Öğrenci kodu hiçbir zaman çalıştırılmaz.
- Çalıştırma, kısıtlı yerleşik fonksiyonlarla yapılır: `open`, `eval`, `exec`, `compile` ve `__import__`
  yoktur. Yalnızca `math` modülünün içe aktarılmasına izin veren bir `__import__` sağlanır.
- Tamamlanan iz en fazla 200 adımdır. 200 adım dolunca çalıştırma bir istisnayla durdurulur ve
  `truncated: True` döner. Çıktı en fazla 5000 karakterdir.
- `functools.lru_cache(maxsize=512)` ile `(code, stdin)` anahtarına göre önbelleğe alınır.
- `sys.settrace` iş parçacığına özeldir; waitress iş parçacıklarında güvenlidir. İz bitince eski
  izleyici geri yüklenir.

### Ekran bileşeni: `static/js/tracer.js`
- `PyTest.renderTrace(container, trace)` adlı tek bir dışa açık fonksiyon sunar.
- **Kod:** Kod satırları satır numaralarıyla gösterilir; o anki satır `--marker` (fosforlu kalem) ile işaretlenir.
- **Durum:** Değişkenler tablosu (`changed` adlar vurgulu), ekran çıktısı ve fonksiyon içindeyse kapsam adı gösterilir.
- **Kontroller:** "Önceki adım", "Sonraki adım", adım çubuğu (`input type=range`), ←/→ tuşları.
  Odak bileşenin içindeyken okları bileşen yakalar.
- **Hata:** Hatalı son adımda hata türü ve satırı `--pen` ile, Caveat yazısıyla gösterilir.
- **Kesilen iz:** 200 adımda kesildiyse son adımda "İlk 200 adım gösteriliyor" notu bulunur.
- **Erişilebilirlik:** Adım değiştiğinde "Adım 4 / 12, satır 3" bilgisi `aria-live` ile duyurulur.

## 4. Pratik akışı

### Durumlar
Soru → (isteğe bağlı) İpucu → Cevabı kontrol et → Doğru / Yanlış.

| Sonuç | Gösterilen | Düğmeler |
|---|---|---|
| Doğru | "Doğru" (+ ipucu alındıysa "ipucuyla") ve kısa çözüm | **Yeni soru**, Kodu adım adım izle |
| Yanlış | Neden yanlış (varsa), doğru cevap ve çözüm | **Bu konudan yeni soru**, Kodu adım adım izle, Yeni soru |

### API
Hepsi pratik açıkken çalışır; kapalıyken `403` döner.

| Uç nokta | İstek | Yanıt |
|---|---|---|
| `POST /api/practice/next` | `{unit, gen?, avoid?: [gen]}` | `{token, unit, question}` |
| `POST /api/practice/hint` | `{token}` | `{hint}` (ipucu yoksa `404`) |
| `POST /api/practice/check` | `{token, answer}` | Bugünkü alanlar + `why`, `gen`, `has_trace` |
| `POST /api/practice/trace` | `{token}` | `trace()` çıktısı (izlenecek kod yoksa `404`) |

**`/next` için kurallar**
- `gen` verilirse ve o şablon üniteye aitse aynı şablondan yeni soru üretilir ("Bu konudan yeni soru").
  Başka üniteye aitse `400` döner.
- `gen` verilmezse şablon şöyle seçilir: `avoid` listesindekiler (tamamlanmış konuların şablonları)
  dışındakilerden rastgele. %20 olasılıkla `avoid` göz ardı edilir (tamamlanmış konudan tekrar sorusu).
  Hepsi tamamlandıysa tümünden seçilir.
- Yanıtta `gen` alanı da döner; tarayıcı "bu konudan yeni soru" ve konu takibi için kullanır.
  `gen` cevap içermez.

**`/check` için kurallar**
- `why` alanı `whys[answer]` (seçenekli sorular) ya da `common_wrongs` eşleşmesi (kısa cevaplı sorular)
  olarak doldurulur. Kod yazma sorularında denetleyicinin notu kullanılır. Eşleşme yoksa `null` döner.

### Konu tamamlama (yalnızca tarayıcıda)
- `sessionStorage` anahtarı `pytest_pratik`. İçeriği:
  `{unit: {gen: {streak: int, done: bool, topic: str}}}`
- İpucusuz doğru cevap `streak` değerini 1 artırır; yanlış cevap ya da ipucu kullanmak sıfırlar.
  `streak >= 2` olunca `done = true` olur ve bir daha geri alınmaz.
- Konu, şablonun `topic` değeridir. Aynı konu adını taşıyan birden fazla şablon varsa konu, hepsi
  `done` olduğunda tamamlanmış sayılır.
- **İçindekiler sayfası:** Her ünitenin altında "4 / 7 konu tamamlandı" ve tamamlanan konuların listesi görünür.
- **Ünite bitince:** Tüm konular tamamlanınca bir not gösterilir: "Bu ünitedeki tüm konuları
  tamamladın. Sıradaki ünite: …"

## 5. Sınav sonuç ekranı ve öğretmen paneli

### `/api/submit`
Çözümler açıksa her ayrıntı öğesine iki alan eklenir:
- `why`: Öğrencinin cevabına karşılık gelen açıklama; yoksa `null`.
- `has_trace`: Soru için izlenecek kod var mı.

### Yeni uç nokta: `POST /api/exam/trace`
- **İstek:** `{exam_id, question_id}`
- **Koşullar:** Sınav gönderilmiş olmalı ve `show_solutions` ayarı açık olmalı. Aksi hâlde `403`.
  Soru yoksa veya izlenecek kod yoksa `404`.
- **Yanıt:** `trace()` çıktısı.

### Yeni uç nokta: `GET /api/results/<exam_id>/trace/<question_id>`
Öğretmene özeldir, şifre ister. Sınav gönderilmiş olmalıdır.

### Öğrenci sonuç ekranı
- Yanlış sorularda "Neden yanlış" satırı Caveat yazısıyla, `--pen` renginde gösterilir.
- "Kodu adım adım izle" düğmesi izi sorunun altında açar ve kapatır; birden fazla iz açık olabilir.
  Doğru sorularda düğme ikincil biçimde görünür.

### Öğretmen paneli
- Öğrenci ayrıntısında "neden yanlış" satırı ve kod izleme düğmesi bulunur.
- Konu analizine **en sık yanlış cevap** eklenir. `exams.topic_stats` her konu için yanlış cevapları
  sayar ve en sık olanı döndürür: `{"common_wrong": {"answer": str, "share": int, "why": str | null}}`.
  Bu yalnızca seçenekli ve kısa cevaplı sorularda geçerlidir; boş cevaplar sayılmaz. Ekranda
  "%40 `7` cevabını verdi" ve yanılgının açıklaması gösterilir.

## 6. Hata durumları

| Durum | Davranış |
|---|---|
| Pratik soru anahtarının süresi doldu | İpucu, iz veya kontrol isteği `404` döner: "Bu soru artık yok, yeni soru al." |
| Açıklaması olmayan yanlış şık | "Neden yanlış" satırı gösterilmez |
| İz 200 adımda kesildi | Son adımda "İlk 200 adım gösteriliyor" yazar |
| İzlenen kod beklenmedik bir hata verdi | Hata, izin son adımı olarak gösterilir; uygulama çökmez |
| Sınav sırasında iz istendi | `403` |

## 7. Testler

### Motor (`tests/test_tracer.py`)
- **Cevap anahtarıyla uyum:** Her `verify="output"` şablonu için 30 tohumla son adımdaki çıktı cevap
  anahtarıyla aynıdır. Her `verify="error"` şablonunda `error.type` cevapta geçer.
- **Davranış:** `input()` girdisinin çıktıya yazılması, fonksiyon içi `scope` ve yerel değişkenler,
  nesne gösterimi, `changed` alanının doğruluğu.
- **Sınırlar:** 200 adım sınırı (`truncated`), yasak işlemlerin hata vermesi (`open`, `import os`),
  `math` içe aktarmanın çalışması.

### İçerik (`tests/test_questions.py`)
- `whys` sözlüğündeki her anahtar gerçekten seçeneklerde bulunur. Yalnızca yanlış seçenekler için
  açıklama vardır; doğru cevap için yoktur.
- İpucu, doğru cevabı kelimesi kelimesine içermez. Bu, cevap 3 karakterden uzunsa denetlenir;
  "True" ve "5" gibi kısa cevaplar hariçtir.
- **Kapsam:** `CONTENT_UNITS` listesindeki ünitelerde her şablonda `hint` vardır ve her yanlış şıkta
  (yedek çeldiriciler hariç) `whys` vardır. Birinci teslimatta liste
  `temel, veri_tipleri, operatorler, metinler` ünitelerinden oluşur; ikinci teslimatta tüm ünitelere genişler.
- Öğrenciye giden soruda `hint`, `whys` ve `trace` bulunmaz.

### API (`tests/test_api.py`)
- Pratik ipucu ve iz akışı.
- `gen` ile aynı şablondan soru; başka ünitenin şablonu için `400`.
- `avoid` listesine uyulması.
- Sınav izinin yalnızca gönderilmiş ve çözümleri açık sınavda verilmesi.
- Öğretmen izi.
- `submit` yanıtında `why` alanı.
- Konu analizinde `common_wrong` alanı.

### Tarayıcı (Playwright, elle çalıştırılır)
- **Pratik:** İpucu, yanlış cevap, açıklama, iz gezinme (düğmeler ve oklar), "bu konudan yeni soru"
  ve iki doğruyla konu tamamlama.
- **Sınav sonucu:** İz ve "neden yanlış" görünümü.
- **Genel:** Telefon görünümünde yatay taşma olmaması, konsolda hata olmaması.

## 8. Teslimatlar

1. **Birinci teslimat:** Bölüm 2–7'nin tamamı ve ilk 4 ünitenin içeriği (30 şablon). Ardından
   öğretmen derste dener ve açıklamaların dilini değerlendirir.
2. **İkinci teslimat:** Kalan 7 ünitenin içeriği (45 şablon), birinci teslimatta oturan dille.
   `CONTENT_UNITS` tüm ünitelere genişletilir.

## 9. Etkilenen dosyalar

| Dosya | Değişiklik |
|---|---|
| `pytest_pro/questions/helpers.py` | `Wrong`, `hint` ve `common_wrongs` parametreleri, yedek çeldirici açıklamaları |
| `pytest_pro/questions/registry.py` | `Generator.__call__` içinde `trace` alanını doldurma |
| `pytest_pro/questions/__init__.py` | `why_for(question, answer)` yardımcısı; `generate_one(unit, gen=None, avoid=())` |
| `pytest_pro/questions/tracer.py` | Yeni: kod izleme motoru |
| `pytest_pro/questions/units/u01–u04` | İpucu ve açıklama içeriği (birinci teslimat) |
| `pytest_pro/questions/units/u05–u11` | İpucu ve açıklama içeriği (ikinci teslimat) |
| `pytest_pro/routes/practice.py` | `/hint`, `/trace`; `/next` için `gen` ve `avoid`; `/check` yanıtına `why` |
| `pytest_pro/routes/student.py` | `/api/exam/trace`; `submit` yanıtına `why` ve `has_trace` |
| `pytest_pro/routes/teacher.py` | Öğretmen izi; ayrıntıda `why` |
| `pytest_pro/exams.py` | `topic_stats` içinde `common_wrong` |
| `pytest_pro/static/js/tracer.js` | Yeni: iz bileşeni |
| `pytest_pro/static/js/practice.js`, `student.js`, `teacher.js` | Yeni akışlar |
| `pytest_pro/templates/*.html` | `tracer.js` eklenmesi ve küçük işaretleme değişiklikleri |
| `pytest_pro/static/css/style.css` | İz bileşeni, "neden yanlış" notu, konu ilerlemesi |
| `docs/TASARIM.md`, `docs/GELISTIRME.md` | Yeni bileşenler ve şablon yazım kuralları |
