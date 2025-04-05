from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from log_store import LogStore  # In-memory log storage with expiration logic

app = Flask(__name__)
store = LogStore()

@app.route("/", methods=["GET"])
def home():
    # Returns API metadata and supported constraints
    response = {
        "status": "running",
        "endpoints": ["/logs [POST]", "/logs [GET]"],
        "constraints": {
            "logs_expire": "Logs older than 1 hour are not returned",
            "thread_safe": True,
            "concurrent_requests": "Supported",
            "sorted_order": "Logs returned are always sorted by timestamp",
            "unordered_ingestion": "Supported"
        },
        "timestamp_format": "ISO 8601 - %Y-%m-%dT%H:%M:%SZ"
    }
    print("GET / ->", response)
    return jsonify(response), 200

@app.route("/logs", methods=["POST"])
def ingest_log():
    if not request.is_json:
        # Reject non-JSON requests
        error_response = {"error": "Content-Type must be application/json"}
        print("POST /logs ->", error_response)
        return jsonify(error_response), 415

    data = request.get_json()
    required_fields = ["service_name", "timestamp", "message"]

    # Check that all required fields are present
    if not all(field in data for field in required_fields):
        error_response = {
            "error": "Missing one or more required fields: service_name, timestamp, message",
            "received": data
        }
        print("POST /logs ->", error_response)
        return jsonify(error_response), 400

    try:
        # Parse timestamp to ensure it's valid ISO 8601
        timestamp = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        error_response = {
            "error": "Invalid timestamp format. Use ISO 8601 (e.g., 2025-03-17T10:15:00Z)"
        }
        print("POST /logs ->", error_response)
        return jsonify(error_response), 400

    # Store the log entry
    store.add_log(data["service_name"], timestamp, data["message"])

    success_response = {
        "status": "Log ingested successfully",
        "stored_log": {
            "service_name": data["service_name"],
            "timestamp": data["timestamp"],
            "message": data["message"]
        },
        "constraints_applied": {
            "log_expiry_cutoff": (datetime.utcnow() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "thread_safe": True
        }
    }
    print("POST /logs ->", success_response)
    return jsonify(success_response), 200

@app.route("/logs", methods=["GET"])
def query_logs():
    # Extract query parameters
    service = request.args.get("service")
    start = request.args.get("start")
    end = request.args.get("end")

    # Validate required query params
    if not all([service, start, end]):
        error_response = {
            "error": "Missing query parameters. Required: service, start, end"
        }
        print("GET /logs ->", error_response)
        return jsonify(error_response), 400

    try:
        # Parse start and end timestamps
        start_time = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        error_response = {
            "error": "Invalid timestamp format in query parameters. Use ISO 8601 (e.g., 2025-03-17T10:00:00Z)"
        }
        print("GET /logs ->", error_response)
        return jsonify(error_response), 400

    # Query logs within the given time range
    logs = store.query_logs(service, start_time, end_time)

    success_response = {
        "queried_service": service,
        "start": start,
        "end": end,
        "result_count": len(logs),
        "logs": logs,
        "constraints_applied": {
            "log_expiry_cutoff": (datetime.utcnow() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sorted_by_timestamp": True
        }
    }
    print("GET /logs ->", success_response)
    return jsonify(success_response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6050)