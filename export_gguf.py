"""
Xuất model fine-tune sang GGUF (Q4_K_M) để chạy trên Ollama / llama.cpp.

Chạy:  python export_gguf.py
Kết quả: gguf_model/<tên>.Q4_K_M.gguf

LƯU Ý Windows: bước này tự build llama.cpp, đôi khi đỏng đảnh trên Windows thuần.
Nếu fail → export bằng Unsloth Studio (Cách A trong README) hoặc dùng WSL.
"""
import argparse

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template


def parse_args():
    p = argparse.ArgumentParser(description="Xuất LoRA -> GGUF")
    p.add_argument("--model", default="lora_model", help="Thư mục LoRA đã lưu")
    p.add_argument("--out", default="gguf_model", help="Thư mục xuất GGUF")
    p.add_argument("--max-seq-length", type=int, default=1024)
    p.add_argument("--quant", default="q4_k_m",
                   help="Mức nén: q4_k_m (cân bằng, khuyến nghị), q5_k_m, q8_0, f16")
    return p.parse_args()


def main():
    args = parse_args()

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    # Gộp LoRA vào model nền rồi xuất GGUF đã nén
    model.save_pretrained_gguf(args.out, tokenizer, quantization_method=args.quant)

    print(f"\n✅ GGUF xuất ở: {args.out}/")
    print("\n--- Import vào Ollama ---")
    print(f"1) Tạo file 'Modelfile' cạnh file .gguf với nội dung:")
    print(f'   FROM ./{args.out}/<đổi-thành-tên-file>.{args.quant.upper()}.gguf')
    print("2) Chạy:")
    print("   ollama create my-model -f Modelfile")
    print("   ollama run my-model")


if __name__ == "__main__":
    main()
