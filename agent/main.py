import argparse
import os
import sys
import httpx
from dotenv import load_dotenv

# ✅ Видалили імпорт застарілого genai, імпортуємо наш Loop
from loop import AgentLoop
from tools import ToolExecutor
from tracer import init_trace

def get_api_token(api_url: str, email: str, password: str) -> str:
    try:
        r = httpx.post(f"{api_url}/auth/login", json={"email": email, "password": password}, timeout=5.0)
        r.raise_for_status()
        return r.json()["access_token"]
    except Exception as e:
        print(f"❌ Failed to login to CRM API: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="AI-Native Real Estate CRM Agent")
    parser.add_argument("brief", nargs="?", help="The natural language brief for the agent")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    parser.add_argument("--use-api", action="store_true", help="Run in API mode")
    parser.add_argument("--steps", type=int, default=10, help="Max steps")
    
    args = parser.parse_args()
    
    if not args.brief:
        args.brief = input("Enter your brief: ").strip()
        
    if not args.brief:
        print("❌ Brief cannot be empty.")
        sys.exit(1)

    if not args.mock and not args.use_api:
        print("❌ Please specify either --mock or --use-api")
        sys.exit(1)

    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        sys.exit(1)

    init_trace()

    mode = "mock" if args.mock else "api"
    token = ""
    api_url = os.getenv("CRM_API_URL", "http://localhost:3000")
    
    if mode == "api":
        print(f"🔗 Connecting to CRM API at {api_url}...")
        token = get_api_token(api_url, os.getenv("CRM_AGENT_EMAIL"), os.getenv("CRM_AGENT_PASSWORD"))
        print("✅ Authenticated with CRM API")
        
    executor = ToolExecutor(mode=mode, api_url=api_url, token=token)
    
    # ✅ Передаємо api_key у новий AgentLoop
    loop = AgentLoop(executor=executor, api_key=api_key, max_steps=args.steps)
    
    print(f"\n🤖 Agent started (Mode: {mode.upper()}, Max Steps: {args.steps})")
    print(f"📝 Brief: {args.brief}\n")
    
    try:
        final_answer = loop.run(args.brief)
        print("\n" + "="*50)
        print("🏁 FINAL AGENT RESPONSE:")
        print("="*50)
        print(final_answer)
        print(f"\n💾 Trace saved to logs/trace.jsonl")
    except RuntimeError as e:
        print(f"\n🛑 Agent stopped by Guardrails: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()