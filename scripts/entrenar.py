"""Train one LoRA configuration (A or B) with TRL's SFTTrainer.

The dataset is converted to the conversational prompt-completion format, so the
loss is computed only on the SQL (completion_only_loss):
    prompt     = build_messages(esquema, pregunta)   (same prompt as solucion.py)
    completion = [{"role": "assistant", "content": sql}]

Only one factor changes between the two configurations: target_modules.

Outputs:
    checkpoints/config_<X>/                  adapter + tokenizer (not in git)
    resultados/entrenamiento_config_<X>.json trainable params, time, losses, args
    resultados/log_config_<X>.json           full trainer log history
    resultados/curvas_loss_<X>.png           train / eval loss curves

Usage:
    python scripts/entrenar.py --config A
    python scripts/entrenar.py --config B --batch 2 --accum 8 --fp16   # T4 (Kaggle/Colab)
    python scripts/entrenar.py --config A --limite 200 --salida checkpoints/prueba  # smoke test
"""
import argparse
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from prompt import build_messages  # noqa: E402

CONFIGS = {
    "A": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "B": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
}


def leer_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def dividir(registros: list[dict], eval_path: Path | None, frac: float, semilla: int):
    """Train/eval split. Priority: explicit eval file, a split field, 5 % per schema."""
    if eval_path is not None and eval_path.exists():
        return registros, leer_jsonl(eval_path)
    for campo in ("particion", "split"):
        if any(campo in r for r in registros):
            train = [r for r in registros if r.get(campo, "train") != "eval"]
            ev = [r for r in registros if r.get(campo) == "eval"]
            return train, ev
    # Fallback: hold out ~frac of every schema so all schemas appear in both.
    por_db = defaultdict(list)
    for r in registros:
        por_db[r["db_id"]].append(r)
    rng = random.Random(semilla)
    train, ev = [], []
    for db in sorted(por_db):
        grupo = por_db[db][:]
        rng.shuffle(grupo)
        k = max(1, round(len(grupo) * frac)) if len(grupo) >= 10 else 0
        ev += grupo[:k]
        train += grupo[k:]
    return train, ev


def a_prompt_completion(r: dict) -> dict:
    return {
        "prompt": build_messages(r["esquema"], r["pregunta"]),
        "completion": [{"role": "assistant", "content": r["sql"]}],
    }


def longitud_tokens(tokenizer, r: dict) -> int:
    ej = a_prompt_completion(r)
    # Render to text first: with tokenize=True transformers 5 returns a
    # BatchEncoding, whose len() is the number of keys, not of tokens.
    texto = tokenizer.apply_chat_template(ej["prompt"] + ej["completion"], tokenize=False)
    return len(tokenizer(texto, add_special_tokens=False)["input_ids"])


def graficar(historial: list[dict], titulo: str, destino: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    tr = [(h["step"], h["loss"]) for h in historial if "loss" in h]
    ev = [(h["step"], h["eval_loss"]) for h in historial if "eval_loss" in h]
    fig, ax = plt.subplots(figsize=(7, 4))
    if tr:
        ax.plot(*zip(*tr), label="train", color="#2a6fdb", linewidth=1.5)
    if ev:
        ax.plot(*zip(*ev), label="eval", color="#e0782d", linewidth=2, marker="o", markersize=4)
    ax.set_xlabel("paso de optimización")
    ax.set_ylabel("loss (solo SQL)")
    ax.set_title(titulo)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=sorted(CONFIGS), required=True)
    ap.add_argument("--datos", type=Path, default=ROOT / "datos" / "entrenamiento.jsonl")
    ap.add_argument("--eval", type=Path, default=ROOT / "datos" / "eval_loss.jsonl",
                    help="optional eval file; otherwise a split field or 5 %% per schema")
    ap.add_argument("--salida", type=Path, default=None)
    ap.add_argument("--resultados", type=Path, default=ROOT / "resultados")
    ap.add_argument("--max-length", type=int, default=2048)
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    # 1 x 16 by default: with ~2k-token schemas, 2 x 8 peaks at ~7.6 GiB on an 8 GB card.
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--accum", type=int, default=16)
    ap.add_argument("--eval-steps", type=int, default=50)
    ap.add_argument("--limite", type=int, default=None, help="use only N training pairs")
    ap.add_argument("--fp16", action="store_true", help="fp16 instead of bf16 (T4)")
    args = ap.parse_args()

    import torch
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    from trl import SFTConfig, SFTTrainer
    from datasets import Dataset

    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    semilla = cfg["semilla"]
    set_seed(semilla)
    salida = args.salida or ROOT / "checkpoints" / f"config_{args.config}"
    etiqueta = args.config if args.limite is None else f"{args.config}_prueba"

    tokenizer = AutoTokenizer.from_pretrained(cfg["modelo_base"])

    registros = leer_jsonl(args.datos)
    train, ev = dividir(registros, args.eval, 0.05, semilla)
    if args.limite is not None:
        random.Random(semilla).shuffle(train)
        train = train[:args.limite]
        ev = ev[:max(10, args.limite // 10)]

    # Truncation would cut the SQL (the only part with loss), so long pairs are
    # dropped and reported instead. A's filter should already remove them.
    largos = {"train": 0, "eval": 0}
    for nombre, conjunto in (("train", train), ("eval", ev)):
        keep = [r for r in conjunto if longitud_tokens(tokenizer, r) <= args.max_length]
        largos[nombre] = len(conjunto) - len(keep)
        conjunto[:] = keep
    print(f"train={len(train)} eval={len(ev)} descartados por max_length={largos}")

    ds_train = Dataset.from_list([a_prompt_completion(r) for r in train])
    ds_eval = Dataset.from_list([a_prompt_completion(r) for r in ev])

    usar_bf16 = not args.fp16 and torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    model = AutoModelForCausalLM.from_pretrained(
        cfg["modelo_base"],
        dtype=torch.bfloat16 if usar_bf16 else torch.float16,
        attn_implementation="sdpa",
    )

    lora = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=CONFIGS[args.config],
        bias="none",
        task_type="CAUSAL_LM",
    )

    sft = SFTConfig(
        output_dir=str(salida),
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_steps=0.03,  # float in [0, 1) = ratio of total steps (transformers 5)
        per_device_train_batch_size=args.batch,
        per_device_eval_batch_size=args.batch,
        gradient_accumulation_steps=args.accum,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        bf16=usar_bf16,
        fp16=not usar_bf16,
        max_length=args.max_length,
        packing=False,
        completion_only_loss=True,
        eval_strategy="steps",
        eval_steps=args.eval_steps,
        logging_steps=10,
        logging_first_step=True,
        save_strategy="steps",
        save_steps=200,
        save_total_limit=1,
        seed=semilla,
        data_seed=semilla,
        report_to="none",
        dataloader_num_workers=0,
    )

    trainer = SFTTrainer(
        model=model,
        args=sft,
        train_dataset=ds_train,
        eval_dataset=ds_eval,
        processing_class=tokenizer,
        peft_config=lora,
    )
    entrenables, total = trainer.model.get_nb_trainable_parameters()
    trainer.model.print_trainable_parameters()

    torch.cuda.reset_peak_memory_stats() if torch.cuda.is_available() else None
    inicio = time.time()
    trainer.train()
    segundos = time.time() - inicio
    metricas_eval = trainer.evaluate()

    trainer.save_model(str(salida))
    tokenizer.save_pretrained(str(salida))

    historial = trainer.state.log_history
    train_losses = [h["loss"] for h in historial if "loss" in h]
    tokens = max((h.get("num_tokens", 0) for h in historial if "loss" in h), default=0)
    resumen = {
        "config": args.config,
        "target_modules": CONFIGS[args.config],
        "parametros_entrenables": entrenables,
        "parametros_totales": total,
        "porcentaje_entrenable": round(100 * entrenables / total, 4),
        "tiempo_segundos": round(segundos, 1),
        "tiempo_legible": time.strftime("%H:%M:%S", time.gmtime(segundos)),
        "pasos": trainer.state.global_step,
        "pares_train": len(train),
        "pares_eval": len(ev),
        "descartados_max_length": largos,
        "loss_train_final": train_losses[-1] if train_losses else None,
        "loss_eval_final": metricas_eval.get("eval_loss"),
        "tokens_entrenados": int(tokens),
        "tokens_por_segundo": round(tokens / segundos, 1) if tokens else None,
        "memoria_pico_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2)
        if torch.cuda.is_available() else None,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "precision": "bf16" if usar_bf16 else "fp16",
        "hiperparametros": {
            "r": 16, "lora_alpha": 32, "lora_dropout": 0.05,
            "learning_rate": args.lr, "scheduler": "cosine", "warmup_ratio": 0.03,
            "epochs": args.epochs, "batch": args.batch, "accum": args.accum,
            "batch_efectivo": args.batch * args.accum, "max_length": args.max_length,
            "seed": semilla,
        },
        "adapter": str(salida.relative_to(ROOT)) if salida.is_relative_to(ROOT) else str(salida),
    }

    args.resultados.mkdir(parents=True, exist_ok=True)
    (args.resultados / f"entrenamiento_config_{etiqueta}.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.resultados / f"log_config_{etiqueta}.json").write_text(
        json.dumps(historial, indent=1), encoding="utf-8")
    graficar(historial, f"Config {args.config}: {', '.join(CONFIGS[args.config])}",
             args.resultados / f"curvas_loss_{etiqueta}.png")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
