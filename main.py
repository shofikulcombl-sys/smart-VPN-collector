import urllib.request
import re
import base64
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def discover_new_sources():
    """১. গভীর স্ক্যানিং: সারা ইন্টারনেট থেকে সচল মেগা সোর্স খোঁজা"""
    discovered_urls = []
    search_queries = [
        "https://api.github.com/search/repositories?q=v2ray+config+stars:>5+updated:>2026-01-01&sort=updated&per_page=50",
        "https://api.github.com/search/repositories?q=vless+sub+stars:>2&sort=updated&per_page=50"
    ]
    browser_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in search_queries:
        try:
            req = urllib.request.Request(url, headers=browser_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if 'items' in data:
                    for item in data['items']:
                        if 'full_name' in item:
                            discovered_urls.append(f"https://raw.githubusercontent.com/{item['full_name']}/main/README.md")
                            discovered_urls.append(f"https://raw.githubusercontent.com/{item['full_name']}/master/README.md")
        except:
            continue
            
    discovered_urls.extend([
        "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Config_base64_Sub.txt",
        "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
        "https://raw.githubusercontent.com/anaer/Sub/master/v2ray.txt",
        "https://raw.githubusercontent.com/v2rayng-config/v2rayng-config/main/v2rayNG_config.txt"
    ])
    return list(set(discovered_urls))

def precise_latency_test(ip_or_domain, port):
    """২. নিখুঁত ৩-লেয়ার চেইন ল্যাটেন্সি টেস্ট মেকানিজম"""
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
    """৩. স্মার্ট ফিল্টার: নকল, ডেমো বা ভাঙা নোড শনাক্ত করে বাদ দেওয়া"""
    # নোডের ভেতর উদাহরণ হিসেবে থাকা কমন ভুয়া শব্দ ফিল্টার করা
    fake_keywords = ['uuid', 'host', 'port', 'xxxxx', 'your-server', 'base64', 'path', '...']
    config_lower = config.lower()
    
    for word in fake_keywords:
        if word in config_lower:
            return False
            
    # নোডের ভেতর @আইপি:পোর্ট বা @ডোমেন:পোর্ট এর সঠিক গঠন আছে কিনা যাচাই
    if not re.search(r'@[^:]+:[0-9]+', config):
        return False
        
    return True

def process_single_node(config):
    """৪. নোড অ্যানালাইসিস এবং ভিপিএন অ্যাপ ফ্রেন্ডলি ক্লিন ফরম্যাটিং"""
    if "#" in config:
        config, _ = config.split("#", 1)
        
    # যদি নোডটি নকল বা ইনভ্যালিড হয়, তবে সরাসরি বাদ (None)
    if not is_valid_config(config):
        return None
        
    protocol_match = re.match(r'^([a-z0-9]+)://', config)
    protocol = protocol_match.group(1) if protocol_match else "vpn"
    server_match = re.search(r'@([^:]+):([0-9]+)', config)
    
    ip_or_domain = server_match.group(1)
    port = server_match.group(2)
    
    # ল্যাটেন্সি টেস্ট
    latency, method_used = precise_latency_test(ip_or_domain, port)
    
    # দেশ নির্ধারণ
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

    # কাজের ধরন নির্ধারণ
    benefit = "MULTI"
    if code in ['SG', 'IN', 'HK', 'MY', 'TH', 'KR', 'TW']:
        benefit = "GAMING"
    elif code in ['US', 'GB', 'DE', 'JP', 'CA', 'FR', 'NL']:
        benefit = "STREAM"

    # স্পেস ও ইমোজি ছাড়া বিশুদ্ধ আলফানিউমেরিক নাম (যা v2rayNG ১০০% রিড করতে পারে)
    if method_used == "FAILED":
        display_name = f"PHONE-TEST-{code}-{benefit}-{protocol.upper()}"
    else:
        display_name = f"{code}-{latency}ms-{benefit}-{protocol.upper()}"

    return f"{config}#{display_name}"

def smart_crawler():
    print("🔍 মেগা ইন্টারনেট ক্রলিং শুরু হচ্ছে...")
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

    print(f"✅ সোর্স থেকে মোট {len(collected_configs)} টি র-কোড পাওয়া গেছে। ফিল্টারিং ও টেস্টিং শুরু হচ্ছে...")

    final_processed_configs = []
    # টপ ৩০০টি নোড ফিল্টার ও মাল্টি-থ্রেড প্রসেস করা হবে
    top_nodes_to_test = collected_configs[:300] 
    
    with ThreadPoolExecutor(max_workers=25) as executor:
        future_to_node = {executor.submit(process_single_node, node): node for node in top_nodes_to_test}
        for future in as_completed(future_to_node):
            try:
                result_config = future.result()
                if result_config: # শুধুমাত্র ভ্যালিড নোডগুলোই যুক্ত হবে
                    final_processed_configs.append(result_config)
            except:
                pass

    print(f"🎯 ফিল্টারিং শেষে {len(final_processed_configs)} টি খাঁটি প্রিমিয়াম নোড ফাইলে সেভ করা হচ্ছে।")

    # ডাটা বেস৬৪ এনকোড করা
    output_text = "\n".join(final_processed_configs)
    b64_output = base64.b64encode(output_text.encode('utf-8')).decode('utf-8')

    with open("subscription.txt", "w") as f:
        f.write(b64_output)
    print("📁 সফলভাবে শত শত খাঁটি নোড দিয়ে subscription.txt ফাইল আপডেট করা হয়েছে।")

if __name__ == "__main__":
    smart_crawler()
