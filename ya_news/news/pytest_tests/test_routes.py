from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'address, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_id'))
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, address, args):
    """Проверить доступ страниц для неавторизованного пользователя."""
    url = reverse(address, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'address, args',
    (('news:edit', pytest.lazy_fixture('comment_id')),
     ('news:delete', pytest.lazy_fixture('comment_id')),),
)
def test_availability_for_comment_edit_and_delete(
    author_client,
    address,
    args
):
    """Проверка доступности страниц удаления и редактировоания для автора."""
    url = reverse(address, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'address',
    ('news:edit', 'news:delete'),
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, address, comment_id):
    """Проверить перенаправление для неавторизованного пользователя."""
    login_url = reverse('users:login')
    url = reverse(address, args=comment_id)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
