# DDNS

将一个随机ip通过DDNS的方式关联到域名

## Google

通过用脚本发起request请求掉用Google Domain API更新/设置DDNS

### 原理

1. 通过向whatismyip.akamai.com发起request请求获取当前IP
2. 通过dig ${Your_Domain_Name} @8.8.8.8 +short 查询Google Domain中的DNS记录以获取IP in DNS
3. 将两个ip做对比
   1. 在两个IP不相等的时候通过request请求更新DNS, 并将返回结果赋值给 update_result
   2. 相等时, 将 "No need to update" 赋值给 update_result

### 需要的操作

1. 修改脚本中的Hostname, Username, Passwd, Curl Proxy(可选, 不需要则设置为空字符串 "" )
2. 将脚本以bash ${Path_Of_DDNS_google.sh} 的格式添加到Crontab(因此无需chmod +x), 建议时间间隔大于5 min

### 查看日志

可以在/tmp/ddns_${Your_Domain_Name}.log里查看更新的日志
