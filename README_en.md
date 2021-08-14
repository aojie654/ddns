# DDNS

Update DNS record with DDNS

[中文](./README.md)

## 1. Google

Send request to Google Domain API to set DDNS

### 1.1. How it works

1. 2 types supported:
   1. Using Global IP as DDNS record value: send request to <https://v4.ipv6-test.com/api/myip.php>, <https://v6.ipv6-test.com/api/myip.php> to get current IP and using localhost as global IP when failed.
   2. Using Hostname record as DDNS record value: lookup IP from DNS of specified hostname, skip process if lookup failed.
2. Lookup current record IP with DNS: 8.8.8.8
3. Compare global IP and DNS IP:
   1. Update DNS record and log if not equal
   2. Just log when equal

### 1.2. What should you do

1. Google Domains DDNS is only support one of A/AAAA at currently. Config content likes to Cloudflare one to complicate with the futher version
2. Config DDNS information in configs/google.ini by referring configs/google.example.ini:
   1. Config the following settings in stanza: DEFAULT :
      |             | Required | Description                      | Example                                |
      | :---------- | :------- | :------------------------------- | :------------------------------------- |
      | proxy_http  | N        | http proxy when sending request  | proxy_http = <http://127.0.0.1:10809>  |
      | proxy_https | N        | https proxy when sending request | proxy_https = <http://127.0.0.1:10809> |
   2. Other stanza:
      |                          | Required | Description                                                                                     | Example                        |
      | :----------------------- | :------- | :---------------------------------------------------------------------------------------------- | :----------------------------- |
      | Stanza Name              | Y        | DDNS Hostname                                                                                   | [ddns.example.com]             |
      | records                  | Y        | DDNS Record type: A/AAAA, using "," to split if there are multiple types                        | records = A,AAAA               |
      | hostname_{{type_record}} | N        | Update DDNS records to IP related with this hostname. Record name should related to record type | hostname_A = cname.example.com |
      | username_{{type_record}} | Y        | Google Domain DDNS credential: username. You could find it at DDNS manage panel.                | username_A = zaoijAn1nfzalkJm  |
      | password_{{type_record}} | Y        | Google Domain DDNS credential: password. Same way to get with username_{{type_record}}          | password_A = fjkmavghjklkjhbn  |
3. Excute the script and check if there are some errors or not in log.
4. Add script task to Crontab. Internal should be 5 min or longger.

### 1.3. Log

Log file stored in folder log which named ddns_google_{{date}}.log

## 2. Cloudflare

Get current global IP / DNS IP with specified hostname then using Cloudflare API to record at DNS

### 2.1. How it works

1. 2 types supported:
   1. Using Global IP as DDNS record value: send request to <https://v4.ipv6-test.com/api/myip.php>, <https://v6.ipv6-test.com/api/myip.php> to get current IP and using localhost as global IP when failed.
   2. Using Hostname record as DDNS record value: lookup IP from DNS of specified hostname, skip process if lookup failed.
2. Get information of hostname via Cloudflare API which includes:
   1. Hostname
   2. Record type
   3. Record value
   4. Record id
3. Compare global IP and DNS IP:
   1. Update DNS record and log if not equal
   2. Just log when equal

### 2.2. What should you do

1. Config DDNS information in configs/cloudflare.ini by referring configs/cloudflare.example.ini:
   1. Config the following settings in stanza: DEFAULT :
      |               | Required | Description                                                                                             | Example                                             |
      | :------------ | :------- | :------------------------------------------------------------------------------------------------------ | :-------------------------------------------------- |
      | proxy_http    | N        | http proxy when sending request                                                                         | proxy_http = <http://127.0.0.1:10809>               |
      | proxy_https   | N        | https proxy when sending request                                                                        | proxy_https = <http://127.0.0.1:10809>              |
      | account_email | Y        | Cloudflare account email                                                                                | account_email = user@example.com                    |
      | account_id    | Y        | Cloudflare account ID                                                                                   | account_id = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       |
      | zone_id       | Y        | Cloudflare DNS Zone ID. Set in stanza: DEFAULT at currently. Will included in hostname stanza in future | zone_id = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx          |
      | api_key       | Y        | API Key created in settings                                                                             | api_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx     |
      | api_token     | Y        | Cloudflare API Token                                                                                    | api_token = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx |
   2. 其余段:
      |                          | Required | Description                                                                                                                     | Example                        |
      | :----------------------- | :------- | :------------------------------------------------------------------------------------------------------------------------------ | :----------------------------- |
      | Stanza Name              | Y        | DDNS Hostname                                                                                                                   | [ddns.example.com]             |
      | records                  | Y        | DDNS Record type: A/AAAA, using "," to split if there are multiple types                                                        | records = A,AAAA               |
      | ttl_{{type_record}}      | N        | Update DDNS ttl to the settings in configuration file, it will be 1(auto) if not set. Record name should related to record type | ttl_A = 120                    |
      | hostname_{{type_record}} | N        | Update DDNS records to IP related with this hostname. Record name should related to record type                                 | hostname_A = cname.example.com |
2. Excute the script and check if there are some errors or not in log.
3. Add script task to Crontab. Internal should be 5 min or longger.

### 2.3. Log

Log file stored in folder log which named ddns_cloudflare_{{date}}.log
