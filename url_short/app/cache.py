import redis

redis_client = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

def get_link(short_code):
    return redis_client.get(f"link:{short_code}")

def set_link(short_code, url):
    redis_client.setex(f"link:{short_code}", 3600, url)

def delete_link(short_code):
    redis_client.delete(f"link:{short_code}")