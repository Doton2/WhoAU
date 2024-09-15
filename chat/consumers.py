import json
from django.core.cache import cache
from channels.generic.websocket import AsyncWebsocketConsumer

waiting_users =[]

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        #websocket 연결
        await self.accept()

        if waiting_users: 
            # waiting_user에 있는 user가져오기 
            self.partner_user = waiting_users.pop(0)

            self.group_name = f"{self.partner_user[-10:]}"

            self.user_id = 2
            self.partner_id = 1
            
            #같은 group_name으로 연결
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add(self.group_name, self.partner_user)

            await self.send(text_data=json.dumps({
                "message": "대화 상대가 연결 됐습니다.",
                "user_id": self.user_id,
                "send_user_id":0}))
            await self.channel_layer.send(self.partner_user, {"type": "chat.message", 
            "message": '대화 상대가 연결 됐습니다', 
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
                "user_id": self.user_id,"send_user_id":0}))


    async def disconnect(self, close_code):
            if self.group_name in waiting_users:
                waiting_users.remove(self.group_name)
            
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
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sendUserId = text_data_json["sendUserId"]

        cache_key = f'{self.group_name}_{self.user_id} '
        # 중복요청과 도배성 message 방지
        if cache.get(cache_key):
            return await self.send(text_data=json.dumps({
                "message": "도배성 글 작성은 안됩니다.",
                "user_id": self.user_id,
                "send_user_id":0}))
        
        cache.set(cache_key, self.user_id, timeout=1)

        #공백 message 처리
        if not message.replace(' ',''):
            return await self.send(text_data=json.dumps({
                "message": "메시지를 입력해 주세요.",
                "user_id": self.user_id,
                "send_user_id":0}))

        #정상 message 처리
        await self.channel_layer.group_send(
            self.group_name, {"type": "chat.message", 
            "message": [message],
            "user_id": self.user_id, 
            "send_user_id":sendUserId}
        )


    async def chat_message(self, event):
        message = event["message"]
        sendUserId = event["send_user_id"]
        await self.send(text_data=json.dumps({
            "message": [message], 
            "user_id":self.user_id,
            "send_user_id":sendUserId}))


    # 화면 refresh 버튼 활성화 
    async def refresh_page(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"refresh": True, "message": [message], "send_user_id":0}))
    

