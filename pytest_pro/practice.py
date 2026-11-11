"""
Pratik modu: öğrenci ünite seçip soru çözer, cevabını hemen kontrol eder. Kayıt tutulmaz.
Sorular kısa süre bellekte saklanır; cevap anahtarı tarayıcıya ancak kontrol edildikten sonra gönderilir.
"""
import secrets
import threading
from collections import OrderedDict

from . import clock

MAX_ITEMS = 5000
TTL_SECONDS = 2 * 60 * 60


class PracticeStore:
    def __init__(self, max_items=MAX_ITEMS, ttl=TTL_SECONDS):
        self._items = OrderedDict()
        self._lock = threading.Lock()
        self.max_items, self.ttl = max_items, ttl

    def put(self, question):
        token = secrets.token_urlsafe(16)
        with self._lock:
            self._items[token] = (clock.now(), question)
            while len(self._items) > self.max_items:
                self._items.popitem(last=False)
        return token

    def get(self, token):
        with self._lock:
            item = self._items.get(str(token or ""))
            if item is None:
                return None
            created, question = item
            if clock.now() - created > self.ttl:
                del self._items[token]
                return None
            return question
