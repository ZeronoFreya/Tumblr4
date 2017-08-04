from multiprocessing import Process,Queue
from json import load as JLoad
from os import path as osPath, getcwd, mkdir
import gui
import Controller


class MainForm(object):
    """docstring for ClassName"""
    def __init__(self, cfg, _GuiRecvMsg, _CtrlRecvMsg ):
        super(MainForm, self).__init__()
        # self.imgListQ = imgListQ
        # self.GuiSendMsg = _GuiSendMsg
        self.cfg = cfg
        self.GuiRecvMsg = _GuiRecvMsg
        # self.CtrlSendMsg = _CtrlSendMsg
        self.CtrlRecvMsg = _CtrlRecvMsg

    def run_app(self):
        print('ctrl')
        Process(target = Controller.run_app, args = ( self.cfg, self.GuiRecvMsg, self.CtrlRecvMsg )).start()
        print('gui')
        Process(target = gui.run_app, args = ( self.cfg, self.GuiRecvMsg, self.CtrlRecvMsg )).start()

        print('over')

def initCfg():
    cfg = {"tumblr":{"alt_sizes":-3,"preview_size":-4,"dashboard_param":{"limit":5,"offset":0},"posts_param":{"limit":5,"offset":0}},"proxies":"","imgTemp":"","imgSave":""}
    with open('data.json', 'r') as f:
        cfg.update( JLoad(f) )
    current_folder = getcwd()
    cfg['imgTemp'] = ( cfg['imgTemp'] or osPath.join( current_folder, 'imgTemp') )
    if not osPath.isdir( cfg['imgTemp'] ):
        mkdir(cfg['imgTemp'])
    cfg['imgSave'] = ( cfg['imgSave'] or osPath.join( current_folder, 'imgSave') )
    if not osPath.isdir( cfg['imgSave'] ):
        mkdir(cfg['imgSave'])
    return cfg

if __name__ == '__main__':
    '''
    http://www.cnblogs.com/kaituorensheng/p/4445418.html
    Pipe方法返回(conn1, conn2)代表一个管道的两个端。
    Pipe方法有duplex参数，如果duplex参数为True(默认值)，那么这个管道是全双工模式，也就是说conn1和conn2均可收发。
    duplex为False，conn1只负责接受消息，conn2只负责发送消息。
    '''
    # pipe = Pipe(duplex=False)
    # _GuiSendMsg = Queue()
    _GuiRecvMsg = Queue()
    # _CtrlSendMsg = Queue()
    _CtrlRecvMsg = Queue()
    # imgListQ = Queue()
    cfg = initCfg()

    # eventManager = EventManager( _GuiSendMsg, funMap )
    main = MainForm( cfg, _GuiRecvMsg, _CtrlRecvMsg )
    main.run_app()