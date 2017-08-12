class EventManager:
    def __init__(self, _CtrlRecvMsg, handlers, funMap):
        # 事件管理器开关
        self.__active = False
        self.handlers = handlers
        self.CtrlRecvMsg = _CtrlRecvMsg
        self.funMap = funMap

    def __Run(self):
        """引擎运行"""
        while self.__active == True:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self.CtrlRecvMsg.get(timeout = 1)
                print(event['type_'], event['event_'])
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
            self.funMap[event['type_']][event['event_']]( event.get('data_',None) )

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