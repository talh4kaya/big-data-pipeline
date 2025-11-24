import os

# 📂 KLASÖR YAPISI
directories = [
    "data",
    "src/ecommerce",  # E-Ticaret Projesi Kodları
    "src/factory",    # Fabrika/IoT Projesi Kodları
    "dags"            # (Opsiyonel) Airflow için
]

# 📄 DOSYA İÇERİKLERİ

# 1. Altyapı (Kafka, Spark, Zookeeper, Postgres)
docker_compose_content = """version: '3.8'

services:
  zookeeper:
    image: bitnami/zookeeper:latest
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes

  kafka:
    image: bitnami/kafka:latest
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_BROKER_ID=1
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
      - ALLOW_PLAINTEXT_LISTENER=yes
    depends_on:
      - zookeeper

  spark-master:
    image: bitnami/spark:latest
    container_name: spark-master
    environment:
      - SPARK_MODE=master
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_RPC_ENCRYPTION_ENABLED=no
      - SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    ports:
      - "8080:8080"
      - "7077:7077"

  spark-worker:
    image: bitnami/spark:latest
    container_name: spark-worker
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
      - SPARK_WORKER_MEMORY=1G
      - SPARK_RPC_AUTHENTICATION_ENABLED=no
      - SPARK_SSL_ENABLED=no
    depends_on:
      - spark-master

  postgres:
    image: postgres:13
    container_name: data_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: big_data_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""

# 2. Python Kütüphaneleri
requirements_content = """
kafka-python
pyspark
streamlit
psycopg2-binary
pandas
python-dotenv
requests
faker
"""

# 3. Git Ignore (Çöp dosyalar gitmesin)
gitignore_content = """
venv/
__pycache__/
.env
.vscode/
*.pyc
postgres_data/
"""

files = {
    "docker-compose.yml": docker_compose_content,
    "requirements.txt": requirements_content,
    ".gitignore": gitignore_content,
    "src/__init__.py": "",
    "src/ecommerce/__init__.py": "",
    "src/factory/__init__.py": ""
}

def create_structure():
    print("🚀 Proje kurulumu başlatılıyor...")
    
    # Klasörleri oluştur
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Klasör oluşturuldu: {directory}")
    
    # Dosyaları oluştur
    for filepath, content in files.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"📄 Dosya oluşturuldu: {filepath}")
        
    print("\n✅ Kurulum Tamamlandı! Şimdi şu adımları izle:")
    print("1. Terminali aç: docker-compose up -d")
    print("2. Sanal ortamı kur: python -m venv venv")
    print("3. Aktif et ve yükle: pip install -r requirements.txt")

if __name__ == "__main__":
    create_structure()