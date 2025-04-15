import requests
import random
import time
import concurrent.futures
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

ENDPOINTS = [
    {"method": "GET", "url": "/"},
    {
        "method": "GET",
        "url": "/items/{item_id}",
        "params": {"q": ["search", "filter", "sort"]},
    },
    {
        "method": "POST",
        "url": "/create-item/",
        "data": {
            "name": ["product", "service", "tool"],
            "description": ["high quality", "affordable", "new release"],
        },
    },
    {
        "method": "PUT",
        "url": "/update-item/{item_id}",
        "data": {
            "name": ["updated product", "updated service", "updated tool"],
            "description": ["improved quality", "price reduced", "new features"],
        },
    },
    {"method": "DELETE", "url": "/delete-item/{item_id}"},
    {"method": "GET", "url": "/users/"},
    {
        "method": "POST",
        "url": "/users/",
        "data": {"username": ["user1", "user2", "user3", "user4", "user5"]},
    },
    {"method": "GET", "url": "/users/{user_id}"},
    {
        "method": "PUT",
        "url": "/users/{user_id}",
        "data": {"username": ["updated_user1", "updated_user2", "updated_user3"]},
    },
    {"method": "DELETE", "url": "/users/{user_id}"},
    {"method": "GET", "url": "/non_existent_endpoint"},
]


def make_request(endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to the specified endpoint and return the response data."""
    method = endpoint["method"]
    url = endpoint["url"]
    original_url = url

    error_probability = 0.15

    if "{item_id}" in url:
        item_id = (
            random.randint(1, 100)
            if random.random() > error_probability
            else random.randint(1000, 2000)
        )
        url = url.replace("{item_id}", str(item_id))
    if "{user_id}" in url:
        user_id = (
            random.randint(1, 20)
            if random.random() > error_probability
            else random.randint(1000, 2000)
        )
        url = url.replace("{user_id}", str(user_id))

    full_url = f"{BASE_URL}{url}"

    kwargs = {}
    if "params" in endpoint:
        param_key = list(endpoint["params"].keys())[0]
        param_values = endpoint["params"][param_key]
        kwargs["params"] = {param_key: random.choice(param_values)}

    if "data" in endpoint:
        if random.random() < error_probability and method in ["POST", "PUT"]:
            if "name" in endpoint["data"]:
                kwargs["json"] = {
                    "description": random.choice(endpoint["data"]["description"])
                }
            elif "username" in endpoint["data"]:
                kwargs["json"] = {"some_other_field": "invalid"}
            else:
                kwargs["json"] = {
                    key: random.choice(values)
                    for key, values in endpoint["data"].items()
                }
        else:
            kwargs["json"] = {}
            for key, values in endpoint["data"].items():
                kwargs["json"][key] = random.choice(values)

    time.sleep(random.uniform(0.01, 0.1))

    start_time = time.time()
    status_code = None
    try:
        response = requests.request(method, full_url, timeout=5, **kwargs)
        status_code = response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        status_code = 503
    except Exception as e:
        print(f"Unexpected error during request: {e}")
        status_code = 500
    finally:
        response_time = time.time() - start_time
        if status_code is None:
            status_code = 500

    return {
        "endpoint": original_url,
        "method": method,
        "status_code": status_code,
        "response_time": response_time,
        "timestamp": time.time(),
    }


def simulate_workload(duration_seconds: int = 60, max_workers: int = 10):
    """Simulate workload by making requests to the API endpoints."""
    print(f"Starting workload simulation for {duration_seconds} seconds...")

    end_time = time.time() + duration_seconds

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        request_count = 0
        error_count = 0

        while time.time() < end_time:
            endpoint = random.choice(ENDPOINTS)
            futures.append(executor.submit(make_request, endpoint))
            request_count += 1

            time.sleep(random.uniform(0.05, 0.2))

            done, _ = concurrent.futures.wait(
                futures, timeout=0, return_when=concurrent.futures.FIRST_COMPLETED
            )
            for future in done:
                futures.remove(future)
                try:
                    result = future.result()
                    print(
                        f"{result['method']} {result['endpoint']} - Status: {result['status_code']} - Response time: {result['response_time']:.4f}s"
                    )
                    if result["status_code"] >= 400:
                        error_count += 1
                except Exception as e:
                    print(f"Error getting result from future: {e}")
                    error_count += 1

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(
                    f"{result['method']} {result['endpoint']} - Status: {result['status_code']} - Response time: {result['response_time']:.4f}s"
                )
                if result["status_code"] >= 400:
                    error_count += 1
            except Exception as e:
                print(f"Error getting result from future: {e}")
                error_count += 1

    print(f"\nWorkload simulation completed.")
    print(f"Total requests attempted: {request_count}")
    print(f"Total errors (status >= 400 or request failed): {error_count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API Workload Simulator")
    parser.add_argument(
        "--duration", type=int, default=60, help="Duration of simulation in seconds"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Maximum number of concurrent workers",
    )

    args = parser.parse_args()
    simulate_workload(args.duration, args.workers)