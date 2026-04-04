import sys
import os
sys.path.append(os.getcwd())

from utils.kaggle_bridge import setup_kaggle_env, load_kaggle_secrets
from utils.firebase_handler import FirebaseHandler
from agents.agents import ResearchAgent, UniverseSelectionAgent

def main():
    setup_kaggle_env()
    secrets = load_kaggle_secrets()
    
    if not secrets["firebase"]["enabled"]:
        print("❌ Firebase not enabled. Check Kaggle Secrets.")
        return

    fb = FirebaseHandler(secrets["firebase"])
    research_agent = ResearchAgent()
    universe_agent = UniverseSelectionAgent(research_agent=research_agent)

    print("🔭 Starting Market Research Scan...")
    # 1. Select Universe based on volume/fundamentals
    # Note: We use a smaller scan set for efficiency if needed
    candidates = universe_agent.select_universe(limit=100)
    
    if candidates:
        print(f"✅ Found {len(candidates)} candidates. Pushing to 'research' queue.")
        fb.push_task("research", candidates)
        fb.log_event("research", "SCAN", details=f"Pushed {len(candidates)} candidates to queue.")
    else:
        print("⚠️ No candidates found today.")

if __name__ == "__main__":
    main()
 Riverside
 Riverside
