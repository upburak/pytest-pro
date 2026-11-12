#!/bin/bash
# PyTest Pro - Mac'te çift tıklayarak başlatma
cd "$(dirname "$0")" || exit 1

bekle() { echo; read -r -p "Pencereyi kapatmak için Enter'a basın..."; }

# İlk açılışta proje klasöründe ayrı bir Python ortamı (.venv) kurulur.
if [ ! -x .venv/bin/python ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 bulunamadı. https://www.python.org/downloads/ adresinden indirip kurun."
    bekle; exit 1
  fi
  echo "İlk açılış: Python ortamı hazırlanıyor..."
  if ! python3 -m venv .venv; then
    echo "Python ortamı oluşturulamadı. Klasöre yazma izni olduğundan emin olun."
    bekle; exit 1
  fi
fi

echo "Gerekli paketler denetleniyor..."
if ! .venv/bin/python -m pip install --disable-pip-version-check -q -r requirements.txt; then
  echo "Paketler kurulamadı. İlk açılışta internet bağlantısı gerekir; bağlantıyı denetleyip yeniden deneyin."
  bekle; exit 1
fi

PORT="${PYTEST_PORT:-5000}"
# Sunucu açılınca öğretmen paneli tarayıcıda açılır.
(sleep 3; open "http://localhost:$PORT/ogretmen" >/dev/null 2>&1) &

.venv/bin/python server.py
echo "Sunucu durdu."
bekle
