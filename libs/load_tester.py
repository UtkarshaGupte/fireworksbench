import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

import aiohttp
from pydantic import BaseModel, Field, field_validator

import config
from libs.log_format import get_logger

logger = get_logger(__name__)


class LoadTester(BaseModel):
    """
    A class for running load tests against a target URL.

    Attributes:
        url (str): The target URL to test.
        duration (int): Duration of the test in seconds.
        qps (Optional[int]): Queries per second. Defaults to config.DEFAULT_QPS.
        concurrency (int): Number of concurrent threads. Defaults to config.DEFAULT_CONCURRENCY.
        http_method (str): The HTTP method to use for requests. Defaults to "GET".
        headers (Optional[Dict[str, str]]): Custom headers to include in requests.
        payload (Optional[Dict[str, Any]]): Payload for POST/PUT requests.
        timeout (float): Timeout for each request in seconds.
        retries (int): Number of retries for failed requests.
        results (DefaultDict[str, Deque[float]]): A dictionary mapping response codes to a deque of response times.
        errors (DefaultDict[str, Deque[str]]): A dictionary mapping response codes to a deque of error messages.
        start_time (Optional[float]): The start time of the test. Initially None.
        end_time (Optional[float]): The end time of the test. Initially None.
        lock (asyncio.Lock): A lock for synchronizing access to shared resources.
        logger (logging.Logger): A logger instance for logging messages.
    """

    url: str = Field(..., description="The target URL to test.")
    duration: int = Field(
        default=config.DEFAULT_DURATION, description="Duration of the test in seconds."
    )
    qps: int = Field(default=config.DEFAULT_QPS, description="Queries per second.")
    concurrency: int = Field(
        default=config.DEFAULT_CONCURRENCY, description="Number of concurrent threads."
    )

    http_method: str = Field(default="GET", description="HTTP method to use.")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Custom headers to include in requests.")
    payload: Optional[Dict[str, str]] = Field(default=None, description="Payload for POST/PUT requests.")
    timeout: float = Field(default=10.0, description="Timeout for each request in seconds.")
    retries: int = Field(default=3, description="Number of retries for failed requests.")

    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_time: Optional[float] = None
    results_lock: asyncio.Lock = Field(default_factory=asyncio.Lock)
    errors_lock: asyncio.Lock = Field(default_factory=asyncio.Lock)
    results: dict[str, Deque[float]] = defaultdict(deque)
    errors: dict[str, Deque[str]] = defaultdict(deque)

    @field_validator("duration", "qps", "concurrency")
    def _validate_positive(cls, value: int) -> int:
        """Validates that the input value is positive."""
        if value <= 0:
            raise ValueError("Value must be positive.")
        return value

    class Config:
        """Pydantic configuration class."""

        arbitrary_types_allowed = True

    async def run_test(self) -> None:
        """
        Starts the load test by spawning threads to send requests.
        """
        logger.info(
            f"Starting test: URL={self.url}, duration={self.duration}s, QPS={self.qps}, concurrency={self.concurrency}"
        )

        self.start_time = time.time()
        end_time = self.start_time + self.duration

        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(self._send_requests(session, end_time))
                for _ in range(self.concurrency)
            ]
            await asyncio.gather(*tasks)

        self.end_time = time.time()
        logger.info("Test finished")

    async def _send_requests(
        self, session: aiohttp.ClientSession, end_time: float
    ) -> None:
        """
        Sends HTTP GET requests to the target URL until the specified end time.

        Args:
            end_time (float): The time at which to stop sending requests.
        """
        if self.qps:
            delay = 1.0 / self.qps
        else:
            delay = 0

        while time.time() < end_time:
            start_time = time.time()

            try:
                for _ in range(self.retries + 1):
                    try:

                        async with session.request(
                                    method=self.http_method,
                                    url=self.url,
                                    headers=self.headers,
                                    json=self.payload,
                                    timeout=self.timeout
                                ) as response:
                            await response.text()
                            status_code = response.status
                            status_group = str(status_code // 100) + "XX"
                            request_time = time.time() - start_time

                            await self._record_result(status_group, request_time)

                    except aiohttp.ClientError as e:
                        if _ == self.retries:
                            raise e
                        await asyncio.sleep(1)  # Exponential backoff could be implemented here
            except Exception as e:
                await self._record_error(e)# Assuming status code 500 for simplicity

            elapsed_time = time.time() - start_time
            remaining_delay = delay - elapsed_time
            if remaining_delay > 0:
                await asyncio.sleep(remaining_delay)

            # Log for debugging
            logger.debug(
                f"Requests sent: {len(self.results)}, Errors: {len(self.errors)}"
            )

    async def _record_result(self, status_group: str, request_time: float) -> None:
        """
        Records the result of a request.

        Args:
            status_group (str): The status code group (e.g., "2XX").
            request_time (float): The time taken for the request.
        """
        async with self.results_lock:
            self.results[status_group].append(request_time)

    async def _record_error(self, error: Exception) -> None:
        """
        Records an error that occurred during a request.

        Args:
            error (Exception): The exception that was raised.
        """
        async with self.errors_lock:
            self.errors[error.__class__.__name__].append(str(error))