from django.urls import path

from . import admin_views, views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("urunler/", views.product_list, name="product_list"),
    path("kategori/<slug:slug>/", views.product_list, name="category"),
    path("urun/<int:pk>/", views.product_detail, name="product_detail"),
    path("iletisim/", views.contact, name="contact"),
    path("hakkimizda/", views.about, name="about"),

    # Özel Yönetim Paneli Rotaları
    path("yonetim/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("yonetim/giris/", admin_views.admin_login, name="admin_login"),
    path("yonetim/cikis/", admin_views.admin_logout, name="admin_logout"),
    path("yonetim/urun/kaydet/", admin_views.admin_product_save, name="admin_product_save"),
    path("yonetim/urun/sil/<int:pk>/", admin_views.admin_product_delete, name="admin_product_delete"),
    path("yonetim/kategori/kaydet/", admin_views.admin_category_save, name="admin_category_save"),
    path("yonetim/kategori/sil/<int:pk>/", admin_views.admin_category_delete, name="admin_category_delete"),
    path("yonetim/teklif/sil/<int:pk>/", admin_views.admin_inquiry_delete, name="admin_inquiry_delete"),
]
