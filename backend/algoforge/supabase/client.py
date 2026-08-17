from supabase import create_client, Client
from algoforge.config import settings

def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def get_user_client(access_token: str) -> Client:
    if access_token and access_token != "dev_mock_token" and len(access_token.split(".")) == 3:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        client.postgrest.auth(access_token)
        return client
    return get_supabase_client()
