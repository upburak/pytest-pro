"""
Ortak madde kalitesi testleri (ölçme raporu bölüm 1 ve 4). Bütün şablonlara kendiliğinden uygulanır;
yeni bir şablon eklendiğinde ayrıca yazmaya gerek yoktur.

İstisna gerekiyorsa aşağıdaki sözlüklere şablonun adı ve GEREKÇESİ yazılır. İstisnalar kalıcı bir
izin değildir; listede olan şablon düzeltilince listeden çıkarılmalıdır.
"""
import pytest
from helpers import filler_rate, gens, samples, top_answer_share

from pytest_pro.questions.helpers import ERROR_PREFIX

N = 300  # şablon başına üretim (testlerin hızlı kalması için)
FILLER_MAX = 0.05  # anlamsız dolgu şık içeren soru oranı en fazla %5
TOP_ANSWER_MAX = 0.40  # en sık doğru cevap en fazla %40
ERROR_GIVEAWAY_MAX = 0.60  # hep yanlış olan "Hata verir" şıkkı soruların en fazla %60'ında görünebilir
ERROR_ANSWER_MIN = 0.15  # hata cevabı en az bu oranda doğruysa şık bir ipucu sayılmaz

FILLER_EXEMPT = {}
TOP_ANSWER_EXEMPT = {
    "fonksiyonlar.fill_def_return": "Ölçülen şey def ve return anahtar sözcüklerinin yeri; cevap doğası gereği "
                                    "sabit, çeşitlilik fonksiyon gövdesi ve çağrıdan gelir.",
}
ERROR_GIVEAWAY_EXEMPT = {}


@pytest.mark.parametrize("gen", [g for g in gens() if g.name not in FILLER_EXEMPT], ids=lambda g: g.name)
def test_filler_options_are_rare(gen):
    """Y1: Genel açıklamalı yedek çeldirici ("None", "[]", sayı ±1) içeren soru oranı %5'i geçmemeli."""
    rate = filler_rate(gen, N)
    assert rate <= FILLER_MAX, f"dolgu şıklı soru oranı %{rate * 100:.0f}"


@pytest.mark.parametrize("gen", [g for g in gens() if g.name not in TOP_ANSWER_EXEMPT], ids=lambda g: g.name)
def test_correct_answer_varies(gen):
    """K4/K5: En sık doğru cevap üretimlerin %40'ını geçmemeli (öğrenci soruyu okumadan bilemesin)."""
    share, value = top_answer_share(gen, N)
    assert share <= TOP_ANSWER_MAX, f"en sık cevap %{share * 100:.0f}: {value[:80]}"


@pytest.mark.parametrize("gen", [g for g in gens() if g.name not in ERROR_GIVEAWAY_EXEMPT], ids=lambda g: g.name)
def test_error_option_is_not_a_giveaway(gen):
    """O8: Bir şablonda 'Hata verir (...)' şıkkı hiç (ya da çok seyrek) doğru olmuyorsa ve her soruda yer
    alıyorsa öğrenci onu düşünmeden eler. Hata cevabı soruların en az %15'inde doğru değilse, hata şıkkı
    soruların en fazla %60'ında görünmeli."""
    shown = correct = 0
    for q in samples(gen, N):
        if q["type"] != "mc":
            continue
        if str(q["answer"]).startswith(ERROR_PREFIX):
            correct += 1
        elif any(str(o).startswith(ERROR_PREFIX) for o in q["options"]):
            shown += 1
    if correct / N >= ERROR_ANSWER_MIN:
        return
    assert shown / N <= ERROR_GIVEAWAY_MAX, f"hata şıkkı soruların %{shown * 100 / N:.0f}'inde var ve hep yanlış"


def test_exempt_lists_name_real_templates():
    names = {g.name for g in gens()}
    for exempt in (FILLER_EXEMPT, TOP_ANSWER_EXEMPT, ERROR_GIVEAWAY_EXEMPT):
        assert set(exempt) <= names
        assert all(reason.strip() for reason in exempt.values()), "istisnanın gerekçesi yazılmalı"
