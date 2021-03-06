#!/usr/bin/python
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import jetson.inference
import jetson.utils

import argparse
import sys

import rospy
from std_msgs.msg import Int16
from std_msgs.msg import Float32MultiArray
from nav_msgs.msg import Odometry


#def odometry_callback(data):
     
#    odom_det.pose.pose.position.x = data.pose.pose.position.x
#    odom_det.pose.pose.position.y = data.pose.pose.position.y
#    odom_det.pose.pose.position.z = data.pose.pose.position.z
    


# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
						   formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")

rospy.init_node("detection_publisher", anonymous=True)
detection_state_pub = rospy.Publisher("/detection_state_bool", Int16, queue_size = 1)
detection_location_pub = rospy.Publisher("/detection_location", Odometry, queue_size = 1)
bb_location_pub = rospy.Publisher("/bounding_box_location", Float32MultiArray, queue_size = 1)
detection_bool = Int16()
detection_bool = 0
global odom_det
odom_det = Odometry()
global bb_location
bb_location = Float32MultiArray()
detection_status = False
ros_rate = rospy.Rate(10)

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# create the camera and display
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
#display = jetson.utils.glDisplay()

# process frames until user exits
while True and not rospy.is_shutdown():
	# capture the image
	img, width, height = camera.CaptureRGBA()

	# detect objects in the image (with overlay)
	detections = net.Detect(img, width, height, opt.overlay)

	# print the detections
	print("detected {:d} objects in image".format(len(detections)))

	for detection in detections:
		print(detection)

        if not detection_status:
              odom_det = rospy.wait_for_message("/camera/odom/sample", Odometry, timeout=5.0)
        bb_location.data = []        

        if len(detections) > 0:
              detection_bool = 1
              detection_state_pub.publish(detection_bool)                   
              detection_location_pub.publish(odom_det)
              detection_status = True
              bb_location.data.append(detection.Top)
              bb_location.data.append(detection.Left)
              bb_location.data.append(detection.Width)
              bb_location.data.append(detection.Height)
              bb_location_pub.publish(bb_location)
              
              

        #else:
        #      detection_bool = 0
        #      detection_state_pub.publish(detection_bool)
        detection_state_pub.publish(detection_bool)
              

	# render the image
	#display.RenderOnce(img, width, height)

	# update the title bar
	#display.SetTitle("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

	# print out performance info
	net.PrintProfilerTimes()

