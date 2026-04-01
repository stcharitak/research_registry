from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role, RoleName
from applications.models import (
    Application,
    ApplicationLog,
    Status,
)
from participants.models import Participant
from studies.models import Study


class ApplicationAPITests(APITestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(name=RoleName.ADMIN)
        self.researcher_role = Role.objects.create(name=RoleName.RESEARCHER)

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            role=self.admin_role,
        )
        self.researcher = User.objects.create_user(
            username="researcher",
            email="researcher@example.com",
            password="testpass123",
            role=self.researcher_role,
        )
        self.other_researcher = User.objects.create_user(
            username="otherresearcher",
            email="other@example.com",
            password="testpass123",
            role=self.researcher_role,
        )

        self.study = Study.objects.create(
            title="Study A",
            created_by=self.researcher,
        )
        self.other_study = Study.objects.create(
            title="Study B",
            created_by=self.other_researcher,
        )

        self.participant = Participant.objects.create(
            code="P1",
            first_name="John",
            last_name="Doe",
        )

        self.other_participant = Participant.objects.create(
            code="P2",
            first_name="Maria",
            last_name="Charitakis",
        )

        self.application = Application.objects.create(
            study=self.study,
            participant=self.participant,
            notes="Pending app",
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_researcher_cannot_approve_via_api(self):
        self.authenticate(self.researcher)

        response = self.client.post(f"/api/applications/{self.application.id}/approve/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Status.PENDING)
        self.assertIsNone(self.application.reviewed_by)
        self.assertEqual(ApplicationLog.objects.count(), 0)

    def test_admin_can_approve_via_api(self):
        self.authenticate(self.admin)

        response = self.client.post(f"/api/applications/{self.application.id}/approve/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Status.APPROVED)
        self.assertEqual(self.application.reviewed_by, self.admin)
        self.assertIsNotNone(self.application.reviewed_by)
        self.assertEqual(ApplicationLog.objects.count(), 1)

    def test_admin_can_reject_via_api(self):
        self.authenticate(self.admin)

        response = self.client.post(f"/api/applications/{self.application.id}/reject/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Status.REJECTED)
        self.assertEqual(self.application.reviewed_by, self.admin)
        self.assertIsNotNone(self.application.reviewed_by)
        self.assertEqual(ApplicationLog.objects.count(), 1)

    def test_researcher_only_sees_own_applications(self):
        other_application = Application.objects.create(
            study=self.other_study,
            participant=self.participant,
            notes="Other app",
        )

        own_application = Application.objects.create(
            study=self.study,
            participant=self.other_participant,
            notes="Same app",
        )

        self.authenticate(self.researcher)

        response = self.client.get("/api/applications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        ids = (
            [item["id"] for item in data["results"]]
            if "results" in data
            else [item["id"] for item in data]
        )

        self.assertIn(self.application.id, ids)
        self.assertNotIn(other_application.id, ids)
        self.assertIn(own_application.id, ids)

    def test_me_endpoint_returns_current_user(self):
        self.authenticate(self.researcher)

        response = self.client.get("/api/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.researcher.username)
        self.assertEqual(response.data["email"], self.researcher.email)
        self.assertEqual(response.data["role"], self.researcher.role.name)
