import sys
from youtube_uploader import get_authenticated_service, CHANNELS

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print("=" * 60, flush=True)
    print("      YouTube Channels One-Time OAuth Authorization", flush=True)
    print("=" * 60, flush=True)
    print("This script will authorize your 3 YouTube channels.\n", flush=True)

    for key, info in CHANNELS.items():
        print("-" * 50, flush=True)
        print(f"Channel: {info['name']}", flush=True)
        print(f"Email: {info['email']}", flush=True)
        print(f"Token File: {info['token_file'].name}", flush=True)
        
        if info['token_file'].exists():
            print("  [OK] Already authenticated (token exists).", flush=True)
            continue
            
        print(f"\n>>> Please authorize for: {info['email']}", flush=True)
        try:
            get_authenticated_service(key)
            print(f"  [SUCCESS] Successfully connected to {info['email']}!", flush=True)
        except Exception as e:
            print(f"  [ERROR] Failed to connect to {key}: {e}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("OAuth authorization process finished.", flush=True)

if __name__ == "__main__":
    main()
