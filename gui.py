import sciter
import ctypes
# from json import load as JLoad
# from win32con import WM_USER
# from os import path as osPath, getcwd, mkdir as osMkdir

ctypes.windll.user32.SetProcessDPIAware(2)

class Frame(sciter.Window):

    def __init__(self, eventQ, cfg):
        '''
            ismain=False, ispopup=False, ischild=False, resizeable=True,
            parent=None, uni_theme=False, debug=True,
            pos=None,  pos=(x, y)
            size=None
        '''
        super().__init__(ismain=True, debug=True)
        self.set_dispatch_options(enable=True, require_attribute=False)
        self.eventQ = eventQ
        self.cfg = cfg

    def document_close(self):
        # print("close")
        self.eventQ.put({
            'type_' : 'sys',
            'event_' : 'close_app'
        })
        return True

    ####################################################  Tumblr
    def initTumblr(self):
        # print('initTumblr')
        self.eventQ.put({
            'type_' : 'tumblr',
            'event_' : 'getDashboards'
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

def run_app( imgListQ, eventQ, cfg ):
    frame = Frame( eventQ, cfg )
    frame.load_file("Gui/main.html")
    frame.run_app()