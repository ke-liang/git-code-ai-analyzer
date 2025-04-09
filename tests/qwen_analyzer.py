from git_code_ai_analyzer.ai_client import AIClient
from git_code_ai_analyzer.git_branch_analyzer import GitBranchAnalyzer
from git_code_ai_analyzer.code_analyzer import CodeAnalyzer
import os

if __name__ == "__main__":
    AI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # AI 模型请求地址
    AI_API_KEY = os.getenv("ALI_AI_API_KEY")  # AI 模型密钥
    AI_MODEL_NAME = "qwen-max-2025-01-25"  # AI 模型名称
    ai_client = AIClient(AI_BASE_URL, AI_API_KEY, AI_MODEL_NAME)

    project_repo = "/your-project-local-root-path"  # 本地代码的仓库路径
    target_branch = "release-1.3.0"  # 需要分析哪个分支的 Commit 代码
    max_count = 1  # 最多分析多少个 Commit
    max_files = 5  # 一个 Commit id 提交了超过 5 个文件则会拆分成多个请求
    commit_diff_unified = 50  # 每个代码变更块前后 50 行代码一起作为上下文交给 AI 分析
    report_file = "report.md"
    branch_analyzer = GitBranchAnalyzer(project_repo, target_branch, max_files, commit_diff_unified)

    analyzer = CodeAnalyzer(project_repo, target_branch, report_file, max_count, max_files,
                            branch_analyzer,
                            ai_client)
    # analyzer.analyze_specific_commits(['{commit-id}','{commit-id}'])# 分析指定的 commit ids
    analyzer.commit_impact_analysis()
