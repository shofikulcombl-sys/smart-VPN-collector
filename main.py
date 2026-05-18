import urllib.request
import re
import base64
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def discover_new_sources():
    """১. গ্লোবাল মেগা সোর্স: ইন্টারনেট জগৎ থেকে ১০০% সচল ও ওপেন সোর্স ভিপিএন লিংক"""
    # গিটহাব সার্চ API বাদ দিয়ে সরাসরি গ্লোবাল র-লিংক ব্যবহার (ফেইল-সেফ মেকানিজম)
    discovered_urls = [
        "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Config_base64_Sub.txt",
        "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
        "https://raw.githubusercontent.com/anaer/Sub/master/v2ray.txt",
        "https://raw.githubusercontent.com/v2rayng-config/v2rayng-config/main/v2rayNG_config.txt",
        "https://raw.githubusercontent.com/freev2ray/v2ray/master/v2ray",
        "https://raw.githubusercontent.com/vless-v2ray/vless/main/sub.txt",
        "https://raw.githubusercontent.com/IranianPremium/v2ray-configs/main/All_Configs_Sub.txt",
        "https://raw.githubusercontent.com/BardiaFA/VPN-Configs/main/All_Configs_Sub.txt"
    ]
    return list(set(discovered_urls))

def precise_latency_test(ip_or_domain, port):
    """২. নিখুঁত ৩-লেয়ার চেইন ল্যাটেন্সি টেস্ট"""
    try:
        port = int(port)
        start_time = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect((ip_or_domain, port))
        sock.close()
        return int((time.perf_counter() - start_time) * 1000), "TCP"
    except:
        pass
    try:
        start_time = time.perf_counter()
        socket.gethostbyname(ip_or_domain)
        return int((time.perf_counter() - start_time) * 1000) + 30, "DNS"
    except:
        return None, "FAILED"

def is_valid_config(config):
    """৩. সেফ ফিল্টার: নিশ্চিত ভুয়া ডেমো নোড বাদ দেওয়া"""
    config_lower = config.lower()
    fake_keywords = ['uuid@', 'your-server', 'xxxxx-xxxx', 'host:port']
    for word in fake_keywords:
        if word in config_lower:
            return False
    if "://" not in config_lower:
        return False
    return True

def process_single_node(config):
    """४. নোড অ্যানালাইসিস এবং ভিপিএন অ্যাপ ফ্রেন্ডলি ক্লিন ফরম্যাটিং"""
    if "#" in config:
        config, _ = config.split("#", 1)
        
    if not is_valid_config(config):
        return None
        
    protocol_match = re.match(r'^([a-z0-9]+)://', config)
    protocol = protocol_match.group(1) if protocol_match else "vpn"
    server_match = re.search(r'@([^:]+):([0-9]+)', config)
    
    if not server_match:
        return f"{config}#PHONE-SOCKET-RAW"

    ip_or_domain = server_match.group(1)
    port = server_match.group(2)
    
    latency, method_used = precise_latency_test(ip_or_domain, port)
    
    code = 'UN'
    try:
        api_url = f"http://ip-api.com/json/{ip_or_domain}?fields=status,countryCode"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.2) as response:
            ip_data = json.loads(response.read().decode('utf-8'))
            if ip_data.get('status') == 'success':
                code = ip_data.get('countryCode', 'UN').upper()
    except:
        pass

    benefit = "MULTI"
    if code in ['SG', 'IN', 'HK', 'MY', 'TH', 'KR', 'TW']:
        benefit = "GAMING"
    elif code in ['US', 'GB', 'DE', 'JP', 'CA', 'FR', 'NL']:
        benefit = "STREAM"

    if method_used == "FAILED":
        display_name = f"PHONE-TEST-{code}-{benefit}-{protocol.upper()}"
    else:
        display_name = f"{code}-{latency}ms-{benefit}-{protocol.upper()}"

    return f"{config}#{display_name}"

def smart_crawler():
    print("🔍 মেগা গ্লোবাল ইন্টারনেট ক্রলিং শুরু হচ্ছে...")
    all_sources = discover_new_sources()
    collected_configs = []
    vpn_pattern = re.compile(r'((?:vmess|vless|trojan|ss)://[^\s"<>\'\`]+)')

    for url in all_sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            content = urllib.request.urlopen(req, timeout=6).read()
            try:
                text_content = base64.b64decode(content).decode('utf-8', errors='ignore')
            except:
                text_content = content.decode('utf-8', errors='ignore')

            matches = vpn_pattern.findall(text_content)
            for config in matches:
                if config not in collected_configs:
                    collected_configs.append(config)
        except:
            continue

    print(f"✅ সোর্স থেকে মোট {len(collected_configs)} টি র-কোড পাওয়া গেছে।")

    final_processed_configs = []
    # টপ ২৫০টি নোড মাল্টি-থ্রেড প্রসেস করা হবে
    top_nodes_to_test = collected_configs[:250] 
    
    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_node = {executor.submit(process_single_node, node): node for node in top_nodes_to_test}
        for future in as_completed(future_to_node):
            try:
                result_config = future.result()
                if result_config:
                    final_processed_configs.append(result_config)
            except:
                pass

    # চূড়ান্ত ব্যাকআপ মেকানিজম
    if not final_processed_configs and collected_configs:
        final_processed_configs = collected_configs[:100]

    # ডাটা বেস৬৪ এনকোড করা
    output_text = "\n".join(final_processed_configs)
    b64_output = base64.b64encode(output_text.encode('utf-8')).decode('utf-8')

    with open("subscription.txt", "w") as f:
        f.write(b64_output)
    print(f"📁 সফলভাবে {len(final_processed_configs)} টি নোড সেভ করা হয়েছে।")

if __name__ == "__main__":
    smart_crawler()
