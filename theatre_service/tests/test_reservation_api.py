from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre_service.models import Ticket, Reservation
from theatre_service.tests.test_performance_api import sample_performance


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


RESERVATION_URL = reverse("theatre-api:reservation-list")


def sample_reservation(user):
    return Reservation.objects.create(user=user)


def sample_ticket(reservation, **params):
    performance = sample_performance()

    defaults = {
        "performance": performance,
        "row": 2,
        "seat": 2,
        "reservation": reservation,
    }

    defaults.update(params)

    return Ticket.objects.create(**defaults)


class PublicReservationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReservationApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test_admin",
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_reservation(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(reservation)

        response = self.client.get(RESERVATION_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_reservation(self):
        response = self.client.post(RESERVATION_URL, {})
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_reservation(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(reservation)

        response = self.client.get(
            reverse("theatre-api:reservation-detail",
                    args=[reservation.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_reservation(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(reservation)

        response = self.client.put(
            reverse("theatre-api:reservation-detail",
                    args=[reservation.id])
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_reservation(self):
        reservation = sample_reservation(user=self.user)
        sample_ticket(reservation)

        response = self.client.delete(
            reverse("theatre-api:reservation-detail",
                    args=[reservation.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AdminReservationApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test_admin",
            email="test@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_reservation_when_admin_dont_have_reservation(self):
        user = get_user_model().objects.create_user(
            username="user",
            email="user@test.com",
            password="paspassjnf",
        )
        reservation = sample_reservation(user=user)
        sample_ticket(reservation)

        response = self.client.get(RESERVATION_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        self.client.force_authenticate(user=user)
        response = self.client.get(RESERVATION_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
