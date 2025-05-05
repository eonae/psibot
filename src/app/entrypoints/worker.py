import subprocess


def main():
    subprocess.run(
        [
            "celery",
            "-A", "src.app.adapters.my_celery.singleton",
            "worker",
            "-l", "DEBUG"
        ],
        check=True,
    )
