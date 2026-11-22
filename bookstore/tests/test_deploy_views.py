from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse


class HelloViewTest(SimpleTestCase):
    def test_hello_uses_template(self):
        with patch('bookstore.views.get_last_commit', return_value=None):
            response = self.client.get(reverse('hello'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hello_world.html')
        self.assertContains(response, 'Hello World')

    def test_hello_shows_last_commit(self):
        commit = {'sha': 'abc1234', 'message': 'Mensagem do commit'}

        with patch('bookstore.views.get_last_commit', return_value=commit):
            response = self.client.get(reverse('hello'))

        self.assertContains(response, 'abc1234')
        self.assertContains(response, 'Mensagem do commit')


class UpdateServerViewTest(SimpleTestCase):
    def test_get_is_not_allowed(self):
        response = self.client.get(reverse('update_server'))

        self.assertEqual(response.status_code, 405)

    def test_post_pulls_the_code(self):
        with patch('git.Repo') as repo_class:
            response = self.client.post(reverse('update_server'))

        self.assertEqual(response.status_code, 200)
        repo_class.return_value.remotes.origin.pull.assert_called_once()

    def test_post_returns_500_when_pull_fails(self):
        with patch('git.Repo', side_effect=Exception('falha')):
            response = self.client.post(reverse('update_server'))

        self.assertEqual(response.status_code, 500)
