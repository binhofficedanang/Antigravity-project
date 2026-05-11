# Task Checklist: Analyze nhadat24h.net

- [x] Analyze listing detail page fields
- [x] Identify categories and subcategories
- [x] Find "Đăng tin" page and posting form fields
- [x] Find registration/login URLs
- [x] Document findings for Google Sheets structure

## Findings for nhadat24h.net

### 1. Registration/Login URLs
- **Login/Register landing page**: `https://nhadat24h.net/DKTV-DT`
- **Registration Form Fields**:
    - Full Name (`txtHT`)
    - Phone Number (`Mobile`)
    - Email (`txtEmail`)
    - Password (`txtMatKhau`)
    - User Type (Individual/Broker)
    - Gender
    - Province/City
    - Address

### 2. Posting Form Fields (Reconstructed from detail page and guide)
- **Essential**: Title (40-80 chars), Category (Bán/Thuê), Property Type, Location (City, District, Ward, Street), Price, Area, Description, Images.
- **Detailed**: Legal Status, Bedrooms, Bathrooms, Floors, Direction, Road Width, Frontage.
- **Contact**: Name, Phone (defaults to profile).

### 3. Categories and Subcategories
- **Main**: Nhà đất bán (Sale), Nhà đất cho thuê (Rent).
- **Subcategories**: Căn hộ chung cư, Đất nền dự án, Nhà đất thổ cư, Nhà biệt thự, Nhà mặt phố, Nhà trọ, Nhà xưởng, Văn phòng, v.v.

### 4. Recommended Google Sheets Structure
Columns: `Tiêu đề`, `Loại tin`, `Loại BĐS`, `Tỉnh/Thành`, `Quận/Huyện`, `Phường/Xã`, `Địa chỉ`, `Giá`, `Đơn vị giá`, `Diện tích`, `Pháp lý`, `Số phòng ngủ`, `Số phòng vệ sinh`, `Số tầng`, `Hướng`, `Đường vào`, `Mặt tiền`, `Nội dung mô tả`, `Link ảnh (cách nhau bởi dấu phẩy)`, `Tên liên hệ`, `Số điện thoại`.
