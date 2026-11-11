"""
Müfredat üniteleri. Her dosya bir üniteyi tanımlar ve içe aktarıldığında kendini kaydeder.

Yeni ünite eklemek: bu klasöre `uNN_ad.py` dosyası ekleyip aşağıdaki listeye yazın.
"""
from . import (
    u01_temel,
    u02_veri_tipleri,
    u03_operatorler,
    u04_metinler,
    u05_kosullar,
    u06_donguler,
    u07_listeler,
    u08_koleksiyonlar,
    u09_fonksiyonlar,
    u10_hatalar,
    u11_nesne,
)

MODULES = (
    u01_temel, u02_veri_tipleri, u03_operatorler, u04_metinler, u05_kosullar, u06_donguler,
    u07_listeler, u08_koleksiyonlar, u09_fonksiyonlar, u10_hatalar, u11_nesne,
)
