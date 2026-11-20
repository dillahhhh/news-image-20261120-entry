# news-image-20261120 — The World in One Day

make.fun competition entry: one image summing up the world's news of
Friday, 20 November 2026. A front-page broadsheet: masthead date,
ICJ genocide ruling as the lead, then Trump–Xi–Putin summit in Shenzhen,
Russia's Kyiv strikes reaching Polish airspace, Anthropic's Nasdaq debut
(+17%) against sliding global stocks (Nikkei −5.1%, S&P 500 −2.0%, sixth
straight daily loss), the Houthi missile on Riyadh's PIF tower,
GTA 6's estimated $2.36B day-one sales (Sensor Tower estimate), and
global public debt nearing 95% of GDP (IMF 2026 projections, 94.6%).

All text is drawn with PIL (DejaVu Sans) onto flat vector art — no
AI-generated text anywhere, so nothing is garbled. The flat-vector
illustrations in `assets/` were generated text-free and composited in;
the market chart, gamepad, tower and debt-bars icons are drawn in code.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# -> out/entry.png (1024x1024, deterministic, byte-identical every run)
```

`build_image.py` regenerates `entry.png` from `assets/` (needs Pillow).
`main.py` is standard library only and just copies the PNG.

## License

MIT — see LICENSE.
