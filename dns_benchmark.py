#!/usr/bin/env python3
# /// script
# dependencies = ["statistics", "tabulate", "dnspython"]
# ///

import asyncio
import time
import statistics
import argparse
import csv
import datetime
import dns.resolver
from tabulate import tabulate

# Default DNS providers
DEFAULT_DNS_PROVIDERS = {
    "Google DNS": "8.8.8.8",
    "Cloudflare DNS 1": "1.1.1.1",
    "Cloudflare DNS 2": "1.0.0.1",
    "OpenDNS 1": "208.67.222.123",
    "OpenDNS 2": "208.67.222.222",
    "Level3 DNS": "4.2.2.1",
    "Quad9 DNS": "9.9.9.9",
    "AdGuard DNS": "176.103.130.132",
    "Comodo Secure DNS": "8.26.56.26",
    "NextDNS 1": "45.90.28.202",
    "NextDNS 2": "45.90.28.0",
    "FIOS Default 1": "71.252.0.12",
    "FIOS Default 2": "68.237.161.12",
    "FIOS VA Opt-Out": "71.252.0.14",
    "FIOS NY Opt-Out": "68.237.161.14",
}

# Default domains to test
DEFAULT_DOMAINS = ["google.com", "apple.com", "office365.com", "icloud.com"]

async def resolve_domain(domain, provider, record_type="A"):
    """Resolves a domain name using the given DNS provider and returns the query time."""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [provider]  # Directly query the specified DNS provider

    start_time = time.perf_counter()
    try:
        resolver.resolve(domain, record_type)
        end_time = time.perf_counter()
        return end_time - start_time
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
        return None  # Return None for failed resolutions

async def benchmark_provider(provider, domains, record_type="A", num_queries=10):
    """Benchmarks a DNS provider by performing multiple queries and calculating statistics for each domain."""
    results = {}
    all_query_times = []  # Stores all times for this provider

    for domain in domains:
        query_times = [await resolve_domain(domain, provider, record_type) for _ in range(num_queries)]
        query_times = [t for t in query_times if t is not None]  # Remove failed queries

        if query_times:
            results[domain] = {
                "avg_query_time": statistics.mean(query_times),
                "min_query_time": min(query_times),
                "max_query_time": max(query_times),
            }
            all_query_times.extend(query_times)
        else:
            results[domain] = {
                "avg_query_time": None,
                "min_query_time": None,
                "max_query_time": None,
            }

    return provider, results, all_query_times

def save_to_csv(csv_filename, results, record_type):
    """Saves benchmark results to a CSV file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = False

    try:
        with open(csv_filename, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass  # File doesn't exist yet, will create a new one

    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header if the file is new
        if not file_exists:
            writer.writerow(["Timestamp", "Provider Name", "IP Address", "Domain", "Query Type", "Avg Query Time", "Min Query Time", "Max Query Time"])

        for provider_name, provider_ip, domain, avg, min_t, max_t in results:
            writer.writerow([timestamp, provider_name, provider_ip, domain, record_type, avg, min_t, max_t])

async def main():
    """Main function to benchmark DNS providers and print the results."""

    parser = argparse.ArgumentParser(description="Benchmark DNS providers using dnspython.")
    parser.add_argument("--dns", nargs="+", help="List of DNS providers to test (IP addresses).")
    parser.add_argument("--domains", nargs="+", help="List of domains to test.")
    parser.add_argument("--record", default="A", choices=["A", "AAAA", "TXT", "MX", "NS", "CNAME"], help="DNS record type to query (default: A).")
    parser.add_argument("--csv", help="CSV file to save results.")
    args = parser.parse_args()

    dns_providers = DEFAULT_DNS_PROVIDERS.copy()
    if args.dns:
        for dns in args.dns:
            dns_providers[dns] = dns  # Allow user-defined IPs

    domains = DEFAULT_DOMAINS.copy()
    if args.domains:
        domains.extend(args.domains)

    tasks = [benchmark_provider(ip, domains, args.record) for ip in dns_providers.values()]
    provider_results = await asyncio.gather(*tasks)

    table_data = []
    csv_data = []
    headers = ["Provider Name", "IP Address", "Domain", "Avg Query Time", "Min Query Time", "Max Query Time"]

    summary_data = []
    for provider_name, provider_ip in dns_providers.items():
        provider_result = next((p for p in provider_results if p[0] == provider_ip), None)
        if provider_result:
            _, results, all_query_times = provider_result
            for domain, result in results.items():
                if result["avg_query_time"] is not None:
                    table_data.append([
                        provider_name, provider_ip, domain,
                        f"{result['avg_query_time']:.6f}",
                        f"{result['min_query_time']:.6f}",
                        f"{result['max_query_time']:.6f}"
                    ])
                    csv_data.append([
                        provider_name, provider_ip, domain,
                        result["avg_query_time"],
                        result["min_query_time"],
                        result["max_query_time"]
                    ])
                else:
                    table_data.append([provider_name, provider_ip, domain, "Failed to resolve", "N/A", "N/A"])

            if all_query_times:  # Ensure we have valid query times
                overall_avg_query_time = sum(all_query_times) / len(all_query_times)
                summary_data.append([provider_name, provider_ip, f"{overall_avg_query_time:.6f}"])
            else:
                summary_data.append([provider_name, provider_ip, "Failed to resolve any domains"])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Sort summary by query time, ensuring "Failed to resolve any domains" stays last
    summary_data.sort(key=lambda x: float(x[2]) if x[2] != "Failed to resolve any domains" else float('inf'))

    # Print Summary Table
    summary_headers = ["Provider Name", "IP Address", "Overall Avg Query Time"]
    print("\nSummary:")
    print(tabulate(summary_data, headers=summary_headers, tablefmt="grid"))

    # Save to CSV if requested
    if args.csv:
        save_to_csv(args.csv, csv_data, args.record)
        print(f"\nResults saved to {args.csv}")

if __name__ == "__main__":
    asyncio.run(main())
