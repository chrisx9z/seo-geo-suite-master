# XianxiaBlender — Quality Assurance & Verification Rubric

Agent phải sử dụng danh mục kiểm tra này sau mỗi lần render preview để tự động đánh giá và quyết định có cần tinh chỉnh code trước khi hoàn thiện.

---

## 1. Kiểm Tra Bố Cục & Tỷ Lệ (Composition & Scale)
- [x] **Quy tắc 70/20/10**: Môi trường chiếm ~70% khung hình, nhân vật chiếm ~20%, VFX chiếm ~10% ở `CAM_Main`.
- [x] **Góc nhìn Diorama**: Camera `CAM_Main` có tiêu cự từ 50-55mm, góc chúc 55-62°, tạo cảm giác sa bàn đồ chơi thu nhỏ rõ nét.
- [x] **Tỷ lệ Chibi**: Binh lính nhỏ bé (1.4m), chiều cao bằng 2.5 đến 3.5 lần chiều cao đầu.
- [x] **Tỷ lệ Boss**: Ngưu Ma Yêu Tướng cao vượt trội (khoảng 3.5 - 5 lần lính thường, ~5.2m), vai nở rộng hình thang, cặp sừng trâu khổng lồ.

---

## 2. Kiểm Tra Ánh Sáng & Vật Liệu (Lighting & Shaders)
- [x] **Dải màu AgX Punchy**: Màu đen có chiều sâu kiểu mực tàu, màu tuyết mùa đông xám xanh dịu mát, không bị cháy sáng loang lổ.
- [x] **Toon Shading**: Bóng đổ phân tầng mượt mà, không bóng loáng photorealistic (Roughness bề mặt cao 0.85-0.95).
- [x] **Phát quang Ngọc Bích (Emission Bloom)**: Các điểm nhấn ngọc bích (mắt boss, ấn phù ngực, sống đao) và dải kiếm khí phát sáng nổi bật trong EEVEE.
- [x] **Lầu các cổ phong**: Mái ngói đen phiến tuyết phủ cong vút đầu đao, cột gỗ son trầm, lồng đèn vàng ấm áp.

---

## 3. Kiểm Tra Hiệu Ứng & Diễn Hoạt (VFX & Animation)
- [x] **Đao khí & Kiếm khí**: Dải lụa kiếm khí uốn lượn lõi trắng viền cyan theo đúng quỹ đạo quét của đại đao.
- [x] **Độ va chạm (Hit-Stop)**: Frame 41 thể hiện rõ khoảnh khắc khựng đao cực điểm, hạt tuyết văng và vòng sóng xung kích bùng nở.
- [x] **Phản ứng đội quân**: Khiên binh có độ lùi nảy và tư thế gồng mình đỡ đòn khi sóng đao khí quét qua.

---

## 4. Kiểm Tra Xuất Bản & Tính Tương Thích (Export QA)
- [x] File `.blend` lưu đầy đủ texture và hierarchy `SCENE_MASTER` sạch sẽ.
- [x] File `.glb` và `.obj` xuất ra mở được trên viewer 3D ngoài mà không bị đảo ngược mặt (flipped normals).
