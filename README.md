# Papers Reviewers · V0.1

由 ChatGPT 网页版直接设计和实现的独立实验项目。目标：先验证论文审稿质量，再增加工作流与工程功能。不是对 ChatGPT 内部机制的复制，也不宣称已经达到网页版质量。

## 当前实现

- 原始 PDF 直接作为 OpenAI Responses API 多模态文件输入（base64），不分块、不摘要、不丢弃页面；实际解析效果由 API 决定。
- 单次自主审稿，自由 Markdown 输出；默认不调用外部工具、不启用多智能体、无强制 JSON 报告。
- CLI 默认离线预检；明确 `--execute` 才允许一次 API 请求，不自动重试。可选本地 Streamlit 页面。
- 本地保存报告、论文及提示词 SHA-256、实际模型、状态、Token 用量和可选估算费用；未完成响应仅保存 `partial.md`。
- 基准评价与生成隔离。`benchmark/README.md` 为开发案例与人工盲评协议，不注入审稿请求。

## 安装与 API 密钥（macOS / Linux）

要求 Python 3.10+。CLI 和离线测试无需第三方包。

```bash
cd papers-reviewers-v0.1  # 如果通过 git clone 获取，则改为实际仓库目录
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
chmod 600 .env
```

用本地编辑器打开 `.env`，填写 `OPENAI_API_KEY` 和实际可用的 `OPENAI_MODEL`。模型 ID 必须来自你的 API 账户，并支持 Responses API 的 PDF/图像输入。不要把 ChatGPT 界面名称当作 API ID。根据模型支持情况设定 `REVIEW_EFFORT`（`default` 表示不发送 reasoning 参数）、`REVIEW_MAX_OUTPUT_TOKENS`。未指定模型则拒绝执行。真实密钥从不提交或粘贴给别人；系统环境变量优先于 `.env`。

密钥管理：https://platform.openai.com/api-keys 。ChatGPT 订阅不含 API 用量；使用前确认计费账户及预算。

Windows PowerShell：`py -m venv .venv`，使用 `.\.venv\Scripts\python.exe` 执行下面命令（或激活虚拟环境），`Copy-Item .env.example .env`。保护本地目录 ACL。不要提交 `.env`。

## 离线测试 / 预检

```bash
python -m unittest discover -s tests -v
python main.py /path/to/paper.pdf
```

第二条默认只校验 PDF 文件头、大小、配置和哈希；不验证 PDF 全文可读性，不发送请求，不产生 API 费用。20 MiB 是本地保守输入限制，不会静默截断；超长论文支持留待后续实验。

## 首次真实审稿（一次付费调用）

确认论文有权发送至外部 API，并确认费用和模型后执行：

```bash
python main.py /path/to/paper.pdf --execute
```

可用 `--model API_MODEL_ID`、`--effort high`、`--max-output-tokens 32000`、`--prompt prompts/review_core.md` 进行控制变量实验。输出在 `runs/<run-id>/`：`started.json`（请求前元数据）、`result.json`（最终状态、用量）、`review.md` 或 `partial.md`。若只剩 started.json，说明进程中断，费用未知；不要直接重跑。HTTP 错误、超时或未完成结果不会自动重试；真实费用以 API 账单为准。输出 Token 预算包含推理 Token，不是美元硬上限。可选的输入/输出费率必须由使用者根据官方模型价格填写；估算未考虑缓存折扣、特殊费率等，不能替代账单或保证成本上限。

## 可选本地网页

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

浏览器打开终端显示的本地链接。选 PDF、模型和提示词，确认本次费用后点击开始。不要将这一测试 UI 直接暴露在公网；它没有账号认证、多人隔离或服务端限额。

## 安全与边界

- 固定官方 API HTTPS endpoint；不允许自动跳转或回退；不向模型内容发送密钥。`store:false` 禁用 Responses 的响应存储设置，不等于无任何服务端留存；查看账户及官方数据处理政策。不要发送保密稿件，除非有权限且政策允许。
- Git 忽略真实密钥、PDF、报告、运行日志等；不要使用 `git add -f` 绕过。未公开报告仅本地保存。公开 GitHub 仅提交源代码与通用评价基准。
- 没有联网检索、外部文献独立核验、代码执行或多轮会话；审稿输出必须注明边界。模型返回 completed 仅表示 API 完成，不表示学术正确。
- 当前提示词根据已讨论要求重建，不是网页版原始内部系统提示词。网页和 API 模型实际配置可能不同，质量需匹配条件盲评。

## P0/P1 与后续

P0: 基准协议及开发案例（草案）。P1: 最简审稿引擎、CLI、可选界面及离线测试。下一步先执行真实单次调用，和同输入同提示词的网页版独立结果对照；未达到质量门槛前，不进入复杂产品开发。

官方接口说明：https://developers.openai.com/api/docs/guides/file-inputs 、https://developers.openai.com/api/docs/guides/reasoning 。
