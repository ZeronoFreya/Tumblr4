import sciter
import ctypes
# from json import load as JLoad
# from win32con import WM_USER
# from os import path as osPath, getcwd, mkdir as osMkdir
from threading import Thread
from EventManager import EventManager

ctypes.windll.user32.SetProcessDPIAware(2)

class GuiCallBack(object):
    """docstring for ClassName"""
    def __init__(self, funCall):
        self.funCall = funCall

    def tumblr__appendImg(self, d):
        return self.funCall('appendImgLoading', d )

    def tumblr__setImgId(self, d):
        return self.funCall('setImgId', d['id'], d['imgid'], d['preview'], d['download'] )
    def tumblr__setImgIdOver(self, d):
        return self.funCall('setImgIdOver')
    def tumblr__setImgBg(self, d):
        return self.funCall('setImgBg', d['id'], d['fpath'] )
    def tumblr__setPreview(self, d):
        return self.funCall('setPreview', d['id'], d['fpath'] )
    def tumblr__downloaded(self, d):
        return self.funCall('downloaded', d['id'], d['fpath'], d['module'])
    def tumblr__timeout(self, d):
        return self.funCall('timeout', d['id'], d['http'], d['module'] )
    def tumblr__statusBar(self, d):
        return self.funCall('statusInfo', d['text'] )


def queueLoop( _GuiRecvMsg, funCall ):
    guiCallBack = GuiCallBack( funCall )
    # _EventListenerMap
    # _ELM = {
    #     'tumblr':[
    #         'tumblr__appendImg',
    #         'tumblr__setImgId',
    #         'tumblr__setImgIdOver',
    #         'tumblr__setImgBg',
    #         'tumblr__setPreview',
    #         'downloaded',
    #         'timeout',
    #         'statusBar',
    #     ]
    # }
    # funMap = {}
    # for k in _ELM:
    #     funMap[k] = {}
    #     for v in _ELM[k]:
    #         funMap[k][v] = getattr(guiCallBack, v)

    handlers = ['tumblr', 'sys']
    EventManager( _GuiRecvMsg, handlers, guiCallBack ).Start()


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
            'event_' : 'init'
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
    def getPreviewSize(self, id, preview, download):
        self.CtrlRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'getPreviewSize',
            'data_' : {
                'id': str(id).strip('"'),
                'preview_size' : str(preview).strip('"'),
                'original_size' : str(download).strip('"')
            }
        })

    def downloadImg(self, id, download):
        self.CtrlRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'downloadImg',
            'data_' : {
                'id': str(id).strip('"'),
                'download' : str(download).strip('"')
            }
        })

    def refreshTimeoutImg(self, id, thumbnails):
        self.CtrlRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'refreshTimeoutImg',
            'data_' : {
                'id': str(id).strip('"'),
                'alt_size' : str(thumbnails).strip('"')
            }
        })

def run_app( cfg, _GuiRecvMsg, _CtrlRecvMsg ):
    frame = Frame( cfg, _GuiRecvMsg, _CtrlRecvMsg )
    frame.load_file("Gui/main.html")
    frame.run_app()