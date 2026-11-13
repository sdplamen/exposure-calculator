from django.http import JsonResponse
from django.shortcuts import render
from calculator.core import ev100, format_shutter, parse_shutter, solve_missing
from calculator.stops import nearest_aperture, nearest_iso, nearest_shutter
from .forms import ExposureForm


def calculate(data: dict) -> dict:
    """Light (EV) + two settings -> the third. Shared by the web page and the API."""
    ev = data["light"]
    r = solve_missing(ev, aperture=data["aperture"], shutter=data["shutter"], iso=data["iso"])

    # Round only the calculated value to a real camera setting.
    camera = dict(r)
    if data["aperture"] is None:
        solved = "aperture"
        camera["aperture"] = nearest_aperture(r["aperture"])
    elif data["shutter"] is None:
        solved = "shutter"
        camera["shutter"] = parse_shutter(nearest_shutter(r["shutter"]))
    else:
        solved = "iso"
        camera["iso"] = nearest_iso(r["iso"])

    # + means more light than the meter wants (brighter photo)
    stops_off = round(ev - ev100(camera["aperture"], camera["shutter"], camera["iso"]), 2)

    return {
        "ev100": ev,
        "solved": solved,
        "exact": {
            "aperture": round(r["aperture"], 1),
            "shutter": format_shutter(r["shutter"]),
            "iso": round(r["iso"]),
        },
        "camera": {
            "aperture": camera["aperture"],
            "shutter": format_shutter(camera["shutter"]),
            "iso": round(camera["iso"]),
        },
        "stops_off": stops_off,
        # Rounding moved it more than half a stop: the camera can't reach it
        "out_of_range": abs(stops_off) > 0.5,
    }

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