# BẢNG CHECKLIST PHÁT HÀNH WINDOWS PRODUCTION ALPHA
## PHÁ GIỚI GIẢ: HỒI 1 — HÀN PHONG QUYẾT ĐỊA (v0.10.0-alpha)

Tài liệu hướng dẫn nghiệm thu, cấu hình và vận hành bản phát hành độc lập **Windows Production Alpha** dành cho người chơi trải nghiệm và đội ngũ kiểm thử chất lượng (QA).

---

## 1. TỔNG QUAN BẢN PHÁT HÀNH (RELEASE OVERVIEW)

- **Tên trò chơi**: Phá Giới Giả (Breaking The Boundary)
- **Nội dung chương**: Hồi 1 — Hàn Phong Quyết Địa (Chapter 1: Cold Wind Battlefield)
- **Phiên bản**: `v0.10.0-alpha`
- **Engine đồ họa**: Godot 4.7.2 Forward+ (Vulkan 1.4 API)
- **Mô hình phân phối**: Windows Standalone 64-bit tự hành (Godot Self-Contained Mode với cờ `_sc_`)
- **Thư mục phát hành chuẩn**: `build/windows/` (Bao gồm đúng 9 tệp tin hợp lệ theo hợp đồng phát hành)

---

## 2. DANH MỤC TỆP TIN PHÁT HÀNH (PACKAGE INVENTORY)

Toàn bộ gói cài đặt được nén gọn trong thư mục `build/windows/`, không yêu cầu người chơi cài đặt Godot Engine hay bất kỳ dependency nào khác:

| Tên Tệp Tin | Loại / Vai Trò | Chức Năng |
| :--- | :---: | :--- |
| `Xianxia_Battlefield.exe` | Executable (GUI) | Trình khởi chạy game chính thức không kèm cửa sổ dòng lệnh. |
| `Xianxia_Battlefield_console.exe` | Executable (Console) | Trình khởi chạy kèm console log phục vụ gỡ lỗi và telemetry. |
| `Xianxia_Battlefield.pck` | Package Data | Toàn bộ tài nguyên đã biên dịch nhị phân (scene, script, shader, texture). |
| `Launch_Player.bat` | Batch Launcher | Phím tắt khởi động nhanh cho người chơi phổ thông. |
| `Launch_QA.bat` | Batch Launcher | Khởi động kèm cờ kiểm thử `--qa-mode` tự động. |
| `Run_Smoke_Test.bat` | Batch Launcher | Thực hiện smoke test nhanh kiểm tra tính toàn vẹn của gói build. |
| `README.md` | Tài liệu | Hướng dẫn khởi động nhanh và lưu ý phần cứng. |
| `RELEASE_MANIFEST.json` | Manifest Máy | Danh mục kích thước và mã băm SHA256 bitwise của toàn bộ package. |
| `RELEASE_MANIFEST.md` | Manifest Người | Báo cáo danh mục phát hành và thông số kỹ thuật chi tiết. |

---

## 3. YÊU CẦU HỆ THỐNG & KHỞI CHẠY SẠCH (CLEAN-ROOM RUN)

### A. Cấu Hình Phần Cứng Khuyến Nghị
- **Hệ điều hành**: Windows 10 / Windows 11 (64-bit).
- **Bộ xử lý (CPU)**: Intel Core i5 / AMD Ryzen 5 thế hệ 8 trở lên.
- **Card đồ họa (GPU)**: Hỗ trợ phần cứng Vulkan 1.2+ (NVIDIA GTX 1060 / AMD RX 580 / RTX Series hoặc tương đương).
- **Bộ nhớ RAM**: Tối thiểu 4 GB RAM trống.
- **Dung lượng ổ đĩa**: ~150 MB trống.

### B. Tiêu Chuẩn Khởi Động Sạch (Clean-Room Standard)
- Người chơi có thể sao chép toàn bộ thư mục `build/windows/` sang bất kỳ ổ đĩa hoặc máy tính nào.
- Nhờ có cờ `_sc_` (Self-Contained), game tự động tạo thư mục lưu trữ cục bộ `user://` ngay bên trong thư mục game, **tuyệt đối không ghi đè** hay rò rỉ dữ liệu sang thư mục hệ thống của Windows (`%APPDATA%`).
- Không phụ thuộc vào đường dẫn của máy phát triển (`d:\Vibe Code\Antigravity`), không yêu cầu quyền Administrator.

---

## 4. HƯỚNG DẪN ĐIỀU KHIỂN & BẢNG THIẾT LẬP (CONTROLS & SETTINGS)

### A. Sơ Đồ Phím Bàn Phím & Thao Tác Chuột

| Thao Tác | Phím Tắt Bàn Phím | Thao Tác Chuột | Mô Tả Chức Năng |
| :--- | :---: | :---: | :--- |
| **Chọn Binh Sĩ** | `[Tab]` / `[1-4]` | Click Chuột Trái (LMB) | Chọn một kiếm sĩ hoặc cung thủ tiên phong để điều động. |
| **Bố Trí Đội Hình** | `[WASD]` / Phím Mũi Tên | Kéo Chuột (Drag LMB) | Di chuyển binh sĩ vào tâm tử địa ($R \le 3.5\text{m}$) quanh điểm va chạm. |
| **Bỏ Chọn Binh Sĩ** | `[Esc]` | Click Chuột Phải (RMB) | Hủy chọn binh sĩ hiện tại, hoàn tất vị trí đứng. |
| **Xuất Kích / Xác Nhận** | `[Space]` / `[Enter]` | Click `[Xuất Kích]` | Xác nhận đội hình và tiến hành giao tranh nghênh đao. |
| **Tạm Dừng / Tiếp Tục** | `[P]` | Click `[\|\|] (P)` | Tạm dừng trận chiến để quan sát sa bàn. |
| **Thiết Lập / Phím Tắt** | `[O]` | Click `[O] Thiết Lập` | Mở bảng Cài đặt & Hướng dẫn điều khiển Alpha. |
| **Bật / Tắt Âm Toàn Cục** | `[M]` | Click `[M] Âm: BẬT/TẮT` | **Priority 0**: Luôn hoạt động ở mọi màn hình và mọi modal. |
| **Bật / Tắt Giảm Rung** | `[N]` | Click `[N] Giảm rung` | Tắt hiệu ứng rung màn hình khi trảm kích va chạm. |
| **Hướng Dẫn Tân Thủ** | `[F2]` | Click `[?] (F2)` | Mở lại hướng dẫn 3 bước bày trận tử địa. |
| **Chọn Nhanh Ải** | `[1]`, `[2]`, `[3]` | Click Tab Ải | Chuyển đổi giữa các Ải đã mở khóa trong Hồi 1. |
| **Quay Về / Thoát** | `[Esc]` | Click `[Tiêu Đề]` / `[Esc]` | Quay lại màn hình trước hoặc hiển thị hộp thoại thoát game. |

### B. Bảng Thiết Lập & Quản Lý Dữ Liệu Lưu (Settings Modal)
- Người chơi có thể nhấn `[O]` hoặc click nút `[O] Thiết Lập / Phím Tắt` tại màn hình Title hoặc trong trận để mở bảng cài đặt.
- **Xác nhận xóa bản lưu 2 bước (Two-Step Reset Confirmation)**:
  - *Bước 1*: Bấm nút `[ Xóa Toàn Bộ Bản Lưu / Chơi Lại Từ Đầu ]` $\to$ Nút chuyển sang viền đỏ cảnh báo: `[ ⚠ BẤM LẦN NỮA ĐỂ XÁC NHẬN XÓA TOÀN BỘ BẢN LƯU! ]`.
  - *Bước 2*: Bấm lần thứ hai $\to$ Game xóa vĩnh viễn tệp save đĩa, hoàn nguyên trạng thái chiến dịch về đầu Ải 1, đặt lại điểm về 0, nhưng **vẫn bảo toàn nguyên vẹn** cài đặt Âm thanh (`Mute`) và Giảm rung (`Reduce Motion`) của người chơi.
  - Nhấn `[Esc]` hoặc click ra ngoài sẽ hủy bỏ bước xác nhận, tránh việc xóa nhầm.

---

## 5. MẠCH TRUYỆN HỒI 1 & QUY TẮC MỞ KHÓA (CHAPTER 1 CAMPAIGN FLOW)

### A. Tuyến Tính 3 Ải Chiến Thuật
1. **Ải 1: Tiên Trâm Liệt Địa** (`mission_01_vanguard`):
   - *Ngưỡng qua ải*: Đón đỡ ít nhất **3 lính tiên phong** vào tâm tử địa ($R \le 3.5\text{m}$).
   - *Khởi đầu*: Đã có sẵn 2 lính lõi; người chơi chỉ cần điều thêm 1 kiếm sĩ vào tâm chấn.
   - *Điểm chuẩn Hạng S*: 2,050 Điểm | 3/3 ★ Tinh thông (11 lính sống sót).
2. **Ải 2: Thiết Quân Phá Trận** (`mission_02_iron_bulwark`):
   - *Điều kiện mở*: Phải đạt chiến thắng `CLEARED` ở Ải 1.
   - *Ngưỡng qua ải*: Đón đỡ ít nhất **4 lính tiên phong** vào tâm tử địa ($R \le 3.5\text{m}$).
   - *Khởi đầu*: Đã có 3 lính cắm chốt; cần điều thêm 1 chiến sĩ kiên cường hợp lực.
   - *Điểm chuẩn Hạng S*: 2,100 Điểm | 3/3 ★ Tinh thông (10 lính sống sót).
3. **Ải 3: Tránh Né Phản Kích** (`mission_03_flank_assault`):
   - *Điều kiện mở*: Phải đạt chiến thắng `CLEARED` ở Ải 2.
   - *Ngưỡng qua ải*: Đón đỡ ít nhất **2 dũng sĩ cảm tử** vào tâm tử địa ($R \le 3.5\text{m}$).
   - *Khởi đầu*: Toàn quân ban đầu né tránh ra ngoài; chỉ huy phải dũng cảm chỉ định 2 lính xông pha đánh lạc hướng.
   - *Điểm chuẩn Hạng S*: 2,000 Điểm | 3/3 ★ Tinh thông (12 lính sống sót).

### B. Bảng Tổng Kết Hồi 1 (Chapter 1 Summary)
- Xuất hiện trang trọng ngay sau khi hoàn thành Ải 3.
- Tổng kết toàn bộ chiến dịch Hồi 1:
  - **Tổng Điểm Toàn Thắng**: **6,150 Điểm (Hạng S)** ($2,050 + 2,100 + 2,000 = 6,150$).
  - **Sao Tinh Thông Toàn Bích**: **9/9 ★ `[★ TOÀN BÍCH]`**.
  - Cung cấp 3 nút điều hướng: `[1] Đánh Lại Hồi 1`, `[C] Khiêu Chiến Thử Thách`, `[Esc] Màn Hình Chính`.

### C. Cách Ly Nhánh Thử Thách (Challenge Hub Isolation)
- Nhánh Khiêu Chiến Thử Thách (Ải 4–6 / Phase 9A–9H) hoàn toàn tách biệt với Chapter 1.
- Điểm số của Thử Thách (tối đa 18 sao) không tính vào tổng điểm Chapter 1 (tối đa 9 sao).

---

## 6. TIÊU CHUẨN ĐỒ HỌA & NGHỆ THUẬT (ART DIRECTION ALIGNMENT)

- **Góc Nhìn Sa Bàn Diorama**: Camera cố định tiêu cự 70mm, FOV `19.455°`, góc nhìn chúc xuống `62.0°` (pitch `-28.0°`), tọa độ `(1.0, 22.3, 40.8)`.
- **Tương Phản Màu Sắc**: Sa trường tuyết trắng và vách đá xanh xám làm nền; Binh sĩ nổi bật với sắc Xanh Ngọc Bích / Đỏ Son; Đại Đao Tướng Quân uy dũng với giáp đen than và hoa văn Vàng Kim.
- **Hiệu Ứng Kiếm Khí Thư Pháp**: Dải đao khí phát quang rực rỡ mô phỏng nét bút lông cuộn trào mềm mại nhưng sắc bén.
- **Nhận Diện Phi Màu (Non-Color Reliance)**: Toàn bộ trạng thái hiển thị rõ nhãn chữ: `[🔒 KHÓA]`, `[✓ QUA ẢI]`, `[★ ĐANG ĐÁNH]`, `[○ SẴN SÀNG]`, `[★ TOÀN BÍCH]`.
- **Không Clipping**: Toàn bộ UI giữ khoảng cách an toàn, không che lấp Boss khổng lồ và tâm va chạm tại `(1.7500, 0.2000, -0.4500)`.

---

## 7. HỆ THỐNG ÂM THANH THỦ TỤC FAIL-SOFT (PROCEDURAL AUDIO)

- 100% âm thanh được tổng hợp trực tiếp trong RAM bằng thuật toán PCM 16-bit, không nạp bất kỳ file ngoài nào:
  - `select`: Tone trong trẻo 880 Hz khi chọn quân / click menu.
  - `invalid`: Tone trầm 220 Hz cảnh báo khi thao tác sai vị trí hoặc chọn ải khóa.
  - `anticipation`: Sweep tần số 120–220 Hz mô phỏng đao khí vận chuyển.
  - `impact`: Kick noise 80 Hz mô phỏng tiếng va chấn long trời lở đất tại Frame 5.
  - `hitstop`: Tone ngân 440 Hz giữ thế đình trệ tại Frame 7–8.
  - `victory`: Hợp âm C5–E5 khải hoàn khi chiến thắng.
  - `defeat`: Hợp âm A3–C4 trầm buồn khi thất bại.
  - `unlock`: Hợp âm ba thăng tiến C major (`[523, 659, 784]` Hz) khi mở khóa ải mới.
  - `chapter_complete`: Hợp âm khải hoàn đại thắng (`[523, 659, 784, 1046]` Hz) khi hoàn tất Hồi 1.
- **Fail-Soft An Toàn Tuyệt Đối**: Tự động bỏ qua không gây crash nếu chạy trên máy không có sound card hoặc môi trường headless CI/CD.

---

## 8. QUY TRÌNH KIỂM THỬ & CHẤP THUẬN PHÁT HÀNH (ACCEPTANCE CRITERIA)

Mọi bản build trước khi gửi cho người chơi phải thỏa mãn các kiểm tra sau:
1. `tools/run_qa_gate.ps1`: Đạt **PASS (12/12 Steps)** với 0 lỗi.
2. `tools/test_cleanroom_release.ps1`: Đạt **PASS** trong thư mục sandbox rỗng.
3. `tools/build_release.ps1 -VerifyOnly`: Đạt **PASS**, 9 file khớp SHA256 với manifest.
4. Process Hygiene: **0 orphan Godot processes** sau khi đóng ứng dụng.
5. Toàn bộ các file Blender `.blend` giữ nguyên vẹn 100% mã băm SHA256.
