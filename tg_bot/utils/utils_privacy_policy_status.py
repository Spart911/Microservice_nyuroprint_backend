import aiohttp
from config import API_USER

# Функция для проверки статуса согласия
async def check_privacy_policy_status(user_id: int) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_USER}/get-privacy-policy-status/{str(user_id)}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("privacy_policy_accepted", False):
                    return 1  # privacy_policy_accepted == true
                else:
                    return 0  # privacy_policy_accepted == false
            elif response.status == 404:
                return 2  # response.status == 404
            return 0  # Default to 0 if response status is something else



# Функция для обновления статуса согласия
async def update_privacy_policy_status(user_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.put(f"{API_USER}/update-privacy-policy-status/{str(user_id)}") as response:
            return response.status == 200
