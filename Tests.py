import subprocess
import json
import argparse
import os
import statistics
from datetime import datetime

def run_iperf3_test(server, protocol='TCP', buffer_size=1000, bandwidth=30, num_runs=10):
    """
    Run iperf3 tests with specified parameters and collect results
    
    :param server: Target server IP or hostname
    :param protocol: 'TCP' or 'UDP'
    :param buffer_size: Buffer size in bytes
    :param bandwidth: Bandwidth for UDP tests (Mbps)
    :param num_runs: Number of test runs
    :return: List of throughput measurements
    """
    results = []
    
    # Create output directory if it doesn't exist
    output_dir = 'iperf3_results'
    os.makedirs(output_dir, exist_ok=True)
    
    for run in range(1, num_runs + 1):
        print(f"Running {protocol} test - Buffer Size: {buffer_size} bytes - Run {run}/{num_runs}")
        
        # Construct iperf3 command based on protocol
        if protocol.upper() == 'UDP':
            cmd = [
                'iperf3', '-c', server, 
                '-u',  # UDP mode
                '-b', f'{bandwidth}M',  # Bandwidth
                '-l', str(buffer_size),  # Buffer size
                '-J'  # JSON output
            ]
        else:  # TCP
            cmd = [
                'iperf3', '-c', server, 
                '-l', str(buffer_size),  # Buffer size
                '-J'  # JSON output
            ]
        
        try:
            # Run iperf3 and capture output
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse JSON output to extract receiver throughput
            json_result = json.loads(result.stdout)
            
            # Extract receiver throughput (Mbits/sec)
            throughput = json_result['end']['sum_received']['bits_per_second'] / 1_000_000
            results.append(throughput)
            
            print(f"Throughput for run {run}: {throughput:.2f} Mbits/sec")
        
        except subprocess.CalledProcessError as e:
            print(f"Error in run {run}: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error in run {run}: {e}")
    
    return results

def analyze_results(results, buffer_size, protocol):
    """
    Compute statistical analysis of results
    
    :param results: List of throughput measurements
    :param buffer_size: Buffer size used
    :param protocol: Test protocol
    :return: Dictionary with results and statistics
    """
    # Compute statistics
    if results:
        stats = {
            'min': min(results),
            'max': max(results),
            'mean': sum(results) / len(results),
            'std': statistics.stdev(results) if len(results) > 1 else 0
        }
    else:
        stats = {
            'min': 0,
            'max': 0,
            'mean': 0,
            'std': 0
        }
    
    # Print statistics
    print("\nTest Statistics:")
    for stat, value in stats.items():
        print(f"{stat.capitalize()}: {value:.2f} Mbits/sec")
    
    # Prepare result dictionary
    result_data = {
        'throughput_values': results,
        'buffer_size': buffer_size,
        'protocol': protocol,
        **stats
    }
    
    return result_data

def save_to_csv(results_list, filename):
    """
    Save results to CSV file
    
    :param results_list: List of result dictionaries
    :param filename: Output CSV filename
    """
    with open(filename, 'w') as f:
        # Write header
        headers = [
            'protocol', 'buffer_size', 
            'throughput_values', 
            'min', 'max', 'mean', 'std'
        ]
        f.write(','.join(headers) + '\n')
        
        # Write data rows
        for result in results_list:
            # Convert throughput values to comma-separated string
            throughput_str = ';'.join(map(str, result['throughput_values']))
            
            row = [
                result['protocol'], 
                str(result['buffer_size']), 
                f'"{throughput_str}"',
                str(result['min']), 
                str(result['max']), 
                str(result['mean']), 
                str(result['std'])
            ]
            f.write(','.join(row) + '\n')

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Iperf3 Performance Testing Script')
    parser.add_argument('protocol', choices=['TCP', 'UDP'], 
                        help='Test protocol (TCP or UDP)')
    parser.add_argument('server', help='Target server IP or hostname')
    parser.add_argument('--bandwidth', type=int, default=30, 
                        help='Bandwidth for UDP tests in Mbits/sec (default: 30)')
    
    args = parser.parse_args()
    
    # Buffer sizes to test
    buffer_sizes = [1000]
    
    # Collect all results
    all_results = []
    
    # Run tests for each buffer size
    for buffer_size in buffer_sizes:
        print(f"\n--- Testing Buffer Size: {buffer_size} bytes ---")
        results = run_iperf3_test(
            server=args.server, 
            protocol=args.protocol, 
            buffer_size=buffer_size,
            bandwidth=args.bandwidth
        )
        
        # Analyze and store results
        buffer_results = analyze_results(results, buffer_size, args.protocol)
        all_results.append(buffer_results)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'iperf3_results_{args.protocol}_{timestamp}.csv'
    
    # Save to CSV
    save_to_csv(all_results, filename)
    print(f"\nResults saved to {filename}")

if __name__ == '__main__':
    main()

# TCP test
#python iperf3_test_script.py TCP 192.168.1.24

# UDP test with default 30M bandwidth
#python iperf3_test_script.py UDP 192.168.1.100

# UDP test with custom 50M bandwidth
#python iperf3_test_script.py UDP 192.168.1.100 --bandwidth 50