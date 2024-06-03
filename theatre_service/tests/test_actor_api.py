from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from theatre_service.models import Actor
from theatre_service.serializers import ActorSerializer

ACTOR_URL = reverse("theatre-api:actor-list")


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


def sample_actor(**params):
    defaults = {
        "first_name": "test_name",
        "last_name": "test_last",
    }
    defaults.update(params)
    return Actor.objects.create(**defaults)


class PublicActorApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ACTOR_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateActorApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test_user",
            email="user@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_actors(self):
        sample_actor()
        response = self.client.get(ACTOR_URL)
        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_post_actors(self):
        payload = {
            "first_name": "test_name",
            "last_name": "test_last",
        }
        response = self.client.post(ACTOR_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminActorApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test_admin",
            email="admin@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_actors(self):
        payload = {
            "first_name": "test_name",
            "last_name": "test_last",
        }
        response = self.client.post(ACTOR_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Actor.objects.count(), 1)
        actor = Actor.objects.get(id=response.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(actor, key))

    def test_retrieve_actor(self):
        actor = sample_actor()
        url = reverse("theatre-api:actor-detail", args=[actor.id])
        response = self.client.get(url)
        serializer = ActorSerializer(actor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_actor(self):
        actor = sample_actor()
        payload = {
            "first_name": "updated_name",
            "last_name": "updated_last",
        }
        url = reverse("theatre-api:actor-detail", args=[actor.id])
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        actor.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(actor, key))

    def test_delete_actor(self):
        actor = sample_actor()
        url = reverse("theatre-api:actor-detail", args=[actor.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Actor.objects.count(), 0)
