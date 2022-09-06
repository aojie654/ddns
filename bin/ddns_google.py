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
filename_log = "ddns_google.log"
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
filename_config = "google.ini"
path_config_dir = path_root.joinpath("configs")
path_config = path_config_dir.joinpath(filename_config)
log_content = "Config path is: {0}".format(path_config)
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
    url_ip4 = "https://v4.ipv6-test.com/api/myip.php"
# URL to get IPv6 address
url_key = "url_ip6"
if url_key in config_default.keys():
    url_ip6 = config_default[url_key]
else:
    url_ip6 = "https://v6.ipv6-test.com/api/myip.php"

# Initial proxy result
proxies_set = dict()
# Load Proxy if exist
if "proxy_http" in config_default.keys():
    proxies_set["http"] = config_default["proxy_http"]
if "proxy_https" in config_default.keys():
    proxies_set["https"] = config_default["proxy_https"]
log_content = "Proxy is: {0}".format(proxies_set)
logger.info(log_content)


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
        logger.exception("Error occured when get global IPv4, using 127.0.0.1 to global IP: {0}".format(exception_tmp))
        # logger.exception("Error occured when get global IPv4, using 127.0.0.1 to global IP.", exc_info=exception_tmp)
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
        logger.exception("Error occured when get global IPv6, using ::1 to global IP: {0}".format(exception_tmp))
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
            log_content = "DNS IP of hostname: {0} : {1} is {2}".format(hostname, type_record, result_ip_dns)
        else:
            log_content = "No record of hostname: {0} : {1} at DNS.".format(hostname, type_record)
        logger.info(log_content)
        # Set success flag to True
        flag_success = True
    except Exception as exception_tmp:
        logger.exception("Error occured when get DNS IP of hostname: {0} : {1}".format(hostname, type_record), exc_info=exception_tmp)

    return flag_success, result_ip_dns


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
    result_ip_dns = ""

    for type_record in type_records:
        # Judge hostname type exist or not
        hostname_type = "hostname_{0}".format(type_record)
        if hostname_type in config_hostname.keys():
            log_content = "Using DNS mode of {0} : {1}".format(hostname, type_record)
            logger.info(log_content)
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
        # Get record IP at DNS
        flag_success, result_ip_dns = get_dns_ip(hostname=hostname, type_record=type_record)
        # Return failed at get DNS IP
        if flag_success == False:
            result_update = "Get DNS IP of {0} : {1} failed.".format(hostname, type_record)

            return result_update
        else:
            log_content = "{0} : {1} at DNS is: {2}".format(hostname, type_record, result_ip_dns)
            logger.info(log_content)
        if result_ip_cur_tmp != result_ip_dns:
            # If changed, update DNS record
            logger.info("Updating DNS records of {0} : {1}...".format(hostname, type_record))

            # Get usrename and password
            key_username = "username_{0}".format(type_record)
            key_password = "password_{0}".format(type_record)
            username = config_hostname[key_username]
            password = config_hostname[key_password]

            # Initial data using to post
            data_record_update = {
                "hostname": hostname,
                "myip": result_ip_cur_tmp
            }

            # Update DNS record with HTTP POST
            url_record_update = "https://{0}:{1}@domains.google.com/nic/update".format(username, password)
            try:
                result_update = requests.request(method="POST", url=url_record_update, data=data_record_update, proxies=proxies_set, timeout=5).text
            except Exception as exception_tmp:
                result_update = "Error occured when update: {0}".format(exception_tmp)
        else:
            # Log no need update
            result_update = "No need update."
        # Log result
        log_content = log_generator(hostname=hostname, type_record=type_record, ip_cur=result_ip_cur_tmp, ip_dns=result_ip_dns, result_update=result_update)
        logger.info(log_content)

    # Return success of
    result_update = "Update of hostname: {0} success.".format(hostname)

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
