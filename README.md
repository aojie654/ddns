# DDNS

将动态ip通过DDNS的方式关联到域名

[English](./README_en.md)

## 1. Google

通过用脚本发起request请求调用Google Domain API更新/设置DDNS

### 1.1. 原理

1. 两种模式:
   1. Global IP作为待更新记录值: <https://v4.ipv6-test.com/api/myip.php>, <https://v6.ipv6-test.com/api/myip.php> 发起request请求获取当前IP, 请求失败时以 localhost 作为 global IP
   2. 指定的 Hostname IP 作为待更新记录值: 通过 DNS 查询提供的 hostname, 请求失败时跳过
2. 通过 DNS: 8.8.8.8 解析现网中的 DNS IP
3. 将 global IP 和 DNS IP做对比
   1. 在两个IP不相等的时候通过request请求更新DNS, 更新 DNS IP 并记录日志
   2. 在两个IP相等时, 记录 "无需更新"

### 1.2. 需要的操作

1. Google Domains DDNS 当前只能支持 A/AAAA 的其中一种. 考虑到向后兼容, 配置内容与 ddns_cloudflare 类似
2. 参考 configs/google.example.ini, 在配置文件 configs/google.ini 中配置代理及各 DDNS 域名的认证信息:
   1. 在 DEFAULT 段中, 配置 proxy_http, proxy_https 代理;
      |             | 必填 | 描述                  | 样例                                   |
      | :---------- | :--- | :-------------------- | :------------------------------------- |
      | proxy_http  | 否   | 发起请求时的http代理  | proxy_http = <http://127.0.0.1:10809>  |
      | proxy_https | 否   | 发起请求时的https代理 | proxy_https = <http://127.0.0.1:10809> |
   2. 其余段:
      |                          | 必填 | 描述                                                          | 样例                           |
      | :----------------------- | :--- | :------------------------------------------------------------ | :----------------------------- |
      | 段名                     | 是   | DDNS 域名                                                     | [ddns.example.com]             |
      | records                  | 是   | DDNS记录类型: A/AAAA, 多个类型以逗号无空格分割                | records = A,AAAA               |
      | hostname_{{type_record}} | 否   | DDNS IP 更新为当前域名 IP, 名称需要与记录类型对应             | hostname_A = cname.example.com |
      | username_{{type_record}} | 是   | 用以进行鉴权的用户名, 从Google Domain DDNS 管理功能创建并查看 | username_A = zaoijAn1nfzalkJm  |
      | password_{{type_record}} | 是   | 用以进行鉴权的密码, 获取方式同 username_{{type_record}}       | password_A = fjkmavghjklkjhbn  |
3. 运行一下试试, 看日志里有没有报错
4. 将脚本执行任务添加到Crontab, 建议时间间隔: 5 min

### 1.3. 日志

按照 ddns_google_{{日期}}.log 的方式存放于 log 文件夹中

## 2. Cloudflare

获取 当前 IP / 指定域名的 DNS IP, 使用 Cloudflare API 更新 DNS 记录

### 2.1. 原理

1. 两种模式:
   1. Global IP作为待更新记录值: <https://v4.ipv6-test.com/api/myip.php>, <https://v6.ipv6-test.com/api/myip.php> 发起request请求获取当前IP, 请求失败时以 localhost 作为 global IP
   2. 指定的 Hostname IP 作为待更新记录值: 通过 DNS 查询提供的 hostname, 请求失败时跳过
2. 通过 Cloudflare API 查询域名相关记录信息, 包括:
   1. 域名
   2. 记录类型
   3. 记录值
   4. record id
3. 将 global IP 和 DNS IP做对比
   1. 在两个IP不相等的时候通过 调用 Cloudflare API 请求更新DNS, 更新 DNS IP 并记录日志
   2. 在两个IP相等时, 记录 "无需更新"

### 2.2. 需要的操作

1. 参考 configs/cloudflare.example.ini, 在配置文件 configs/cloudflare.ini 中配置代理及各 DDNS 域名的认证信息:
   1. 在 DEFAULT 段中, 配置:
      |               | 必填 | 描述                                                                        | 样例                                                |
      | :------------ | :--- | :-------------------------------------------------------------------------- | :-------------------------------------------------- |
      | proxy_http    | 否   | 发起请求时的http代理                                                        | proxy_http = <http://127.0.0.1:10809>               |
      | proxy_https   | 否   | 发起请求时的https代理                                                       | proxy_https = <http://127.0.0.1:10809>              |
      | account_email | 是   | Cloudflare 账号邮箱                                                         | account_email = user@example.com                    |
      | account_id    | 是   | Cloudflare 账号ID                                                           | account_id = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       |
      | zone_id       | 是   | Cloudflare DNS Zone ID, 当前先放在 DEFAULT里面,后续更新以支持多一级域名DDNS | zone_id = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx          |
      | api_key       | 是   | 设置里面创建的API Key                                                       | api_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     |
      | api_token     | 是   | Cloudflare API Token                                                        | api_token = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
   2. 其余段:
      |                          | 必填 | 描述                                                                        | 样例                           |
      | :----------------------- | :--- | :-------------------------------------------------------------------------- | :----------------------------- |
      | 段名                     | 是   | DDNS 域名                                                                   | [ddns.example.com]             |
      | records                  | 是   | DDNS记录类型: A/AAAA, 多个类型以逗号无空格分割                              | records = A,AAAA               |
      | ttl_{{type_record}}      | 否   | DDNS TTL 更新为配置文件中的ttl, 缺省时默认为1(自动), 名称需要与记录类型对应 | ttl_A = 120                    |
      | hostname_{{type_record}} | 否   | DDNS IP 更新为当前域名 IP, 名称需要与记录类型对应                           | hostname_A = cname.example.com |
2. 运行一下试试, 看日志里有没有报错
3. 将脚本执行任务添加到Crontab, 建议时间间隔: 5 min

### 2.3. 日志

按照 ddns_cloudflare_{{日期}}.log 的方式存放于 log 文件夹中
