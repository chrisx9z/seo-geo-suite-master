# HỒI 1: HÀN PHONG QUYẾT ĐỊA (CAMPAIGN CHAPTER 1)
## Phá Giới Giả: Chiến Địa Tiên Hiệp — Core Campaign Progression Specification

---

## 1. TỔNG QUAN & BỐI CẢNH CHIẾN DỊCH

**Hồi 1: Hàn Phong Quyết Địa** là chiến dịch cốt lõi mở màn của *Phá Giới Giả: Chiến Địa Tiên Hiệp*. Người chơi vào vai Tiền Quân Thống Lĩnh của quân đội Đại Chu, chỉ huy một toán quân gồm 14 binh sĩ tinh nhuệ (8 kiếm sĩ, 4 cung thủ, 2 thương sĩ tiên phong) chấn thủ một quan ải hiểm trở giữa tuyết sơn giá lạnh.

Tại đây, toàn quân phải đối mặt với **Đại Đao Tướng Quân** — một ma tướng khổng lồ với thể hình áp đảo gấp 4 lần lính thường, sở hữu tuyệt chiêu trảm kích khai sơn liệt địa mang hàn băng sát khí. Nhiệm vụ của người chơi không phải là giao tranh kéo dài, mà là vận dụng trí tuệ chiến thuật để **dàn trận đón đỡ đúng thời khắc** (Impact Frame F5), bẻ gãy ba thế đao liên tiếp để bảo toàn lực lượng và phản công toàn thắng.

---

## 2. MẠCH CHIẾN DỊCH 3 ẢI CỐT LÕI (CORE MISSIONS)

```
[ TITLE SCREEN ]
       │
       ▼ (Bắt Đầu / Tiếp Tục)
[ ẢI 1: TIÊN TRÂM LIỆT ĐỊA ] ──(Thắng: Mở khóa Ải 2)──► [ ẢI 2: THIẾT QUÂN PHÁ TRẬN ]
       │                                                         │
       │ (Thất bại: Cho phép Replay/Edit)                        │ (Thắng: Mở khóa Ải 3)
       ▼                                                         ▼
[ Giữ nguyên khóa Ải 2 ]                                  [ ẢI 3: TRÁNH NÉ PHẢN KÍCH ]
                                                                 │
                                                                 ▼ (Thắng)
                                                   [ TỔNG KẾT TOÀN THẮNG HỒI 1 ]
                                                   (Điểm Chiến Dịch & 9/9 Sao Tinh Thông)
```

### Ải 1: Tiên Trâm Liệt Địa (`mission_01_vanguard`)
- **Tình thế**: Đòn tấn công mở màn của Đại Đao Tướng Quân. Ma tướng giáng đại đao xuống sa trường, tạo luồng xung chấn cực mạnh có bán kính $R = 3.5\text{m}$ tại tọa độ $(1.75, 0.20, -0.45)$.
- **Bố trận ban đầu**: Đội hình xuất phát chỉ có 2 lính lõi trong tầm va chạm.
- **Nhiệm vụ**: Điều động thêm ít nhất 1 chiến sĩ tiến nhập tâm trảm kích ($R \le 3.5\text{m}$) để đạt ngưỡng **tối thiểu 3 lính đón đỡ**.
- **Ý nghĩa chiến thuật**: Giúp người chơi làm quen với thao tác chọn lính, điều chuyển vị trí và nhận thức vùng tử địa sa trường.
- **Điều kiện mở khóa**: Mở khóa mặc định khi bắt đầu trò chơi hoặc sau khi Đặt Lại Run (`reset_run`).

### Ải 2: Thiết Quân Phá Trận (`mission_02_iron_bulwark`)
- **Tình thế**: Bị bẻ gãy đòn đầu, Đại Đao Tướng Quân cuồng nộ dồn nội lực cực đại, phóng xuất đao kình cuộn trào hung hiểm hơn gấp bội.
- **Bố trận ban đầu**: 3 binh sĩ đã sẵn sàng đón đao tại rìa tâm tử địa.
- **Nhiệm vụ**: Hợp lực điều động thêm 1 chiến sĩ dũng cảm tiến vào tâm chấn, nâng tổng số lính đón đỡ lên **tối thiểu 4 lính**.
- **Ý nghĩa chiến thuật**: Thử thách khả năng phối hợp cự ly, căn chỉnh khoảng cách giữa các đơn vị ($> 0.8\text{m}$) và khoảng cách an toàn với Boss ($> 2.5\text{m}$).
- **Điều kiện mở khóa**: Chỉ mở khóa khi Ải 1 đã đạt trạng thái `CLEARED` (Đã vượt ải).

### Ải 3: Tránh Né Phản Kích (`mission_03_flank_assault`)
- **Tình thế**: Đại Đao Tướng Quân thi triển tuyệt kỹ tối thượng, giáng thế đao sấm sét hủy thiên diệt địa xuống khu vực trung tâm.
- **Bố trận ban đầu**: Toàn quân ban đầu nhận lệnh chủ động lùi sâu ra ngoài biên tử địa để bảo toàn sinh lực (số lính trong tâm ban đầu = 0).
- **Nhiệm vụ**: Chỉ huy đúng **2 chiến sĩ cảm tử** xung phong vào tâm trảm kích để đánh lạc hướng và bẻ gãy đòn thế, bảo vệ 12 đồng đội phía sau phản kích đại thắng.
- **Ý nghĩa chiến thuật**: Đòi hỏi tư duy chiến thuật ngược — từ né tránh sang đột kích dũng cảm, hoàn thiện cảm giác làm chủ thế trận của người chơi.
- **Điều kiện mở khóa**: Chỉ mở khóa khi Ải 2 đã đạt trạng thái `CLEARED` (Đã vượt ải).

---

## 3. QUY TẮC MỞ KHÓA & BẢO VỆ TIẾN TRÌNH (UNLOCK GATING)

### 3.1. Truy Vấn Mở Khóa Phái Sinh (Derived Query Logic)
Hệ thống không sử dụng cờ boolean độc lập để mở khóa, mà tính toán mở khóa trực tiếp từ trạng thái hoàn thành bền vững của các ải trước:
```gdscript
func is_mission_unlocked(mission_id: String) -> bool:
    if mission_id == "mission_01_vanguard":
        return true
    elif mission_id == "mission_02_iron_bulwark":
        return is_mission_cleared("mission_01_vanguard")
    elif mission_id == "mission_03_flank_assault":
        return is_mission_cleared("mission_02_iron_bulwark")
    return true
```

### 3.2. Bất Biến Thất Bại (Defeat Invariant)
- Thất bại (`OUTCOME_DEFEAT`) ở bất kỳ ải nào ghi nhận trạng thái `FAILED`, tuyệt đối **không bao giờ** kích hoạt `CLEARED`.
- Do đó, việc thua trận ở Ải 1 không thể mở Ải 2; thua ở Ải 2 không thể mở Ải 3.
- Mọi phím tắt (`[2]`, `[3]`, `[Left]`, `[Right]`) và thao tác click chuột vào tab ải bị khóa đều bị từ chối ở tầng logic điều khiển (`MissionFlow.gd`), kèm âm thanh cảnh báo và thông báo nhắc nhở trực quan.

### 3.3. Bảo Tồn Đơn Điệu Kỷ Lục (Monotonic Best Score & Mastery)
- **Kỷ lục điểm số**: `best_score = max(prev_best, match_score)`. Người chơi có thể tự do bấm `[1] Đánh Lại (Replay)` hoặc `[2] Sửa Đội Hình (Edit)` để thử nghiệm đội hình mới; nếu ván đấu sau đạt điểm thấp hơn, kỷ lục cũ vẫn được giữ nguyên vẹn.
- **Sao Tinh Thông (Mastery Stars)**: Một khi đã hoàn thành bất kỳ chiến tích nào trong số 3 mục tiêu của ải (Thắng trận, Đúng số lính lõi, Số lính sống sót), mục tiêu đó sẽ vĩnh viễn được ghi nhận (`achieved = true`), không bị xóa đi khi chơi lại.

---

## 4. TIẾP TỤC CHIẾN DỊCH & NẠP DỮ LIỆU AN TOÀN (CONTINUE WORKFLOW)

1. **Nhận Diện Tiến Trình Trên Title**:
   - Khi có dữ liệu lưu, nút chính trên Title Screen tự động chuyển thành: `[ Tiếp Tục Chiến Dịch (Ải X/3) (Space / Enter) ]`.
   - Nút `[ Đặt Lại Chiến Dịch (R) ]` xuất hiện cho phép người chơi xóa sạch tiến trình để chơi lại từ đầu nếu muốn.
2. **Kẹp An Toàn (Safe Clamping)**:
   - Khi người chơi chọn Tiếp tục, hệ thống nạp `current_mission_id`.
   - Nếu `current_mission_id` bị trống hoặc chỉ tới ải chưa mở khóa (do sửa file save hoặc bản lưu cũ), hệ thống tự động kẹp về ải hợp lệ cao nhất đã mở khóa thông qua `get_highest_unlocked_mission_id()`.
3. **Mở Vào Briefing**:
   - Tiếp tục chiến dịch chuyển người chơi vào màn hình Briefing của ải đó để xem lại tình thế chiến thuật, mục tiêu và gợi ý trước khi bước vào bày trận, không bỏ sót thông tin quan trọng.

---

## 5. TỔNG KẾT HOÀN THÀNH HỒI 1 (CHAPTER 1 COMPLETION)

Khi người chơi chiến thắng Ải 3 (`mission_03_flank_assault` đạt `CLEARED`), toàn bộ Hồi 1 hoàn thành (`campaign_state.is_all_cleared() == true`):

### 5.1. Bảng Tổng Kết Hồi 1 (Chapter 1 Summary Overlay)
Màn hình chuyển sang bảng tổng kết chiến dịch trang trọng:
- **Tiêu đề**: `[ HỒI 1: HÀN PHONG QUYẾT ĐỊA — TOÀN THẮNG ]`
- **Bảng chi tiết 3 ải**:
  - `Ải 1: Tiên Trâm Liệt Địa`: Điểm số tốt nhất, Hạng (S/A/B/C/D), Tinh thông (X/3 ★)
  - `Ải 2: Thiết Quân Phá Trận`: Điểm số tốt nhất, Hạng (S/A/B/C/D), Tinh thông (X/3 ★)
  - `Ải 3: Tránh Né Phản Kích`: Điểm số tốt nhất, Hạng (S/A/B/C/D), Tinh thông (X/3 ★)
- **Tổng kết toàn chiến dịch**:
  - **Tổng điểm Hồi 1**: Tổng điểm tốt nhất của 3 ải cốt lõi (tối đa ~6,150+ điểm).
  - **Xếp hạng chiến dịch**:
    - $\ge 4,800$ điểm: **Hạng S** (Xuất Quỷ Nhập Thần)
    - $\ge 3,900$ điểm: **Hạng A** (Đại Tướng Trấn Ải)
    - $\ge 3,000$ điểm: **Hạng B** (Kiên Cường Thủ Trận)
    - $\ge 1,500$ điểm: **Hạng C** (Sơ Phá Đao Kình)
    - $< 1,500$ điểm: **Hạng D**
  - **Tổng Tinh Thông**: Số sao đạt được trên tổng số 9 sao ($X / 9\text{ ★}$). Nếu đạt đủ 9/9 sao, trao danh hiệu `[★ TOÀN BÍCH]`.
- **Hành động điều hướng**:
  - `[1] Đánh Lại Hồi 1`: Đưa người chơi về Ải 1 để săn điểm cao hơn.
  - `[C] Khiêu Chiến Thử Thách`: Mở thẳng Khu Vực Thử Thách (Challenge Hub) để trải nghiệm các ải cực hạn 4, 5, 6.
  - `[Esc] Màn Hình Chính`: Trở về Title Screen với trạng thái đã hoàn thành toàn bộ Hồi 1.

---

## 6. PHÂN LẬP TUYỆT ĐỐI VỚI KHU THỬ THÁCH (CHALLENGE HUB ISOLATION)

- **Danh mục nhiệm vụ**:
  - Hồi 1 (`CORE_MISSION_IDS`): Chỉ gồm `mission_01_vanguard`, `mission_02_iron_bulwark`, `mission_03_flank_assault`.
  - Khu Thử Thách (`CHALLENGE_MISSION_IDS`): Gồm `mission_04_frozen_gate` (Normal/Hard), `mission_05_moonlit_ambush` (Normal/Hard), `mission_06_frostline_encirclement` (Normal/Hard).
- **Chỉ số không trộn lẫn**:
  - Tổng điểm và hạng Hồi 1 **tuyệt đối không** cộng điểm của các ải thử thách.
  - Tổng tinh thông Hồi 1 có giới hạn tối đa là 9 sao (3 ải $\times$ 3 sao). 18 sao của Khu Thử Thách được quản lý riêng qua `get_challenge_summary()`.
  - Việc mở khóa và hoàn thành Hồi 1 vận hành độc lập, không yêu cầu người chơi phải chạm vào Challenge Hub.
