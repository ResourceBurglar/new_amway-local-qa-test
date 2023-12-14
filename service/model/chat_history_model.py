class ChatHistoryModel:
    """
    历史聊天记录
    """
    def __init__(
            self,
            data: tuple
    ):
        """
        构造函数
        :param data: 数据集合
        """
        self.question = data[0]
        self.answer = data[1]
        self.user_id = data[2]
        self.bot_id = data[3]
        self.create_time = data[4]
        self.update_time = data[5]
        self.deleted = data[6]
        self.creator = data[7]
        self.updator = data[8]
        self.answer_like = data[9]
        self.group_uuid = data[10]

    def __str__(self):
        """
        描述函数
        :return: 描述信息
        """
        return "ChatHistoryModel{" \
               "'question': '"+str(self.question)+"', " \
               "'answer': '"+str(self.answer)+"', " \
               "'user_id': '"+str(self.user_id)+"', " \
               "'bot_id': '"+str(self.bot_id)+"', " \
               "'create_time': '"+str(self.create_time)+"', " \
               "'update_time': '"+str(self.update_time)+"', " \
               "'deleted': '"+str(self.deleted)+"', " \
               "'creator': '"+str(self.creator)+"', " \
               "'updator': '"+str(self.updator)+"', " \
               "'answer_like': '"+str(self.answer_like)+"', " \
               "'group_uuid': '"+str(self.group_uuid)+"'" \
               "}"
