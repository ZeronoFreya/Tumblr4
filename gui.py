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
            elif event['type_'] == 'tumblr' and event['event_'] == 'setImgId':
                d = event.get('data_', '')
                if d:
                    funCall('setImgId', d['id'], d['imgid'], d['preview'] )
            elif event['type_'] == 'tumblr' and event['event_'] == 'setImgIdOver':
                funCall('setImgIdOver')
            elif event['type_'] == 'tumblr' and event['event_'] == 'setImgBg':
                d = event.get('data_', '')
                if d:
                    funCall('setImgBg', d['id'], d['fpath'] )
            elif event['type_'] == 'tumblr' and event['event_'] == 'setPreview':
                d = event.get('data_', '')
                if d:
                    funCall('setPreview', d['id'], d['fpath'] )
            elif event['type_'] == 'tumblr' and event['event_'] == 'timeout':
                d = event.get('data_', '')
                if d:
                    funCall('timeout', d['id'], d['module'] )
        except Exception as e:
            pass

class Frame(sciter.Window):

    def __init__(self, cfg, _GuiRecvMsg, _CtrlRecvMsg):
        '''
            ismain=False, ispopup=False, ischild=False, resizeable=True,
            parent=None, uni_theme=False, debug=True,
            pos=None,  pos=(x, y)
            size=None
        '''
        super().__init__(ismain=True, debug=True)
        self.set_dispatch_options(enable=True, require_attribute=False)
        # self.GuiSendMsg = _GuiSendMsg
        self.GuiRecvMsg = _GuiRecvMsg
        self.CtrlRecvMsg = _CtrlRecvMsg
        self.cfg = cfg
        Thread(target=queueLoop, args=( self.GuiRecvMsg, self.call_function )).start()

    def document_close(self):
        # print("close")
        # self.GuiSendMsg.put({
        #     'type_' : 'sys',
        #     'event_' : 'close_app'
        # })
        self.GuiRecvMsg.put({
            'type_' : 'sys',
            'event_' : 'close_app'
        })
        self.CtrlRecvMsg.put({
            'type_' : 'sys',
            'event_' : 'close_app'
        })
        return True

    ####################################################  Tumblr
    def initTumblr(self):
        # print('initTumblr')
        # self.GuiSendMsg.put({
        #     'type_' : 'tumblr',
        #     'event_' : 'initTumblr'
        # })
        self.CtrlRecvMsg.put({
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

    def getDashboards(self):
        self.CtrlRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'getDashboards'
        })
    def getPreviewSize(self, id, preview):
        self.CtrlRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'getPreviewSize',
            'data_' : {
                'id': str(id).strip('"'),
                'preview_size' : str(preview).strip('"')
            }
        })

def run_app( cfg, _GuiRecvMsg, _CtrlRecvMsg ):
    frame = Frame( cfg, _GuiRecvMsg, _CtrlRecvMsg )
    frame.load_file("Gui/main.html")
    frame.run_app()