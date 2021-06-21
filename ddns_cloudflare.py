# encoding = utf-8

import configparser
import datetime
import json
import logging
import os
from datetime import datetime

import dns.resolver
import requests

# Root path
path_root = os.path.dirname(__file__)

# Log Path in path_root/log/
path_log_dir = os.path.join(path_root, "log")
filename_log = "ddns_cloudflare_{0:%Y%m%d}.log".format(datetime.now())
path_log = os.path.join(path_log_dir, filename_log)

# Create log folder if not exist
if not os.path.exists(path_log_dir):
    os.mkdir(path_log_dir)

# Set log format
logging.basicConfig(format="%(asctime)s; %(levelname)s; %(message)s", filename=path_log, level=logging.INFO)

# Config path is path_root/.config
filename_config = "cloudflare.ini"
path_config_dir = os.path.join(path_root, "configs")
path_config = os.path.join(path_config_dir, filename_config)
log_content = "Config path is: {0}".format(path_config)
logging.info(log_content)

# Load config
config = configparser.ConfigParser()
config.read(path_config)
config_default = config["DEFAULT"]

# Initial proxy result
proxies_set = dict()
# Load Proxy if exist
if "proxy_http" in config_default.keys():
    proxies_set["http"] = config_default["proxy_http"]
if "proxy_https" in config_default.keys():
    proxies_set["https"] = config_default["proxy_https"]
log_content = "Proxy is: {0}".format(proxies_set)
logging.info(log_content)

# Read [ Account Email, Account ID, Zone ID, API Key, API Token ]
account_email = config_default["account_email"]
account_id = config_default["account_id"]
zone_id = config_default["zone_id"]
api_key = config_default["api_key"]
api_token = config_default["api_token"]

# Initial Headers
header_record = {
    "X-Auth-Email": account_email,
    "X-Auth-Key": api_key,
    "Content-Type": "application/json",
}


def get_global_ip():
    """
    Get global ip of ipv4 and ipv6. Using localhost(127.0.0.1 and ::1) as global IP if failed.
    Input: None
    Return: Global IP.
    """

    # Initial current IP result
    result_ip_cur = dict()

    # Get current global IPv4
    # URL to get IPv4 address
    url_ip4 = "https://v4.ipv6-test.com/api/myip.php"
    try:
        result_ip4_cur = requests.get(url_ip4, timeout=5).text.replace("\n", "")
    except Exception as exception_tmp:
        result_ip4_cur = "127.0.0.1"
        logging.error("Error occured when get global IPv4, using 127.0.0.1 to global IP.", exc_info=exception_tmp)
    # result_ip4_cur = get_dns_ip(hostname=hostname, type_record="A")
    # Use 127.0.0.1 as result IPv4 address for debug.
    # result_ip4_cur = "127.0.0.1"

    # Get current global IPv6
    # URL to get IPv6 address
    url_ip6 = "https://v6.ipv6-test.com/api/myip.php"
    try:
        result_ip6_cur = requests.get(url_ip6, timeout=5).text.replace("\n", "")
    except Exception as exception_tmp:
        result_ip6_cur = "::1"
        logging.error("Error occured when get global IPv6, using ::1 to global IP. ", exc_info=exception_tmp)
    # result_ip4_cur = get_dns_ip(hostname=hostname, type_record="AAAA")
    # Use ::1 as result IPv6 address for debug.
    # result_ip6_cur = "::1"

    # Change result here
    result_ip_cur = {
        "cur_A": result_ip4_cur,
        "cur_AAAA": result_ip6_cur,
    }

    # Log current IP
    result_ip_cur_json = json.dumps(result_ip_cur, indent=4, ensure_ascii=False)
    log_content = "Current IP is: {0}".format(result_ip_cur_json)
    logging.info(log_content)

    return result_ip_cur


def get_dns_ip(hostname, type_record):
    """
    Get specified record at DNS of hostname.
    Input: hostname, type_record
    Return: Flag of success, DNS IP
    """

    # Initial DNS resolver and empty result_ip_dns
    resolver_tmp = dns.resolver.Resolver()
    resolver_tmp.nameservers = ["8.8.8.8", "8.8.4.4"]
    result_ip_dns = ""

    # Initial success flag
    flag_success = False

    # IPv4 query
    try:
        result_ip_dns = resolver_tmp.resolve(hostname, type_record).rrset[0].address
        # Log current IP
        if result_ip_dns != "":
            log_content = "DNS IP of hostname: {0} : {1} is {2}".format(hostname, type_record, result_ip_dns)
        else:
            log_content = "No record of hostname: {0} : {1} at DNS.".format(hostname, type_record)
        logging.info(log_content)
        # Set success flag to True
        flag_success = True
    except Exception as exception_tmp:
        logging.error("Error occured when get DNS IP of hostname: {0} : {1}".format(hostname, type_record), exc_info=exception_tmp)

    return flag_success, result_ip_dns


def get_hostname_detail(hostname, type_records):
    """
    Get the record ID and record of hostname
    """

    logging.info("Current hostname: {0:-^40}".format(hostname))

    # Initial Hostnames result
    result_hostname = dict()
    result_hostname["hostname"] = hostname

    # Initial success flag
    flag_success = False

    # URL of list records
    url_record_list = "https://api.cloudflare.com/client/v4/zones/{0}/dns_records?name={1}".format(zone_id, hostname)
    # Get all records of this hostname
    try:
        result_request = requests.request(method="GET", url=url_record_list, headers=header_record, proxies=proxies_set, timeout=5).json()["result"]
        result_request_json = json.dumps(result_request, indent=4, ensure_ascii=False)
        log_content = "Request result is: {0}".format(result_request_json)
        logging.info(log_content)
        # Save all records content and id to dict
        for result_record in result_request:
            record_type_tmp = result_record["type"]
            if record_type_tmp in type_records:
                key_content = "content_{0}".format(record_type_tmp)
                result_hostname[key_content] = result_record["content"]
                key_record_id = "record_id_{0}".format(record_type_tmp)
                result_hostname[key_record_id] = result_record["id"]
        # Log hostname detail
        result_hostnames_json = json.dumps(result_hostname, indent=4, ensure_ascii=False)
        log_content = "Hostname detail is: {0}".format(result_hostnames_json)
        logging.info(log_content)
        # Set success flag to True
        flag_success = True
    except Exception as exception_tmp:
        log_content = "Error occured when get details of {0}.".format(hostname)
        logging.error(log_content, exc_info=exception_tmp)

    return flag_success, result_hostname


def log_generator(hostname, ip_cur, ip_dns, type_record, result_update):
    """
    Generate log.
    Input: Hostname, current ip, DNS ip, update result
    Return: Hostname: {{hostname}}, record type: {{type_record}}, current IP: {{ip_cur}}, DNS IP: {{ip_dns}}, update result: {{result_update}}
    """

    # Define log tamplate
    log_content = "Hostname: {0}, record type: {1}, current IP: {2}, DNS IP: {3}, update result: {4}, ".format(hostname, type_record, ip_cur, ip_dns, result_update)

    return log_content


def dns_update_step(hostname, result_ip_cur, config_hostname):
    """
    Update DNS record.
    Input: IP information, current ip
    Return: None
    """

    # Get type of records
    type_records = config_hostname["records"].split(",")

    # Initial blank result_ip_cur_tmp
    result_ip_cur_tmp = ""

    # Log the hostname and IP
    flag_success, hostname_detail = get_hostname_detail(hostname, type_records)

    # Return failed at get hostname detail
    if flag_success == False:
        result_update = "Get detail of hostname {0} failed.".format(hostname)
        
        return result_update

    for type_record in type_records:
        # Judge the IP was changed or not
        key_content = "content_{0}".format(type_record)
        key_id = "record_id_{0}".format(type_record)
        # Judge hostname type exist or not
        hostname_type = "hostname_{0}".format(type_record)
        if hostname_type in config_hostname.keys():
            log_content = "Using DNS mode of {0} : {1}".format(hostname, type_record)
            logging.info(log_content)

            # Get IP of hostname type record from DNS IP
            hostname_tmp = config_hostname[hostname_type]
            flag_success, result_ip_cur_tmp = get_dns_ip(hostname=hostname_tmp, type_record=type_record)
            # Return failed at get DNS IP
            if flag_success == False:
                result_update = "Get DNS IP of {0} : {1} failed.".format(hostname, type_record)

                return result_update
        else:
            # Get IP of type record from global IP
            key_cur = "cur_{0}".format(type_record)
            result_ip_cur_tmp = result_ip_cur[key_cur]
        if result_ip_cur_tmp != hostname_detail[key_content]:
            # If changed, update DNS record
            logging.info("Updating DNS records of {0} : {1}...".format(hostname, type_record))
            data_record_update = {
                "name": hostname,
                "type": type_record,
                "content": result_ip_cur_tmp,
                "ttl": 1,
                "proxied": False
            }
            # Update DNS record with HTTP POST
            url_record_update = "https://api.cloudflare.com/client/v4/zones/{0}/dns_records/{1}".format(zone_id, hostname_detail[key_id])
            try:
                result_update = requests.request(method="PUT", url=url_record_update, headers=header_record, json=data_record_update, proxies=proxies_set,timeout=5).text
            except Exception as exception_tmp:
                result_update = "Error occured when update: {0}".format(exception_tmp)
        else:
            # Log no need update
            result_update = "No need update."
        # Log result
        log_content = log_generator(hostname=hostname, type_record=type_record, ip_cur=result_ip_cur_tmp, ip_dns=hostname_detail[key_content], result_update=result_update)
        logging.info(log_content)

    # Return success of 
    result_update = "Update of hostname: {0} success.".format(hostname)

    return result_update


def testing():
    """
    Write your testing function here
    """
    pass


if __name__ == "__main__":

    # Log script start
    log_content = "{0:=^100}".format(" DDNS script start ")
    logging.info(log_content)
    # Using your testing function here
    # testing()

    # Get current IP
    result_ip_cur = get_global_ip()

    # Update each hostname in config file
    for hostname in config.sections():
        # Get hostname config
        config_hostname = config[hostname]
        # Update DNS record if config is related to hostname
        result_update = dns_update_step(hostname, result_ip_cur, config_hostname)
        logging.info(result_update)

    # Log script end
    log_content = "{0:=^100}\n".format(" DDNS script End ")
    logging.info(log_content)
