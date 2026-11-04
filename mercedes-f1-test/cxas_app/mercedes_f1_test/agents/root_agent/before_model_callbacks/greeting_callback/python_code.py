"""Before-model callback for session start & deterministic greeting."""
from typing import Optional

def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    """CES before_model_callback entrypoint."""
    try:
        user_input = callback_context.get_last_user_input() if hasattr(callback_context, "get_last_user_input") else []
        for part in user_input:
            text = getattr(part, "text", "")
            if "<event>welcome</event>" in text or "<event>session start</event>" in text:
                return None
        return None
    except Exception:
        return None
