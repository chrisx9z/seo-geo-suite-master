# CẨM NANG NGƯỜI CHƠI & HƯỚNG DẪN TÂN THỦ (PLAYER ONBOARDING)
## Phá Giới Giả: Chiến Địa Tiên Hiệp — Vertical Slice UX Standard

---

## 1. TỔNG QUAN & NGUYÊN LÝ THIẾT KẾ

Hệ thống Hướng Dẫn Tân Thủ (*Tactical Onboarding*) trong **Phá Giới Giả: Chiến Địa Tiên Hiệp** được xây dựng nhằm giúp người chơi mới nhanh chóng nắm bắt bản chất của lối chơi sa bàn chiến thuật thu nhỏ (*diorama tactical battlefield*) ngay trong lần đầu trải nghiệm, đồng thời tôn trọng tuyệt đối thời gian của người chơi cũ thông qua cơ chế bỏ qua tức thì và xem lại theo yêu cầu.

### Nguyên Tắc Cốt Lõi:
1. **Dạy đúng 3 hành động cốt lõi**: Chọn lính $\to$ Đưa lính vào vùng tử địa $\to$ Xuất kích nghênh đao.
2. **Không làm nghẽn người chơi cũ (Zero Friction)**: Chỉ mở tự động ở lần đầu vào Ải 1 khi chưa hoàn thành onboarding; cho phép bỏ qua trong 1 frame bằng phím `[Esc]`.
3. **Xem lại linh hoạt (On-Demand Replay)**: Bất kỳ lúc nào ở giai đoạn Bày Trận, người chơi đều có thể mở lại cẩm nang qua phím `[F2]` hoặc nút `[?]`.
4. **Song hành điều khiển 100% (Input Parity)**: Mọi thao tác bàn phím đều có nút chuột tương ứng trên màn hình.
5. **Cách ly chân lý chiến đấu (Preview Isolation)**: Các chỉ báo tầm đánh và dự kiến số lính chỉ mang tính chất cố vấn trực quan (Advisory UX), không làm sai lệch hay can thiệp vào bộ quy tắc tính toán chiến đấu thực tế (`CombatRules.gd`).

---

## 2. CHUỖI 3 BƯỚC HƯỚNG DẪN TÂN THỦ (3-STEP ONBOARDING SEQUENCE)

Modal hướng dẫn tân thủ xuất hiện dưới dạng bảng ngọc bích - kính than tối trang nhã ($460 \times 240\text{px}$) tại tâm màn hình khi bước vào Ải 1:

```
+-------------------------------------------------------------+
|                     [1/3] CHỌN BINH SĨ                      |
|                                                             |
|  Click chuột trái (LMB) hoặc nhấn [Tab] để chọn một kiếm sĩ |
|                  hoặc cung thủ tiên phong.                  |
|                                                             |
|  +-------------------------------------------------------+  |
|  | [LMB / Tab] Chọn lính   |   [1 - 4] Chọn nhanh đội    |  |
|  +-------------------------------------------------------+  |
|                                                             |
|         [ Bỏ Qua (Esc) ]         [ Tiếp (Space / Enter) ]   |
+-------------------------------------------------------------+
```

### Bước 1: [1/3] CHỌN BINH SĨ (`step_select`)
- **Mục tiêu**: Hướng dẫn người chơi cách tương tác và lựa chọn đơn vị trên sa bàn.
- **Lời dẫn**: *"Click chuột trái (LMB) hoặc nhấn [Tab] để chọn một kiếm sĩ hoặc cung thủ tiên phong."*
- **Phím tắt hỗ trợ**: `[LMB]` (Click trực tiếp), `[Tab]` (Duyệt tuần tự 14 binh sĩ), `[1 - 4]` (Chọn nhanh phân đội).
- **Hành động tiếp theo**: Nhấn `[Space]` / `[Enter]` hoặc click `[Tiếp]` để chuyển sang Bước 2.

### Bước 2: [2/3] BỐ TRÍ TỬ ĐỊA (`step_position`)
- **Mục tiêu**: Giải thích cơ chế đón đỡ đao kình — chìa khóa sống còn của chiến thuật.
- **Lời dẫn**: *"Kéo chuột hoặc dùng phím [WASD] để điều chuyển lính vào tâm trảm kích (vòng tròn bán kính 3.5m)."*
- **Phím tắt hỗ trợ**: `[WASD]` hoặc `[Mũi tên]` (Dịch chuyển bước 0.25m), `[Kéo chuột / Drag]` (Di chuyển tự do trên mặt phẳng đất), `[C]` (Đặt lại vị trí ban đầu).
- **Hành động tiếp theo**: Nhấn `[Space]` / `[Enter]` hoặc click `[Tiếp]` để chuyển sang Bước 3.

### Bước 3: [3/3] XUẤT KÍCH (`step_strike`)
- **Mục tiêu**: Kích hoạt giao tranh và chiêm ngưỡng chu kỳ trảm kích 24 frame.
- **Lời dẫn**: *"Sau khi hoàn tất bố trận, nhấn [Space] / [Enter] hoặc click [Xuất Kích] để tham chiến hóa giải đao kình!"*
- **Phím tắt hỗ trợ**: `[Space] / [Enter]` (Xuất kích), `[P]` (Tạm dừng trận đấu), `[R]` (Đặt lại ải), `[Esc]` (Đổi ải).
- **Hành động hoàn tất**: Nhấn `[Space]` / `[Enter]` hoặc click `[Đã Hiểu]` để đóng modal, tự động lưu cờ `onboarding_completed = true` vào đĩa và mở khóa sa bàn để người chơi tự do điều binh.

---

## 3. BẢNG ĐỒNG BỘ ĐIỀU KHIỂN (INPUT PARITY MATRIX)

Mọi hành động trong trò chơi đều tuân thủ nguyên tắc song hành: Người chơi có thể sử dụng hoàn toàn bàn phím, hoàn toàn chuột, hoặc kết hợp cả hai.

| Hành Động | Phím Tắt Bàn Phím | Thao Tác Chuột | Giao Diện Trực Quan Tương Ứng |
| :--- | :---: | :---: | :--- |
| **Bắt Đầu / Tiếp Tục** | `[Space]` / `[Enter]` | Click chuột trái | Nút `[ Bắt Đầu Nhiệm Vụ ]` / `[ Tiếp Tục Chiến Dịch ]` |
| **Chọn Binh Sĩ** | `[Tab]` (Tuần tự) | Click vào lính | Khung định vị 4 góc vàng kim quanh chân lính |
| **Điều Động Binh Sĩ** | `[WASD]` / Phím Mũi Tên | Kéo thả chuột trái | Đơn vị di chuyển thời gian thực trên mặt phẳng $Y=0$ |
| **Xác Nhận Đội Hình Tạm**| `[Space]` / `[Enter]` | Click ngoài lính | Bỏ chọn đơn vị, lưu vị trí đã điều chỉnh |
| **Hủy Đội Hình Tạm** | `[Esc]` | Click nút Hủy | Hoàn nguyên lính về vị trí xác nhận gần nhất |
| **Xuất Kích Nghênh Chiến**| `[Space]` / `[Enter]` | Click nút Xuất Kích | Nút `[ Xuất Kích (Space) ]` góc dưới màn hình |
| **Tạm Dừng Trận Đấu** | `[P]` | Click nút Pause | Nút `[P] Tạm Dừng` góc trên bên phải |
| **Bật / Tắt Âm Thanh** | `[M]` (Toàn cục) | Click nút Mute | Nút `[M] Âm: BẬT / TẮT` góc trên bên phải |
| **Giảm Rung Màn Hình** | `[N]` (Toàn cục) | Click nút Giảm Rung | Nút `[N] Giảm rung: BẬT / TẮT` |
| **Xem Lại Hướng Dẫn** | `[F2]` | Click nút Trợ Giúp | Nút `[?] (F2)` trên thanh trạng thái Bày Trận |
| **Đánh Lại (Replay)** | `[1]` | Click nút Đánh Lại | Nút `[1] Đánh Lại` trên màn hình Kết Quả |
| **Sửa Đội Hình (Edit)** | `[2]` | Click nút Sửa | Nút `[2] Sửa Đội Hình` trên màn hình Kết Quả |
| **Đặt Lại Ải (Reset)** | `[3]` | Click nút Đặt Lại | Nút `[3] Đặt Lại Ải` trên màn hình Kết Quả |
| **Ải Kế Tiếp (Next)** | `[Space]` / `[Enter]` | Click nút Kế Tiếp | Nút `[ Tiếp Theo (Space/Enter) ]` |
| **Về Màn Hình Chính** | `[Esc]` | Click nút Tiêu Đề | Nút `[Esc] Màn Hình Chính` trên màn hình Kết Quả |

---

## 4. CƠ CHẾ BỎ QUA & XEM LẠI (SKIP & REPLAY MECHANICS)

### 4.1. Bỏ Qua Tức Thì (Instant Skip)
- Người chơi có thể nhấn `[Esc]` hoặc click `[Bỏ Qua (Esc)]` tại bất kỳ bước nào trong 3 bước.
- Modal đóng ngay lập tức trong 1 frame, không có hiệu ứng chờ gây trì hoãn.
- Trạng thái `onboarding_completed: true` được ghi nhận lập tức vào `CampaignState` và tự động lưu đĩa (`SaveManager`).
- Khi người chơi chơi lại hoặc khởi động lại game, modal Onboarding **sẽ không bao giờ tự động hiện ra nữa**.

### 4.2. Xem Lại Theo Yêu Cầu (On-Demand Replay)
- Nếu người chơi muốn xem lại cơ chế hoặc phím tắt, chỉ cần nhấn phím `[F2]` hoặc click nút `[?]` tại thanh trạng thái Bày Trận.
- Modal Onboarding sẽ mở lại từ Bước 1, cho phép duyệt qua các bước bình thường.
- Vị trí đội hình lính đã dàn trước đó được giữ nguyên vẹn 100%, không bị reset hay xáo trộn.

### 4.3. Tự Động Bỏ Qua Trong Môi Trường CI/CD & Automated Testing
- Khi game chạy với cờ `--headless`, cờ `qa_mode`, biến `is_qa_runner` hoặc chế độ `auto_exit_sec > 0.0`, hệ thống tự động vô hiệu hóa việc mở modal Onboarding.
- Điều này bảo đảm toàn bộ pipeline kiểm thử tự động (continuous integration) chạy mượt mà 100% mà không bị modal chặn luồng input.

---

## 5. HỆ THỐNG PREVIEW BÀY TRẬN & TÁCH BIỆT CHÂN LÝ CHIẾN ĐẤU

### 5.1. Các Thành Phần Trực Quan Hóa (Visual Indicators)
1. **Vòng Tử Địa Sa Trường ($R = 3.5\text{m}$)**:
   - Một đường vòng tròn khép kín được lấy mẫu 36 điểm trong không gian 3D tại độ cao mặt tuyết ($Y = 0.000\text{m}$) quanh tâm trảm kích `(1.7500, 0.2000, -0.4500)`.
   - Vòng tròn được chiếu qua Camera3D sa bàn (ống kính 70mm, góc nhìn chúc 62°) tạo thành một đường elip phối cảnh chuẩn xác trên mặt đất.
   - Màu sắc: Vàng kim thanh lịch (`Color(0.92, 0.82, 0.55, 0.45)`) trong lúc bày trận, chuyển sang Đỏ son va chạm (`Color(0.95, 0.45, 0.35, 0.70)`) tại Frame 5 trảm kích.
2. **Khung Định Vị Đơn Vị (Selection Reticle)**:
   - 4 góc ngắm quanh chân đơn vị được chọn:
     - Màu **Vàng Kim**: Vị trí hợp lệ, bảo đảm khoảng cách Boss $\ge 2.5\text{m}$ và giãn cách lính $\ge 0.8\text{m}$.
     - Màu **Đỏ Son**: Vị trí vi phạm quy tắc (quá gần Boss, chồng lấn đồng đội, hoặc ra ngoài biên sa bàn).
3. **Thanh Chỉ Báo Quân Số Đón Đao (Live Tally Indicator)**:
   - Hiển thị dòng trạng thái thời gian thực trên thanh HUD:  
     `Mục tiêu: Đón đỡ 3 lính lõi | Dự kiến: 2/3 lính lõi [○ CHƯA ĐỦ]` (Màu Vàng)  
     $\to$ Khi người chơi điều chuyển đủ 3 lính vào vòng tử địa:  
     `Mục tiêu: Đón đỡ 3 lính lõi | Dự kiến: 3/3 lính lõi [✓ ĐẠT ĐIỀU KIỆN]` (Màu Ngọc Bích).

### 5.2. Tách Biệt Tuyệt Đối Khỏi Chân Lý Chiến Đấu (Advisory-Only Isolation)
- Toàn bộ các thông số `Dự kiến: X/3 lính lõi` chỉ là phép đo khoảng cách hình học $XZ$ thuần túy trên giao diện người dùng.
- Lớp Preview **hoàn toàn không ghi trạng thái giả**, không trừ máu lính trước giờ G, không can thiệp vào `GameSession` hay bộ chấm điểm `CampaignState`.
- Khi người chơi bấm Xuất Kích, hoạt cảnh diễn ra tuần tự 24 frame, và tại đúng Frame 5, hàm `CombatRules.evaluate_impact()` mới chính thức phân định sát thương, số lính hy sinh và số lính sống sót.

---

## 6. QUY CHUẨN ĐỒ HỌA & ĐỘ PHÂN GIẢI (ART DIRECTION & READABILITY)

- **Tuân thủ Art Direction Bible (`docs/ART_DIRECTION.md`)**:
  - Tông màu nền kính than tối: `Color(0.06, 0.08, 0.10, 0.92)`.
  - Viền ngọc bích phong thủy: `Color(0.35, 0.72, 0.62, 0.85)`.
  - Chữ trắng tuyết tương phản cao: `Color(0.92, 0.94, 0.96, 1.0)`.
  - Điểm nhấn vàng kim hoàng gia: `Color(0.95, 0.85, 0.58, 1.0)`.
- **Ký hiệu hỗ trợ người mù màu (Non-Color Reliance)**:
  - Mọi trạng thái đều có marker dạng chữ đi kèm: `[✓ ĐẠT ĐIỀU KIỆN]`, `[○ CHƯA ĐỦ]`, `[✕ VI PHẠM]`, `[★ ĐANG CHỌN]`.
- **Thích ứng hiển thị 960×540 & 1080p**:
  - Sử dụng cấu hình `window/stretch/mode="viewport"` và `window/stretch/aspect="keep"`.
  - Mọi modal và panel đều nằm gọn trong kích thước $860 \times 465\text{px} \ll 900 \times 520\text{px}$, tuyệt đối không bị tràn viền (clipping) hay che khuất tầm nhìn Boss và sa bàn trung tâm ở cả độ phân giải cơ sở 960×540 lẫn màn hình Full HD 1080p.
