# Unsloth Starter Kit — RTX 5060 Ti 8GB (Windows)

Bộ khởi động để fine-tune model open-source **ngay trên máy nhà** (Windows + RTX 5060 Ti 8GB, kiến trúc Blackwell).
Copy repo này về máy → làm theo README → train model riêng → xuất ra Ollama/llama.cpp.

> ### ⚡ Cài 1 LỆNH (chạy ở máy nhà — PowerShell)
> ```powershell
> [Net.ServicePointManager]::SecurityProtocol='Tls12'; irm https://raw.githubusercontent.com/sonhai88/unsloth-5060ti-starter/main/bootstrap.ps1 | iex
> ```
> Tự clone repo → tự cài Unsloth Studio → xong. Sau đó bấm icon **"Unsloth Studio"** trên Desktop.
>
> 👉 Hướng dẫn dùng app: [`studio/QUICKSTART.md`](./studio/QUICKSTART.md) · Phần dưới dành cho ai muốn kiểm soát bằng **code/script**.

> **TL;DR:** 8GB VRAM + Unsloth QLoRA = train ngon model **3B**, gắng được **8B** (sát trần).
> Đừng mơ 13B trở lên. Context dài là thứ ăn VRAM, không phải số tham số.

---

## 0. Hai cách dùng — chọn 1

| | Cách A — Studio (bấm nút) | Cách B — Script (repo này) |
|---|---|---|
| Dành cho | Lười code, muốn UI | Muốn kiểm soát bằng code, tự động hoá |
| Cài | 1 dòng PowerShell | venv + pip + chạy `train.py` |
| Train data riêng | Kéo file PDF/CSV/DOCX vào | Sửa `data/sample.jsonl` |

Mới bắt đầu → **chạy Cách A trước** để chắc máy ổn, rồi quay lại Cách B khi cần script.

---

## 1. Card anh train được gì? (8GB VRAM)

| Model | Trên 8GB | Ghi chú |
|---|---|---|
| 1–3B (Llama 3.2 3B, Qwen 3B) | ✅ thoải mái | **Bắt đầu ở đây.** Default của repo. |
| 7–8B (Llama 3.1 8B, Qwen 7B) | ✅ sát trần | Bắt buộc 4-bit, batch 1, `max_seq_length` ≤ 1024 |
| 13B+ | ❌ | OOM (hết VRAM) |
| Chạy chat GGUF Q4 | ✅ 8B chạy mượt | Inference nhẹ hơn train nhiều |

**Quy tắc sống còn trên 8GB:** giảm `max_seq_length` trước khi giảm mọi thứ khác. Train OOM → hạ `max_seq_length` xuống 512–1024.

---

## 2. Chuẩn bị máy (làm 1 lần)

Blackwell (50-series) là card mới → cần đồ mới. Thiếu cái nào là lỗi cài, không phải tại anh.

1. **NVIDIA Driver mới nhất** — Game Ready hoặc Studio driver ≥ 560.xx (Blackwell cần driver mới). [nvidia.com/Download](https://www.nvidia.com/Download/index.aspx)
2. **Python 3.12** (khuyến nghị — ít lỗi nhất với stack này). Cài từ [python.org](https://www.python.org/downloads/), **tick "Add Python to PATH"**. Đừng dùng 3.13 cho chắc.
3. **Git** — [git-scm.com](https://git-scm.com/download/win)
4. **Visual C++ Redistributable** (x64) — [aka.ms/vs/17/release/vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)

Check nhanh trong PowerShell:
```powershell
nvidia-smi          # thấy "RTX 5060 Ti" + driver version
python --version    # Python 3.12.x
git --version
```

---

## 3. Cách A — Unsloth Studio (web UI, không cần code)

Mở **PowerShell** rồi chạy:
```powershell
irm https://unsloth.ai/install.ps1 | iex
unsloth studio -p 8888
```
Mở trình duyệt vào **http://localhost:8888**. Xong. Train/chat bằng cách bấm nút.

> Installer tự lo phần khó của Blackwell (CUDA 12.8 torch, Triton-windows, bitsandbytes). Lần đầu tải vài GB, kiên nhẫn.

---

## 4. Cách B — Script (repo này)

### 4.1. Tạo môi trường + cài

Trong thư mục repo, mở PowerShell:
```powershell
# 1. Tạo virtual env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# Nếu báo lỗi execution policy:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass   rồi chạy lại dòng Activate

# 2. PyTorch build cho Blackwell (CUDA 12.8 — BẮT BUỘC đúng cu128)
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu128

# 3. Unsloth + phụ thuộc
pip install unsloth
pip install triton-windows     # Triton trên Windows cần fork này
```

Kiểm tra GPU thấy chưa:
```powershell
python -c "import torch; print(torch.cuda.get_device_name(0), torch.cuda.is_available())"
# Phải in: NVIDIA GeForce RTX 5060 Ti True
```

### 4.2. Train thử (data mẫu có sẵn)

```powershell
python train.py
```
Mặc định: model **Llama-3.2-3B-Instruct**, data `data/sample.jsonl`, `max_steps=60` (chạy nhanh để thử). LoRA lưu vào `lora_model/`.

### 4.3. Chat thử model vừa train

```powershell
python chat.py
```

### 4.4. Train data của anh

Sửa `data/sample.jsonl` — mỗi dòng 1 ví dụ:
```json
{"instruction": "Câu hỏi / yêu cầu", "output": "Câu trả lời mong muốn"}
```
Có thể thêm `"input"` nếu cần ngữ cảnh. **Nên có ≥ 100 dòng** để model học ra trò (10 dòng chỉ để demo).
Train thật thì bỏ giới hạn bước:
```powershell
python train.py --data data/sample.jsonl --epochs 2 --max-steps 0
```

### 4.5. Xuất sang Ollama (chạy như model thường)

```powershell
python export_gguf.py
# Tạo gguf_model/*.Q4_K_M.gguf → import vào Ollama bằng Modelfile (xem cuối file đó)
```

---

## 5. Tinh chỉnh cho 8GB (sửa trong `train.py` hoặc qua cờ)

| Cần gì | Làm |
|---|---|
| Bị OOM | `--max-seq-length 512` (hạ trước tiên) → rồi `--batch 1` |
| Train 8B thay vì 3B | `--model unsloth/Llama-3.1-8B-Instruct --max-seq-length 1024 --batch 1` |
| Học kỹ hơn | `--epochs 3 --max-steps 0` |
| Học nhẹ (đỡ overfit) | giảm `--lr 1e-4` |

---

## 6. Lỗi hay gặp (Blackwell / Windows)

| Triệu chứng | Nguyên nhân & fix |
|---|---|
| `torch.cuda.is_available() == False` | Cài nhầm torch CPU. Gỡ rồi cài lại đúng `--index-url .../cu128`. |
| `sm_120 is not compatible` / kernel lỗi | torch không phải cu128. Phải dùng wheel cu128 (Blackwell = sm_120). |
| `RuntimeError ... Triton` | Thiếu `triton-windows`. Chạy `pip install triton-windows`. |
| `CUDA out of memory` | Hạ `--max-seq-length` → `--batch 1`. Đóng game/Chrome đang ăn VRAM. |
| `bitsandbytes` import lỗi | `pip install -U bitsandbytes` (cần bản có wheel cu128). |
| GGUF export fail trên Windows | Export GGUF build llama.cpp hơi đỏng đảnh trên Windows. Cách chắc: train ở Cách B, export bằng **Studio (Cách A)** hoặc dùng WSL. |

---

## Nguồn
- [Unsloth — Fine-tuning với Blackwell / RTX 50 series](https://docs.unsloth.ai/basics/fine-tuning-llms-with-blackwell-rtx-50-series-and-unsloth)
- [Notebook gốc Llama 3.2 (code train base ở đây)](https://github.com/unslothai/notebooks)
- [Unsloth Studio](https://github.com/unslothai/unsloth)

> Repo này test syntax trên máy khác (Mac, không CUDA) — script đúng cú pháp nhưng **chưa chạy thật trên 5060 Ti**. Bước train thật anh chạy ở máy nhà; lỗi gì ới em.
