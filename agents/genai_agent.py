import asyncio
import os
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class SentimentOutput(BaseModel):
    sentiment: float = Field(
        description="Continuous sentiment score bounded strictly between -1.0 (extremely negative) and 1.0 (extremely positive) inclusive."
    )
    rationale: str = Field(
        description="Factual rationale extracted directly from the text without hallucination."
    )

class FundamentalAgent:
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        """
        Initialize the FundamentalAgent.
        Assumes GEMINI_API_KEY is set in the environment.
        """
        self.client = genai.Client()
        self.model_name = model_name

    async def analyze_sentiment(self, text: str) -> SentimentOutput:
        """
        Asynchronously extract sentiment and rationale from a single financial text.
        """
        prompt = (
            f"Analyze the following financial text.\n"
            f"Extract the continuous sentiment score (-1.0 to 1.0) and a factual rationale.\n\n"
            f"Text:\n{text}"
        )
        return await self._call_gemini(prompt)

    async def analyze_nday_batch(self, ticker: str, headlines: List[str], n_days: int) -> SentimentOutput:
        """
        Process a batched group of news headlines spanning N days for a given equity.
        """
        if not headlines:
            # Neutral sentiment if no news
            return SentimentOutput(sentiment=0.0, rationale="No headlines available for the period.")

        joined_headlines = "\n- ".join(headlines)
        prompt = (
            f"Analyze the following batched news headlines spanning {n_days} days for the equity '{ticker}'.\n"
            f"Extract the overall continuous sentiment score (-1.0 to 1.0) and a factual rationale summarizing the key drivers.\n\n"
            f"Headlines:\n- {joined_headlines}"
        )
        return await self._call_gemini(prompt)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def _call_gemini_with_retry(self, prompt: str):
        return await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=SentimentOutput,
            ),
        )

    async def _call_gemini(self, prompt: str) -> SentimentOutput:
        try:
            response = await self._call_gemini_with_retry(prompt)
            output = SentimentOutput.model_validate_json(response.text)
            
            # Enforce strict bounds just in case the LLM wanders outside [-1.0, 1.0]
            if output.sentiment < -1.0:
                output.sentiment = -1.0
            elif output.sentiment > 1.0:
                output.sentiment = 1.0
                
            return output
        except Exception as e:
            logger.error(f"Gemini API failure after retries: {e}")
            return SentimentOutput(sentiment=0.0, rationale="API failure")

if __name__ == "__main__":
    async def test():
        # Set a dummy API key if not present for testing the instantiation
        if "GEMINI_API_KEY" not in os.environ:
            os.environ["GEMINI_API_KEY"] = "dummy_key"
            
        agent = FundamentalAgent()
        print("FundamentalAgent initialized.")
        print(f"analyze_nday_batch is a coroutine: {asyncio.iscoroutinefunction(agent.analyze_nday_batch)}")
        
    asyncio.run(test())
