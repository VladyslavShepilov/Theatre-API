from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre_service.models import TheatreHall
from theatre_service.serializers import TheatreHallSerializer, TheatreHallListSerializer


def create_user(**kwargs):
    return get_user_model().objects.create(**kwargs)


THEATRE_HALL_LIST_URL = reverse("theatre-api:theatrehall-list")


def sample_theatre_hall(**params):
    defaults = {
        "name": "Blue",
        "rows": 15,
        "seats_in_row": 20,
    }
    defaults.update(params)
    return TheatreHall.objects.create(**defaults)


class PublicTheatreHallApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(THEATRE_HALL_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTheatreHallApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username="test_user",
            email="user@test.com",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_theatre_hall(self):
        sample_theatre_hall()
        response = self.client.get(THEATRE_HALL_LIST_URL)
        theatre_halls = TheatreHall.objects.all()
        serializer = TheatreHallListSerializer(theatre_halls, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_post_theatre_hall(self):
        payload = {
            "name": "Blue",
            "rows": 15,
            "seats_in_row": 20,
        }
        response = self.client.post(THEATRE_HALL_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminTheatreHallApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            username="test_admin",
            email="admin@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_post_theatre_hall(self):
        payload = {
            "name": "Blue",
            "rows": 15,
            "seats_in_row": 20,
        }
        response = self.client.post(THEATRE_HALL_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TheatreHall.objects.count(), 1)
        theatre_hall = TheatreHall.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(theatre_hall, key))

    def test_retrieve_theatre_hall(self):
        theatre_hall = sample_theatre_hall()
        url = reverse("theatre-api:theatrehall-detail", args=[theatre_hall.id])
        response = self.client.get(url)
        serializer = TheatreHallSerializer(theatre_hall)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_theatre_hall(self):
        theatre_hall = sample_theatre_hall()
        payload = {
            "name": "Red",
            "rows": 20,
            "seats_in_row": 25,
        }
        url = reverse("theatre-api:theatrehall-detail", args=[theatre_hall.id])
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        theatre_hall.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(theatre_hall, key))

    def test_delete_theatre_hall(self):
        theatre_hall = sample_theatre_hall()
        url = reverse("theatre-api:theatrehall-detail", args=[theatre_hall.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TheatreHall.objects.count(), 0)
