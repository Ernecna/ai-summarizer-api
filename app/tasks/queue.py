from redis import Redis
from rq import Queue

from app.core.config import settings

# 1. Redis'e Bağlan
# .env dosyasından okuduğumuz REDIS_URL'yi kullanarak Redis'e bağlanıyoruz.
# decode_responses=True parametresini, RQ belgelerine göre DESTEKLENMEDİĞİ için kaldırıyoruz.
redis_conn = Redis.from_url(settings.REDIS_URL) # <--- DEĞİŞİKLİK BURADA

# 2. Bir RQ Kuyruğu (Queue) Oluştur
# Bağlantıyı açıkça (explicitly) connection parametresi ile veriyoruz.
# is_async'i False yapmak, geliştirme sırasında daha öngörülebilir olabilir.
# Production için True kalması daha performanslıdır. Şimdilik True bırakalım.
q = Queue("default", connection=redis_conn, is_async=True)