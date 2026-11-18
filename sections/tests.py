from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from .models import Section


class SectionWorkspaceTests(TestCase):
    def setUp(self):
        self.treasurer1 = CustomUser.objects.create_user(
            email='treasurer1@cit.edu',
            password='Password123!',
            full_name='Treasurer One',
            role='TREASURER',
        )
        self.treasurer2 = CustomUser.objects.create_user(
            email='treasurer2@cit.edu',
            password='Password123!',
            full_name='Treasurer Two',
            role='TREASURER',
        )
        self.member = CustomUser.objects.create_user(
            email='student1@cit.edu',
            password='Password123!',
            full_name='Student One',
            role='MEMBER',
        )

    def test_treasurer_can_create_section_with_unique_invite_code(self):
        self.client.force_login(self.treasurer1)
        response = self.client.post(reverse('sections:section_create'), {
            'section_name': 'CSIT327-G1',
            'academic_term': '1st Semester 2026-2027',
        })
        self.assertEqual(Section.objects.count(), 1)
        section = Section.objects.first()
        self.assertEqual(section.treasurer, self.treasurer1)
        self.assertEqual(len(section.invite_code), 8)
        self.assertTrue(section.invite_code.isalnum())
        self.assertRedirects(response, reverse('sections:section_detail', args=[section.section_id]))

    def test_treasurer_can_update_and_delete_own_section(self):
        section = Section.objects.create(
            treasurer=self.treasurer1,
            section_name='CSIT327-G1',
            academic_term='1st Semester 2026-2027',
        )
        original_code = section.invite_code
        self.client.force_login(self.treasurer1)

        # Update
        edit_res = self.client.post(reverse('sections:section_update', args=[section.section_id]), {
            'section_name': 'CSIT327-G1 Updated',
            'academic_term': '1st Semester 2026-2027',
        })
        self.assertRedirects(edit_res, reverse('sections:section_detail', args=[section.section_id]))
        section.refresh_from_db()
        self.assertEqual(section.section_name, 'CSIT327-G1 Updated')
        self.assertEqual(section.invite_code, original_code)

        # Delete
        del_res = self.client.post(reverse('sections:section_delete', args=[section.section_id]))
        self.assertRedirects(del_res, reverse('sections:section_list'))
        self.assertEqual(Section.objects.count(), 0)

    def test_member_blocked_with_403(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse('sections:section_list'))
        self.assertEqual(response.status_code, 403)

    def test_other_treasurer_blocked_from_foreign_section_with_403(self):
        section = Section.objects.create(
            treasurer=self.treasurer1,
            section_name='CSIT327-G1',
            academic_term='1st Semester 2026-2027',
        )
        self.client.force_login(self.treasurer2)
        for url_name in ('sections:section_detail', 'sections:section_update', 'sections:section_delete'):
            res = self.client.get(reverse(url_name, args=[section.section_id]))
            self.assertEqual(res.status_code, 403)