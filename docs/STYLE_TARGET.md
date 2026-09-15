# Xianxia Miniature Battlefield Diorama — Style Target

Tài liệu này xác định mục tiêu phong cách nghệ thuật (Master Style Bible) cho dự án `XianxiaBlender` dựa trên việc phân tích trực tiếp video tham chiếu `references/IMG_8957.MP4` và các keyframe trích xuất tại `references/frames/`.

---

## 1. Phân Tích Thông Số Thị Giác Từ Video Tham Chiếu (Reference Analysis)

| Hạng Mục | Ước Tính Từ Video Tham Chiếu | Thiết Lập Chuẩn Trong Blender | Ghi Chú Kỹ Thuật |
| :--- | :--- | :--- | :--- |
| **Camera Downward Angle** | Chúc xuống khoảng **55° – 65°** | **61.9°** (Euler X: `radians(61.9)`) | Tạo cảm giác sa bàn chiến thuật (near-isometric), hạn chế méo hình học. |
| **Apparent Focal Length / Compression** | Ống kính tiêu chuẩn hẹp, độ nén phối cảnh cao | **52.0 mm** (Sensor size 36mm) | Tránh góc rộng (18–35mm), kéo camera ra xa `(0, -29, 18)` để nén phối cảnh. |
| **Boss-to-Soldier Scale** | Boss gấp **3.5x – 4.5x** chiều cao binh lính | **3.75x** (Boss ~5.25m, Lính Chibi ~1.40m) | Boss áp đảo hoàn toàn thị giác ở góc máy sa bàn xa. |
| **Soldier Body Proportions** | Tỷ lệ Chibi **2.5 – 3.2 đầu** | **2.8 đầu** (Đầu r=0.32m, Thân h=0.55m, Chân h=0.38m) | Đầu to ngộ nghĩnh, tay chân ngắn, nón trúc và khiên tạo hình khối rõ nét. |
| **Battlefield Scale** | Sa bàn diorama bán kính ~18–25m | Bệ tròn đường kính **44m** (R=22m, z=-0.8m) | Môi trường chiếm 70% khung hình, bố cục bao quát thung lũng tuyết. |
| **Dominant Environment Colors** | Xám xanh tuyết lạnh, đen than củi, trắng sương | Tuyết: `#98AAB2` / `#E2ECF0`, Đá/Ngói: `#2E3A3D` / `#455054` | Độ bão hòa thấp (desaturated), tương phản dịu mắt kiểu tranh thủy mặc. |
| **Character Accent Colors** | Xanh ngọc bích, đỏ son, vàng hổ phách | Ngọc bích: `#34D399` / `#14B8A6`, Đỏ son: `#E11D48`, Vàng: `#F59E0B` | Độ bão hòa cao hơn môi trường để nổi bật trên nền tuyết trắng. |
| **Lighting Softness** | Ánh sáng mùa đông phân tán dịu nhẹ, không gắt | Mặt trời góc tán xạ **35°**, Fill Sky bán kính rộng **85°** | Đổ bóng mềm (Soft Shadows), không có vùng đen gắt (harsh black shadows). |
| **Fog Amount** | Sương mù mờ ảo nhẹ che khuất chân núi phía xa | World Background `#B8C8D0` + World Strength 0.95 | Loại bỏ khoảng đen vô tận, hòa sắc ngọn núi đá Hoàng Sơn vào đường chân trời. |
| **Material / Shader Style** | Toon/Hybrid stylized, AgX Punchy, không noise | Roughness cao (0.70–0.92), Metallic chọn lọc (0.35–0.85) | Tuyệt đối KHÔNG dùng PBR tả thực, không dùng photo texture phân giải cao. |
| **Outline Strength** | Nét viền mực mờ tinh tế hoặc phân tách mảng | Sử dụng độ tương phản khối và viền sáng (Rim Light) | Subtle ink line, tránh viền đen dày hoạt hình phương Tây. |
| **VFX Shapes and Colors** | 14–16 tia đao khí đài sen (Lotus burst), sóng chấn | Lõi trắng tinh `#FFFFFF` (Strength 11.0), viền cyan `#5EEAD4` | Dải Bezier 3D vuốt nhọn đầu đuôi, uốn lượn như nét bút lông thư pháp. |
| **Animation Timing Characteristics** | Nhịp đòn đánh Wuxia có độ khựng (Hit-Stop) | Chu kỳ 120f: Gồng f1-27, Chém f28-40, Hit-Stop f41-42, Hồi f43-70 | Frame 41 khựng cứng 1-2 frame, lính giật lùi, camera rung chấn 2 frame. |

---

## 2. Bố Cục Sa Bàn Diorama Chuẩn (Quy Tắc 70 / 20 / 10)

1. **Môi Trường (70%)**: Thung lũng mùa đông phủ tuyết, hệ thống tường thành cổ kính ngói cong có trụ cổng đỏ son, 2 lầu các Trung Hoa 2 tầng, 9 cây thông tuyết bonsai phân tầng, 3 đỉnh núi đá Hoàng Sơn hùng vĩ.
2. **Nhân Vật (20%)**: Trùm Ngưu Ma Yêu Tướng (tay áo chiến bào ngọc bích tung bay, sừng cong nhọn, ngực khắc ấn phù, vung đại đao nguyệt nha) đối đầu 14 chiến binh Chibi (5 Tiên phong kiếm thủ, 5 Khiên thủ giáo binh thủ cánh trái, 4 Cung thủ phía sau).
3. **Hiệu Ứng VFX (10%)**: 16 dải kiếm khí 3D vút cao 3.8m hình đài sen/liễu rủ, 2 lưỡi đao khí bán nguyệt quét ngang, vòng sóng xung kích mở rộng trên mặt tuyết và cụm 28 mảnh bụi tuyết văng tung tóe.

---

## 3. Hệ Thống 3 Góc Máy Sản Xuất (Camera Rigs)
- **`CAM_Main`**: Tiêu cự 52mm, vị trí `(0.0, -29.0, 18.0)`, góc nghiêng 61.9°. Đây là góc máy sa bàn chuẩn mực tái hiện đúng góc nhìn trong video tham chiếu.
- **`CAM_Close`**: Tiêu cự 50mm, vị trí `(-6.5, -12.5, 4.8)`, góc 3/4 cận cảnh điểm giao tranh giữa Boss và Tiền quân Chibi.
- **`CAM_TopAction`**: Tiêu cự 45mm, vị trí `(0.0, 2.5, 24.0)`, góc nhìn thẳng đứng từ trên xuống kiểm soát đội hình chiến thuật và cung xòe quạt của kiếm khí.
