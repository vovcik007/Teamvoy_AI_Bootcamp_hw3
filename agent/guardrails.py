import time
from typing import Optional

class Guardrails:
    def __init__(self, max_steps: int = 10, timeout_seconds: int = 60):
        self.max_steps = max_steps
        self.timeout_seconds = timeout_seconds
        self.start_time = time.time()
        self.current_step = 0

    def check_step(self):
        """Перевіряє ліміти перед виконанням кроку. Кидає Exception, якщо перевищено."""
        self.current_step += 1
        
        if self.current_step > self.max_steps:
            raise RuntimeError(f"Guardrail: Reached max steps limit ({self.max_steps}). Stopping agent.")
        
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            raise RuntimeError(f"Guardrail: Reached timeout limit ({self.timeout_seconds}s). Stopping agent.")

    def get_status(self) -> dict:
        return {
            "step": self.current_step,
            "max_steps": self.max_steps,
            "elapsed_seconds": round(time.time() - self.start_time, 2)
        }