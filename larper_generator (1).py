import asyncio
import aiohttp
import random
import string
import sys
import time
import os
import json
import signal
from datetime import datetime

# ============================================================
#   Larper Generator — by @xndv
#   TikTok Username Hunter  [FAST MODE - async + persistent log]
# ============================================================

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

CONCURRENT = 20

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE   = os.path.join(SCRIPT_DIR, "larper_log.json")

STOP = False
LOG  = None

# ─── SIGNAL HANDLER ─────────────────────────────────────────

def handle_exit(sig=None, frame=None):
    global STOP
    STOP = True
    if LOG is not None:
        save_log(LOG)
        print(f"\n  {YELLOW}[!] Closing. Log saved ({len(LOG['checked'])} names).{RESET}\n")
    sys.exit(0)

signal.signal(signal.SIGINT,  handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# ─── LOG ────────────────────────────────────────────────────

def load_log():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"checked": {}, "available": [], "sessions": 0}

def save_log(log):
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(log, f, indent=2)
    except Exception:
        pass

def log_result(log, username, result):
    if STOP:
        return
    log["checked"][username] = {
        "result": result,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if result == "available" and username not in log["available"]:
        log["available"].append(username)
    if len(log["checked"]) % 10 == 0:
        save_log(log)

# ─── UI ─────────────────────────────────────────────────────

def banner():
    print(f"""
{CYAN}{BOLD}
  ██╗      █████╗ ██████╗ ██████╗ ███████╗██████╗ 
  ██║     ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
  ██║     ███████║██████╔╝██████╔╝█████╗  ██████╔╝
  ██║     ██╔══██║██╔══██╗██╔═══╝ ██╔══╝  ██╔══██╗
  ███████╗██║  ██║██║  ██║██║     ███████╗██║  ██║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
{RESET}
{WHITE}{BOLD}  G E N E R A T O R{RESET}  {GRAY}by discord:@xndv{RESET}
  {GRAY}TikTok Username Sniper  [{GREEN}FAST MODE{GRAY}]{RESET}
{GRAY}  ─────────────────────────────────────────────────{RESET}
""")

def credits(log):
    total_checked = len(log["checked"])
    total_avail   = len(log["available"])
    sessions      = log["sessions"]

    print(f"  {GRAY}Tool      : {WHITE}Larper Tiktok Name sniper{RESET}")
    print(f"  {GRAY}Author    : {CYAN}dc:@xndv{RESET}")
    print(f"  {GRAY}Version   : {WHITE}4.0 (async + instant log){RESET}")
    print(f"  {GRAY}Parallel  : {GREEN}{CONCURRENT} simultaneous requests{RESET}")
    print(f"\n{GRAY}  ── Persistent log ({os.path.basename(LOG_FILE)}) ──────────────{RESET}")
    print(f"  {GRAY}Previous sessions  : {WHITE}{sessions}{RESET}")
    print(f"  {GRAY}Already checked    : {WHITE}{total_checked}{RESET}  {GRAY}(will not be repeated){RESET}")
    print(f"  {GRAY}Already found      : {GREEN}{total_avail}{RESET}")
    if total_avail > 0:
        print(f"\n  {GRAY}Previously available:{RESET}")
        for name in log["available"][-5:]:
            print(f"    {GREEN}@{name}{RESET}  ->  {CYAN}tiktok.com/@{name}{RESET}")
        if total_avail > 5:
            print(f"    {GRAY}... and {total_avail - 5} more. Check larper_log.json for full list.{RESET}")
    print(f"\n{GRAY}  ─────────────────────────────────────────────────{RESET}\n")

def menu():
    print(f"  {WHITE}Username length:{RESET}")
    length = input(f"  {CYAN}> {RESET}").strip()
    try:
        length = int(length)
        if not 1 <= length <= 24:
            raise ValueError
    except ValueError:
        print(f"\n  {RED}Invalid value. Use a number between 1 and 24.{RESET}\n")
        input("  Press Enter to exit...")
        sys.exit(1)

    print(f"\n  {WHITE}How many available names do you want to find?{RESET}")
    goal = input(f"  {CYAN}> {RESET}").strip()
    try:
        goal = int(goal)
        if goal < 1:
            raise ValueError
    except ValueError:
        print(f"\n  {RED}Invalid value.{RESET}\n")
        input("  Press Enter to exit...")
        sys.exit(1)

    print(f"""
  {WHITE}Username type:{RESET}
  {GRAY}[1]{RESET} Letters           e.g nega
  {GRAY}[2]{RESET} Numbers           e.g 1939
  {GRAY}[3]{RESET} Mixed (letters + numbers) e.g n3ga
  {GRAY}[4]{RESET} With underscores  e.g. ab_cd
  {GRAY}[5]{RESET} With dots         e.g. ab.cd
""")
    mode = input(f"  {CYAN}> {RESET}").strip()
    if mode not in ["1","2","3","4","5"]:
        mode = "1"

    return length, goal, mode

# ─── GENERATOR ──────────────────────────────────────────────

def generate_name(length, mode):
    alpha = string.ascii_lowercase
    nums  = string.digits
    mix   = alpha + nums

    if mode == "1":
        return ''.join(random.choices(alpha, k=length))
    elif mode == "2":
        return ''.join(random.choices(nums, k=length))
    elif mode == "3":
        return ''.join(random.choices(mix, k=length))
    elif mode == "4":
        base = list(random.choices(alpha, k=length))
        if length > 2:
            base[random.randint(1, length - 2)] = '_'
        return ''.join(base)
    elif mode == "5":
        base = list(random.choices(alpha, k=length))
        if length > 2:
            base[random.randint(1, length - 2)] = '.'
        return ''.join(base)
    else:
        return ''.join(random.choices(alpha, k=length))

# ─── CHECKER ────────────────────────────────────────────────

async def check_username(session, username, semaphore):
    url = f"https://www.tiktok.com/oembed?url=https://www.tiktok.com/@{username}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with semaphore:
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                if resp.status == 200:
                    return username, "taken"
                elif resp.status == 404:
                    return username, "available"
                else:
                    return username, "error"
        except asyncio.TimeoutError:
            return username, "timeout"
        except Exception:
            return username, "error"

# ─── HUNT ───────────────────────────────────────────────────

async def hunt(length, goal, mode, log):
    global STOP
    mode_names = {"1":"letters","2":"numbers","3":"mixed","4":"underscores","5":"dots"}
    found   = []
    total   = 0
    taken   = 0
    errors  = 0
    start   = time.time()

    already_checked = set(log["checked"].keys())
    skipped = sum(1 for k in already_checked if len(k) == length)

    print(f"\n{GRAY}  ─────────────────────────────────────────────────{RESET}")
    print(f"  {WHITE}Starting hunt...{RESET}")
    print(f"  {GRAY}length={WHITE}{length}{RESET}  {GRAY}goal={WHITE}{goal}{RESET}  {GRAY}type={WHITE}{mode_names.get(mode,'?')}{RESET}  {GRAY}parallel={GREEN}{CONCURRENT}{RESET}")
    if skipped > 0:
        print(f"  {GRAY}Skipping {YELLOW}{skipped}{GRAY} names already checked in previous sessions{RESET}")
    print(f"  {GRAY}Close window or Ctrl+C to stop (log is saved automatically){RESET}")
    print(f"{GRAY}  ─────────────────────────────────────────────────{RESET}\n")

    semaphore = asyncio.Semaphore(CONCURRENT)
    connector = aiohttp.TCPConnector(limit=CONCURRENT, ssl=False)
    checked_this_session = set()

    async with aiohttp.ClientSession(connector=connector) as session:
        while len(found) < goal and not STOP:
            batch = []
            attempts = 0
            while len(batch) < CONCURRENT and attempts < 50000:
                name = generate_name(length, mode)
                if name not in already_checked and name not in checked_this_session:
                    checked_this_session.add(name)
                    batch.append(name)
                attempts += 1

            if not batch:
                print(f"\n  {YELLOW}[!] Combinations exhausted for this length/type.{RESET}")
                break

            tasks = [check_username(session, name, semaphore) for name in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for item in results:
                if STOP or len(found) >= goal:
                    break
                if isinstance(item, Exception):
                    continue
                username, result = item
                total += 1
                elapsed = time.time() - start
                rate = total / elapsed if elapsed > 0 else 0

                log_result(log, username, result)

                if result == "available":
                    found.append(username)
                    print(f"  {GREEN}{BOLD}[+] @{username:<{length+2}} AVAILABLE{RESET}  {GRAY}({len(found)}/{goal})  [{rate:.1f}/s]{RESET}")
                elif result == "taken":
                    taken += 1
                    print(f"  {RED}[-] @{username:<{length+2}} taken{RESET}  {GRAY}[{total} checked  {rate:.1f}/s]{RESET}")
                else:
                    errors += 1
                    print(f"  {YELLOW}[?] @{username:<{length+2}} error/timeout{RESET}  {GRAY}[{total} checked]{RESET}")

    save_log(log)
    print(f"\n  {GRAY}Log saved -> {WHITE}{LOG_FILE}{RESET}")

    return found, total, taken, errors, start

# ─── RESULTS ────────────────────────────────────────────────

def show_results(found, total, taken, errors, start):
    elapsed = time.time() - start
    rate = total / elapsed if elapsed > 0 else 0

    print(f"\n{GRAY}  ─────────────────────────────────────────────────{RESET}")
    print(f"  {WHITE}{BOLD}SESSION RESULTS{RESET}")
    print(f"{GRAY}  ─────────────────────────────────────────────────{RESET}")
    print(f"  {GRAY}Checked    : {WHITE}{total}{RESET}")
    print(f"  {GRAY}Available  : {GREEN}{len(found)}{RESET}")
    print(f"  {GRAY}Taken      : {RED}{taken}{RESET}")
    print(f"  {GRAY}Errors     : {YELLOW}{errors}{RESET}")
    print(f"  {GRAY}Time       : {WHITE}{elapsed:.1f}s{RESET}")
    print(f"  {GRAY}Speed      : {GREEN}{rate:.1f} checks/s{RESET}")
    print(f"{GRAY}  ─────────────────────────────────────────────────{RESET}\n")

    if found:
        print(f"  {GREEN}{BOLD}Available names found:{RESET}\n")
        for name in found:
            print(f"    {GREEN}@{name}{RESET}  ->  {CYAN}https://www.tiktok.com/@{name}{RESET}")
    else:
        print(f"  {YELLOW}No available names found.{RESET}")

    print(f"\n{GRAY}  ─────────────────────────────────────────────────{RESET}")
    print(f"  {GRAY}Larper Generator — by {CYAN}@xndv{RESET}\n")

# ─── MAIN ───────────────────────────────────────────────────

async def main():
    global LOG
    banner()
    LOG = load_log()
    LOG["sessions"] += 1
    credits(LOG)
    length, goal, mode = menu()
    found, total, taken, errors, start = await hunt(length, goal, mode, LOG)
    if not STOP:
        show_results(found, total, taken, errors, start)
        input(f"  {GRAY}Press Enter to exit...{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
