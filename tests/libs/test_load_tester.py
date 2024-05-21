import time
from collections import deque
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from aiohttp import ClientConnectionError
from pydantic import ValidationError

from libs.load_tester import LoadTester
from libs.log_result import logResult


# Fixture to create a LoadTester instance with default parameters
@pytest.fixture
def load_tester() -> LoadTester:
    return LoadTester(url="http://amazon.in", duration=5, qps=10, concurrency=2)

# Test case for the run_test method
@pytest.mark.asyncio
async def test_run_test(load_tester: LoadTester, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test case to verify the behavior of the run_test method.

    It mocks the send_requests method and checks if the start_time, end_time are set and
    if send_requests is called with the expected arguments.
    """

    # Mock the send_requests method
    mock_send_requests = AsyncMock()
    monkeypatch.setattr(LoadTester, "_send_requests", mock_send_requests)

    # Execute the run_test method
    await load_tester.run_test()

    # Assertions
    assert load_tester.start_time is not None
    assert load_tester.end_time is not None
    assert (
        mock_send_requests.await_args_list
        == [call(mock.ANY, mock.ANY)] * load_tester.concurrency
    )

# Test case for run_test method when an error occurs
@pytest.mark.asyncio
async def test_run_test_error(load_tester: LoadTester, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test case to verify error handling in the run_test method.

    It mocks the send_requests method to raise a ClientConnectionError and checks if
    the exception is propagated correctly.
    """
    # Mock the send_requests method to raise a ClientConnectionError
    mock_send_requests = AsyncMock(
        side_effect=ClientConnectionError("Connection error")
    )
    monkeypatch.setattr(LoadTester, "_send_requests", mock_send_requests)

     # Execute the run_test method and expect a ClientConnectionError
    with pytest.raises(ClientConnectionError):
        await load_tester.run_test()

    # Assertions
    assert (
        mock_send_requests.await_args_list
        == [call(mock.ANY, mock.ANY)] * load_tester.concurrency
    )

# Test case for send_requests method
@pytest.mark.asyncio
async def test_send_requests(load_tester: LoadTester) -> None:
    """
    Test case to verify the behavior of the send_requests method.

    It mocks the aiohttp.ClientSession and checks if HTTP GET requests are sent
    successfully and if the results are updated accordingly.
    """
    # Create a LoadTester instance with specific parameters
    lt = load_tester
    lt.start_time = time.time()
    lt.end_time = lt.start_time + 1  # Set short end time for the test

    # Mock the response from the HTTP GET request
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = "OK"
    mock_response.__aenter__.return_value = mock_response
    mock_response.__aexit__.return_value = False

    # Mock the aiohttp ClientSession
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    # Patch the aiohttp.ClientSession and execute the send_requests method
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await lt._send_requests(mock_session, lt.end_time)

    # Assertion
    assert len(lt.results["2XX"]) > 0

# Test case for send_requests method when an error occurs
@pytest.mark.asyncio
async def test_send_requests_with_error(load_tester: LoadTester) -> None:
    """
    Test case to verify error handling in the send_requests method.

    It mocks the aiohttp.ClientSession to raise an Exception during HTTP GET requests
    and checks if the errors are captured properly.
    """
    # Create a LoadTester instance with specific parameters
    lt = load_tester
    lt.start_time = time.time()
    lt.end_time = lt.start_time + 1  # Set short end time for the test

    # Mock the response from the HTTP GET request to raise an Exception 
    mock_response = AsyncMock()
    mock_response.__aenter__.side_effect = Exception("Network error")
    mock_response.__aexit__.return_value = False

    # Mock the aiohttp ClientSession
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    # Patch the aiohttp.ClientSession and execute the send_requests method
    with patch("aiohttp.ClientSession", return_value=mock_session):
        await lt._send_requests(mock_session, lt.end_time)

    # Assertion
    assert len(lt.errors) > 0


@pytest.mark.asyncio
async def test_high_qps() -> None:
    """
    Test case to verify behavior when the qps (Queries per second) is very high.

    It sets up a LoadTester instance with a high qps value, mocks the HTTP GET requests,
    and checks if the results contain successful responses (2XX).
    """
    lt = LoadTester(url="http://example.com", duration=10, qps=10000, concurrency=2)
    lt.start_time = time.time()
    lt.end_time = lt.start_time + 1

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = "OK"
    mock_response.__aenter__.return_value = mock_response
    mock_response.__aexit__.return_value = False

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session):
        await lt._send_requests(mock_session, lt.end_time)

    assert len(lt.results["2XX"]) > 0


@pytest.mark.asyncio
async def test_max_concurrency() -> None:
    """
    Test case to verify behavior when the maximum concurrency is reached.

    It sets up a LoadTester instance with maximum concurrency, mocks the HTTP GET requests,
    and checks if the results contain successful responses (2XX).
    """
    max_concurrency = 1000
    lt = LoadTester(
        url="http://example.com", duration=10, qps=5, concurrency=max_concurrency
    )
    lt.start_time = time.time()
    lt.end_time = lt.start_time + 1

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = "OK"
    mock_response.__aenter__.return_value = mock_response
    mock_response.__aexit__.return_value = False

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_session):
        await lt._send_requests(mock_session, lt.end_time)

    assert len(lt.results["2XX"]) > 0


def test_report_results(load_tester: LoadTester) -> None:
    """
    Test case to verify the report_results method.

    It sets up a LoadTester instance with sample results and errors, then verifies
    if the statistics are calculated correctly.
    """
    load_tester.start_time = 1
    load_tester.end_time = 6
    load_tester.results = {"2XX": deque([0.1, 0.2, 0.3]), "4XX": deque([0.4, 0.5])}
    load_tester.errors = {"ValueError": deque(["Test error"])}

    stats = logResult.report_results(load_tester)

    assert stats.total_requests == 5
    assert stats.total_time == 5
    assert stats.qps == 1
    assert stats.avg_latency == pytest.approx(0.3, abs=1e-2)
    assert stats.min_latency == 0.1
    assert stats.max_latency == 0.5
    assert stats.amp == 0.4
    assert stats.stdev == pytest.approx(0.141, abs=1e-3)
    assert stats.qpm == 60


def test_validate_positive() -> None:
    """
    Test case to verify positive value validation.

    It checks if ValueError is raised when duration is negative.
    """
    with pytest.raises(ValueError):
        LoadTester(url="http://example.com", duration=-1, qps=10, concurrency=2)


def test_zero_qps_validation() -> None:
    """
    Test case to verify zero qps validation.

    It checks if a ValidationError is raised when qps is set to zero.
    """
    with pytest.raises(ValidationError) as exc_info:
        LoadTester(url="http://example.com", duration=10, qps=0, concurrency=2)

    assert "Value must be positive" in str(exc_info.value)
