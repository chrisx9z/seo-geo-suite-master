# Phá Giới Giả — Art Direction Bible (Master Art Standard)

**Document Version**: 1.0 — Phase 10A Production Lock  
**Target Platform**: Windows Standalone (Godot 4.7.2 Forward+ / Vulkan)  
**Visual Reference Authority**: `references/IMG_8957.MP4` & `references/frames/`  
**Artistic Genre**: 3D Chibi Xianxia / Wuxia Miniature Tactical Diorama  

---

## 1. TỔNG QUAN ĐỊNH HƯỚNG NGHỆ THUẬT (ARTISTIC VISION)

Dự án **Phá Giới Giả** hướng tới trải nghiệm sa bàn sa trường thu nhỏ (*miniature battlefield diorama*) mang đậm phong vị tiên hiệp cổ phong (Chinese xianxia/wuxia fantasy) kết hợp tạo hình Chibi cách điệu cao cấp:
- **Cảm giác thị giác chủ đạo**: Một mô hình sa bàn sa trường cổ kính thu nhỏ đặt giữa thung lũng tuyết mùa đông, mang tính chiến thuật bàn cờ nhưng sở hữu hiệu ứng điện ảnh sống động như phim hoạt hình 3D cách điệu.
- **Tính đối lập thị giác (Contrast Strategy)**:
  - Bối cảnh tuyết phủ và tường thành đá mang tông màu lạnh, trầm mặc, độ bão hòa thấp (*cool, desaturated palette*).
  - Nhân vật và kiếm khí nổi bật với các mảng màu bão hòa cao (*saturated jewel tones*: lam ngọc, đỏ son, vàng hổ phách, trắng phát quang).
- **Tuyệt đối tránh**:
  - Phong cách PBR tả thực (realistic photogrammetry, photo textures da thịt, lỗ chân lông).
  - Camera góc rộng cinematic mắt người (18–35mm) làm vỡ tỷ lệ sa bàn.
  - Hiệu ứng cháy nổ kiểu khoa học viễn tưởng (lasers, neon glow, bloom chói mắt).

---

## 2. CHUẨN GÓC MÁY SA BÀN (CAMERA CALIBRATION & DIORAMA COMPRESSION)

Camera là thành tố quan trọng bậc nhất định hình toàn bộ phong cách sa bàn thu nhỏ:

| Thông Số Camera | Giá Trị Khóa Chuẩn | Ý Nghĩa Kỹ Thuật & Thẩm Mỹ |
| :--- | :--- | :--- |
| **Vị trí Camera (`Position`)** | `Vector3(1.0000, 22.3000, 40.8000)` | Đặt camera trên cao và kéo lùi xa để triệt tiêu méo phối cảnh. |
| **Góc chúc (`Pitch`)** | `-28.000°` (Euler X: `-0.48869 rad`) | Nhìn xuống chiến trường ở góc nghiêng **62.0°**, bao quát toàn bộ 14 lính và Boss. |
| **Góc xoay ngang / nghiêng** | `Yaw = 0.0°`, `Roll = 0.0°` | Trục nhìn thẳng đối xứng, cân bằng hai cánh đội hình. |
| **Tiêu cự tương đương / FOV** | **Vertical FOV: 19.455°** (~70mm Telephoto) | Độ nén phối cảnh cao (*telephoto compression*), tạo ấn tượng gần trục đo (*near-isometric*). |
| **Hit-Stop Displacement** | Khóa chặn `0.0065m` tại F7 $\to$ F8 | Rung chấn va chạm cực tinh tế trong 2 frame, không làm rung lắc lệch góc nhìn người chơi. |

---

## 3. TỶ LỆ & SILHOUETTE NHÂN VẬT (CHARACTER PROPORTIONS & SHAPES)

### 3.1. Thủ Lĩnh (Đại Đao Tướng Quân — `CHAR_Boss`)
- **Tỷ lệ**: Cao gấp **3.75 lần** lính chibi (~5.25m so với ~1.40m).
- **Silhouette**:
  - Thân trên vạm vỡ, vai bọc giáp giác đấu nhọn hoắt, sừng ngưu ma cong vút trên đỉnh mũ chiến.
  - Đại đao nguyệt nha siêu kích thước vung ngang chiến trường.
  - Vạt chiến bào ngọc bích xòe rộng tạo khối chuyển động thứ cấp (*secondary motion*).
- **Màu sắc & Chất liệu**:
  - Giáp trụ kim loại đen than củi (`#1E2226`) với viền lam ngọc (`#14B8A6`) và ngọc bích phát quang dịu.
  - Roughness giáp: 0.40 – 0.60 (phản quang mảng rộng, không bóng gương).

### 3.2. Đội Hình 14 Binh Sĩ Chibi (`CHAR_Soldier`)
- **Tỷ lệ cơ thể**: **2.8 đầu** (Đầu lớn ngộ nghĩnh, thân ngắn chắc khỏe, tay chân gọn gàng).
- **Khối hình học rõ nét từ camera xa**:
  - **Giáo Binh (Spear Vanguard/Wing)**: Ngọn giáo dài cán đen, tua giáo đỏ son (`#E11D48`) phấp phới chỉ hướng tấn công.
  - **Kiếm Sĩ (Swordsmen)**: Kiếm cong xianxia bản rộng, khiên tròn hộ thân viền vàng.
  - **Cung Thủ (Archers)**: Nón trúc tròn cách điệu, cánh cung cong thanh thoát.
- **Trang phục**: Chiến bào vải thô tông xanh lam/xám nhạt kết hợp thắt lưng đỏ son và giáp vai vàng kim nhạt (`#F59E0B`). Roughness vải: 0.70 – 0.85.

---

## 4. MÔI TRƯỜNG & BẢNG MÀU CHIẾN TRƯỜNG (ENVIRONMENT & COLOR BIBLE)

### 4.1. Bảng Màu Môi Trường (60% Khung Hình)
- **Tuyết phủ sa bàn**: `#98AAB2` (vùng tối) $\to$ `#E2ECF0` (vùng sáng phản quang), Roughness 0.85.
- **Đá cổ & Ngói lầu các**: `#2E3A3D` / `#455054`, tạo khối kiến trúc vững chãi.
- **Gỗ & Cột đình**: Nâu sẫm ấm `#3D2E24`, hạn chế chói gắt.
- **Sương mù chân trời (Atmosphere)**: `#B8C8D0` hòa sắc chân núi Hoàng Sơn vào bầu trời mùa đông, loại bỏ viền đen vô tận.

### 4.2. Bảng Màu Điểm Nhấn Nhân Vật & VFX (30% + 10%)
- **Ngọc Bích Tiên Hiệp**: `#34D399` / `#14B8A6` (Huy hiệu, ấn chú, viền giáp).
- **Đỏ Son Cổ Phong**: `#E11D48` (Tua giáo, cờ hiệu, dải lụa thắt lưng).
- **Vàng Kim Hổ Phách**: `#F59E0B` (Viền khiên, ấn quyết, hiệu ứng thắng trận).
- **Kiếm Khí Bạch Quang**: Lõi trắng `#FFFFFF` với hào quang `#5EEAD4`.

---

## 5. ÁNH SÁNG & KHÔNG KHÍ (LIGHTING & ATMOSPHERE)

- **Chiếu sáng chính (Sun Light)**: Nguồn sáng hướng dốc **35°**, mô phỏng ánh nắng chiều đông xuyên qua màn sương mù lạnh.
- **Chiếu sáng môi trường (Ambient Fill)**: Vòm trời bán cầu tỏa sáng mềm góc **85°**, độ tương phản vừa phải, loại bỏ hoàn toàn vùng bóng tối đen kịt (shadows luôn giữ sắc lam xám lạnh).
- **Volumetric Fog**: Lớp sương mù tĩnh mỏng tạo chiều sâu không gian nhiều tầng (tiền cảnh lính $\to$ trung cảnh Boss $\to$ hậu cảnh cổng thành & núi đá Hoàng Sơn).

---

## 6. HIỆU ỨNG KIẾM KHÍ & NHỊP ĐỘ CHIẾN ĐẤU (VFX & COMBAT TIMING)

### 6.1. Kiếm Khí Thư Pháp (Sword-Qi Ribbon VFX)
- Dải hình học 3D uốn lượn hình cánh cung bán nguyệt, đầu thon nhọn, thân mở rộng và vuốt mềm về đuôi giống nét đặt bút lông thư pháp Trung Hoa.
- Chất liệu tự phát quang (*Unshaded Emission*) với lõi trắng 100% và viền chuyển sắc sang cyan/ngọc bích.

### 6.2. Nhịp Đòn Đánh Wuxia Chuẩn (24-Frame Timeline @ 30 FPS)
- **F1 – F4 (Anticipation)**: Boss vung ngược đại đao lên đỉnh điểm, tụ khí đao phong.
- **F5 (Impact & Strike)**: Đại đao giáng xuống mặt đất tại `(1.75, 0.20, -0.45)`. Vệt kiếm khí bùng nổ, vòng sóng xung kích mở rộng, tuyết văng tung tóe. Lính trong vòng tử địa ($R \le 3.5\text{m}$) nhận 150 sát thương và bị đánh gục.
- **F6 – F7 (Hit-Stop & Freeze)**: Khựng hình vi mô, camera rung chấn nhẹ 0.0065m nhấn mạnh uy lực đòn chém.
- **F8 – F24 (Recovery & Dissipation)**: Đao phong tan biến vào sương lạnh, lính sống sót ngoài vòng giữ vững thế trận phòng thủ.

---

## 7. CẤU TRÚC GIAO DIỆN & KHẢ NĂNG TIẾP CẬN (UI HIERARCHY & ACCESSIBILITY)

- **Màu nền Modal**: Kính mờ than củi xianxia (`Color(0.10, 0.12, 0.14, 0.88)`), viền mạ vàng (`#D4AF37`) hoặc ngọc bích (`#34D399`).
- **Phân cấp thị giác**:
  - Tiêu đề chính 16–17pt Vàng Kim.
  - Nội dung chiến thuật 12–13pt Bạc/Trắng.
  - Chú thích điều khiển 10–11pt Lam nhạt.
- **Nguyên tắc phi màu sắc (Non-Color Accessibility)**:
  - Mọi trạng thái luôn đi kèm ký hiệu văn bản rõ ràng: `[✓ ĐẠT]` / `[○ CHƯA]`, `[★]` cho sao tinh thông.
- **Khóa kích thước giao diện**:
  - Mọi bảng modal (Title 460px, Briefing 700×440px, Result 760×460px, Hub 860×465px) nằm gọn trong khung hình an toàn $900 \times 520\text{px}$ ở độ phân giải gốc 960×540.
  - Phóng to tỷ lệ nguyên ($2\times$) hoàn hảo lên 1080p (1920×1080) thông qua cơ chế `stretch/mode="viewport"`.
