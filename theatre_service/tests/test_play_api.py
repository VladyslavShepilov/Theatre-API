import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from theatre_service.models import Play, Performance, TheatreHall, Genre, Actor
from theatre_service.serializers import PlayDetailSerializer

PLAY_URL = reverse("theatre-api:play-list")
PERFORMANCE_URL = reverse("theatre-api:performance-list")


def sample_play(**params) -> Play:
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
        "duration": 90,
    }
    defaults.update(params)
    return Play.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)
    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)
    return Actor.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Yellow", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "play": None,
        "theatre_hall": theatre_hall,
    }
    defaults.update(params)
    return Performance.objects.create(**defaults)


def image_upload_url(play_id):
    """Return URL for play image upload"""
    return reverse("theatre-api:play-upload-image", args=[play_id])


def detail_url(play_id):
    return reverse("theatre-api:play-detail", args=[play_id])


def performance_detail_url(performance_id):
    return reverse("theatre-api:performance-detail", args=[performance_id])


class PlayImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin", "admin@theatre.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.play = sample_play()
        self.genre = sample_genre()
        self.actor = sample_actor()
        self.performance = sample_performance(play=self.play)

    def tearDown(self):
        self.play.image.delete()

    def test_upload_image_to_play(self):
        """Test uploading an image to play"""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.play.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.play.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.play.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_play_list(self):
        url = PLAY_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "duration": 90,
                    "genres": [self.genre.id],
                    "actors": [self.actor.id],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(title="Title")
        self.assertFalse(play.image)

    def test_image_url_is_shown_on_play_detail(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.play.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_performance_detail(self):
        upload_url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(upload_url, {"image": ntf}, format="multipart")
        performance_detail = performance_detail_url(
            performance_id=self.performance.pk
        )
        res = self.client.get(performance_detail)

        self.assertIn("image", res.data["play"])


class PlayTestUnauthorizedUser(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PlayTestAuthorizedUser(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="admin,"
        )
        self.genre = sample_genre()
        self.genre1 = sample_genre(name="Comedy")

        self.actor = sample_actor()
        self.actor1 = sample_actor(first_name="Denis", last_name="Petrov")

        self.client.force_authenticate(user=self.user)

        self.play = sample_play()
        self.play.actors.add(self.actor)
        self.play.genres.add(self.genre)

        self.play2 = sample_play(
            title="Test play",
            description="Test play written to test API",
            duration=125,
        )
        self.play2.actors.add(self.actor, self.actor1)
        self.play2.genres.add(self.genre, self.genre1)

        self.performance = sample_performance(play=self.play)

    def test_authorized_access_list(self):
        response = self.client.get(PLAY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authorized_access_detail(self):
        response = self.client.get(detail_url(self.play.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filtering_genres_actors_id_title_str(self):
        response = self.client.get(
            PLAY_URL,
            data={
                "title": self.play.title,
                "actors": self.actor.pk,
                "genres": self.genre.pk,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        response = self.client.get(
            PLAY_URL,
            data={"actors": self.actor.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        response = self.client.get(
            PLAY_URL,
            data={"genres": self.genre1.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_play_post(self):
        payload = {
            "title": "Test play post",
            "description": "Test play written to test API",
            "duration": 125,
            "actors": [self.actor.pk],
            "genres": [self.genre.pk]
        }
        response = self.client.post(PLAY_URL, data=payload)
        play = Play.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key not in ("actors", "genres"):
                self.assertEqual(payload[key], getattr(play, key))

    def test_list_play(self):
        response = self.client.get(PLAY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_play(self):
        play = sample_play(title="Test play post", duration=120)
        url = detail_url(play_id=play.pk)
        response = self.client.get(url)
        serializer = PlayDetailSerializer(play)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
