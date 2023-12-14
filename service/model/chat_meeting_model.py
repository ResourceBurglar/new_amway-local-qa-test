class ChatMeetingModel:
    """
    会议室预订历史聊天记录
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
        self.question_time = data[4]
        self.answer_time = data[5]
        self.category = data[6]
        self.parameters = data[7]
        self.group_id = data[8]

    def __str__(self):
        """
        描述函数
        :return: 描述信息
        """
        return "ChatMeetingModel{" \
               "'question': '"+str(self.question)+"', " \
               "'answer': '"+str(self.answer)+"', " \
               "'user_id': '"+str(self.user_id)+"', " \
               "'bot_id': '"+str(self.bot_id)+"', " \
               "'question_time': '"+str(self.question_time)+"', " \
               "'answer_time': '"+str(self.answer_time)+"', " \
               "'category': '"+str(self.category)+"', " \
               "'group_id': '"+str(self.group_id)+"', " \
               "'parameters': '"+str(self.parameters)+"'" \
               "}"
