import json
import logging
import time
from django.core.management.base import BaseCommand
from app.models import Order
from app.rabbitmq_utils import get_connection, publish_message
import pika

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Chạy RabbitMQ Consumer cho Order Service (Nhạc Trưởng)'

    def handle(self, *args, **options):
        time.sleep(5)
        
        try:
            connection = get_connection()
            channel = connection.channel()

            # Nhạc trưởng luôn lắng nghe ngóng trên loa order_queue
            channel.queue_declare(queue='order_queue', durable=True)
            self.stdout.write(self.style.SUCCESS('🎼 Vui lòng chờ... Order Service (Nhạc trưởng) sẵn sàng điều phối tại "order_queue"'))

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body)
                    event_type = payload.get('event_type')
                    order_id = payload.get('order_id')
                    
                    logger.info(f"Nhận báo cáo: [{event_type}] cho Đơn hàng #{order_id}")

                    # --- KỊCH BẢN 1: PAY THU TIỀN XONG ---
                    if event_type == "PaymentReserved":
                        # Chuyển lệnh giục Ship đi gói hàng
                        shipping_command = {
                            "order_id": order_id,
                            "customer_address": payload.get('customer_address'),
                            "shipping_method_id": payload.get('shipping_method_id')
                        }
                        publish_message('shipping_queue', shipping_command)
                        logger.info(f"Đã ra lệnh cho Ship Service chuẩn bị hàng cho Đơn #{order_id}")

                    # --- KỊCH BẢN 2: SHIP GÓI HÀNG XONG ---
                    elif event_type == "ShippingReserved":
                        # Đổi trạng thái chốt hạ! Thành công mỹ mãn!
                        try:
                            order = Order.objects.get(id=order_id)
                            order.status = 'PAID_AND_SHIPPING'
                            order.save()
                            logger.info(f"🎉 Saga hoàn tất! Đơn #{order_id} đã đổi sang PAID_AND_SHIPPING.")
                        except Order.DoesNotExist:
                            logger.error(f"Đơn hàng #{order_id} lặn đâu mất rồi?")

                    # ==============================================================
                    # KỊCH BẢN HỦY (ROLLBACK) SẴN SÀNG CHO TƯƠNG LAI
                    # ==============================================================
                    elif event_type == "PaymentFailed":
                        order = Order.objects.get(id=order_id)
                        order.status = 'CANCELLED'
                        order.save()
                        logger.error(f"Khách hết tiền! Hủy đơn #{order_id}")

                    elif event_type == "ShippingFailed":
                        # Nếu ship sập -> Phải bảo thằng Pay ói tiền (hoàn tiền)
                        refund_command = { "order_id": order_id }
                        publish_message('payment_refund_queue', refund_command)
                        
                        order = Order.objects.get(id=order_id)
                        order.status = 'CANCELLED'
                        order.save()
                        logger.error(f"Cháy kho! Đã hủy đơn #{order_id} và yêu cầu hoàn tiền.")

                    # Đánh dấu đã đọc báo cáo
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                except Exception as e:
                    logger.error(f"Lỗi khi điều phối Saga: {e}")

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='order_queue', on_message_callback=callback)
            
            channel.start_consuming()

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Nhạc trưởng đã đi ngủ.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Kết nối thất bại: {e}'))
