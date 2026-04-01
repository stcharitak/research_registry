from django.test import TestCase
from django.core.exceptions import PermissionDenied

from accounts.models import User, Role, RoleName
from applications.models import (
    Application,
    ApplicationLog,
    ApplicationLogAction,
    Status,
)
from applications.services import ApplicationService
from participants.models import Participant
from studies.models import Study


class ApplicationServiceTests(TestCase):
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
            first_name="John",
            last_name="Doe",
        )

    def test_researcher_can_create_application_for_own_study(self):
        application = ApplicationService.create_application(
            user=self.researcher,
            validated_data={
                "study": self.study,
                "participant": self.participant,
                "notes": "Test application",
            },
        )

        self.assertEqual(application.study, self.study)
        self.assertEqual(application.participant, self.participant)
        self.assertEqual(application.notes, "Test application")

        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(ApplicationLog.objects.count(), 1)

    def test_researcher_cannot_create_application_for_other_study(self):
        with self.assertRaises(PermissionDenied):
            ApplicationService.create_application(
                user=self.researcher,
                validated_data={
                    "study": self.other_study,
                    "participant": self.participant,
                    "notes": "Should fail",
                },
            )

        self.assertEqual(Application.objects.count(), 0)
        self.assertEqual(ApplicationLog.objects.count(), 0)

    def test_update_application_creates_log(self):
        application = Application.objects.create(
            study=self.study,
            participant=self.participant,
            notes="Old notes",
        )

        updated = ApplicationService.update_application(
            application=application,
            user=self.researcher,
            validated_data={"notes": "New notes"},
        )

        self.assertEqual(updated.notes, "New notes")
        self.assertEqual(ApplicationLog.objects.count(), 1)
        self.assertEqual(
            ApplicationLog.objects.first().action,
            ApplicationLogAction.UPDATED,
        )

    def test_admin_can_approve_application(self):
        application = Application.objects.create(
            study=self.study,
            participant=self.participant,
            notes="Pending app",
        )

        approved = ApplicationService.approve(application, self.admin)

        self.assertEqual(approved.status, Status.APPROVED)
        self.assertEqual(approved.reviewed_by, self.admin)
        self.assertIsNotNone(approved.reviewed_by)

        self.assertEqual(ApplicationLog.objects.count(), 1)
        self.assertEqual(
            ApplicationLog.objects.first().action,
            ApplicationLogAction.APPROVED,
        )

    def test_admin_can_reject_application(self):
        application = Application.objects.create(
            study=self.study,
            participant=self.participant,
            notes="Pending app",
        )

        rejected = ApplicationService.reject(application, self.admin)

        self.assertEqual(rejected.status, Status.REJECTED)
        self.assertEqual(rejected.reviewed_by, self.admin)
        self.assertIsNotNone(rejected.reviewed_by)

        self.assertEqual(ApplicationLog.objects.count(), 1)
        self.assertEqual(
            ApplicationLog.objects.first().action,
            ApplicationLogAction.REJECTED,
        )

    def test_researcher_cannot_approve_or_reject(self):
        application = Application.objects.create(
            study=self.study,
            participant=self.participant,
            notes="Pending app",
        )

        with self.assertRaises(PermissionDenied):
            ApplicationService.approve(application, self.researcher)

        with self.assertRaises(PermissionDenied):
            ApplicationService.reject(application, self.researcher)

        # Status should remain unchanged
        application.refresh_from_db()
        self.assertEqual(application.status, Status.PENDING)
        self.assertIsNone(application.reviewed_by)
        self.assertEqual(ApplicationLog.objects.count(), 0)
