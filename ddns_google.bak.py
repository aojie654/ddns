# encoding = utf-8

import configparser
from contextlib import ExitStack
import datetime
import logging
import json
import os
from datetime import datetime

import dns.resolver
import requests

# Root path
path_root = os.path.dirname(__file__)

# Log Path in path_root/log/
path_log_dir = os.path.join(path_root, "log")
filename_log = "ddns_google_{0:%Y%m%d}.log".format(datetime.now())
path_log = os.path.join(path_log_dir, filename_log)

# Create log folder if not exist
if not os.path.exists(path_log_dir):
    os.mkdir(path_log_dir)

# Set log format
logging.basicConfig(format="%(asctime)s; %(levelname)s; %(message)s", filename=path_log, level=logging.INFO)

# Config path is path_root/.config
filename_config = "google.ini"
path_config_dir = os.path.join(path_root, "configs")
path_config = os.path.join(path_config_dir, filename_config)
log_content = "Config path is: {0}".format(path_config)
logging.info(log_content)

# Load config
config = configparser.ConfigParser()
config.read(path_config)
config_default = config["DEFAULT"]

# Load Proxy
proxies_set = {
    "http": config_default["http"],
    "https": config_default["https"],
}
log_content = "Proxy is: {0}".format(proxies_set)
logging.info(log_content)


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
    except Exception as e:
        result_ip4_cur = "127.0.0.1"
        logging.error("Error occured when get global IPv4, using 127.0.0.1 to global IP", exc_info=e)
    # result_ip4_cur = get_dns_ip(hostname=hostname, type_record="A")
    # Use 127.0.0.1 as result IPv4 address for debug.
    # result_ip4_cur = "127.0.0.1"

    # Get current global IPv6
    # URL to get IPv6 address
    url_ip6 = "https://v6.ipv6-test.com/api/myip.php"
    try:
        result_ip6_cur = requests.get(url_ip6, timeout=5).text.replace("\n", "")
    except Exception as e:
        result_ip6_cur = "::1"
        logging.error("Error occured when get global IPv6, using ::1 to global IP. ", exc_info=e)
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
    except Exception as e:
        logging.error("Error occured when get DNS IP of hostname: {0} : {1}".format(hostname, type_record), exc_info=e)

    return flag_success, result_ip_dns


def log_generator(hostname, ip_cur, ip_dns, result_update):
    """
    Generate log.
    Input: Hostname, current ip, DNS ip, update result
    Return: Hostname: {{hostname}}, current IP: {{ip_cur}}, DNS IP: {{ip_dns}}, update result: {{result_update}}
    """

    # Define log tamplate
    log_content = "Hostname: " + hostname + ", current IP: " + ip_cur + \
        ", DNS IP: " + ip_dns + ", update result: " + result_update

    return log_content


def dns_update_step(hostname_tmp, result_ip_cur):
    """
    Update DNS record.
    Input: IP information, current ip
    Return: None
    """

    # Get username, password, hostname, current IP
    hostname = hostname_tmp
    username = config[hostname_tmp]["username"]
    password = config[hostname_tmp]["password"]
    ip_cur = result_ip_cur

    # Initial data using to post
    data_post = {
        "hostname": hostname,
        "myip": ip_cur
    }

    # Log the hostname and IP
    logging.info("Current hostname: {0}".format(hostname))
    ip_dns = get_dns_ip(hostname)
    logging.info("Getting DNS IP...".format(ip_dns))

    # Judge the IP was changed or not
    if (ip_cur != ip_dns):
        # If changed, update DNS record
        logging.info("Updating DNS records...")
        try:
            # Update DNS record with HTTP POST
            url_update = "https://{0}:{1}@domains.google.com/nic/update".format(username, password)
            result_update = requests.request(method="POST", url=url_update, data=data_post, proxies=proxies_set, timeout=5).text
        except Exception as exception_tmp:
            result_update = "Error occured: {0}".format(exception_tmp)
    else:
        # Log no need update
        result_update = "No need update."
    # Log result
    log_content = log_generator(hostname, ip_cur, ip_dns, result_update)
    logging.info(log_content)

    return


def testing():
    """
    Write your testing function here
    """
    pass


if __name__ == "__main__":

    # Log script start
    log_content = "{0:=^50}".format(" DDNS script start ")
    logging.info(log_content)
    # Using your testing function here
    # testing()

    # Get current IP
    result_ip_cur = get_global_ip()
    log_content = "Current IP is: {0}".format(result_ip_cur)

    # Update each hostname in hostnames list
    for section_tmp in config.sections():
        dns_update_step(section_tmp, result_ip_cur)
    pass

    # Log script end
    log_content = "{0:=^50}\n".format(" DDNS script End ")
    logging.info(log_content)
