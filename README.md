# DNS Benchmarking Tool

## Overview
This script benchmarks various DNS providers to measure query resolution time across multiple domains. It uses `dnspython` for direct DNS queries, providing accurate and realistic performance metrics for different DNS services. Results are displayed in a structured table and can logged to a CSV file for long-term analysis.

## About UV
This script is designed to run with `uv`, a modern Python package manager and runtime that provides fast and isolated execution environments. To install `uv`, follow the instructions at [uv’s official documentation](https://github.com/astral-sh/uv).

To run this script, use:
```sh
uv run dns_benchmark.py
```
`uv` will manage the necessary dependencies.

## Installation

### Prerequisites
- Python **3.8+**
- `uv` package manager

## Usage

### Basic Benchmarking (Default Providers & Domains)
```sh
uv run dns_benchmark.py
```
Runs a benchmark on the default DNS providers and domains.

### Custom DNS Providers
```sh
uv run dns_benchmark.py --dns myFaveDNS.com
```
Adds myFaveDNS.com to the default test set.

### Custom Domains
```sh
uv run dns_benchmark.py --domains example.com
```
Adds example.com  to the default test set.

### Choose a Specific DNS Record Type
```sh
uv run dns_benchmark.py --record AAAA
```
Tests IPv6 resolution times using `AAAA` records.

### Save Results to CSV
```sh
uv run dns_benchmark.py --csv results.csv
```
Appends benchmark results to `results.csv` for long-term tracking.

## Example Output

### Detailed Query Performance Table
```
+-----------------+---------------+---------------+------------------+------------------+------------------+
| Provider Name   | IP Address    | Domain        | Avg Query Time   | Min Query Time   | Max Query Time   |
+-----------------+---------------+---------------+------------------+------------------+------------------+
| Google DNS      | 8.8.8.8       | google.com    | 0.00143          | 0.00120          | 0.00230          |
| Cloudflare DNS  | 1.1.1.1       | apple.com     | 0.00121          | 0.00098          | 0.00175          |
| Quad9 DNS       | 9.9.9.9       | office365.com | 0.00210          | 0.00180          | 0.00290          |
+-----------------+---------------+---------------+------------------+------------------+------------------+
```

### Summary Table
```
+-------------------+-----------------+--------------------------+
| Provider Name     | IP Address      |   Overall Avg Query Time |
+-------------------+-----------------+--------------------------+
| Google DNS        | 8.8.8.8         |                 0.00192 |
| Cloudflare DNS    | 1.1.1.1         |                 0.00185 |
| OpenDNS           | 208.67.222.222  |                 0.00220 |
+-------------------+-----------------+--------------------------+
```

## Design Decisions

### **Switch to `dnspython` for Direct DNS Queries**  
The script originally used `socket.getaddrinfo()` but was changed to `dnspython` for greater accuracy and flexibility. This ensures queries go directly to the specified DNS provider rather than relying on the system resolver, which may cache results or alter behavior. The switch also allows testing additional record types like `TXT` and `MX`, improving the script’s versatility.

### "Overall Avg Query Time" as the Main Performance Metric
This metric was chosen because it represents real-world DNS performance, measuring both network latency and resolver efficiency. It reflects how quickly a DNS provider can return useful results, rather than just raw connection speed.

### No Separate Latency Test
A standalone latency test (e.g., ping or raw UDP timing) was considered but rejected. The reason is that our existing query time measurement already includes network latency and resolver performance. Adding a separate latency test would be redundant.

### Geolocation and Distance Calculation
Originally, the script attempted to estimate the physical distance between the user and each DNS provider using IP geolocation services. However, this approach proved unreliable for anycast providers like Google and Cloudflare, which route queries to the nearest location but register their IPs to corporate headquarters.
