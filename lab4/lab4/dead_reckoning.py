import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped


class DeadReckoningNode(Node):
    def __init__(self):
        super().__init__("dead_reckoning")

        self.declare_parameter("cmd_vel_topic", "/cmd_vel")
        self.declare_parameter("ground_truth_topic", "/odom")
        self.declare_parameter("path_dr_topic", "/path_dr")
        self.declare_parameter("frame_id", "odom")
        self.declare_parameter("max_poses", 2000)

        cmd_topic = self.get_parameter("cmd_vel_topic").value
        gt_topic = self.get_parameter("ground_truth_topic").value
        path_topic = self.get_parameter("path_dr_topic").value
        self.frame_id = self.get_parameter("frame_id").value
        self.max_poses = int(self.get_parameter("max_poses").value)

        self.create_subscription(TwistStamped, cmd_topic, self.cmd_callback, 10)
        self.create_subscription(Odometry, gt_topic, self.gt_callback, 10)
        self.pub_path = self.create_publisher(Path, path_topic, 10)

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_time = None

        self.gt_x = 0.0
        self.gt_y = 0.0
        self.gt_theta = 0.0
        
        self.path_msg = Path()
        self.path_msg.header.frame_id = self.frame_id

    def cmd_callback(self, msg: TwistStamped):
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        if self.last_time is None:
            self.last_time = current_time
            return
        
        dt = current_time - self.last_time
        self.last_time = current_time

        v = msg.twist.linear.x
        w = msg.twist.angular.z

        self.x = self.x + (v * dt * math.cos(self.theta))
        self.y = self.y + (v * dt * math.sin(self.theta))
        self.theta = self.theta + (w * dt)

        pose = PoseStamped()
        pose.header.stamp = msg.header.stamp
        pose.header.frame_id = self.frame_id
        pose.pose.position.x = self.x
        pose.pose.position.y = self.y
        
        pose.pose.orientation.z = math.sin(self.theta / 2.0)
        pose.pose.orientation.w = math.cos(self.theta / 2.0)

        self.path_msg.poses.append(pose)
        if len(self.path_msg.poses) > self.max_poses:
            self.path_msg.poses.pop(0)

        self.pub_path.publish(self.path_msg)

    def gt_callback(self, msg: Odometry):
        self.gt_x = msg.pose.pose.position.x
        self.gt_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.gt_theta = math.atan2(siny, cosy)

        error_x = self.x - self.gt_x
        error_y = self.y - self.gt_y
        drift_distance = math.sqrt(error_x**2 + error_y**2)

        self.get_logger().info(f"Drift: {drift_distance:.3f}m | X error: {error_x:.3f}, Y error: {error_y:.3f}", throttle_duration_sec=1.0)


def main(args=None):
    rclpy.init(args=args)
    node = DeadReckoningNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()