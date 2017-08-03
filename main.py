from multiprocessing import Process,Queue
from json import load as JLoad
from os import path as osPath, getcwd, mkdir
import gui

class EventManager:
    def __init__(self, eventQ):
        # 事件管理器开关
        self.__active = False
        self.handlers = ['tumblr', 'sys']
        self.eventQ = eventQ

    def __Run(self):
        """引擎运行"""
        while self.__active == True:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self.eventQ.get(timeout = 1)
                if event['type_'] == 'sys' and event['event_'] == 'close_app':
                    self.Stop()
                    break
                self.__EventProcess(event)
            except Exception as e:
                pass
    def __EventProcess(self, event):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if event['type_'] in self.handlers:
            # print(event['type_'], event['event_'])
            eval(event['event_'])()
    def Start(self):
        """启动"""
        # 将事件管理器设为启动
        self.__active = True
        self.__Run()
    def Stop(self):
        """停止"""
        # 将事件管理器设为停止
        self.__active = False
        # 等待事件处理线程退出
        # self.__thread.join()

class MainForm(object):
    """docstring for ClassName"""
    def __init__(self, imgListQ, eventQ, eventManager ):
        super(MainForm, self).__init__()
        self.imgListQ = imgListQ
        self.eventQ = eventQ
        self.eventManager = eventManager

    def initCfg(self):
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

    def run_app(self):
        self.cfg = self.initCfg()
        Process(target = gui.run_app, args = ( self.imgListQ, self.eventQ, self.cfg )).start()
        self.eventManager.Start()

funMap = {
    'tumblr':{
        'getDashboards':TumblrFun.getDashboards
    }
}
class TumblrFun:
    """docstring for ClassName"""
    def __init__(self, arg):
        self.arg = arg
    def getDashboards():
        pass
        
# def getDashboards():
#     print('getDashboards')
#     pass


if __name__ == '__main__':
    eventQ = Queue()
    imgListQ = Queue()
    eventManager = EventManager( eventQ )
    main = MainForm( imgListQ, eventQ, eventManager )
    main.run_app()