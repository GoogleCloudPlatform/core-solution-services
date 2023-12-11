import sys
import truss
from pathlib import Path
import os


def main():

    model_name = sys.argv[1]
    print(f"Generating Docker setup for {model_name}")
    tr = truss.load(os.path.join(os.path.dirname(__file__), f"../{model_name}"))
    tr.docker_build_setup(build_dir=Path(os.path.dirname(__file__), f"../{model_name}"))
    print(f"Done generating Docker setup for {model_name}")


if __name__ == "__main__":
    main()
