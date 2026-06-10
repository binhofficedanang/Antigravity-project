import streamlit as st
import pandas as pd
import json
import csv
import os
import time
import sys
import io
import contextlib
import re

import importlib
import web_automation
importlib.reload(web_automation)
from web_automation import WebAutomation
from extract_buildings import OfficeDanangCrawler, save_to_csv

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Poster Bot Dashboard - Officedanang",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thêm CSS tùy biến để giao diện nhìn premium, hiện đại
st.markdown("""
<style>
    /* CSS Tùy biến Giao diện Premium */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e0e4ec;
        color: #1f77b4;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4 !important;
        color: white !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    .listing-card {
        background-color: #fafbfc;
        border: 1px solid #e1e4e8;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .stTextArea textarea {
        font-family: 'Monaco', 'Courier New', Courier, monospace;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .log-box {
        background-color: #0e1117;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 15px;
        border-radius: 5px;
        height: 300px;
        overflow-y: scroll;
    }
    /* Style rule to dim and blur disabled checkboxes */
    div[data-testid="stCheckbox"] > label[data-disabled="true"] {
        opacity: 0.55;
        filter: blur(0.4px) grayscale(30%);
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CÁC HÀM TIỆN ÍCH DỮ LIỆU & CẤU HÌNH
# -----------------------------------------------------------------------------

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BOT_DIR, "config.json")
DATA_FILE = os.path.join(BOT_DIR, "data.csv")
HISTORY_FILE = os.path.join(BOT_DIR, "posted_history.json")

# Định nghĩa các trang web được hỗ trợ - DỄ DÀNG MỞ RỘNG TRONG TƯƠNG LAI
SUPPORTED_SITES = {
    "raovat.net": {
        "name": "RaoVat.net",
        "fields": [
            {"key": "email", "label": "Email đăng ký", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "thuviennhadat.vn": {
        "name": "ThuVienNhaDat.vn",
        "fields": [
            {"key": "username", "label": "Tên đăng nhập (SĐT/Email)", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "muaban.net": {
        "name": "MuaBan.net",
        "fields": [
            {"key": "username", "label": "Số điện thoại", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "123nhadatviet.com": {
        "name": "123NhaDatViet.com",
        "fields": [
            {"key": "username", "label": "Tên đăng nhập (SĐT/Email)", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "nhadatviet247.net": {
        "name": "NhaDatViet247.net",
        "fields": [
            {"key": "username", "label": "Tên đăng nhập (SĐT/Email)", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "muabandanang.vn": {
        "name": "MuaBanDaNang.vn",
        "fields": [
            {"key": "username", "label": "Tên đăng nhập", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "phongtro123.com": {
        "name": "PhongTro123.com",
        "fields": [
            {"key": "username", "label": "Số điện thoại đăng nhập", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "thuephongtro.com": {
        "name": "ThuePhongTro.com",
        "fields": [
            {"key": "username", "label": "Số điện thoại đăng nhập", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "bds123.vn": {
        "name": "BDS123.vn",
        "fields": [
            {"key": "username", "label": "Số điện thoại đăng nhập", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "giaodichnhadat.vn": {
        "name": "GiaoDichNhaDat.vn",
        "fields": [
            {"key": "email", "label": "Email đăng nhập", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "thongtinnhadat.vn": {
        "name": "ThongTinNhaDat.vn",
        "fields": [
            {"key": "email", "label": "Email đăng nhập", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "dangtinbatdongsan.vn": {
        "name": "DangTinBatDongSan.vn",
        "fields": [
            {"key": "username", "label": "Tên đăng nhập", "type": "text"},
            {"key": "password", "label": "Mật khẩu", "type": "password"}
        ]
    },
    "luachonnhadat.vn": {
        "name": "LuaChonNhaDat.vn",
        "fields": [
            {"key": "username", "label": "Email liên hệ", "type": "text"}
        ]
    }
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f"Lỗi ghi cấu hình: {e}")
        return False

def load_listings():
    data = []
    if not os.path.exists(DATA_FILE):
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Phục hồi dấu xuống dòng trong nội dung từ định dạng \\n lưu trữ
                if 'content' in row and row['content']:
                    row['content'] = row['content'].replace('\\n', '\n')
                data.append(row)
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu data.csv: {e}")
    return data

def save_listings(listings):
    try:
        import copy
        listings_copy = copy.deepcopy(listings)
        for row in listings_copy:
            if 'content' in row and row['content']:
                row['content'] = row['content'].replace('\n', '\\n')
            if 'is_ai' not in row:
                row['is_ai'] = 'False'
        if not listings_copy:
            return True
            
        headers = []
        for row in listings_copy:
            for k in row.keys():
                if k not in headers:
                    headers.append(k)
                    
        with open(DATA_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(listings_copy)
        return True
    except Exception as e:
        st.error(f"Lỗi ghi dữ liệu data.csv: {e}")
        return False

def parse_usd_and_vnd(price_str, area_str):
    import re
    price_str = str(price_str).strip().lower()
    area_str = str(area_str).strip().lower()
    
    # Get area
    area_num = 100
    area_match = re.search(r'(\d+)', area_str)
    if area_match:
        area_num = int(area_match.group(1))
        
    usd_rate = 26200
    usd_val = 0.0
    vnd_val = 0
    
    if 'usd' in price_str or '$' in price_str or 'đô' in price_str:
        price_match = re.search(r'([\d\.,]+)', price_str)
        if price_match:
            usd_val = float(price_match.group(1).replace(',', '.'))
            vnd_val = int(usd_val * area_num * usd_rate)
    else:
        # VND
        price_digits = re.sub(r'[^\d]', '', price_str)
        if price_digits:
            vnd_val = int(price_digits)
            
    return usd_val, vnd_val

def load_posted_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_posted_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu lịch sử đăng bài: {e}")
        return False

def get_site_cooldown(site_key, history):
    import datetime
    valid_posts = []
    for p in history:
        if not isinstance(p, dict):
            continue
        if p.get("status") != "Thành công":
            continue
        channels = p.get("channels", "")
        if not channels:
            continue
        channel_list = [c.strip() for c in channels.split(",")]
        if site_key in channel_list:
            posted_at_str = p.get("posted_at")
            if posted_at_str:
                try:
                    dt = datetime.datetime.strptime(posted_at_str, "%Y-%m-%d %H:%M:%S")
                    valid_posts.append(dt)
                except Exception:
                    pass
    if not valid_posts:
        return False, ""
    valid_posts.sort(reverse=True)
    now = datetime.datetime.now()
    if site_key == "muaban.net":
        latest_post = valid_posts[0]
        cooldown_period = datetime.timedelta(days=15)
        elapsed = now - latest_post
        if elapsed < cooldown_period:
            remaining = cooldown_period - elapsed
            days = remaining.days
            hours = remaining.seconds // 3600
            mins = (remaining.seconds % 3600) // 60
            if days > 0:
                time_str = f"còn {days} ngày {hours} giờ"
            elif hours > 0:
                time_str = f"còn {hours} giờ {mins} phút"
            else:
                time_str = f"còn {mins} phút"
            return True, f"MuaBan.net (Chờ đếm ngược: {time_str} ⏳)"
    elif site_key in ["123nhadatviet.com", "nhadatviet247.net"]:
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_posts_count = sum(1 for dt in valid_posts if dt >= today_start)
        if today_posts_count >= 2:
            tomorrow = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time.min)
            time_until_reset = tomorrow - now
            hours = time_until_reset.seconds // 3600
            mins = (time_until_reset.seconds % 3600) // 60
            time_str = f"reset sau {hours}h{mins}m"
            site_display_name = "123NhaDatViet.com" if site_key == "123nhadatviet.com" else "NhaDatViet247.net"
            return True, f"{site_display_name} (Đạt giới hạn 2 tin/ngày, {time_str} ⏳)"
    return False, ""

def extract_building_name_from_title(title, district=""):
    import re
    # Clean brackets first
    name = re.sub(r'\[.*?\]', '', title, flags=re.DOTALL)
    # Remove emojis and other special characters
    name = re.sub(r'[^\w\s\/\-\,\.\:\(\)]', '', name)
    name = name.strip()
    
    # Try to extract after keywords
    keywords = [
        r'\btại tòa nhà chuyên nghiệp\b', r'\btại toà nhà chuyên nghiệp\b',
        r'\btại tòa nhà\b', r'\btại toà nhà\b', r'\btại\b',
        r'\bở tòa nhà chuyên nghiệp\b', r'\bở toà nhà chuyên nghiệp\b',
        r'\bở tòa nhà\b', r'\bở toà nhà\b', r'\bở\b',
        r'\btòa nhà chuyên nghiệp\b', r'\btoà nhà chuyên nghiệp\b',
        r'\btòa nhà\b', r'\btoà nhà\b'
    ]
    
    extracted = None
    for kw in keywords:
        match = list(re.finditer(kw, name, re.IGNORECASE))
        if match:
            last_match = match[-1]
            extracted = name[last_match.end():].strip()
            break
            
    if extracted:
        # Clean suffixes from the extracted part
        for sep in [r'\s*-\s*', r'\s*,\s*', r'\s+Quận\b', r'\s+Q\.', r'\bgiá tốt\b', r'\bgiá rẻ\b']:
            parts = re.split(sep, extracted, flags=re.IGNORECASE)
            if parts and parts[0].strip():
                extracted = parts[0].strip()
        
        # Split at district name
        if district:
            parts = re.split(re.escape(district), extracted, flags=re.IGNORECASE)
            if parts and parts[0].strip():
                extracted = parts[0].strip()
                
        # Clean up any leftover leading words like "chuyên nghiệp" if it was not caught by keyword
        if extracted.lower().startswith("chuyên nghiệp "):
            extracted = extracted[len("chuyên nghiệp "):].strip()
        elif extracted.lower().startswith("chuyên nghiệp nhất "):
            extracted = extracted[len("chuyên nghiệp nhất "):].strip()
            
        extracted = extracted.strip(" -,.")
        if len(extracted) >= 2 and len(extracted) <= 40:
            return extracted

    # Fallback to prefix-stripping method
    prefixes = [
        r'^cho thuê văn phòng \d+m2 tại tòa nhà',
        r'^cho thuê văn phòng \d+m2 tại',
        r'^văn phòng cho thuê \d+m2 tại tòa nhà',
        r'^văn phòng cho thuê \d+m2 tại',
        r'^cho thuê sàn văn phòng \d+m2 ở',
        r'^cho thuê sàn văn phòng \d+m2 tại',
        r'^cho thuê diện tích văn phòng \d+m2 tại',
        r'^cho thuê văn phòng trống \d+m2 cực đẹp ở tòa nhà',
        r'^cho thuê văn phòng trống \d+m2 cực đẹp ở',
        r'^cho thuê văn phòng trống \d+m2 tại tòa nhà',
        r'^văn phòng làm việc \d+m2 cho thuê tại',
        r'^cho thuê sàn văn phòng \d+m2 cực đẹp tòa',
        r'^văn phòng cho thuê \d+m2 tòa nhà chuyên nghiệp',
        r'^văn phòng cho thuê \d+m2 tòa nhà',
        r'^cho thuê văn phòng trống \d+m2 giá tốt tại tòa',
        r'^sàn văn phòng chuyên nghiệp \d+m2 cho thuê tại',
        r'^cho thuê văn phòng \d+m2 tòa nhà',
        r'^cho thuê văn phòng tại tòa nhà',
        r'^cho thuê văn phòng tại',
        r'^văn phòng cho thuê tại tòa nhà',
        r'^văn phòng cho thuê tại',
        r'^tòa nhà',
        r'^toà nhà',
    ]
    for pref in prefixes:
        match = re.search(pref, name, re.IGNORECASE)
        if match:
            name = name[match.end():].strip()
            break
            
    # Remove suffixes like " - Quận ...", " Q. ...", " - Q. ...", " - Giá tốt", etc.
    name = re.split(r'\s*-\s*Quận', name, flags=re.IGNORECASE)[0]
    name = re.split(r'\s*-\s*Q\.', name, flags=re.IGNORECASE)[0]
    name = re.split(r'\s+Q\.', name, flags=re.IGNORECASE)[0]
    name = re.split(r'\s+Quận', name, flags=re.IGNORECASE)[0]
    name = re.split(r'\s*-\s*giá', name, flags=re.IGNORECASE)[0]
    name = re.split(r'\s*\(', name)[0] # remove (giá tốt...), (Mới...)
    
    if district:
        name = re.split(re.escape(district), name, flags=re.IGNORECASE)[0]
        
    # Remove trailing/leading punctuation/spaces
    name = name.strip(" -,.")
    return name

def normalize_string(s):
    import unicodedata
    s = s.lower().strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    s = s.replace('đ', 'd')
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def is_already_posted(title, area, source_url, posted_history):
    match = re.search(r'/property/([^/]+)', source_url)
    slug = match.group(1) if match else ""
    slug_clean = slug.replace("toa-nha-", "")
    if not slug_clean:
        return False
        
    for hist_item in posted_history:
        if isinstance(hist_item, dict):
            if hist_item.get("status") == "Thất bại":
                continue
            hist_url = hist_item.get("source_url", "")
            hist_match = re.search(r'/property/([^/]+)', hist_url)
            hist_slug = hist_match.group(1) if hist_match else ""
            hist_slug_clean = hist_slug.replace("toa-nha-", "")
            
            if hist_slug_clean == slug_clean:
                return True
        else:
            hist_str = str(hist_item).lower()
            slug_spaced = slug_clean.replace("-", " ")
            if (slug_spaced in hist_str or 
                slug_clean in hist_str or 
                normalize_string(slug_clean) in normalize_string(hist_str)):
                return True
    return False

# -----------------------------------------------------------------------------
# LỚP BẮT LUỒNG LOGS (STDOUT REDIRECTOR)
# -----------------------------------------------------------------------------

class StreamlitLogRedirector(io.StringIO):
    def __init__(self, text_placeholder):
        super().__init__()
        self.placeholder = text_placeholder
        self.log_content = ""

    def write(self, string):
        if string:
            self.log_content += string
            # Hiển thị log dạng code terminal màu xanh lá cây
            self.placeholder.code(self.log_content, language="bash")
        return len(string)

    def flush(self):
        pass

# -----------------------------------------------------------------------------
# CẤU HÌNH POPUP XEM SCREENSHOT (DLG & UTILS)
# -----------------------------------------------------------------------------

@st.dialog("Ảnh chụp màn hình kết quả")
def show_screenshot_dialog(title, image_paths):
    st.write(f"### {title}")
    for path in image_paths:
        st.write(f"**📷 {os.path.basename(path)}**")
        st.image(path, use_container_width=True)

def get_recent_screenshots(site_keys, max_age_secs=600):
    """Tìm các screenshot liên quan đến site_keys được cập nhật gần đây (max_age_secs)."""
    import glob
    import time
    
    screenshots = []
    if not site_keys:
        return screenshots
        
    now = time.time()
    # Danh sách tất cả file png trong thư mục làm việc
    png_files = glob.glob(os.path.join(BOT_DIR, "*.png"))
    
    for f in png_files:
        filename = os.path.basename(f)
        # Kiểm tra xem file có chứa từ khóa của bất kỳ site nào không
        for key in site_keys:
            clean_key = key.replace(".vn", "").replace(".com.vn", "").replace(".com", "").replace(".net", "").replace(".", "_")
            if clean_key in filename.lower():
                try:
                    mtime = os.path.getmtime(f)
                    if now - mtime <= max_age_secs:
                        screenshots.append((f, mtime))
                except OSError:
                    pass
                break
                
    screenshots.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in screenshots]

# -----------------------------------------------------------------------------
# CÁC HÀM HỖ TRỢ ĐĂNG TIN LAI (HYBRID SELECTOR & AI-REPAIR UI)
# -----------------------------------------------------------------------------

def run_ai_repair_ui(site_name, headless=False):
    """Gọi ai_selector_generator.py bằng subprocess để tự động sửa/cập nhật selectors bằng AI."""
    import subprocess
    import sys
    
    python_path = sys.executable
    cmd = [python_path, "ai_selector_generator.py", "--site", site_name]
    if headless:
        cmd.append("--headless")
        
    print(f"⚙️ [AI-REPAIR] Đang chạy lệnh: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(res.stdout)
        return "AI đã phân tích và trích xuất thành công" in res.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy AI Selector Generator: {e.stderr or e.stdout}")
        return False

def execute_channel_posting_ui(site_name, account, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_callback):
    """Thực thi luồng đăng tin cho một trang: Thử Hybrid -> Sửa AI (nếu có cờ) -> Chạy Fallback."""
    if not account:
        print(f"Bỏ qua {site_name} (chưa cấu hình tài khoản)")
        return False
        
    print(f"\n--- [ {site_name.upper()} ] ---")
    
    # 1. Thử chạy bằng Hybrid Selector Runner
    success = bot.post_by_selectors(site_name, account, target_item, dry_run=run_dry_run)
    if success:
        return True
        
    # 2. Nếu thất bại, thử chạy AI-Repair nếu được cấp cờ
    if run_ai_repair:
        print(f"🤖 [AI-REPAIR] Đăng tin bằng Hybrid Selector thất bại. Đang gọi AI Selector Generator...")
        repair_ok = run_ai_repair_ui(site_name, run_headless)
        if repair_ok:
            # Thử chạy lại bằng Hybrid Selector sau khi đã cập nhật selectors
            print(f"🔄 [AI-REPAIR] Thử chạy lại Hybrid Selector sau khi đã cập nhật selectors...")
            success = bot.post_by_selectors(site_name, account, target_item, dry_run=run_dry_run)
            if success:
                return True
                
    # 3. Chạy bằng Fallback code cứng
    print(f"⚠️ Fallback về code cứng cho {site_name}...")
    try:
        return fallback_callback()
    except Exception as e:
        print(f"❌ Lỗi khi chạy fallback cho {site_name}: {e}")
        return False


# -----------------------------------------------------------------------------
# GIAO DIỆN CHÍNH
# -----------------------------------------------------------------------------

st.title("🏢 Hệ thống Đăng tin Bất động sản Tự động (Offline)")
st.caption("Quản lý thông tin văn phòng trống, tự động xào diện tích, tự động đăng tin đa kênh - 0 Token LLM!")

# Tải cấu hình và dữ liệu
config = load_config()
all_listings = load_listings()
posted_history = load_posted_history()

# Phân loại bài viết
pending_listings = []
completed_listings = []

for item in all_listings:
    if is_already_posted(item.get("title", ""), item.get("area", ""), item.get("source_url", ""), posted_history):
        completed_listings.append(item)
    else:
        pending_listings.append(item)

# -----------------------------------------------------------------------------
# SIDEBAR - THỐNG KÊ RÚT GỌN
# -----------------------------------------------------------------------------

with st.sidebar:
    st.header("🏢 Poster Bot Dashboard")
    st.caption("Hệ thống tự động hóa đăng tin văn phòng cho thuê Đà Nẵng")
    st.markdown("---")
    
    st.subheader("📊 Số liệu Thống kê")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric(label="Chờ đăng", value=len(pending_listings))
    with col_sb2:
        st.metric(label="Đã đăng", value=len(completed_listings))
        
    st.markdown("---")
    st.info("""
    💡 **Hướng dẫn nhanh**:
    1. Thiết lập tài khoản tại Tab **Hệ thống**.
    2. Cào bài mới tại Tab **Cào & Xào bài**.
    3. Biên tập & Đăng tin hoặc Hẹn giờ đăng tại Tab **Biên tập**.
    """)

# -----------------------------------------------------------------------------
# PHẦN NỘI DUNG TABS CHÍNH
# -----------------------------------------------------------------------------

tab_post, tab_spin, tab_schedule, tab_renew, tab_watermark, tab_accounts, tab_history = st.tabs([
    "📋 Biên tập & Đăng tin", 
    "🌪️ Máy Cào & Xào bài", 
    "📅 Lịch trình & Hẹn giờ",
    "🔄 Tự động Up Tin",
    "🎨 Cấu hình Watermark",
    "⚙️ Hệ thống & Tài khoản",
    "📜 Lịch sử chạy Bot"
])

# =============================================================================
# TAB 1: BIÊN TẬP & ĐĂNG TIN
# =============================================================================
with tab_post:
    if not pending_listings:
        st.success("🎉 Tuyệt vời! Toàn bộ các tin đăng đã được đăng hoàn tất. Hãy quét thêm tòa nhà mới ở Tab 2!")
    else:
        st.subheader("1. Chọn tin đăng cần xử lý")
        
        # Cho phép chọn tin đăng cụ thể trong danh sách chờ
        listing_options = [
            f"[{item.get('district', 'Đà Nẵng')}] - {item.get('title')} ({item.get('area')}m²)"
            for item in pending_listings
        ]
        
        # Giữ nguyên bài viết đang chọn khi reload trang
        if "selected_listing_idx" not in st.session_state:
            st.session_state["selected_listing_idx"] = 0
        elif st.session_state["selected_listing_idx"] >= len(pending_listings):
            st.session_state["selected_listing_idx"] = 0
            
        selected_idx = st.selectbox(
            "Chọn bài viết từ danh sách chờ:",
            options=list(range(len(pending_listings))),
            format_func=lambda idx: listing_options[idx],
            index=st.session_state["selected_listing_idx"]
        )
        st.session_state["selected_listing_idx"] = selected_idx
        
        target_item = pending_listings[selected_idx]
        
        # --- Khởi tạo Session State cho việc Biên tập thông tin phản hồi từ UI ---
        state_key = f"prev_selected_idx"
        if state_key not in st.session_state or st.session_state[state_key] != selected_idx:
            st.session_state[state_key] = selected_idx
            
            usd_val, vnd_val = parse_usd_and_vnd(target_item.get("price", ""), target_item.get("area", ""))
            # Tính giá VNĐ/m² từ tổng VNĐ và diện tích
            area_match_init = re.search(r'(\d+)', str(target_item.get("area", "100")))
            area_init = int(area_match_init.group(1)) if area_match_init else 100
            vnd_per_m2_init = int(vnd_val / area_init) if area_init > 0 and vnd_val > 0 else 0
            st.session_state["temp_vnd_per_m2"] = vnd_per_m2_init
            st.session_state["temp_vnd"] = vnd_val
            st.session_state["temp_ref_usd"] = usd_val
            st.session_state["temp_area"] = target_item.get("area", "")
            st.session_state["temp_address"] = target_item.get("address", "")
            st.session_state["temp_district"] = target_item.get("district", "")
            st.session_state["temp_title"] = target_item.get("title", "")
            st.session_state["temp_content"] = target_item.get("content", "")

        # Callback khi đổi đơn giá VNĐ/m²
        def on_vnd_per_m2_change():
            try:
                vnd_m2 = float(st.session_state.temp_vnd_per_m2)
                area_match = re.search(r'(\d+)', str(st.session_state.temp_area))
                area = int(area_match.group(1)) if area_match else 100
                st.session_state["temp_vnd"] = int(vnd_m2 * area)
                # Cập nhật giá USD tham chiếu ngược lại
                st.session_state["temp_ref_usd"] = round(vnd_m2 / 26200, 2)
            except Exception:
                pass

        # Callback khi đổi diện tích
        def on_area_change():
            try:
                area_match = re.search(r'(\d+)', str(st.session_state.temp_area))
                area = int(area_match.group(1)) if area_match else 100
                vnd_m2 = float(st.session_state.temp_vnd_per_m2)
                st.session_state["temp_vnd"] = int(vnd_m2 * area)
            except Exception:
                pass

        # Callback khi đổi tổng giá VNĐ
        def on_vnd_change():
            try:
                vnd = float(st.session_state.temp_vnd)
                area_match = re.search(r'(\d+)', str(st.session_state.temp_area))
                area = int(area_match.group(1)) if area_match else 100
                if area > 0:
                    vnd_m2 = int(vnd / area)
                    st.session_state["temp_vnd_per_m2"] = vnd_m2
                    st.session_state["temp_ref_usd"] = round(vnd_m2 / 26200, 2)
            except Exception:
                pass

        # Callback khi đổi giá USD tham chiếu
        def on_ref_usd_change():
            try:
                usd = float(st.session_state.temp_ref_usd)
                if usd > 0:
                    usd_rate = 26200
                    area_match = re.search(r'(\d+)', str(st.session_state.temp_area))
                    area = int(area_match.group(1)) if area_match else 100
                    vnd_m2 = int(usd * usd_rate)
                    st.session_state["temp_vnd_per_m2"] = vnd_m2
                    st.session_state["temp_vnd"] = int(vnd_m2 * area)
            except Exception:
                pass

        # Hiển thị chi tiết bài viết trong Layout đẹp mắt
        st.markdown('<div class="listing-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### 📍 {target_item.get('title')}")
            st.caption(f"🔗 **Link gốc:** [{target_item.get('source_url')}]({target_item.get('source_url')})")
        with col2:
            st.metric(label="Diện tích", value=f"{target_item.get('area')} m²")
        with col3:
            _, vnd_display = parse_usd_and_vnd(target_item.get('price', ''), target_item.get('area', ''))
            if vnd_display > 0:
                st.metric(label="Giá thuê", value=f"{vnd_display:,} VNĐ".replace(',', '.'))
            else:
                st.metric(label="Giá thuê", value=target_item.get('price'))
            
        col_addr1, col_addr2 = st.columns([3, 1])
        with col_addr1:
            st.info(f"📍 **Địa chỉ:** {target_item.get('address')}")
        with col_addr2:
            st.warning(f"🏛️ **Quận chính xác:** {target_item.get('district')}")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Hiển thị nhãn trạng thái tối ưu hóa AI
        is_ai_val = target_item.get("is_ai", "False")
        if is_ai_val == "True":
            st.success("🤖 **Tin đăng này đã được tối ưu hóa độc bản bằng AI (Ollama)**")
        else:
            st.warning("📝 **Tin đăng này đang sử dụng mẫu spin thường (chưa tối ưu bằng AI)**")
            
        st.subheader("2. Biên tập nội dung bài đăng (Nếu muốn)")
        
        col_fields1, col_fields2, col_fields3 = st.columns(3)
        with col_fields1:
            edited_area = st.text_input(
                "Diện tích sử dụng (m²):", 
                key="temp_area",
                on_change=on_area_change
            )
            edited_price_vnd_per_m2 = st.number_input(
                "💰 Giá thuê VNĐ/m²/tháng:",
                min_value=0,
                step=10000,
                key="temp_vnd_per_m2",
                on_change=on_vnd_per_m2_change,
                help="Nhập giá một mét vuông mỗi tháng. Thay đổi sẽ tự động tính lại Tổng giá."
            )
            
        with col_fields2:
            edited_address = st.text_input(
                "Địa chỉ:", 
                key="temp_address"
            )
            edited_price_vnd = st.number_input(
                "Tổng giá thuê VNĐ/tháng:",
                min_value=0,
                step=500000,
                key="temp_vnd",
                on_change=on_vnd_change,
                help="Tổng giá thuê mỗi tháng. Thay đổi sẽ tự động tính lại Giá/m²."
            )
            
        with col_fields3:
            edited_district = st.text_input(
                "Quận/Huyện (Đã chuẩn hóa):", 
                key="temp_district"
            )
            ref_usd_val = st.number_input(
                "💵 Giá USD/m²/tháng (Tham chiếu):",
                min_value=0.0,
                step=0.5,
                key="temp_ref_usd",
                on_change=on_ref_usd_change,
                help="Chỉ dùng làm mốc quy đổi nhanh ra VNĐ (Tỷ giá: 26.200 VNĐ/USD). Không lưu trực tiếp vào tin đăng."
            )
            
        edited_title = st.text_input(
            "Tiêu đề bài viết:", 
            key="temp_title"
        )
        edited_content = st.text_area(
            "Nội dung mô tả bài viết (Nhấn xuống dòng thoải mái cho đẹp mắt):", 
            height=300,
            key="temp_content"
        )
        
        # Đồng bộ lại nội dung sửa đổi vào đối tượng cho tiến trình chạy bot
        target_item['area'] = edited_area
        target_item['price'] = str(int(edited_price_vnd))
        target_item['address'] = edited_address
        target_item['district'] = edited_district
        target_item['title'] = edited_title
        target_item['content'] = edited_content
        
        # Nút hành động bổ sung (AI Rewrite & Lưu chỉnh sửa)
        col_actions1, col_actions2 = st.columns(2)
        with col_actions1:
            if st.button("🤖 Viết lại (Rewrite) bằng AI cục bộ", use_container_width=True, help="Yêu cầu Qwen2:1.5b viết lại tiêu đề và mô tả mới dựa trên thông tin hiện tại."):
                with st.spinner("AI đang suy nghĩ và viết lại..."):
                    try:
                        from extract_buildings import rewrite_listing_with_ollama
                        
                        # Chuẩn bị giá dạng chuỗi để gửi AI
                        _, total_vnd_numeric = parse_usd_and_vnd(edited_price_vnd, edited_area)
                        price_display = f"{total_vnd_numeric:,} VNĐ/tháng".replace(',', '.') if total_vnd_numeric > 0 else "Thỏa thuận"
                        
                        # Trích xuất tên tòa nhà sạch từ tiêu đề gốc để tránh bị lồng tiêu đề dài dòng
                        clean_building_name = extract_building_name_from_title(edited_title, edited_district)
                        if not clean_building_name:
                            clean_building_name = edited_title
                            
                        ai_title, ai_content = rewrite_listing_with_ollama(
                            building_name=clean_building_name,
                            area=edited_area,
                            price=price_display,
                            address=edited_address,
                            raw_content=edited_content,
                            scenario="marketing",
                            model="gemma2:2b" # default model on 8GB Mac
                        )
                        
                        if ai_title and ai_content:
                            contact_name = target_item.get("contact_name", "Nguyễn Ngọc Thiên Bình")
                            phone = target_item.get("phone", "0935723727")
                            footer = f"\n\n📞 Liên hệ xem văn phòng: {phone} ({contact_name})"
                            
                            # Cập nhật trực tiếp vào đối tượng và lưu
                            target_item['title'] = ai_title
                            target_item['content'] = ai_content.strip() + footer
                            target_item['is_ai'] = "True"
                            
                            # Xóa flag index cũ để ép buộc reload lại session state ở đầu trang ở chu kỳ sau
                            if "prev_selected_idx" in st.session_state:
                                del st.session_state["prev_selected_idx"]
                            
                            if save_listings(all_listings):
                                st.toast("Đã viết lại bằng AI và tự động lưu!", icon="🤖")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("❌ AI không trả về dữ liệu. Hãy đảm bảo ứng dụng Ollama đã chạy.")
                    except Exception as ex:
                        st.error(f"❌ Lỗi khi kết nối Ollama: {ex}")
                        
        with col_actions2:
            if st.button("💾 Lưu chỉnh sửa thủ công (data.csv)", type="primary", use_container_width=True):
                target_item['is_ai'] = "False"  # Đánh dấu là đã sửa thủ công hoặc không phải AI gốc
                if save_listings(all_listings):
                    st.toast("Đã lưu các sửa đổi vào data.csv thành công!", icon="💾")
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        st.subheader("3. Thiết lập & Bắt đầu đăng")
        
        # Chọn các kênh để đăng tin
        col_setup1, col_setup2 = st.columns(2)
        with col_setup1:
            st.write("👉 **Chọn các trang web muốn đăng bài:**")
            active_channels = []
            for site_key, site_info in SUPPORTED_SITES.items():
                # Lấy danh sách tài khoản để xác định trạng thái cấu hình
                accs = config.get("accounts", {}).get(site_key, [])
                old_creds = config.get(site_key, {})
                has_creds = len(accs) > 0 or any(old_creds.values()) if old_creds else False
                
                is_cooldown, cooldown_msg = get_site_cooldown(site_key, posted_history)
                if is_cooldown:
                    st.checkbox(
                        cooldown_msg,
                        value=False,
                        disabled=True,
                        key=f"check_post_{site_key}"
                    )
                else:
                    is_selected = st.checkbox(
                        f"{site_info['name']} (Đã cấu hình)" if has_creds else f"{site_info['name']} (Chưa cấu hình ⚠️)",
                        value=has_creds,
                        key=f"check_post_{site_key}"
                    )
                    if is_selected:
                        active_channels.append(site_key)
                    
            # Chọn tài khoản cụ thể cho từng trang đã chọn
            selected_accounts = {}
            if active_channels:
                st.markdown("🔒 **Chọn tài khoản thực hiện cho từng trang:**")
                for site_key in active_channels:
                    site_info = SUPPORTED_SITES[site_key]
                    acc_list = config.get("accounts", {}).get(site_key, [])
                    old_creds = config.get(site_key, {})
                    if old_creds and any(old_creds.values()):
                        if not any(a.get("username") == old_creds.get("username") or a.get("email") == old_creds.get("email") for a in acc_list):
                            acc_list = [old_creds] + acc_list
                    
                    if not acc_list:
                        st.warning(f"⚠️ Chưa có tài khoản cho {site_info['name']}. Vui lòng thiết lập ở Tab Cấu hình.")
                        selected_accounts[site_key] = {}
                    else:
                        options_lbl = []
                        for idx, a in enumerate(acc_list):
                            lbl = a.get("label") or a.get("username") or a.get("email") or f"Tài khoản #{idx+1}"
                            options_lbl.append(lbl)
                        sel_lbl = st.selectbox(f"Tài khoản {site_info['name']}:", options=options_lbl, key=f"sel_acc_post_{site_key}")
                        selected_accounts[site_key] = acc_list[options_lbl.index(sel_lbl)]
        
        with col_setup2:
            st.write("⚙️ **Chế độ trình duyệt:**")
            run_headless = st.checkbox("Chạy ẩn danh (Không hiện cửa sổ Chrome tự động)", value=False)
            save_hist = st.checkbox("Lưu bài viết này vào lịch sử sau khi đăng thành công", value=True)
            run_dry_run = st.checkbox("Chạy thử nghiệm (Dry-run)", value=False, help="Điền tất cả thông tin biểu mẫu nhưng không bấm nút đăng tin cuối cùng")
            run_ai_repair = st.checkbox("Tự động sửa lỗi bằng AI (AI-Repair)", value=False, help="Tự động gọi AI phân tích DOM và cập nhật selectors khi gặp lỗi")
            
        # NÚT BẮT ĐẦU ĐĂNG TIN
        st.write("")
        if st.button("🚀 BẮT ĐẦU ĐĂNG TIN NGAY", type="primary", use_container_width=True):
            if not active_channels:
                st.error("⚠️ Vui lòng tích chọn ít nhất 1 trang web để đăng tin!")
            else:
                st.info(f"Đang chuẩn bị đăng bài viết lên {len(active_channels)} kênh đã chọn...")
                
                # Khởi tạo container hiển thị log trực tiếp
                st.subheader("📟 Tiến trình chạy của Bot (Log thời gian thực)")
                log_placeholder = st.empty()
                
                # Chạy luồng tự động hóa đăng tin
                with st.spinner("Đang chạy bot tự động. Vui lòng không đóng tab Web App..."):
                    # Redirect stdout để bắt logs trực tiếp
                    log_redirect = StreamlitLogRedirector(log_placeholder)
                    
                    old_stdout = sys.stdout
                    sys.stdout = log_redirect
                    
                    success_channels = []
                    failed_channels = []
                    bot = None
                    try:
                        bot = WebAutomation(headless=run_headless)
                        bot.start()
                        
                        # Kịch bản 1: Raovat.net
                        if "raovat.net" in active_channels:
                            acc = selected_accounts.get("raovat.net", {})
                            def fallback_raovat():
                                email_val = acc.get("email")
                                if email_val:
                                    login_ok = bot.login_raovat_net(email_val, acc.get("password"))
                                    if login_ok:
                                        post_ok = bot.post_raovat_net(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin Raovat thất bại!")
                                    else:
                                        print("❌ Đăng nhập Raovat thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("raovat.net", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_raovat):
                                success_channels.append("raovat.net")
                            else:
                                failed_channels.append("raovat.net")
                            time.sleep(3)

                        # Kịch bản 2: Thuviennhadat.vn
                        if "thuviennhadat.vn" in active_channels:
                            acc = selected_accounts.get("thuviennhadat.vn", {})
                            def fallback_thuviennhadat():
                                username_val = acc.get("username") or acc.get("phone")
                                if username_val:
                                    login_ok = bot.login_thuviennhadat(username_val, acc.get("password"))
                                    if login_ok:
                                        post_ok = bot.post_thuviennhadat(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin Thuviennhadat thất bại!")
                                    else:
                                        print("❌ Đăng nhập Thuviennhadat thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("thuviennhadat.vn", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_thuviennhadat):
                                success_channels.append("thuviennhadat.vn")
                            else:
                                failed_channels.append("thuviennhadat.vn")
                            time.sleep(3)

                        # Kịch bản 3: Muaban.net
                        if "muaban.net" in active_channels:
                            acc = selected_accounts.get("muaban.net", {})
                            def fallback_muaban():
                                username_mb = acc.get("username", "")
                                password_mb = acc.get("password", "")
                                if username_mb:
                                    login_ok = bot.login_muaban(username_mb, password_mb)
                                    if login_ok:
                                        post_ok = bot.post_muaban(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin Muaban thất bại!")
                                    else:
                                        print("❌ Đăng nhập Muaban thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("muaban.net", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_muaban):
                                success_channels.append("muaban.net")
                            else:
                                failed_channels.append("muaban.net")
                            time.sleep(3)

                        # Kịch bản 4: 123NhaDatViet.com
                        if "123nhadatviet.com" in active_channels:
                            acc = selected_accounts.get("123nhadatviet.com", {})
                            def fallback_123nhadatviet():
                                user_123 = acc.get("username", "")
                                pass_123 = acc.get("password", "")
                                if user_123:
                                    login_ok = bot.login_123nhadatviet(user_123, pass_123)
                                    if login_ok:
                                        post_ok = bot.post_123nhadatviet(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin 123NhaDatViet thất bại!")
                                    else:
                                        print("❌ Đăng nhập 123NhaDatViet thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("123nhadatviet.com", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_123nhadatviet):
                                success_channels.append("123nhadatviet.com")
                            else:
                                failed_channels.append("123nhadatviet.com")
                            time.sleep(3)

                        # Kịch bản 5: NhaDatViet247.net
                        if "nhadatviet247.net" in active_channels:
                            acc = selected_accounts.get("nhadatviet247.net", {})
                            def fallback_nhadatviet247():
                                user_247 = acc.get("username", "")
                                pass_247 = acc.get("password", "")
                                if user_247:
                                    login_ok = bot.login_nhadatviet247(user_247, pass_247)
                                    if login_ok:
                                        post_ok = bot.post_nhadatviet247(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin NhaDatViet247 thất bại!")
                                    else:
                                        print("❌ Đăng nhập NhaDatViet247 thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("nhadatviet247.net", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_nhadatviet247):
                                success_channels.append("nhadatviet247.net")
                            else:
                                failed_channels.append("nhadatviet247.net")
                            time.sleep(3)

                        # Kịch bản 6: MuaBanDaNang.vn
                        if "muabandanang.vn" in active_channels:
                            acc = selected_accounts.get("muabandanang.vn", {})
                            def fallback_muabandanang():
                                user_mbdn = acc.get("username", "")
                                pass_mbdn = acc.get("password", "")
                                if user_mbdn:
                                    login_ok = bot.login_muabandanang(user_mbdn, pass_mbdn)
                                    if login_ok:
                                        post_ok = bot.post_muabandanang(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin MuaBanDaNang thất bại!")
                                    else:
                                        print("❌ Đăng nhập MuaBanDaNang thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("muabandanang.vn", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_muabandanang):
                                success_channels.append("muabandanang.vn")
                            else:
                                failed_channels.append("muabandanang.vn")
                            time.sleep(3)

                        # Kịch bản 7: PhongTro123.com
                        if "phongtro123.com" in active_channels:
                            acc = selected_accounts.get("phongtro123.com", {})
                            def fallback_phongtro123():
                                user_val = acc.get("username", "")
                                pass_val = acc.get("password", "")
                                if user_val:
                                    login_ok = bot.login_phongtro123(user_val, pass_val)
                                    if login_ok:
                                        post_ok = bot.post_phongtro123(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin PhongTro123 thất bại!")
                                    else:
                                        print("❌ Đăng nhập PhongTro123 thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("phongtro123.com", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_phongtro123):
                                success_channels.append("phongtro123.com")
                            else:
                                failed_channels.append("phongtro123.com")
                            time.sleep(3)

                        # Kịch bản 8: ThuePhongTro.com
                        if "thuephongtro.com" in active_channels:
                            acc = selected_accounts.get("thuephongtro.com", {})
                            def fallback_thuephongtro():
                                user_val = acc.get("username", "") or acc.get("phone", "")
                                pass_val = acc.get("password", "")
                                if user_val:
                                    login_ok = bot.login_thuephongtro(user_val, pass_val)
                                    if login_ok:
                                        post_ok = bot.post_thuephongtro(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin ThuePhongTro thất bại!")
                                    else:
                                        print("❌ Đăng nhập ThuePhongTro thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("thuephongtro.com", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_thuephongtro):
                                success_channels.append("thuephongtro.com")
                            else:
                                failed_channels.append("thuephongtro.com")
                            time.sleep(3)

                        # Kịch bản 9: BDS123.vn
                        if "bds123.vn" in active_channels:
                            acc = selected_accounts.get("bds123.vn", {})
                            def fallback_bds123():
                                user_val = acc.get("username") or acc.get("phone")
                                pass_val = acc.get("password")
                                if user_val:
                                    login_ok = bot.login_bds123(user_val, pass_val)
                                    if login_ok:
                                        post_ok = bot.post_bds123(target_item, user_val, pass_val)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin BDS123 thất bại!")
                                    else:
                                        print("❌ Đăng nhập BDS123 thất bại!")
                                return False
                                
                            if execute_channel_posting_ui("bds123.vn", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_bds123):
                                success_channels.append("bds123.vn")
                            else:
                                failed_channels.append("bds123.vn")
                            time.sleep(3)

                        # Kịch bản 10: GiaoDichNhaDat.vn
                        if "giaodichnhadat.vn" in active_channels:
                            acc = selected_accounts.get("giaodichnhadat.vn", {})
                            def fallback_giaodichnhadat():
                                email_val = acc.get("email") or acc.get("username")
                                pass_val  = acc.get("password")
                                if email_val:
                                    login_ok = bot.login_giaodichnhadat(email_val, pass_val)
                                    if login_ok:
                                        post_ok = bot.post_giaodichnhadat(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin GiaoDichNhaDat thất bại!")
                                    else:
                                        print("❌ Đăng nhập GiaoDichNhaDat thất bại!")
                                return False
                            if execute_channel_posting_ui("giaodichnhadat.vn", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_giaodichnhadat):
                                success_channels.append("giaodichnhadat.vn")
                            else:
                                failed_channels.append("giaodichnhadat.vn")
                            time.sleep(3)

                        # Kịch bản 11: ThongTinNhaDat.vn
                        if "thongtinnhadat.vn" in active_channels:
                            acc = selected_accounts.get("thongtinnhadat.vn", {})
                            def fallback_thongtinnhadat():
                                email_val = acc.get("email") or acc.get("username")
                                pass_val  = acc.get("password")
                                if email_val:
                                    login_ok = bot.login_thongtinnhadat(email_val, pass_val)
                                    if login_ok:
                                        post_ok = bot.post_thongtinnhadat(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin ThongTinNhaDat thất bại!")
                                    else:
                                        print("❌ Đăng nhập ThongTinNhaDat thất bại!")
                                return False
                            if execute_channel_posting_ui("thongtinnhadat.vn", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_thongtinnhadat):
                                success_channels.append("thongtinnhadat.vn")
                            else:
                                failed_channels.append("thongtinnhadat.vn")
                            time.sleep(3)

                        # Kịch bản 12: DangTinBatDongSan.vn
                        if "dangtinbatdongsan.vn" in active_channels:
                            acc = selected_accounts.get("dangtinbatdongsan.vn", {})
                            def fallback_dangtinbatdongsan():
                                user_val = acc.get("username") or acc.get("phone")
                                pass_val = acc.get("password")
                                if user_val:
                                    login_ok = bot.login_dangtinbatdongsan(user_val, pass_val)
                                    if login_ok:
                                        post_ok = bot.post_dangtinbatdongsan(target_item)
                                        if post_ok:
                                            return True
                                        print("❌ Đăng tin DangTinBatDongSan thất bại!")
                                    else:
                                        print("❌ Đăng nhập DangTinBatDongSan thất bại!")
                                return False
                            if execute_channel_posting_ui("dangtinbatdongsan.vn", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_dangtinbatdongsan):
                                success_channels.append("dangtinbatdongsan.vn")
                            else:
                                failed_channels.append("dangtinbatdongsan.vn")
                            time.sleep(3)

                        # Kịch bản 13: LuaChonNhaDat.vn
                        if "luachonnhadat.vn" in active_channels:
                            acc = selected_accounts.get("luachonnhadat.vn", {})
                            def fallback_luachonnhadat():
                                email_val = acc.get("username") or acc.get("email")
                                if email_val:
                                    post_ok = bot.post_luachonnhadat(target_item)
                                    if post_ok:
                                        return True
                                    print("❌ Đăng tin LuaChonNhaDat thất bại!")
                                return False
                            if execute_channel_posting_ui("luachonnhadat.vn", acc, target_item, bot, run_dry_run, run_ai_repair, run_headless, fallback_luachonnhadat):
                                success_channels.append("luachonnhadat.vn")
                            else:
                                failed_channels.append("luachonnhadat.vn")
                            time.sleep(3)

                        print("\n🏁 Đã hoàn thành tiến trình đăng bài trên tất cả các trang được chọn!")
                        
                        if success_channels:
                            print(f"✅ Đăng tin thành công trên các kênh: {', '.join(success_channels)}")
                        else:
                            print("❌ Không có kênh nào đăng tin thành công!")
                        
                        if failed_channels:
                            print(f"❌ Đăng tin thất bại trên các kênh: {', '.join(failed_channels)}")
                            
                    except Exception as e:
                        print(f"\n❌ Có lỗi xảy ra trong quá trình chạy bot: {e}")
                    finally:
                        if bot:
                            bot.stop()
                            print("🔒 Trình duyệt Playwright đã đóng.")
                            
                        # Ghi nhận log file và lịch sử
                        if save_hist:
                            log_filename = f"run_{time.strftime('%Y%m%d_%H%M%S')}.log"
                            try:
                                logs_dir = os.path.join(BOT_DIR, "logs")
                                os.makedirs(logs_dir, exist_ok=True)
                                with open(os.path.join(logs_dir, log_filename), "w", encoding="utf-8") as lf:
                                    lf.write(log_redirect.log_content)
                            except:
                                pass
                            
                            status_val = "Thành công" if success_channels else "Thất bại"
                            posted_history.append({
                                "title": target_item.get("title"),
                                "area": target_item.get("area"),
                                "source_url": target_item.get("source_url"),
                                "posted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "status": status_val,
                                "channels": ", ".join(success_channels) if success_channels else "Không có",
                                "log_file": log_filename
                            })
                            save_posted_history(posted_history)
                            
                        # Khôi phục lại stdout chuẩn
                        sys.stdout = old_stdout
                        
                st.success("🎉 Bot đã chạy xong! Bạn có thể xem log chi tiết bên trên hoặc chuyển sang tin khác.")
                
                # Hiển thị các nút xem screenshot gần đây
                recent_screenshots = get_recent_screenshots(active_channels, max_age_secs=600)
                if recent_screenshots:
                    st.write("### 📸 Ảnh chụp màn hình kết quả:")
                    for site_key in active_channels:
                        clean_key = site_key.replace(".vn", "").replace(".com.vn", "").replace(".com", "").replace(".net", "").replace(".", "_")
                        site_screenshots = [p for p in recent_screenshots if clean_key in os.path.basename(p).lower()]
                        if site_screenshots:
                            st.write(f"**{SUPPORTED_SITES[site_key]['name']}**:")
                            cols = st.columns(len(site_screenshots))
                            for idx, img_path in enumerate(site_screenshots):
                                name = os.path.basename(img_path)
                                label = "Đăng nhập OK" if "login_ok" in name else "Kết quả đăng" if "post_done" in name or "after_submit" in name else "Form đã điền" if "filled" in name else "Lỗi" if "error" in name or "fail" in name else name
                                with cols[idx]:
                                    if st.button(f"🔍 Xem {label}", key=f"btn_show_img_{name}_{idx}_{site_key}"):
                                        show_screenshot_dialog(f"Ảnh: {name}", [img_path])
                                        
                st.button("🔄 Làm mới danh sách tin đăng", on_click=lambda: None)

# =============================================================================
# TAB 2: CÀO & XÀO BÀI VIẾT MỚI
# =============================================================================
with tab_spin:
    st.subheader("🌪️ Máy Quét & Xào bài viết (Cơ chế 100% Cục bộ)")
    st.write("""
    Tính năng này giúp tự động cào các tòa nhà văn phòng cho thuê mới nhất từ website **Officedanang.vn**, 
    sau đó tự động tách các diện tích trống thực tế thành hàng loạt các tin rao vặt độc bản phong phú.
    """)
    
    col_crawl1, col_crawl2, col_crawl3 = st.columns(3)
    with col_crawl1:
        limit_pages = st.number_input("Số trang danh mục cần quét tối đa:", min_value=1, max_value=30, value=3, step=1)
    with col_crawl2:
        scenario_options = {
            "long": "Dài (Đầy đủ chi tiết)",
            "medium": "Trung bình (Tóm tắt)",
            "short": "Ngắn (Chỉ địa chỉ, diện tích, giá)",
            "basic_lease": "Chào thuê cơ bản (Tài chính & Bàn giao)",
            "marketing": "Quảng cáo (Tiêu đề thu hút + Pitching)"
        }
        scenario_choice = st.selectbox(
            "Kịch bản nội dung (Xào bài):",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x]
        )
    with col_crawl3:
        st.write("")
        st.write("")
        run_spin = st.button("🌪️ BẮT ĐẦU QUÉT & XÀO BÀI MỚI", type="primary", use_container_width=True)
        
    st.markdown("---")
    col_ai1, col_ai2 = st.columns(2)
    with col_ai1:
        use_llm = st.checkbox(
            "🤖 Sử dụng AI cục bộ (Ollama) để viết lại nội dung", 
            value=False, 
            help="Dùng mô hình Qwen2/Gemma2 chạy offline để viết lại tiêu đề và mô tả tự nhiên, tránh trùng lặp tin rao vặt."
        )
    with col_ai2:
        llm_model = st.text_input(
            "Tên mô hình Ollama sử dụng:", 
            value="gemma2:2b", 
            help="Đảm bảo mô hình này đã được tải về và Ollama đang hoạt động ngầm (ví dụ: ollama run gemma2:2b)."
        )
        
    if run_spin:
        st.subheader("📟 Nhật ký Quét & Xào tin đăng")
        log_crawl_placeholder = st.empty()
        
        with st.spinner("Đang kết nối tới Officedanang và xào bài viết..."):
            log_redirect = StreamlitLogRedirector(log_crawl_placeholder)
            old_stdout = sys.stdout
            sys.stdout = log_redirect
            
            try:
                print("🔍 1. Khởi động Crawler...")
                crawler = OfficeDanangCrawler()
                
                print(f"🔍 2. Bắt đầu quét {limit_pages} trang danh mục để lấy link tòa nhà...")
                all_links = []
                for p in range(1, limit_pages + 1):
                    links = crawler.extract_property_links(p)
                    all_links.extend(links)
                    time.sleep(0.5)
                
                all_links = list(set(all_links))
                print(f"=> Tìm thấy tổng cộng {len(all_links)} link tòa nhà.")
                
                # Cào chi tiết tòa nhà
                buildings = []
                print("\n🔍 3. Bắt đầu cào thông tin chi tiết từng tòa nhà...")
                for idx, url in enumerate(all_links):
                    print(f"[{idx+1}/{len(all_links)}]...")
                    details = crawler.parse_property_details(url)
                    if details:
                        buildings.append(details)
                        print(f"   => Thành công: {details['title']} | Các diện tích: {details['split_sizes']}")
                    time.sleep(0.5)
                
                # Xào bài viết
                print(f"\n🌪️ 4. Bắt đầu xào bài viết tự động với kịch bản '{scenario_choice}'...")
                listings = crawler.spin_and_generate_listings(
                    buildings, 
                    scenario=scenario_choice,
                    use_llm=use_llm,
                    llm_model=llm_model
                )
                
                # Ghi đè vào data.csv
                save_to_csv(listings, DATA_FILE)
                print(f"\n✅ HOÀN THÀNH! Đã lưu {len(listings)} bài viết vào file dữ liệu data.csv.")
                
            except Exception as e:
                print(f"\n❌ Lỗi hệ thống: {e}")
            finally:
                sys.stdout = old_stdout
                
        st.success("🎉 Đã quét và xào bài viết thành công! Dữ liệu của bạn đã được cập nhật.")
        st.button("🔄 Nhấn để xem tin đăng mới ở Tab 1", on_click=lambda: None)

# =============================================================================
# TAB 3: LỊCH TRÌNH & HẸN GIỜ ĐĂNG
# =============================================================================
with tab_schedule:
    st.subheader("📅 Quản lý Lịch trình & Hẹn giờ đăng tin tự động")
    import scheduler
    scheduler.start_scheduler()
    
    queue = scheduler.load_queue()
    
    st.write("### ➕ Lên lịch đăng tin mới")
    if not pending_listings:
        st.info("Không có tin đăng nào đang chờ xử lý.")
    else:
        col_sch1, col_sch2 = st.columns(2)
        with col_sch1:
            sch_idx = st.selectbox(
                "Chọn bài đăng từ danh sách chờ:",
                options=range(len(pending_listings)),
                format_func=lambda idx: f"[{pending_listings[idx].get('district')}] - {pending_listings[idx].get('title')}"
            )
            sch_date = st.date_input("Chọn ngày thực hiện:")
            sch_time = st.time_input("Chọn giờ thực hiện:")
        with col_sch2:
            st.write("Chọn các trang đăng:")
            sch_channels = []
            for site_key, site_info in SUPPORTED_SITES.items():
                is_cooldown, cooldown_msg = get_site_cooldown(site_key, posted_history)
                if is_cooldown:
                    st.checkbox(
                        cooldown_msg,
                        value=False,
                        disabled=True,
                        key=f"sch_check_{site_key}"
                    )
                else:
                    if st.checkbox(site_info["name"], key=f"sch_check_{site_key}"):
                        sch_channels.append(site_key)
                    
        if st.button("⏰ Thêm vào hàng đợi hẹn giờ", use_container_width=True):
            if not sch_channels:
                st.error("⚠️ Vui lòng chọn ít nhất 1 trang web!")
            else:
                target = pending_listings[sch_idx]
                dt_str = f"{sch_date} {sch_time.strftime('%H:%M:00')}"
                import uuid
                task_id = str(uuid.uuid4())[:8]
                new_task = {
                    "id": task_id,
                    "item": target,
                    "scheduled_time": dt_str,
                    "channels": sch_channels,
                    "status": "Chờ chạy"
                }
                queue.append(new_task)
                if scheduler.save_queue(queue):
                    st.success(f"Đã lên lịch thành công tác vụ {task_id} vào lúc {dt_str}!")
                    time.sleep(1)
                    st.rerun()

    st.write("---")
    st.write("### 📋 Hàng đợi đăng tin hiện tại")
    if not queue:
        st.info("Chưa có tác vụ hẹn giờ nào.")
    else:
        df_queue = pd.DataFrame(queue)
        st.dataframe(
            df_queue[["id", "scheduled_time", "channels", "status"]],
            column_config={
                "id": "Mã tác vụ",
                "scheduled_time": "Thời gian chạy",
                "channels": "Trang đăng",
                "status": "Trạng thái"
            },
            use_container_width=True
        )
        
        # Hủy lịch trình
        to_delete = st.selectbox("Chọn mã tác vụ muốn hủy bỏ:", options=[t["id"] for t in queue])
        if st.button("🗑️ Hủy lịch trình tác vụ đã chọn", type="secondary"):
            queue = [t for t in queue if t["id"] != to_delete]
            if scheduler.save_queue(queue):
                st.success("Đã hủy bỏ tác vụ hẹn giờ thành công!")
                time.sleep(1)
                st.rerun()

# =============================================================================
# TAB 4: TỰ ĐỘNG UP TIN / LÀM MỚI TIN ĐĂNG CŨ
# =============================================================================
with tab_renew:
    st.subheader("🔄 Tự động Up Tin / Làm mới tin đăng cũ trên các nền tảng")
    st.write("Bot sẽ tự động đăng nhập vào Dashboard cá nhân của các nền tảng và nhấn nút Up tin/Làm mới để đưa tin của bạn lên đầu trang.")
    
    col_renew1, col_renew2 = st.columns(2)
    with col_renew1:
        renew_site = st.selectbox("Chọn trang rao vặt muốn Up tin:", options=list(SUPPORTED_SITES.keys()), format_func=lambda k: SUPPORTED_SITES[k]["name"])
        
        acc_list = config.get("accounts", {}).get(renew_site, [])
        old_creds = config.get(renew_site, {})
        if old_creds and any(old_creds.values()):
            if not any(a.get("username") == old_creds.get("username") or a.get("email") == old_creds.get("email") for a in acc_list):
                acc_list = [old_creds] + acc_list
                
        if not acc_list:
            st.error("Chưa cấu hình tài khoản cho trang này. Vui lòng thêm tài khoản ở Tab Hệ thống.")
            renew_acc = None
        else:
            renew_acc = st.selectbox(
                "Chọn tài khoản thực hiện:",
                options=acc_list,
                format_func=lambda a: a.get("label") or a.get("username") or a.get("email")
            )
            
    with col_renew2:
        renew_headless = st.checkbox("Chạy trình duyệt ẩn danh khi Up tin", value=True)
        st.write("")
        run_renew_btn = st.button("⚡ KHỞI CHẠY TỰ ĐỘNG UP TIN NGAY", type="primary", use_container_width=True, disabled=(renew_acc is None))
        
    if run_renew_btn and renew_acc:
        st.subheader("📟 Nhật ký hoạt động chạy Up tin")
        renew_log_placeholder = st.empty()
        with st.spinner("Đang kết nối trình duyệt để Up tin tự động..."):
            log_redirect = StreamlitLogRedirector(renew_log_placeholder)
            old_stdout = sys.stdout
            sys.stdout = log_redirect
            
            bot = None
            try:
                bot = WebAutomation(headless=renew_headless)
                bot.start()
                username_val = renew_acc.get("username") or renew_acc.get("email")
                bot.renew_posts(renew_site, username_val, renew_acc.get("password"))
            except Exception as e:
                print(f"❌ Lỗi: {e}")
            finally:
                if bot:
                    bot.stop()
                sys.stdout = old_stdout
        st.success("🎉 Đã hoàn thành tiến trình tự động Up tin!")

# =============================================================================
# TAB 5: CẤU HÌNH ĐÓNG DẤU ẢNH (WATERMARK)
# =============================================================================
with tab_watermark:
    st.subheader("🎨 Thiết lập chèn đóng dấu bản quyền hình ảnh (Watermark)")
    st.write("Tự động phủ tên thương hiệu/số điện thoại lên các hình ảnh bài viết để bảo vệ bản quyền.")
    
    wm_config = config.get("watermark", {
        "enabled": False,
        "text": "Ngọc Thiên Bình - 0935.723.727",
        "color": "#FFFFFF",
        "opacity": 0.6,
        "position": "bottom_right"
    })
    
    wm_enabled = st.checkbox("Kích hoạt đóng dấu ảnh tự động khi đăng tin", value=wm_config.get("enabled", False))
    
    col_wm1, col_wm2 = st.columns(2)
    with col_wm1:
        wm_text = st.text_input("Nội dung chữ chèn đè:", value=wm_config.get("text", "Ngọc Thiên Bình - 0935.723.727"))
        wm_color = st.color_picker("Màu sắc chữ đóng dấu:", value=wm_config.get("color", "#FFFFFF"))
    with col_wm2:
        wm_opacity = st.slider("Độ trong suốt chữ (Opacity):", min_value=0.1, max_value=1.0, value=float(wm_config.get("opacity", 0.6)), step=0.05)
        wm_pos = st.selectbox(
            "Vị trí hiển thị chữ:",
            options=["bottom_right", "bottom_left", "top_right", "top_left", "center"],
            index=["bottom_right", "bottom_left", "top_right", "top_left", "center"].index(wm_config.get("position", "bottom_right")),
            format_func=lambda x: {
                "bottom_right": "Dưới cùng bên phải",
                "bottom_left": "Dưới cùng bên trái",
                "top_right": "Trên cùng bên phải",
                "top_left": "Trên cùng bên trái",
                "center": "Chính giữa ảnh"
            }[x]
        )
        
    if st.button("💾 Lưu Cấu Hình Watermark", use_container_width=True):
        config["watermark"] = {
            "enabled": wm_enabled,
            "text": wm_text,
            "color": wm_color,
            "opacity": wm_opacity,
            "position": wm_pos
        }
        if save_config(config):
            st.toast("Đã cập nhật và lưu cấu hình Watermark thành công!", icon="🎨")
            time.sleep(1)
            st.rerun()

# =============================================================================
# TAB 6: HỆ THỐNG & QUẢN LÝ TÀI KHOẢN
# =============================================================================
with tab_accounts:
    st.subheader("⚙️ Hệ thống, Quản lý Đa tài khoản & Giải CAPTCHA")
    
    # 1. Khóa CAPTCHA Dịch vụ
    st.write("### 🧩 Tích hợp dịch vụ giải CAPTCHA tự động")
    st.write("Sử dụng API 2Captcha để tự động vượt qua Turnstile Cloudflare khi bot chạy chế độ ẩn danh.")
    captcha_api_key = st.text_input(
        "Nhập API Key 2Captcha:",
        value=config.get("captcha_api_key", ""),
        type="password",
        help="Lấy API Key từ trang chủ 2captcha.com để bot tự động thanh toán giải captcha."
    )
    if st.button("💾 Lưu API Key CAPTCHA"):
        config["captcha_api_key"] = captcha_api_key
        if save_config(config):
            st.toast("Đã lưu API Key CAPTCHA thành công!", icon="🧩")
            time.sleep(1)
            st.rerun()
            
    st.write("### 🛡️ Cấu hình Proxy Server (Chế độ Stealth)")
    st.write("Cấu hình HTTP/SOCKS5 Proxy để che dấu địa chỉ IP thực của bạn khi bot đăng tin tự động.")
    proxy_server = st.text_input(
        "Nhập địa chỉ Proxy Server (ví dụ: http://192.168.1.100:8080):",
        value=config.get("proxy", {}).get("server", ""),
        help="Để trống nếu không muốn sử dụng Proxy."
    )
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        proxy_username = st.text_input("Tên đăng nhập Proxy (Username):", value=config.get("proxy", {}).get("username", ""))
    with col_p2:
        proxy_password = st.text_input("Mật khẩu Proxy (Password):", value=config.get("proxy", {}).get("password", ""), type="password")
        
    if st.button("💾 Lưu cấu hình Proxy"):
        if proxy_server:
            config["proxy"] = {
                "server": proxy_server,
                "username": proxy_username,
                "password": proxy_password
            }
        else:
            if "proxy" in config:
                del config["proxy"]
        if save_config(config):
            st.toast("Đã lưu cấu hình Proxy thành công!", icon="🛡️")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    
    # 2. Cấu hình Đa tài khoản (Multi-Account)
    st.write("### 👥 Quản lý Đa tài khoản đăng bài")
    
    site_for_acc = st.selectbox("Chọn nền tảng quản lý tài khoản:", options=list(SUPPORTED_SITES.keys()), format_func=lambda k: SUPPORTED_SITES[k]["name"])
    site_info = SUPPORTED_SITES[site_for_acc]
    
    accounts_dict = config.setdefault("accounts", {})
    site_accounts = accounts_dict.setdefault(site_for_acc, [])
    
    # Hiển thị bảng tài khoản
    if site_accounts:
        st.write(f"Danh sách tài khoản hiện có:")
        df_accs = pd.DataFrame(site_accounts)
        st.dataframe(df_accs, use_container_width=True)
        
        # Xóa tài khoản
        to_del_username = st.selectbox(
            "Chọn tài khoản muốn xóa bỏ:",
            options=[a.get("username") or a.get("email") for a in site_accounts]
        )
        if st.button("🗑️ Xóa tài khoản đã chọn"):
            config["accounts"][site_for_acc] = [a for a in site_accounts if (a.get("username") != to_del_username and a.get("email") != to_del_username)]
            if save_config(config):
                st.toast("Đã xóa tài khoản khỏi danh sách!")
                time.sleep(1)
                st.rerun()
    else:
        st.info("Chưa có tài khoản nào được đăng ký đa tài khoản.")
        
    st.write("➕ **Thêm tài khoản mới:**")
    new_acc_form = {}
    new_acc_form["label"] = st.text_input("Nhãn gợi nhớ tài khoản (ví dụ: Bình Hải Châu 1):", key="new_acc_lbl")
    for field in site_info['fields']:
        if field['type'] == 'password':
            new_acc_form[field['key']] = st.text_input(f"Mật khẩu ({field['label']}):", type="password", key=f"new_acc_{field['key']}")
        else:
            new_acc_form[field['key']] = st.text_input(f"Tài khoản ({field['label']}):", key=f"new_acc_{field['key']}")
            
    if st.button("➕ Thêm tài khoản mới vào hệ thống", use_container_width=True):
        if not new_acc_form.get("username") and not new_acc_form.get("email"):
            st.error("⚠️ Vui lòng điền đầy đủ email hoặc username!")
        else:
            config["accounts"][site_for_acc].append(new_acc_form)
            if save_config(config):
                st.toast("Đã thêm tài khoản mới thành công!", icon="👥")
                time.sleep(1)
                st.rerun()
                
    st.markdown("---")
    
    # 3. Session Muaban.net
    st.write("### 🛡️ Thiết lập Session Cloudflare (Muaban.net)")
    st.caption("Chạy 1 lần để vượt Cloudflare của muaban.net. Session sẽ được lưu vào disk.")
    session_dir = os.path.join(BOT_DIR, "browser_sessions")
    session_exists = os.path.exists(session_dir) and len(os.listdir(session_dir)) > 0 if os.path.exists(session_dir) else False
    if session_exists:
        st.success("✅ Session muaban đã được lưu sẵn")
    else:
        st.warning("⚠️ Chưa có session - cần thiết lập lần đầu")
    if st.button("🔑 Thiết lập Session Muaban.net", use_container_width=True):
        with st.spinner("Đang mở trình duyệt để thiết lập session..."):
            try:
                import subprocess
                subprocess.Popen(
                    ["../venv/bin/python3", "scratch/setup_muaban_session.py"],
                    cwd=BOT_DIR
                )
                st.info("🌐 Đã mở trình duyệt. Hãy:\n1. Chờ Cloudflare xác minh tự động\n2. Đăng nhập nếu cần\n3. Script sẽ tự đóng sau khi lưu session")
            except Exception as e:
                st.error(f"Lỗi: {e}")
                
    st.write("### 🛡️ Đăng nhập thủ công các trang còn lại (Bypass CAPTCHA)")
    st.caption("Nếu các trang DatViet24h, RaoVat247, NhaDat24h yêu cầu CAPTCHA hoặc gặp Cloudflare, bạn hãy click nút bên dưới để mở trình duyệt Chrome chứa session của bot và đăng nhập thủ công 1 lần duy nhất.")
    if st.button("🌐 Mở Trình duyệt Đăng nhập thủ công", use_container_width=True):
        with st.spinner("Đang mở trình duyệt..."):
            try:
                import subprocess
                subprocess.Popen(
                    ["../venv/bin/python3", "scratch/open_browser_for_manual_login.py"],
                    cwd=BOT_DIR
                )
                st.info("🌐 Đã mở trình duyệt Chrome. Hãy truy cập trang web mong muốn (ví dụ: datviet24h.com.vn, raovat247.net), tự đăng nhập và giải CAPTCHA, sau đó ĐÓNG trình duyệt để lưu lại session.")
            except Exception as e:
                st.error(f"Lỗi: {e}")

# =============================================================================
# TAB 7: LỊCH SỬ CHẠY BOT
# =============================================================================
with tab_history:
    st.subheader("📜 Lịch sử chạy Bot đăng bài")
    st.write("Đây là dữ liệu lịch sử hoạt động được lưu lại sau mỗi lần bot tự động đăng tin (cả thành công và thất bại).")
    
    if not posted_history:
        st.info("Chưa có lịch sử đăng bài nào được lưu lại.")
    else:
        # Chuyển đổi thành Pandas DataFrame để hiển thị đẹp mắt
        df_hist = pd.DataFrame(posted_history)
        # Sắp xếp theo mốc thời gian đăng mới nhất lên đầu
        if 'posted_at' in df_hist.columns:
            df_hist = df_hist.sort_values(by='posted_at', ascending=False)
            
        st.dataframe(
            df_hist,
            column_config={
                "title": "Tiêu đề bài viết",
                "area": "Diện tích (m²)",
                "source_url": st.column_config.LinkColumn("Đường dẫn gốc tòa nhà"),
                "posted_at": "Mốc thời gian chạy",
                "status": "Trạng thái",
                "channels": "Kênh thành công",
                "log_file": "Tên file log"
            },
            use_container_width=True
        )
        
        # Xem log hoạt động chi tiết
        st.markdown("---")
        st.subheader("📟 Xem lại Nhật ký Hoạt động Chi tiết (Past Logs)")
        st.caption("Chọn một lượt chạy dưới đây để xem lại toàn bộ log hoạt động chi tiết của trình duyệt Playwright:")
        
        log_options = [
            item for item in posted_history 
            if isinstance(item, dict) and item.get("log_file")
        ]
        log_options = sorted(log_options, key=lambda x: x.get("posted_at", ""), reverse=True)
        
        if not log_options:
            st.info("Chưa có lượt chạy nào được ghi log.")
        else:
            log_labels = [
                f"[{item.get('posted_at')}] ({item.get('status')}) - {item.get('title')[:60]}..."
                for item in log_options
            ]
            
            selected_log_idx = st.selectbox(
                "Chọn lượt chạy để xem log:",
                options=range(len(log_options)),
                format_func=lambda idx: log_labels[idx]
            )
            
            selected_item = log_options[selected_log_idx]
            log_file_path = os.path.join(BOT_DIR, "logs", selected_item.get("log_file"))
            
            if os.path.exists(log_file_path):
                # Hiển thị nút xem screenshot hiện tại của các kênh này
                channels_str = selected_item.get("channels", "")
                if channels_str and channels_str != "Không có":
                    hist_channels = [c.strip() for c in channels_str.split(",")]
                    # Lấy tất cả screenshot hiện có cho các kênh này (không giới hạn thời gian)
                    existing_screenshots = get_recent_screenshots(hist_channels, max_age_secs=3600*24*365)
                    if existing_screenshots:
                        st.write("📸 **Ảnh chụp màn hình hiện tại trên đĩa của các kênh này:**")
                        for site_key in hist_channels:
                            clean_key = site_key.replace(".vn", "").replace(".com.vn", "").replace(".com", "").replace(".net", "").replace(".", "_")
                            site_screenshots = [p for p in existing_screenshots if clean_key in os.path.basename(p).lower()]
                            if site_screenshots:
                                st.write(f"**{SUPPORTED_SITES.get(site_key, {}).get('name', site_key)}**:")
                                cols = st.columns(len(site_screenshots))
                                for idx, img_path in enumerate(site_screenshots):
                                    name = os.path.basename(img_path)
                                    label = "Đăng nhập OK" if "login_ok" in name else "Kết quả đăng" if "post_done" in name or "after_submit" in name else "Form đã điền" if "filled" in name else "Lỗi" if "error" in name or "fail" in name else name
                                    with cols[idx]:
                                        if st.button(f"🔍 Xem {label}", key=f"btn_hist_img_{name}_{idx}_{site_key}"):
                                            show_screenshot_dialog(f"Ảnh hiện tại: {name}", [img_path])
                
                try:
                    with open(log_file_path, "r", encoding="utf-8") as lf:
                        log_content = lf.read()
                    st.code(log_content, language="bash")
                except Exception as read_err:
                    st.error(f"Lỗi đọc file log: {read_err}")
            else:
                st.warning("⚠️ Không tìm thấy file log tương ứng trên hệ thống.")
        
        # Nút xóa lịch sử có cảnh báo
        st.markdown("---")
        st.subheader("🗑️ Quản trị dữ liệu (Hard Reset)")
        col_del1, col_del2 = st.columns([1, 2])
        with col_del1:
            confirm_del = st.checkbox("Tôi chắc chắn muốn Hard Reset toàn bộ lịch sử đăng bài", value=False)
        with col_del2:
            if st.button("⚡ HARD RESET LỊCH SỬ & ĐĂNG LẠI TỪ ĐẦU", type="primary", disabled=not confirm_del, use_container_width=True):
                # Xóa toàn bộ file trong thư mục logs
                logs_dir = os.path.join(BOT_DIR, "logs")
                deleted_logs_count = 0
                if os.path.exists(logs_dir):
                    for f in os.listdir(logs_dir):
                        file_path = os.path.join(logs_dir, f)
                        if os.path.isfile(file_path):
                            try:
                                os.remove(file_path)
                                deleted_logs_count += 1
                            except Exception:
                                pass
                if save_posted_history([]):
                    st.success(f"Đã thực hiện Hard Reset thành công! Đã xóa sạch lịch sử và {deleted_logs_count} tệp nhật ký chi tiết.")
                    time.sleep(1.5)
                    st.rerun()
