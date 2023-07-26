from datetime import date

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news_count(client, news_list):
    """Проверить ограничение количества новостей на странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = list(response.context['object_list'])
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news(client):
    """Проверить сортироовку новостей от новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = list(response.context['object_list'])
    assert isinstance(object_list[0].date, date)
    assert object_list == sorted(
        object_list,
        key=lambda x: x.date,
        reverse=True,
    )


@pytest.mark.django_db
@pytest.mark.usefixtures('comment_list')
def test_comments(client, news_id):
    """Проверить сортировку комментариев по времени создания."""
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    news = response.context['news']
    comments_list = list(news.comment_set.all())
    assert isinstance(comments_list[0].created, timezone.datetime)
    assert comments_list == sorted(
        comments_list,
        key=lambda x: x.created,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, value',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_form(user, value, news_id):
    """Проверить доступность формы для отправки комментария."""
    url = reverse('news:detail', args=news_id)
    response = user.get(url)
    assert ('form' in response.context) == value
