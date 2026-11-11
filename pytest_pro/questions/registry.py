"""
Ünite ve soru şablonu kaydı.

Her ünite kendi dosyasında `register_unit(...)` ile tanımlanır ve şablonlarını
`@UNIT.question("Konu adı", verify=...)` dekoratörüyle kaydeder.

verify değerleri (testlerin cevap anahtarını nasıl doğrulayacağı):
    "output"     kod çalıştırılır; ekran çıktısı cevapla birebir aynı olmalı
    "error"      kod çalıştırılır; hata vermeli ve hatanın adı cevapta geçmeli
    "raises_one" seçenekler birer ifadedir; yalnızca doğru seçenek hata vermeli
    "identifier" seçenekler değişken adıdır; yalnızca doğru seçenek geçerli ad olmalı
    None         otomatik doğrulama yok (doğru/yanlış soruları, kod yazma vb.)
"""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

VERIFY_KINDS = ("output", "error", "raises_one", "identifier", None)
LEVELS = ("Başlangıç", "Orta", "İleri")


@dataclass(frozen=True)
class Generator:
    func: Callable[[], dict]
    unit: str
    topic: str
    verify: Optional[str]

    @property
    def name(self):
        return f"{self.unit}.{self.func.__name__}"

    def __call__(self):
        q = self.func()
        q.setdefault("topic", self.topic)
        q["unit"] = self.unit
        q["gen"] = self.name
        return q


@dataclass
class Unit:
    id: str
    title: str
    level: str
    description: str
    order: int
    generators: List[Generator] = field(default_factory=list)

    def question(self, topic, verify=None):
        if verify not in VERIFY_KINDS:
            raise ValueError(f"Bilinmeyen verify türü: {verify}")

        def decorator(func):
            self.generators.append(Generator(func, self.id, topic, verify))
            return func
        return decorator

    @property
    def topics(self):
        return list(dict.fromkeys(g.topic for g in self.generators))

    def to_public(self):
        return {"id": self.id, "title": self.title, "level": self.level, "description": self.description,
                "order": self.order, "templates": len(self.generators), "topics": self.topics}


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
