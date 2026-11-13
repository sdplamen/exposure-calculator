"""Standard 1/3-stop values found on real cameras."""
import math

APERTURES = [
    1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.5, 2.8, 3.2, 3.5, 4, 4.5, 5, 5.6,
    6.3, 7.1, 8, 9, 10, 11, 13, 14, 16, 18, 20, 22, 25, 29, 32,
]

SHUTTERS = [
    "30", "25", "20", "15", "13", "10", "8", "6", "5", "4", "3.2", "2.5", "2",
    "1.6", "1.3", "1", "0.8", "0.6", "0.5", "0.4", "0.3",
    "1/4", "1/5", "1/6", "1/8", "1/10", "1/13", "1/15", "1/20", "1/25", "1/30",
    "1/40", "1/50", "1/60", "1/80", "1/100", "1/125", "1/160", "1/200", "1/250",
    "1/320", "1/400", "1/500", "1/640", "1/800", "1/1000", "1/1250", "1/1600",
    "1/2000", "1/2500", "1/3200", "1/4000", "1/5000", "1/6400", "1/8000",
]

ISOS = [
    50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250,
    1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000,
    20000, 25600,
]


def _nearest(value: float, options, key=float):
    """Closest option on a log scale (in stops), not in plain numbers."""
    return min(options, key=lambda o: abs(math.log2(key(o)) - math.log2(value)))


def nearest_aperture(n: float) -> float:
    return _nearest(n, APERTURES)


def nearest_shutter(seconds: float) -> str:
    from calculator.core import parse_shutter
    return _nearest(seconds, SHUTTERS, key=parse_shutter)


def nearest_iso(iso: float) -> int:
    return _nearest(iso, ISOS)