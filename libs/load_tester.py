import asyncio
import math
import time
from collections import defaultdict, deque, namedtuple
from typing import Deque, Optional, List

import aiohttp
from pydantic import BaseModel, Field, validator

import config
from libs.log_format import get_logger

RunStats = namedtuple(
    "RunStats",
    ["count", "total_time", "rps", "avg", "min", "max", "amp", "stdev", "rpm"],
)

logger = get_logger(__name__)


class LoadTester(BaseModel):
    """
    A class for running load tests against a target URL.

    Attributes:
        url (str): The target URL to test.
        duration (int): Duration of the test in seconds.
        qps (Optional[int]): Queries per second. Defaults to config.DEFAULT_QPS.
        concurrency (int): Number of concurrent threads. Defaults to config.DEFAULT_CONCURRENCY.
        results (DefaultDict[int, Deque[float]]): A dictionary mapping response codes to a deque of response times.
        errors (DefaultDict[int, Deque[str]]): A dictionary mapping response codes to a deque of error messages.
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

    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_time: Optional[float] = None
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock)
    results: dict[str, Deque[float]] = defaultdict(deque)
    errors: dict[str, Deque[str]] = defaultdict(deque)

    @validator("duration", "qps", "concurrency")
    def validate_positive(cls, value: int) -> int:
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
                asyncio.create_task(self.send_requests(session, end_time))
                for _ in range(self.concurrency)
            ]
            await asyncio.gather(*tasks)

        self.end_time = time.time()
        logger.info("Test finished")

    async def send_requests(self, session: aiohttp.ClientSession, end_time: float) -> None:
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
                async with session.get(self.url) as response:
                    await response.text()
                    status_code = response.status
                    status_group = str(status_code // 100) + "XX"
                    request_time = time.time() - start_time

                    async with self.lock:
                        self.results[status_group].append(request_time)
            except Exception as e:
                async with self.lock:
                    self.errors["5XX"].append(
                        str(e)
                    )  # Assuming status code 500 for simplicity

            
            elapsed_time = time.time() - start_time
            remaining_delay = delay - elapsed_time
            if remaining_delay > 0:
                # time.sleep(remaining_delay)
                await asyncio.sleep(remaining_delay)

    def report_results(self) -> RunStats:
        """
        Calculates and prints the statistics of the load test, including request counts,
        latencies, QPS, QPM and error rates.

        Returns:
            RunStats: A named tuple containing the run statistics.
        """
        all_res: List[float] = []

        total_requests, successful_calls = 0, 0
        for keys,values in self.results.items():
            if keys == "2XX":
                successful_calls = len(values)
            all_res += values
            total_requests += len(values)
        
        total_errors = sum(len(v) for v in self.errors.values())
        
        total_calls = total_requests + total_errors

        error_rate: Union[float, int]  = (total_calls - successful_calls)/ total_calls if total_calls > 0 else 0

        self.total_time = self.end_time - self.start_time
        cum_time = sum(all_res)

        if cum_time == 0 or len(all_res) == 0:
            rps = avg_latency = min_latency = max_latency = amp = stdev = 0
            rpm = 0
        else:
            if self.total_time == 0:
                rps = 0
                rpm = 0
            else:
                rps = float(len(all_res)) / float(self.total_time)
                rpm = rps * 60
            avg_latency = sum(all_res) / len(all_res)
            max_latency = max(all_res)
            min_latency = min(all_res)
            amp = max(all_res) - min(all_res)
            stdev = math.sqrt(
                sum((x - avg_latency) ** 2 for x in all_res) / total_requests
            )

            logger.info(f"Total calls: {total_calls}")
            for status_group, values in self.results.items():
                logger.info(f"{status_group} responses: {len(values)}")
            for status_group, errors in self.errors.items():
                logger.info(f"{status_group} errors: {len(errors)}")
            logger.info(f"Error Rate: {error_rate * 100:.2f}%")
            
            logger.info(f"Total Duration: {self.total_time:.4f} s")
            logger.info(f"Average Latency: {avg_latency:.4f} s")
            logger.info(f"Minimum Latency: {min_latency:.4f} s")
            logger.info(f"Maximum Latency: {max_latency:.4f} s")
            logger.info(f"Amplitude: {amp:.4f} s")
            logger.info(f"Standard deviation: {stdev:.6f}")
            logger.info(f"Queries Per Second: {rps:.2f}")
            logger.info(f"Queries Per Minute: {rpm:.2f}")

        return RunStats(
            total_requests,
            self.total_time,
            rps,
            avg_latency,
            min_latency,
            max_latency,
            amp,
            stdev,
            rpm,
        )
