import requests
from cyclist_helmet_detect import detect
from fastapi import FastAPI,Form,UploadFile
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
import time
import cv2
import numpy as np
import json

app = FastAPI()

origins=["*"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


URL = ""
with open('/app/config/config.json') as fp:
    URL=json.load(fp)["cg"]

def get_time_spane():
    '''
    获取时间戳
    :return:
    '''
    t = time.time()
    return int(round(t * 1000000)).__str__()


def post_image_url(type, url, contents):
    '''
    将图片和url发送到服务器中
    :param type:
    :param url:
    :param file:
    :return:
    '''
        
    try:
        payload = {'type':type,'imgUrl':url}
        if type=='URL':
            files = [('file', open('image.jpg', 'rb'))]
        elif type=='FILE':
            files = [('file', ('image.jpg',contents))]
        headers = {}
        response = requests.request("POST", URL, headers=headers, data = payload, files = files).json()
        if response.get('code') != 200:
            return None
        else:
            keys = response.get('data').keys()
            for key in keys:
                return response.get('data')[key]
            return  None
    except:
        return None


def download_url(url):
    try:
        pic = requests.get(url)
        if pic.status_code != 200:
            return False
        fp = open('image.jpg', 'wb')
        fp.write(pic.content)
        fp.close()
        return True
    except:
        return False





@app.post('/ch')
async def process(type:str=Form(...),file:UploadFile=Form(None),imgUrl:str=Form(None)):
    if type not in ('FILE','URL'):
        return {'code': 1001, 'msg': 'paraters error'}

    if type == 'FILE': #文件保存
        try:
            contents=file.file.read()
            value=bytearray(contents)
            #read file bytes from file. 
            #file is a uploadFile, 
            #file.file is a spooledtemporaryfile
            #file.file.read() read file as bytes
            value=np.asarray(value,dtype='uint8')
            img=cv2.imdecode(value,1)
        except cv2.error:
            return{'code':1004,'msg':'file is empty!'}

    if type == 'URL': #判断url是否有效
        if download_url(imgUrl) is False:
            return {'code': 1002, 'msg': 'download the picture url:%s occurs error!' % (imgUrl)}
        else:
            img=cv2.imread('image.jpg')
            contents=''


    upload_image_url = post_image_url(type=type, url=imgUrl,contents=contents)
    if upload_image_url is None:
        return {'code': 1003, 'msg': 'request %s has error!'%(URL)}


    #进行算法检测了返回接口信息
    data = detect(upload_image_url,img)

    print(data)
    return {'code': 200,
                'data': data,
                "id": get_time_spane(),
                "msg": "success"
                }

if __name__ == '__main__':
    uvicorn.run(app=app,host='0.0.0.0', port=5003)