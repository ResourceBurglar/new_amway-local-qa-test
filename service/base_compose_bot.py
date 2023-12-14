from service.model.chat_bot_model import ChatBotModel


class BaseComposeBot:
    """
    组合机器人功能的超类
    """
    @staticmethod
    def split_slave_bot(chatBotModel: ChatBotModel):
        """
        切分组装从属机器人信息
        :param chatBotModel: 机器人模型对象
        :return: 从属机器人
        """
        slave_bot_dict = {}
        if chatBotModel.is_master_type() and chatBotModel.slave_bot_mark:
            model_list = chatBotModel.slave_bot_mark.split(",")
            for model in model_list:
                _models = tuple(model.split(":"))
                if len(_models) == 2:
                    slave_bot_dict[_models[0]] = _models[1]
        return slave_bot_dict
