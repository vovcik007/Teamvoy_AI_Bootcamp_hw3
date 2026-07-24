import httpx
import uuid
from typing import Any, Dict

TOOL_DEFINITIONS = [
    {
        "name": "search_companies",
        "description": "Search for existing real estate companies/brokerages by name.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search string for company name"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_company",
        "description": "Create a new real estate brokerage/agency.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING", "description": "Name of the company"},
                "domain": {"type": "STRING", "description": "Website domain (optional)"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "create_contact",
        "description": "Create a new lead (buyer or seller) and link to a company.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING", "description": "Full name of the contact"},
                "email": {"type": "STRING", "description": "Email address"},
                "phone": {"type": "STRING", "description": "Phone number"},
                "role": {"type": "STRING", "enum": ["BUYER", "SELLER", "BOTH"], "description": "Role of the contact"},
                "company_id": {"type": "STRING", "description": "UUID of the company"}
            },
            "required": ["name", "company_id"]
        }
    },
    {
        "name": "create_deal",
        "description": "Create a new property transaction/deal.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Property address or deal title"},
                "amount": {"type": "NUMBER", "description": "Property price"},
                "company_id": {"type": "STRING", "description": "UUID of the company"},
                "contact_id": {"type": "STRING", "description": "UUID of the lead (optional)"}
            },
            "required": ["title", "company_id"]
        }
    },
    {
        "name": "update_deal",
        "description": "Update an existing deal's information. Use this to change deal stage (e.g., move from LEAD to VIEWING), update amount, or modify title. Only provide fields you want to change (partial update).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "id": {"type": "STRING", "description": "UUID of the deal to update"},
                "title": {"type": "STRING", "description": "New property address or deal title (optional)"},
                "stage": {"type": "STRING", "enum": ["LEAD", "VIEWING", "OFFER", "NEGOTIATION", "CLOSED_WON", "CLOSED_LOST"], "description": "New deal stage (optional)"},
                "amount": {"type": "NUMBER", "description": "New property price (optional)"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "delete_deal",
        "description": "Permanently delete a deal and all its associated activities. WARNING: This action cannot be undone.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "id": {"type": "STRING", "description": "UUID of the deal to delete"}
            },
            "required": ["id"]
        }
    },
    {
        "name": "create_activity",
        "description": "Log an interaction (call, showing, etc.) for a specific deal.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "type": {"type": "STRING", "enum": ["CALL", "EMAIL", "SHOWING", "OFFER", "MEETING", "OTHER"]},
                "note": {"type": "STRING", "description": "Details of the interaction"},
                "deal_id": {"type": "STRING", "description": "UUID of the deal"}
            },
            "required": ["type", "deal_id"]
        }
    },
    # ✅ НОВИЙ ІНСТРУМЕНТ для GraphQL
    {
        "name": "execute_graphql",
        "description": "Execute a GraphQL query or mutation against the CRM. Use this for complex read operations with nested relations (e.g., get company with all its deals and activities in one query). For simple write operations, prefer REST tools (create_company, create_deal, etc.).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "GraphQL query or mutation string"
                },
                "variables": {
                    "type": "OBJECT",
                    "description": "Variables for the GraphQL query (optional)"
                }
            },
            "required": ["query"]
        }
    }
]

class ToolExecutor:
    def __init__(self, mode: str, api_url: str = "", token: str = ""):
        self.mode = mode
        self.api_url = api_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}
        self.mock_db = {"companies": [], "contacts": [], "deals": [], "activities": []}
        self.mock_counter = 1

    def _mock_id(self) -> str:
        self.mock_counter += 1
        return str(uuid.uuid4())

    def execute(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if self.mode == "mock":
                result = self._execute_mock(name, args)
            else:
                result = self._execute_api(name, args)
            
            if isinstance(result, list):
                return {"items": result}
            elif isinstance(result, str):
                return {"message": result}
            return result
            
        except Exception as e:
            return {"error": str(e), "detail": "Tool execution failed"}

    def _execute_mock(self, name: str, args: Dict[str, Any]) -> Any:
        # ✅ Mock для GraphQL — повертаємо всі дані
        if name == "execute_graphql":
            return {
                "data": {
                    "companies": self.mock_db["companies"],
                    "contacts": self.mock_db["contacts"],
                    "deals": self.mock_db["deals"],
                    "activities": self.mock_db["activities"]
                }
            }
        
        if name == "search_companies":
            return [c for c in self.mock_db["companies"] if args["query"].lower() in c["name"].lower()]
        
        record = {"id": self._mock_id(), **args}
        if name == "create_company": self.mock_db["companies"].append(record)
        elif name == "create_contact": self.mock_db["contacts"].append(record)
        elif name == "create_deal": self.mock_db["deals"].append(record)
        elif name == "create_activity": self.mock_db["activities"].append(record)
        return record

    def _execute_api(self, name: str, args: Dict[str, Any]) -> Any:
        # ✅ НОВИЙ GraphQL endpoint
        if name == "execute_graphql":
            url = f"{self.api_url}/graphql"
            payload = {
                "query": args["query"],
                "variables": args.get("variables", {})
            }
            r = httpx.post(url, json=payload, headers=self.headers, timeout=10.0)
            r.raise_for_status()
            return r.json()
        
        # REST endpoints
        endpoints = {
            "search_companies": ("GET", f"/companies?search={args.get('query', '')}"),
            "create_company": ("POST", "/companies"),
            "create_contact": ("POST", "/contacts"),
            "create_deal": ("POST", "/deals"),
            "create_activity": ("POST", "/activities"),
        }
        
        if name not in endpoints:
            raise ValueError(f"Unknown tool: {name}")
            
        method, path = endpoints[name]
        url = f"{self.api_url}{path}"
        
        if method == "GET":
            r = httpx.get(url, headers=self.headers, timeout=5.0)
        else:
            r = httpx.post(url, json=args, headers=self.headers, timeout=5.0)
            
        r.raise_for_status()
        return r.json()