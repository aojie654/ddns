import os
import requests
import datetime
import dns.resolver
import logging
from datetime import datetime


# Log path
log_folder = "log"
# Create log folder if not exist
if not os.path.exists(log_folder):
    os.mkdir(log_folder)

log_filename = "ddns_google_{0:%Y%m%d}.log".format(datetime.now())
log_path = os.path.join(log_folder, log_filename)

# Set log format
logging.basicConfig(format="%(asctime)s; %(levelname)s; %(message)s", filename=log_path, level=logging.INFO)

# Proxy settings
proxies_set = {
    "http": "Your HTTP Proxy",
    "https": "Your HTTPS Proxy",
}

# Google Domains hostnames and credentials
update_lists = [
    {
        "hostname": "Your Google DDNS Hostname",
        "username": "Your Google DDNS Username",
        "password": "Your Google DDNS Password"
    },
]


def get_global_ip():
    """
    Get global ip.
    Input: None
    Return: Global IP
    """

    # URL to get IPv4 address
    url_ip4 = "https://v4.ipv6-test.com/api/myip.php"
    # Get current global IPv4
    # Use 1.1.1.1 as result IPv4 address for debug.
    # result_ip4_cur = "1.1.1.1"
    result_ip4_cur = requests.get(url_ip4).text.replace("\n", "")

    # URL to get IPv4 address
    # url_ip6 = "https://v6.ipv6-test.com/api/myip.php"
    # Get current global IPv6
    # Use fe80::1 as result IPv6 address for debug.
    # result_ip6_cur = "fe80::1"
    # result_ip6_cur = requests.get(url_ip6).text.replace("\n", "")

    # Change result here
    result_ip_cur = result_ip4_cur
    # result_ip_cur = result_ip6_cur

    # Log current IP
    log_content = "Current IP is: {0}".format(result_ip_cur)
    logging.info(log_content)

    return result_ip_cur


def get_dns_ip(hostname):
    """
    Get ip record at DNS.
    Input: None
    Return: DNS IP
    """

    # Initial DNS resolver
    resolver_tmp = dns.resolver.Resolver()
    resolver_tmp.nameservers = ["8.8.8.8", "8.8.4.4"]

    # IPv4 query
    result_ip4_dns = resolver_tmp.resolve(hostname, 'A').rrset[0].address

    # IPv6 query
    # result_ip6_dns = resolver_tmp.query(hostname, 'AAAA').rrset[0].address

    # Change the result here
    result_ip_dns = result_ip4_dns
    # result_ip_dns = result_ip6_dns

    # Log current IP
    if result_ip_dns != "":
        log_content = "DNS IP is: {0}".format(result_ip_dns)
    else:
        log_content = "No record at DNS."
    logging.info(log_content)

    return result_ip_dns


def log_generator(hostname, ip_cur, ip_dns, result_update):
    """
    Generate log.
    Input: Hostname, current ip, DNS ip, update result
    Return: Hostname: {{hostname}}, current IP: {{ip_cur}}, DNS IP: {{ip_dns}}, update result: {{result_update}}
    """
    
    # Define log tamplate
    log_content = "Hostname: " + hostname + ", current IP: " + ip_cur + \
        ", DNS IP: " + ip_dns + ", update result: " + result_update + "\n"

    return log_content


def dns_update_step(update_meta, result_ip_cur):
    """
    Update DNS record.
    Input: IP information, current ip
    Return: None
    """

    # Get username, password, hostname, current IP
    username = update_meta["username"]
    password = update_meta["password"]
    hostname = update_meta["hostname"]
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
            result_update = requests.post(url_update, data=data_post, proxies=proxies_set).text
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
    # Using your testing function here
    # testing()

    # Get current IP
    result_ip_cur = get_global_ip()
    log_content = "Current IP is: {0}".format(result_ip_cur)

    # Update each hostname in hostnames list
    for update_meta in update_lists:
        dns_update_step(update_meta, result_ip_cur)
    pass
