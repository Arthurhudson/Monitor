# System Resource Monitoring Tool

A Python-based system resource monitoring tool that tracks CPU, memory, disk usage, and other system metrics, sending alert emails when thresholds are exceeded.

## Features

- Monitor key system metrics:
  - CPU usage, core count, frequency, and system load
  - Memory usage and swap status
  - Disk usage and available space
  - Network traffic statistics (bytes sent/received, errors, packet loss)
- Monitor critical process status
- Support for multiple alert levels (warning and critical)
- Alert frequency control to avoid alert flooding
- JSON format persistence for monitoring data
- Automatic log rotation (max 10MB, keeps 5 backups)
- Graceful exit with data saving
- Type annotation support

## Requirements

- Python 3.6+
- psutil >= 5.9.0
- typing-extensions >= 4.5.0

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Arthurhudson/Monitor.git
cd Monitor
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure monitoring parameters:
   - Copy configuration template: `cp config/config.py.template config/config.py`
   - Modify parameters in `config.py`

## Configuration

The configuration file is located at `config/config.py`. Main configuration items include:

```python
MONITOR_CONFIG = {
    'interval': 300,  # Monitoring interval (seconds)
    'log_file': '../logs/monitor.log',  # Log file path

    # Resource usage thresholds (percentage)
    'thresholds': {
        'cpu': 80,
        'memory': 80,
        'disk': 85,
        'network': {
            'bytes_sent': 1000000,  # 1MB/s
            'bytes_recv': 1000000   # 1MB/s
        }
    },

    # Critical processes to monitor
    'critical_processes': [
        'nginx',
        'mysql',
        'redis-server'
    ],

    # Alert configuration
    'alert': {
        'interval': 3600,  # Minimum interval between same alerts (seconds)
        'levels': {
            'warning': 80,  # Warning threshold
            'critical': 90  # Critical threshold
        }
    },

    # Email configuration
    'email': {
        'sender': 'your-email@example.com',
        'receiver': 'admin@example.com',
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'username': 'your-username',
        'password': 'your-password'
    }
}
```

## Running

1. Direct execution:
```bash
python3 src/monitor.py
```

2. Background execution:
```bash
nohup python3 src/monitor.py > /dev/null 2>&1 &
```

## Logs and Data Files

- Monitor logs: `logs/monitor.log`
  - Automatic rotation, maximum 10MB per file
  - Keeps 5 most recent backup files
- Monitor data: `logs/metrics_YYYYMMDD.json`
  - New file generated daily
  - JSON format storage
  - Stores last 1000 records

## Alert System

The system supports two alert levels:
- Warning: Resource usage exceeds warning threshold (default 80%)
- Critical: Resource usage exceeds critical threshold (default 90%)

Alert information includes:
- Alert level and timestamp
- CPU information (usage, core count, frequency, system load)
- Memory information (total, available, usage, swap status)
- Disk information (total, used, available, usage)
- Network status (send/receive traffic, errors, packet loss)
- Critical process status

## Important Notes

1. Ensure email server information is correct in the configuration
2. Recommended monitoring interval is 5 minutes or more
3. Appropriate system permissions required for process information
4. Ensure write permissions for log directory
5. Configuration file must include all required fields

## Contributing

Issues and Pull Requests are welcome to improve this tool. When submitting code:

1. Ensure code includes appropriate type annotations
2. Pass all test cases
3. Update relevant documentation

## License

MIT License
