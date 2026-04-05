import json
import logging
import time
from django.core.management.base import BaseCommand
from app.models import Payment
from app.rabbitmq_utils import get_connection, publish_message
import pika

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Chạy RabbitMQ Consumer cho Pay Service'

    def handle(self, *args, **options):
        # Đợi một chút để RabbitMQ và DB khởi động xong
        time.sleep(5)
        
        try:
            connection = get_connection()
            channel = connection.channel()

            # Khai báo queue cần lắng nghe
            channel.queue_declare(queue='payment_queue', durable=True)
            self.stdout.write(self.style.SUCCESS('📦 Vui lòng chờ... Pay Service đang lắng nghe Mệnh lệnh từ Order Service trên kênh "payment_queue"'))

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body)
                    order_id = payload.get('order_id')
                    amount = payload.get('amount')
                    customer_address = payload.get('customer_address')
                    shipping_method_id = payload.get('shipping_method_id')

                    logger.info(f"Nhận được yêu cầu thanh toán cho Đơn hàng #{order_id}")

                    # 1. Thực hiện thanh toán (Lưu DB)
                    Payment.objects.create(order_id=order_id, amount=amount, status='SUCCESS')
                    logger.info(f"✅ Đã thanh toán thành công Đơn hàng #{order_id}")

                    # 2. Báo cáo lại cho Nhạc trưởng trên kênh "order_queue"
                    event = {
                        "event_type": "PaymentReserved",
                        "order_id": order_id,
                        "customer_address": customer_address,
                        "shipping_method_id": shipping_method_id
                    }
                    publish_message('order_queue', event)

                    # Đánh dấu đã xử lý tin nhắn
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý thanh toán: {e}")
                    # Nếu lỗi, có thể reject message để RabbitMQ biết mà đẩy lại cho thằng khác
                    # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            # Lắng nghe (auto_ack=False để đảm bảo xử lý xong mới xóa tin)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='payment_queue', on_message_callback=callback)
            
            # --- THÊM LISTENER LẮNG NGHE LỆNH HOÀN TIỀN TỪ NHẠC TRƯỞNG ---
            channel.queue_declare(queue='payment_refund_queue', durable=True)
            def refund_callback(ch, method, properties, body):
                try:
                    payload = json.loads(body)
                    order_id = payload.get('order_id')
                    
                    logger.info(f"⚠️ Nhận yêu cầu HOÀN TIỀN cho Đơn hàng #{order_id} do lỗi bên bộ phận Ship!")
                    
                    # 1. Tìm lại phiên giao dịch cũ
                    try:
                        payment = Payment.objects.get(order_id=order_id, status='SUCCESS')
                        # 2. Hoàn tiền 
                        payment.status = 'REFUNDED'
                        payment.save()
                        logger.info(f"💸 Đã HOÀN TIỀN thành công cho Đơn hàng #{order_id}")
                    except Payment.DoesNotExist:
                        logger.error(f"Không tìm thấy giao dịch thành công nào của Đơn #{order_id} để hoàn tiền.")

                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý hoàn tiền: {e}")
            
            channel.basic_consume(queue='payment_refund_queue', on_message_callback=refund_callback)

            channel.start_consuming()

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Đã dừng đột ngột.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Kết nối thất bại: {e}'))
