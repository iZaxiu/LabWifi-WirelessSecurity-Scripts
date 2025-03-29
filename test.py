import subprocess
import json
import statistics
import csv
import re

def get_bitrate():
    """Ottiene il bitrate attuale dall'output di iwconfig."""
    try:
        result = subprocess.run(["iwconfig"], capture_output=True, text=True, check=True)
        match = re.search(r"Bit Rate=(\d+\.?\d*) Mb/s", result.stdout)
        if match:
            return float(match.group(1))
    except Exception as e:
        print(f"Errore durante l'esecuzione di iwconfig: {e}")
    return None

def run_iperf(server, length):
    """Esegue iperf3 in modalità TCP e restituisce il throughput del mittente e del ricevente."""
    try:
        result = subprocess.run(
            ["iperf3", "-c", server, "-l", str(length), "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        sender_bps = data["end"]["sum_sent"]["bits_per_second"] / 1e6  # Converti in Mb/s
        receiver_bps = data["end"]["sum_received"]["bits_per_second"] / 1e6  # Converti in Mb/s
        return sender_bps, receiver_bps
    except Exception as e:
        print(f"Errore durante l'esecuzione di iperf3: {e}")
        return None, None

def main():
    server = "192.168.118.161"  # Sostituisci con l'indirizzo del server iperf3
    results = []

    for length in range(1000, 1500, 200):  # Test con buffer da 1000B a 5000B (passo 1000B)
        sender_results = []
        receiver_results = []
        bitrate_changes = []

        for i in range(10):  # Esegui 10 esperimenti
            print(f"{i}. Running iperf3 with buffer size {length}B")
            
            bitrate_before = get_bitrate()
            sender_bps, receiver_bps = run_iperf(server, length)
            bitrate_after = get_bitrate()
            
            if sender_bps is not None and receiver_bps is not None and bitrate_before is not None and bitrate_after is not None:
                sender_results.append(sender_bps)
                receiver_results.append(receiver_bps)
                bitrate_changes.append(bitrate_after - bitrate_before)

        if sender_results and receiver_results and bitrate_changes:
            results.append([
                length,
                min(sender_results), max(sender_results), statistics.mean(sender_results), statistics.stdev(sender_results),
                min(receiver_results), max(receiver_results), statistics.mean(receiver_results), statistics.stdev(receiver_results),
                min(bitrate_changes), max(bitrate_changes), statistics.mean(bitrate_changes), statistics.stdev(bitrate_changes)
            ])

    headers = [
        "Buffer Size (B)", "Sender Min (Mb/s)", "Sender Max (Mb/s)", "Sender Avg (Mb/s)", "Sender Std Dev (Mb/s)",
        "Receiver Min (Mb/s)", "Receiver Max (Mb/s)", "Receiver Avg (Mb/s)", "Receiver Std Dev (Mb/s)",
        "Bitrate Change Min (Mb/s)", "Bitrate Change Max (Mb/s)", "Bitrate Change Avg (Mb/s)", "Bitrate Change Std Dev (Mb/s)"
    ]

    print("\nRisultati salvati in iperf_results_tcp.csv")

    

    with open("tcp_basic_144.4_AB.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(results)

if __name__ == "__main__":
    main()
