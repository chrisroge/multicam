from distutils.command.build import build
import time
import threading
import queue
import cv2
import datetime
import random

img_cache = []

class VideoCapture:
    

    def __init__(self, name):
        
        self.cap = cv2.VideoCapture(name)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()



    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()   # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)



    def read(self):
        
        return self.q.get()



class GetLatestFrame:    

    def _frame(cap):

        image = cap.read()

        

        return image
