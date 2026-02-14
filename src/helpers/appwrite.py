import json
import os

import requests


def appwrite_db_api(
    uri: str, method: str, payload: dict, x_appwrite_key: str, log
) -> dict | None:
    headers = {
        "x-appwrite-key": x_appwrite_key,
        "x-appwrite-project": os.environ.get("APPWRITE_FUNCTION_PROJECT_ID"),
    }
    api_endpoint = os.environ["APPWRITE_FUNCTION_API_ENDPOINT"]
    # pbapi function call
    try:
        execution_payload = {
            "method": method,
            "path": uri,
            "body": json.dumps(payload),
            "headers": {"content-type": "application/json"},
        }
        response = requests.post(
            f"{api_endpoint}/functions/pbapi/executions",
            json=execution_payload,
            headers=headers,
            timeout=10,
        )
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                # Appwrite returns an execution object, we want the responseBody
                if "responseBody" in result:
                    try:
                        return json.loads(result["responseBody"])
                    except (ValueError, json.JSONDecodeError):
                        return result["responseBody"]
                return result
            except (ValueError, json.JSONDecodeError) as e:
                log.error(f"Failed to parse JSON response from pbapi: {str(e)}")
                return None

        log.error(f"Error calling pbapi: {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        log.error("Timeout calling pbapi")
    except requests.exceptions.ConnectionError:
        log.error("Connection error calling pbapi")
    except requests.exceptions.RequestException as e:
        log.error(f"Request exception calling pbapi: {str(e)}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        log.error(f"Unexpected exception calling pbapi: {str(e)}")

    return None
