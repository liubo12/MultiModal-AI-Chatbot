# -*- coding: utf-8 -*-
# filename: handle_interface.py
from flask.views import MethodView
from config import MyConfig
#from multiprocessing import Manager

#manager=Manager()
#实现chatGPT的多轮对话操作
#chat_cache=manager.dict()#key:(toUser, fromUser) values:[] 列表结构的query

class Handle(MethodView):

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.myconfig=MyConfig()

    def help(self):
        return 

    def rm_chat_cache(self):
        # for i in chat_cache.keys():
        #     chat_cache.pop(i)
        # print('清除chat_cache',chat_cache)
        return

    def drawing(self,content):
        return

    def chating(self,content):
        return

    def get(self):
        return

    def post(self):
        return
