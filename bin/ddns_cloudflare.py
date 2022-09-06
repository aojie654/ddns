# encoding = utf-8

import configparser
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import dns.resolver
import requests

# Root path
path_root = Path(__file__).parents[1]

# Log Path in path_root/log/
path_log_dir = path_root.joinpath("log")
filename_log = "ddns_cloudflare.log"
path_log = path_log_dir.joinpath(filename_log)

# Create log folder if not exist
if not Path.exists(path_log_dir):
    Path.mkdir(path_log_dir)

# Set log format
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
logger_formatter = logging.Formatter(fmt="%(asctime)s; %(levelname)s; %(message)s")
logger_handler =  TimedRotatingFileHandler(path_log, when="d", interval=1, backupCount=5)
logger_handler.setFormatter(fmt=logger_formatter)
logger.addHandler(logger_handler)

# Log script start
log_content = "{0:=^100}".format(" DDNS script start ")
logger.info(log_content)

# Config path is path_root/.config
filename_config = "cloudflare.ini"
path_config_dir = path_root.joinpath("configs")
path_config = path_config_dir.joinpath(filename_config)
log_content = "Config path is: {:}".format(path_config)
logger.info(log_content)

# Load config
config = configparser.ConfigParser()
config.read(path_config)
config_default = config["DEFAULT"]

# Load URL of IPv4, IPv6
# URL to get IPv4 address
url_key = "url_ip4"
if url_key in config_default.keys():
    url_ip4 = config_default[url_key]
else:
    url_ip4 = "http://ipv4.whatismyip.akamai.com/"
# URL to get IPv6 address
url_key = "url_ip6"
if url_key in config_default.keys():
    url_ip6 = config_default[url_key]
else:
    url_ip6 = "http://ipv4.whatismyip.akamai.com/"

# Initial proxy result
proxies_set = dict()
# Load Proxy if exist
if "proxy_http" in config_default.keys():
    proxies_set["http"] = config_default["proxy_http"]
if "proxy_https" in config_default.keys():
    proxies_set["https"] = config_default["proxy_https"]
log_content = "Proxy is: {:}".format(proxies_set)
logger.info(log_content)

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
    try:
        result_ip4_cur = requests.get(url_ip4, timeout=5).text.replace("\n", "")
    except Exception as exception:
        result_ip4_cur = "127.0.0.1"
        log_content = "Error occured when get global IPv4, using 127.0.0.1 to global IP: {:}".format(exception)
        logger.error(log_content)
        # logger.exception(log_content)
    # result_ip4_cur = get_dns_ip(hostname=hostname, type_record="A")
    # Use 127.0.0.1 as result IPv4 address for debug.
    # result_ip4_cur = "127.0.0.1"

    # Get current global IPv6
    try:
        result_ip6_cur = requests.get(url_ip6, timeout=5).text.replace("\n", "")
    except Exception as exception:
        result_ip6_cur = "::1"
        log_content = "Error occured when get global IPv6, using ::1 to global IP: {:}".format(exception)
        logger.error(log_content)
        # logger.exception(log_content)
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
    log_content = "Current IP is: {:}".format(result_ip_cur_json)
    logger.info(log_content)

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
            log_content = "DNS IP of hostname: {:} : {:} is {:}".format(hostname, type_record, result_ip_dns)
        else:
            log_content = "No record of hostname: {:} : {:} at DNS.".format(hostname, type_record)
        logger.info(log_content)
        # Set success flag to True
        flag_success = True
    except Exception as exception:
        log_content = "Error occured when get DNS IP of hostname: {:}".format(exception)
        logger.error(log_content)
        # logger.exception(log_content)

    return flag_success, result_ip_dns


def get_hostname_detail(hostname, type_records):
    """
    Get the record ID and record of hostname
    """

    logger.info("Current hostname: {0:-^80}".format(hostname))

    # Initial Hostnames result
    result_hostname = dict()
    result_hostname["hostname"] = hostname

    # Initial success flag
    flag_success = False

    # URL of list records
    url_record_list = "https://api.cloudflare.com/client/v4/zones/{:}/dns_records?name={:}".format(zone_id, hostname)
    # Get all records of this hostname
    try:
        result_request = requests.request(method="GET", url=url_record_list, headers=header_record, proxies=proxies_set, timeout=5).json()["result"]
        result_request_json = json.dumps(result_request, indent=4, ensure_ascii=False)
        log_content = "Request result is: {:}".format(result_request_json)
        logger.info(log_content)
        # Save all records content and id to dict
        for result_record in result_request:
            record_type_tmp = result_record["type"]
            if record_type_tmp in type_records:
                key_content = "content_{:}".format(record_type_tmp)
                result_hostname[key_content] = result_record["content"]
                key_record_id = "record_id_{:}".format(record_type_tmp)
                result_hostname[key_record_id] = result_record["id"]
                key_ttl = "ttl_{:}".format(record_type_tmp)
                result_hostname[key_ttl] = result_record["ttl"]
        # Log hostname detail
        result_hostnames_json = json.dumps(result_hostname, indent=4, ensure_ascii=False)
        log_content = "Hostname detail is: {:}".format(result_hostnames_json)
        logger.info(log_content)
        # Set success flag to True
        flag_success = True
    except Exception as exception:
        log_content = "Error occured when get details of {:}: {:}.".format(hostname, exception)
        logger.error(log_content)
        # logger.exception(log_content)

    return flag_success, result_hostname


def log_generator(hostname, ip_cur, ip_dns, type_record, ttl_config, ttl_cur, result_update):
    """
    Generate log.
    Input: Hostname, current ip, DNS ip, update result
    Return: Hostname: {{hostname}}, record type: {{type_record}}, current IP: {{ip_cur}}, DNS IP: {{ip_dns}}, update result: {{result_update}}
    """
    result_update = json.dumps(result_update, indent=4, ensure_ascii=False)
    # Define log tamplate
    log_content = "Hostname: {:}, record type: {:}, current IP: {:}, DNS IP: {:}, configured ttl: {:}, current ttl: {:}, update result: {:} ".format(
        hostname, type_record, ip_cur, ip_dns, ttl_config, ttl_cur, result_update)

    return log_content


def dns_update_step(hostname, result_ip_cur, config_hostname):
    """
    Update DNS record.
    Input: IP information, current ip
    Return: result_update
    """

    # Get type of records
    type_records = config_hostname["records"].split(",")

    # Initial blank result_ip_cur_tmp
    result_ip_cur_tmp = ""

    # Log the hostname and IP
    flag_success, hostname_detail = get_hostname_detail(hostname, type_records)

    # Return failed at get hostname detail
    if flag_success == False:
        result_update = "Get detail of hostname {:} failed.".format(hostname)

        return result_update

    for type_record in type_records:
        key_content = "content_{:}".format(type_record)
        key_id = "record_id_{:}".format(type_record)
        key_ttl = "ttl_{:}".format(type_record)
        # Get config ttl if exist or set to "auto"
        if key_ttl in config_hostname.keys():
            ttl_config = eval(config_hostname[key_ttl])
        else:
            # Initial ttl to "auto"
            ttl_config = 1
        # Judge hostname type exist or not
        hostname_type = "hostname_{:}".format(type_record)
        if hostname_type in config_hostname.keys():
            log_content = "Using DNS mode of {:} : {:}".format(hostname, type_record)
            logger.info(log_content)

            # Get IP of hostname type record from DNS IP
            hostname_tmp = config_hostname[hostname_type]
            flag_success, result_ip_cur_tmp = get_dns_ip(hostname=hostname_tmp, type_record=type_record)
            # Return failed at get DNS IP
            if flag_success == False:
                result_update = "Get DNS IP of {:} : {:} failed.".format(hostname, type_record)

                return result_update
        else:
            # Get IP of type record from global IP
            key_cur = "cur_{:}".format(type_record)
            result_ip_cur_tmp = result_ip_cur[key_cur]
        if key_content not in hostname_detail.keys():
            log_content = "There are not such key: {:} of hostname: {:}.".format(key_content, hostname)
            return log_content
        # Judge the IP and ttl were changed or not
        if (result_ip_cur_tmp != hostname_detail[key_content]) or (ttl_config != hostname_detail[key_ttl]):
            # If changed, update DNS record
            logger.info("Updating DNS records of {:} : {:}...".format(hostname, type_record))
            data_record_update = {
                "name": hostname,
                "type": type_record,
                "content": result_ip_cur_tmp,
                "ttl": ttl_config,
                "proxied": False
            }
            # Update DNS record with HTTP POST
            url_record_update = "https://api.cloudflare.com/client/v4/zones/{:}/dns_records/{:}".format(zone_id, hostname_detail[key_id])
            try:
                result_update = requests.request(method="PUT", url=url_record_update, headers=header_record, json=data_record_update, proxies=proxies_set, timeout=5).json()
            except Exception as exception:
                result_update = {
                    "result": "Error occured when update: {:}".format(exception)
                }
        else:
            # Log no need update
            result_update = {
                "result": "No need update."
            }
        # Log result
        log_content = log_generator(hostname=hostname, type_record=type_record, ip_cur=result_ip_cur_tmp,
                                    ip_dns=hostname_detail[key_content], ttl_config=ttl_config, ttl_cur=hostname_detail[key_ttl], result_update=result_update)
        logger.info(log_content)

    # Return success of
    result_update = "Update of hostname: {:} success.".format(hostname)

    return result_update


def testing():
    """
    Write your testing function here
    """
    pass


if __name__ == "__main__":

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
        logger.info(result_update)

    # Log script end
    log_content = "{0:=^100}\n".format(" DDNS script End ")
    logger.info(log_content)
