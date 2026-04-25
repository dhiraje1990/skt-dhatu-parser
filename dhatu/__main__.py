import argparse
import sys
from dhatu import conjugate, analyse, krdanta

def main():
    parser = argparse.ArgumentParser(description="Sanskrit Verb (Dhatu) Parser CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Conjugate Command
    conj_parser = subparsers.add_parser("conjugate", help="Conjugate a dhatu")
    conj_parser.add_argument("dhatu", help="Root dhatu in HK (e.g., pac)")
    conj_parser.add_argument("-l", "--lakara", default="lat", help="Lakara (default: lat)")
    conj_parser.add_argument("-p", "--pada", default="parasmai", help="parasmai | atmane | both")
    conj_parser.add_argument("-u", "--upasarga", nargs="*", default=[], help="List of upasargas")

    # Analyse Command
    ana_parser = subparsers.add_parser("analyse", help="Analyse a conjugated form")
    ana_parser.add_argument("form", help="Conjugated form in HK (e.g., pacati)")

    # Krdanta Command
    krd_parser = subparsers.add_parser("krdanta", help="Get krdanta forms")
    krd_parser.add_argument("dhatu", help="Root dhatu in HK")
    krd_parser.add_argument("-s", "--suffix", default="all", help="Suffix name or 'all'")
    krd_parser.add_argument("-u", "--upasarga", nargs="*", default=[], help="List of upasargas")

    args = parser.parse_args()

    if args.command == "conjugate":
        try:
            tbl = conjugate(args.dhatu, lakara=args.lakara, pada=args.pada, upasarga=args.upasarga)
            if isinstance(tbl, dict):
                for p, t in tbl.items():
                    print(f"\n--- {p.upper()} ---")
                    t.display()
            else:
                tbl.display()
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "analyse":
        results = analyse(args.form)
        if not results:
            print("No analysis found.")
        for r in results:
            print(f"\nType: {r.form_type.upper()}")
            print(f"Dhatu: {r.dhatu}")
            if r.upasarga: print(f"Upasarga: {r.upasarga}")
            if r.form_type == "tinanta":
                print(f"Grammar: {r.lakara}, {r.pada}, {r.puruSa}, {r.vacana}")
            else:
                print(f"Suffix: {r.suffix}")

    elif args.command == "krdanta":
        try:
            k = krdanta(args.dhatu, suffix=args.suffix, upasarga=args.upasarga)
            for s, forms in k.forms.items():
                print(f"{s:8}: {', '.join(forms)}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()