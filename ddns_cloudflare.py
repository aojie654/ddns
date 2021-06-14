# encoding=utf-8

from os import pathconf
import requests
from requests.api import head
import configparser
import json

# Path of credentials
path_config = "/Users/shengjyerao/.cloudflarerc"
# Initial config
config_tmp = configparser.ConfigParser()
config_tmp.read(path_config)
account_email = config_tmp["DEFAULT"]["account_email"]
account_id = config_tmp["DEFAULT"]["account_id"]
zone_id = config_tmp["DEFAULT"]["zone_id"]
api_key = config_tmp["DEFAULT"]["api_key"]
api_token = config_tmp["DEFAULT"]["api_token"]

hostname_tmp = "aa.tlsj.us"
hostname_id_tmp = "84233328482f0d039d2cf47524797ab7"
ip_tmp = "124.156.157.124"

header_record = {
    "X-Auth-Email": account_email,
    "X-Auth-Key": api_key,
    "Content-Type": "application/json",
}

# Record List
url_record_list = "https://api.cloudflare.com/client/v4/zones/{0}/dns_records?name={1}".format(zone_id, hostname_tmp)

# Record Detail
url_record_detail = "https://api.cloudflare.com/client/v4/zones/{0}/dns_records/{1}".format(zone_id, hostname_id_tmp)

# Record Update
url_record_update = "https://api.cloudflare.com/client/v4/zones/{0}/dns_records/{1}".format(zone_id, hostname_id_tmp)
data_record_update = {
    "name": hostname_tmp,
    "type": "A",
    "content": ip_tmp,
    "ttl": 120,
    "proxied": False
}


if __name__ == '__main__':
    """
    curl -X GET "https://api.cloudflare.com/client/v4/zones/b66c6e351a60bd8cae02f74bd63193f0/dns_records/84233328482f0d039d2cf47524797ab7" \
     -H "Content-Type:application/json" \
     -H "X-Auth-Key:1356cb5af0d26ecb00277e31ce470136f4115" \
     -H "X-Auth-Email:aojie654@live.cn"

    curl -X PUT "https://api.cloudflare.com/client/v4/zones/b66c6e351a60bd8cae02f74bd63193f0/dns_records/84233328482f0d039d2cf47524797ab7" \
     -H "Content-Type:application/json" \
     -H "X-Auth-Key:1356cb5af0d26ecb00277e31ce470136f4115" \
     -H "X-Auth-Email:aojie654@live.cn" \
     --data '{"name": "aa.tlsj.us", "type": "A", "content": "124.156.157.124", "ttl": 120, "proxied": false}'
    """

    # List All Records
    # rr = requests.request(method="GET", url=url_record_list, headers=header_record)
    # Get Details
    rr = requests.request(method="GET", url=url_record_detail, headers=header_record)
    # Update Details
    # rr = requests.request(method="PUT", url=url_record_update, headers=header_record, data="{0}".format(data_record_update))
    print(json.dumps(rr.json(), indent=2, ensure_ascii=False))
