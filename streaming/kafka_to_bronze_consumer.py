"""
Consumer Kafka : lit le topic news_streaming et sauvegarde 
les articles en micro-batches dans MinIO Bronze.
"""
import sys
import os
import json
from io import BytesIO
from datetime import datetime
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka import KafkaConsumer
from minio import Minio
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class KafkaToBronzeConsumer:
    """Consumer Kafka qui sauvegarde en Bronze (micro-batches par source)."""

    def __init__(self, batch_size: int = 10):
        self.kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC_NEWS', 'news_streaming')
        self.batch_size = batch_size
        
        # MinIO
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
            secure=False
        )
        self.bronze_bucket = os.getenv('BUCKET_BRONZE', 'bronze')
        if not self.minio_client.bucket_exists(self.bronze_bucket):
            self.minio_client.make_bucket(self.bronze_bucket)
            logger.info(f"✅ Bucket créé : {self.bronze_bucket}")
        
        # Kafka Consumer
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=[self.kafka_broker],
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',
            group_id='bronze-sink-group',
            enable_auto_commit=True,
        )
        
        # Buffer par source (pour micro-batching)
        self.buffer = defaultdict(list)
        self.total_processed = 0
        
        logger.info(f"✅ Consumer Kafka initialisé. Topic: {self.topic}, Batch: {batch_size}")

    def save_batch_to_bronze(self, source: str, articles: list):
        """Sauvegarde un batch d'articles d'une source dans Bronze."""
        if not articles:
            return
        
        now = datetime.now()
        timestamp = int(now.timestamp())
        
        # Path : bronze/streaming/source/YYYY/MM/DD/source_streaming_TIMESTAMP.json
        filename = (
            f"streaming/{source}/{now.year}/{now.month:02d}/{now.day:02d}/"
            f"{source}_streaming_{timestamp}.json"
        )
        
        payload = {
            'source': source,
            'ingestion_type': 'streaming_kafka',
            'batch_timestamp': timestamp,
            'batch_datetime': now.isoformat(),
            'article_count': len(articles),
            'articles': articles,
        }
        
        json_data = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
        
        self.minio_client.put_object(
            self.bronze_bucket,
            filename,
            BytesIO(json_data),
            len(json_data),
            content_type='application/json'
        )
        
        logger.success(f"💾 Batch [{source}] : {len(articles)} articles → bronze/{filename}")

    def run(self, max_messages: int = None, timeout_ms: int = 10000):
        """
        Consomme les messages Kafka et stocke en micro-batches.
        
        Args:
            max_messages: limite de messages à consommer (None = infini)
            timeout_ms: timeout d'attente entre messages
        """
        logger.info(f"🚀 Démarrage du consumer (max: {max_messages or 'infini'})")
        
        try:
            for message in self.consumer:
                self.total_processed += 1
                event = message.value
                source = event.get('source', 'unknown')
                
                # Ajouter au buffer de la source
                self.buffer[source].append(event)
                
                logger.info(
                    f"  📥 [{source}] partition={message.partition} offset={message.offset} | "
                    f"{event.get('title', '')[:60]}"
                )
                
                # Si batch atteint, flusher
                if len(self.buffer[source]) >= self.batch_size:
                    self.save_batch_to_bronze(source, self.buffer[source])
                    self.buffer[source] = []
                
                # Limite atteinte
                if max_messages and self.total_processed >= max_messages:
                    logger.info(f"Limite de {max_messages} messages atteinte")
                    break
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️ Arrêt utilisateur")
        finally:
            # Flusher tous les buffers restants
            for source, articles in self.buffer.items():
                if articles:
                    self.save_batch_to_bronze(source, articles)
            
            self.consumer.close()
            logger.success(
                f"🎉 Consumer terminé. "
                f"Total processés : {self.total_processed} messages"
            )


if __name__ == "__main__":
    # Mode test : consommer 50 messages max
    consumer = KafkaToBronzeConsumer(batch_size=10)
    consumer.run(max_messages=50)