import time
import json
import random
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

# 1. AYARLAR
KAFKA_TOPIC = "ecommerce_events"
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'

# Sahte veri üreticisi
fake = Faker()

# 2. KAFKA PRODUCER (Veri Gönderici) TANIMLA
# Kafka bazen geç açılır, bağlanamazsa hata vermesin diye try-except yok, 
# direkt bağlanmaya çalışacak. Eğer hata alırsan 1 dk bekle tekrar dene.
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8') # Veriyi JSON yapıp gönderir
)

print(f"🚀 Veri üretimi başlıyor... Hedef Kafka Konusu: {KAFKA_TOPIC}")

# 3. SENARYO VERİLERİ
PRODUCT_CATEGORIES = ["Electronics", "Fashion", "Home", "Beauty", "Sports"]
ACTIONS = ["view", "view", "view", "add_to_cart", "purchase"] # 'view' ihtimali daha yüksek olsun

def generate_event():
    """Rastgele bir e-ticaret olayı üretir"""
    return {
        "event_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": random.randint(1000, 9999),
        "product_id": f"PROD-{random.randint(1, 1000)}",
        "category": random.choice(PRODUCT_CATEGORIES),
        "price": round(random.uniform(10, 5000), 2),
        "action": random.choice(ACTIONS), # view, click, purchase...
        "device": random.choice(["mobile", "desktop", "tablet"])
    }

# 4. SONSUZ DÖNGÜ (Veri Akışı)
try:
    while True:
        event = generate_event()
        
        # Kafka'ya gönder
        producer.send(KAFKA_TOPIC, event)
        
        # Ekrana da bas ki görelim
        print(f"📤 Gönderildi: {event['action']} - {event['category']} - {event['price']} TL")
        
        # Hız ayarı (Saniyede 1-2 veri)
        time.sleep(random.uniform(0.5, 2.0))

except KeyboardInterrupt:
    print("\n🛑 Veri üretimi durduruldu.")
    producer.close()