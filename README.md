# Sprite-Splitter

Web app used to split a "sprite sheet" into individual sprites.

## Backend

Simple fastapi API that downloads / uploads the image(s) and splits according to the parameters.

**roadmap**: 
- [ ] deploy

The python api is made using [uv](https://github.com/astral-sh/uv) as a python package and project manager.

If you wish to install locally, run:

1. Install it by following the [documentation](https://docs.astral.sh/uv/getting-started/installation/)
2. Install the corresponding python version with `uv python install 3.12`
3. Install the project `uv sync --all-extras --dev`
4. Run the API with `uv run app.py`

Else, you can use docker. Consider using [just](https://github.com/casey/just) to run the commands `just docker`.

## Frontend

Simple frontend made using a single html file.

**roadmap**:
- [ ] deploy

The frontend can be launched by simply opening the `index.html` file ;)

