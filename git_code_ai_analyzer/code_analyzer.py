# -*- coding: utf-8 -*-
# @Author  : AaronXu
# @Date    : 2025/02/24
# @Time    : 3:32 PM
from datetime import datetime


class CodeAnalyzer:
    def __init__(self, local_repo_path, target_branch, report_file, max_count, max_files_per_request,
                 branch_analyzer, ai_client):
        self.repo_path = local_repo_path
        self.target_branch = target_branch
        self.max_count = max_count
        self.max_files_per_request = max_files_per_request
        self.report_file = report_file
        self.branch_analyzer = branch_analyzer
        self.ai_client = ai_client

    def detect_high_risk(self, result, segment_length=20):
        # 寻找所有包含"风险等级"的位置
        start_index = 0
        while True:
            risk_level_position = result.find("风险等级", start_index)
            if risk_level_position == -1:  # 如果没有找到更多"风险等级"
                return False

            # 截取"风险等级"后的一段文本用于检查
            # 使用较长的片段以确保能捕获到"高"，但避免过长
            end_position = min(risk_level_position + segment_length, len(result))
            risk_level_segment = result[risk_level_position:end_position]

            # 如果检查到包含"高"，则直接返回 True 结束
            if "高" in risk_level_segment:
                return True

            # 更新起始位置为当前位置之后，继续搜索
            start_index = risk_level_position + 1

    def commit_impact_analysis(self):
        commits = self.branch_analyzer.get_branch_commits(self.max_count)

        is_first = True

        for commit in commits:
            diffs_content = self.branch_analyzer.get_commit_diff(commit)
            if "无代码变更" in diffs_content:
                print(f"✅ Commit {commit.hexsha[:7]} 无代码变更，跳过分析")
                continue
            for diff_content in diffs_content:
                result = self.ai_client.analyze_commit(diff_content["diffs"], commit)
                # 检查“风险等级”后的 20 个字符是否包含"低"/"高"
                if "风险等级" in result:
                    if self.detect_high_risk(result):
                        print(f"⚠️ 高风险提交：{commit.hexsha}, 提交信息：{commit.message}")

                analysis_report = {
                    "commit_id": commit.hexsha[:7],
                    "author": commit.author,
                    "summary": commit.message.split("\n")[0],
                    "analysis": result
                }
                # 每一次 commit 都会写入报告，所以第一次写入之后需要设置 is_first 为 False
                self._generate_report(analysis_report, len(commits), diff_content['files'], is_first=is_first)
                is_first = False

    def analyze_specific_commits(self, commits: list):
        """
        指定分析哪些 commit id
        """
        is_first = True
        for commit in commits:
            commit = self.branch_analyzer.repo.commit(commit)  # 获取指定的 commit 对象
            diffs_content = self.branch_analyzer.get_commit_diff(commit)
            if "无代码变更" in diffs_content:
                print(f"✅ Commit {commit.hexsha[:7]} 无代码变更，跳过分析")
                continue
            for diff_content in diffs_content:
                result = self.ai_client.analyze_commit(diff_content["diffs"], commit)
                # 检查“风险等级”后的 20 个字符是否包含 "高"
                if "风险等级" in result:
                    if self.detect_high_risk(result, segment_length=20):
                        print(f"⚠️ 高风险提交：{commit.hexsha}, 提交信息：{commit.message}")

                analysis_report = {
                    "commit_id": commit.hexsha[:7],
                    "author": commit.author,
                    "summary": commit.message.split("\n")[0],
                    "analysis": result
                }
                # 每一次 commit 都会写入报告，所以第一次写入之后需要设置 is_first 为 False
                self._generate_report(analysis_report, len(commits), diff_content['files'], is_first=is_first)
                is_first = False

    def _generate_report(self, report, total_commits, diff_files, is_first=True):
        mode = "w" if is_first else "a"  # 如果是第一次写入，则使用 "w" 覆盖模式，否则使用 "a" 追加模式
        with open(self.report_file, mode) as f:
            if is_first:
                f.write(f"# {self.target_branch} 提交影响分析报告\n\n")
                f.write(f"**生成时间**：{datetime.now().isoformat()}\n")
                f.write(f"**总提交数**：{total_commits}\n\n")
            f.write(f"## {report['author']} - commit -  {report['commit_id']}: {report['summary']}\n")
            f.write(f"### 此次分析的文件有：\n")
            for i in range(len(diff_files)):
                f.write(f"{i + 1}. {diff_files[i]}\n")
            f.write(f"\n\n---\n{report['analysis']}\n---\n\n")
