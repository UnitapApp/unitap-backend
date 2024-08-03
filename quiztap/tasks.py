# import logging
# from datetime import timedelta
# from decimal import Decimal

# from celery import shared_task
# from django.core.cache import cache
# from django.utils import timezone

# from core.utils import memcache_lock
# from quiztap.constants import (
#     ANSWER_TIME_SECOND,
#     REGISTER_COMPETITION_TASK_PERIOD_SECONDS,
#     REST_BETWEEN_EACH_QUESTION_SECOND,
# )
# from quiztap.models import Competition, Question, UserCompetition


# @shared_task()
# def setup_competition_to_start(competition_pk):
#     try:
#         competition = Competition.objects.get(
#             pk=competition_pk, status=Competition.Status.NOT_STARTED
#         )
#     except Competition.DoesNotExist:
#         logging.warning(f"Competition with pk {competition_pk} not exists.")
#         return

#     question = competition.questions.order_by("number").first()
#     competition.status = competition.Status.IN_PROGRESS
#     question.can_be_shown = True
#     competition.save(update_fields=("status",))
#     question.save(update_fields=("can_be_shown",))
#     user_competition_count = competition.participants.count()
#     cache.set(
#         f"comp_{competition_pk}_total_participants_count", user_competition_count, 360
#     )
#     process_competition_answers.apply_async(
#         (competition_pk, question.pk),
#         eta=competition.start_at + timedelta(seconds=ANSWER_TIME_SECOND),
#     )


# @shared_task()
# def process_competition_questions(competition_pk, ques_pk):
#     try:
#         competition = Competition.objects.get(
#             pk=competition_pk, status=Competition.Status.IN_PROGRESS
#         )
#         question = Question.objects.get(pk=ques_pk)
#     except Competition.DoesNotExist:
#         logging.warning(f"Competition with pk {competition_pk} not exists.")
#         return
#     except Question.DoesNotExist:
#         logging.warning(f"Question with pk {ques_pk} not exists.")
#         return
#     question.can_be_shown = True
#     question.save(update_fields=("can_be_shown",))
#     process_competition_answers.apply_async(
#         (competition_pk, ques_pk),
#         eta=competition.start_at
#         + timedelta(
#             seconds=(
#                 (question.number * ANSWER_TIME_SECOND)
#                 + (question.number - 1) * REST_BETWEEN_EACH_QUESTION_SECOND
#             )
#         ),
#     )


# @shared_task()
# def process_competition_answers(competition_pk, ques_pk):
#     try:
#         competition = Competition.objects.get(
#             pk=competition_pk, status=Competition.Status.IN_PROGRESS
#         )
#         current_question = Question.objects.prefetch_related("users_answer").get(
#             pk=ques_pk
#         )
#     except Competition.DoesNotExist:
#         logging.warning(f"Competition with pk {competition_pk} not exists.")
#         return
#     except Question.DoesNotExist:
#         logging.warning(f"Question with pk {ques_pk} not exists.")
#         return

#     current_question.answer_can_be_shown = True
#     current_question.save(update_fields=("answer_can_be_shown",))
#     next_question = (
#         competition.questions.filter(number__gt=current_question.number)
#         .order_by("number")
#         .first()
#     )
#     users_answered_correct = current_question.users_answer.filter(
#         selected_choice__is_correct=True
#     ).values_list("user_competition__pk", flat=True)

#     if next_question is None:
#         try:
#             amount_won = Decimal(competition.prize_amount / len(users_answered_correct))
#         except ZeroDivisionError:
#             logging.warning("no correct answer be found")
#         else:
#             UserCompetition.objects.filter(pk__in=users_answered_correct).update(
#                 is_winner=True, amount_won=amount_won
#             )
#             competition.amount_won = amount_won

#         competition.winner_count = len(users_answered_correct)
#         competition.status = competition.Status.FINISHED
#         competition.save(update_fields=("status", "amount_won", "winner_count"))
#         cache.delete(f"comp_{competition_pk}_eligible_users_count")
#         cache.delete(f"comp_{competition_pk}_eligible_users")
#         cache.delete(f"comp_{competition_pk}_total_participants_count")
#         return
#     user_competition_count = competition.participants.count()
#     cache.set(
#         f"comp_{competition_pk}_total_participants_count", user_competition_count, 360
#     )
#     cache.set(
#         f"comp_{competition_pk}_eligible_users_count", len(users_answered_correct), 360
#     )
#     cache.set(f"comp_{competition_pk}_eligible_users", set(users_answered_correct), 360)
#     process_competition_questions.apply_async(
#         (competition_pk, next_question.pk),
#         eta=competition.start_at
#         + timedelta(
#             seconds=(
#                 ((next_question.number - 1) * ANSWER_TIME_SECOND)
#                 + (next_question.number - 1) * REST_BETWEEN_EACH_QUESTION_SECOND
#             )
#         ),
#     )


# @shared_task(bind=True)
# def register_competition_to_start(self):
#     now = timezone.now()
#     id_ = f"{self.name}-LOCK"

#     with memcache_lock(id_, self.app.oid) as acquired:
#         if not acquired:
#             logging.warning(f"Could not acquire process lock at {self.name}")
#             return
#         threshold = now + timedelta(seconds=REGISTER_COMPETITION_TASK_PERIOD_SECONDS)

#         competitions = Competition.objects.filter(
#             start_at__lt=threshold,
#             is_active=True,
#             status=Competition.Status.NOT_STARTED,
#         )

#         for competition in competitions:
#             setup_competition_to_start.apply_async(
#                 (competition.pk,),
#                 eta=competition.start_at - timedelta(milliseconds=0.5),
#             )
