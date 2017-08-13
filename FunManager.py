# from multiprocessing import Queue
# import TumblrManager
import aiohttp
import asyncio
from time import time
from threading import Thread
from os import path as osPath
from tumblpy import Tumblpy
from json import load as JLoad
from common import gets

async def stream_download( d, proxies, _GuiRecvMsg, _GuiRecvMsgDict, _Timeout ):
    '''协程下载列表中图片'''
    print('下载',d['http'])
    try:
        with aiohttp.Timeout(10):
            async with aiohttp.request( 'GET', d['http'], proxy=''.join(('http://', proxies)) ) as response:
            # async with client.get( d['http'], proxy=''.join(('http://', proxies)), timeout=10 ) as response:
                if response.status != 200:
                    print('error')
                    _GuiRecvMsg.put(_Timeout)
                    return
                print('200',d['id'])
                if not osPath.isfile(d['fpath']):
                    with open(d['fpath'], 'ab') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
        _GuiRecvMsg.put(_GuiRecvMsgDict)
        return
    except asyncio.TimeoutError:
        # continue
        _GuiRecvMsg.put(_Timeout)
    # finally:
    #     print(err, d['id'])

class ServiceEvent(object):
    """docstring for ClassName"""
    def __init__(self, tumblrCfg, _GuiRecvMsg, proxies, imgTemp, imgSave):
        self.GuiRecvMsg = _GuiRecvMsg
        self.cfg = tumblrCfg
        self.proxies = proxies
        self.imgTemp = imgTemp
        self.imgSave = imgSave
        self.imgList = []
        self.working = 0
        self.liHtml = '''
            <li.loading imgid=%s>
                <footer .li-footer></footer>
            </li>
        '''
        self.new_loop = asyncio.new_event_loop()
        t = Thread(target=self.start_loop, args=(self.new_loop,))
        t.setDaemon(True)    # 设置子线程为守护线程
        t.start()

    def start_loop(self, loop):
        # self.sem = asyncio.Semaphore(30)
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def tumblr__init(self, data_=None):
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
        self.__putGui('tumblr', 'statusBar', {
            'text' : '获取图片列表'
        })
        self.__tumblr__getImgList()
        return self.tumblr__getDashboards()

    def tumblr__downloadImg(self, d):
        file_name = d['id'] + '_' + d['download'].split("_")[-1]
        file_path = osPath.join( self.imgSave, file_name )
        _GuiRecvMsgDict = {
            'type_' : 'tumblr',
            'event_' : 'downloaded',
            'data_' : {'id':d['id'],'fpath':file_path,'module':'"'.join(('#tumblr .list li[imgid=',d['id'],']'))}
        }
        _Timeout = {
            'type_' : 'tumblr',
            'event_' : 'statusBar',
            'data_' : {
                'text' : d['id'] + '下载失败！'
            }
        }
        if not osPath.isfile(file_path):
            asyncio.run_coroutine_threadsafe(stream_download(
                {'id': d['id'],'http': d['download'],'fpath': file_path},
                self.proxies,
                self.GuiRecvMsg,
                _GuiRecvMsgDict,
                _Timeout
            ), self.new_loop)
        else:
            self.GuiRecvMsg.put(_GuiRecvMsgDict)

    def tumblr__getDashboards(self, data_=None):
        print('getDashboards')
        imgid_list = self.__tumblr__imgPretreatment()
        limit = int( self.cfg['dashboard_param']['limit'] )
        self.__tumblr__setImgList(imgid_list)
        self.__putGui('tumblr', 'setImgIdOver')
        if len( self.imgList ) < limit*2:
            self.__tumblr__getImgList()

    def tumblr__getPreviewSize(self, d):
        '''获取预览大图'''
        print('getPreviewSize')
        file_name = d['id'] + '_' + d['original_size'].split("_")[-1]
        file_path = osPath.join( self.imgSave, file_name )
        if not osPath.isfile(file_path):
            file_name = d['id'] + '_' + d['preview_size'].split("_")[-1]
            file_path = osPath.join( self.imgTemp, file_name )
        _GuiRecvMsgDict = {
            'type_' : 'tumblr',
            'event_' : 'setPreview',
            'data_' : {'id':d['id'],'fpath':file_path}
        }
        if not osPath.isfile(file_path):
            _Timeout = {
                'type_' : 'tumblr',
                'event_' : 'timeout',
                'data_' : {'id':d['id'],'http':d['preview_size'],'module':'"'.join(('#tumblr .list li[imgid=',d['id'],']'))}
            }
            asyncio.run_coroutine_threadsafe(stream_download(
                {'id': d['id'],'http': d['preview_size'],'fpath': file_path},
                self.proxies,
                self.GuiRecvMsg,
                _GuiRecvMsgDict,
                _Timeout
            ), self.new_loop)
        else:
            self.GuiRecvMsg.put(_GuiRecvMsgDict)

    def tumblr__refreshTimeoutImg(self, d):
        '''刷新加载失败的缩略图'''
        print('refreshTimeoutImg')
        file_name = d['id'] + '_' + d['alt_size'].split("_")[-1]
        file_path = osPath.join( self.imgTemp, file_name )
        _GuiRecvMsgDict = {
            'type_' : 'tumblr',
            'event_' : 'setImgBg',
            'data_' : {'id':d['id'],'fpath':file_path}
        }
        _Timeout = {
            'type_' : 'tumblr',
            'event_' : 'timeout',
            'data_' : {'id':d['id'],'http':d['alt_size'],'module':'"'.join(('#tumblr .view li[imgid=',d['id'],']'))}
        }
        asyncio.run_coroutine_threadsafe(stream_download(
            {'id': d['id'],'http': d['alt_size'],'fpath': file_path},
            self.proxies,
            self.GuiRecvMsg,
            _GuiRecvMsgDict,
            _Timeout
        ), self.new_loop)

    def __tumblr__getImgList(self):
        ''' 获取图片列表
            预期格式：[{
                'id': '0',
                'link_url': 'xx',
                'source_url': '',
                'original_size': 'xx',
                'preview_size': 'x',
                'alt_sizes': 'x'
            }]
        '''
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
            dashboard = self.tumblr.dashboard( p )
            # dashboard = self.tumblr.posts('kuvshinov-ilya.tumblr.com', None, p)
            # # print('dashboard',dashboard)
        except Exception as e:
            print('err dashboard')
            return
        self.cfg['dashboard_param']['offset'] += p['limit']
        # # print(self.cfg)
        imgList = self.__tumblr__mkDict( dashboard, self.cfg['preview_size'], self.cfg['alt_sizes'] )

        for d in imgList:
            self.imgList.append( d )

    def __tumblr__imgPretreatment(self):
        html = ''
        limit = self.cfg['dashboard_param']['limit']
        # i = 0
        imgid = []
        time_now = ''
        for i in range(0, limit):
            time_now = '-'.join( ( str(i), str(time()) ) )
            imgid.append( time_now )
            html += self.liHtml % ( time_now )
        self.__putGui('tumblr', 'appendImg', html)
        return imgid

    def __tumblr__mkDict( self, d, preview_size, alt_sizes ):
        print('mkMainDict')
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

    def __tumblr__setImgList(self, imgid_list):
        print('setImgList')
        imgDict = []
        for imgid in imgid_list:
            d = self.imgList.pop(0)
            self.__putGui('tumblr', 'setImgId', {
                'id': d['id'],
                'imgid': imgid,
                'preview': d['preview_size'],
                'download': d['original_size']
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
                'data_' : {'id':d['id'],'http':d['alt_sizes'],'module':'"'.join(('#tumblr .view li[imgid=',d['id'],']'))}
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
                self.GuiRecvMsg.put(_GuiRecvMsgDict)

    def __putGui(self, t, e, d = None):
        self.GuiRecvMsg.put({
            'type_' : t,
            'event_' : e,
            'data_' : d
        })