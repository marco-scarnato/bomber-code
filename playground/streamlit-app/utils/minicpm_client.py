import os
import json
import requests
from openai import OpenAI

class MiniCPMClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("MINICPM_API_URL", "http://localhost:8001")
        self.client = OpenAI(
            base_url=f"{self.base_url}/v1",
            api_key="sk-no-key-required"
        )
        self.last_stats = {
            "prompt_tokens": 0,
            "reasoning_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "gen_speed_tps": 0.0,
            "prompt_ms": 0.0,
            "prompt_speed_tps": 0.0,
            "predicted_ms": 0.0
        }

    def health(self):
        """Check the health status of the MiniCPM API by listing models."""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def chat(self, messages, temperature=0.7, max_tokens=1024, top_p=0.95, stream=False):
        """Send a chat completion request to MiniCPM (non-streaming by default)."""
        if stream:
            return self.chat_stream(messages, temperature=temperature, max_tokens=max_tokens, top_p=top_p)
        
        try:
            url = f"{self.base_url}/v1/chat/completions"
            payload = {
                "model": "minicpm",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "stream": False
            }
            resp = requests.post(url, json=payload, timeout=600)
            resp.raise_for_status()
            data = resp.json()

            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {})
            reasoning = msg.get("reasoning_content", "")
            content = msg.get("content", "")

            timings = data.get("timings", {})
            usage = data.get("usage", {})

            r_tokens = len(reasoning.split()) if reasoning else 0

            self.last_stats = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "reasoning_tokens": r_tokens,
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "gen_speed_tps": round(timings.get("predicted_per_second", 0), 1),
                "prompt_ms": round(timings.get("prompt_ms", 0), 1),
                "prompt_speed_tps": round(timings.get("prompt_per_second", 0), 1),
                "predicted_ms": round(timings.get("predicted_ms", 0), 1)
            }

            if reasoning:
                return f"> 🧠 **Processo di Ragionamento:**\n> {reasoning.replace(chr(10), chr(10) + '> ')}\n\n---\n\n{content}"
            return content

        except Exception as e:
            raise Exception(f"MiniCPM chat request failed: {str(e)}")

    def chat_stream(self, messages, temperature=0.7, max_tokens=1024, top_p=0.95):
        """
        Stream response tokens from MiniCPM via SSE, separating reasoning and output,
        while collecting usage & timing metrics.
        """
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": "minicpm",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": True,
            "stream_options": {"include_usage": True}
        }

        try:
            resp = requests.post(url, json=payload, stream=True, timeout=600)
            resp.raise_for_status()

            def generator():
                reasoning_started = False
                content_started = False
                reasoning_chunk_count = 0
                collected_timings = {}
                collected_usage = {}

                for line in resp.iter_lines():
                    if not line:
                        continue
                    line_str = line.decode("utf-8")
                    if not line_str.startswith("data: "):
                        continue
                    data_str = line_str[6:].strip()
                    if data_str == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if "timings" in chunk:
                        collected_timings = chunk["timings"]
                    if "usage" in chunk:
                        collected_usage = chunk["usage"]

                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        
                        rc = delta.get("reasoning_content")
                        if rc:
                            reasoning_chunk_count += 1
                            if not reasoning_started:
                                reasoning_started = True
                                yield "> 🧠 **Processo di Ragionamento:**\n> "
                            yield rc.replace("\n", "\n> ")

                        c = delta.get("content")
                        if c:
                            if reasoning_started and not content_started:
                                content_started = True
                                yield "\n\n---\n\n"
                            yield c

                comp_tokens = collected_usage.get("completion_tokens", 0)
                r_tokens = min(reasoning_chunk_count, comp_tokens) if comp_tokens > 0 else reasoning_chunk_count
                
                self.last_stats = {
                    "prompt_tokens": collected_usage.get("prompt_tokens", 0),
                    "reasoning_tokens": r_tokens,
                    "completion_tokens": comp_tokens,
                    "total_tokens": collected_usage.get("total_tokens", 0),
                    "gen_speed_tps": round(collected_timings.get("predicted_per_second", 0), 1),
                    "prompt_ms": round(collected_timings.get("prompt_ms", 0), 1),
                    "prompt_speed_tps": round(collected_timings.get("prompt_per_second", 0), 1),
                    "predicted_ms": round(collected_timings.get("predicted_ms", 0), 1)
                }

            return generator()

        except Exception as e:
            raise Exception(f"MiniCPM streaming failed: {str(e)}")