# Unsloth Studio — App fine-tune trên Windows (RTX 5060 Ti 8GB)

App có sẵn của Unsloth: chọn data → bấm Train → xuất model. Không cần code.
**Không phải tự build** — đây là app chính hãng, đường ngắn nhất.

---

## Cài 1 lần (5 phút bấm + chờ tải)

### Trước khi cài (làm 1 lần)
1. **NVIDIA Driver mới nhất** (Blackwell cần driver mới) → [nvidia.com/Download](https://www.nvidia.com/Download/index.aspx)
2. Check: mở `cmd`, gõ `nvidia-smi` → phải thấy "RTX 5060 Ti".

### Cài Studio
- **Double-click [`INSTALL.bat`](./INSTALL.bat)** trong thư mục này.
- Lần đầu nó tải PyTorch + CUDA + Unsloth (~vài GB) — để yên cho chạy, đừng tắt.
- Xong → có **icon "Unsloth Studio" trên Desktop**.

> Không thích .bat? Mở **PowerShell** gõ 1 dòng:
> `[Net.ServicePointManager]::SecurityProtocol='Tls12'; irm https://unsloth.ai/install.ps1 | iex`

---

## Dùng hằng ngày = 1 cú double-click

Double-click icon **"Unsloth Studio"** trên Desktop → cửa sổ terminal hiện ra → **trình duyệt tự mở app**. Xong, đó là app của anh.

(Nếu trình duyệt không tự mở: vào thẳng **http://localhost:8888**)

---

## Trong app làm gì (luồng chuẩn)

| Bước | Làm trong UI |
|---|---|
| 1. Lấy model | Tab **Models** → tải **Llama 3.2 3B Instruct** (an toàn nhất cho 8GB). Đừng tải >8B. |
| 2. Tạo data | Tab **Data Recipes** → kéo PDF/CSV/DOCX vào, hoặc nhập cặp hỏi–đáp. |
| 3. Train | Tab **Train** → chọn model + data → **đặt `max_seq_length` = 1024** (8GB!) → Start. Xem **loss** tụt dần. |
| 4. Chat thử | Tab **Chat** → hỏi vài câu xem model học chưa. |
| 5. Xuất | **Export → GGUF (Q4_K_M)** → dùng cho Ollama (xem dưới). |

### Model nào vừa 8GB
- **3B** → thoải mái, bắt đầu ở đây.
- **8B** → được nhưng sát trần: 4-bit + `max_seq_length` ≤ 1024.
- **13B+** → ❌ hết VRAM.
- Train báo **out of memory** → hạ `max_seq_length` (1024 → 512) TRƯỚC, rồi mới giảm batch.

---

## Nối model vào Ollama (chạy như model thường)

Sau khi Export GGUF, dùng [`Modelfile`](./Modelfile) trong thư mục này:
```bat
REM đặt Modelfile cạnh file .gguf, sửa tên file trong đó cho đúng, rồi:
ollama create my-model -f Modelfile
ollama run my-model
```

---

## Lỗi hay gặp (Blackwell)

| Triệu chứng | Fix |
|---|---|
| Cài lỗi / kernel `sm_120` | Driver NVIDIA cũ → update driver, cài lại. Installer tự lấy CUDA 12.8 đúng cho Blackwell. |
| Cài bị lỗi Python | Mở PowerShell, ép Python 3.12: `$env:UNSLOTH_PYTHON='3.12'; irm https://unsloth.ai/install.ps1 | iex` |
| Train `out of memory` | Hạ `max_seq_length` xuống 512, đóng game/Chrome đang ăn VRAM. |
| Icon Desktop không mở app | Vào thẳng http://localhost:8888 sau khi double-click icon. |

---

## Nguồn
- [Unsloth Studio](https://github.com/unslothai/unsloth) · [Blackwell / RTX 50 guide](https://docs.unsloth.ai/basics/fine-tuning-llms-with-blackwell-rtx-50-series-and-unsloth)

> Studio đang **Beta** — gặp bug là bình thường. Cần kiểm soát bằng code thay vì UI thì xem `train.py` ở thư mục gốc repo.
