INTENT_EXTRACTION_PROMPT = """
Convert the conversation into JSON structure exactly.
Infer likely bankCode from bankName words if possible.
Valid bankCode values are only BPI or GCASH.
If user mentions any other bank, set missing_fields to include "bankCode".
"""
