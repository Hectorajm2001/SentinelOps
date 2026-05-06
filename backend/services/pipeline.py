"""Bridge between the API and the multi-agent pipeline."""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from agents.crew import AgentsPipeline as CrewPipeline


class AgentsPipeline:
    def __init__(self, vllm_base_url: str, model_name: str) -> None:
        self._pipeline = CrewPipeline(vllm_base_url=vllm_base_url, model_name=model_name)

    async def run(self, event: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await asyncio.to_thread(self._pipeline.run, event=event, history=history)
