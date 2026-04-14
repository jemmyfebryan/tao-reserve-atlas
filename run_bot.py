#!/usr/bin/env python3
"""
Quick script to run the Atlas Discord bot.
"""
import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🚀 Launching Atlas Bot...", flush=True)

try:
    from bot import start_bot
    start_bot()
except KeyboardInterrupt:
    print("\n\n👋 Atlas Bot stopped by user", flush=True)
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error starting bot: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
