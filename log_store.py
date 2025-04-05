from threading import Lock  # Ensures thread-safe access to shared data
from datetime import datetime, timedelta  # Used for log timestamps and expiry
import bisect  # For maintaining sorted order efficiently

class LogStore:
    def __init__(self):
        self.logs = {}  # Dictionary to store logs grouped by service name
        self.lock = Lock()  # Lock for thread-safe operations

    def _expire_old_logs(self):
        # Remove logs older than 1 hour for each service
        cutoff = datetime.utcnow() - timedelta(hours=1)
        for service, entries in self.logs.items():
            self.logs[service] = [entry for entry in entries if entry["timestamp"] > cutoff]

    def add_log(self, service_name, timestamp, message):
        with self.lock:
            # Ensure old logs are cleaned before adding new one
            self._expire_old_logs()

            # Initialize the log list if it's a new service
            if service_name not in self.logs:
                self.logs[service_name] = []

            # Insert the log while maintaining sorted order by timestamp
            bisect.insort(self.logs[service_name], {
                "timestamp": timestamp,
                "message": message
            })

    def query_logs(self, service_name, start_time, end_time):
        with self.lock:
            # Clean up expired logs before querying
            self._expire_old_logs()

            # Return empty list if no logs for this service
            if service_name not in self.logs:
                return []

            # Filter logs by time range and format timestamps for output
            return [
                {
                    "timestamp": log["timestamp"].isoformat() + "Z",
                    "message": log["message"]
                }
                for log in self.logs[service_name]
                if start_time <= log["timestamp"] <= end_time
            ]