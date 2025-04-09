# -*- coding: utf-8 -*-
# @Author  : AaronXu
# @Date    : 2025/02/24
# @Time    : 3:32 PM

from git import Repo


class GitBranchAnalyzer:
    def __init__(self, repo_path, target_branch, max_files_per_request=5, commit_diff_unified=50):
        self.repo = Repo(repo_path)
        self.target_branch = target_branch
        self._fetch_check_branches()
        self.commit_diff_unified = commit_diff_unified
        self.max_files_per_request = max_files_per_request

    def _fetch_check_branches(self):
        remote = self.repo.remote()
        remote.fetch()
        branches = [ref.name for ref in remote.refs]
        if f"origin/{self.target_branch}" not in branches:
            raise ValueError(f"分支 {self.target_branch} 不存在")

    def get_branch_commits(self, max_count=2, reverse=False):
        """
        获取指定分支的最近N个提交
        :param max_count: 获取多少个 Commit id
        :param reverse: 默认为 False，即取最新的 Commit id
        """
        branch_ref = self.repo.remote().refs[self.target_branch]
        # no_merges=True 表示不包含合并提交
        return list(self.repo.iter_commits(branch_ref, max_count=max_count, reverse=reverse, no_merges=True))

    def get_new_commits(self, last_analyzed_commit):
        branch_commits = set(c.hexsha for c in self.repo.iter_commits(self.target_branch, no_merges=True))
        if last_analyzed_commit not in branch_commits:
            print(f"⚠️ 提交 {last_analyzed_commit} 不在 {self.target_branch} 历史中，默认返回最新 5 个提交")
            return list(self.repo.iter_commits(self.target_branch, max_count=5))
        return list(self.repo.iter_commits(f"{last_analyzed_commit}..{self.target_branch}"))

    def get_commit_diff(self, commit) -> list[dict]:
        """
        获取单个commit的代码差异（包含文件级变更）
        commit.diff(parent_commit) 是从当前提交的角度出发，显示当前提交与父提交的差异。
        parent_commit.diff(commit) 是从父提交的角度出发，显示父提交与当前提交的差异，这在 合并提交的分析中 更适用，因为它能准确显示从父提交到合并提交的变更（即显示合并引入的变更）。
        """
        parent_commit = commit.parents[0] if commit.parents else None

        if parent_commit:
            # 是从父提交的角度出发，显示父提交与当前提交的差异，这在 合并提交的分析中 更适用，因为它能准确显示从父提交到合并提交的变更（即显示合并引入的变更）
            # unified=50 指定 每个变更块前后显示 50 行代码 作为上下文
            diffs = parent_commit.diff(commit, create_patch=True, unified=self.commit_diff_unified)
        else:
            # 无父提交，返回整个提交的内容，是从当前提交的角度出发，显示当前提交与父提交的差异
            diffs = commit.diff(create_patch=True)

        if not diffs:
            return [{'0': "无代码变更"}]

        return self.__split_diffs(diffs)

    def __split_diffs(self, diffs) -> list[dict]:
        """
        按文件数量拆分 diff，避免请求过长
        """
        diffs_content = []
        total_files = len(diffs)
        for i in range(0, total_files, self.max_files_per_request):
            sub_diffs = diffs[i: i + self.max_files_per_request]
            diff_content = "\n".join(d.diff.decode('utf-8', errors='ignore') for d in sub_diffs)
            diffs_content.append(
                {
                    "files": [d.b_path for d in sub_diffs],
                    "diffs": diff_content
                }
            )

        return diffs_content
