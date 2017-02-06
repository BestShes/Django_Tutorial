from django.test import TestCase
from .models import Question
from django.utils import timezone
from django.urls import reverse
import datetime

# Create your tests here.

class QuestionMethodTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        pub_date가 미래면 was_published_recently()는 false를 반환해야 됩니다
        :return:
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        pub_date가 24시간보다 이전이면 was_published_recently()는 False를 반환해야 한다
        :return:
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        pub_date가 지난 24시간 이내라면 was_published_recently()는 True를 반환해야한다
        :return:
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    주어진 'question_text'와 'days'로 설문을 작성 'days'는 지금부터 발행일까지 날짜의 수
    (음수면 과거에 발행한 설문 양수면 아직 발행하지 않은 설문)
    :param question_text:
    :param days: 지금부터 발행일까지의 날짜수
    :return:
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionViewTests(TestCase):
    def test_index_view_with_no_question(self):
        """
        설문이 없을 경우에 적절한 메세지가 출력되어야 한다
        :return:
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        pub_date가 과거인 설문은 목록페이지에 표시되어야한다
        :return:
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question:Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        pub_date가 미래인 설문은 목록페이지에 표시되지 않아야 한다
        :return:
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_index_view_with_future_question_and_past_question(self):
        """
        발행일이 과거인 설문과 미래인 설문이 모두 있더라도 과거인 설문만 표시되어야 합니다
        :return:
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.']
        )

    def test_index_view_with_two_past_questions(self):
        """
        설문 목록 페이지는 여러 설문을 표시 할 수 있다
        :return:
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuesetionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        pub_date가 미래이면 DetailView는 404 Not Found를 반환해야한다
        :return:
        """
        future_question = create_question(question_text='Ruture question.', days=5)
        url = reverse('polls:index', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        pub_date가 과거이면 설문내용을 표시해야한다
        :return:
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:index', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_texy)