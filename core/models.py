from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Kategori Adı", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True, blank=True)
    image = models.ImageField("Görsel", upload_to="categories/", blank=True, null=True)
    order = models.PositiveIntegerField("Sıra", default=0, db_index=True)

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name.replace("ı", "i").replace("İ", "i"))
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products", verbose_name="Kategori"
    )
    name = models.CharField("Ürün Adı", max_length=200)
    model_code = models.CharField("Model Kodu", max_length=60, unique=True, db_index=True)
    image = models.ImageField("Görsel", upload_to="products/", blank=True, null=True)
    is_featured = models.BooleanField("Ana Sayfada Öne Çıkar", default=False)
    specs = models.TextField(
        "Teknik Özellikler / Ölçüler", blank=True,
        help_text="Her satıra bir özellik: 'Çap: 40 cm', 'Yükseklik: 30 cm', 'Hacim: 25 lt' ...",
    )
    wholesale_info = models.TextField(
        "Toptan / Proje İskonto Bilgisi", blank=True,
        help_text="Örn: 10+ adet siparişlerde %10 iskonto. Projeye özel fiyat için iletişime geçin.",
    )
    created_at = models.DateTimeField("Oluşturulma Tarihi", auto_now_add=True)

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model_code} - {self.name}"

    @property
    def spec_rows(self):
        """specs alanını (özellik, değer) çiftlerine ayırır. 'Anahtar: Değer' biçimi beklenir."""
        rows = []
        for line in self.specs.splitlines():
            line = line.strip()
            if not line:
                continue
            key, sep, value = line.partition(":")
            rows.append((key.strip(), value.strip()) if sep else (line, ""))
        return rows

    @property
    def gallery_images(self):
        """Ana görsel ve ek galeri görsellerinin tümünü liste olarak döner."""
        imgs = []
        if self.image:
            imgs.append(self.image)
        for pi in self.images.all():
            if pi.image:
                imgs.append(pi.image)
        return imgs


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Ürün"
    )
    image = models.ImageField("Görsel", upload_to="products/gallery/")
    order = models.PositiveIntegerField("Sıra", default=0, db_index=True)

    class Meta:
        verbose_name = "Ürün Ek Görseli"
        verbose_name_plural = "Ürün Ek Görselleri"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.model_code} - Görsel #{self.pk}"


class ContactInquiry(models.Model):
    full_name = models.CharField("Ad Soyad", max_length=150)
    company_name = models.CharField("Firma Adı", max_length=200)
    phone = models.CharField("Telefon", max_length=30)
    product_interest = models.CharField("İlgilenilen Ürün", max_length=200, blank=True)
    message = models.TextField("Mesaj", blank=True)
    created_at = models.DateTimeField("Talep Tarihi", auto_now_add=True)

    class Meta:
        verbose_name = "Teklif Talebi"
        verbose_name_plural = "Teklif Talepleri"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.company_name})"
