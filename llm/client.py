from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config.settings import settings
import httpx


openai_api_key = settings.openai_api_key
if not openai_api_key:
    raise ValueError("OpenAI API Key is not set. Please add it to the .env file.")


def create_openai_llm(temperature=0.7, model="gpt-4o"):
    """Creates an OpenAI Chat Model with custom parameters."""

    def update_base_url(request: httpx.Request) -> None:
        """Dynamically updates API endpoint based on model type."""
        model_map = {
            "gpt-4o": "/v1/openai/deployments/gpt-4o-2024-11-20/chat/completions",
            "gpt-o1-mini": "/v1/openai/deployments/o1-mini-2024-09-12/chat/completions",
            "gpt-o1": "/v1/openai/deployments/o1-2024-12-17/chat/completions"
        }

        if model not in model_map:
            raise ValueError(f"Unsupported model '{model}'. Available models: {list(model_map.keys())}")

        request.url = request.url.copy_with(path=model_map[model])

    # Modify API endpoint
    http_client = httpx.Client(event_hooks={"request": [update_base_url]})

    if model=="gpt-4o":
        return ChatOpenAI(
            base_url="https://aalto-openai-apigw.azure-api.net",
            api_key=openai_api_key,
            default_headers={"Ocp-Apim-Subscription-Key": openai_api_key},
            http_client=http_client,
            temperature=temperature
        )
    else:
        return ChatOpenAI(
            base_url="https://aalto-openai-apigw.azure-api.net",
            api_key=openai_api_key,
            default_headers={"Ocp-Apim-Subscription-Key": openai_api_key},
            http_client=http_client
        )

# Single HTTP client for embeddings
_http_client_embeddings = httpx.Client()

def create_openai_embeddings():
    """Creates an OpenAI Embeddings model."""
    return OpenAIEmbeddings(
        base_url="https://aalto-openai-apigw.azure-api.net/v1/openai/ada-002/embeddings",
        api_key=openai_api_key,
        default_headers={"Ocp-Apim-Subscription-Key": openai_api_key},
        http_client=_http_client_embeddings  # Reuse a single HTTP client
    )

llm = create_openai_llm(model="gpt-4o")
