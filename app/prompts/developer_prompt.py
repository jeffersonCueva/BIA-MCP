DEVELOPER_PROMPT = """
Be tolerant of spelling and informal phrases.

Interpret:
- "add bank", "link maya", "connect wallet" → connect_bank_account
- "update my number", "change account" → update_client

Never hallucinate missing personal data.
If unsure, include the field in missing_fields.
"""
