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
]


def make_request(endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to the specified endpoint and return the response data."""
    method = endpoint["method"]
    url = endpoint["url"]

    if "{item_id}" in url:
        url = url.replace("{item_id}", str(random.randint(1, 100)))
    if "{user_id}" in url:
        url = url.replace("{user_id}", str(random.randint(1, 20)))

    full_url = f"{BASE_URL}{url}"

    kwargs = {}
    if "params" in endpoint:
        param_key = list(endpoint["params"].keys())[0]
        param_values = endpoint["params"][param_key]
        kwargs["params"] = {param_key: random.choice(param_values)}

    if "data" in endpoint:
        kwargs["json"] = {}
        for key, values in endpoint["data"].items():
            kwargs["json"][key] = random.choice(values)

    if random.random() < 0.05:
        if method == "GET":
            full_url = f"{BASE_URL}/non_existent_endpoint"

    time.sleep(random.uniform(0.01, 0.2))

    start_time = time.time()
    try:
        response = requests.request(method, full_url, **kwargs)
        status_code = response.status_code
        response_time = time.time() - start_time
    except Exception as e:
        status_code = 500
        response_time = time.time() - start_time

    return {
        "endpoint": url,
        "method": method,
        "status_code": status_code,
        "response_time": response_time,
        "timestamp": time.time(),
    }


def simulate_workload(duration_seconds: int = 60, max_workers: int = 5):
    """Simulate workload by making requests to the API endpoints."""
    print(f"Starting workload simulation for {duration_seconds} seconds...")

    end_time = time.time() + duration_seconds

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        while time.time() < end_time:
            endpoint = random.choice(ENDPOINTS)
            futures.append(executor.submit(make_request, endpoint))

            time.sleep(random.uniform(0.1, 0.5))

            for future in concurrent.futures.as_completed(futures[:]):
                if future in futures:
                    futures.remove(future)
                    result = future.result()
                    print(
                        f"{result['method']} {result['endpoint']} - Status: {result['status_code']} - Response time: {result['response_time']:.4f}s"
                    )

    print("Workload simulation completed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API Workload Simulator")
    parser.add_argument(
        "--duration", type=int, default=60, help="Duration of simulation in seconds"
    )
    parser.add_argument(
        "--workers", type=int, default=5, help="Maximum number of concurrent workers"
    )

    args = parser.parse_args()
    simulate_workload(args.duration, args.workers)
