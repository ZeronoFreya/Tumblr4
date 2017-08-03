from multiprocessing import Process,Queue
import TumblrManager

class TumblrFun:
    """docstring for ClassName"""
    def __init__(self, imgListQ, cfg, proxies):
        self.imgListQ = imgListQ
        self.cfg = cfg
        self.proxies = proxies
        pass
    def initTumblr(self):
        print('initTumblr')
        Process(target = TumblrManager.initTumblr, args = ( self.imgListQ, self.cfg, self.proxies )).start()
        pass
    def getDashboards(self):
        print('getDashboards')
        pass