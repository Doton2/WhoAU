import json

from channels.generic.websocket import AsyncWebsocketConsumer

waiting_users =[]

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        
        #websocket 연결
        await self.accept()

        if waiting_users: 
            # waiting_user에 있는 user가져오기 
            partner_user = waiting_users.pop(0)

            self.group_name = f"{partner_user[-10:]}"
            
            #같은 group_name으로 연결
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.channel_layer.group_add(self.group_name, partner_user)

            await self.send(text_data=json.dumps({"message": ['대화 상대와 연결됐습니다.']}))
            await self.channel_layer.send(partner_user, {"type": "chat.message", "message": '대화 상대와 연결됐습니다.'})
            
        else:
            #waiting_user가 없으면 waiting에 추가 
            waiting_users.append(self.channel_name)

            self.group_name = self.channel_name[-10:]
            await self.send(text_data=json.dumps({"message": "대화 상대를 기다리고 있습니다."}))


    async def disconnect(self, close_code):
            # 연결 종료시 group_name 삭제
            if self.group_name in waiting_users:
                waiting_users.remove(self.group_name)

            await self.send(text_data=json.dumps({"message": "대화 상대가 나갔습니다."}))
            await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.group_name, {"type": "chat.message", "message": [message]}
        )


    async def chat_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": [message]}))