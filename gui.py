import sciter
import ctypes
# from json import load as JLoad
# from win32con import WM_USER
# from os import path as osPath, getcwd, mkdir as osMkdir
from threading import Thread

ctypes.windll.user32.SetProcessDPIAware(2)

def queueLoop( _GuiRecvMsg, funCall ):
    while 1:
        try:
            # 获取事件的阻塞时间设为1秒
            event = _GuiRecvMsg.get(timeout = 1)
            if event['type_'] == 'sys' and event['event_'] == 'close_app':
                break
            if event['type_'] == 'tumblr' and event['event_'] == 'appendImg':
                funCall('appendImgLoading', event.get('data_', '') )
        except Exception as e:
            pass

class Frame(sciter.Window):

    def __init__(self, _GuiSendMsg, cfg, _GuiRecvMsg):
        '''
            ismain=False, ispopup=False, ischild=False, resizeable=True,
            parent=None, uni_theme=False, debug=True,
            pos=None,  pos=(x, y)
            size=None
        '''
        super().__init__(ismain=True, debug=True)
        self.set_dispatch_options(enable=True, require_attribute=False)
        self.GuiSendMsg = _GuiSendMsg
        self.GuiRecvMsg = _GuiRecvMsg
        self.cfg = cfg
        Thread(target=queueLoop, args=( self.GuiRecvMsg, self.call_function )).start()

    def document_close(self):
        # print("close")
        self.GuiSendMsg.put({
            'type_' : 'sys',
            'event_' : 'close_app'
        })
        self.GuiRecvMsg.put({
            'type_' : 'sys',
            'event_' : 'close_app'
        })
        return True

    ####################################################  Tumblr
    def initTumblr(self):
        # print('initTumblr')
        self.GuiSendMsg.put({
            'type_' : 'tumblr',
            'event_' : 'initTumblr'
        })
        # self.tumblrCtrl = TumblrCtrl({
        #     'call'          : self.call_function,
        #     'cfg'           : self.cfg['tumblr'],
        #     'Gui_HWND'      : self.hwnd,
        #     'proxies'       : self.cfg['proxies']
        # })
        # return self.getDashboards()

    # def getDashboards(self):
    #     self.tumblrCtrl.getDashboards()

def run_app( imgListQ, _GuiSendMsg, cfg, _GuiRecvMsg ):
    frame = Frame( _GuiSendMsg, cfg, _GuiRecvMsg )
    frame.load_file("Gui/main.html")
    frame.run_app()