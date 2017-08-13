
from EventManager import EventManager
from FunManager import ServiceEvent

class MainForm(object):
    def __init__(self, cfg, _GuiRecvMsg, _CtrlRecvMsg ):
        super(MainForm, self).__init__()
        # self.imgListQ = imgListQ
        self.cfg = cfg
        self.GuiRecvMsg = _GuiRecvMsg
        # self.CtrlSendMsg = _CtrlSendMsg
        self.CtrlRecvMsg = _CtrlRecvMsg

    # def __initFunMap(self):
    #     tumblrFun = TumblrFun( self.cfg['tumblr'], self.GuiRecvMsg, self.cfg['proxies'], self.cfg['imgTemp'], self.cfg['imgSave'] )
    #     return {
    #         'tumblr':{
    #             'initTumblr':tumblrFun.initTumblr,
    #             'getDashboards':tumblrFun.getDashboards,
    #             'getPreviewSize':tumblrFun.getPreviewSize,
    #             'refreshTimeoutImg':tumblrFun.refreshTimeoutImg,
    #             'downloadImg':tumblrFun.downloadImg
    #         }
    #     }

    def run_app(self):
        funMap = ServiceEvent( self.cfg['tumblr'], self.GuiRecvMsg, self.cfg['proxies'], self.cfg['imgTemp'], self.cfg['imgSave'] )
        handlers = ['tumblr', 'sys']
        return EventManager( self.CtrlRecvMsg, handlers, funMap ).Start()

def run_app( cfg, _GuiRecvMsg, _CtrlRecvMsg ):
    main = MainForm( cfg, _GuiRecvMsg, _CtrlRecvMsg )
    main.run_app()