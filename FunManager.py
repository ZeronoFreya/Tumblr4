# from multiprocessing import Queue
# import TumblrManager
import aiohttp
import asyncio
from os import path as osPath
from tumblpy import Tumblpy
from json import load as JLoad
from common import gets

def asyncImgList( _GuiRecvMsg, imgDict, proxies ):
    '''协程下载列表中图片'''

    async def stream_download( client, _GuiRecvMsg, d, proxies ):
        async with client.get( d['http'], proxy=''.join(('http://', proxies)), timeout=10 ) as response:
            if response.status != 200:
                print('error')
                return
            with open(d['fpath'], 'ab') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)
        # imgDoneQ.put( {'id':d['id'],'fpath':d['fpath']} )
        _GuiRecvMsg.put({
            'type_' : 'tumblr',
            'event_' : 'setImgBg',
            'data_' : {'id':d['id'],'fpath':d['fpath']}
        })
        # postMessage(f_hwnd, loadImgMsg, 0, 0)

    print('asyncImgList')
    client = aiohttp.ClientSession()
    loop = asyncio.get_event_loop()
    tasks = [stream_download(client, _GuiRecvMsg, d, proxies) for d in imgDict]
    try:
        loop.run_until_complete( asyncio.wait(tasks) )
    except Exception as e:
        print('0',asyncio.Task.all_tasks())
        print('1',asyncio.gather(*asyncio.Task.all_tasks()).cancel())
        loop.stop()
        loop.run_forever()
    finally:
        loop.close()
    print('end')
    # postMessage(f_hwnd, loadtest, 0, 0)
    return

class TumblrFun:
    """docstring for ClassName"""
    def __init__(self, tumblrCfg, _GuiRecvMsg, proxies, imgTemp):
        # self.imgListQ = imgListQ
        self.GuiRecvMsg = _GuiRecvMsg
        self.cfg = tumblrCfg
        self.proxies = proxies
        self.imgTemp = imgTemp
        self.imgList = []

    def initTumblr(self):
        print('initTumblr')
        with open('tumblr_credentials.json', 'r') as f:
            self.tumblr_key = JLoad(f)
        self.tumblr = Tumblpy(
            self.tumblr_key['consumer_key'],
            self.tumblr_key['consumer_secret'],
            self.tumblr_key['oauth_token'],
            self.tumblr_key['oauth_token_secret'],
            proxies={ "http": self.proxies, "https": self.proxies }
        )
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

    def getDashboards(self):
        print('getDashboards')
        self.__ImgPretreatment()
        limit = int( self.cfg['dashboard_param']['limit'] )
        if len( self.imgList ) < limit:
            self.getImgList()
        self.setImgList(limit)

    def getImgList(self):
        '''获取图片列表'''
        p = self.cfg['posts_param'].copy()
        p['limit'] *= 5
        # dashboard = tumblr.dashboard( param['dashboard_param'] )
        dashboard = self.tumblr.posts('kuvshinov-ilya.tumblr.com', None, p)
        if not dashboard:
            return
        self.cfg['dashboard_param']['offset'] += p['limit']
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

    def setImgList(self, limit):
        i = 0
        imgDict = []
        while i < limit:
            d = self.imgList.pop(0)
            self.GuiRecvMsg.put({
                'type_' : 'tumblr',
                'event_' : 'setImgId',
                'data_' : {
                    'id': d['id'],
                    'imgid': str(i)
                }
            })
            file_name = d['id'] + '_' + d['alt_sizes'].split("_")[-1]
            file_path = osPath.join( self.imgTemp, file_name )
            if not osPath.isfile(file_path):
                imgDict.append({
                    'id': d['id'],
                    'http': d['alt_sizes'],
                    'fpath': file_path
                })
            else:
                self.GuiRecvMsg.put({
                    'type_' : 'tumblr',
                    'event_' : 'setImgBg',
                    'data_' : {'id':d['id'],'fpath':file_path}
                })
            i += 1

        if imgDict:
            return asyncImgList( self.GuiRecvMsg, imgDict, self.proxies )

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