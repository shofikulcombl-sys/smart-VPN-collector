import urllib.request
import re
import base64
import json
import socket
import time

def discover_new_sources():
    """১. সারা ইন্টারনেট থেকে নতুন ভিপিএন সোর্স স্বয়ংক্রিয়ভাবে খোঁজা"""
    discovered_urls = []
    # গিটহাবের আসল অনুসন্ধান API (যা ভ্যালিড JSON রেসপন্স দেয়)
    search_api_url = "https://api.github.com/search/repositories?q=v2ray+config+stars:>10&sort=updated"
    
    try:
        req = urllib.request.Request(search_api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            for item in data.get('items', []):
                # সঠিক র-ডাউনলোড লিংক ফরম্যাট তৈরি করা
                raw_url = f"https://raw.githubusercontent.com/{item['full_name']}/main/README.md"
                discovered_urls.append(raw_url)
    except:
        pass
    
    # সোর্স লিংকগুলোর ডাবল স্ল্যাশ (https://://) এরর সম্পূর্ণ ফিক্স করা হলো
    discovered_urls.extend([
        "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Config_base64_Sub.txt",
        "https://raw.githubusercontent.com/MatinGhanbari/v2ray-configs/main/subscriptions/v2ray/all_sub.txt"
    ])
    return list(set(discovered_urls))

def test_server_latency(ip_or_domain, port):
    """২. রিয়েল-টাইম মিলি-সেকেন্ড (ms) পিং টেস্ট করার লজিক"""
    try:
        port = int(port)
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.5)
        sock.connect((ip_or_domain, port))
        sock.close()
        latency = int((time.time() - start_time) * 1000)
        return latency
    except:
        return None

def get_premium_server_details(ip_or_domain, port, protocol):
    """৩. লাইভ টুলস ব্যবহার করে ডাটা সেন্টার, লোকেশন এবং পিং হিসাব করা"""
    latency = test_server_latency(ip_or_domain, port)
    if latency is None:
        return None

    if latency < 150:
        speed_tag = f"🟢 {latency}ms [🟢 ULTRA-FAST]"
    elif latency < 300:
        speed_tag = f"🟡 {latency}ms [🟡 MEDIUM-SPEED]"
    else:
        speed_tag = f"🔴 {latency}ms [🔴 SLOW-SPEED]"

    try:
        # ip-api এর স্ল্যাশ এরর ফিক্স করা হয়েছে (com{ip} এর বদলে com/json/{ip})
        api_url = f"http://ip-api.com/json/{ip_or_domain}?fields=status,country,countryCode,city,isp"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=3) as response:
            ip_data = json.loads(response.read().decode('utf-8'))
            
            if ip_data.get('status') == 'success':
                country = ip_data.get('country', 'Global')
                code = ip_data.get('countryCode', 'UN').upper()
                city = ip_data.get('city', 'Anycast')
                isp_raw = ip_data.get('isp', 'Cloud-Compute')
                
                isp = isp_raw.split(',')[0].split(' ')[0].upper()
                if len(isp) > 12: isp = isp[:12]

                flag = "".join(chr(127397 + ord(c)) for c in code) if code != 'UN' else '🌐'
                
                benefit = "⚡ HIGH-SPEED DL"
                
                if code in ['SG', 'IN', 'HK', 'MY', 'TH']:
                    benefit = "🎮 GAMING / LOW-PING"
                elif code in ['US', 'GB', 'DE', 'JP', 'CA']:
                    benefit = "🎬 STREAMING & BYPASS"

                return f"{speed_tag} 🔸 {flag} {code}-{city} [{protocol.upper()}] 🔸 {isp} 🔸 {benefit}"
    except:
        pass
    return f"{speed_tag} 🔸 🌐 Global Node [{protocol.upper()}] 🔸 PREMIUM BACKBONE"

def smart_crawler():
    print("🔍 স্বয়ংক্রিয়ভাবে প্রিমিয়াম নোড অনুসন্ধান করা হচ্ছে...")
    all_sources = discover_new_sources()
    print(f"🤖 মোট {len(all_sources)} টি সোর্স থেকে রিয়েল-টাইম ডাটা স্ক্যান করা হচ্ছে...")

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

    print(f"✅ মোট {len(collected_configs)} টি ইউনিক প্রিমিয়াম কোড সংগৃহীত হয়েছে।")
    
    final_processed_configs = []
    # টপ ১০০টি ফ্রেশ সার্ভার ফিল্টার করা হবে
    for config in collected_configs[:100]: 
        if "#" in config:
            base_part, _ = config.split("#", 1)
        else:
            base_part = config
            
        protocol_match = re.match(r'^([a-z0-9]+)://', base_part)
        protocol = protocol_match.group(1) if protocol_match else "vpn"

        # আইপি/ডোমেইন এবং পোর্ট প্রসেসিং
        server_match = re.search(r'@([^:]+):([0-9]+)', base_part)
        if server_match:
            ip_or_domain = server_match.group(1)
            port = server_match.group(2)
            
            premium_display = get_premium_server_details(ip_or_domain, port, protocol)
            
            if premium_display is None:
                continue
        else:
            continue
        
        new_config = f"{base_part}#{premium_display}"
        final_processed_configs.append(new_config)

    # v2rayNG বা অন্যান্য অ্যাপে ইমপোর্ট করার জন্য বেস৬৪ এনকোড করা হচ্ছে
    output_text = "\n".join(final_processed_configs)
    b64_output = base64.b64encode(output_text.encode('utf-8')).decode('utf-8')

    with open("subscription.txt", "w") as f:
        f.write(b64_output)
    print("📁 সফলভাবে রিয়েল পিং ও প্রিমিয়াম ফরম্যাটে subscription.txt ফাইলে সেভ করা হয়েছে।")

if __name__ == "__main__":
    smart_crawler()
