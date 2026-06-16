import traceback

from whatsapp_confirmations import generate_confirmation_token, confirmation_token_is_valid

secret = "test-secret"
escala_id = "e1"

try:
    token = generate_confirmation_token(escala_id, secret)
    assert token, "Token should not be empty"
    assert confirmation_token_is_valid(token, escala_id, secret), "Token should validate"
    print("ok", token)
except Exception:
    traceback.print_exc()
