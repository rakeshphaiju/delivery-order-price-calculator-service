import aiohttp
from service.common.logger import logger


class RestClient:
    async def get(self, url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error occurred while fetching {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
        return None
