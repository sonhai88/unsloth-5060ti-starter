"""
QLoRA fine-tune với Unsloth — tối ưu cho RTX 5060 Ti 8GB (Blackwell).

Mặc định train Llama-3.2-3B-Instruct trên data/sample.jsonl.
Code base lấy từ notebook chính thức của Unsloth (Llama 3.2 Conversational).

Chạy:  python train.py
Train thật:  python train.py --epochs 2 --max-steps 0
"""
import argparse

# QUAN TRỌNG: import unsloth TRƯỚC torch/transformers để nó kịp patch tối ưu.
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template, train_on_responses_only
from datasets import load_dataset
from trl import SFTConfig, SFTTrainer
from transformers import DataCollatorForSeq2Seq


def parse_args():
    p = argparse.ArgumentParser(description="Unsloth QLoRA fine-tune (8GB friendly)")
    p.add_argument("--model", default="unsloth/Llama-3.2-3B-Instruct",
                   help="Model nền. 8GB: dùng 3B (mặc định) hoặc 8B + max-seq-length nhỏ.")
    p.add_argument("--data", default="data/sample.jsonl",
                   help="File JSONL, mỗi dòng {instruction, output, input?}")
    p.add_argument("--out", default="lora_model", help="Thư mục lưu LoRA")
    p.add_argument("--max-seq-length", type=int, default=1024,
                   help="Độ dài context. Ăn VRAM nhất — OOM thì hạ cái này TRƯỚC (512).")
    p.add_argument("--batch", type=int, default=2, help="per_device_train_batch_size")
    p.add_argument("--grad-accum", type=int, default=4, help="gradient_accumulation_steps")
    p.add_argument("--lr", type=float, default=2e-4, help="learning rate")
    p.add_argument("--epochs", type=float, default=1.0, help="số epoch (bỏ qua nếu max-steps>0)")
    p.add_argument("--max-steps", type=int, default=60,
                   help="Số bước train. >0 = chạy nhanh để thử. 0 = train hết theo --epochs.")
    p.add_argument("--chat-template", default="llama-3.1",
                   help="Template chat. llama-3.1 cho Llama 3.x; qwen-2.5 cho Qwen; gemma-3 cho Gemma.")
    return p.parse_args()


def main():
    args = parse_args()

    # 1) Load model 4-bit (QLoRA)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,            # tự chọn theo GPU
        load_in_4bit=True,     # 4-bit = tiết kiệm VRAM, chìa khoá chạy được trên 8GB
    )

    # 2) Gắn LoRA adapter
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",   # tiết kiệm thêm VRAM
        random_state=3407,
        use_rslora=False,
        loftq_config=None,
    )

    # 3) Chat template + biến data thành chuỗi "text"
    tokenizer = get_chat_template(tokenizer, chat_template=args.chat_template)

    def formatting_prompts_func(examples):
        instructions = examples["instruction"]
        outputs = examples["output"]
        inputs = examples.get("input", [""] * len(instructions))
        texts = []
        for ins, inp, out in zip(instructions, inputs, outputs):
            user = ins if not inp else f"{ins}\n\n{inp}"
            convo = [
                {"role": "user", "content": user},
                {"role": "assistant", "content": out},
            ]
            texts.append(tokenizer.apply_chat_template(
                convo, tokenize=False, add_generation_prompt=False))
        return {"text": texts}

    dataset = load_dataset("json", data_files=args.data, split="train")
    dataset = dataset.map(formatting_prompts_func, batched=True)
    print(f"[data] {len(dataset)} ví dụ từ {args.data}")

    # 4) Trainer
    cfg = SFTConfig(
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        warmup_steps=5,
        learning_rate=args.lr,
        logging_steps=1,
        optim="adamw_8bit",          # optimizer 8-bit = nhẹ VRAM
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
        report_to="none",
    )
    if args.max_steps > 0:
        cfg.max_steps = args.max_steps
    else:
        cfg.num_train_epochs = args.epochs

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
        packing=False,
        args=cfg,
    )

    # Chỉ tính loss trên câu trả lời của assistant (không học phần prompt của user)
    if args.chat_template.startswith("llama"):
        trainer = train_on_responses_only(
            trainer,
            instruction_part="<|start_header_id|>user<|end_header_id|>\n\n",
            response_part="<|start_header_id|>assistant<|end_header_id|>\n\n",
        )

    # 5) Train
    trainer.train()

    # 6) Lưu LoRA
    model.save_pretrained(args.out)
    tokenizer.save_pretrained(args.out)
    print(f"\n✅ Xong. LoRA lưu ở: {args.out}/")
    print("   Chat thử:  python chat.py")
    print("   Xuất GGUF: python export_gguf.py")


if __name__ == "__main__":
    main()
