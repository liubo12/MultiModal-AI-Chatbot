# -*- coding: utf-8 -*-
# filename: handle_termianl.py
import time
import os
import sys
#from multiprocessing import Manager
from flask import request

from app.handle_interface import Handle

sys.path.append('..')
from model.stablediffusion_api import txt2img
from model.openai_api import achieve_query
from model.openai_api import chat_GPT
from model.openai_api import image_create
from model.translator_api import cn2en

from config import MyConfig
#manager=Manager()


#实现chatGPT的多轮对话操作
chat_cache={}#manager.dict()#key:user values:[] 列表结构的query

class HandleTerminal(Handle):

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.myconfig=MyConfig()
    
    def help(self):
        data='您好，这是一个多功能AI聊天机器人，支持输入语音、文字，生成对应的图文。\n1.聊天默认开启多轮服务模式，清除多轮缓存请输入“清除”\n2.如需查看使用方法，可输入“help”或者“帮助”\n'
        data+='请直接输入您的问题！'
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(data)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


    def rm_chat_cache(self,user):
        if user in chat_cache.keys():
            chat_cache.pop(user)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('清除chat_cache...\n清除成功，可以开始新的聊天！~',chat_cache)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        data='清除成功，可以开始新的聊天！~'

    def start(self):
        self.help()
        chat_name=input('请输入您的昵称！')
        
        while True:
            content=input('请输入您的问题！')
            try:
                content=content.lower()
                if ('help' in content[:8] or '帮助' in content[:6]):
                    self.help()
                    continue
                elif (content=='清除'):
                    self.rm_chat_cache(chat_name) 
                    continue
                if ('画图' in content) or ('生成图片' in content) or ('生成图像' in content) or ('画' in content[:3]) or ('draw' in content[:6]):
                    #画图
                    content=cn2en(content)
                    method=self.myconfig.get_terminal_txt2img_method()
                    self.drawing(chat_name,content,method=method)
                    continue
                else:
                    #chatGPT
                    self.chating(chat_name,content)
                    continue
            except:
                print('出错了，靓仔！')
                continue


    def drawing(self,user,content,method='openai'):
        if method=='stable diffusion':
            txt2img_res=txt2img(content)
        elif method=='openai':
            timestamp=time.time()
            timestamp=int(timestamp)
            timestamp=str(timestamp)
            timestamp=user+timestamp
            txt2img_res=image_create(content=content,timestamp=timestamp)
        if not txt2img_res:
            data='生成图片过程中出错~！'
            print(data)
            return

        data='你的图片生成成功，查看路径generate/'+timestamp+'.jpg'
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(data)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return

    def chating(self,user,content):
        if user in chat_cache.keys():
            history_query=chat_cache[user]
            user_query=achieve_query(messages_of_user=content,history=history_query)
        else:
            user_query=achieve_query(messages_of_user=content)
        chat_cache[user]=user_query

        chat_res=chat_GPT(query=user_query)
        if not chat_res:
            data='ChatGPT计算或网络传输过程中出错~！'
            print(data)
            return

        assistant_role={'role':'assistant','content':chat_res}
        chat_cache[user].append(assistant_role)

        data=chat_res
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(data)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return



