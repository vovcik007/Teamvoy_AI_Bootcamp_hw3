from google import genai
from google.genai import types
from tools import TOOL_DEFINITIONS, ToolExecutor
from guardrails import Guardrails
from tracer import log_trace

class AgentLoop:
    def __init__(self, executor: ToolExecutor, api_key: str, max_steps: int = 10):
        self.system_instruction = (
            "You are an AI assistant for a Real Estate CRM. "
            "Your goal is to help agents onboard clients, manage properties, and log activities.\n\n"
            "CRITICAL RULES:\n"
                "1. ALWAYS use 'search_companies' or 'search_contacts' BEFORE creating new records to prevent duplicates (idempotency) WITHOUT ANY EXCEPTIONS.\n"
            "2. Always use the provided tools to interact with the CRM. Never hallucinate IDs.\n"
            "3. If a tool returns a 'validation_error' or '400 Bad Request', carefully read the 'detail', fix the arguments (e.g., ensure correct snake_case/camelCase mapping), and retry.\n"
            "4. Chain dependencies correctly: you MUST have a company_id before creating a contact, and a company_id/contact_id before creating a deal.\n"
            "5. When the task is fully completed, provide a concise, structured summary of what was created (with IDs)."
        )
        self.executor = executor
        self.guardrails = Guardrails(max_steps=max_steps)
        
        # ✅ Ініціалізуємо новий офіційний клієнт
        self.client = genai.Client(api_key=api_key)
        
        # ✅ ВИПРАВЛЕНО: Інструменти передаються всередині GenerateContentConfig
        self.genai_config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=TOOL_DEFINITIONS)]
        )

    def run(self, user_brief: str) -> str:
        log_trace("agent_start", {"brief": user_brief})
        
        # Початковий контекст розмови
        contents = [{"role": "user", "parts": [{"text": user_brief}]}]
        final_response = "Agent stopped without a final response."
        
        while True:
            self.guardrails.check_step()
            
            # ✅ ВИПРАВЛЕНО: використовуємо config=self.genai_config замість tools=...
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=contents,
                config=self.genai_config
            )
            
            candidate = response.candidates[0]
            parts = candidate.content.parts
            
            # Перевіряємо, чи модель хоче викликати інструмент
            if parts and parts[0].function_call:
                fc = parts[0].function_call
                tool_name = fc.name
                tool_args = dict(fc.args) if fc.args else {}
                
                log_trace("tool_call", {
                    "step": self.guardrails.current_step,
                    "name": tool_name,
                    "args": tool_args
                })
                
                # Виконуємо інструмент (Mock або API)
                result = self.executor.execute(tool_name, tool_args)
                
                log_trace("tool_result", {
                    "step": self.guardrails.current_step,
                    "name": tool_name,
                    "result": result
                })
                
                # Додаємо виклик моделі до історії (зберігає thought_signature автоматично)
                contents.append(candidate.content)
                
                # Додаємо відповідь інструменту до історії
                contents.append({
                    "role": "user", # У raw API function_response додається як "user"
                    "parts": [{
                        "function_response": {
                            "name": tool_name,
                            "response": {"result": result} # Gemini вимагає dict
                        }
                    }]
                })
            else:
                # Якщо виклику функції немає, це фінальна текстова відповідь
                final_response = candidate.content.parts[0].text
                break
                
        log_trace("agent_finish", {
            "response": final_response,
            "status": self.guardrails.get_status()
        })
        return final_response