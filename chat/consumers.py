import json
import time
from django.core.cache import cache
from channels.generic.websocket import AsyncWebsocketConsumer
waiting_users =[]

#redls에 값을 저장해서 관리
group_status = cache.get('group_status', default=json.dumps({}))
group_status = json.loads(group_status)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #websocket 연결
        await self.accept()

        if waiting_users: 
            # waiting_user에 있는 channel_name가져오기 
            self.partner_user = waiting_users.pop(0)

            self.group_name = self.partner_user[-10:]
            self.user_id = 2
            self.partner_id = 1

            #group 생성시간 저장
            group_status[self.group_name] = int(time.time())
            cache.set(key='group_status',value=json.dumps(group_status))

            #같은 group_name으로 연결
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add(self.group_name, self.partner_user)

            await self.send(text_data=json.dumps({
                "message": "대화 상대가 연결 됐습니다.",
                "user_id": self.user_id,
                "submitButton": False,
                "send_user_id":0}))
            await self.channel_layer.send(self.partner_user, {"type": "chat.message", 
            "message": '대화 상대가 연결 됐습니다', 
            "submitButton": False,
            "user_id": self.user_id, 
            "send_user_id":0})
            
        else:
            #waiting_user가 없으면 waiting에 추가 
            waiting_users.append(self.channel_name)
            
            self.user_id = 1
            self.partner_id = 2
            self.group_name = self.channel_name[-10:]
            await self.send(text_data=json.dumps({
                "message": "대화 상대를 기다리고 있습니다.",
                "submitButton": True,
                "user_id": self.user_id,
                "send_user_id":0}))


    async def disconnect(self, close_code):
            # 같은 이름이의 waiting_user 가있으면 제거
            if self.channel_name in waiting_users:
                waiting_users.remove(self.channel_name)

            await self.channel_layer.group_send(
            self.group_name,
                {
                "type": "refresh.page",
                "message": "상대방과 연결이 끊어졌습니다.",
                "send_user_id":0
                })
            
            # 그룹에서 제거
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    
    async def receive(self, text_data):
        # 아직 대기중인 user일 경우 메시지 못보내게 방지
        if self.channel_name in waiting_users:
            return await self.send(text_data=json.dumps({
                "message": "대화 상대를 기다리고 있습니다.",
                "submitButton": True,
                "user_id": self.user_id,
                "send_user_id":0}))
        
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sendUserId = text_data_json["sendUserId"]

        cache_key = f'{self.group_name}_{self.user_id} '
        # 중복요청과 도배성 message 방지
        if cache.get(cache_key):
            return await self.send(text_data=json.dumps({
                "message": "도배성 글 작성은 안됩니다.",
                "user_id": self.user_id,
                "submitButton": False,
                "send_user_id":0}))
        
        cache.set(cache_key, self.user_id, timeout=1)

        #1분 간격으로 group의 상태를 redis에 업데이트
        if int(time.time())-group_status[self.group_name] > 60:
            group_status[self.group_name] = int(time.time())
            cache.set(key='group_status',value=json.dumps(group_status))

        #공백 message 처리
        if not message.replace(' ',''):
            return await self.send(text_data=json.dumps({
                "message": "메시지를 입력해 주세요.",
                "submitButton": False,
                "user_id": self.user_id,
                "send_user_id":0}))
        
        #메시지 50자 이하만 입력가능 
        if len(message) > 50:
            return await self.send(text_data=json.dumps({
                "message": "50자 까지 입력 가능합니다.",
                "submitButton": False,
                "user_id": self.user_id,
                "send_user_id":0}))

        #정상 message 처리
        await self.channel_layer.group_send(
            self.group_name, {"type": "chat.message", 
            "message": [message],
            "submitButton": False,
            "user_id": self.user_id, 
            "send_user_id":sendUserId}
        )


    async def chat_message(self, event):
        message = event["message"]
        sendUserId = event["send_user_id"]
        await self.send(text_data=json.dumps({
            "message": [message],
            "submitButton": False,
            "user_id":self.user_id,
            "send_user_id":sendUserId}))


    # 화면 refresh 버튼 활성화 
    async def refresh_page(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"refresh": True,"submitButton": True, "message": [message], "send_user_id":0}))
    

