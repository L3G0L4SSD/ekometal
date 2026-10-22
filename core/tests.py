from django.test import TestCase
from django.urls import reverse

from core.models import Category, ContactInquiry, Product


class SiteTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Izgara")
        self.p1 = Product.objects.create(
            category=self.cat, name="Çift Gözlü Izgara", model_code="EK-100",
            is_featured=True, specs="Çap: 40 cm\nYükseklik: 30 cm",
        )
        self.p2 = Product.objects.create(category=self.cat, name="Gizli", model_code="EK-101")

    def test_home_featured_only(self):
        h = self.client.get("/").content.decode()
        self.assertIn("EK-100", h)
        # Dynamic category stream now legitimately includes products of self.cat
        self.assertIn("EK-101", h)
        self.assertIn("wa.me/905334197894?text=Merhaba%2C%20EK-100", h)

    def test_list_and_search(self):
        r = self.client.get(reverse("core:product_list"), {"q": "ek-101"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["total"], 1)
        r = self.client.get(reverse("core:category", args=[self.cat.slug]))
        self.assertEqual(r.context["total"], 2)
        self.assertEqual(self.client.get("/kategori/yok/").status_code, 404)

    def test_detail(self):
        r = self.client.get(reverse("core:product_detail", args=[self.p1.pk]))
        self.assertContains(r, "Çap")
        self.assertContains(r, "EK-100")
        self.assertEqual(self.client.get("/urun/9999/").status_code, 404)

    def test_contact_post(self):
        data = {"full_name": "Ali Veli", "company_name": "Lezzet Restoran",
                "phone": "0532 111 22 33", "product_interest": "EK-100", "message": "10 adet"}
        r = self.client.post(reverse("core:contact"), data)
        self.assertRedirects(r, reverse("core:contact"))
        self.assertEqual(ContactInquiry.objects.get().message, "10 adet")

    def test_contact_invalid_and_honeypot(self):
        bad = {"full_name": "A", "company_name": "B", "phone": "123"}
        self.client.post(reverse("core:contact"), bad)
        self.assertEqual(ContactInquiry.objects.count(), 0)
        spam = {"full_name": "A", "company_name": "B", "phone": "05321112233", "website": "x"}
        self.client.post(reverse("core:contact"), spam)
        self.assertEqual(ContactInquiry.objects.count(), 0)
