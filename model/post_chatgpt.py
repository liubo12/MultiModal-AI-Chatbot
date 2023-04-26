import openai
import sys
sys.path.append('..')
from config import MyConfig

def achieve_query(messages_of_user,history=False):#history默认为False，否则为history query
	user_role={'role':'user','content':messages_of_user}
	if not history:
		res=[]
		res.append(user_role)
		return res
	else:
		history.append(user_role)
		return history
	#chatGPT的请求参数query
	#query[{'role':'user','content':''},{'role':'assistant','':''}] 
	#列表里存的是dict格式数据  user是用词问话 assistant是gpt的回话

def chat_GPT(query=""):
	myconfig=MyConfig()
	
	openai.api_key=myconfig.get_model_chatgpt_api_key()	#openai.api_key
	print('api_key')
	print(myconfig.get_model_chatgpt_api_key())
	chat_model=myconfig.get_model_chatgpt_chat_model()	#chat_model="gpt-3.5-turbo"
	print('chat_model')
	print(chat_model)
	
	try:
		response = openai.ChatCompletion.create(model=chat_model,messages=query,temperature=0.75,frequency_penalty= 0.0,presence_penalty=1.0)	
	except Exception as e:
		return False
	response_content = response.choices[0]['message']['content']
	return response_content
    #used_token = response['usage']['total_tokens']
	#接口参数说明
	#temperature熵值，在[0,1]之间，越大表示选取的候选词越随机，回复越具有不确定性，
	#建议和top_p参数二选一使用，创意性任务越大越好，精确性任务越小越好
	#max_tokens=4096,  # 回复最大的字符数，为输入和输出的总数
	#top_p=model_conf(const.OPEN_AI).get("top_p", 0.7),,  
	#候选词列表。0.7 意味着只考虑前70%候选词的标记，建议和temperature参数二选一使用
	#frequency_penalty= 0.0,[-2,2]之间，
	#该值越大则越降低模型一行中的重复用词，更倾向于产生不同的内容
	#presence_penalty= 1.0[-2,2]之间，该值越大则越不受输入限制，
	#将鼓励模型生成输入中不存在的新词，更倾向于产生不同的内容