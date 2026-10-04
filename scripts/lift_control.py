#!/usr/bin/env python3
"""Скрипт для управления пневмоподъёмником."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time

class LiftControl(Node):
    def __init__(self):
        super().__init__('lift_control')
        self.publisher = self.create_publisher(Float64, '/lift_cmd', 10)
        
    def lift(self, height):
        """Поднять на высоту (в метрах)."""
        msg = Float64()
        msg.data = float(height)
        self.publisher.publish(msg)
        self.get_logger().info(f'Подъём на {height*1000:.1f} мм')
        
    def lower(self):
        """Опустить."""
        msg = Float64()
        msg.data = 0.0
        self.publisher.publish(msg)
        self.get_logger().info('Опускание')

def main():
    rclpy.init()
    node = LiftControl()
    
    print("\n=== Управление подъёмником ===")
    print("1 - Поднять на 30 мм")
    print("2 - Поднять на 50 мм (максимум)")
    print("3 - Опустить")
    print("4 - Цикл: поднять-подождать-опустить")
    print("q - Выход\n")
    
    while True:
        cmd = input("Введите команду: ")
        
        if cmd == '1':
            node.lift(0.03)
            time.sleep(2)
        elif cmd == '2':
            node.lift(0.05)
            time.sleep(2)
        elif cmd == '3':
            node.lower()
            time.sleep(2)
        elif cmd == '4':
            print("Цикл: подъём...")
            node.lift(0.03)
            time.sleep(5)
            print("Цикл: опускание...")
            node.lower()
            time.sleep(3)
        elif cmd == 'q':
            break
        else:
            print("Неизвестная команда")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
