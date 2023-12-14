import json
from typing import List

from custom.amway.prepare.service.prepare_services import NamespacePrepareService
from custom.amway.prepare.service.prepare_update_param import PrepareData, PrepareUpdateParam
from service.data_entity_service import OnlineCountPredictDomain


ques_list = [
    "未来七天的电商平台流量预测数据",
    "未来几天的在线人数预测",
    "接下来几天最大在线人数是多少",
    "后天的大促会有多少人同时在线",
    "明天的流量数据是多少",
    "下周的在线人数峰值是多少",
    "未来几天平台流量是怎样的",
    "能否提供未来一周的电商平台流量预测数据？",
    "能否预测一下接下来几天的在线用户数量？",
    "在未来几天里，预计的最大在线人数会达到多少？",
    "预测后天的大促活动同时在线的人数大约有多少？",
    "能否预测一下明天大致的流量数据？",
    "预测下周在线人数的最高峰值是多少？",
    "预测一下接下来几天的平台流量趋势是怎样的？",
    "未来七天电商平台的预计流量数据是多少？",
    "未来几天的在线人数大概会是多少？",
    "能否预测接下来几天的最大在线人数是多少？",
    "能否估计后天大促时的并发在线人数？",
    "明天的网络流量数据预计是多少？",
    "下周我们预计的在线人数最高值是多少？",
    "能否提供关于未来几天平台流量的预测数据？",
    "我想了解未来七天内电商平台的流量预测情况，有相关的数据吗？",
    "能否估算一下未来几天的在线人数趋势？",
    "未来几天内，网站或应用的最大在线用户数量会是多少？",
    "后天的大促销活动，预计有多少用户会同时在线参与？",
    "能否提供关于明天流量数据的一些预测或估计？",
    "下周的在线人数最高点是多少？",
    "未来几天的平台流量预计会有什么变化？",
    "流量趋势预测",
]


def reload_online_count_predict():
    # 查询流量
    result_list = OnlineCountPredictDomain().find()

    date_list = []
    online_list = []
    predict_list = []
    for model in result_list:
        date_list.append(str(model.sale_date))
        online_list.append(int(model.max_online_cnt))
        predict_list.append(int(model.online_count_pred))
    new_date_list = [i for i in date_list[::-1]]
    new_online_list = [i for i in online_list[::-1]]
    new_predict_list = [i for i in predict_list[::-1]]

    prepare_update_list = [
        PrepareData(
            question=ques,
            answer=get_vec_data(date_list=new_date_list, online_list=new_online_list, predict_list=new_predict_list),
            scene="echart",
        )
        for ques in ques_list
    ]

    NamespacePrepareService(
        namespace_id="48",
        name="echart",
        file_display_name="echart",
        remark="echart",
        param=PrepareUpdateParam(update_list=prepare_update_list),
    ).handle()


def get_vec_data(
        date_list: List[str],
        online_list: List[int],
        predict_list: List[int],
):
    data = {
        "scene": "echart",
        "title": {
            "text": "流量趋势预测"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "legend": {},
        "toolbox": {
            "show": True,
            "feature": {
                "magicType": {
                    "type": ["line", "bar"]
                },
                "restore": {
                    "readOnly": False
                },
                "saveAsImage": {}
            }
        },
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": date_list,
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {
                "formatter": "{value} "
            }
        },
        "series": [{
            "name": "实际",
            "type": "line",
            "data": online_list,
        }, {
            "name": "预测",
            "type": "line",
            "data": predict_list,
        }]
    }
    return json.dumps(data, ensure_ascii=False)
