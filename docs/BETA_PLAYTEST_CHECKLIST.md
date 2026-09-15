# BẢNG CHECKLIST BÀN GIAO WINDOWS BETA PLAYTEST CANDIDATE
## PHÁ GIỚI GIẢ: HỒI 1 — HÀN PHONG QUYẾT ĐỊA (`v0.11.0-beta`)

Tài liệu hướng dẫn nghiệm thu, cấu hình và vận hành bản phát hành độc lập **Windows Beta Playtest Candidate** dành cho người chơi trải nghiệm bên ngoài và đội ngũ kiểm thử chất lượng (QA).

---

## 1. TỔNG QUAN BẢN PHÁT HÀNH (RELEASE OVERVIEW)

- **Tên trò chơi**: Phá Giới Giả: Hồi 1 — Hàn Phong Quyết Địa (Beta)
- **Tên quốc tế**: Breaker of Realms: Chapter 1 — Cold Wind Battlefield (Beta)
- **Phiên bản**: `v0.11.0-beta` (Build 2026-09)
- **Engine đồ họa**: Godot 4.7.2 Forward+ (Vulkan 1.4 API)
- **Mô hình phân phối**: Windows Standalone 64-bit tự hành (Godot Self-Contained Mode với cờ `_sc_`)
- **Thư mục phát hành chuẩn**: `build/windows/` (Bao gồm đúng 9 tệp tin hợp lệ theo hợp đồng phát hành)
- **Trọng tâm giai đoạn Beta**: Bàn giao cho người chơi ngoài trải nghiệm độc lập, nắm vững phím điều khiển, cài đặt tùy biến và báo lỗi thủ công mà không cần IDE hay công cụ kỹ thuật.

---

## 2. DANH MỤC TỆP TIN PHÁT HÀNH (PACKAGE INVENTORY)

Toàn bộ gói cài đặt được đóng gói độc lập trong thư mục `build/windows/`, không yêu cầu người chơi cài đặt Godot Engine hay bất kỳ runtime bổ sung nào:

| Tên Tệp Tin | Loại / Vai Trò | Chức Năng Chính |
| :--- | :---: | :--- |
| `Xianxia_Battlefield.exe` | Executable (GUI) | Trình khởi chạy game chính thức dành cho người chơi. |
| `Xianxia_Battlefield_console.exe` | Executable (Console) | Trình khởi chạy kèm console log phục vụ chẩn đoán lỗi chi tiết. |
| `Xianxia_Battlefield.pck` | Package Data | Toàn bộ tài nguyên đã biên dịch nhị phân (scene, script, shader, 3D model). |
| `Launch_Player.bat` | Batch Launcher | Phím tắt khởi động nhanh tiện lợi cho người chơi. |
| `Launch_QA.bat` | Batch Launcher | Khởi động nội bộ kèm cờ chẩn đoán telemetry `--qa-mode`. |
| `Run_Smoke_Test.bat` | Batch Launcher | Bounded smoke test 2 giây kiểm tra nhanh tính toàn vẹn của package. |
| `README.md` | Tài liệu Người Chơi | Hướng dẫn khởi động nhanh, sơ đồ điều khiển và quy trình báo lỗi. |
| `RELEASE_MANIFEST.json` | Manifest Máy | Danh mục kích thước và mã băm SHA256 bitwise của toàn bộ package. |
| `RELEASE_MANIFEST.md` | Manifest Người | Báo cáo danh mục phát hành và thông số kỹ thuật chi tiết. |

---

## 3. YÊU CẦU HỆ THỐNG & KHỞI CHẠY SẠCH (CLEAN-ROOM SANDBOXING)

### A. Cấu Hình Phần Cứng Yêu Cầu
- **Hệ điều hành**: Windows 10 / Windows 11 (64-bit).
- **Bộ xử lý (CPU)**: Intel Core i5 / AMD Ryzen 5 thế hệ 8 trở lên.
- **Card đồ họa (GPU)**: Hỗ trợ phần cứng Vulkan 1.2+ (NVIDIA GeForce GTX 1060 / AMD Radeon RX 580 trở lên). Đã kiểm chứng tối ưu trên NVIDIA GeForce RTX 5070 Ti (Vulkan 1.4.341).
- **Bộ nhớ RAM**: Tối thiểu 4 GB RAM trống.
- **Dung lượng ổ đĩa**: 500 MB dung lượng trống.
- **Độ phân giải hiển thị**: Cửa sổ mặc định $1280 \times 720$ (Độ phân giải ảo nội bộ: $960 \times 540$, tỷ lệ 16:9). Hỗ trợ toàn màn hình (`Alt+Enter`).

### B. Tiêu Chuẩn Khởi Động Sạch (Clean-Room Standard)
- Người chơi có thể sao chép toàn bộ thư mục `build/windows/` sang bất kỳ thư mục rỗng nào trên máy tính.
- Nhờ có cờ `_sc_` (Self-Contained), game tự động lưu dữ liệu cục bộ vào `editor_data/user/campaign_save.json` ngay trong thư mục game, **tuyệt đối không ghi đè** hay rò rỉ dữ liệu sang thư mục hệ thống của Windows (`%APPDATA%`).
- Không phụ thuộc vào đường dẫn của máy phát triển (`d:\Vibe Code\Antigravity`), không yêu cầu quyền Administrator.

---

## 4. SƠ ĐỒ ĐIỀU KHIỂN & BẢNG THIẾT LẬP (CONTROLS & SETTINGS)

### A. Sơ Đồ 9 Phím Điều Khiển Chiến Thuật
- **`[WASD]` hoặc Kéo chuột**: Điều động đơn vị được chọn vào vị trí chiến thuật đón đao ($R \le 3.5\text{m}$).
- **`[Tab]` hoặc Click trái**: Chọn hoặc đổi mục tiêu binh sĩ trên sa bàn.
- **`[Space]` hoặc `[Enter]` hoặc Click `[Xuất Kích]`**: Xác nhận đội hình / Tiến hành giao chiến / Tiếp tục.
- **`[P]` hoặc `[Esc]`**: Tạm dừng chiến trận / Đóng các cửa sổ thông báo, modal.
- **`[M]`**: **Bật / Tắt âm thanh toàn cục (Global Mute)** — luôn giữ quyền ưu tiên xử lý cao nhất ở mọi màn hình và modal.
- **`[N]`**: **Bật / Tắt hiệu ứng giảm rung lắc màn hình (Reduce Screen Shake)** giúp người chơi nhạy cảm thị giác không bị mỏi mắt.
- **`[F2]` hoặc `[?]`**: Mở lại hướng dẫn tân thủ sa bàn 3 bước trực quan.
- **`[1-3]`**: Chọn nhanh các ải chiến dịch đã mở khóa trong Hồi 1.
- **`[O]`**: Mở / Đóng bảng **Thiết Lập & Sơ Đồ Phím Tắt**.

### B. Bảng Thiết Lập & Bảo Vệ Bản Lưu 2 Bước (Safe Reset Save)
- Nền modal bán trong suốt chặn click chuột xuyên thấu sa bàn 3D (`mouse_filter = MOUSE_FILTER_STOP`).
- Toggles trực quan cho Âm lượng và Giảm rung camera.
- Nút `[ Xóa Toàn Bộ Bản Lưu / Chơi Lại Từ Đầu ]` yêu cầu xác nhận 2 bước an toàn:
  - Bấm lần 1: Nút chuyển sang màu đỏ cảnh báo `[ ⚠ BẤM LẦN NỮA ĐỂ XÁC NHẬN XÓA TOÀN BỘ BẢN LƯU! ]`.
  - Bấm lần 2: Xóa dữ liệu tiến trình và đưa game về trạng thái Ải 1 xuất phát điểm.
  - Tùy chọn cài đặt cá nhân (Mute, Reduce Motion) được bảo toàn nguyên vẹn sau khi reset dữ liệu tiến trình.

---

## 5. MẠCH TRUYỆN HỒI 1 & QUY TẮC MỞ KHÓA (CHAPTER 1 CAMPAIGN FLOW)

### A. Tuyến Tính 3 Ải Chiến Thuật (Golden Path)
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
- Xuất hiện trang trọng ngay sau khi hoàn thành Ải 3:
  - **Tổng Điểm Toàn Thắng**: **6,150 Điểm (Hạng S)** ($2,050 + 2,100 + 2,000 = 6,150$).
  - **Sao Tinh Thông Toàn Bích**: **9/9 ★ `[★ TOÀN BÍCH]`**.
  - Cung cấp 3 nút điều hướng: `[1] Đánh Lại Hồi 1`, `[C] Khiêu Chiến Thử Thách`, `[Esc] Màn Hình Chính`.

### C. Cách Ly Nhánh Thử Thách (Challenge Hub Isolation)
- Nhánh Khiêu Chiến Thử Thách (Ải 4–6 / Phase 9A–9H) hoàn toàn tách biệt với Chapter 1.
- Điểm số của Thử Thách (tối đa 18 sao, điểm chuẩn Ải 4 Normal `2,150`) không tính vào tổng điểm Chapter 1 (tối đa 9 sao).

---

## 6. GIỚI HẠN ĐÃ BIẾT TRONG BẢN BETA (KNOWN LIMITATIONS)

1. **Phương thức điều khiển**: Phiên bản Beta hiện chỉ hỗ trợ Bàn phím & Chuột; chưa hỗ trợ tay cầm chơi game (Gamepad).
2. **Tỷ lệ hiển thị**: Game thiết kế chuẩn tỷ lệ 16:9. Khi chạy trên màn hình Ultrawide, hệ thống hiển thị thanh viền đen để bảo toàn góc quay sa bàn thu nhỏ.
3. **Đóng gói PCK độc lập**: Tệp tin `Xianxia_Battlefield.pck` phải luôn đặt cùng thư mục với `Xianxia_Battlefield.exe`.
4. **Âm thanh tổng hợp bộ nhớ**: Toàn bộ hiệu ứng âm thanh là procedural PCM 16-bit, không tốn dung lượng tải về, có thể nghe mộc mạc hơn âm thanh thu âm phòng thu.

---

## 7. QUY TRÌNH BÁO CÁO LỖI DÀNH CHO NGƯỜI CHƠI (MANUAL BUG REPORTING)

Nếu gặp bất kỳ hiện tượng bất thường nào trong quá trình thử nghiệm bản Beta, người chơi vui lòng thực hiện:
1. Ghi lại: Tên ải đang chơi, Thao tác thực hiện ngay trước khi lỗi xuất hiện.
2. Chụp ảnh màn hình (`PrintScreen` hoặc công cụ chụp ảnh).
3. Nếu trò chơi bị tắt đột ngột: Khởi chạy tệp **`Xianxia_Battlefield_console.exe`** để mở game kèm cửa sổ lệnh, sao chép dòng thông báo lỗi (Error Log) cuối cùng.

---

## 8. BỘ TIÊU CHÍ NGHIỆM THU CHẤT LƯỢNG (QA ACCEPTANCE CRITERIA)

Mọi bản Beta Candidate trước khi chuyển giao cho người chơi phải thỏa mãn toàn bộ các điều kiện:
1. `test_phase_11a_beta_candidate.gd`: Đạt **PASS (6/6 Groups, Exit Code 0)**.
2. Chuỗi kiểm thử hồi quy (8R–10D Corrective): Đạt **PASS (100%)**.
3. `tools/run_qa_gate.ps1`: Đạt **PASS (12/12 Steps)** trong $< 45$s.
4. `tools/test_cleanroom_release.ps1`: Đạt **PASS** từ sandbox rỗng trong $< 10$s, 0 rò rỉ biến môi trường.
5. `tools/build_release.ps1 -VerifyOnly`: Đạt **PASS**, 9 file khớp SHA256 với manifest.
6. Process Hygiene: **0 orphan Godot processes** sau khi đóng ứng dụng.
7. Bất biến Blender: SHA256 của `phase_07D_full_combat_timing.blend` và `Xianxia_Battlefield.blend` bảo toàn 100%.
