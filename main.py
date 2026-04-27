#!/home/pdolcini/pyenv_ev/bin/python3
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

import agent

if __name__ == "__main__":
    try:
        agent.run_digest()
        print("EV digest run complete.")
    except Exception as e:
        print(f"EV digest run failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)