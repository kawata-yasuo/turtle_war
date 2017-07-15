#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
import rospkg
import random
import time

from abstractBot import *
from geometry_msgs.msg import Twist

class BoringBot(AbstractBot):

    def imageCallback(self, data):
        try:
            bgr_image = self.bridge.imgmsg_to_cv2(data, 'bgr8')
            original_height, original_width, original_channels = bgr_image.shape
            rectangle_image = bgr_image[int(original_height*0):original_height, int(original_width*0.4):int(original_width*0.8)]
            rectangle_height, rectangle_width, rectangle_channels = rectangle_image.shape
            similarity_record = 0
            total_similarity = 0
            turning_threshold = 0.001
            for h in range(rectangle_height):
                for w in range(rectangle_width):
                    target_similarity = 0
                    target_blue = float(rectangle_image[h, w, 0]) / 255
                    target_green = float(rectangle_image[h, w, 1]) / 255
                    target_red = float(rectangle_image[h, w, 2]) / 255
                    if target_red - target_blue > 0:
                        target_similarity += target_red - target_blue
                    if target_green - target_blue > 0:
                        target_similarity += target_green - target_blue
                    similarity_record += target_similarity
            total_similarity = float(similarity_record) / (rectangle_height * rectangle_width)
            if total_similarity >= turning_threshold:
                self.turning_point = False
            else:
                self.turning_point = True
            print(str(total_similarity))
            cv2.imshow("Image window", rectangle_image)
        except CvBridgeError as e:
            print(e)

        cv2.waitKey(3)

    def strategy(self):
        r = rospy.Rate(100)

        control_speed = 0
        control_turn = 0

        UPDATE_FREQUENCY = 1
        update_time = 0

        while not rospy.is_shutdown():
            if self.center_bumper or self.left_bumper or self.right_bumper or self.turning_point:
                update_time = time.time()
                control_speed = 0
                control_turn = 0.5

            #elif time.time() - update_time > UPDATE_FREQUENCY:
            else:
                update_time = time.time()
                control_speed = 0.5
                control_turn = 0

            twist = Twist()
            twist.linear.x = control_speed; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = control_turn
            self.vel_pub.publish(twist)

            r.sleep()


if __name__ == '__main__':
    rospy.init_node('boring_bot')
    bot = BoringBot('Boring')
    bot.strategy()
