from tumblpy import Tumblpy
from json import load as JLoad
from common import gets


class TumblrManager(object):
    def __init__(self, imgListQ, cfg, proxies):
        super(TumblrManager, self).__init__()
        self.imgListQ = imgListQ
        self.cfg = cfg
        self.proxies = 'http://' + proxies
        with open('tumblr_credentials.json', 'r') as f:
            self.tumblr_key = JLoad(f)
        self.tumblr = Tumblpy(
            self.tumblr_key['consumer_key'],
            self.tumblr_key['consumer_secret'],
            self.tumblr_key['oauth_token'],
            self.tumblr_key['oauth_token_secret'],
            proxies=self.proxies
        )

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
        if self.imgListQ.qsize() < self.cfg['dashboard_param']['limit']:
            print('getList')
            self.getImgList()
        else:
            postMessage(self.Gui_HWND, loadImgListMsg, 0, 0)
            pass
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
            self.imgListQ.put( d )

def initTumblr(imgListQ, cfg):
    tm = TumblrManager(imgListQ, cfg)
    pass