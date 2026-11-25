"""
Ünite ve soru şablonu kaydı.

Her ünite kendi dosyasında `register_unit(...)` ile tanımlanır ve şablonlarını
`@UNIT.question("Konu adı", verify=...)` dekoratörüyle kaydeder.

verify değerleri (testlerin cevap anahtarını nasıl doğrulayacağı):
    "output"     kod çalıştırılır; ekran çıktısı cevapla birebir aynı olmalı
    "error"      kod çalıştırılır; hata vermeli ve hatanın adı cevapta geçmeli
    "code_one"   seçenekler birer koddur (helpers.code_options_question): her seçenek sorunun "harness"
                 kalıbına konup her "cases" durumunda çalıştırılır; yalnızca doğru seçenek her durumda
                 beklenen sonucu ("expect": çıktı, "Hata verir (Tür)" ya da LOOP_OUTCOME) vermeli
    "raises_one" seçenekler birer ifadedir; yalnızca doğru seçenek hata vermeli
    "identifier" seçenekler değişken adıdır; yalnızca doğru seçenek geçerli ad olmalı
    "outcome"    kod çalıştırılır; hata vermezse çıktı, verirse "Hata verir (TürAdı)" cevapla aynı olmalı
                 (aynı şablon hatalı ve hatasız değişkeler üretebilir)
    "tf_output"  hesaplanan doğru/yanlış (helpers.tf_claim): kod çalıştırılır; sonuç sorunun "output"
                 alanına eşit olmalı ve cevap ancak iddia ("claim") gerçek sonuca eşitse "True" olmalı
    "fill"       boşluk doldurma: her kabul edilen cevap (ya da answer_sets takımı) koda yerleştirilip
                 çalıştırılır; çıktı "expect" ile birebir aynı olmalı. blank_whys'teki yanlışlar farklı
                 sonuç vermeli
    None         otomatik doğrulama yok (sabit havuzlu doğru/yanlış, kod yazma vb.)
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .fill import fill_in

VERIFY_KINDS = ("output", "error", "outcome", "tf_output", "code_one", "raises_one", "identifier", "fill", None)
LEVELS = ("Başlangıç", "Orta", "İleri")
# Ortak kalite testleri (tests/test_quality.py); şablon @q(..., exempt={ad: gerekçe}) ile istisna alabilir
QUALITY_CHECKS = {
    "filler": "anlamsız dolgu şık içeren soru oranı en fazla %5",
    "top_answer": "en sık doğru cevap en fazla %40",
    "error_giveaway": "hep yanlış olan 'Hata verir' şıkkı soruların en fazla %60'ında",
}


@dataclass(frozen=True)
class Generator:
    func: Callable[[], dict]
    unit: str
    topic: str
    verify: Optional[str]
    exempt: Dict[str, str] = field(default_factory=dict, compare=False, hash=False)

    @property
    def name(self):
        return f"{self.unit}.{self.func.__name__}"

    def __call__(self):
        q = self.func()
        q.setdefault("topic", self.topic)
        q["unit"] = self.unit
        q["gen"] = self.name
        q["trace"] = self._trace(q)
        return q

    def _trace(self, q):
        """Adım adım izlenecek kod: çıktı/hata sorularında sorunun kodu, kod yazmada örnek çözüm,
        boşluk doldurmada cevap anahtarı yerleştirilmiş kod."""
        if q["type"] == "code":
            return {"code": q["answer"], "stdin": ""}
        if q["type"] == "fill":
            return {"code": fill_in(q["code"], [alts[0] for alts in q["answer"]]), "stdin": q.get("stdin", "")}
        if self.verify in ("output", "error", "outcome", "tf_output") and q.get("code"):
            return {"code": q["code"], "stdin": q.get("stdin", "")}
        return None


@dataclass
class Unit:
    id: str
    title: str
    level: str
    description: str
    order: int
    generators: List[Generator] = field(default_factory=list)

    def question(self, topic, verify=None, exempt=None):
        """Şablon kaydı. exempt: ortak kalite testlerinden (tests/test_quality.py) gerekçeli istisna,
        ör. {"top_answer": "Ölçülen şey anahtar sözcük; cevap doğası gereği sabit."}."""
        if verify not in VERIFY_KINDS:
            raise ValueError(f"Bilinmeyen verify türü: {verify}")
        exempt = dict(exempt or {})
        for check, reason in exempt.items():
            if check not in QUALITY_CHECKS:
                raise ValueError(f"Bilinmeyen kalite denetimi: {check} (geçerli: {', '.join(QUALITY_CHECKS)})")
            if not str(reason).strip():
                raise ValueError("Kalite istisnasının gerekçesi yazılmalı")

        def decorator(func):
            self.generators.append(Generator(func, self.id, topic, verify, exempt))
            return func
        return decorator

    @property
    def topics(self):
        return list(dict.fromkeys(g.topic for g in self.generators))

    def to_public(self):
        topic_templates = {}
        for g in self.generators:
            topic_templates[g.topic] = topic_templates.get(g.topic, 0) + 1
        return {"id": self.id, "title": self.title, "level": self.level, "description": self.description,
                "order": self.order, "templates": len(self.generators), "topics": self.topics,
                "topic_templates": topic_templates}


UNITS: Dict[str, Unit] = {}


def register_unit(id, title, level, description, order):
    if id in UNITS:
        raise ValueError(f"Ünite iki kez tanımlandı: {id}")
    if level not in LEVELS:
        raise ValueError(f"Bilinmeyen seviye: {level}")
    unit = Unit(id, title, level, description, order)
    UNITS[id] = unit
    return unit


def ordered_units():
    return sorted(UNITS.values(), key=lambda u: u.order)


def all_generators():
    return [g for u in ordered_units() for g in u.generators]
