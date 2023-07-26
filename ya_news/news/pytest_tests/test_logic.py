from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_id, form_data):
    """Проверить, что неавторизованный пользователь не создаст комментарий."""
    url = reverse('news:detail', args=news_id)
    response = client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


def test_user_can_create_comment(
        author_client,
        form_data,
        news_id,
        news,
        author
):
    """Проверить создание комментария авторизованным пользователем."""
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, news_id, bad_word):
    """Проверить работу фильтра запрещенных слов в тексте комментария."""
    url = reverse('news:detail', args=news_id)
    comments_count = Comment.objects.count()
    bad_words = {'text': f'Какой-то текст, {bad_word}, еще текст.'}
    response = author_client.post(url, data=bad_words)
    assert comments_count == 0
    assertFormError(response, form='form', field='text', errors=WARNING)


def test_author_can_edit_comment(
        author_client,
        form_data,
        comment_id,
        news_id,
        comment
):
    """Проверит, что автор может редактировать свои комментарии."""
    url = reverse('news:edit', args=comment_id)
    response = author_client.post(url, data=form_data)
    news_detail_url = reverse('news:detail', args=news_id)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(
        author_client,
        comment_id,
        news_id,
):
    """Проверить, что автор может удалить свой комментарий."""
    url = reverse('news:delete', args=comment_id)
    response = author_client.post(url)
    news_detail_url = reverse('news:detail', args=news_id)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_reader_cant_edit_comment_of_another_user(
        reader_client,
        form_data,
        comment_id,
        comment
):
    """Проверить, что пользователи не могут редактировать чужие комментарии"""
    comment_text = comment.text
    url = reverse('news:edit', args=comment_id)
    response = reader_client.post(url, data=form_data)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    expected_count = 1
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == expected_count
    assert comment.text == comment_text


def test_user_cant_delete_comment_of_another_user(
        reader_client,
        comment_id
):
    """Проверить, что пользователи не могут удалять чужие комментарии."""
    url = reverse('news:delete', args=comment_id)
    response = reader_client.post(url)
    comments_count = Comment.objects.count()
    assert comments_count == 1
    assert response.status_code == HTTPStatus.NOT_FOUND
