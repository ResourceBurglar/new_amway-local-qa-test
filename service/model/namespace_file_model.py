class NamespaceFileModel:
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
        self.id = data[0]
        self.namespace_id = data[1]
        self.name = data[2]
        self.path = data[3]
        self.type = data[4]
        self.size = data[5]
        self.remark = data[6]
        self.vector_ids = data[7]
        self.vector_status = data[8]
        self.vector_count = data[9]
        self.channel = data[10]
        self.deleted = data[11]
        self.creator = data[12]
        self.create_time = data[13]
        self.updator = data[14]
        self.update_time = data[15]
        self.version = data[16]
        self.display_name = data[17]
        self.md5 = data[18]

    def __str__(self):
        """
        描述函数
        :return: 描述信息
        """
        return "NamespaceFileModel{" \
               "'id': '"+str(self.id)+"', " \
               "'namespace_id': '"+str(self.namespace_id)+"', " \
               "'name': '"+str(self.name)+"', " \
               "'path': '"+str(self.path)+"', " \
               "'type': '"+str(self.type)+"', " \
               "'size': '"+str(self.size)+"', " \
               "'remark': '"+str(self.remark)+"', " \
               "'vector_ids': '"+str(self.vector_ids)+"', " \
               "'vector_status': '"+str(self.vector_status)+"', " \
               "'vector_count': '"+str(self.vector_count)+"', " \
               "'channel': '"+str(self.channel)+"', " \
               "'deleted': '"+str(self.deleted)+"', " \
               "'creator': '"+str(self.creator)+"', " \
               "'create_time': '"+str(self.create_time)+"', " \
               "'updator': '"+str(self.updator)+"', " \
               "'update_time': '"+str(self.update_time)+"', " \
               "'version': '"+str(self.version)+"', " \
               "'display_name': '"+str(self.display_name)+"', " \
               "'md5': '"+str(self.md5)+"'" \
               "}"
