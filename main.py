from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from reviewer.core import ROOT, ReviewError, load_settings, config_from_settings, read_pdf, sha, run_review


def main() -> int:
    p = argparse.ArgumentParser(description="Papers Reviewers v0.1 — local single-pass PDF review")
    p.add_argument("pdf", type=Path)
    p.add_argument("--model")
    p.add_argument("--effort")
    p.add_argument("--max-output-tokens", type=int)
    p.add_argument("--prompt", type=Path, default=ROOT / "prompts/review_core.md")
    p.add_argument("--output-dir", type=Path, default=ROOT / "runs")
    p.add_argument("--execute", action="store_true", help="Explicitly authorize one paid API request. Default is offline dry run.")
    a = p.parse_args()
    try:
        s = load_settings()
        cfg = config_from_settings(s, model=a.model, effort=a.effort, max_output_tokens=a.max_output_tokens)
        data, prompt = read_pdf(a.pdf), a.prompt.read_text(encoding="utf-8")
        if not prompt.strip():
            raise ReviewError("审稿提示词为空。")
        print(json.dumps({"mode": "execute" if a.execute else "dry_run", "model": cfg.model,
                          "effort": cfg.effort, "max_output_tokens": cfg.max_output_tokens,
                          "paper_bytes": len(data), "paper_sha256": sha(data), "prompt_sha256": sha(prompt.encode())}, ensure_ascii=False, indent=2))
        if not a.execute:
            print("离线检查完成：未发送论文、未调用 API、未产生 API 费用。")
            return 0
        folder, meta = run_review(data, prompt, cfg, s.get("OPENAI_API_KEY", ""), a.output_dir, authorized=True)
        print("结果目录:", folder)
        print("状态:", meta["status"], "用量:", json.dumps(meta["usage"], ensure_ascii=False))
        return 0 if meta["status"] == "completed" else 2
    except (ReviewError, OSError, UnicodeError) as e:
        print(str(e) if isinstance(e, ReviewError) else "读取或写入本地文件失败。", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
