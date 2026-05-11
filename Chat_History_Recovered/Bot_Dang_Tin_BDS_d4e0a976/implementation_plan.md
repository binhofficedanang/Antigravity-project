# Bot Đăng Tin BĐS — Kế Hoạch Triển Khai (Đã rà soát)

## Kết quả rà soát chính sách miễn phí

> [!WARNING]
> Sau khi rà soát kỹ, tôi đã **loại bỏ chothuenha.com.vn** và **dothi.net** khỏi Nhóm A vì chúng yêu cầu trả phí hoặc không rõ chính sách free.

| # | Trang Web | Miễn phí? | Giới hạn | Đánh giá spam | Ghi chú |
|---|---|---|---|---|---|
| 1 | **bds123.vn** | ✅ Có gói free | Tin thường miễn phí, VIP trả phí | 🟢🟢🟢🟢🟢 | Đăng SĐT, có mục VP riêng |
| 2 | **alonhadat.com.vn** | ✅ Miễn phí | **2 tin/ngày** (sau xác thực) | 🟢🟢🟢🟢 | Lâu đời, cần xác thực tài khoản. 2 tin/ngày → cần đa tài khoản |
| 3 | **nhadat24h.net** | ✅ Có gói free | Một số tin miễn phí | 🟢🟢🟢🟢 | Đăng ký bằng SĐT/Email |
| 4 | **rongbay.com** | ✅ Miễn phí cơ bản | Tin thường free, VIP trả phí | 🟢🟢🟢🟢 | Rao vặt lâu đời, ít kiểm duyệt |
| 5 | **muaban.net** | ✅ Miễn phí | **10 tin free**, khóa nếu >10 tin/7 ngày | 🟢🟢🟢 | Đăng nhập FB/Google/Zalo |
| ~~6~~ | ~~chothuenha.com.vn~~ | ❌ **TRẢ PHÍ** | Cần mua gói tin | ~~Loại~~ | Cần mua tin Siêu VIP/VIP/Thường |
| ~~7~~ | ~~dothi.net~~ | ⚠️ Không rõ | Cần kiểm tra thêm | ~~Loại~~ | Không xác minh được chính sách free |

---

## Nhóm A cuối cùng — 5 trang để code bot

### 1. bds123.vn ⭐⭐⭐⭐⭐
- **Đăng ký**: SĐT → `/dang-ky.html`
- **Đăng tin**: `/quan-ly/dang-tin-moi.html`
- **Danh mục VP**: Cho thuê văn phòng, Cho thuê mặt bằng
- **Ưu điểm**: Giao diện form hiện đại, danh mục VP theo tỉnh thành

### 2. alonhadat.com.vn ⭐⭐⭐⭐
- **Đăng ký**: Trên trang
- **Đăng tin**: `/dang-tin-nha-dat.html`
- **Giới hạn**: 2 tin/ngày/tài khoản → **cần 5+ tài khoản để spam 10 tin/ngày**
- **Danh mục VP**: Cho thuê văn phòng, mặt bằng, kho xưởng

### 3. nhadat24h.net ⭐⭐⭐⭐
- **Đăng ký**: SĐT/Email → `/DKTV-DT`
- **Đăng tin**: Nút "ĐĂNG TIN" góc phải
- **Danh mục VP**: Cho thuê VP trong mục Cho thuê

### 4. rongbay.com ⭐⭐⭐
- **Đăng ký**: Trên trang
- **Đăng tin**: Rao vặt → BĐS → Cho thuê VP
- **Ưu điểm**: Ít kiểm duyệt nhất, phù hợp spam

### 5. muaban.net ⭐⭐⭐
- **Đăng ký**: FB/Google/Zalo
- **Đăng tin**: Chọn danh mục → điền thông tin
- **Giới hạn**: 10 tin free, khóa nếu >10 tin/7 ngày → cần đa tài khoản

---

## Kiến trúc Code

```
real_estate_bot/
├── requirements.txt          # playwright, pandas, openpyxl
├── config.py                 # Google Sheets URL, cấu hình chung
├── data_loader.py            # Đọc dữ liệu từ Google Sheets / Excel
├── accounts.json             # Danh sách tài khoản cho từng trang
├── base_bot.py               # Class BaseBot (mở browser, login, upload ảnh)
├── title_spinner.py          # Module spin tiêu đề tự động
├── main.py                   # File chạy chính
├── images/                   # Thư mục chứa ảnh BĐS
└── sites/
    ├── __init__.py
    ├── bds123.py             # Bot cho bds123.vn
    ├── alonhadat.py          # Bot cho alonhadat.com.vn
    ├── nhadat24h.py          # Bot cho nhadat24h.net
    ├── rongbay.py            # Bot cho rongbay.com
    └── muaban.py             # Bot cho muaban.net
```

## Cấu trúc Google Sheets

### Sheet `accounts`
| email | password | phone | contact_name | site |
|---|---|---|---|---|
| acc1@gmail.com | pass123 | 0912xxx | Nguyễn A | bds123 |
| acc2@gmail.com | pass456 | 0913xxx | Trần B | alonhadat |

### Sheet `listings`
| title | listing_type | property_type | price | price_unit | area | province | district | ward | street | description | images | account_email | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cho thuê VP 50m2 Q1 | cho_thue | van_phong | 15 | trieu | 50 | HCM | Quận 1 | P. Bến Nghé | Lê Lợi | Mô tả... | img1.jpg,img2.jpg | acc1@gmail.com | pending |

---

## Verification Plan

### Giai đoạn 1: Khung bot cơ bản
- [ ] Cài Playwright, chạy mở trình duyệt thành công
- [ ] Đọc dữ liệu từ Google Sheets / Excel
- [ ] Module spin tiêu đề hoạt động

### Giai đoạn 2: Bot cho từng trang (test 1 tin)
- [ ] bds123.vn: Đăng nhập → điền form → dừng trước nút Submit
- [ ] alonhadat.com.vn: Tương tự
- [ ] nhadat24h.net: Tương tự
- [ ] rongbay.com: Tương tự
- [ ] muaban.net: Tương tự

### Giai đoạn 3: Chạy thật
- [ ] Bot đăng 1 tin thật trên mỗi trang
- [ ] Cập nhật status trên Google Sheets
- [ ] Chạy loop cho nhiều tin
