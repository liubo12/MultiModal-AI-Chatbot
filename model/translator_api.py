import sys
sys.path.append('..')
from config import MyConfig
from googletrans import Translator
def cn2en(content):
    # myconfig=MyConfig()
    # trans=myconfig.get_model_translator()
    # if trans is None:
        # 	return False
    try:
        translator = Translator()
        return translator.translate(content,dest='en').text
    except Exception as e:
        raise "访问googletrans过程中出错"
