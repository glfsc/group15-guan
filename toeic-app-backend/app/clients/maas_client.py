import json
import logging
from typing import Dict, Any, List

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class MaasClient:
    def __init__(self):
        self.endpoint = settings.MAAS_ENDPOINT.rstrip("/")
        self.api_key = (settings.MAAS_API_KEY or "").strip()
        self.model = settings.MAAS_MODEL
        timeout = httpx.Timeout(
            connect=10.0,
            read=settings.MAAS_TIMEOUT_SECONDS,
            write=30.0,
            pool=30.0,
        )
        self.client = httpx.AsyncClient(timeout=timeout, verify=False)

    async def _call_chat_api(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("MAAS_API_KEY is required for MaaS v2 API")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "max_tokens": 1800,
        }

        response = await self.client.post(self.endpoint, headers=headers, json=request_body)
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    @retry(stop=stop_after_attempt(settings.MAAS_MAX_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_listening_question(
        self,
        difficulty: str,
        question_type: str,
        count: int = 1
    ) -> List[Dict[str, Any]]:
        if question_type == "photo_description":
            prompt = f"""请生成{count}道托业听力图片描述题，要求如下：
难度等级：{difficulty}

每道题必须严格按这个顺序设计：
1. 先构造一个清晰、具体、适合生成图片的真实场景
2. 再根据该场景编写标准托业图片题题干 question
3. 再根据同一场景编写四个选项，并确保只有一个正确答案
4. 最后输出可直接用于生成图片的 image_prompt

每道题目包含以下内容：
1. 问题文本（question）：必须是标准托业图片题文字题干，例如 "What is happening in the picture?"、"What can be seen in the picture?"，不超过500字符
2. 音频内容描述（audio_content）：一段自然的英文图片描述播报内容，应与场景完全一致，不能只是把四个选项读一遍
3. 场景描述（image_prompt）：必须具体描述人物、动作、位置、物品、环境，直接可用于生成图片；不要写成问句，不要只写选项内容
4. 原文依据（script_reference）：给出能直接支撑正确答案的关键句或原文
5. 四个选项（options）：四选一，只有一个正确答案；错误选项必须与图片场景可区分，不能只是改写正确项
6. 正确答案（correct_answer）：选项索引（0-3）
7. 答案解析（analysis）：说明为什么正确选项对、其他选项错

请以JSON数组格式返回，格式如下：
[
  {{
    "question": "What is the man doing in the picture?",
    "audio_content": "A man is standing beside a delivery truck and carrying a large box toward a store entrance.",
    "image_prompt": "A delivery worker is standing beside a truck, carrying a large box toward the entrance of a store in the daytime. There are stacked packages near the door.",
    "script_reference": "A man is standing beside a delivery truck and carrying a large box toward a store entrance.",
    "options": {{"option_0": "He is carrying a package into a building.", "option_1": "He is driving a truck down a street.", "option_2": "He is talking to customers at a counter.", "option_3": "He is fixing shelves inside a store."}},
    "correct_answer": 0,
    "analysis": "原文明确说明男子正搬着箱子走向商店入口，因此A正确。"
  }}
]

注意：
- 先有清晰场景，再有题干、选项、答案和图片提示词
- image_prompt 必须和 audio_content、correct_answer 完全一致
- script_reference 必须能直接支持正确答案
- question 必须是问句形式的标准图片题题干，不得写成选项朗读稿
- audio_content 不得只是罗列 A/B/C/D 四个选项
- 只返回JSON，不要有其他文字
"""
        else:
            prompt = f"""请生成{count}道托业听力题，要求如下：
难度等级：{difficulty}
题目类型：{question_type}

每道题目包含以下内容：
1. 问题文本（question）：不超过500字符
2. 音频内容描述（audio_content）：描述音频中会听到的对话或独白
3. 四个选项（options）：每个选项不超过200字符
4. 正确答案（correct_answer）：选项索引（0-3）
5. 答案解析（analysis）：不超过1000字符
6. 原文依据（script_reference）：给出能支撑正确答案的原文句子、关键描述或简短听力脚本

请以JSON数组格式返回，格式如下：
[
  {{
    "question": "问题文本",
    "audio_content": "音频内容描述",
    "script_reference": "与正确答案直接相关的原文或关键句",
    "options": {{"option_0": "选项A", "option_1": "选项B", "option_2": "选项C", "option_3": "选项D"}},
    "correct_answer": 0,
    "analysis": "答案解析"
  }}
]

注意：
- 确保题目真实可信，符合托业考试标准
- script_reference 要尽量具体，能直接说明为什么答案正确
- 只返回JSON，不要有其他文字
"""

        try:
            content = await self._call_chat_api(prompt)
            try:
                questions = json.loads(content)
                return questions if isinstance(questions, list) else [questions]
            except json.JSONDecodeError:
                start = content.find('[')
                end = content.rfind(']') + 1
                if start != -1 and end > start:
                    try:
                        questions = json.loads(content[start:end])
                        return questions if isinstance(questions, list) else [questions]
                    except json.JSONDecodeError:
                        pass
                logger.error(f"Failed to parse MaaS response: {content[:200]}")
                return []
        except Exception as e:
            logger.error(f"Failed to generate listening question: {type(e).__name__}: {e!r}")
            raise

    @retry(stop=stop_after_attempt(settings.MAAS_MAX_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_grammar_question(
        self,
        knowledge_point: str,
        difficulty: str,
        count: int = 1
    ) -> List[Dict[str, Any]]:
        prompt = f"""请生成{count}道托业语法题，要求如下：
语法知识点：{knowledge_point}
难度等级：{difficulty}

每道题目包含以下内容：
1. 完整句子或段落（content）：包含需要填空的部分
2. 问题标注（question_mark）：标注需要填空或选择的部分
3. 四个选项（options）：每个选项不超过100字符
4. 正确答案（correct_answer）：选项索引（0-3）
5. 语法规则说明（grammar_rule）：不超过500字符
6. 例句（example）：语法应用的例句

请以JSON数组格式返回，格式如下：
[
  {{
    "content": "完整句子",
    "question_mark": "问题标注",
    "options": {{"option_0": "选项A", "option_1": "选项B", "option_2": "选项C", "option_3": "选项D"}},
    "correct_answer": 0,
    "grammar_rule": "语法规则说明",
    "example": "例句"
  }}
]

注意：确保语法正确，符合托业考试标准。只返回JSON，不要有其他文字。"""

        try:
            content = await self._call_chat_api(prompt)
            try:
                questions = json.loads(content)
                return questions if isinstance(questions, list) else [questions]
            except json.JSONDecodeError:
                start = content.find('[')
                end = content.rfind(']') + 1
                if start != -1 and end > start:
                    try:
                        questions = json.loads(content[start:end])
                        return questions if isinstance(questions, list) else [questions]
                    except json.JSONDecodeError:
                        pass
                logger.error(f"Failed to parse MaaS response: {content[:200]}")
                return []
        except Exception as e:
            logger.error(f"Failed to generate grammar question: {type(e).__name__}: {e!r}")
            raise

    async def close(self):
        await self.client.aclose()
