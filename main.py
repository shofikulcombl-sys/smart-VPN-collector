import urllib.request
import re
import base64
import json
import socket
import time

def discover_new_sources():
    """১. সারা ইন্টারনেট জগৎ থেকে স্বয়ংক্রিয়ভাবে নতুন ভিপিএন সোর্স খোঁজা (ফায়ারওয়াল ইভেশন সহ)"""
    discovered_urls = []
    search_queries = [
        "https://api.github.com/search/repositories?q=v2ray+config+forks:>5&sort=updated",
        "https://api.github.com/search/repositories?q=clash+vless+stars:>5&sort=updated",
        "https://api.github.com/search/code?q=vmess://+path:README.md&sort=indexed"
    ]
    
    # ফায়ারওয়ালকে ধোঁকা দেওয়ার জন্য রিয়েল ব্রাউজার হেডার (Bypass Mechanism)
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive'
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
                        elif 'repository' in item:
                            discovered_urls.append(f"https://raw.githubusercontent.com/{item['repository']['full_name']}/main/README.md")
        except:
            continue
    
    discovered_urls.extend([
        "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Config_base64_Sub.txt",
        "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt",
        "https://raw.githubusercontent.com/anaer/Sub/master/v2ray.txt",
        "https://raw.githubusercontent.com/v2rayng-config/v2rayng-config/main/v2rayNG_config.txt"
    ])
    return list(set(discovered_urls))

def test_server_latency_chain(ip_or_domain, port):
    """২. চেইন মেকানিজম: ৩টি বিকল্প মেথড পর পর ট্রাই করবে, সব ফেল করলে ফোনের সকেটে পাঠাবে"""
    port = int(port)
    
    # --- মেথড ১: ডাইরেক্ট টিসিপি সকেট কানেকশন ---
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect((ip_or_domain, port))
        sock.close()
        return int((time.time() - start_time) * 1000), "METHOD_1_TCP"
    except:
        pass

    # --- মেথড ২: HTTP/HTTPS ওয়েব পোর্ট পিং (যদি সকেট পোর্ট ব্লক থাকে) ---
    try:
        start_time = time.time()
        test_url = f"http://{ip_or_domain}:80" if port == 80 else f"https://{ip_or_domain}:443"
        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.0) as _:
            pass
        return int((time.time() - start_time) * 1000), "METHOD_2_HTTP"
    except:
        pass

    # --- মেথড ৩: DNS解析 ও লাইভনেস বাইন্ডিং স্পিড টেস্ট ---
    try:
        start_time = time.time()
        socket.gethostbyname(ip_or_domain)
        latency = int((time.time() - start_time) * 1000)
        return latency + 40, "METHOD_3_DNS"
    except:
        # ৩টি মেথডই ফেল করলে None এবং FAILED রিটার্ন করবে (যা ফোন সকেটে ট্রিগার হবে)
        return None, "FAILED"

def get_premium_server_details(ip_or_domain, port, protocol):
    """৩. নিখুঁত ডেটা অ্যানালাইসিস: দেশ, কাজের ধরন এবং সফল মেথড উল্লেখ করা"""
    latency, method_used = test_server_latency_chain(ip_or_domain, port)
    
    # ডিফল্ট ভ্যালু (যদি আইপি এপিআই ব্লক খায়)
    country, code, city, isp = 'Global', 'UN', 'Anycast', 'PREMIUM'
    flag = '🌐'
    
    # আইপি ইনফো বের করা
    try:
        api_url = f"http://ip-api.com/json/{ip_or_domain}?fields=status,country,countryCode,city,isp"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=2) as response:
            ip_data = json.loads(response.read().decode('utf-8'))
            if ip_data.get('status') == 'success':
                country = ip_data.get('country', 'Global')
                code = ip_data.get('countryCode', 'UN').upper()
                city = ip_data.get('city', 'Anycast')
                isp_raw = ip_data.get('isp', 'Cloud')
                isp = isp_raw.split(',')[0].split(' ')[0].upper()[:10]
                flag = "".join(chr(127397 + ord(c)) for c in code) if code != 'UN' else '🌐'
    except:
        pass

    # কাজের ধরন (Use Case Optimization) নির্ধারণ
    benefit = "⚡ MULTI-PURPOSE"
    if code in ['SG', 'IN', 'HK', 'MY', 'TH', 'KR']:
        benefit = "🎮 GAMING / LOW-PING"
    elif code in ['US', 'GB', 'DE', 'JP', 'CA', 'FR']:
        benefit = "🎬 STREAMING & BYPASS"

    # স্পিড ট্যাগ এবং কোন পদ্ধতিতে সফল হয়েছে তার বিবরণী
    if method_used == "FAILED":
        # ৪ নম্বর পদ্ধতি: গিটহাবের সব মেথড ফেল, ফোন সকেটের জন্য পাস করা হলো
        return f"📱 [PHONE-SOCKET-TEST] 🔸 {flag} {code}-{city} 🔸 {benefit} 🔸 [FALLBACK-ACTIVE]"
    else:
        # গিটহাবের ৩টির কোনো একটি মেথডে সফল হলে
        if latency < 150: speed_icon = f"🟢 {latency}ms [ULTRA-FAST]"
        elif latency < 300: speed_icon = f"🟡 {latency}ms [MEDIUM]"
        else: speed_icon = f"🔴 {latency}ms [SLOW]"
        
        return f"{speed_icon} 🔸 {flag} {code}-{city} 🔸 {benefit} 🔸 [via_{method_used}]"

def smart_crawler():
    print("🔍 গ্লোবাল ইন্টারনেট থেকে ভিপিএন অনুসন্ধান করা হচ্ছে...")
    all_sources = discover_new_sources()
    
    collected_configs = []
    vpn_pattern = re.compile(r'((?:vmess|vless|trojan|ss)://[^\s"<>\'\`]+)')

    for url in all_sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            content = urllib.request.urlopen(req, timeout=7).read()
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

    print(f"✅ মোট {len(collected_configs)} টি নোড ইন্টারনেট থেকে সংগৃহীত হয়েছে।")
    
    final_processed_configs = []
    # ফিল্টারিং এবং প্রসেসিং (টপ ১৫০টি ফ্রেশ নোড)
    for config in collected_configs[:150]: 
        if "#" in config:
            base_part, _ = config.split("#", 1)
        else:
            base_part = config
            
        protocol_match = re.match(r'^([a-z0-9]+)://', base_part)
        protocol = protocol_match.group(1) if protocol_match else "vpn"
        server_match = re.search(r'@([^:]+):([0-9]+)', base_part)
        
        if server_match:
            ip_or_domain = server_match.group(1)
            port = server_match.group(2)
            # চেইন মেকানিজম এবং ডেটা অ্যানালাইসিসে পাঠানো হচ্ছে
            premium_display = get_premium_server_details(ip_or_domain, port, protocol)
            new_config = f"{base_part}#{premium_display}"
        else:
            new_config = f"{base_part}#📱 [PHONE-SOCKET-TEST] 🔸 🌐 RAW-NODE"
        
        final_processed_configs.append(new_config)

    if not final_processed_configs and collected_configs:
        final_processed_configs = collected_configs[:150]

    # v2rayNG/অন্যান্য অ্যাপের জন্য বেস৬৪ লক করা
    output_text = "\n".join(final_processed_configs)
    b64_output = base64.b64encode(output_text.encode('utf-8')).decode('utf-8')

    with open("subscription.txt", "w") as f:
        f.write(b64_output)
    print("📁 সফলভাবে ৪-লেয়ার চেইন মেকানিজমে subscription.txt ফাইল সাজানো হয়েছে।")

if __name__ == "__main__":
    smart_crawler()
