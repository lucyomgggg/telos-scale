#!/usr/bin/env python3
"""
Simple demonstration script for Telos-Scale v0.1.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telos_scale.core import TelosScale

def main():
    print("=== Telos-Scale Demo (v0.1) ===")
    print("This demo runs a single autonomous loop using default settings.")
    print("Make sure Docker is running and OPENROUTER_API_KEY is set (optional).")
    print()
    
    agent = TelosScale()
    print("Agent initialized. Running loop...")
    try:
        result = agent.run_loop()
        print("✅ Loop completed!")
        print(f"Goal: {result['goal']}")
        print(f"Result: {result['result']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This may be due to missing dependencies or Docker not running.")
        print("For a simpler test, run the unit tests.")
        return 1
    
    print("\nDemo finished. You can run more loops with:")
    print("  telos-scale run --loops 10")
    return 0

if __name__ == "__main__":
    sys.exit(main())