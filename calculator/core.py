import math

def ev100(aperture, shutter, iso):
    return math.log2(aperture**2 / shutter) - math.log2(iso / 100)

def solve_shutter(ev, aperture, iso):
    return aperture**2 / 2 ** (ev + math.log2(iso / 100))

def solve_aperture(ev, shutter, iso):
    return math.sqrt(shutter * 2 ** (ev + math.log2(iso / 100)))

def solve_iso(ev, aperture, shutter):
    return 100 * aperture**2 / (shutter * 2**ev)

def parse_shutter(text):          # "1/250" or "2"
    if "/" in text:
        num, den = text.split("/")
        return float(num) / float(den)
    return float(text)

def format_shutter(seconds: float) -> str:
    # From 0.3 s up, cameras show decimals (0.8s, 2.5s); faster speeds as fractions
    if seconds >= 0.3:
        return f"{round(seconds, 1):g}s"
    return f"1/{round(1 / seconds)}"

def solve_missing(ev, aperture=None, shutter=None, iso=None):
    """Give exactly two of the three settings; the third is calculated."""
    if [aperture, shutter, iso].count(None) != 1:
        raise ValueError("Fill in exactly two of: aperture, shutter, ISO")
    if aperture is None:
        aperture = solve_aperture(ev, shutter, iso)
    elif shutter is None:
        shutter = solve_shutter(ev, aperture, iso)
    else:
        iso = solve_iso(ev, aperture, shutter)
    return {"aperture": aperture, "shutter": shutter, "iso": iso}