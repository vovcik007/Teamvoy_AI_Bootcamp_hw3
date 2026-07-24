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
            "1. ALWAYS use 'search_companies' or 'search_contacts' BEFORE creating new records to prevent duplicates (idempotency).\n"
            "2. Always use the provided tools to interact with the CRM. Never hallucinate IDs.\n"
            "3. If a tool returns a 'validation_error' or '400 Bad Request', carefully read the 'detail', fix the arguments, and retry.\n"
            "4. Chain dependencies correctly: you MUST have a company_id before creating a contact, and a company_id/contact_id before creating a deal.\n"
            "5. When the task is fully completed, provide a concise, structured summary of what was created (with IDs).\n\n"
            
            "SUPPORTED OPERATIONS:\n"
            "- CREATE: You can create companies, contacts, deals, and activities.\n"
            "- READ: You can search and retrieve any entity using REST or GraphQL.\n"
            "- UPDATE/DELETE: You can ONLY update and delete DEALS. Other entities (companies, contacts, activities) cannot be modified or deleted.\n"
            "- If a user asks to update/delete a company, contact, or activity, politely explain that this operation is not currently supported and suggest alternatives (e.g., creating a new record instead).\n\n"
            
            "API SELECTION STRATEGY:\n"
            "- Use REST tools (create_company, create_contact, create_deal, create_activity) for WRITE operations.\n"
            "- Use 'execute_graphql' for COMPLEX READ operations with nested relations. Examples:\n"
            "  * Get a company with all its deals and activities in one query\n"
            "  * Get all deals for a specific contact with their activities\n"
            "- For simple reads (e.g., 'search_companies'), prefer REST tools.\n\n"
            
            "GRAPHQL EXAMPLE:\n"
            "query {\n"
            "  company(id: \"<id>\") {\n"
            "    name\n"
            "    deals {\n"
            "      title\n"
            "      amount\n"
            "      contact { name email }\n"
            "      activities { type note }\n"
            "    }\n"
            "  }\n"
            "}\n"
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