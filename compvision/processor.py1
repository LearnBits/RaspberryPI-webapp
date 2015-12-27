import sys
import threading
import numpy as np
import cv2
import time
from Queue import Queue

from test_lbp import lbp_cascade
from test_haar import haar_cascade
from test_pedestrian import pedestrian
from color_motion_detect import color_motion_detect

__author__ = 'yonatan'
__project__ = 'video_base'

# Drawing parameters
fontFace = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 0.5
streamFrameNum = 0


class Processor(threading.Thread):
    def __init__(self, capturer, drawFrameNum = False):
        super(Processor, self).__init__()

        self.daemon = True
        self.images_by_process = {}
        self.results_by_process = {}
        self.capturer = capturer

        self.drawFrameNum = drawFrameNum

        self.available_processors = dict()

        self.available_processors['face'] = haar_cascade()
        self.available_processors['pedestrian'] = pedestrian()
        self.available_processors['color_motion_detect'] = color_motion_detect()

        #self.enabled_processors = set(('color_motion_detect',))
        self.enabled_processors = set()
        self.config_queue = Queue()

        self.frameNum = 0
        self.start()

    def run(self):
        while True:
            self.apply_configuration()
            self.capturer.new_frame.wait()
            captured_frame = self.capturer.get_last_frame()
            if (captured_frame is not None):
                self.process(captured_frame)
                self.frameNum = self.frameNum + 1
            self.capturer.new_frame.clear()


    def draw(self, image):
        text = "frame: %d" % self.frameNum
        cv2.putText(image, text = text, org = (10, 10), fontFace = fontFace, fontScale = fontScale, color = (0, 255, 0), thickness = 1)
        cv2.putText(image, text = "||", org = (10 + 10 * ((self.frameNum % 10) + 1), 30 + 10 * ((self.frameNum % 10) + 1)),
                    fontFace = fontFace, fontScale = 0.3, color = (0, 0, 255))


    def process(self, image):

        images_by_process = dict()
        results_by_process = dict()

        for processor_name in self.enabled_processors.copy():
            image_to_process = image.copy()
            processor = self.available_processors[processor_name]
            (processed_img, result) = processor.detect(image_to_process)

            if self.drawFrameNum:
                self.draw(processed_img)

            images_by_process[processor_name] = processed_img
            results_by_process[processor_name] = result

        self.images_by_process = images_by_process
        self.results_by_process = results_by_process

    def apply_configuration(self):
        while not self.config_queue.empty():
            (processor_name, configuration) = self.config_queue.get()
            if processor_name in self.available_processors:
                try:
                    self.available_processors[processor_name].configure(configuration)
                    # Method exists, and was used.  
                except AttributeError,e:
                    print e



    def get_processed_frame(self, processor_name):
        return self.images_by_process.get(processor_name,  None)

    def enable_processor(self, processor_name):
        if processor_name in self.available_processors:
            self.enabled_processors.add(processor_name)
        else:
            raise Exception("No such availble processor: " + processor_name)


    def disable_processor(self, processor_name):
        if processor_name in self.enabled_processors:
            self.enabled_processors.remove(processor_name)
        else:
            raise Exception("No such enabled processor: " + processor_name)

    def config_processor(self, processor_name, configuration):
        self.config_queue.put((processor_name, configuration))

    def get_results(self):
        return self.results_by_process

