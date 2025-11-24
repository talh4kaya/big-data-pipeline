from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, sum as _sum, count
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType

# 1. SPARK OTURUMUNU BAŞLAT
# Kafka entegrasyonu için gerekli paketi indiriyoruz (Spark 3.5.x uyumlu)
spark = SparkSession.builder \
    .appName("EcommerceRealTimeAnalysis") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .getOrCreate()

# Log seviyesini düşür (Sürekli INFO mesajı görmeyelim)
spark.sparkContext.setLogLevel("WARN")

# 2. ŞEMAYI TANIMLA (Kafka'dan gelen veri JSON formatında, yapısını Spark'a anlatmalıyız)
schema = StructType([
    StructField("event_time", StringType()),
    StructField("user_id", IntegerType()),
    StructField("product_id", StringType()),
    StructField("category", StringType()),
    StructField("price", DoubleType()),
    StructField("action", StringType()), # view, purchase...
    StructField("device", StringType())
])

# 3. KAFKA'DAN OKU (ReadStream)
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "ecommerce_events") \
    .option("startingOffsets", "earliest") \
    .load()

# Kafka verisi binary (010101) gelir, onu String'e ve sonra JSON'a çeviriyoruz
parsed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 4. ANALİZ YAP (Transformation)
# Soru: "Her kategoride, işlem türüne göre (satın alma/görüntüleme) toplam ciro ve işlem sayısı nedir?"
analysis_df = parsed_df.groupBy("category", "action") \
    .agg(
        count("*").alias("count"),
        _sum("price").alias("total_revenue")
    )

# 5. SONUCU EKRANA YAZ (WriteStream)
# "complete" modu: Her tetiklemede tablonun TAMAMINI tekrar hesaplar ve basar.
query = analysis_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

print("🔥 Spark Streaming başladı... Veriler işleniyor...")
query.awaitTermination()