from app.llm.langchain_client import get_chat_model

def test_chat_model_creation():

    model = get_chat_model()

    assert model is not None
    assert model.model_name