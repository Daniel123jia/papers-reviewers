"""Optional local test UI; launch with streamlit run app.py --server.address 127.0.0.1."""
import streamlit as st
from reviewer.core import ROOT, ReviewError, load_settings, config_from_settings, validate_pdf, run_review

st.set_page_config(page_title="Papers Reviewers v0.1", layout="wide")
st.title("Papers Reviewers · V0.1")
st.caption("最简审稿质量实验 | 原始 PDF → 单次 Responses API → Markdown")
s = load_settings()
with st.sidebar:
    model = st.text_input("API 模型 ID", value=s.get("OPENAI_MODEL", ""))
    effort = st.selectbox("推理强度（须为模型支持的档位）", ["high", "xhigh", "medium", "low", "default"])
    budget = st.number_input("最大输出 Token（含推理 Token）", 1, 128000, 32000, 1000)
    st.write("密钥配置：" + ("已读取（未显示）" if s.get("OPENAI_API_KEY") else "未配置 .env"))
    st.caption("仅本地运行。不自动重试，不自动调用网络工具。")
file = st.file_uploader("选择有权发送至 API 的 PDF", type=["pdf"])
prompt = st.text_area("审稿提示词（可编辑）", (ROOT / "prompts/review_core.md").read_text(encoding="utf-8"), height=300)
consent = st.checkbox("我有权发送此论文，并明确同意本次付费 API 调用；Token 上限不是美元硬限额。")
if st.button("开始一次审稿", disabled=not (file and consent), type="primary"):
    try:
        data = validate_pdf(file.getvalue())
        cfg = config_from_settings(s, model=model, effort=effort, max_output_tokens=int(budget))
        with st.spinner("正在等待 API 响应（不会自动重试）"):
            folder, meta = run_review(data, prompt, cfg, s.get("OPENAI_API_KEY", ""), ROOT / "runs", authorized=consent)
        st.session_state["last_result"] = (str(folder), meta)
    except (ReviewError, OSError) as e:
        st.error(str(e) if isinstance(e, ReviewError) else "本地文件操作失败。")
if "last_result" in st.session_state:
    from pathlib import Path
    folder, meta = st.session_state["last_result"]
    st.write("运行状态：", meta["status"])
    st.json(meta["usage"])
    path = Path(folder) / ("review.md" if meta["status"] == "completed" else "partial.md")
    if path.is_file():
        report = path.read_text(encoding="utf-8")
        if meta["status"] != "completed":
            st.warning("以下为不完整输出，不视为正式审稿。")
        st.text_area("审稿报告（原始 Markdown，避免加载模型生成的外部资源）", report, height=650, disabled=True)
        st.download_button("下载 Markdown", report, file_name=path.name, mime="text/markdown")
    st.caption("本地结果目录：" + folder)
