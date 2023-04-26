import requests
import json
import numpy as np
import cv2
import base64
import sys
sys.path.append('..')
from config import MyConfig


def get_access_token():
  ##grant_type  appid  secret  
  ##3个get参数可以修改这个函数传入
  #url = "https://api.weixin.qq.com/cgi-bin/token?
  #grant_type=
  #appid=
  #secret=
  myconfig=MyConfig()
  url=myconfig.get_wechat_access_token_interface()
  grant_type=myconfig.get_wechat_grant_type()
  appid=myconfig.get_wechat_appid()
  secret=myconfig.get_wechat_secret()

  url=url+'grant_type='+grant_type+'&appid='+appid+'&secret='+secret

  payload={}
  headers = {}
  response = requests.request("GET", url, headers=headers, data=payload)
  res=json.loads(response.text)
  if 'access_token' not in res.keys():
    return False
  return res['access_token']

def upload_mmdeia(access_token,itype,file_name):#itype:[image voice]
  #url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token="
  myconfig=MyConfig()
  url=myconfig.get_wechat_up_media_interface()+"access_token="
  url += access_token
  url += "&type="
  url += itype
  payload={}

  img_para=''
  if '.jpg' in file_name:
    img_para='image/jpeg'
  elif '.png' in file_name:
    img_para='image/png'

  files=[('media',(file_name,open(file_name,'rb'),img_para))]
  headers = {}

  response = requests.request("POST", url, headers=headers, data=payload, files=files)

  print(response.text)
  res=json.loads(response.text)
  if 'media_id' not in res.keys():
    return False
  return res['media_id']


def txt2img(prompt,negative_prompt=''):#调用api由txt生成img，img以base64返回。目前落盘'res.jpg'，待优化。
  myconfig=MyConfig()
  url=myconfig.get_model_stable_diffusion_txt2img()#sd接口地址
  payload = json.dumps({
    "enable_hr": False,
    "denoising_strength": 0,
    "firstphase_width": 0,
    "firstphase_height": 0,
    "hr_scale": 2,
    "hr_second_pass_steps": 0,
    "hr_resize_x": 0,
    "hr_resize_y": 0,
    "prompt": prompt,
    "styles": [
      "string"
    ],
    "seed": -1,
    "subseed": -1,
    "subseed_strength": 0,
    "seed_resize_from_h": -1,
    "seed_resize_from_w": -1,
    "batch_size": 1,
    "n_iter": 1,
    "steps": 50,
    "cfg_scale": 7,
    "width": 512,
    "height": 512,
    "restore_faces": False,
    "tiling": False,
    "do_not_save_samples": False,
    "do_not_save_grid": False,
    "negative_prompt": negative_prompt,
    "eta": 0,
    "s_churn": 0,
    "s_tmax": 0,
    "s_tmin": 0,
    "s_noise": 1,
    "override_settings_restore_afterwards": True,
    "sampler_index": "Euler",
    "send_images": True,
    "save_images": False,
    "alwayson_scripts": {}
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  #print(response.text)

  res=json.loads(response.text)
  #print(type(res))
  res_pic=None

  if 'images' in res.keys():
    res_pic=res['images']
  #print(len(res_pic),type(res_pic))

  try:
    imgstring=res_pic[0]
    imgdata = base64.b64decode(imgstring)
    filename = 'res.jpg'  
    with open(filename, 'wb') as f:
      f.write(imgdata)
  except Exception as e:
    return False
  
  return True