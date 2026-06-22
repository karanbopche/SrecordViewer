@echo off
python -m pip install uv
python -m uv init --bare --python=3.11 -q
for %%A in (*.whl) do (
    python -m uv add %%~nxA
)
python -m uv run image_viewer
