# FireworksBench

## Description
Fireworksbench is a http load testing tool designed to perform load testing on a specified URL. It measures and reports latencies, error rates, and supports configuring the rate of requests per second (QPS) and concurrency level.

## Features
- Reports latencies (average, minimum, maximum)
- Reports error rates
- Configurable queries per second (QPS)
- Configurable concurrency level
- Runs for a specified duration
- Prints detailed statistics after the test


## Usage

### Via Docker
To use fireworksbench with Docker, follow these steps:

1. Build the Docker image:
```bash
docker build -t fireworksbench:v1 .
```

2. Run the Docker container:
```bash
docker run fireworksbench:v1 --url <target_url> --duration <duration_seconds> --qps <queries_per_second> --concurrency <concurrency_level>
```


### Via CLI

##### with poetry
```bash
poetry run python main.py --url <target_url> --duration <duration_seconds> --qps <queries_per_second> --concurrency <concurrency_level>
```

##### without poetry
```bash
python main.py --url <target_url> --duration <duration_seconds> --qps <queries_per_second> --concurrency <concurrency_level>
```


Replace <target_url>, <duration_seconds>, <queries_per_second>, and <concurrency_level> with your desired values.

