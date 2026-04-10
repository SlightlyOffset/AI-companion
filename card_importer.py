import os

from colorama import Fore

from engines.character_importer import import_character


def main():
    """Simple script to import cards from a file."""
    def _import_card(args):
        """Imports a character card (PNG or JSON) from SillyTavern format."""
        if not args:
            print(Fore.RED + "[ERROR] Usage: //import_card <path_to_card_png_or_json>")
            return

        path = args.strip().strip('"').strip("'")
        if not os.path.exists(path):
            print(Fore.RED + f"[ERROR] File not found: {path}")
            return

        import_character(path)

    print(Fore.GREEN + "Card Importer is ready. Use //import <path_to_card> to import a character card.")

    try:
        while True:
            user_input = input("Enter command: ")
            if user_input.startswith("//import"):
                _import_card(user_input[len("//import"):].strip())
                print()
            else:
                print(Fore.RED + "[ERROR] Unknown command. Use //import_card <path_to_card> to import a character card.")
    except KeyboardInterrupt:
        print("\nExiting Card Importer.")

    except Exception as e:
        print(f"{Fore.RED}[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
