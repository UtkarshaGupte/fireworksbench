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

## Additional Features of the CLI:
- **HTTP Method:** You can specify the HTTP method to use for requests. Supported methods include GET, POST, PUT, DELETE, and PATCH.
- **Custom Headers:** You can provide custom headers in JSON format to include in the requests.
- **Payload:** For POST and PUT requests, you can provide a payload in JSON format to include in the request body.
- **Timeout:** You can specify the timeout duration for each request in seconds. The default is set to 10 seconds.
- **Retries:** Specify the number of retries for failed requests. The default is set to 3 retries.
- **Output:** Optionally, you can provide a file path to save the test results.

## Installation

1. Clone the Repository:
```bash
git clone https://github.com/UtkarshaGupte/fireworksbench.git
```
This command clones the repository from the specified URL (https://github.com/UtkarshaGupte/fireworksbench.git) to your local machine. After running this command, you will have a local copy of the fireworksbench project directory.

2. Navigate to the Project Directory:
```bash
cd fireworksbench
```

3. Install Poetry
```bash
pip install poetry
```

4. Activate the Virtual Environment:
```bash
poetry shell
```

This command activates the virtual environment created by Poetry. Activating the virtual environment ensures that you're using the correct dependencies and environment settings for the project.


5. Install Project Dependencies:
```bash
poetry install --no-dev --no-root
```

* poetry install: This command installs the project dependencies specified in the pyproject.toml file using Poetry.

* --no-dev: This flag tells Poetry not to install development dependencies. Development dependencies are typically used for testing, linting, or other tasks related to development but not necessary for running the application.

* --no-root: This flag tells Poetry not to create a virtual environment in the project directory. Instead, Poetry manages the virtual environment in its own directory.


## Usage

### URL Format
Please ensure that the target URL is in the format https://www.example.com or http://www.example.com and not just www.example.com. 
For example, use https://www.amazon.in instead of www.amazon.in.

### Via Docker
To use fireworksbench with Docker, follow these steps:

1. Build the Docker image:
```bash
docker build -t fireworksbench:v1 .
```

2. Run the Docker container:
```bash
docker run fireworksbench:v1 <target_url> --duration <duration_seconds> --concurrency <concurrency_level> --qps <queries_per_second> --method <http_method> --headers '<json_headers>' --payload '<json_payload>' --timeout <timeout_seconds> --retries <retries> --output <output_file>

```

### Via CLI

##### with poetry
```bash
poetry run python main.py <target_url> --duration <duration_seconds> --concurrency <concurrency_level> --qps <queries_per_second> --method <http_method> --headers '<json_headers>' --payload '<json_payload>' --timeout <timeout_seconds> --retries <retries> --output <output_file>
```

##### without poetry
```bash
python main.py <target_url> --duration <duration_seconds> --concurrency <concurrency_level> --qps <queries_per_second> --method <http_method> --headers '<json_headers>' --payload '<json_payload>' --timeout <timeout_seconds> --retries <retries> --output <output_file>
```

Replace <target_url>, <duration_seconds>, <queries_per_second>, <concurrency_level>, <http_method>, <custom_headers_json>, <payload_json>, <timeout_seconds>, <num_retries>, and <output_file> with your desired values.


## Local Development

To run it locally for development purposes, follow these steps:

1. Clone the repository
```bash
git clone https://github.com/UtkarshaGupte/fireworksbench.git
```

2. Navigate to the Project Directory:
```bash
cd fireworksbench
```

3. Install Poetry

FireworksBench uses Poetry for dependency management. If you don't have Poetry installed already, you can install it using pip:

```bash
pip install poetry
```

4. Install Project Dependencies:
```bash
poetry install
```

This command installs the project dependencies specified in the pyproject.toml file using Poetry. The --dev flag is omitted because development dependencies are necessary for local development.

5. Activate the Virtual Environment:
```bash
poetry shell
```

This command activates the virtual environment created by Poetry. Activating the virtual environment ensures that you're using the correct dependencies and environment settings for the project.

6. Start Developing:

Now that you have set up the project locally, you can start contributing or making changes to the codebase. You can run tests, make changes to the code, and run the application locally for testing and development purposes.

7. Run Tests:
```bash
pytest
```

FireworksBench uses pytest for testing. You can run the tests to ensure that your changes haven't introduced any regressions and that the existing functionality is working as expected.

8. Make Changes and Commit:

Once you have made your changes and tested them locally, you can commit your changes to your local repository and push them to GitHub if you're working on a fork or a branch.

By following these steps, you can set up FireworksBench for local development and contribute to the project or use it for testing and experimentation.

## Note To Reviewer 

Added some explanation regarding the choice of current implementation vs an alternative approach in the [Note to Reviewer file](note_to_reviewer.md).
