from django.conf import settings


def site_info(request):
    """Tüm template'lerde kullanılabilen iletişim bilgileri."""
    return {
        "whatsapp_number": getattr(settings, "WHATSAPP_NUMBER", "905334197894"),
        "site_phone": getattr(settings, "SITE_PHONE", "+90 531 880 86 54"),
        "site_phone_2": getattr(settings, "SITE_PHONE_2", "+90 533 419 78 94"),
        "contact_1_name": getattr(settings, "CONTACT_PERSON_1_NAME", "Ekrem Özdemir"),
        "contact_1_phone": getattr(settings, "CONTACT_PERSON_1_PHONE", "0531 880 86 54"),
        "contact_1_intl": getattr(settings, "CONTACT_PERSON_1_INTL", "+90 531 880 86 54"),
        "contact_1_raw": getattr(settings, "CONTACT_PERSON_1_RAW", "905318808654"),
        "contact_2_name": getattr(settings, "CONTACT_PERSON_2_NAME", "Nur Özdemir"),
        "contact_2_phone": getattr(settings, "CONTACT_PERSON_2_PHONE", "0533 419 78 94"),
        "contact_2_intl": getattr(settings, "CONTACT_PERSON_2_INTL", "+90 533 419 78 94"),
        "contact_2_raw": getattr(settings, "CONTACT_PERSON_2_RAW", "905334197894"),
        "site_email": getattr(settings, "SITE_EMAIL", "info@ekometal.com"),
        "site_address": getattr(settings, "SITE_ADDRESS", "Muratpaşa, 14. Blok Sk. 6 /1, 34040 Bayrampaşa/İstanbul"),
        "site_instagram": getattr(settings, "SITE_INSTAGRAM", "https://www.instagram.com/nurscraft2025?psln=MW42eDFzZmgzdTlhNg%3D%3D"),
    }
