from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Category, ContactInquiry, Product, ProductImage


def admin_login(request):
    """Sade ve şık yönetici giriş ekranı."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("core:admin_dashboard")

    error_message = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Hoş geldiniz, {user.first_name or user.username}!")
            return redirect("core:admin_dashboard")
        else:
            error_message = "Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin."

    return render(request, "yonetim/login.html", {"error_message": error_message})


def admin_logout(request):
    """Güvenli çıkış."""
    logout(request)
    messages.info(request, "Güvenli çıkış yapıldı.")
    return redirect("core:admin_login")


@login_required(login_url="core:admin_login")
def admin_dashboard(request):
    """Tek sayfa ana yönetim kokpiti (CRM, Ürünler, Kategoriler)."""
    today = date.today()

    # İstatistikler
    inquiries_qs = ContactInquiry.objects.order_by("-created_at")
    total_inquiries = inquiries_qs.count()
    today_inquiries = inquiries_qs.filter(created_at__date=today).count()
    
    products_qs = Product.objects.select_related("category").prefetch_related("images").order_by("-created_at")
    categories_qs = Category.objects.annotate(product_count=Count("products")).order_by("order", "name")

    # Arama / Filtreleme (Ürünler veya Teklifler için)
    q = request.GET.get("q", "").strip()
    active_tab = request.GET.get("tab", "teklifler")

    if q:
        if active_tab == "urunler":
            products_qs = products_qs.filter(
                Q(name__icontains=q) | Q(model_code__icontains=q) | Q(category__name__icontains=q)
            )
        elif active_tab == "teklifler":
            inquiries_qs = inquiries_qs.filter(
                Q(full_name__icontains=q) | Q(company_name__icontains=q) | Q(phone__icontains=q) | Q(product_interest__icontains=q)
            )

    cat_filter = request.GET.get("cat")
    if cat_filter:
        products_qs = products_qs.filter(category_id=cat_filter)

    context = {
        "inquiries": inquiries_qs,
        "products": products_qs,
        "categories": categories_qs,
        "total_inquiries": total_inquiries,
        "today_inquiries": today_inquiries,
        "total_products": products_qs.count(),
        "total_categories": categories_qs.count(),
        "active_tab": active_tab,
        "q": q,
        "cat_filter": cat_filter,
    }
    return render(request, "yonetim/dashboard.html", context)


@login_required(login_url="core:admin_login")
@require_POST
def admin_product_save(request):
    """Yeni ürün ekleme veya mevcut ürünü güncelleme."""
    product_id = request.POST.get("product_id")
    name = request.POST.get("name", "").strip()
    model_code = request.POST.get("model_code", "").strip().upper()
    category_id = request.POST.get("category_id")
    specs = request.POST.get("specs", "").strip()
    wholesale_info = request.POST.get("wholesale_info", "").strip()
    is_featured = bool(request.POST.get("is_featured"))

    if not name or not model_code or not category_id:
        messages.error(request, "Ürün adı, model kodu ve kategori alanları zorunludur.")
        return redirect(f"/yonetim/?tab=urunler")

    category = get_object_or_404(Category, pk=category_id)

    if product_id:
        product = get_object_or_404(Product, pk=product_id)
        # Model kodu tekil mi kontrol et
        if Product.objects.filter(model_code=model_code).exclude(pk=product.pk).exists():
            messages.error(request, f"'{model_code}' model kodu başka bir üründe kullanılıyor.")
            return redirect(f"/yonetim/?tab=urunler")
        product.name = name
        product.model_code = model_code
        product.category = category
        product.specs = specs
        product.wholesale_info = wholesale_info
        product.is_featured = is_featured
    else:
        if Product.objects.filter(model_code=model_code).exists():
            messages.error(request, f"'{model_code}' model kodu zaten mevcut.")
            return redirect(f"/yonetim/?tab=urunler")
        product = Product(
            name=name,
            model_code=model_code,
            category=category,
            specs=specs,
            wholesale_info=wholesale_info,
            is_featured=is_featured,
        )

    # Ana kapak görseli
    if "image" in request.FILES:
        product.image = request.FILES["image"]

    product.save()

    # Silinmek istenen ek galeri görselleri
    delete_image_ids = request.POST.getlist("delete_images")
    if delete_image_ids:
        ProductImage.objects.filter(product=product, id__in=delete_image_ids).delete()

    # Yeni yüklenen çoklu galeri görselleri (HTML5 Çoklu Seçim + Ayrı 4 Slot)
    gallery_files = request.FILES.getlist("gallery_images")
    for slot_name in ["gallery_image_1", "gallery_image_2", "gallery_image_3", "gallery_image_4"]:
        if slot_name in request.FILES:
            gallery_files.append(request.FILES[slot_name])

    if gallery_files:
        current_max_order = (
            ProductImage.objects.filter(product=product).count()
        )
        for idx, f in enumerate(gallery_files):
            ProductImage.objects.create(
                product=product,
                image=f,
                order=current_max_order + idx + 1,
            )

    messages.success(request, f"'{product.name}' ({product.model_code}) başarıyla kaydedildi.")
    return redirect("/yonetim/?tab=urunler")


@login_required(login_url="core:admin_login")
@require_POST
def admin_product_delete(request, pk):
    """Ürün silme."""
    product = get_object_or_404(Product, pk=pk)
    name = f"{product.name} ({product.model_code})"
    product.delete()
    messages.success(request, f"'{name}' ürünü başarıyla silindi.")
    return redirect("/yonetim/?tab=urunler")


@login_required(login_url="core:admin_login")
@require_POST
def admin_category_save(request):
    """Kategori ekleme veya düzenleme."""
    category_id = request.POST.get("category_id")
    name = request.POST.get("name", "").strip()
    order = request.POST.get("order", 0)

    try:
        order = int(order)
    except ValueError:
        order = 0

    if not name:
        messages.error(request, "Kategori adı zorunludur.")
        return redirect("/yonetim/?tab=kategoriler")

    if category_id:
        category = get_object_or_404(Category, pk=category_id)
        category.name = name
        category.order = order
    else:
        category = Category(name=name, order=order)

    if "image" in request.FILES:
        category.image = request.FILES["image"]

    category.save()
    messages.success(request, f"'{category.name}' kategorisi başarıyla kaydedildi.")
    return redirect("/yonetim/?tab=kategoriler")


@login_required(login_url="core:admin_login")
@require_POST
def admin_category_delete(request, pk):
    """Kategori silme."""
    category = get_object_or_404(Category, pk=pk)
    if category.products.exists():
        messages.error(
            request,
            f"'{category.name}' kategorisinde {category.products.count()} ürün bulunuyor. Önce bu ürünleri taşıyın veya silin.",
        )
    else:
        name = category.name
        category.delete()
        messages.success(request, f"'{name}' kategorisi silindi.")
    return redirect("/yonetim/?tab=kategoriler")


@login_required(login_url="core:admin_login")
@require_POST
def admin_inquiry_delete(request, pk):
    """Teklif talebi silme."""
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    name = f"{inquiry.full_name} ({inquiry.company_name})"
    inquiry.delete()
    messages.success(request, f"'{name}' talebi silindi.")
    return redirect("/yonetim/?tab=teklifler")
