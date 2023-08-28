from django.urls import reverse

from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'page, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('pk_from_news')),
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, page, args):
    """
    Проверка доступности страниц
    для анонимного пользователя.
    """
    url = reverse(page, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_from_comment')),
        ('news:delete', pytest.lazy_fixture('pk_from_comment')),
    ),
)
def test_pages_availability_for_auth_user(author_client, page, args):
    """
    Проверка доступности страниц для
    аутентифицированного пользователя.
    """
    url = reverse(page, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'page, args',
    (('news:edit', pytest.lazy_fixture('pk_from_comment')),
     ('news:delete', pytest.lazy_fixture('pk_from_comment')),),
)
def test_redirects(client, page, args):
    """
    Проверка перенаправления анонимного пользователя
    на страницу входа при доступе к защищенным страницам.
    """
    login_url = reverse('users:login')
    url = reverse(page, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize('page', ('news:edit', 'news:delete'))
def test_pages_availability_for_different_users(
        page, pk_from_comment, admin_client
):
    """
    Проверка доступности страниц
    для различных пользователей.
    """
    url = reverse(page, args=pk_from_comment)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
