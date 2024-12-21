from invoke import task


@task
def lint(c):
    c.run("ruff check")


@task
def cov(c):
    c.run("cd tests && pytest --cov=kinship .")


@task(lint)
def test(c):
    c.run("pytest --rich --strict-config")


@task
def parse(c, path):
    c.run(f"python main.py {path}")


@task
def venv(c):
    c.run("python3.9 -m venv venv")
    print("Now run 'source venv/bin/activate' to activate the virtual environment.")


@task
def install(c):
    print("assuming you are already have your venv active...")
    c.run("pip install -r requirements.txt")