import pytest

from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_count(client, home_page_url):
    """
    Проверка количества новостей на главной странице.
    """
    url = home_page_url
    res = client.get(url)
    object_list = res.context['object_list']
    news_count = len(object_list)
    msg = (
        'На главной странице должно находиться не больше '
        f'{settings.NEWS_COUNT_ON_HOME_PAGE} новостей,'
        f' выведено {news_count}'
    )
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, msg


@pytest.mark.parametrize(
    'username, is_permitted',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
def test_comment_form_availability_for_different_users(
    pk_from_news,
    username,
    is_permitted
):
    """
    Проверка доступности формы комментария
    для разных пользователей.
    """
    url = reverse('news:detail', args=pk_from_news)
    res = username.get(url)
    form_available = 'form' in res.context
    assert form_available == is_permitted


@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_order(client):
    """
    Проверка порядка отображения новостей на главной странице.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    sorted_list_of_news = sorted(
        object_list,
        key=lambda news: news.date,
        reverse=True
    )
    for actual_news, expected_news in zip(object_list, sorted_list_of_news):
        assert actual_news.date == expected_news.date, (
            'Должна быть первой в списке '
            f'новость "{expected_news.title}" с датой '
            f'{expected_news.date}, получена '
            f'"{actual_news.title}" {actual_news.date}'
        )


@pytest.mark.usefixtures('make_bulk_of_comments')
def test_comments_order(client, pk_from_news):
    """
    Проверка порядка отображения
    комментариев на странице новости.
    """
    url = reverse('news:detail', args=pk_from_news)
    res = client.get(url)
    object_list = res.context['news'].comment_set.all()
    sorted_list_of_comments = sorted(
        object_list, key=lambda comment: comment.created
    )
    for as_is, to_be in zip(
        object_list,
        sorted_list_of_comments
    ):
        msg = (
            'Первым в списке должен быть'
            f' комментарий "{to_be.text}" с датой'
            f' {to_be.created}, получен '
            f'"{as_is.text}" {as_is.created}'
        )
        assert as_is.created == to_be.created, msg
