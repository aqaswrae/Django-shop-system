# coding:utf-8


class RETCODE:
    OK = "0"
    IMAGECODEERR = "4001"
    THROTTLINGERR = "4002"
    NECESSARYPARAMERR = "4003"
    USERERR = "4004"
    PWDERR = "4005"
    CPWDERR = "4006"
    MOBILEERR = "4007"
    SMSCODERR = "4008"
    ALLOWERR = "4009"
    SESSIONERR = "4101"
    DBERR = "5000"
    EMAILERR = "5001"
    TELERR = "5002"
    NODATAERR = "5003"
    NEWPWDERR = "5004"
    OPENIDERR = "5005"
    PARAMERR = "5006"
    STOCKERR = "5007"


err_msg = {
    RETCODE.OK: "成功",
    RETCODE.IMAGECODEERR: "图形验证码错误",
    RETCODE.THROTTLINGERR: "访问过于频繁",
    RETCODE.NECESSARYPARAMERR: "缺少必传参数",
    RETCODE.USERERR: "用户名错误",
    RETCODE.PWDERR: "密码错误",
    RETCODE.CPWDERR: "密码不一致",
    RETCODE.MOBILEERR: "手机号错误",
    RETCODE.SMSCODERR: "短信验证码有误",
    RETCODE.ALLOWERR: "未勾选协议",
    RETCODE.SESSIONERR: "用户未登录",
    RETCODE.DBERR: "数据错误",
    RETCODE.EMAILERR: "邮箱错误",
    RETCODE.TELERR: "固定电话错误",
    RETCODE.NODATAERR: "无数据",
    RETCODE.NEWPWDERR: "新密码数据",
    RETCODE.OPENIDERR: "无效的openid",
    RETCODE.PARAMERR: "参数错误",
    RETCODE.STOCKERR: "库存不足",
}
