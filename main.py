from multiprocessing import Process,Queue
from json import load as JLoad
from os import path as osPath, getcwd, mkdir
import gui
from EventManager import EventManager
from FunManager import TumblrFun


class MainForm(object):
    """docstring for ClassName"""
    def __init__(self, imgListQ, eventQ, eventManager, cfg ):
        super(MainForm, self).__init__()
        self.imgListQ = imgListQ
        self.eventQ = eventQ
        self.eventManager = eventManager
        self.cfg = cfg

    def run_app(self):
        Process(target = gui.run_app, args = ( self.imgListQ, self.eventQ, self.cfg )).start()
        self.eventManager.Start()

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
    eventQ = Queue()
    imgListQ = Queue()
    cfg = initCfg()
    tumblrFun = TumblrFun( imgListQ, cfg['tumblr'], cfg['proxies'] )
    funMap = {
        'tumblr':{
            'initTumblr':tumblrFun.initTumblr,
            'getDashboards':tumblrFun.getDashboards
        }
    }

    eventManager = EventManager( eventQ, funMap )
    main = MainForm( imgListQ, eventQ, eventManager, cfg )
    main.run_app()