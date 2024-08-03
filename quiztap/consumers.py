import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Competition, Question, Choice, UserCompetition, UserAnswer

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.competition_id = self.scope['url_route']['kwargs']['competition_id']
        self.competition_group_name = f'quiz_{self.competition_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.competition_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.competition_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        
        if message_type == 'answer':
            question_id = data['question_id']
            selected_choice_id = data['selected_choice_id']
            await self.save_answer(question_id, selected_choice_id)

        # Send message to room group
        await self.channel_layer.group_send(
            self.competition_group_name,
            {
                'type': 'quiz_message',
                'message': data
            }
        )

    async def quiz_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def save_answer(self, question_id, selected_choice_id):
        user = self.scope["user"]
        question = Question.objects.get(pk=question_id)
        selected_choice = Choice.objects.get(pk=selected_choice_id)
        user_competition = UserCompetition.objects.get(user_profile=user, competition_id=self.competition_id)

        UserAnswer.objects.create(
            user_competition=user_competition,
            question=question,
            selected_choice=selected_choice
        )
