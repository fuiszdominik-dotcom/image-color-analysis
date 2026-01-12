import os
from image_analyzer import analyze_folder


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def main_menu():
    while True:
        print("Kép Színelemző és Kategorizáló Rendszer \n")
        print("Mit szeretnél csinálni?\n")
        print("1 - Képek elemzése és kategorizálása (Excel + Becsült kategória)")
        print("2 - Kilépés\n")

        choice = input("Választásod (1/2): ").strip()

        if choice == "1":
            finished = run_analysis()
            if finished:
                print("\nProgram vége.")
                break
        elif choice == "2":
            print("\nKilépés...")
            break
        else:
            print("\nÉrvénytelen választás, próbáld újra!\n")


def run_analysis():
    """Képek elemzése + kategorizálás (hisztogram választható)."""
    print("\nKépek elemzése és kategorizálása")

    while True:
        folder = input("Add meg a képek mappáját (Enter = 'pictures'): ").strip()
        if not folder:
            folder = "pictures"

        if os.path.exists(folder):
            break
        else:
            print(f"\nA megadott mappa nem létezik: {folder}\n")
            print("Próbáld újra!\n")

    hist_input = input("Szeretnél hisztogramokat generálni? (y/n, Enter = n): ").strip().lower()
    generate_histograms = hist_input == "y"

    print(f"\nKépek feldolgozása ebből a mappából: {folder}")
    if generate_histograms:
        print("Hisztogram generálás: BEKAPCSOLVA (lassabb futás)\n")
    else:
        print("Hisztogram generálás: KIKAPCSOLVA (gyorsabb futás)\n")

    analyze_folder(folder, generate_histograms=generate_histograms)
    print("\nElemzés kész. A metaadatok a 'kep_szinelemzes_eredmenyek.xlsx' fájlban találhatók.\n")

    return True


if __name__ == "__main__":
    clear_screen()
    main_menu()
