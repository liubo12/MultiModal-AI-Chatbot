# -*- coding: utf-8 -*-
# filename: handle_termianl.py
import time
import os
import sys
from multiprocessing import Manager
from flask import request

from app.handle_interface import Handle

sys.path.append('..')
from model.stablediffusion_api import txt2img
from model.openai_api import achieve_query
from model.openai_api import chat_GPT
from model.openai_api import image_create
from model.translator_api import cn2en

from config import MyConfig
manager=Manager()


#实现chatGPT的多轮对话操作
chat_cache=manager.dict()#key:user values:[] 列表结构的query

class HandleWeb(Handle):

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.myconfig=MyConfig()
    
    def help(self):
        data='您好，这是一个多功能AI聊天机器人，支持输入语音、文字，生成对应的图文。\n1.聊天默认开启多轮服务模式，清除多轮缓存请输入“清除”\n2.如需查看使用方法，可输入“help”或者“帮助”\n问答输入通过http服务post方式进行。\n'
        data+='\n问答请求模式：ip:port 通过表单form-data传送字段\n{type:"[text,image,voice]",user:"your name",data:"your chat or file"}，\ntype必须选择一个\ncURL示例：curl --location "ip:port" --form "data="1+1等于几"" --form "type="text"" --form "user="yourname""\n推荐使用postman!'
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(data)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return {'code':200,'data':data}

    def get(self):
        try:
            return self.help()
        except (Exception) as Argument:
            return Argument

    def rm_chat_cache(self,user):
        if user in chat_cache.keys():
            chat_cache.pop(user)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('清除chat_cache...\n清除成功，可以开始新的聊天！~',chat_cache)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        data='清除成功，可以开始新的聊天！~'
        return {'code':200,'data':data}

    def post(self):
        try:
            chat_type=request.form.get('type')
            chat_name=request.form.get('user')
            print("type=",chat_type)
            chat_type=chat_type.lower()

            if chat_type=='text':
                content=request.form.get('data')
                content=content.lower()
                if ('help' in content[:8] or '帮助' in content[:6]):
                    return self.help()
                elif (content=='清除'):
                    return self.rm_chat_cache(chat_name) 
                if ('画图' in content) or ('生成图片' in content) or ('生成图像' in content) or ('画' in content[:3]) or ('draw' in content[:6]):
                    #画图
                    content=cn2en(content)
                    method=self.myconfig.get_terminal_txt2img_method()
                    return self.drawing(chat_name,content,method=method)
                else:
                    #chatGPT
                    return self.chating(chat_name,content)
            elif chat_type=='voice':
                print('代码开发中....')
                #1识别voice
                #2转到text相同操作
                pass
            elif chat_type=='image':
                print('代码开发中....')
                pass
                #print('type=',request.files['data'])
            return
        except:
            print('出错了，靓仔！')


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
            return {'code':200,'data':data}

        data='你的图片生成成功，查看路径generate/'+timestamp+'.jpg'
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(data)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return {'code':200,'data':data}

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
            return {'code':200,'data':data}

        assistant_role={'role':'assistant','content':chat_res}
        chat_cache[user].append(assistant_role)

        data=chat_res
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(data)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        return {'code':200,'data':data}



