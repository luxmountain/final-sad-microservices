import pika
import json
import logging

logger = logging.getLogger(__name__)

RABBITMQ_HOST = 'rabbitmq'

def get_connection():
    """Tạo kết nối tới RabbitMQ."""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    return pika.BlockingConnection(parameters)

def publish_message(queue_name, message):
    """
    Hàm tiện ích gửi tin nhắn vào một Queue cụ thể.
    """
    try:
        connection = get_connection()
        channel = connection.channel()

        # Đảm bảo queue có tồn tại (durable=True để không mất tin nhắn khi Rabbit bị restart)
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Tin nhắn sẽ được lưu vào ổ cứng (persistent)
            )
        )
        logger.info(f"Đã gửi tin nhắn tới {queue_name}: {message}")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Lỗi khi gửi RabbitMQ tới {queue_name}: {e}")
        return False
