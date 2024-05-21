import argparse
import asyncio

from libs.load_tester import LoadTester
from libs.log_result import logResult


def main() -> None:
    parser = argparse.ArgumentParser(description="HTTP Load Tester")
    parser.add_argument("url", help="Target URL")
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)",
    )
    parser.add_argument("--qps", type=int, help="Requests per second (QPS)")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Number of concurrent requests (default: 10)",
    )
    parser.add_argument(
        "--build-docker", action="store_true", help="Build Docker image"
    )

    args = parser.parse_args()

    load_tester = LoadTester(
        url=args.url, duration=args.duration, qps=args.qps, concurrency=args.concurrency
    )
    asyncio.run(load_tester.run_test())
    logResult.report_results(load_tester)


if __name__ == "__main__":
    main()
