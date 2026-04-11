import os

from colorama import Fore

from engines.character_importer import import_character


def main():
    """Simple script to import cards from a file or directory."""
    def _import_card(args):
        """Imports a character card (PNG, WEBP or JSON) from SillyTavern format."""
        if not args:
            print(Fore.RED + "[ERROR] Usage: //import <path_to_card_png_or_json>")
            return

        path = args.strip().strip('"').strip("'")
        if not os.path.exists(path):
            print(Fore.RED + f"[ERROR] File not found: {path}")
            return

        import_character(path)

    def _batch_import(args):
        """Imports all character cards from a directory."""
        if not args:
            print(Fore.RED + "[ERROR] Usage: //batch_import <directory_path>")
            return

        dir_path = args.strip().strip('"').strip("'")
        if not os.path.isdir(dir_path):
            print(Fore.RED + f"[ERROR] Directory not found: {dir_path}")
            return

        files = [f for f in os.listdir(dir_path) if f.lower().endswith((".png", ".webp", ".json"))]
        if not files:
            print(Fore.YELLOW + f"[INFO] No valid character files found in {dir_path}")
            return

        print(Fore.CYAN + f"[SYSTEM] Found {len(files)} potential cards. Starting batch import...")
        success_count = 0
        for f in files:
            full_path = os.path.join(dir_path, f)
            print(Fore.WHITE + f" -> Importing {f}...")
            if import_character(full_path):
                success_count += 1
        
        print(Fore.GREEN + f"\n[SUCCESS] Batch import complete. {success_count}/{len(files)} characters imported.")

    print(Fore.GREEN + "Card Importer is ready.")
    print(Fore.CYAN + "Commands:")
    print(Fore.CYAN + "  //import <path>        - Import a single character card (PNG/WEBP/JSON)")
    print(Fore.CYAN + "  //batch_import <dir>   - Import all cards from a directory")
    print(Fore.CYAN + "  Ctrl+C                 - Exit")

    try:
        while True:
            user_input = input("\nEnter command: ").strip()
            if not user_input:
                continue

            if user_input.startswith("//batch_import"):
                _batch_import(user_input[len("//batch_import"):].strip())
            elif user_input.startswith("//import"):
                _import_card(user_input[len("//import"):].strip())
            else:
                print(Fore.RED + "[ERROR] Unknown command. Use //import <path> or //batch_import <dir>.")
    except KeyboardInterrupt:
        print("\nExiting Card Importer.")

    except Exception as e:
        print(f"{Fore.RED}[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
