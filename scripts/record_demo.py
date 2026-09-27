"""Record the README demo GIF by driving the app in a headless browser.

    uv run python -m betting_dashboard.app          # in one terminal (serves :8050)
    uv run --group demo playwright install chromium # once
    uv run --group demo python scripts/record_demo.py

Options: --url (default http://localhost:8050), --out (default docs/demo.gif),
--chromium PATH (use an existing Chromium instead of Playwright's download).

Frames are captured losslessly with Chrome's screencast API, which emits a frame only when
the page changes, so static stretches cost almost nothing. ffmpeg (bundled by imageio-ffmpeg)
then assembles them into a palette-optimised GIF.
"""

from __future__ import annotations

import argparse
import base64
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
VIEWPORT = {"width": 1280, "height": 720}


def pause(page: Page, ms: int) -> None:
    page.wait_for_timeout(ms)


def scroll(page: Page, pixels: int, steps: int = 12) -> None:
    for _ in range(steps):
        page.mouse.wheel(0, pixels / steps)
        pause(page, 40)


def pick(page: Page, dropdown_id: str, text: str) -> None:
    """Choose an option in a Dash dropdown: open it, search, select the match, close."""
    page.click(f"#{dropdown_id}")
    # Single-selects with a value focus the selected option, so focus the search box.
    page.locator(".dash-dropdown-search").first.click()
    page.keyboard.type(text, delay=60)
    page.locator(".dash-dropdown-option", has_text=text).first.wait_for()
    pause(page, 500)
    page.keyboard.press("Enter")
    pause(page, 300)
    page.keyboard.press("Escape")


def open_overview(page: Page, url: str) -> None:
    page.goto(url)
    page.wait_for_selector("#ov-kpis .kpi")
    page.wait_for_selector("#ov-cumulative .main-svg")


def tour(page: Page) -> None:
    pause(page, 2200)

    # Recommended strategy -> all picks -> back, with the slider's keyboard control.
    handle = page.locator("#ov-edge [role=slider]").first
    handle.focus()
    for _ in range(5):
        page.keyboard.press("ArrowLeft")
        pause(page, 250)
    pause(page, 1600)
    for _ in range(5):
        page.keyboard.press("ArrowRight")
        pause(page, 250)
    pause(page, 1400)
    scroll(page, 620)
    pause(page, 2000)

    page.click("a.nav-link[href='/predictions']")
    page.wait_for_selector("#pred-archive .ag-row", state="attached")
    pause(page, 1500)
    scroll(page, 1500, steps=18)
    pause(page, 1200)
    page.locator("#pred-archive").scroll_into_view_if_needed()
    page.click("label[for=pred-recommended]")
    pause(page, 1300)
    page.click("label[for=pred-recommended]")
    pause(page, 1300)

    page.click("a.nav-link[href='/explorer']")
    page.wait_for_selector("#ex-trend .main-svg")
    pause(page, 1500)
    pick(page, "ex-leagues", "EuroLeague")
    pause(page, 2200)

    page.click("a.nav-link[href='/teams']")
    page.wait_for_selector("#tm-kpis .kpi")
    pause(page, 1000)
    pick(page, "tm-team", "Real Madrid")
    pause(page, 2600)


class Screencast:
    """Collect lossless PNG frames (with timestamps) from Chrome's screencast."""

    def __init__(self, page: Page, folder: Path) -> None:
        self.folder = folder
        self.frames: list[tuple[Path, float]] = []
        self.cdp = page.context.new_cdp_session(page)
        self.cdp.on("Page.screencastFrame", self._on_frame)

    def _on_frame(self, event: dict) -> None:
        path = self.folder / f"frame_{len(self.frames):05d}.png"
        path.write_bytes(base64.b64decode(event["data"]))
        self.frames.append((path, event["metadata"]["timestamp"]))
        self.cdp.send("Page.screencastFrameAck", {"sessionId": event["sessionId"]})

    def start(self) -> None:
        self.cdp.send(
            "Page.startScreencast",
            {"format": "png", "maxWidth": VIEWPORT["width"], "maxHeight": VIEWPORT["height"]},
        )

    def stop(self, page: Page) -> None:
        pause(page, 300)  # let the last frames arrive
        self.cdp.send("Page.stopScreencast")

    def write_concat_list(self, hold_last: float = 1.5) -> Path:
        """An ffmpeg concat list where each frame lasts until the next one arrived."""
        lines = []
        for (path, ts), (_, next_ts) in zip(self.frames, self.frames[1:], strict=False):
            lines += [f"file '{path}'", f"duration {max(next_ts - ts, 0.01):.3f}"]
        last = self.frames[-1][0]
        lines += [f"file '{last}'", f"duration {hold_last}", f"file '{last}'"]
        listing = self.folder / "frames.txt"
        listing.write_text("\n".join(lines) + "\n")
        return listing


def to_gif(frames: Path, out: Path, fps: int, width: int) -> None:
    ffmpeg = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error"]
    source = ["-f", "concat", "-safe", "0", "-i", str(frames)]
    scale = f"fps={fps},scale={width}:-1:flags=lanczos"
    palette = frames.parent / "palette.png"
    make_palette = f"{scale},palettegen=max_colors=128:stats_mode=diff"
    subprocess.run([*ffmpeg, *source, "-vf", make_palette, str(palette)], check=True)
    use_palette = "paletteuse=dither=none:diff_mode=rectangle"
    filters = ["-lavfi", f"{scale}[x];[x][1:v]{use_palette}"]
    subprocess.run([*ffmpeg, *source, "-i", str(palette), *filters, str(out)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", default="http://localhost:8050")
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "demo.gif")
    parser.add_argument("--chromium", help="path to a Chromium executable")
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--width", type=int, default=960)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium)
        page = browser.new_page(viewport=VIEWPORT)
        open_overview(page, args.url.rstrip("/"))
        cast = Screencast(page, Path(tmp))
        cast.start()
        tour(page)
        cast.stop(page)
        browser.close()
        to_gif(cast.write_concat_list(), args.out, args.fps, args.width)

    size_mb = args.out.stat().st_size / 1e6
    print(f"wrote {args.out} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
