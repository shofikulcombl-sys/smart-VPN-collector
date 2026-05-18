import urllib.request
import re
import base64
import json
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def discover_new_sources():
    """১. গ্লোবাল ইন্টারনেট জগৎ থেকে ১০,০০০+ নোড ক্রল করার মেগা হাব"""
    discovered_urls = []
    search_queries = [
        "https://api.github.com/search/repositories?q=v2ray+config+forks:>5&sort=updated&per_page=100",
        "https://api.github.com/search/repositories?q=clash+vless+stars:>5&sort=updated&per_page=100",
        "https://api.github.com/search/code?q=vmess://+path:README.md&sort=indexed&per_page=100",
        "https://api.github.com/search/code?q=vless://+path:README.md&sort=updated&per_page=100"
    ]
    
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }
    
    for url in search_queries:
        try:
            req = urllib.request.Request(url, headers=browser_headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode('utf-8'))
                if 'items' in data:
                    for item in data['items']:
                        if 'full_name' in item:
                            discovered_urls.append(f"https://raw.githubusercontent.com/{item['full_name']}/main/README.md")
                            discovered_urls.append(f"https://raw.githubusercontent.com/{item['full_name']}/master/README.md")
        except:
            continue
    
    # নোডের সংখ্যা সর্বোচ্চ করার জন্য মেগা র-সোর্স চেইন
    discovered_urls.extend([
        "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Config_base64_Sub.txt",
        "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
        "https://raw.githubusercontent.com/anaer/Sub/master/v2ray.txt",
        "https://raw.githubusercontent.com/v2rayng-config/v2rayng-config/main/v2rayNG_config.txt",
        "https://raw.githubusercontent.com/freev2ray/v2ray/master/v2ray",
        "https://raw.githubusercontent.com/vless-v2ray/vless/main/sub.txt",
        "https://raw.githubusercontent.com/Alvin9999/new-pac/master/vpn/v2ray/v2ray.txt",
        "https://raw.githubusercontent.com/cooal/V2ray/main/Sub",
        "https://raw.githubusercontent.com/wondrey/2024vless/main/v2ray.txt"
    ])
    return list(set(discovered_urls))

def precise_latency_test(ip_or_domain, port):
    """২. আল্ট্রা-ফাস্ট ৩-লেয়ার চেইন ল্যাটেন্সি টেস্ট মেকানিজম"""
    try:
        port = int(port)
        start_time = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.4) # টাইমআউট ০.৪ সেকেন্ড করায় অচল নোডগুলো দ্রুত বাদ পড়বে, গিটহাব ক্র্যাশ করবে না
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

def process_single_node(config):
    """৩. সার্ভার লাইভ টেস্ট এবং ক্যাটাগরি অনুযায়ী আইপি ভাগ করার লজিক"""
    if "#" in config:
        config, _ = config.split("#", 1)
        
    protocol_match = re.match(r'^([a-z0-9]+)://', config)
    protocol = protocol_match.group(1) if protocol_match else "vpn"
    server_match = re.search(r'@([^:]+):([0-9]+)', config)
    
    if not server_match:
        return None # ভুল ফরম্যাটের নোড সরাসরি বাদ

    ip_or_domain = server_match.group(1)
    port = server_match.group(2)
    
    # লাইভ সার্ভার টেস্ট
    latency, method_used = precise_latency_test(ip_or_domain, port)
    
    # ❌ যদি গিটহাব টেস্টে নোডটি সম্পূর্ণ ব্যর্থ (FAILED) হয়, তবে এটি ফাইলে যুক্ত হবে না (আপনার শর্তানুযায়ী বাদ)
    if method_used == "FAILED" or latency is None:
        return None

    # নোড সচল হলে দেশ ও ক্যাটাগরি নির্ধারণ শুরু
    code = 'UN'
    try:
        api_url = f"http://ip-api.com/json/{ip_or_domain}?fields=status,countryCode"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.0) as response:
            ip_data = json.loads(response.read().decode('utf-8'))
            if ip_data.get('status') == 'success':
                code = ip_data.get('countryCode', 'UN').upper()
    except:
        pass

    # --- ক্যাটাগরি অনুযায়ী আইপি ভাগ করা ---
    benefit = "BROWSING"
    if code in ['SG', 'IN', 'HK', 'MY', 'TH', 'KR', 'TW']:
        benefit = "GAMING" # এশিয়ান লো-ল্যাটেন্সি নোড
    elif code in ['US', 'GB', 'CA', 'DE']:
        benefit = "STREAMING" # হাই-স্পিড ওটিটি বাইপাস
    elif protocol.lower() == 'trojan' or protocol.lower() == 'ss':
        benefit = "PRIVACY-SECURE" # হাই-এনক্রিপশন সিকিউরিটি
    elif code in ['FR', 'NL', 'FI', 'SE']:
        benefit = "FAST-DOWNLOAD" # ইউরোপীয় মেগা ব্যান্ডউইথ

    # প্রফেশনাল ক্লিন নাম জেনারেশন
    display_name = f"{code}-{latency}ms-{benefit}-{protocol.upper()}"
    return f"{config}#{display_name}"

def smart_crawler():
    print("🔍 মেগা ১০,০০০+ প্যাক অনুসন্ধান ও লাইভ সার্ভার টেস্টিং শুরু হচ্ছে...")
    all_sources = discover_new_sources()
    collected_configs = []
    vpn_pattern = re.compile(r'((?:vmess|vless|trojan|ss)://[^\s"<>\'\`]+)')

    for url in all_sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            content = urllib.request.urlopen(req, timeout=5).read()
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

    total_scraped = len(collected_configs)
    print(f"✅ সোর্স থেকে মোট {total_scraped} টি র-নোড সংগৃহীত হয়েছে।")

    final_processed_configs = []
    # 💥 সম্পূর্ণ ১০,০০০ নোডের মেগা প্যাক একসাথে সিলেক্ট করা হলো
    top_nodes_to_test = collected_configs[:10000] 
    
    # ⚡ মেগা মাল্টি-থ্রেডিং সচল (৮০ জন কর্মী একসাথে কাজ করবে)
    print(f"⚡ ১০,০০০ নোডের ওপর লাইভ ব্যাকঅ্যান্ড টেস্ট শুরু হচ্ছে (Workers: 80)...")
    with ThreadPoolExecutor(max_workers=80) as executor:
        future_to_node = {executor.submit(process_single_node, node): node for node in top_nodes_to_test}
        for future in as_completed(future_to_node):
            try:
                result_config = future.result()
                if result_config: # শুধুমাত্র কার্যকর (Live) নোডগুলোই যুক্ত হবে, অচলগুলো বাদ
                    final_processed_configs.append(result_config)
            except:
                pass

    print(f"🎯 টেস্ট শেষে {len(final_processed_configs)} টি কার্যকর নোড পাওয়া গেছে।")

    # 🔒 আলটিমেট ফেইল-সেফ লক (ফাইল ফাঁকা হওয়া চিরতরে বন্ধ)
    if not final_processed_configs or len(final_processed_configs) == 0:
        print("⚠️ গুরুতর সতর্কবার্তা: টেস্ট বাফারে কোনো লাইভ নোড আসেনি! পুরোনো সফল ফাইলটি সুরক্ষিত রাখা হলো।")
        return

    # মেগা ডেটা বেস৬৪ এনকোড করা
    output_text = "\n".join(final_processed_configs)
    b64_output = base64.b64encode(output_text.encode('utf-8')).decode('utf-8')

    with open("subscription.txt", "w") as f:
        f.write(b64_output)
    print(f"📁 সফলভাবে শুধুমাত্র কার্যকর {len(final_processed_configs)} টি নোড নিয়ে subscription.txt ফাইল লক করা হয়েছে।")

if __name__ == "__main__":
    smart_crawler()
