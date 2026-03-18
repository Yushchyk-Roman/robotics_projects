"""Figure-8 path using timed motion (Circle Left + Circle Right)."""
import time
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped

class Figure8Path(Node):
    def __init__(self):
        super().__init__('figure_8_path')

        self.declare_parameter("linear_speed", 0.3)
        self.declare_parameter("angular_speed", 0.3)
        self.declare_parameter("rate_hz", 20.0)

        self.pub = self.create_publisher(TwistStamped, "/cmd_vel", 10)

        v = float(self.get_parameter("linear_speed").value)
        w = float(self.get_parameter("angular_speed").value)
        dt = 1.0 / max(float(self.get_parameter("rate_hz").value), 1.0)

        duration_one_circle = (2.0 * math.pi / max(abs(w), 1e-6)) + 6.0

        self.get_logger().info(f"Starting Normal Figure-8. Each circle takes {duration_one_circle:.2f}s")

        msg = TwistStamped()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = v

        self.get_logger().info("Circle 1/2: Turning LEFT")
        msg.twist.angular.z = abs(w)
        t_end = time.time() + duration_one_circle
        
        while time.time() < t_end:
            msg.header.stamp = self.get_clock().now().to_msg()
            self.pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(dt)

        self.get_logger().info("Circle 2/2: Turning RIGHT")
        msg.twist.angular.z = -abs(w)
        t_end = time.time() + duration_one_circle
        
        while time.time() < t_end:
            msg.header.stamp = self.get_clock().now().to_msg()
            self.pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(dt)

        self.pub.publish(TwistStamped())
        self.get_logger().info("Figure-8 complete! Robot stopped.")

def main(args=None):
    rclpy.init(args=args)
    node = Figure8Path()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()