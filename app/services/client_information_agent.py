import os
import json
import logging
try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None
from app.utils.cosmo_db import get_database, CosmosContainer
from app.utils.validators import valid_email, valid_mobile
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.prompts.developer_prompt import DEVELOPER_PROMPT
from app.prompts.intent_prompt import INTENT_EXTRACTION_PROMPT

class ClientInformationAgent:
    def __init__(self):
        self.client_ai = None
        self.clients_container = None
        self.bpi_accounts = None
        self.gcash_accounts = None
        self._init_error = None
        self._initialize()

    def _initialize(self):
        if AzureOpenAI is None:
            self._init_error = "Missing dependency: 'openai'."
            return

        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        missing = []
        if not api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        if not api_version:
            missing.append("AZURE_OPENAI_API_VERSION")
        if not endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not deployment:
            missing.append("AZURE_OPENAI_DEPLOYMENT")

        if missing:
            self._init_error = f"Missing environment variables: {', '.join(missing)}"
            return

        try:
            self.client_ai = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint,
            )

            bia_db = get_database("bia_db")
            mock_bpi_db = get_database("mock-bank-db-bpi")
            mock_gcash_db = get_database("mock-bank-db-gcash")

            self.clients_container = CosmosContainer(
                bia_db.get_container_client("clients")
            )
            self.bpi_accounts = CosmosContainer(
                mock_bpi_db.get_container_client("accounts")
            )
            self.gcash_accounts = CosmosContainer(
                mock_gcash_db.get_container_client("accounts")
            )
        except Exception as e:
            logging.exception("Failed to initialize ClientInformationAgent")
            self._init_error = str(e)

    def _not_ready_response(self):
        if self._init_error:
            return {
                "status": "error",
                "message": f"Client information agent is not configured: {self._init_error}",
            }
        return None

    def _extract_intent(self, message: str):
        completion = self.client_ai.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": DEVELOPER_PROMPT},
                {"role": "user", "content": INTENT_EXTRACTION_PROMPT + "\n" + message}
            ],
            temperature=0
        )
        content = completion.choices[0].message.content
        return json.loads(content)

    async def handle_message(self, message: str):
        not_ready = self._not_ready_response()
        if not_ready:
            return not_ready

        try:
            intent_obj = self._extract_intent(message)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Could not parse agent response as JSON"}
        except Exception:
            logging.exception("Intent extraction failed")
            return {"status": "error", "message": "Intent extraction failed"}

        intent = intent_obj.get("intent")
        f = intent_obj.get("extracted_fields", {})
        missing = intent_obj.get("missing_fields", [])

        if missing:
            return {"status": "clarify", "missing_fields": missing}

        if intent == "get_client":
            return await self.get_client(f)

        if intent == "update_client":
            return await self.update_client(f)

        return {"status": "clarify", "message": "Need more details"}

    async def get_client(self, f):
        query = {"email": f.get("email")} if f.get("email") else {"userId": f.get("userId")}
        client = await self.clients_container.find_one(query)
        if not client:
            return {"status": "error", "message": "Client not found"}
        
        # Fetch linked accounts from all banks
        accounts = []
        for bank in [self.bpi_accounts, self.gcash_accounts]:
            bank_accounts = await bank.find_all({"userId": client["userId"]})
            accounts.extend(bank_accounts)
        
        client["accounts"] = accounts
        return {"status": "success", "client": client}

    async def update_client(self, f):
        query = {"email": f.get("email")} if f.get("email") else {"userId": f.get("userId")}
        client = await self.clients_container.find_one(query)
        if not client:
            return {"status": "error", "message": "Client not found"}

        update_fields = {}
        for field in ["fullName", "email", "mobile"]:
            if f.get(field):
                if field == "email" and not valid_email(f[field]):
                    return {"status": "error", "message": "Invalid email"}
                if field == "mobile" and not valid_mobile(f[field]):
                    return {"status": "error", "message": "Invalid mobile"}
                update_fields[field] = f[field]

        if not update_fields:
            return {"status": "clarify", "missing_fields": ["fields_to_update"]}

        await self.clients_container.update_one(query, update_fields)
        return {"status": "success", "updated_fields": update_fields}
