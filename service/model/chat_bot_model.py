class ChatBotModel:
    """
    机器人实体模型
    """
    CONSTANTS_BOT_MASTER = "Master"  # 主机器人
    CONSTANTS_BOT_SLAVER = "Slave"   # 从机器人
    CONSTANTS_PRIVATE_BOT = 0      # 领域问答机器人
    CONSTANTS_PUBLIC_BOT = 1       # 公共问答机器人
    CONSTANTS_CHAINS_STUFF = "stuff"
    CONSTANTS_CHAINS_REFINE = "refine"

    def __init__(
            self,
            data: tuple
    ):
        """
        构造函数
        :param data: 数据集合
        """
        # 机器人标识
        self.bot_id = data[0]
        # 提示词信息
        self.prompt = data[1]
        # 提示词变量
        self.prompt_variables = data[8]
        # 提示词前缀信息
        self.prefix_prompt = data[9]
        # 提示词前缀变量
        self.prefix_prompt_variables = data[10]
        # 知识库标识
        self.namespace_id = data[2]
        # 机器人名称
        self.name = data[3]
        # 长程记忆长度
        self.memory_limit_size = data[4]
        # 机器人欢迎语
        self.welcome_tip = data[5]
        # 语义搜索Top值
        self.vector_top_k = data[6]
        # 问答链交互类型
        self.chains_chunk_type = data[7]
        # 机器人类型: Master[主类型] Slave[从类型]
        self.bot_type = data[11]
        # 从节点机器人标记
        self.slave_bot_mark = data[12]
        # (Slave类型机器人)固定问题
        self.fixed_ques = data[13]
        # 机器人使用类型: 0[领域问答机器人] 1[公共知识机器人]
        self.use_type = data[14]
        # 提示词后缀信息
        self.suffix_prompt = data[15]
        self.id = data[16]
        self.deleted = data[17]
        self.creator = data[18]
        self.create_time = data[19]
        self.updator = data[20]
        self.update_time = data[21]
        self.version = data[22]

    def __str__(self):
        """
        描述函数
        :return: 描述信息
        """
        return "ChatBotModel{" \
               "'bot_id': '"+str(self.bot_id)+"', " \
               "'prompt': '"+str(self.prompt)+"', " \
               "'prompt_variables': '"+str(self.prompt_variables)+"', " \
               "'prefix_prompt': '"+str(self.prefix_prompt)+"', " \
               "'prefix_prompt_variables': '"+str(self.prefix_prompt_variables)+"', " \
               "'namespace_id': '"+str(self.namespace_id)+"', " \
               "'name': '"+str(self.name)+"', " \
               "'memory_limit_size': '"+str(self.memory_limit_size)+"', " \
               "'welcome_tip': '"+str(self.welcome_tip)+"', " \
               "'vector_top_k': '"+str(self.vector_top_k)+"', " \
               "'chains_chunk_type': '"+str(self.chains_chunk_type)+"', " \
               "'bot_type': '"+str(self.bot_type)+"', " \
               "'slave_bot_mark': '"+str(self.slave_bot_mark)+"', " \
               "'fixed_ques': '"+str(self.fixed_ques)+"', " \
               "'use_type': '"+str(self.use_type)+"', " \
               "'suffix_prompt': '"+str(self.suffix_prompt)+"', " \
               "'id': '"+str(self.id)+"', " \
               "'deleted': '"+str(self.deleted)+"', " \
               "'creator': '"+str(self.creator)+"', " \
               "'create_time': '"+str(self.create_time)+"', " \
               "'updator': '"+str(self.updator)+"', " \
               "'update_time': '"+str(self.update_time)+"', " \
               "'version': '"+str(self.version)+"'" \
               "}"

    def is_master_type(self):
        """
        是否为主机器人
        :return: 识别结果
        """
        return self.bot_type == self.CONSTANTS_BOT_MASTER

    def is_stuff_chains(self):
        """
        是否 Stuff 类型的聊天链
        :return: 识别结果
        """
        return self.chains_chunk_type == self.CONSTANTS_CHAINS_STUFF

    def is_refine_chains(self):
        """
        是否 Refine 类型的聊天链
        :return: 识别结果
        """
        return self.chains_chunk_type == self.CONSTANTS_CHAINS_REFINE

    def is_public_bot(self):
        """
        是否为公共问答机器人
        :return: 识别结果
        """
        return self.use_type == self.CONSTANTS_PUBLIC_BOT

    def is_private_bot(self):
        """
        是否为领域问答机器人
        :return: 识别结果
        """
        return self.use_type == self.CONSTANTS_PRIVATE_BOT

