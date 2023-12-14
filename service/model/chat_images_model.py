class ChatImagesModel:

    def __init__(
            self,
            data: tuple
    ):
        self.id = data[0]
        self.deleted = data[1]
        self.creator = data[2]
        self.create_time = data[3]
        self.updator = data[4]
        self.update_time = data[5]
        self.version = data[6]
        self.user_id = data[7]
        self.source = data[8]
        self.target = data[9]
        self.answer_like = data[10]
        self.num = data[11]
        self.uuid = data[12]
        self.style = data[13]
        self.model = data[14]
        self.dir = data[15]
        self.status = data[16]

    def __str__(self):
        """
        描述函数
        :return: 描述信息
        """
        return "ChatImagesModel{" \
               "'id': '"+str(self.id)+"', " \
               "'deleted': '"+str(self.deleted)+"', " \
               "'creator': '"+str(self.creator)+"', " \
               "'create_time': '"+str(self.create_time)+"', " \
               "'updator': '"+str(self.updator)+"', " \
               "'update_time': '"+str(self.update_time)+"', " \
               "'version': '"+str(self.version)+"', " \
               "'user_id': '"+str(self.user_id)+"', " \
               "'source': '"+str(self.source)+"', " \
               "'target': '"+str(self.target)+"', " \
               "'answer_like': '"+str(self.answer_like)+"', " \
               "'num': '"+str(self.num)+"', " \
               "'uuid': '"+str(self.uuid)+"', " \
               "'style': '"+str(self.style)+"', " \
               "'model': '"+str(self.model)+"', " \
               "'dir': '"+str(self.dir)+"', " \
               "'status': '"+str(self.status)+"'" \
               "}"
