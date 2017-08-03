
def gets( t, s, d=None ):
    '''
        拓展字典的get方法
        gets( 字典, key [, '默认值'])
        dict = {'a':{'b':1}}
        gets( dict, 'a.b', 'xx')
        返回 值 | 默认值（未指定返回None）
    '''
    if not t: return d
    for k in s.split('.'):
        if type(t) == list and k.lstrip('-').isdigit():
            l = k = int(k)
            if k < 0: l = abs(k) - 1
            if len(t) > l: t = t[k]; continue
        elif type(t) == dict and k in t:
            t = t[k]; continue
        else:
            return d
    return t

