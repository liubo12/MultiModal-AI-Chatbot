import json
import os


class MyConfig(object):#单例模式
    _instance=None
    def __new__(cls,*args,**kw):
        if cls._instance is None:
            cls._instance=object.__new__(cls,*args,**kw)
        return cls._instance

    def __init__(self,myconfig='./config.json'):
        if not os.path.exists(myconfig):
            raise Exception('你惨了，配置文件config.json都能丢失。')
        with open(myconfig,mode='r',encoding='utf-8') as f:
            config_info=json.loads(f.read())
        if not config_info:
            raise Exception('加载config.json时出错！')
        self.config_info=config_info

    def get_interface(self,*args):
        config_info=self.config_info
        for i in args:
            if i not in config_info.keys():
                raise Exception('配置文件出错，不存在“'+i+'”！')
            config_info=config_info[i]
        return config_info

    def get_wechat_token(self):
        return self.get_interface('wechat','wechat token')

    def get_wechat_access_token_interface(self):
        return self.get_interface('wechat','access_token interface')

    def get_wechat_grant_type(self):
        return self.get_interface('wechat','grant_type')

    def get_wechat_appid(self):
        return self.get_interface('wechat','appid')

    def get_wechat_secret(self):
        return self.get_interface('wechat','secret')

    def get_wechat_up_media_interface(self):
        return self.get_interface('wechat','up_media interface')

    def get_model_chatgpt_chat_model(self):
        return self.get_interface('model','openai','chatgpt_model')

    def get_model_openai_api_key(self):
        return self.get_interface('model','openai','api_key')

    def get_model_stable_diffusion_txt2img(self):
        return self.get_interface('model','stable diffusion','txt2img')

    def get_model_translator(self):
        return self.get_interface('model','translator')

    def get_terminal_txt2img_method(self):
        return self.get_interface('terminal','txt2img method')

    def get_wechat_txt2img_method(self):
        return self.get_interface('wechat','txt2img method')








