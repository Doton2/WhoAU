import time
import json
import redis
from config.celery import app
from django.core.cache import cache
from decouple import config

rd = redis.StrictRedis(host = config("REDIS_ADDRESS"),port= config("REDIS_PORT"),password=config("REDIS_PASSWORD"), db=0)

@app.task()
def task_group_delete():
    #redis에 있는 group_status값 가져오기
    group_status = cache.get("group_status")
    keys_to_delete = []
    # group_status가 빈값이 아닌 경우에만 실행
    if group_status:
        group_status = json.loads(group_status)
        for key, value in group_status.items():
            #10분간 비활성화 상태이면 group에서 삭제 
            if int(time.time()) - value > 600:
                rd.delete(f"asgi:group:{key}")
                keys_to_delete.append(key)
                
        #group_status dit안에 있는 값 삭제
        for key in keys_to_delete:
            del group_status[key] 
        
        #redis에 group_status 업데이트 
        cache.set(key="group_status",value=json.dumps(group_status))
        return "tesk_group_delet"