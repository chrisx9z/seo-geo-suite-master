# CHAPTER 2 — STORY VERTICAL SLICE BRIEF & EXPERIENCE TARGET

**Version**: `v0.12.0-slice` / Milestone: Chapter 2 Story Vertical Slice  
**Baseline**: Locked Beta Release `v0.11.0-beta` (Phase 11B)  
**Document**: `docs/CHAPTER_2_BRIEF.md`

---

## 1. NARRATIVE & EXPERIENTIAL TARGET

### 1.1. Cốt Truyện Tiếp Nối (Narrative Continuity)
Sau thắng lợi rực rỡ tại **Hàn Phong Quyết Địa (Hồi 1)** — nơi 3 đợt cuồng đao bão tuyết của Đại Đao Tướng Quân bị bẻ gãy hoàn toàn ($6,150$ điểm, Hạng S, 9/9 ★ [★ TOÀN BÍCH]), tiền quân tiếp tục hành quân tiến sâu vào hiểm địa **Tuyết Nhai (Hồi 2)**.

Tại lối hẹp hẻm núi Tuyết Nhai, Đại Đao Tướng Quân hồi phục chân nguyên, thi triển thế trận **Thiết Bích Đao Kình** với quỹ đạo sắc bén và áp lực dồn dập. Không chỉ đòi hỏi lòng dũng cảm, trận chiến này buộc thống soái phải bố trí chính xác thế trận đón đỡ có kỷ luật nghiêm ngặt.

### 1.2. Mục Tiêu Trải Nghiệm (Player Experience Target)
- **Tập trung vào tính chiến thuật**: Người chơi trải nghiệm ngay một màn chơi hoàn chỉnh từ khâu tiếp nhận quân lệnh (Briefing), điều quân bày trận (Formation), kích hoạt giao tranh 24-frame kịch tính (Combat), đến bảng tổng kết chiến tích và sao tinh thông (Result).
- **Trải nghiệm liền mạch**: Không bị ngắt quãng, không phát sinh lỗi thoát game hay tràn chữ; hỗ trợ đầy đủ bàn phím lẫn chuột.
- **Tiếp cận nhanh chóng**: Có thể khởi động thử nghiệm Hồi 2 trực tiếp từ Màn hình Tiêu Đề (`[X] Hồi 2: Thử Nghiệm`) hoặc sau khi hoàn thành Hồi 1 (`[2] Tiến Vào Hồi 2`).

---

## 2. BẢO TỒN BẢN SẮC MỸ THUẬT DIORAMA TIÊN HIỆP (ZERO ART DRIFT)

Dự án tuyệt đối không thay đổi phong cách nghệ thuật, giữ trọn vẹn bản sắc sa bàn thu nhỏ:
1. **Camera Calibration Invariant**:
   - Camera diorama phối cảnh tiêu cự 70mm.
   - Tọa độ Godot: `(1.0000, 22.3000, 40.8000)`.
   - Góc chúc nhìn xuống: `-28.000°` (góc nhìn xuống `62.0°`).
   - Vertical FOV: `19.455°`.
2. **Combat Origin & Geometry Invariants**:
   - Tâm tử địa va chạm cố định: `(1.7500, 0.2000, -0.4500)`.
   - Bán kính vùng lõi: $R \le 3.5\text{m}$.
   - Checkpoint Blender SHA256: `1627c789d06c48870f13935be476d75a0815f93fe8bafd3d9ea8c3ec0155f94e`.
   - Master Scene Blender SHA256: `94dd14dd38c845e52ba3d1004dbc3423548604cffb5c64f074ba205a90b6550f`.
3. **Shader & VFX Identity**:
   - Phong cách Soft Toon Shading trên nền sa bàn tuyết phủ và kiến trúc cổ phong.
   - Hiệu ứng đao khí thư pháp (Sword Qi Ribbon) phát quang trắng tuyết viền ngọc bích.
   - Hit-stop giữ thế va chạm cực hạn F7–F8 (độ dịch chuyển $\le 0.008\text{m}$).

---

## 3. THIẾT KẾ MÀN CHƠI MẪU: `chapter_2_mission_01`

- **Mã định danh (Namespace)**: `chapter_2_mission_01` (Cách ly hoàn toàn với Hồi 1 và Challenge Hub 9A–9H).
- **Tiêu đề**: `HỒI 2 - ẢI 1: TUYẾT NHAI QUYẾT CHIẾN`
- **Ngưỡng đón đỡ mục tiêu (`target_threshold`)**: `4` lính tiên phong.
- **Bố trí ban đầu (`initial_formation_offsets`)**:
  - `CHAR_Spear_Point`: `Vector3(4.3, 0.004, -0.6)` (Khoảng cách XZ tới tâm $\approx 2.55\text{m} \le 3.5\text{m}$).
  - Cùng với 2 lính mặc định trong vùng lõi, tổng khởi điểm có 3 lính trong tâm.
  - Người chơi cần điều thêm đúng 1 đơn vị kiếm sĩ vào tâm để đạt 4 lính đón đao (Thiết Bích Trận).
- **Mục tiêu Tinh Thông (Mastery Objectives)**:
  1. `obj_ch2_m1_clear`: Thắng trận (`RULE_VICTORY`)
  2. `obj_ch2_m1_exact_core`: Đúng 4 lính lõi (`RULE_EXACT_CORE_HITS`, giá trị: 4)
  3. `obj_ch2_m1_high_survivors`: Sống sót $\ge 10$ lính (`RULE_MIN_SURVIVORS`, giá trị: 10)
- **Công thức tính điểm chuẩn (Canonical Score)**:
  $$\text{Cơ bản (Thắng): } 1000 + \text{Đón đao (4): } 400 + \text{Sống sót (10): } 500 + \text{Kỷ luật (Đúng 4): } 200 = \mathbf{2,100 \text{ Điểm}} \quad (\text{Hạng S, 3/3 ★})$$

---

## 4. QUY TẮC CÁCH LY & BẢO VỆ BASELINE HỒI 1

1. `MissionConfig.get_catalog(false)` tiếp tục trả về duy nhất 3 ải Hồi 1.
2. `CampaignState.CORE_MISSION_IDS` giữ nguyên 3 ải Hồi 1; tổng điểm Hồi 1 luôn là $2050 + 2100 + 2000 = 6,150$.
3. Challenge Mission 4 Normal giữ nguyên điểm chuẩn $2,150$; cụm Thử Thách 9A–9H độc lập 100%.
4. Lưu trữ bản lưu (Save Schema v3) tương thích ngược hoàn toàn, không tạo schema phụ hay file cấu hình rác.
