class NamespaceModel:
    """
    知识库实体模型
    """
    CONSTANTS_PERMANENT = 0  # 长期
    CONSTANTS_TEMPORARY = 1  # 临时
    CONSTANTS_PREPARE = 2    # 预制

    def __init__(
            self,
            data: tuple
    ):
        """
        构造函数
        :param data: 数据集合
        """
        self.namespace = data[0]
        self.name = data[1]
        self.remark = data[2]
        self.chunk_size = data[3]
        self.chunk_overlap = data[4]
        self.type = data[5]
        self.user_id = data[6]
        self.id = data[7]
        self.deleted = data[8]
        self.creator = data[9]
        self.create_time = data[10]
        self.updator = data[11]
        self.update_time = data[12]
        self.version = data[13]

    def __str__(self):
        """
        描述函数
        :return: 描述信息
        """
        return "NamespaceModel{" \
               "'namespace': '"+str(self.namespace)+"', " \
               "'name': '"+str(self.name)+"', " \
               "'remark': '"+str(self.remark)+"', " \
               "'chunk_size': '"+str(self.chunk_size)+"', " \
               "'chunk_overlap': '"+str(self.chunk_overlap)+"', " \
               "'type': '"+str(self.type)+"', " \
               "'user_id': '"+str(self.user_id)+"', " \
               "'id': '"+str(self.id)+"', " \
               "'deleted': '"+str(self.deleted)+"', " \
               "'creator': '"+str(self.creator)+"', " \
               "'create_time': '"+str(self.create_time)+"', " \
               "'updator': '"+str(self.updator)+"', " \
               "'update_time': '"+str(self.update_time)+"', " \
               "'version': '"+str(self.version)+"'" \
               "}"

    def is_permanent_type(self):
        """
        是否为长期知识库
        :return: 识别结果
        """
        return self.type == self.CONSTANTS_PERMANENT

    def is_temporary_type(self):
        """
        是否为临时知识库
        :return: 识别结果
        """
        return self.type == self.CONSTANTS_TEMPORARY

    def is_prepare_type(self):
        """
        是否为Q&A知识库
        :return: 识别结果
        """
        return self.type == self.CONSTANTS_PREPARE
