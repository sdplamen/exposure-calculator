from django.http import JsonResponse
from django.shortcuts import render
from calculator.service import calculate
from .forms import ExposureForm


# ---------- HTML pages (DTL) ----------
def index(request):
    form = ExposureForm(request.GET or None)
    result = calculate(form.cleaned_data) if form.is_valid() else None
    return render(request, "calculator/index.html", {"form": form, "result": result})

def about(request):
    return render(request, "calculator/about.html")

# ---------- JSON API ----------
def api_exposure(request):
    form = ExposureForm(request.GET)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)
    return JsonResponse(calculate(form.cleaned_data))