# HỒI 2: TUYẾT NHAI QUYẾT CHIẾN (CAMPAIGN CHAPTER 2)
## Phá Giới Giả: Chiến Địa Tiên Hiệp — Core Campaign Chapter 2 Specification

---

## 1. TỔNG QUAN & BỐI CẢNH CHIẾN DỊCH HỒI 2

Sau thắng lợi rực rỡ tại **Hàn Phong Quyết Địa (Hồi 1)** — nơi ba đợt cuồng đao bão tuyết của Đại Đao Tướng Quân bị bẻ gãy hoàn toàn ($6,150$ điểm, Hạng S, 9/9 ★ [★ TOÀN BÍCH]), tiền quân Đại Chu tiếp tục hành quân tiến sâu vào hiểm địa **Tuyết Nhai (Hồi 2)**.

Tại hẻm núi Tuyết Nhai ngập tràn ma khí và bão tuyết cuồng phong, **Đại Đao Tướng Quân** hồi phục chân nguyên ma đạo, thi triển những thế trận đao kình biến ảo khôn lường với sát lực gia tăng vượt bậc. Không chỉ dừng lại ở việc đón đỡ đơn thuần, Hồi 2 đòi hỏi Thống Soái phải nắm vững trận pháp phối hợp: từ **Thiết Bích Trận** (4 lính) mở đường, qua **Ngũ Hành Tuyệt Trận** (5 lính) trảm trừ yêu ma, tới **Tam Cương Quyết Đao** (3 lính cảm tử) phá giải đại chiêu Thập Băng Liệt Địa Trảm tại đỉnh núi tuyết.

---

## 2. MẠCH CHIẾN DỊCH 3 ẢI CỐT LÕI (CORE CHAPTER 2 MISSIONS)

```
[ TITLE SCREEN / KẾT THÚC HỒI 1 ]
       │
       ▼ (Khởi Động Hồi 2: Phím [X] hoặc [2])
[ ẢI 1: TUYẾT NHAI QUYẾT CHIẾN ] ──(Thắng: Mở khóa Ải 2)──► [ ẢI 2: TUYẾT SƠN TRẢM YÊU ]
       │                                                         │
       │ (Thất bại: Cho phép Replay/Edit)                        │ (Thắng: Mở khóa Ải 3)
       ▼                                                         ▼
[ Giữ nguyên khóa Ải 2 ]                                  [ ẢI 3: TUYẾT NHAI ĐỈNH PHONG ]
                                                                 │
                                                                 ▼ (Thắng)
                                                   [ TỔNG KẾT TOÀN THẮNG HỒI 2 ]
                                                   (6,300 Điểm & 9/9 Sao Tinh Thông)
```

### Ải 1: Tuyết Nhai Quyết Chiến (`chapter_2_mission_01`)
- **Tình thế**: Sau khi bẻ gãy đao kình tại Hàn Phong Quyết Địa, tiền quân tiến nhập hiểm địa Tuyết Nhai. Đại Đao Tướng Quân hồi phục chân nguyên, đao phong biến hóa thâm sâu khôn lường.
- **Tâm tử địa**: $(1.75, 0.20, -0.45)$, bán kính $R \le 3.5\text{m}$.
- **Ngưỡng đón đỡ mục tiêu**: **Tối thiểu 4 lính** ($4$ core hits).
- **Bố trận ban đầu**: Đội hình khởi điểm có 3 lính trong tâm tử địa (`CHAR_Spear_Point` tại offset $(4.3, 0.004, -0.6)$ kết hợp 2 thương sĩ tiên phong).
- **Chiến thuật tối ưu**: Điều động thêm đúng 1 kiếm sĩ (`CHAR_Swordsman_L1`) tiến vào tâm tại tọa độ offset $(3.3, 0.008, -0.7)$ để kết thành Thiết Bích Trận (đúng 4 lính đón đao, 10 lính sống sót).
- **Điểm chuẩn (Canonical Score)**:
  $$\text{Cơ bản (Thắng): } 1000 + \text{Đón đao (4): } 400 + \text{Sống sót (10): } 500 + \text{Kỷ luật (Đúng 4): } 200 = \mathbf{2,100 \text{ Điểm}} \quad (\text{Hạng S})$$
- **Mục tiêu Tinh Thông**:
  1. `obj_ch2_m1_clear`: Thắng trận (`RULE_VICTORY`)
  2. `obj_ch2_m1_exact_core`: Đúng 4 lính lõi (`RULE_EXACT_CORE_HITS`, giá trị: 4)
  3. `obj_ch2_m1_high_survivors`: Sống sót $\ge 10$ lính (`RULE_MIN_SURVIVORS`, giá trị: 10)

---

### Ải 2: Tuyết Sơn Trảm Yêu (`chapter_2_mission_02`)
- **Tình thế**: Tiến sâu vào Tuyết Sơn Ma Vực, ma khí cuồn cuộn ngút trời. Đại Đao Tướng Quân thi triển cuồng ma sát trận hiểm ác trên diện rộng.
- **Tâm tử địa**: $(1.75, 0.20, -0.45)$, bán kính $R \le 3.5\text{m}$.
- **Ngưỡng đón đỡ mục tiêu**: **Tối thiểu 5 lính** ($5$ core hits).
- **Bố trận ban đầu**: Đội hình khởi điểm có 4 lính trong tâm tử địa (`CHAR_Spear_Point` và `CHAR_Swordsman_L1`).
- **Chiến thuật tối ưu**: Điều động thêm đúng 1 kiếm sĩ (`CHAR_Swordsman_L2`) vào tâm tại tọa độ offset $(2.5, 0.004, -0.5)$ để kết thành Ngũ Hành Tuyệt Trận (đúng 5 lính đón đao, 9 lính sống sót).
- **Điểm chuẩn (Canonical Score)**:
  $$\text{Cơ bản (Thắng): } 1000 + \text{Đón đao (5): } 500 + \text{Sống sót (9): } 450 + \text{Kỷ luật (Đúng 5): } 200 = \mathbf{2,150 \text{ Điểm}} \quad (\text{Hạng S})$$
- **Mục tiêu Tinh Thông**:
  1. `obj_ch2_m2_clear`: Thắng trận (`RULE_VICTORY`)
  2. `obj_ch2_m2_exact_core`: Đúng 5 lính lõi (`RULE_EXACT_CORE_HITS`, giá trị: 5)
  3. `obj_ch2_m2_high_survivors`: Sống sót $\ge 9$ lính (`RULE_MIN_SURVIVORS`, giá trị: 9)

---

### Ải 3: Tuyết Nhai Đỉnh Phong (`chapter_2_mission_03`)
- **Tình thế**: Đỉnh núi tuyết ngập tràn hàn phong lãnh liệt. Đại Đao Tướng Quân dồn toàn bộ tàn lực vào tuyệt kỹ Thập Băng Liệt Địa Trảm bao phủ phạm vi cực rộng.
- **Tâm tử địa**: $(1.75, 0.20, -0.45)$, bán kính $R \le 3.5\text{m}$.
- **Ngưỡng đón đỡ mục tiêu**: **Đúng 3 lính** ($3$ core hits).
- **Bố trận ban đầu**: Toàn quân chủ động dạt ra xa tránh né (`CHAR_Vanguard_Lead` và `CHAR_Vanguard_Wing` lùi ra ngoài biên tử địa, số lính trong tâm ban đầu = 0).
- **Chiến thuật tối ưu**: Chỉ huy 3 dũng sĩ cảm tử đột nhập tâm tử địa (`CHAR_Spear_Point`, `CHAR_Swordsman_L1`, `CHAR_Swordsman_L2`), bảo toàn 11 binh sĩ tại vùng ngoài để phản kích toàn thắng (đúng 3 lính đón đao, 11 lính sống sót).
- **Điểm chuẩn (Canonical Score)**:
  $$\text{Cơ bản (Thắng): } 1000 + \text{Đón đao (3): } 300 + \text{Sống sót (11): } 550 + \text{Kỷ luật (Đúng 3): } 200 = \mathbf{2,050 \text{ Điểm}} \quad (\text{Hạng S})$$
- **Mục tiêu Tinh Thông**:
  1. `obj_ch2_m3_clear`: Thắng chung cuộc (`RULE_VICTORY`)
  2. `obj_ch2_m3_exact_core`: Đúng 3 lính lõi (`RULE_EXACT_CORE_HITS`, giá trị: 3)
  3. `obj_ch2_m3_high_survivors`: Sống sót $\ge 11$ lính (`RULE_MIN_SURVIVORS`, giá trị: 11)

---

## 3. QUY TẮC MỞ KHÓA & BẢO VỆ TIẾN TRÌNH

### 3.1. Cơ Chế Mở Khóa Tuần Tự (Sequential Gating)
```gdscript
func is_mission_unlocked(mission_id: String) -> bool:
    if mission_id == "chapter_2_mission_01":
        return true
    elif mission_id == "chapter_2_mission_02":
        return is_mission_cleared("chapter_2_mission_01")
    elif mission_id == "chapter_2_mission_03":
        return is_mission_cleared("chapter_2_mission_02")
    return true
```

### 3.2. Bất Biến Khi Thất Bại (Defeat Invariant)
- Thất bại ở Ải 1 ghi nhận `FAILED`, không mở khóa Ải 2.
- Thất bại ở Ải 2 không mở khóa Ải 3.
- Mọi nỗ lực truy cập ải bị khóa đều bị từ chối an toàn ở controller, kèm âm thanh cảnh báo từ chối (`wav_invalid`).

### 3.3. Bảo Toàn Kỷ Lục Đơn Điệu (Monotonic Integrity)
- Khi chơi lại ải với điểm số thấp hơn, kỷ lục điểm cao nhất (`best_score`), hạng (`best_rank`) và số sao tinh thông (`mastery`) vĩnh viễn được giữ nguyên.
- Không phát sinh hiện tượng thụt lùi sao hay điểm số.

---

## 4. TỔNG KẾT ĐẠI THẮNG TOÀN BỘ HỒI 2

Khi chiến thắng Ải 3 (`chapter_2_mission_03` đạt `CLEARED`), toàn bộ Hồi 2 hoàn thành:
- **Tổng Điểm Toàn Hồi**:
  $$\text{Tổng Điểm} = 2,100 + 2,150 + 2,050 = \mathbf{6,300 \text{ Điểm}}$$
- **Xếp Hạng Chiến Dịch**: **Hạng S** ($\ge 6,000$ điểm).
- **Tinh Thông Toàn Phần**: **9/9 ★ [★ TOÀN BÍCH]**.
- **Hiệu Ứng Trực Quan & Âm Thanh**:
  - Giao diện `chapter_summary_overlay` hiển thị tiêu đề `TỔNG KẾT HỒI 2: TUYẾT NHAI QUYẾT CHIẾN`.
  - Hiệu ứng âm thanh hợp âm 4 nốt `wav_chapter_complete` (C5, E5, G5, C6).
  - Banner chiến cục: `[👑] TOÀN THẮNG: HOÀN THÀNH HỒI 2`.

---

## 5. TƯƠNG THÍCH LƯU TRỮ SAVE SCHEMA V3 & KIỂM THỬ

- **Save Schema v3**: Dữ liệu cả 3 ải Hồi 2 được lưu trữ nguyên tử qua Windows Win32 MoveFile replace tại `user://campaign_save.json`.
- **Bộ Kiểm Thử Tự Động**: Toàn bộ tiến trình được bảo vệ bởi test suite [test_phase_12b_chapter2_campaign.gd](file:///d:/Vibe%20Code/Antigravity/game/tests/test_phase_12b_chapter2_campaign.gd) với tỷ lệ vượt qua $100\%$ (6/6 nhóm kiểm định, 0 lỗi).
