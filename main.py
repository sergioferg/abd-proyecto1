import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="StreamUCV D/D")
    parser.add_argument("usuario", type=str, help="Nombre de usuario de SQLServer")
    args = parser.parse_args()
    
    print(args.usuario)

if __name__ == "__main__":
    main()