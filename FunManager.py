# from multiprocessing import Queue
# import TumblrManager
import aiohttp
import asyncio
from threading import Thread
from os import path as osPath
from tumblpy import Tumblpy
from json import load as JLoad
from common import gets

# def asyncImgList( _GuiRecvMsg, imgDict, proxies ):
#     '''协程下载列表中图片'''

#     async def stream_download( d, proxies ):
#         async with aiohttp.request('GET', d['http'], proxy=''.join(('http://', proxies))) as response:
#         # async with client.get( d['http'], proxy=''.join(('http://', proxies)), timeout=10 ) as response:
#             if response.status != 200:
#                 # print('error')
#                 return
#             with open(d['fpath'], 'ab') as file:
#                 while True:
#                     chunk = await response.content.read(1024)
#                     if not chunk:
#                         break
#                     file.write(chunk)
#         return {'id':d['id'],'fpath':d['fpath']}

#     # print('asyncImgList')
#     # client = aiohttp.ClientSession()
#     loop = asyncio.get_event_loop()
#     # try:
#     #     loop = asyncio.get_event_loop()
#     #     # if self.loop.is_running():
#     #     #     raise NotImplementedError("Cannot use aioutils in "
#     #     #                               "asynchroneous environment")
#     # except:
#     #     loop = asyncio.new_event_loop()
#     #     asyncio.set_event_loop(loop)
#     # tasks = [stream_download(_GuiRecvMsg, d, proxies) for d in imgDict]
#     def callback(future):
#         _GuiRecvMsg.put({
#             'type_' : 'tumblr',
#             'event_' : 'setImgBg',
#             'data_' : future.result()
#         })

#     tasks = []
#     for d in imgDict:
#         task = asyncio.ensure_future(stream_download(d, proxies))
#         task.add_done_callback(callback)
#         tasks.append(task)
#     try:
#         results = loop.run_until_complete( asyncio.wait(tasks) )
#     except Exception as e:
#         # # print('0',asyncio.Task.all_tasks())
#         # # print('1',asyncio.gather(*asyncio.Task.all_tasks()).cancel())
#         loop.stop()
#         # loop.run_forever()
#     finally:
#         loop.close()
#     # print('end')
#     # postMessage(f_hwnd, loadtest, 0, 0)
#     return

async def stream_download( d, proxies, _GuiRecvMsg, _GuiRecvMsgDict ):
    '''协程下载列表中图片'''
    print('下载',d['id'])
    async with aiohttp.request('GET', d['http'], proxy=''.join(('http://', proxies))) as response:
    # async with client.get( d['http'], proxy=''.join(('http://', proxies)), timeout=10 ) as response:
        if response.status != 200:
            print('error')
            return
        with open(d['fpath'], 'ab') as file:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                file.write(chunk)
    # print('over',d['id'])
    # func()
    _GuiRecvMsg.put(_GuiRecvMsgDict)
    # print('over2',d['id'])
    # return {'id':d['id'],'fpath':d['fpath']}

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
        self.__ImgPretreatment()
        limit = int( self.cfg['dashboard_param']['limit'] )
        # # print( len( self.imgList ), limit)
        if len( self.imgList ) < limit:
            self.getImgList()
        self.setImgList(limit)

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
        if not osPath.isfile(file_path):
            asyncio.run_coroutine_threadsafe(stream_download(
                {'id': d['id'],'http': d['preview_size'],'fpath': file_path},
                self.proxies,
                self.GuiRecvMsg,
                _GuiRecvMsgDict
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
            raise e

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

    def setImgList(self, limit):
        print('setImgList')
        i = 0
        imgDict = []
        while i < limit:
            d = self.imgList.pop(0)
            # # print(d)
            self.GuiRecvMsg.put({
                'type_' : 'tumblr',
                'event_' : 'setImgId',
                'data_' : {
                    'id': d['id'],
                    'imgid': str(i),
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
            if not osPath.isfile(file_path):
                # # print('准备下载',d['id'])
                # imgDict.append({
                #     'id': d['id'],
                #     'http': d['alt_sizes'],
                #     'fpath': file_path
                # })
                # task = asyncio.ensure_future(stream_download({
                #     'id': d['id'],
                #     'http': d['alt_sizes'],
                #     'fpath': file_path
                # }, self.proxies))
                # task.add_done_callback(callback)
                asyncio.run_coroutine_threadsafe(stream_download(
                    {'id': d['id'],'http': d['alt_sizes'],'fpath': file_path},
                    self.proxies,
                    self.GuiRecvMsg,
                    _GuiRecvMsgDict
                ), self.new_loop)
                # task.add_done_callback(callback)
            else:
                # # print('存在',d['id'])
                self.GuiRecvMsg.put(_GuiRecvMsgDict)
            i += 1
        # # print(imgDict)
        # if imgDict:
        #     asyncImgList( self.GuiRecvMsg, imgDict, self.proxies )

    def __ImgPretreatment(self):
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