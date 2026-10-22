from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactInquiryForm
from .models import Category, Product


CATEGORY_THEMES = [
    {
        "bg_gradient": "from-[#f9e9f1] via-[#eed6e4] to-[#dfc0d4]",
        "border": "border-[#d4b0c7]/50",
        "text_color": "text-[#2b1220]",
        "glow_1": "bg-white/30",
        "glow_2": "bg-rose-300/20",
        "btn_bg": "bg-[#2b1220] hover:bg-[#3d1a2e]",
        "btn_text": "text-white",
        "badge_color": "bg-[#2b1220]",
        "shadow": "shadow-[0_35px_80px_-20px_rgba(210,175,195,0.45)]",
    },
    {
        "bg_gradient": "from-[#e2ece5] via-[#d4e4d8] to-[#c5dccb]",
        "border": "border-[#b6d3be]/50",
        "text_color": "text-[#142318]",
        "glow_1": "bg-white/40",
        "glow_2": "bg-emerald-300/20",
        "btn_bg": "bg-[#142318] hover:bg-[#1f3625]",
        "btn_text": "text-white",
        "badge_color": "bg-[#142318]",
        "shadow": "shadow-[0_35px_80px_-20px_rgba(182,211,190,0.45)]",
    },
    {
        "bg_gradient": "from-[#a7c1d4] via-[#96b0c4] to-[#849fb3]",
        "border": "border-[#738e9f]/40",
        "text_color": "text-[#0f1d27]",
        "glow_1": "bg-white/20",
        "glow_2": "bg-blue-300/20",
        "btn_bg": "bg-[#0f1d27] hover:bg-[#182e3d]",
        "btn_text": "text-white",
        "badge_color": "bg-[#0f1d27]",
        "shadow": "shadow-[0_30px_70px_-20px_rgba(0,0,0,0.22)]",
    },
    {
        "bg_gradient": "from-[#fff2d6] via-[#fae6bc] to-[#f3daa3]",
        "border": "border-[#edd194]/50",
        "text_color": "text-[#1a1a1f]",
        "glow_1": "bg-white/40",
        "glow_2": "bg-amber-300/20",
        "btn_bg": "bg-[#1a1a1f] hover:bg-[#2d2d35]",
        "btn_text": "text-white",
        "badge_color": "bg-amber-600",
        "shadow": "shadow-[0_35px_80px_-20px_rgba(237,209,148,0.45)]",
    },
    {
        "bg_gradient": "from-[#ebe6f2] via-[#ddd4e6] to-[#cfc2da]",
        "border": "border-[#c2b3cf]/50",
        "text_color": "text-[#1d1428]",
        "glow_1": "bg-white/35",
        "glow_2": "bg-purple-300/20",
        "btn_bg": "bg-[#1d1428] hover:bg-[#2d203e]",
        "btn_text": "text-white",
        "badge_color": "bg-[#1d1428]",
        "shadow": "shadow-[0_35px_80px_-20px_rgba(194,179,207,0.45)]",
    },
]


def home(request):
    raw_categories = Category.objects.prefetch_related("products").all()

    showcase_categories = []
    total_cats = raw_categories.count()
    for idx, cat in enumerate(raw_categories):
        theme = CATEGORY_THEMES[idx % len(CATEGORY_THEMES)]
        cat_products = list(cat.products.all())

        # Marquee için en az 6 ürün kartı olacak şekilde döngü listesi
        repeated_list = []
        if cat_products:
            while len(repeated_list) < 6:
                repeated_list.extend(cat_products)

        showcase_categories.append({
            "category": cat,
            "theme": theme,
            "products": repeated_list,
            "has_products": bool(cat_products),
            "index": idx,
            "index_display": f"{idx + 1:02d}",
            "direction": "left" if idx % 2 == 0 else "right",
        })

    context = {
        "categories": raw_categories,
        "showcase_categories": showcase_categories,
        "total_categories_display": f"{total_cats:02d}",
        "featured_products": (
            Product.objects.filter(is_featured=True).select_related("category")[:8]
        ),
    }
    return render(request, "home.html", context)


def product_list(request, slug=None):
    """Tüm ürünler veya tek kategori; ?q= ile model kodu / ad araması."""
    category = get_object_or_404(Category, slug=slug) if slug else None
    products = Product.objects.select_related("category")
    if category:
        products = products.filter(category=category)

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(model_code__icontains=query) | Q(name__icontains=query)
        )
    products = products.order_by("model_code")

    page = Paginator(products, 12).get_page(request.GET.get("page"))
    # Sayfalama linklerinde q parametresini korumak için
    return render(request, "urunler.html", {
        "category": category,
        "categories": Category.objects.all(),
        "page": page,
        "query": query,
        "total": page.paginator.count,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk)
    related = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk).select_related("category")[:4]
    )
    return render(request, "urun_detay.html", {"product": product, "related": related})


def contact(request):
    if request.method == "POST":
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Talebiniz alındı. En kısa sürede sizinle iletişime geçeceğiz.")
            return redirect("core:contact")
    else:
        # Ürün sayfasından gelindiğinde ?urun= ile ürün alanını önceden doldur
        form = ContactInquiryForm(initial={"product_interest": request.GET.get("urun", "")})
    return render(request, "iletisim.html", {"form": form})


def about(request):
    return render(request, 'hakkimizda.html')
