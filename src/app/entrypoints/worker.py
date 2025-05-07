import subprocess


def main():
    subprocess.run(
        [
            "celery",
            "-A", "src.app.adapters.celery_runner.singleton",
            "worker",
            "-l", "DEBUG"
        ],
        check=True,
    )
