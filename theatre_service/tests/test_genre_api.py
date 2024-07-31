from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from theatre_service.models import Genre
from django.contrib.auth import get_user_model
from theatre_service.serializers import GenreSerializer

GENRE_URL = reverse("theatre-api:genre-list")


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


def sample_genre(**params):
    defaults = {"name": "Comedy"}
    defaults.update(params)
    return Genre.objects.create(**defaults)


class PublicGenresApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGenreApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test_user",
            email="user@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_genres(self):
        sample_genre()

        response = self.client.get(GENRE_URL)

        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_post_genres(self):
        payload = {"name": "Name"}

        response = self.client.post(GENRE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminGenreApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test_admin",
            email="admin@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_genres(self):
        payload = {"name": "Name"}

        response = self.client.post(GENRE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genre.objects.count(), 1)
        genre = Genre.objects.get(id=response.data["id"])
        self.assertEqual(genre.name, payload["name"])

    def test_retrieve_genre(self):
        genre = sample_genre()

        url = reverse("theatre-api:genre-detail", args=[genre.id])
        response = self.client.get(url)

        serializer = GenreSerializer(genre)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_genre(self):
        genre = sample_genre()

        payload = {"name": "Updated Name"}
        url = reverse("theatre-api:genre-detail", args=[genre.id])
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        genre.refresh_from_db()
        self.assertEqual(genre.name, payload["name"])

    def test_delete_genre(self):
        genre = sample_genre()

        url = reverse("theatre-api:genre-detail", args=[genre.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Genre.objects.count(), 0)
