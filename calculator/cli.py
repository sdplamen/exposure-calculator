import argparse
from calculator.core import ev100, format_shutter, parse_shutter, solve_shutter

def main():
    p = argparse.ArgumentParser(description="Keep the same exposure while changing one setting.")
    p.add_argument("aperture", type=float)
    p.add_argument("shutter", type=parse_shutter)
    p.add_argument("iso", type=float)
    p.add_argument("--new-aperture", type=float)
    p.add_argument("--new-iso", type=float)
    a = p.parse_args()

    ev = ev100(a.aperture, a.shutter, a.iso)
    aperture = a.new_aperture or a.aperture
    iso = a.new_iso or a.iso
    print(f"EV100 = {ev:.2f}")
    print(f"Equivalent: f/{aperture:g}  {format_shutter(solve_shutter(ev, aperture, iso))}  ISO {iso:g}")