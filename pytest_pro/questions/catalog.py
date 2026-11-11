"""
Müfredat haritasını Markdown olarak üretir.

Kullanım: python -m pytest_pro.questions.catalog > docs/MUFREDAT.md
"""
import random

from .registry import ordered_units

TYPE_NAMES = {"mc": "Çoktan seçmeli", "tf": "Doğru / Yanlış", "short": "Kısa cevap", "code": "Kod yazma"}
VERIFY_NAMES = {
    "output": "Kod çalıştırılıp çıktı karşılaştırılır",
    "error": "Kod çalıştırılıp hata türü karşılaştırılır",
    "raises_one": "Her seçenek çalıştırılır",
    "identifier": "Python ad kurallarıyla denetlenir",
    None: "—",
}


def render():
    state = random.getstate()
    unit_list = ordered_units()
    total = sum(len(u.generators) for u in unit_list)
    lines = [
        "# Müfredat Haritası",
        "",
        "Bu dosya koddan otomatik üretilir; elle düzenlemeyin:",
        "`python -m pytest_pro.questions.catalog > docs/MUFREDAT.md`",
        "",
        f"Toplam **{len(unit_list)} ünite**, **{total} soru şablonu**. Her şablon her çağrıldığında farklı "
        "değerlerle yeni bir soru üretir.",
        "",
        "| # | Ünite | Seviye | Şablon |",
        "|---|---|---|---|",
    ]
    lines += [f"| {u.order} | {u.title} | {u.level} | {len(u.generators)} |" for u in unit_list]
    for u in unit_list:
        lines += ["", f"## {u.order}. {u.title}", "", f"**Seviye:** {u.level} · **Kimlik:** `{u.id}`", "",
                  u.description, "", "| Konu | Soru tipi | Cevap anahtarı doğrulaması |", "|---|---|---|"]
        for g in u.generators:
            random.seed(0)
            lines.append(f"| {g.topic} | {TYPE_NAMES[g()['type']]} | {VERIFY_NAMES[g.verify]} |")
    random.setstate(state)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(render(), end="")
