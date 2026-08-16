from fastapi import Depends
from algoforge.api.middleware.auth import get_current_user
from algoforge.supabase.client import get_user_client, Client

def get_supabase(user: dict = Depends(get_current_user)) -> Client:
    return get_user_client(user["token"])
