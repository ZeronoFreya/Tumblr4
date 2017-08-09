# from multiprocessing import Queue
# import TumblrManager
import aiohttp
import asyncio
from threading import Thread
from os import path as osPath
from tumblpy import Tumblpy
from json import load as JLoad
from common import gets

# _GuiRecvMsg.put({
#     'type_' : 'tumblr',
#     'event_' : 'setPreview',
#     'data_' : {'id':d['id'],'fpath':file_path}
# })
async def stream_download( d, proxies, _GuiRecvMsg, _GuiRecvMsgDict, _Timeout ):
    '''协程下载列表中图片'''
    print('下载',d['id'])
    for x in range(0, 3):
        try:
            with aiohttp.Timeout(10):
                async with aiohttp.request( 'GET', d['http'], proxy=''.join(('http://', proxies)) ) as response:
                # async with client.get( d['http'], proxy=''.join(('http://', proxies)), timeout=10 ) as response:
                    if response.status != 200:
                        print('error')
                        return
                    print('200',d['id'])
                    with open(d['fpath'], 'ab') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
            _GuiRecvMsg.put(_GuiRecvMsgDict)
            return
        except asyncio.TimeoutError:

            continue
    _GuiRecvMsg.put(_Timeout)

class TumblrFun:
    """docstring for ClassName"""
    def __init__(self, tumblrCfg, _GuiRecvMsg, proxies, imgTemp):
        # self.imgListQ = imgListQ
        self.GuiRecvMsg = _GuiRecvMsg
        self.cfg = tumblrCfg
        self.proxies = proxies
        self.imgTemp = imgTemp
        self.imgList = []

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def initTumblr(self, data_=None):
        # print('initTumblr')
        with open('tumblr_credentials.json', 'r') as f:
            self.tumblr_key = JLoad(f)
        self.tumblr = Tumblpy(
            self.tumblr_key['consumer_key'],
            self.tumblr_key['consumer_secret'],
            self.tumblr_key['oauth_token'],
            self.tumblr_key['oauth_token_secret'],
            proxies={ "http": self.proxies, "https": self.proxies }
        )
        self.new_loop = asyncio.new_event_loop()
        t = Thread(target=self.start_loop, args=(self.new_loop,))
        t.setDaemon(True)    # 设置子线程为守护线程
        t.start()
        return self.getDashboards()

    def mkMainDict( self, d, preview_size, alt_sizes ):
        data = []
        for v in d["posts"]:
            t = {
                'link_url'        : gets(v, 'link_url', ''),
                'source_url'      : gets(v, 'source_url', '')
            }
            index = 1
            for i in v['photos']:
                t['id'] = str(v['id']) + '[' + str(index) + ']'
                t['original_size'] = gets(i, 'original_size.url', '')
                t['preview_size'] = gets(i, 'alt_sizes.' + str(preview_size) + '.url', '')
                t['alt_sizes'] = gets(i, 'alt_sizes.' + str(alt_sizes) + '.url', '')
                data.append(t.copy())
                index += 1
        return data

    def getDashboards(self, data_=None):
        print('getDashboards')
        imgid_list = self.__ImgPretreatment()
        limit = int( self.cfg['dashboard_param']['limit'] )
        # # print( len( self.imgList ), limit)
        if len( self.imgList ) < limit:
            self.getImgList()
        self.setImgList(imgid_list)
        self.GuiRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'setImgIdOver'
        })

    def getPreviewSize(self, d):
        '''获取预览大图'''
        print('getPreviewSize')
        file_name = d['id'] + '_' + d['preview_size'].split("_")[-1]
        file_path = osPath.join( self.imgTemp, file_name )
        _GuiRecvMsgDict = {
            'type_' : 'tumblr',
            'event_' : 'setPreview',
            'data_' : {'id':d['id'],'fpath':file_path}
        }
        _Timeout = {
            'type_' : 'tumblr',
            'event_' : 'timeout',
            'data_' : {'id':d['id'],'module':'"'.join(('#tumblr .list li[imgid=',d['id'],']'))}
        }
        if not osPath.isfile(file_path):
            asyncio.run_coroutine_threadsafe(stream_download(
                {'id': d['id'],'http': d['preview_size'],'fpath': file_path},
                self.proxies,
                self.GuiRecvMsg,
                _GuiRecvMsgDict,
                _Timeout
            ), self.new_loop)
        else:
            self.GuiRecvMsg.put(_GuiRecvMsgDict)

    def getImgList(self):
        '''获取图片列表'''
        print('getImgList')
        p = self.cfg['dashboard_param'].copy()
        p['limit'] *= 5
        # # print('p',p)
        # dashboard = tumblr.dashboard( param['dashboard_param'] )
        # dashboard = self.tumblr.posts('kuvshinov-ilya.tumblr.com', None, p)
        # if not dashboard:
        #     raise 'not dashboard'
        #     return
        try:
            # dashboard = self.tumblr.dashboard( p )
            dashboard = self.tumblr.posts('kuvshinov-ilya.tumblr.com', None, p)
            # # print('dashboard',dashboard)
        except Exception as e:
            print('err dashboard')
            return

        self.cfg['dashboard_param']['offset'] += p['limit']
        # # print(self.cfg)
        imgList = self.mkMainDict( dashboard, self.cfg['preview_size'], self.cfg['alt_sizes'] )
        # imgList = [{
        #     'link_url': 'xx',
        #     'source_url': '',
        #     'id': str( random.randint(1,999999) ),
        #     'original_size': 'xx',
        #     'preview_size': 'x',
        #     'alt_sizes': 'x'
        # }]
        for d in imgList:
            self.imgList.append( d )
        # # print(self.imgList)

    def setImgList(self, imgid_list):
        print('setImgList')
        # i = 0
        imgDict = []
        # while i < limit:
        for imgid in imgid_list:
            d = self.imgList.pop(0)
            # # print(d)
            self.GuiRecvMsg.put({
                'type_' : 'tumblr',
                'event_' : 'setImgId',
                'data_' : {
                    'id': d['id'],
                    'imgid': imgid,
                    'preview': d['preview_size']
                }
            })
            file_name = d['id'] + '_' + d['alt_sizes'].split("_")[-1]
            file_path = osPath.join( self.imgTemp, file_name )
            # # print(file_path)
            _GuiRecvMsgDict = {
                'type_' : 'tumblr',
                'event_' : 'setImgBg',
                'data_' : {'id':d['id'],'fpath':file_path}
            }
            _Timeout = {
                'type_' : 'tumblr',
                'event_' : 'timeout',
                'data_' : {'id':d['id'],'module':'"'.join(('#tumblr .view li[imgid=',d['id'],']'))}
            }
            if not osPath.isfile(file_path):
                asyncio.run_coroutine_threadsafe(stream_download(
                    {'id': d['id'],'http': d['alt_sizes'],'fpath': file_path},
                    self.proxies,
                    self.GuiRecvMsg,
                    _GuiRecvMsgDict,
                    _Timeout
                ), self.new_loop)
            else:
                # print('存在',d['id'])
                self.GuiRecvMsg.put(_GuiRecvMsgDict)
            # i += 1

    def __ImgPretreatment(self):
        html = ''
        limit = self.cfg['dashboard_param']['limit']
        i = 0
        imgid = []
        while i < limit:
            imgid.append( str(i) )
            html += '<li.loading imgid="' + str(i) + '"></li>'
            i += 1
        self.GuiRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'appendImg',
            'data_' : html
        })
        return imgid