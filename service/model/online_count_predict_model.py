class OnlineCountPredictModel:
    """
    知识库文件实体模型
    """
    def __init__(
            self,
            data: tuple
    ):
        """
        构造函数
        :param data: 数据集合
        """
        self.sale_date = data[0]
        self.max_online_cnt = data[1]
        self.online_count_pred = data[2]

    def __str__(self):
        """
        描述函数
        :return: 描述信息
        """
        return "OnlineCountPredictModel{" \
               "'sale_date': '"+str(self.sale_date)+"', " \
               "'max_online_cnt': '"+str(self.max_online_cnt)+"', " \
               "'online_count_pred': '"+str(self.online_count_pred)+"'" \
               "}"
