from django.test import TestCase

from ...models import Office


class PublishedMixinTest(TestCase):

    def test_only_published_manager_and_queryset_default_datetime(self):
        data = [
            dict(published=False, address='office', office='not_published'),
            dict(office='published', address='some adress'),
            dict(office='published again', address='some address')
        ]

        published_offices = []
        not_published_offices = []

        for item in data:
            office = Office.objects.create(**item)
            if office.is_published():
                published_offices.append(office)
            else:
                not_published_offices.append(office)

        self.assertQuerysetEqual(
            Office.objects.published(), reversed(published_offices),
            transform=lambda o: o)
        self.assertQuerysetEqual(
            Office.published_objects.all(), reversed(published_offices),
            transform=lambda o: o)
