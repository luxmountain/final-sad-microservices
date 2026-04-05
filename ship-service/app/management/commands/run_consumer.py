import json
import logging
import time
from django.core.management.base import BaseCommand
from app.models import Shipment
from app.rabbitmq_utils import get_connection, publish_message
import pika

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Chạy RabbitMQ Consumer cho Ship Service'

    def handle(self, *args, **options):
        # Đợi một chút để RabbitMQ và DB khởi động xong
        time.sleep(5)
        
        try:
            connection = get_connection()
            channel = connection.channel()

            # Khai báo queue cần lắng nghe
            channel.queue_declare(queue='shipping_queue', durable=True)
            self.stdout.write(self.style.SUCCESS('🚚 Vui lòng chờ... Ship Service đang túc trực tại kênh "shipping_queue"'))

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body)
                    order_id = payload.get('order_id')
                    customer_address = payload.get('customer_address')
                    shipping_method_id = payload.get('shipping_method_id')

                    logger.info(f"Nhận được yêu cầu vận chuyển cho Đơn hàng #{order_id}")

                    # --- GIẢ LẬP LỖI SHIP (ĐỂ TEST HOÀN TIỀN SAGA) ---
                    # Nếu địa chỉ có chữ 'fail', cố tình báo lỗi "Cháy kho"
                    if customer_address and 'fail' in customer_address.lower():
                        logger.error(f"❌ CHÁY KHO!!! Không thể đóng gói Đơn hàng #{order_id}")
                        event = {
                            "event_type": "ShippingFailed",
                            "order_id": order_id
                        }
                        publish_message('order_queue', event)
                    else:
                        # 1. Tạo đơn vị Ship hàng (Lưu DB)
                        Shipment.objects.create(order_id=order_id, status='PREPARING')
                        logger.info(f"✅ Đã đóng gói thành công Đơn hàng #{order_id}")

                        # 2. Báo cáo lại cho Nhạc trưởng trên kênh "order_queue"
                        event = {
                            "event_type": "ShippingReserved",
                            "order_id": order_id
                        }
                        publish_message('order_queue', event)

                    # Đánh dấu đã xử lý tin nhắn
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý vận chuyển: {e}")
                    # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='shipping_queue', on_message_callback=callback)
            
            channel.start_consuming()

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Đã dừng đột ngột.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Kết nối thất bại: {e}'))
