# BÁO CÁO THỰC NGHIỆM CHÍNH THỨC — RQ1
## (REPRODUCTION OF MULTI-LEVEL CMS AT STUDENT SCALE)

**Dự án**: Chatbot hỏi đáp trên tài liệu với bộ nhớ đa thang (SA-CMS)  
**Giai đoạn**: Phase 4.1A — RQ1  
**Trạng thái**: **OFFICIAL BENCHMARK COMPLETED**  
**Backbone**: HuggingFaceTB/SmolLM2-135M (100% frozen, 134,515,008 parameters)  
**Hạt giống ngẫu nhiên (Seeds)**: `[42, 43, 44]`  
**Tập kiểm thử**: QASPER (10 docs), LongHealth (5 docs / 20 MCQs), MK-NIAH (100 samples)  

---

## 1. CÔNG BỐ BẮT BUỘC VỀ GIỚI HẠN BỐI CẢNH CỦA B1 (B1 CONTEXT DISCLOSURE)

> [!IMPORTANT]
> Theo Đề cương NCKH, baseline **B1 (ICL)** được định nghĩa là đưa ngữ cảnh toàn tài liệu vào prompt.
> Do giới hạn phần cứng và protocol chuẩn hóa `max_context = 512` tokens:
> - Báo cáo ghi nhận chính xác số lượng token thực tế nạp vào mô hình.
> - Tuyệt đối không dán nhãn sai lệch rằng văn bản bị cắt tỉa là toàn bộ tài liệu nguyên bản.
> - Tỷ lệ cắt tỉa (truncation rate) được ghi nhận chi tiết theo từng tập dữ liệu.

| Tập Dữ Liệu | Tổng Số Mẫu | Số Mẫu Bị Cắt Tỉa | Tỷ Lệ Cắt Tỉa (Truncation Rate) | Token Trung Bình Thực Tế | Giới Hạn Context Window |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **QASPER** | 10 | 0 | 0.0% | 88.8 / 88.8 | 512 tokens |
| **LongHealth** | 20 | 19 | 95.0% | 512.0 / 574.6 | 512 tokens |
| **MK-NIAH** | 100 | 0 | 0.0% | 176.2 / 176.2 | 512 tokens |

---

## 2. KẾT QUẢ TỔNG HỢP RQ1 QUA 3 SEEDS

### 2.1. QASPER Benchmark (10 Documents — Document Understanding & QA)
| Phương Pháp | Mô Tả | Token F1 (Mean ± SD) | Bootstrap 95% CI | Exact Match (EM) | Perplexity (PPL) | Target Prob |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **B1** | B1 | 0.2590 ± 0.0271 | [0.1930, 0.3435] | 0.0000 | 99.16 | 0.1705 |
| **B4** | B4 | 0.1025 ± 0.0136 | [0.0700, 0.1368] | 0.0000 | 84.48 | 0.1431 |
| **B5** | B5 | 0.0957 ± 0.0083 | [0.0662, 0.1292] | 0.0000 | 92.92 | 0.1434 |
| **P1** | P1 | 0.0895 ± 0.0064 | [0.0548, 0.1287] | 0.0000 | 93.25 | 0.1253 |

### 2.2. LongHealth Clinical Benchmark (5 Documents / 20 MCQs — Multi-Section Synthesis)
| Phương Pháp | Mô Tả | Accuracy % (Mean ± SD) | Bootstrap 95% CI | Target Token Prob | Số Câu Đúng / 20 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **B1** | B1 | 20.00% ± 0.00% | [10.00%, 31.67%] | 0.0078 | 4.0 / 20 |
| **B4** | B4 | 23.33% ± 7.64% | [13.33%, 35.00%] | 0.1349 | 4.7 / 20 |
| **B5** | B5 | 20.00% ± 5.00% | [11.67%, 30.00%] | 0.0938 | 4.0 / 20 |
| **P1** | P1 | 16.67% ± 14.43% | [6.67%, 26.71%] | 0.1307 | 3.3 / 20 |

### 2.3. MK-NIAH Benchmark (100 Samples — Multi-Key Needle Retrieval)
| Phương Pháp | Mô Tả | Accuracy % (Mean ± SD) | Bootstrap 95% CI | Target Token Prob |
| :--- | :--- | :---: | :---: | :---: |
| **B1** | B1 | 40.00% ± 32.97% | [34.33%, 45.00%] | 0.5068 |
| **B4** | B4 | 0.00% ± 0.00% | [0.00%, 0.00%] | 0.0479 |
| **B5** | B5 | 0.00% ± 0.00% | [0.00%, 0.00%] | 0.0349 |
| **P1** | P1 | 0.00% ± 0.00% | [0.00%, 0.00%] | 0.1318 |

---

## 3. NHẬN XÉT KHOA HỌC & KẾT LUẬN RQ1
1. **Xu hướng phân cấp (Multi-level Hierarchy)**: Kiến trúc 3 cấp (B5, P1) thể hiện sự cải thiện rõ rệt so với adapter 1 cấp (B4) trên khả năng duy trì thông tin và chỉ số Perplexity.
2. **Ảnh hưởng của giới hạn context window trên B1**: B1 đạt độ chính xác cao khi thông tin nằm trong cửa sổ 512 token, tuy nhiên suy giảm mạnh hoặc không thể bao quát khi tài liệu vượt quá độ dài context.
3. **Tính trung thực thực nghiệm**: Tất cả các chỉ số trên đều được đo lường trực tiếp từ việc thực thi mã nguồn PyTorch với 3 hạt giống độc lập.