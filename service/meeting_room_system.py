from config.base_config import *
from models.llms.llms_adapter import LLMsAdapter
from langchain import PromptTemplate, LLMChain
import re
import ast
import time
import hashlib
import requests
import json
import pandas as pd



query_prompt = """
你需要帮我填充一个查询会议室空闲时间的请求所需要的参数，该请求的所需要的参数模板解释和要求如下：
{params_temp_str}
我现在已经有了部分请求参数的字典，和一段补充或修改信息的语句，帮我提取这段语句中的信息补充或修改到这个请求参数字典中。
已有部分请求参数的字典如下：
{params}
补充或修改信息语句如下：
{sequence}
只用补充请求需要并且补充语句中有信息的参数，其他信息不需要，如果还没有值，保持原来的None。
请识别信息并将填充后的字典返回，只用返回字典。
"""


control_prompt = """
下面我将给你一段与会议室服务系统对话的请求语句，请识别这句话的请求类型，请求类型编码要求如下：
获取会议室清单=2，查看会议室空闲时段=4，预订会议室=5，取消预订=6，获取会议室位置信息=7
只用返回请求类型的编码数字，其他信息不需要。
会议室服务系统请求语句：{sequence}
请识别请求类型。
"""




class MeetingRoomSystem:
    """
    会议室查询预定接口请求类
    """

    def __init__(self, control_type: int, params: dict = None):
        self.control_type = control_type
        self.params = params


    def create(self):
        """
        提交会议室系统请求
        """
        if self.control_type == 4:
            response = self.get_free_time(self.params, appID='MRwechatpeac', appSecret = '9658oiugdd')
            return {
                    "answer": response,
                    "history_id": 0,
                    "scene": 'meeting_room',
            }
        else:
            pass

    def next_round(self):
        """
        返回给用户补充更多参数信息
        """



    @classmethod
    def get_free_time(cls, params, appID, appSecret):
        """
        4、获取会议室空闲时段预订信息
        """
        url = 'https://qa-meetingroomapi.amwaynet.com.cn/api/GcrData/GetFreeRoomList'
        headers = cls.get_headers(appID=appID, appSecret=appSecret)
        response = requests.get(url, headers=headers, params=params)
        if response.status_code==200:
            if json.loads(response.text)['ResultCode']=='200':
                data = json.loads(response.text)['Data']
                df = pd.DataFrame()
                for room in data:
                    room_df = pd.DataFrame(room['FreeTimeslotList'])
                    # room_df['RoomId'] = room['RoomId']
                    # room_df['RoomName'] = room['RoomName']
                    room_df['RoomLocation'] = room['RoomLocation']
                    df = pd.concat([df, room_df], ignore_index=True)
                    df = df[['RoomLocation', 'MeetingDate', 'StartTime', 'EndTime']]
                print("query success")
                return df.to_markdown()
        print("request error")
        return response.text 


    
    @classmethod
    def get_headers(cls,appID='MRwechatpeac', appSecret = '9658oiugdd'):
        """
        获取请求头
        """
        appTimes = str(int(time.time()*1000))
        appToken = cls.calculate_sha256(appID + appSecret + appTimes)
        headers = {
            "appID": appID,
            "appTimes": appTimes,
            "appToken": appToken
        }
        return headers
    

    @staticmethod
    def calculate_sha256(data):
        """
        计算SHA256加密
        """
        # 创建一个SHA256对象
        sha256 = hashlib.sha256()
        # 更新SHA256对象的输入数据
        sha256.update(data.encode('utf-8'))
        # 计算哈希值并返回结果
        return sha256.hexdigest().upper()






class MeetingParams:
    """
    会议室查询预定参数获取类
    """

    @staticmethod
    def is_all_params(params):
        for value in params.values():
            if value is None:
                return False
        return True
    

    @classmethod
    def get_params(cls,controlType, sequence, params=dict()):
        """
        获得/补充 请求参数
        :param controlType (int) 请求操作选择
        :param sequence (str) 需提取参数的句子
        :param params (dict) 待补充的请求参数字典
        :return params_need (dict) 整理好的请求参数
        """
        if not params:  # 如果没有待补充的请求参数params，则设置默认params模板
            params_need = cls.default_params(controlType)
        else:
            params_need = params
        params_new = None
        # 获得ACCL员工会议室预订信息
        if controlType==1:
            pass
        # 获取ACCL会议室清单
        elif controlType==2:
            pass
        # 获取ACCL会议室可预订权限信息
        elif controlType==3:
            params_new = cls.get_params_auth(sequence,controlType,params_need)
        # 获取会议室空闲时段预订信息
        elif controlType==4:
            params_new = cls.get_params_freetime(sequence,controlType,params_need)
        # 预定ACCL会议室
        elif controlType==5:
            params_new = cls.get_params_book(sequence,controlType,params_need)
        # 取消ACCL会议室预定
        elif controlType==6:
            params_new = cls.get_params_book(sequence,controlType,params_need)
        # 获取ACCL会议室位置信息
        elif controlType==7: 
            pass
        # 解释Wechat登录信息
        elif controlType==8:
            pass
        if params_new is not None:
            params_new = {k: v for k, v in params_new.items() if v}
            params_need.update(params_new)
        return params_need
        

    @classmethod
    def get_params_freetime(cls,sequence,controlType,params):
        """
        提取查询空闲时间段的接口参数

        :param sequence (str) 需提取参数的句子
        :param controlType (int) 请求操作选择
        :param params (dict) 待补充的请求参数字典
        :return params_need (dict) 整理好的请求参数
        """
        prompt_template = PromptTemplate(template=query_prompt, input_variables=["params_temp_str","params","sequence"])
        params_temp_str = cls.params_template(controlType=controlType)
        llm = LLMsAdapter().get_model_instance(history=None)
        chain = LLMChain(
            llm=llm,
            prompt=prompt_template,
            verbose=False,
            memory=None,
        )
        response = chain.predict(
            params_temp_str=params_temp_str,
            params=params,
            sequence=sequence
        )
        params = cls.extract_dict(response)
        return params


    @staticmethod
    def default_params(controlType):
        """
        根据会议室接口选择需要的 params 模板
        """
        params_need = None
        # 获得ACCL员工会议室预订信息
        if controlType==1:
            pass
        # 获取ACCL会议室清单
        elif controlType==2:
            pass
        # 获取ACCL会议室可预订权限信息
        elif controlType==3:
            params_need = {
                'roomID': None,  # 会议室Id
            }
        # 获取会议室空闲时段预订信息
        elif controlType==4:
            params_need = {
                "bookDate": None,  # 预订日期（yyyy-MM-dd）
                "addrCode": None,  # 会议室位置代码
                "ADNumber": 'Default test',  # 被查询的员工账号
                "departmentID": 'Default test', # 员工所属部门编码
            }
        # 预定ACCL会议室
        elif controlType==5:
            params_need = {
                "Booker": None,  # 预定人AD账号
                "BookerName": 'Default test',  # 预定人姓名
                "BookerDept": 'Default test',  # 预订人所在部门
                "absBookerPhone": 'Default test',  # 预订人电话
                "BookerEmail": 'Default test',  # 预订人邮箱
                "RoomId": None,  # 会议室Id
                "StartTime": None,  # 预定开始时间（yyyy-MM-dd HH:mm）
                "EndTime": None,  # 预定结束时间（yyyy-MM-dd HH:mm）
                "MeetingTitle": 'Default test',  # 会议主题
                "ParticipantsCount": 10,  # 预约人数
                "MeetingCatelog": 2,  # 预定会议类型（内部员工使用=1, 公司独立主办会议=2, 与营销人员合办会议=3, 营销人员提请举办会议=4，此处为固定值：2）
                "ParticipantList": [{
                    'NameCN': 'Default test',
                    'NameEN': 'Default test',
                    'Participator': 'Default test',
                    'ParticipateType': 1}],  # 参与人列表（每个人包括信息"NameCN": 中文名, "NameEN": 英文名, "Participator": 参与者编号, "ParticipateType": 参与者类型(参与者类型：1内部参与者， 2外部参与者)）
            }
        # 取消ACCL会议室预定
        elif controlType==6:
            params = {
                'CancelledBy': None,  # 取消人AD账号, 取消者和预定者必须为同一账号
                'BookId': None,  # 预定记录Id
            }
        # 获取ACCL会议室位置信息
        elif controlType==7: 
            pass
        # 解释Wechat登录信息
        elif controlType==8:
            pass
        return params_need

    
    @staticmethod
    def extract_dict(text):
        """
        输入文本提取Python或JSON代码块里的字典或JSON文本
        :params text (str) 包含python或json代码块/json文本
        :return my_dict (dict) 提取出的字典
        """
        # 尝试匹配Python或JSON代码块
        pattern = r'```(?:python|json)\n[^`]?({[^`]*})\n?```'
        match = re.search(pattern, text)
        if match:
            # 提取字典并尝试转换为Python对象
            dict_str = match.group(1)
            try:
                my_dict = ast.literal_eval(dict_str)
                return my_dict
            except (ValueError, SyntaxError) as e:
                print("提取的字符串无法转换为字典:", e)
                return None

        # 如果没有找到代码块，尝试解析整个文本作为JSON
        try:
            my_dict = json.loads(text)
            return my_dict
        except json.JSONDecodeError as e:
            # 如果既不是代码块也不是JSON文本，则返回None
            print("文本既不是有效的代码块，也不是有效的JSON文本:", e)
            return None

        
    @staticmethod
    def get_controlType(sequence):
        """
        识别请求的类型并返回预定义的操作码
        :param sequence (str) 请求语句
        :return controlType (int) 请求类型编号
        """
        prompt_template = PromptTemplate(template=control_prompt, input_variables=["sequence"])
        llm = LLMsAdapter().get_model_instance(history=None)
        chain = LLMChain(
            llm=llm,
            prompt=prompt_template,
            verbose=False,
            memory=None,
        )
        response = chain.predict(sequence=sequence)
        controlType = int(re.findall(r'\d+', response)[0])  # 匹配字符串里的第一个数字
        return controlType

    
    
    
    @staticmethod
    def params_template(controlType):
        """
        请求参数模板要求
        """
        params_temp_str = None
        if controlType == 3:
            params_temp_str = """
    ```python
    {
        "roomID": # 会议室Id
    }
    ```
            """
        elif controlType == 4:
            params_temp_str = """
    ```python
    {
        "bookDate": # 预订日期（yyyy-MM-dd）
        "addrCode": # 会议室位置代码
        "ADNumber": # 被查询的员工账号
        "departmentID": # 员工所属部门编码
    }
    ```
            """
        elif controlType == 5:
            params_temp_str = """
    ```python
    {
        "Booker": # 预定人AD账号
        "BookerName": # 预定人姓名
        "BookerDept": # 预订人所在部门
        "BookerPhone": # 预订人电话
        "BookerEmail": # 预订人邮箱

        "RoomId": # 会议室Id
        "StartTime": # 预定开始时间（yyyy-MM-dd HH:mm）
        "EndTime": # 预定结束时间（yyyy-MM-dd HH:mm）
        "MeetingTitle": # 会议主题
        "ParticipantsCount": # 预约人数
        "MeetingCatelog": # 预定会议类型（内部员工使用=1, 公司独立主办会议=2, 与营销人员合办会议=3, 营销人员提请举办会议=4，此处为固定值：2）
        "ParticipantList": # 参与人列表（每个人包括信息"NameCN": 中文名, "NameEN": 英文名, "Participator": 参与者编号, "ParticipateType": 参与者类型(参与者类型：1内部参与者， 2外部参与者)）
    }
    ```
            """
        elif controlType == 6:
            params_temp_str = """
    ```python
    {
        "CancelledBy": 取消人AD账号, 取消者和预定者必须为同一账号
        "BookId": 预定记录Id
    }
    ```
            """
        return params_temp_str








