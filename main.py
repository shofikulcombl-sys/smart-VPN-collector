import urllib.request
import re
import base64
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def discover_new_sources():
    """১. সারা ইন্টারনেট থেকে নতুন ভিপিএন সোর্স খোঁজা"""
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
    """২. ৩-লেয়ার চেইন ল্যাটেন্সি টেস্ট মেকানিজম"""
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

def clean_and_format_config(config, flag, code, city, latency, method, protocol, benefit):
    """৩. ভ ভিপিএন নোডের ভেতরের নাম নিখুঁত প্রফেশনাল ফরম্যাটে সাজানো"""
    # পুরোনো বা অস্পষ্ট নাম মুছে ফেলার জন্য লিঙ্কের পেছনের অংশ পরিষ্কার করা
    if "#" in config:
        config, _ = config.split("#", 1)
        
    # সুন্দর ও স্পষ্ট নাম তৈরি
    if method == "FAILED":
        display_name = f"{flag} [{code}-{city}] 📱 PHONE-TEST 🔸 {benefit}"
    else:
        speed_icon = "🟢 ULTRA" if latency < 150 else ("🟡 MED" if latency < 250 else "🔴 SLOW")
        display_name = f"{flag} [{code}-{city}] ⚡ {latency}ms ({speed_icon}) 🔸 {benefit} [{protocol.upper()}]"
        
    # URL Encoding-এর জন্য স্পেস বা ক্যারেক্টার ক্লিন করা
    safe_name = urllib.parse.quote(display_name)
    return f"{config}#{safe_name}"

def process_single_node(config):
    """প্রতিটি নোড অ্যানালাইসিস করে দেশ ও কাজ স্পষ্ট করার লজিক"""
    if "#" in config:
        base_part, _ = config.split("#", 1)
    else:
        base_part = config
        
    protocol_match = re.match(r'^([a-z0-9]+)://', base_part)
    protocol = protocol_match.group(1) if protocol_match else "vpn"
    server_match = re.search(r'@([^:]+):([0-9]+)', base_part)
    
    if not server_match:
        return f"{base_part}#🌐 [RAW-NODE] 🔸 ⚡ MULTI-PURPOSE"

    ip_or_domain = server_match.group(1)
    port = server_match.group(2)
    
    latency, method_used = precise_latency_test(ip_or_domain, port)
    
    # IP থেকে দেশের কোড বের করা
    code, city, flag = 'UN', 'Anycast', '🌐'
    try:
        api_url = f"http://ip-api.com/json/{ip_or_domain}?fields=status,countryCode,city"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            ip_data = json.loads(response.read().decode('utf-8'))
            if ip_data.get('status') == 'success':
                code = ip_data.get('countryCode', 'UN').upper()
                city = ip_data.get('city', 'Anycast')
                flag = "".join(chr(127397 + ord(c)) for c in code) if code != 'UN' else '🌐'
    except:
        pass

    # কাজের ধরন ক্যাটাগরাইজ করা
    benefit = "⚡ MULTI"
    if code in ['SG', 'IN', 'HK', 'MY', 'TH', 'KR', 'TW']:
        benefit = "🎮 GAMING"
    elif code in ['US', 'GB', 'DE', 'JP', 'CA', 'FR', 'NL']:
        benefit = "🎬 STREAM"

    return clean_and_format_config(base_part, flag, code, city, latency, method_used, protocol, benefit)

def smart_crawler():
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

    final_processed_configs = []
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

    if not final_processed_configs and collected_configs:
        final_processed_configs = collected_configs[:100]

    output_text = "\n".join(final_processed_configs)
    b64_output = base64.b64encode(output_text.encode('utf-8')).decode('utf-8')

    with open("subscription.txt", "w") as f:
        f.write(b64_output)
    print("📁 সফলভাবে ক্লিনিং ও প্রফেশনাল ফরমেটে ফাইল আপডেট করা হয়েছে।")

if __name__ == "__main__":
    smart_crawler()
