#!/usr/bin/env python
from __future__ import print_function

import roslib
#roslib.load_manifest('my_package')
import sys
import rospy
import cv2
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import os
import sys




class detect_logitech:

  def __init__(self):
    rospy.init_node('detect-logitech', anonymous=True)
    
    self.image_pub = rospy.Publisher("image_topic_2",Image)
   
    self.bridge = CvBridge()
    
    self.image_sub = rospy.Subscriber("/usb_cam/image_raw",Image,self.callback)
    rospy.spin()

  
    

  def callback(self,data):
    
    try:
      cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)

    (rows,cols,channels) = cv_image.shape
    print(rows)
    print(cols)
    cv_image = cv2.resize(cv_image,(480,640))
    
    try:
      self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv_image, "bgr8"))
    except CvBridgeError as e:
      print(e)

def main(args):
  ic = detect_logitech()
  
  
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
