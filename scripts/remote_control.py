#!/usr/bin/env python3
"""Интерактивный пульт управления роботом."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class RemoteControl(Node):
    def __init__(self):
        super().__init__('remote_control')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.lift_pub = self.create_publisher(Float64, '/lift_cmd', 10)

    def drive(self, v, w=0.0):
        t = Twist()
        t.linear.x = float(v)
        t.angular.z = float(w)
        self.cmd_pub.publish(t)

    def lift(self, h):
        m = Float64()
        m.data = float(h)
        self.lift_pub.publish(m)

def main():
    rclpy.init()
    node = RemoteControl()
    
    print("\n" + "="*50)
    print("🤖 ПУЛЬТ УПРАВЛЕНИЯ РОБОТОМ")
    print("="*50)
    print("🚗 ДВИЖЕНИЕ:")
    print("  w — Вперёд      s — Назад")
    print("  a — Влево       d — Вправо")
    print("  x — Стоп")
    print("\n🔧 ПОДЪЁМНИК:")
    print("  1 — Поднять 30мм   2 — Поднять 50мм")
    print("  0 — Опустить")
    print("\n🎯 МИССИИ:")
    print("  m — Авто-миссия 'Заезд под поддон'")
    print("\n  q — Выход")
    print("="*50 + "\n")
    
    while True:
        cmd = input("Команда: ").lower()
        
        if cmd == 'w':
            node.drive(0.2)
            print("⬆️ Вперёд")
        elif cmd == 's':
            node.drive(-0.2)
            print("⬇️ Назад")
        elif cmd == 'a':
            node.drive(0.0, 0.3)
            print("️ Влево")
        elif cmd == 'd':
            node.drive(0.0, -0.3)
            print("️ Вправо")
        elif cmd == 'x':
            node.drive(0.0)
            print("⏹️ Стоп")
        elif cmd == '1':
            node.lift(0.03)
            print("️ Подъём на 30мм")
        elif cmd == '2':
            node.lift(0.05)
            print("️ Подъём на 50мм (макс)")
        elif cmd == '0':
            node.lift(0.0)
            print("⬇️ Опущение")
        elif cmd == 'm':
            print(" Запуск авто-миссии... (откройте новый терминал)")
            print("   ros2 run robot_description pallet_mission.py")
        elif cmd == 'q':
            node.drive(0.0)
            node.lift(0.0)
            print("👋 Выход")
            break
        else:
            print("❌ Неизвестная команда")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
