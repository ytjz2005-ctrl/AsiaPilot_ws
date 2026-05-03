#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import threading

class ImageViewerNode:
    def __init__(self):
        rospy.init_node('image_viewer_node')

        self.bridge = CvBridge()
        self.color_image = None
        self.depth_image = None

        # 状态控制
        self.lock = threading.Lock()
        self.freeze = False
        self.fixed_frame = None
        self.selecting = False
        self.start_point = ()
        self.current_point = ()

        # 订阅图像
        self.color_sub = rospy.Subscriber('/camera/color/image_raw', Image, self.color_callback)
        self.depth_sub = rospy.Subscriber('/camera/depth/image_rect_raw', Image, self.depth_callback)

        cv2.namedWindow("RGB Image", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("RGB Image", self.mouse_callback)

        rospy.loginfo("Image Viewer Node with Mouse Callback Started")
        self.run()

    def color_callback(self, msg):
        if not self.freeze:
            try:
                image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                with self.lock:
                    self.color_image = image
            except Exception as e:
                rospy.logerr("Failed to convert color image: %s", e)

    def depth_callback(self, msg):
        try:
            self.depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as e:
            rospy.logerr("Failed to convert depth image: %s", e)

    def mouse_callback(self, event, x, y, flags, param):
        with self.lock:
            if event == cv2.EVENT_LBUTTONDOWN:
                if not self.selecting and self.color_image is not None:
                    self.selecting = True
                    self.start_point = (x, y)
                    self.current_point = (x, y)
                    self.fixed_frame = self.color_image.copy()
                    self.freeze = True  # 锁定画面
            elif event == cv2.EVENT_MOUSEMOVE and self.selecting:
                self.current_point = (x, y)
            elif event == cv2.EVENT_LBUTTONUP and self.selecting:
                self.selecting = False
                self.freeze = False  # 解锁画面
                end_point = (x, y)
                x0, y0 = self.start_point
                x1, y1 = end_point
                bbox = (min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0))
                rospy.loginfo("Selected ROI: x=%d, y=%d, w=%d, h=%d", *bbox)

    def run(self):
        rate = rospy.Rate(30)
        while not rospy.is_shutdown():
            with self.lock:
                if self.freeze and self.fixed_frame is not None:
                    frame = self.fixed_frame.copy()
                elif self.color_image is not None:
                    frame = self.color_image.copy()
                else:
                    rate.sleep()
                    continue

                if self.selecting and self.start_point and self.current_point:
                    cv2.rectangle(frame, self.start_point, self.current_point, (0, 255, 0), 2)

                cv2.imshow("RGB Image", frame)
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break

            rate.sleep()

        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        ImageViewerNode()
    except rospy.ROSInterruptException:
        pass
