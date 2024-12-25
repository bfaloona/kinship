from invoke import task


@task
def lint(c):
    c.run("ruff check")

@task
def cov(c):
    c.run("pytest --cov-branch --cov-report=html --cov=kinship .")

@task(lint)
def test(c):
    c.run("pytest -v -rA --strict-config --html=results.html --self-contained-html")

@task
def parse(c, path):
    c.run(f"python main.py parse {path}")

@task
def load(c):
    c.run("python main.py load")

@task
def venv(c):
    c.run("python3.13 -m venv venv")
    print("Now run 'source venv/bin/activate' to activate the virtual environment.")


@task
def install(c):
    print("assuming you are already have your venv active...")
    c.run("pip install -r requirements.txt")