import os
import requests
import datetime
import dns.resolver


#log_folder = "D:\\tmp\\"
log_folder = "/var/log/ddns/"
log_filename = "ddns_google.log"
log_path = os.path.join(log_folder, log_filename)

if not os.path.exists(log_folder):
    os.mkdir(log_folder)

proxies_set = {
    "http": "Your HTTP Proxy",
    "https": "Your HTTPS Proxy",
}

update_lists = [
    {
        "hostname": "Your Google DDNS Hostname",
        "username": "Your Google DDNS Username",
        "password": "Your Google DDNS Password"
    },
]


def get_current_time():
    format_timestamp = "%Y/%m/%d %H:%M:%S.%f +08:00"
    result_timestamp = datetime.datetime.now().strftime(format_timestamp)

    return result_timestamp


def get_public_ip():
    url_ip = "http://whatismyip.akamai.com"
    
    # Use 1.1.1.1 as result IP for debug.
    # result_ip_cur = "1.1.1.1"
    result_ip_cur = requests.get(url_ip).text.replace("\n", "")

    return result_ip_cur


def get_dns_ip(hostname):
    resolver_tmp = dns.resolver.Resolver()
    resolver_tmp.nameservers = ["8.8.8.8", "8.8.4.4"]
    result_ip_dns = resolver_tmp.query(hostname, 'A').rrset[0].address

    return result_ip_dns


def log_generator(hostname, ip_cur, ip_dns, result_update):
    # Get timestamp
    timestamp = get_current_time()

    # Set vars
    hostname = hostname
    ip_cur = ip_cur
    ip_dns = ip_dns
    result_update = result_update

    # Define log tamplate
    log_content = timestamp + ", hostname: " + hostname + ", current IP: " + ip_cur + \
        ", DNS IP: " + ip_dns + ", update result: " + result_update + "\n"

    log_object = open(log_path, mode="a+t", encoding="utf-8")
    log_object.write(log_content)
    log_object.close()
    # print(log_content)


def dns_update_step(update_meta, result_ip_cur):
    # print(update_meta["hostname"], update_meta["username"],
    #       update_meta["password"])

    username = update_meta["username"]
    password = update_meta["password"]
    hostname = update_meta["hostname"]
    ip_cur = result_ip_cur

    data_post = {
        "hostname": hostname,
        "myip": ip_cur
    }

    print("Current hostname: " + hostname)

    print("Getting DNS IP: ", end="")
    ip_dns = get_dns_ip(hostname)
    print(ip_dns)

    if (ip_cur != ip_dns):
        print("Updating DNS records: ", end="") 
        result_update = requests.post("https://" + username + ":" + password + "@domains.google.com/nic/update",
                                      data=data_post, proxies=proxies_set).text
    else:
        result_update = "No need update."
    print(result_update)
    log_generator(hostname, ip_cur, ip_dns, result_update)


def testing():
    pass


if __name__ == "__main__":
    # testing()

    print("Getting public IP: ", end="")
    result_ip_cur = get_public_ip()
    print(result_ip_cur)

    for update_meta in update_lists:
        dns_update_step(update_meta, result_ip_cur)
    pass
