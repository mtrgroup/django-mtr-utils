from django.test import TestCase

from mtr.utils.helpers import absolute_url, relative_media_url


class HelpersTest(TestCase):

    def test_absolute_url(self):
        self.assertEqual(
            'http://localhost/test/test.html',
            absolute_url('test/test.html'))

        self.assertEqual(
            '/media/test/somemedia.jpeg',
            relative_media_url('test/somemedia.jpeg'))

        # BUG: real settings
