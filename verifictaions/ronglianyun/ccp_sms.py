from ronglian_sms_sdk import SmsSDK
import json

accId = '2c94811c88bf3503018900ca795012ba'
accToken = '382b17b971884ddfad5c7ecadc07149b'
appId = '2c94811c88bf3503018900ca7a9d12c1'

class CCP(object):
    # 使用单例模式
    _instance = None
    def __new__(cls, *args, **kwargs):
        # 给对象分配内存空间
        if cls._instance is None:
            # 判断属性是否为空 ， 为空说明这个类还未生成对象
            # 生成对象 ， 给对象分配内存空间
            cls._instance = super().__new__(cls, *args, **kwargs)
        # new 必须要有返回值 ， 返回的是对象的引用（对象内存地址）
        return cls._instance

    def send_message(self , mobile , datas , tid):
        sdk = SmsSDK(accId, accToken, appId)
        resp = sdk.sendMessage(tid, mobile, datas)
        # print(resp)
        # print(type(resp))
        res = json.loads(resp)
        if res['statusCode'] == '000000':
            return 0
        else:
            return -1
sand_code = CCP()

if __name__ == '__main__':
    c = CCP()
    c.send_message('17841687578',('1234' , '1') , 1)