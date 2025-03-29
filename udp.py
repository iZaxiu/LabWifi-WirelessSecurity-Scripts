import subprocess
import json
import statistics
import csv

def run_iperf(server, rate, length):
    try:
        result = subprocess.run(
            ["iperf3", "-c", server, "-u", "-b", rate, "-l", str(length), "--json"],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)
        sender_bps = data["end"]["sum_sent"]["bits_per_second"] / 1e6  # Convert to Mb/s
        receiver_bps = data["end"]["sum_received"]["bits_per_second"] / 1e6  # Convert to Mb/s
        return sender_bps, receiver_bps

    except Exception as e:
        print(f"Error running iperf3: {e}")
        return None, None

def main():
    server = "192.168.106.116"  # Replace with actual server address
    rate = "1000M"  # Replace with desired sending rate (e.g., "10M")
    results = []

    for length in range(1000, 15000, 2000):  # Buffer size from 1000B to 15000B in steps of 1000
        sender_results = []
        receiver_results = []

        for i in range(10):
            print(f"{i}. Running iperf3 with buffer size {length}B")
            sender_bps, receiver_bps = run_iperf(server, rate, length)
            if sender_bps is not None:
                sender_results.append(sender_bps)
                receiver_results.append(receiver_bps)

        if sender_results and receiver_results:
            results.append([
                length,
                min(sender_results), max(sender_results), statistics.mean(sender_results), statistics.stdev(sender_results),
                min(receiver_results), max(receiver_results), statistics.mean(receiver_results), statistics.stdev(receiver_results)
            ])

    headers = [
        "Buffer Size (B)", "Sender Min (Mb/s)", "Sender Max (Mb/s)", "Sender Avg (Mb/s)", "Sender Std Dev (Mb/s)",
        "Receiver Min (Mb/s)", "Receiver Max (Mb/s)", "Receiver Avg (Mb/s)", "Receiver Std Dev (Mb/s)"
    ]

    print("\nSummary saved to iperf_results.csv")
    with open("udp_wifi_wifi__AB_casas.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(results)

if __name__ == "__main__":
    main()
