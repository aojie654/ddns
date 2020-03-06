# Using For DDNS Set Of Google Domains

# Define the timestamp
timestamp=$(date "+%Y-%m-%d %H:%M:%S.%3N %z")

# Define the hostname
hostname_g="www.example"

# Define the username and passwd
username_g="Your Username"
password_g="Your Passwd"

# Define the proxy of curl if you need or just set it to ""
curl_proxy="Curl Proxy"

# Get the current IP via whatismyip of akamai and ip of domain in DNS
ip_current=$(curl whatismyip.akamai.com)
ip_dns=$(dig ${hostname_g} @8.8.8.8 +short)

# Define the log name to 
filename_log="/tmp/ddns_${hostname_g}.log"

# Compare the current IP and IP of domain in DNS
if [ ${ip_current} = ${ip_dns} ];then
    # Using this to debug in case
    echo "No need to update for ${ip_current} equels ${ip_dns}"

    # Define the update_result that no need to update
    update_result="No need to update"
else
    # Using this to debug in case
    echo "Update current ip ${ip_current} with previous ip ${ip_dns} to hostname ${hostname_g}"

    # Define the reulst what returned
    update_result=$(curl -d "hostname=${hostname_g}&myip=${ip_current}" "https://${username_g}:${password_g}@domains.google.com/nic/update" -x ${curl_proxy})
    
    # Using this to debug in case
    echo ${update_result}
fi

# Add the update result to log
timestamp=$(date "+%Y-%m-%d %H:%M:%S.%3N %z")
echo "${timestamp} Hostname: ${hostname_g}, Current IP: ${ip_current}, IP in DNS: ${ip_dns}, Result: ${update_result}" >> ${filename_log}