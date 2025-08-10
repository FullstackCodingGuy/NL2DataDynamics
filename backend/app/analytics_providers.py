import httpx
from typing import Dict, Any

class BaseTextAnalyticsProvider:
    async def analyze(self, text: str, task: str = "summarization") -> Dict[str, Any]:
        raise NotImplementedError

class LocalLLMTextAnalyticsProvider(BaseTextAnalyticsProvider):
    def __init__(self, endpoint: str):
        if not endpoint or endpoint.strip() == "":
            raise ValueError("Local LLM endpoint is required and cannot be empty")
        self.endpoint = endpoint.strip()

    async def analyze(self, text: str, task: str = "summarization") -> Dict[str, Any]:
        if not text or text.strip() == "":
            raise ValueError("Text input cannot be empty")
        payload = {
            "prompt": f"Perform {task} on the following text: {text}",
            "max_tokens": 256,
            "temperature": 0.7
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                result = response.json()
                output = result.get("response") or result.get("result") or str(result)
                return {
                    "task": task,
                    "result": output,
                    "provider": "local",
                    "endpoint": self.endpoint
                }
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Local LLM error: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise ValueError("Local LLM request timed out")
        except Exception as e:
            raise ValueError(f"Local LLM request failed: {str(e)}")

def get_text_analytics_provider(endpoint: str) -> BaseTextAnalyticsProvider:


    print(f"Creating Local LLM Text Analytics Provider with endpoint: {endpoint}")

    if not endpoint:
        raise ValueError("Local LLM endpoint is required")
    return LocalLLMTextAnalyticsProvider(endpoint=endpoint)