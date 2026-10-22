from django import forms

from .models import ContactInquiry

_INPUT = (
    "w-full rounded-xl border border-[#1c3527]/20 bg-cream-50/70 px-4 py-3.5 text-sm text-[#14281e] "
    "placeholder:text-[#1c3527]/40 focus:border-[#1c2d26] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#1c2d26]/10 transition-all duration-200"
)


class ContactInquiryForm(forms.ModelForm):
    # Honeypot: botlar doldurur, insanlar görmez
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "tabindex": "-1", "autocomplete": "off", "class": "hidden",
    }))

    class Meta:
        model = ContactInquiry
        fields = ["full_name", "company_name", "phone", "product_interest", "message"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Adınız Soyadınız", "autocomplete": "name"}),
            "company_name": forms.TextInput(attrs={"class": _INPUT, "placeholder": "İşletme / Restoran Adı", "autocomplete": "organization"}),
            "phone": forms.TextInput(attrs={"class": _INPUT, "placeholder": "05xx xxx xx xx", "type": "tel", "autocomplete": "tel"}),
            "product_interest": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Model kodu veya ürün adı"}),
            "message": forms.Textarea(attrs={"class": _INPUT, "rows": 5, "placeholder": "İhtiyacınızı, adedi ve teslimat bölgesini yazabilirsiniz"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = [c for c in phone if c.isdigit()]
        if len(digits) < 10:
            raise forms.ValidationError("Lütfen geçerli bir telefon numarası girin.")
        return phone

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Geçersiz istek.")
        return ""

    def save(self, commit=True):
        # 'website' modelde yok; ModelForm bunu zaten yok sayar
        return super().save(commit=commit)
