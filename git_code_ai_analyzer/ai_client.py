# -*- coding: utf-8 -*-
# @Author  : AaronXu
# @Date    : 2025/02/24
# @Time    : 3:32 PM
import requests
import time
from openai import OpenAI


class AIClient:
    def __init__(self, ai_base_url, ai_api_key, ai_model_name):
        self.base_url = ai_base_url
        self.api_key = ai_api_key
        self.model = ai_model_name

    def analyze_commit(self, diff_content, commit_info):
        system_prompt = ("你是一位资深的软件质量分析专家，具备超强的逻辑思维和代码分析能力，擅长通过代码变更推导影响范围，具备金融/电商系统测试经验。"
                         "请你根据以下[代码差异]按照给定的[分析维度]认真评估一下这次改动，如果有其它错误(如参数错误、空指针异常等)也请你一并指出。"
                         "请用专业但简洁的表述输出分析结果，谢谢！")
        # 时间：{datetime.fromtimestamp(commit_info.committed_date).isoformat()}
        user_prompt = f"""
        --------------------------------------------------
        提交信息：{commit_info.message}
        提交者：{commit_info.author}
        --------------------------------------------------
        [代码差异]：
        {diff_content}

        [分析维度]
        1. 影响模块：前端/后端/数据库/中间件/测试
        2. 变更类型：功能新增｜BUG修复｜配置变更｜文档更新
        3. 风险等级：高（影响核心逻辑或者参数传错或者潜在的空指针异常或者其它明显的错误都设置为高）｜中（影响非关键模块）｜低（仅格式调整）
        4. 关联测试建议：需要补充的测试用例路径
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,  # 默认不启用流式输出
            # "temperature": 0.7
        }
        if self.model in ['qwq-plus', 'qwq-32b']:
            payload["stream"] = True  # 启用流式输出
        try:
            print(f"======🚀 正在向 AI 发起分析 Commit id 为 {commit_info.hexsha} 请求...======")
            start_time = time.perf_counter()
            if payload["stream"] is False:
                response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload,
                                         timeout=(5, 300))
                # 如果返回的状态码不是 200，则抛出异常
                if response.status_code != 200:
                    raise Exception(f"请求失败，状态码：{response.status_code}, 响应内容：{response.text}")

                print(f"======✅ AI 分析成功，耗时 {time.perf_counter() - start_time:.2f} 秒======")
                return response.json()["choices"][0]["message"]["content"]
            else:
                # 初始化OpenAI客户端
                client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                # 创建聊天完成请求
                completion = client.chat.completions.create(**payload)

                reasoning_content = ""  # 定义完整思考过程
                answer_content = ""  # 定义完整回复
                is_answering = False  # 判断是否结束思考过程并开始回复
                for chunk in completion:
                    if not chunk.choices:
                        print("\nUsage:")
                        print(chunk.usage)
                    else:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                            reasoning_content += delta.reasoning_content
                        else:
                            if delta.content != "" and is_answering is False:
                                is_answering = True
                            answer_content += delta.content

                print(f"======✅ AI 分析成功，耗时 {time.perf_counter() - start_time:.2f} 秒======")

                return answer_content
                # return "\n###完整思考过程:\n\n" + reasoning_content + "\n\n---\n\n###分析结果:\n\n" + answer_content

        except requests.RequestException as e:
            print(f"❌ AI 代码分析失败: {e}")
            return "AI 分析失败，建议手动检查提交变更。"
