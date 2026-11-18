from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from .models import MAX_ACTIVE_STUDENTS, Section, SectionMember


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

        edit_res = self.client.post(reverse('sections:section_update', args=[section.section_id]), {
            'section_name': 'CSIT327-G1 Updated',
            'academic_term': '1st Semester 2026-2027',
        })
        self.assertRedirects(edit_res, reverse('sections:section_detail', args=[section.section_id]))
        section.refresh_from_db()
        self.assertEqual(section.section_name, 'CSIT327-G1 Updated')
        self.assertEqual(section.invite_code, original_code)

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


class MemberOnboardingTests(TestCase):
    def setUp(self):
        self.treasurer = CustomUser.objects.create_user(
            email='treasurer@cit.edu',
            password='Password123!',
            full_name='Class Treasurer',
            role='TREASURER',
        )
        self.member = CustomUser.objects.create_user(
            email='karl@cit.edu',
            password='Password123!',
            full_name='Karl Cyrus Solinap',
            role='MEMBER',
        )
        self.section = Section.objects.create(
            treasurer=self.treasurer,
            section_name='CSIT327-G1',
            academic_term='1st Semester 2026-2027',
        )

    def test_member_can_join_section_via_invite_code(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse('sections:join_section'), {
            'invite_code': self.section.invite_code.lower(),
            'student_id_number': '24-1585-641',
        })
        self.assertEqual(SectionMember.objects.count(), 1)
        membership = SectionMember.objects.first()
        self.assertEqual(membership.user, self.member)
        self.assertEqual(membership.student_id_number, '24-1585-641')
        self.assertTrue(membership.is_active)
        self.assertRedirects(response, reverse('sections:member_section_detail', args=[self.section.section_id]))

    def test_duplicate_section_enrollment_blocked_br04(self):
        SectionMember.objects.create(
            section=self.section,
            user=self.member,
            student_id_number='24-1585-641',
        )
        self.client.force_login(self.member)
        response = self.client.post(reverse('sections:join_section'), {
            'invite_code': self.section.invite_code,
            'student_id_number': '24-1585-641',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SectionMember.objects.count(), 1)

    def test_fifty_active_student_limit_enforced_br05(self):
        for i in range(MAX_ACTIVE_STUDENTS):
            student = CustomUser.objects.create_user(
                email=f'student{i}@cit.edu',
                password='Password123!',
                full_name=f'Student {i}',
                role='MEMBER',
            )
            SectionMember.objects.create(
                section=self.section,
                user=student,
                student_id_number=f'24-0000-{i:03d}',
            )

        self.client.force_login(self.member)
        response = self.client.post(reverse('sections:join_section'), {
            'invite_code': self.section.invite_code,
            'student_id_number': '24-1585-641',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.section.active_member_count, MAX_ACTIVE_STUDENTS)

    def test_treasurer_can_toggle_and_remove_member(self):
        membership = SectionMember.objects.create(
            section=self.section,
            user=self.member,
            student_id_number='24-1585-641',
        )
        self.client.force_login(self.treasurer)

        toggle_url = reverse('sections:toggle_member_status', args=[self.section.section_id, membership.membership_id])
        self.client.post(toggle_url)
        membership.refresh_from_db()
        self.assertFalse(membership.is_active)

        self.client.post(toggle_url)
        membership.refresh_from_db()
        self.assertTrue(membership.is_active)

        remove_url = reverse('sections:remove_member', args=[self.section.section_id, membership.membership_id])
        self.client.post(remove_url)
        self.assertEqual(SectionMember.objects.count(), 0)