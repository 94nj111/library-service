# from rest_framework.test import APITestCase
# from django.urls import reverse
# from rest_framework import status
# from borrowings_service.models import Borrowing
#
#
# class PaymentTests(APITestCase):
#     def setUp(self):
#         self.borrowing = Borrowing.objects.create(book_title="Test Book", total_price=100.00)
#
#     def test_create_payment_session(self):
#         url = reverse("payment:create-session", kwargs={"borrowing_id": self.borrowing.id})
#         response = self.client.post(url)
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn("session_url", response.data)
#         self.assertIn("session_id", response.data)
#
#     def test_success_payment(self):
#         session_id = "test_session_id"
#         url = reverse('payment:success') + f"?session_id={session_id}"
#         response = self.client.get(url)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["message"], "Payment successful")
#
#     def test_cancel_payment(self):
#         session_id = "test_session_id"
#         url = reverse("payment:cancel") + f"?session_id={session_id}"
#         response = self.client.get(url)
#
#         self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
#         self.assertEqual(response.data["message"],
#                          "The payment can be made later, but the session is available for only 24 hours.")