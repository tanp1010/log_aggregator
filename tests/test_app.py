import unittest
import json
from app import app  # Import the Flask app for testing

class LogAggregatorTestCase(unittest.TestCase):
    def setUp(self):
        # Create a test client for sending HTTP requests to the Flask app
        self.client = app.test_client()

    def test_home_route(self):
        # Test the root endpoint to ensure it's working and returning expected keys
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("status", data)
        self.assertIn("constraints", data)

    def test_valid_log_ingestion(self):
        # Test POST /logs with valid log data
        res = self.client.post("/logs", json={
            "service_name": "auth-service",
            "timestamp": "2025-04-04T20:00:00Z",
            "message": "User login"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "Log ingested successfully")
        self.assertIn("stored_log", data)

    def test_missing_field_in_log(self):
        # Test POST /logs with a missing required field ("timestamp")
        res = self.client.post("/logs", json={
            "service_name": "auth-service",
            "message": "Missing timestamp"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_invalid_timestamp_format(self):
        # Test POST /logs with improperly formatted timestamp
        res = self.client.post("/logs", json={
            "service_name": "auth-service",
            "timestamp": "04-04-2025 20:00",  # Not ISO 8601
            "message": "Wrong format"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_valid_log_query(self):
        # First, ingest a log entry
        self.client.post("/logs", json={
            "service_name": "web",
            "timestamp": "2025-04-04T20:15:00Z",
            "message": "Page view"
        })

        # Then, query it with a matching time range
        res = self.client.get("/logs?service=web&start=2025-04-04T20:00:00Z&end=2025-04-04T21:00:00Z")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["result_count"], 1)
        self.assertIn("logs", data)

    def test_query_with_missing_params(self):
        # Test GET /logs with missing query parameters (missing "end")
        res = self.client.get("/logs?service=web&start=2025-04-04T20:00:00Z")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.get_json())

    def test_expired_log_not_returned(self):
        # Add a log with an extremely old timestamp (should be expired)
        self.client.post("/logs", json={
            "service_name": "temp",
            "timestamp": "2000-01-01T00:00:00Z",
            "message": "Should be expired"
        })

        # Query for that log — should return an empty result
        res = self.client.get("/logs?service=temp&start=1990-01-01T00:00:00Z&end=2090-01-01T00:00:00Z")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["result_count"], 0)

# Run all tests
if __name__ == "__main__":
    unittest.main()