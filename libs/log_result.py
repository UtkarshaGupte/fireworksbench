import math
from collections import namedtuple
from typing import List, Tuple

from libs.load_tester import LoadTester
from libs.log_format import get_logger

RunStats = namedtuple(
    "RunStats",
    [
        "total_requests",
        "total_time",
        "qps",
        "avg_latency",
        "min_latency",
        "max_latency",
        "amp",
        "stdev",
        "qpm",
    ],
)


class logResult:
    @staticmethod
    def report_results(load_tester: LoadTester) -> RunStats:
        """
        Calculates and prints the statistics of the load test, including request counts,
        latencies, QPS, QPM, and error rates.

        Returns:
            RunStats: A named tuple containing the run statistics.
        """
        # Initialize variables to store results and errors
        all_res: List[float] = []
        total_requests, successful_calls = 0, 0

        # Collect results and count total requests and successful calls
        total_requests, successful_calls, all_res = logResult._collect_results(load_tester)

        # Count total errors
        total_errors = logResult._collect_errors(load_tester)
        
        # Calculate total calls and error rate
        total_calls = total_requests + total_errors
        error_rate = logResult._calculate_error_rate(total_calls, successful_calls)

        # Calculate total time of the load test
        load_tester.total_time = logResult._calculate_total_time(load_tester)

        # Calculate various statistics
        cum_time = sum(all_res)
        rps, rpm, avg_latency, min_latency, max_latency, amp, stdev = logResult._calculate_statistics(
            load_tester, all_res, cum_time, total_requests
        )

        # Log the results
        logResult._log_results(load_tester, total_calls, error_rate, rps, rpm, avg_latency, min_latency, max_latency, amp, stdev)

        # Return the run statistics as a named tuple
        return RunStats(
            total_requests,
            load_tester.total_time,
            rps,
            avg_latency,
            min_latency,
            max_latency,
            amp,
            stdev,
            rpm,
        )

    @staticmethod
    def _collect_results(load_tester: LoadTester) -> Tuple[int, int, List[float]]:
        all_res: List[float] = []
        total_requests, successful_calls = 0, 0
        for keys, values in load_tester.results.items():
            if keys == "2XX":
                successful_calls = len(values)
            all_res += values
            total_requests += len(values)
        return total_requests, successful_calls, all_res

    @staticmethod
    def _collect_errors(load_tester: LoadTester) -> int:
        return sum(len(v) for v in load_tester.errors.values())

    @staticmethod
    def _calculate_error_rate(total_calls: int, successful_calls: int) -> float:
        return (total_calls - successful_calls) / total_calls if total_calls > 0 else 0

    @staticmethod
    def _calculate_total_time(load_tester: LoadTester) -> float:
        if load_tester.start_time is not None and load_tester.end_time is not None:
            return load_tester.end_time - load_tester.start_time
        return 0

    @staticmethod
    def _calculate_statistics(load_tester: LoadTester, all_res: List[float], cum_time: float, total_requests: int) -> Tuple[int, int, float, float, float, float, float]:
        rps: int = 0
        rpm: int = 0
        avg_latency: float = 0.0
        min_latency: float = 0.0
        max_latency: float = 0.0
        amp: float = 0.0
        stdev: float = 0.0

        if cum_time != 0 and len(all_res) != 0 and load_tester.total_time:
            if load_tester.total_time != 0:
                rps = int(len(all_res) / load_tester.total_time)
                rpm = rps * 60
            avg_latency = sum(all_res) / len(all_res)
            max_latency = max(all_res)
            min_latency = min(all_res)
            amp = max(all_res) - min(all_res)
            stdev = math.sqrt(
                sum((x - avg_latency) ** 2 for x in all_res) / total_requests
            )

        return rps, rpm, avg_latency, min_latency, max_latency, amp, stdev

    @staticmethod
    def _log_results(load_tester: LoadTester, total_calls: int, error_rate: float, rps: int, rpm: int, avg_latency: float, min_latency: float, max_latency: float, amp: float, stdev: float) -> None:
        logger = get_logger(__name__, load_tester.output)
        logger.info(f"Total calls: {total_calls}")
        for status_group, values in load_tester.results.items():
            logger.info(f"{status_group} responses: {len(values)}")
        for status_group, errors in load_tester.errors.items():
            logger.info(f"{status_group} errors: {len(errors)}")
        logger.info(f"Error Rate: {error_rate * 100:.2f}%")

        logger.info(f"Total Duration: {load_tester.total_time:.4f} s")
        logger.info(f"Average Latency: {avg_latency:.2f} s")
        logger.info(f"Minimum Latency: {min_latency:.2f} s")
        logger.info(f"Maximum Latency: {max_latency:.2f} s")
        logger.info(f"Amplitude: {amp:.2f} s")
        logger.info(f"Standard deviation: {stdev:.2f}")
        logger.info(f"Queries Per Second: {rps:.2f}")
        logger.info(f"Queries Per Minute: {rpm:.2f}")

    # NOTE - I used static methods to centralize the configuration of logging settings, such as log levels, log file locations, 
    # or log formats, within the log class itself. This allows to manage and modify the logging configuration in one place, 
    # rather than having to update multiple instances of the log class.
