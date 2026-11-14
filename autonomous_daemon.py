import os
import sys
import time
import socket
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Fix console encoding on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup persistent logging
LOG_DIR = BASE_DIR / "output" / "autopilot_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / "autonomous_autopilot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(log_file), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# DNS Cache
DNS_CACHE = {
    'youtube.googleapis.com': '172.217.112.4',
    'www.googleapis.com': '172.217.116.4',
    'oauth2.googleapis.com': '74.125.133.95',
}
_orig_getaddrinfo = socket.getaddrinfo
def fast_getaddrinfo(host, port, *args, **kwargs):
    if host in DNS_CACHE:
        return _orig_getaddrinfo(DNS_CACHE[host], port, *args, **kwargs)
    return _orig_getaddrinfo(host, port, *args, **kwargs)
socket.getaddrinfo = fast_getaddrinfo

os.environ['QURAN_MASTER_SESSION_AUTH'] = 'AUTHORIZED_786'


def run_master_trend_discovery():
    """Runs Option A: 100% Pure Fresh Trend Discovery (Zero Repeats)."""
    logging.info("=====================================================")
    logging.info("📡 [حالت الف: رادار شکار ترندهای داغ و ۱۰۰٪ جدید]")
    logging.info("=====================================================")
    try:
        import master_quran_factory
        factory = master_quran_factory.MasterQuranFactory()
        res = factory.run_factory_cycle()
        logging.info(f"Master trend factory cycle result: {res}")
    except Exception as e:
        logging.error(f"Error during trend factory cycle: {e}")


def main_daemon():
    logging.info("=====================================================")
    logging.info("🌟 AUTONOMOUS ZERO-TOUCH AUTOPILOT DAEMON ACTIVE")
    logging.info("Mode: Option A - 100% Fresh Trend Discovery (Zero Repeats)")
    logging.info("=====================================================")

    # Infinite loop: checks hourly
    while True:
        try:
            now = datetime.now()
            # Golden hours check: early morning (05:00 / 06:00), afternoon (16:00 / 17:00), night (21:00 / 22:00)
            if now.hour in [5, 6, 16, 17, 21, 22]:
                run_master_trend_discovery()

            # Sleep 1 hour
            time.sleep(3600)
        except KeyboardInterrupt:
            logging.info("Daemon stopped by user.")
            break
        except Exception as e:
            logging.error(f"Autopilot daemon loop warning: {e}")
            time.sleep(120)


if __name__ == "__main__":
    main_daemon()
