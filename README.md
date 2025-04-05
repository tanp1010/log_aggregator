## My Log Aggregator provides a scalable log aggregation service that:
- Ingests logs from different microservices.
- Supports querying logs by service name and time range.
- Stores logs in-memory and removes logs older than 1 hour.
- Handles unordered ingestion and returns logs in sorted timestamp order.
- Provides a thread-safe, concurrent architecture.
- Can handle multiple requests at the same time safely


## Note: Logs can be sent and viewed using simple HTTP requests, all tested and run using terminal windows only.

## Additional Feature Implemented:
- Performed full unit testing to make sure all features work properly, catch edge cases, and help keep the project easy to maintain.

---

## Project Folder Structure

```
log_aggregator/
├── app.py           # Main application file
├── log_store.py     # Where the logs are stored and filtered
├── tests/
│   └── test_app.py  # Unit tests for all main features
├── requirements.txt
└── README.md
```

---

## Tools and Technologies Used

| Tool / Library     | Version        | Purpose                                |
|--------------------|----------------|----------------------------------------|
| Python             | 3.12           | Main language used                     |
| Flask              | 3.0.0          | For building the REST API              |
| threading (Lock)   | built-in       | To make the aggregator thread-safe     |
| bisect             | built-in       | To keep logs sorted by timestamp       |
| unittest           | built-in       | For writing and running test cases     |

---


## How to Set It Up
To get this project running on any PC, please follow these steps:

### 1. Install Python 3.12 or later

### 2. Install required libraries
After installing Python, you need to install the libraries. These are listed in a file called `requirements.txt`.

To install them, run:
```
pip install -r requirements.txt
```
This command will install everything needed to run the aggregator

### 3. Start the aggregator by running: 
```
python app.py
```
If everything is set up correctly, your terminal will show something like:
```
Running on http://0.0.0.0:6050
```
That means the aggregator is running locally at:
```
http://localhost:6050
```
Next, please open a second terminal window and use curl commands to send logs and view them.

---

## How to perform Unit Testing
The test suite can be run using this command:
```
python -m unittest discover -s tests
```
This runs a set of unit tests to make sure all parts of the aggregator work as expected.

---





