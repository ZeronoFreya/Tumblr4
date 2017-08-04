# from multiprocessing import Process,Queue
# import TumblrManager

class TumblrFun:
    """docstring for ClassName"""
    def __init__(self, imgListQ, _GuiRecvMsg, cfg, proxies):
        self.imgListQ = imgListQ
        self.GuiRecvMsg = _GuiRecvMsg
        self.cfg = cfg
        self.proxies = proxies
        pass
    def initTumblr(self):
        print('initTumblr')
        # Process(target = TumblrManager.initTumblr, args = ( self.imgListQ, self.cfg, self.proxies )).start()
        return self.getDashboards()

    def getDashboards(self):
        print('getDashboards')
        html = ''
        limit = self.cfg['dashboard_param']['limit']
        i = 0
        while i < limit:
            html += '<li.loading imgid="' + str(i) + '"></li>'
            i += 1
        self.GuiRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'appendImg',
            'data_' : html
        })