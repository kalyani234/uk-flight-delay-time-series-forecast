import subprocess
import sys

def run(module_name: str):
    print("\n==============================")
    print("RUN:", module_name)
    print("==============================")
    subprocess.run([sys.executable, "-m", module_name], check=True)

def main():
    run("src.models.train_baseline")
    run("src.models.train_xgb")
    run("src.models.train_sarima")

if __name__ == "__main__":
    main()
