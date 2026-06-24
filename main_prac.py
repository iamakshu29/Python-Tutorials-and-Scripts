from datetime import datetime, timedelta

logs = [
    # --- ERRORS within last 2 hrs (should appear in output) ---
    {"timestamp": "2026-06-19T14:45:00z", "level": "ERROR", "service": "api-gateway",     "message": "Token Validation Failed"},
    {"timestamp": "2026-06-19T14:15:00z", "level": "ERROR", "service": "payment-service", "message": "Stripe API Unreachable"},
    {"timestamp": "2026-06-19T13:30:00z", "level": "ERROR", "service": "auth-service",    "message": "JWT Secret Missing"},
    {"timestamp": "2026-06-19T14:50:00z", "level": "ERROR", "service": "api-gateway",     "message": "Rate Limit Exceeded"},
    {"timestamp": "2026-06-19T14:05:00z", "level": "ERROR", "service": "payment-service", "message": "Database Connection Timeout"},

    # --- Non-ERROR within last 2 hrs (filtered out by level) ---
    {"timestamp": "2026-06-19T14:30:00z", "level": "INFO",  "service": "api-gateway",     "message": "Request Processed Successfully"},
    {"timestamp": "2026-06-19T14:00:00z", "level": "INFO",  "service": "auth-service",    "message": "User Login Successful"},

    # --- ERRORS older than 2 hrs (filtered out by time) ---
    {"timestamp": "2026-06-19T12:00:00z", "level": "ERROR", "service": "payment-service", "message": "Old Stripe Timeout"},
    {"timestamp": "2026-06-19T10:00:00z", "level": "ERROR", "service": "api-gateway",     "message": "Old Gateway Error"},

    # --- Malformed entries (handle gracefully) ---
    {"timestamp": "2026-06-19T14:40:00z", "level": "ERROR"},                                                                     # missing service & message
    {"level": "ERROR", "service": "auth-service", "message": "Token Expired"},                                                  # missing timestamp
    {"timestamp": "2026-06-19T14:50:00z", "level": "ERROR", "service": "payment-service"},                                       # missing message
    "this is not a dict at all",                                                                                                 # completely malformed
]

# filter error from last 2 hrs
# group by service and print count + all messages per service
# handle missing keys and malformed lines gracefull

now = datetime.now()
two_hrs_ago = now - timedelta(hours=2)

def lets_filter(logs):
    filtered_logs = []
    for i in range(len(logs)):
        log_time = datetime.fromisoformat(
            logs[i].get("timestamp").replace("z", "+00:00")
        )
        log_time_naive = log_time.replace(tzinfo=None)
        if start_time <= log_time_naive <= end_time:
            filtered_logs.append(logs)

    return logs

get_logs = lets_filter(logs)

print(get_logs)