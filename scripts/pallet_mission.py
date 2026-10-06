#!/usr/bin/env python3
"""
Автопилот складского робота:
1. Выравнивание траектории строго по створу поддона (y = 0.0)
2. Полный заезд под европоддон (до центра x = 2.50 м)
3. Подъем пневмоплатформы (+35 мм)
4. Удержание и опускание
5. Выезд задним ходом в исходную точку
"""
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry

def get_yaw(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))

class PalletAutopilot(Node):
    def __init__(self):
        super().__init__('pallet_autopilot')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lift_pub = self.create_publisher(Float64, '/lift_cmd', 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.odom_ready = False

        self.state = 'APPROACH'
        self.step_timer = 0

        # Таймер цикла управления 20 Гц
        self.create_timer(0.05, self.control_loop)
        self.get_logger().info('=== АВТОПИЛОТ ГОТОВ К РАБОТЕ ===')

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.yaw = get_yaw(msg.pose.pose.orientation)
        self.odom_ready = True

    def send_cmd(self, vx, wz):
        t = Twist()
        t.linear.x = float(vx)
        t.angular.z = float(wz)
        self.cmd_pub.publish(t)

    def set_lift(self, height):
        m = Float64()
        m.data = float(height)
        self.lift_pub.publish(m)

    def control_loop(self):
        # Если одометрия ещё не пришла, робот плавно трогается вперед для инициализации
        if not self.odom_ready:
            self.send_cmd(0.05, 0.0)
            return

        # 1. Подъезд к поддону с точным П-регулированием курса в створ тоннеля
        if self.state == 'APPROACH':
            w_corr = -1.8 * self.y - 1.2 * self.yaw
            w_corr = max(-0.3, min(0.3, w_corr))

            if self.x < 1.8:
                self.send_cmd(0.20, w_corr)
            else:
                self.get_logger().info('>> Робот подошел к поддону. Начало полного заезда...')
                self.state = 'DRIVE_UNDER'

        # 2. Медленный заезд внутрь поддона до точки x = 2.50 (робот полностью скрывается под ним)
        elif self.state == 'DRIVE_UNDER':
            w_corr = -1.5 * self.y - 1.0 * self.yaw
            w_corr = max(-0.15, min(0.15, w_corr))

            if self.x < 2.50:
                self.send_cmd(0.10, w_corr)
            else:
                self.send_cmd(0.0, 0.0)
                self.get_logger().info(f'>> Робот ПОЛНОСТЬЮ заехал под поддон (x={self.x:.2f} м)!')
                self.state = 'LIFT_UP'
                self.step_timer = 0

        # 3. Надувание пневмоподушки / подъем площадки (+35 мм)
        elif self.state == 'LIFT_UP':
            self.send_cmd(0.0, 0.0)
            self.set_lift(0.035)
            self.step_timer += 1
            if self.step_timer == 1:
                self.get_logger().info('>> Подъем пневмоподъемника: отрыв поддона от пола...')
            elif self.step_timer > 80:  # 4 секунды на подъем и стабилизацию
                self.state = 'LIFT_DOWN'
                self.step_timer = 0

        # 4. Сброс давления / опускание площадки в исходное состояние 0 мм
        elif self.state == 'LIFT_DOWN':
            self.send_cmd(0.0, 0.0)
            self.set_lift(0.0)
            self.step_timer += 1
            if self.step_timer == 1:
                self.get_logger().info('>> Опускание поддона на пол...')
            elif self.step_timer > 60:  # 3 секунды на опускание
                self.state = 'DRIVE_BACK'
                self.get_logger().info('>> Выезд робота из-под поддона...')

        # 5. Выезд задним ходом в исходное положение
        elif self.state == 'DRIVE_BACK':
            w_corr = 1.0 * self.y - 0.5 * self.yaw
            w_corr = max(-0.2, min(0.2, w_corr))

            if self.x > 0.3:
                self.send_cmd(-0.18, w_corr)
            else:
                self.send_cmd(0.0, 0.0)
                self.get_logger().info('=== МИССИЯ УСПЕШНО ЗАВЕРШЕНА! РОБОТ ВЕРНУЛСЯ ===')
                self.state = 'FINISHED'

        elif self.state == 'FINISHED':
            self.send_cmd(0.0, 0.0)

def main():
    rclpy.init()
    node = PalletAutopilot()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.send_cmd(0.0, 0.0)
    node.set_lift(0.0)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
