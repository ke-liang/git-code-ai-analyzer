### Git-Code-AI-Analyzer

🔍 基于 AI 的 Git 提交与代码变更分析工具，可用于精准回归测试、代码影响评估等智能辅助测试任务。

## 📦 安装

未发布到 pypi 仓库，需要手动安装。

```bash
pip install git+https://github.com/your-username/git-code-ai-analyzer.git
```

或从源码安装：

```
git clone https://github.com/your-org/git-code-ai-analyzer.git
cd git-code-ai-analyzer
pip install .
```

🚀 使用示例

```python
from git_code_ai_analyzer.ai_client import AIClient
from git_code_ai_analyzer.git_branch_analyzer import GitBranchAnalyzer
from git_code_ai_analyzer.code_analyzer import CodeAnalyzer
import os

# 这里以阿里 qwen 模型为例，可以使用火山引擎的模型，也可以使用 OpenAI 的模型。
AI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
AI_API_KEY = os.getenv("ALI_AI_API_KEY")  # 设置你的环境变量
AI_MODEL_NAME = "qwen-max-2025-01-25"

project_repo = "/your-project-local-root-path"  # 项目的本地路径
target_branch = "release-1.3.0"  # 需要分析哪个分支的 Commit 代码，且必须是本地已 pull 的分支
max_count = 1  # 最多分析多少个 Commit
max_files = 5  # 一个 Commit id 提交了超过 5 个文件则会拆分成多个请求
commit_diff_unified = 50  # 每个代码变更块前后 50 行代码一起作为上下文交给 AI 分析
report_file = "report.md"

ai_client = AIClient(AI_BASE_URL, AI_API_KEY, AI_MODEL_NAME)
branch_analyzer = GitBranchAnalyzer(project_repo, target_branch, max_files, commit_diff_unified)

analyzer = CodeAnalyzer(
    project_repo,
    target_branch,
    report_file,
    max_count,
    max_files,
    branch_analyzer,
    ai_client
)

analyzer.commit_impact_analysis()
```

✅ 功能说明
• ✨ 分析某个分支最近的提交变更；
• 🧠 接入大模型（如 Qwen、OpenAI）自动生成影响分析报告；
• 📄 支持 Markdown 格式的输出报告；
• 📂 拆分多文件变更提交，提升 AI 分析质量。

🔧 环境变量
• ALI_AI_API_KEY：你的阿里云 DashScope API 密钥

📦 依赖项
• gitpython
• requests
• openai（或兼容 OpenAI 协议的服务）

📝 License

MIT License © 2025 Aaron Xu