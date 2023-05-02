# -*- coding: utf-8 -*-
# filename: handle_wechat.py

import hashlib
import time
import os
import sys
from multiprocessing import Process
from multiprocessing import Value
from multiprocessing import Manager

from flask import request
#from flask.views import MethodView

import app.wechat.receive as receive
import app.wechat.reply as reply
from app.handle_interface import Handle

sys.path.append('..')
from model.stablediffusion_api import txt2img
from model.stablediffusion_api import get_access_token
from model.stablediffusion_api import upload_mmdeia
from model.openai_api import achieve_query
from model.openai_api import chat_GPT
from model.openai_api import image_create
from model.translator_api import cn2en

from config import MyConfig


#res_cache的key为元组类型，存放(toUser, fromUser)
#res_cache的values为reply.Msg类型，存放返回消息数据
manager=Manager()

#实现返回结果的同步操作，所有超过5秒的图片、文字结果都可能通过此数据结构缓存
res_cache=manager.dict()#key:(toUser, fromUser) values:reply.Msg

#实现chatGPT的多轮对话操作
chat_cache=manager.dict()#key:(toUser, fromUser) values:[] 列表结构的query

class HandleWeChat(Handle):

    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        #self.render = web.template.render(self.templates_root)
        self.myconfig=MyConfig()
    def get(self):
        try:
            signature = request.args.get('signature')
            timestamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            echostr = request.args.get('echostr')
            token=self.myconfig.get_wechat_token()#公众号token

            list = [token, timestamp, nonce]
            list.sort()
            s = list[0] + list[1] + list[2]
            hashcode = hashlib.sha1(s.encode('utf-8')).hexdigest()
            print("handle/GET func: hashcode, signature: ", hashcode, signature)
            if hashcode == signature:
                return echostr
            else:
                return echostr
        except (Exception) as Argument:
            return Argument
    
    #generate res of longtime(>5s) requests,to put into res_cache
    def child_operation_draw(self,toUser,fromUser,content,method='openai'):
        if method=='stable diffusion':
            txt2img_res=txt2img(content)
        elif method=='openai':
            txt2img_res=image_create(content)
        if not txt2img_res:
            replyMsg=reply.TextMsg(toUser, fromUser, '生成图片过程中出错~！')
            res_cache[(toUser, fromUser)]=replyMsg
            return

        #txt2img里面将返回图片写死存入res.jpg;这个操作会影响异步，可以考虑通过时间戳来优化，但必须定期清理硬盘#
        #操作res.jpg将它上传到微信#
        #获取上传token#
        access_token=get_access_token()
        if not access_token:
            print('Access_token failed to achieve, chect your wechat parameters(grant_type appid secret)！')
            replyMsg=reply.TextMsg(toUser, fromUser, '结果生成微信信令过程中出错~！')
            res_cache[(toUser, fromUser)]=replyMsg
            print(access_token)
            return

        img_id=upload_mmdeia(access_token,'image','./generate/res.jpg')
        if not img_id:
            print('Upload processing failed,chect your access_token or file is legal！~')
            replyMsg=reply.TextMsg(toUser, fromUser, '结果上传微信媒体服务器过程中出错~！')
            res_cache[(toUser, fromUser)]=replyMsg
            return
          
        replyMsg=reply.ImageMsg(toUser, fromUser, img_id)
        res_cache[(toUser, fromUser)]=replyMsg
        print('结果')
        print(res_cache)
        return

    def child_operation_chat(self,toUser,fromUser,user_query):
        chat_res=chat_GPT(query=user_query)
        if not chat_res:
            replyMsg=reply.TextMsg(toUser, fromUser, 'ChatGPT计算或网络传输过程中出错~！')
            res_cache[(toUser, fromUser)]=replyMsg
            return
        assistant_role={'role':'assistant','content':chat_res}
        chat_cache[(toUser,fromUser)].append(assistant_role)
        replyMsg=reply.TextMsg(toUser, fromUser, chat_res)
        res_cache[(toUser, fromUser)]=replyMsg
        return 

    def help(self,toUser,fromUser):
        replyMsg = reply.TextMsg(toUser, fromUser, '您好，这是一个多功能AI聊天机器人，支持输入语音、文字，生成对应的图文。\n1.文字、语音请直接发送，回复包括文字，图片，表格等形式的答案；\n2.支持中英双语画图，中文请在问题中声明“画”或“生成图片”，英文请声明“draw”，输入语音时同理；\n3.聊天默认开启多轮服务模式，清除多轮缓存请输入“清除”\n4.如需查看使用方法，可输入“help”或者“帮助”\n更多功能开发中，敬请期待！~')
        return replyMsg.send()

    def go_on(self,toUser,fromUser):
        print('res_cache:',res_cache)
        if (toUser, fromUser) in res_cache.keys():
            res=res_cache[(toUser, fromUser)]
            res_cache.pop( (toUser, fromUser) )
            return res.send()
        else:
            replyMsg = reply.TextMsg(toUser, fromUser, '结果还未计算成功，请稍微再输入‘继续’或1查看！~')
            return replyMsg.send()

    def rm_chat_cache(self,toUser,fromUser):
        for i in chat_cache.keys():
            chat_cache.pop(i)
        print('清除chat_cache',chat_cache)
        replyMsg = reply.TextMsg(toUser, fromUser, '清除成功，可以开始新的聊天！~')
        return replyMsg.send() 

    def drawing(self,toUser,fromUser,content):
        process=Process(target=self.child_operation_draw,args=(toUser,fromUser,content,))
        process.start()
        replyMsg = reply.TextMsg(toUser, fromUser, '您的图像生成业务巨耗时，后台正在疯狂计算。25秒左右请输入“继续”或1查看结果！~')
        return replyMsg.send()

    def chating(self,toUser,fromUser,content):
        if (toUser,fromUser) in chat_cache:
            history_query=chat_cache[(toUser,fromUser)]
            user_query=achieve_query(messages_of_user=content,history=history_query)
        else:
            user_query=achieve_query(messages_of_user=content)
        chat_cache[(toUser,fromUser)]=user_query

        process=Process(target=self.child_operation_chat,args=(toUser,fromUser,user_query,))
        process.start()
        
        time.sleep(1)
        if (toUser, fromUser) in res_cache.keys():
            res=res_cache[(toUser, fromUser)]
            res_cache.pop( (toUser, fromUser) )
            return res.send()
        time.sleep(1.5)
        if (toUser, fromUser) in res_cache.keys():
            res=res_cache[(toUser, fromUser)]
            res_cache.pop( (toUser, fromUser) )
            return res.send()
        time.sleep(2)
        if (toUser, fromUser) in res_cache.keys():
            res=res_cache[(toUser, fromUser)]
            res_cache.pop( (toUser, fromUser) )
            return res.send()

        replyMsg = reply.TextMsg(toUser, fromUser, '您的聊天GPT业务相对耗时，后台正在努力计算。稍后请输入“继续”或1查看结果！~')
        return replyMsg.send()

    def post(self):
        try:
            #webData = web.data()
            webData=request.get_data()
            print("Handle Post webdata is ", webData)  # 后台打日志
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg):
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                if recMsg.MsgType == 'text':
                    content=(recMsg.Content).decode('utf-8')
                    content=content.lower()
                    print(content)

                    if ('help' in content[:8] or '帮助' in content[:6]):
                        return self.help(toUser,fromUser)
                    elif (content=='继续' or content=='1'):
                        return self.go_on(toUser,fromUser)
                    elif (content=='清除'):
                        return self.rm_chat_cache(toUser,fromUser) 

                    if ('画图' in content) or ('生成图片' in content) or ('生成图像' in content) or ('画' in content[:3]) or ('draw' in content[:6]):
                        #画图
                        content=cn2en(content)
                        return self.drawing(toUser,fromUser,content)
                    else:
                        #chatGPT
                        return self.chating(toUser,fromUser,content)

                elif recMsg.MsgType == 'image':
                    mediaId = recMsg.MediaId
                    replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
                    return replyMsg.send()

                elif recMsg.MsgType == 'voice':
                    content=recMsg.Recognition
                    content=content.lower()
                    print(type(content))
                    print(content)
                    if ('help' in content[:8] or '帮助' in content[:6]):
                        return self.help(toUser,fromUser)
                    elif (content=='继续') or '继续' in content[:4]:
                        return self.go_on(toUser,fromUser)
                    elif (content=='清除') or '清除' in content[:4]:
                        return self.rm_chat_cache(toUser,fromUser) 

                    if ('画图' in content) or ('生成图片' in content) or ('生成图像' in content) or ('画' in content[:3]) or ('draw' in content[:6]):
                        #画图
                        content=cn2en(content)
                        return self.drawing(toUser,fromUser,content)
                    else:
                        #chatGPT
                        return self.chating(toUser,fromUser,content)
            else:
                print("暂且不处理")
                return reply.Msg().send()
        except Exception(Argment):
            return Argment

