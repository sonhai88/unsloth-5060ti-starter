"""
Chat thử model vừa fine-tune (load LoRA từ lora_model/).

Chạy:  python chat.py
Thoát: gõ 'exit' hoặc Ctrl+C
"""
import argparse

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from transformers import TextStreamer


def parse_args():
    p = argparse.ArgumentParser(description="Chat với model đã fine-tune")
    p.add_argument("--model", default="lora_model", help="Thư mục LoRA đã lưu")
    p.add_argument("--max-seq-length", type=int, default=1024)
    p.add_argument("--chat-template", default="llama-3.1")
    p.add_argument("--max-new-tokens", type=int, default=256)
    return p.parse_args()


def main():
    args = parse_args()

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )
    tokenizer = get_chat_template(tokenizer, chat_template=args.chat_template)
    FastLanguageModel.for_inference(model)   # bật chế độ inference (nhanh gấp 2)

    print("💬 Model sẵn sàng. Gõ câu hỏi (exit để thoát).\n")
    streamer = TextStreamer(tokenizer, skip_prompt=True)

    while True:
        try:
            user = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user.lower() in {"exit", "quit", "q"}:
            break
        if not user:
            continue

        messages = [{"role": "user", "content": user}]
        inputs = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to("cuda")

        print("Model: ", end="")
        model.generate(
            input_ids=inputs,
            streamer=streamer,
            max_new_tokens=args.max_new_tokens,
            use_cache=True,
            temperature=0.7,
            min_p=0.1,
        )
        print()


if __name__ == "__main__":
    main()
