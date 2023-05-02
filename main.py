# -*- coding: utf-8 -*-
# filename: main.py
import argparse
from flask import Flask

parser = argparse.ArgumentParser()
parser.add_argument("--app", help="launch mode,switch from [terminal,web,wechat]", type=str,default='terminal')
#parser.add_argument('--cmd', default=False, action=argparse.BooleanOptionalAction)

args = parser.parse_args()

app=Flask(__name__)

mylaunch=args.app
if mylaunch=='wechat':
    #安装后使用如下命令快速开始：
    #python main.py
    #需要配置微信公众号
    from app.wechat.handle_wechat import HandleWeChat
    handle=HandleWeChat
elif mylaunch=='web':
    #安装后使用如下命令快速开始：
    #python main.py --app web
    #启动后通过以下命令快速获取使用方式：
    #curl --location '3.143.252.187:80'
    from app.web.handle_web import HandleWeb
    handle=HandleWeb
elif mylaunch=='terminal':
    #安装后使用如下命令快速开始：
    #python main.py --app terminal
    from app.terminal.handle_terminal import HandleTerminal
    HandleTerminal().start()

app.add_url_rule('/',view_func=handle.as_view('/'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
