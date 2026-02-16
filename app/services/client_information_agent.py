import os
import json
import uuid
import re
from datetime import datetime
from openai import AzureOpenAI
from utils.cosmo_db import get_database, CosmosContainer
from utils.validators import valid_email, valid_mobile
from prompts.system_prompt import SYSTEM_PROMPT
from prompts.developer_prompt import DEVELOPER_PROMPT
from prompts.intent_prompt import INTENT_EXTRACTION_PROMPT

# Azure OpenAI Client
client_ai = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Cosmos DB Clients
bia_db = get_database("bia_db")
mock_bpi_db = get_database("mock-bank-db-bpi")
mock_gcash_db = get_database("mock-bank-db-gcash")

clients_container = CosmosContainer(bia_db.get_container_client("clients"))
bpi_accounts = CosmosContainer(mock_bpi_db.get_container_client("accounts"))
gcash_accounts = CosmosContainer(mock_gcash_db.get_container_client("accounts"))

class ClientInformationAgent:

    def _extract_intent(self, message: str):
        completion = client_ai.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": DEVELOPER_PROMPT},
                {"role": "user", "content": INTENT_EXTRACTION_PROMPT + "\n" + message}
            ],
            temperature=0
        )
        return json.loads(completion.choices[0].message.content)

    async def handle_message(self, message: str):
        intent_obj = self._extract_intent(message)
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
        client = await clients_container.find_one(query)
        if not client:
            return {"status": "error", "message": "Client not found"}
        
        # Fetch linked accounts from all banks
        accounts = []
        for bank in [bpi_accounts, gcash_accounts]:
            bank_accounts = await bank.find_all({"userId": client["userId"]})
            accounts.extend(bank_accounts)
        
        client["accounts"] = accounts
        return {"status": "success", "client": client}

    async def update_client(self, f):
        query = {"email": f.get("email")} if f.get("email") else {"userId": f.get("userId")}
        client = await clients_container.find_one(query)
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

        await clients_container.update_one(query, update_fields)
        return {"status": "success", "updated_fields": update_fields}
