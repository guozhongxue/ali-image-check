#!flask/bin/python
from flask import Flask
from flask import request as r
from aliyunsdkcore import client
from aliyunsdkgreen.request.v20180509 import ImageSyncScanRequest
from aliyunsdkgreenextension.request.extension import HttpContentHelper
import json
import uuid
from flask import make_response, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/o')
def oss():
    u = r.args.get('url',default='');
    if u[0:4] != 'http':
        return suc(None,1,'Error')
    # 请使用您自己的AccessKey信息。
    clt = client.AcsClient("accessKeyId", "accessKeyId", "cn-beijing")
    # 每次请求时需要新建request，请勿复用request对象。
    request = ImageSyncScanRequest.ImageSyncScanRequest()
    request.set_accept_format('JSON')
    task = {
        "dataId": str(uuid.uuid1()),
        "url": u
    }

    # 设置待检测的图片，一张图片对应一个检测任务。
    # 多张图片同时检测时，处理时间由最后一张处理完的图片决定。
    # 通常情况下批量检测的平均响应时间比单任务检测长，一次批量提交的图片数越多，响应时间被拉长的概率越高。
    # 代码中以单张图片检测作为示例，如果需要批量检测多张图片，请自行构建多个任务。
    # 一次请求中可以检测多张图片，每张图片支持检测多个风险场景，计费按照单图片单场景检测叠加计算。
    # 例如：检测2张图片，场景传递porn和terrorism，则计费按照2张图片鉴黄和2张图片暴恐检测计算。
    request.set_content(HttpContentHelper.toValue({"tasks": [task],
                                                   "scenes": ["porn","terrorism","ad","qrcode","live","logo"],
                                                   "bizType":"examine"#自定义模板
                                                   }))
    response = clt.do_action_with_exception(request)
    # print(response)
    result = json.loads(response)
    result = json.loads(response)
    if 200 == result["code"]:
        taskResults = result["data"]
        for taskResult in taskResults:
            if (200 == taskResult["code"]):
                sceneResults = taskResult["results"]
                for sceneResult in sceneResults:
                    scene = sceneResult["scene"]
                    suggestion = sceneResult["suggestion"]
                    # 根据scene和suggetion设置后续操作。
                    # do something
                    if (suggestion != "pass"):
                        return suc({'scene': scene}, 3, 'Failed')
                    # print(scene)
            else:
                return suc({'result': result}, 2, 'Faulty')
        return suc()
    return suc({'result': result}, 2, 'Faulty')


def suc(data,status=0,msg='OK'):
    return jsonify({'data':data,'status':status,'msg':msg})

if __name__ == '__main__':
    app.run(debug=True)