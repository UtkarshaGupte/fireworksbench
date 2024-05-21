import argparse
import asyncio

import config
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
        "--method",
        type=str,
        default="GET",
        choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
        help="HTTP method to use (default: GET)",
    )
    parser.add_argument(
        "--headers",
        type=str,
        help="Custom headers in JSON format",
    )
    parser.add_argument(
        "--payload",
        type=str,
        help="Payload for POST/PUT requests in JSON format",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout for each request in seconds (default: 10.0)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retries for failed requests (default: 3)",
    )
    parser.add_argument(
        "--output",
        default=config.LOG_FILE,
        type=str,
        help="File to save test results",
    )
    
    args = parser.parse_args()

    headers = None
    payload = None

    if args.headers:
        import json
        headers = json.loads(args.headers)
    
    if args.payload:
        import json
        payload = json.loads(args.payload)

    load_tester = LoadTester(
        url=args.url, 
        duration=args.duration, 
        qps=args.qps, 
        concurrency=args.concurrency,
        http_method=args.method,
        headers=headers,
        payload=payload,
        timeout=args.timeout,
        retries=args.retries,
        output=args.output

    )
    asyncio.run(load_tester.run_test())
    logResult.report_results(load_tester)


if __name__ == "__main__":
    main()
