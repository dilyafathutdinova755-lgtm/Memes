"""
Estimate the needed drop-shadow intensity for white hook text over a photo.

Replicates ffmpeg's crop-to-fill (scale to cover 1080x1920, center-crop),
samples the region where the hook text block will actually sit, and scores
it on:
  - mean brightness (bright backgrounds wash out white text -> need darker shadow)
  - local contrast/"busyness" (edges under the text reduce legibility regardless
    of brightness -> also need a stronger shadow)

Maps the combined score to a shadowcolor alpha in [0.12, 0.50].
"""
import sys
from PIL import Image, ImageFilter
import numpy as np

TARGET_W, TARGET_H = 1080, 1920

def crop_to_fill(im, tw=TARGET_W, th=TARGET_H):
    w, h = im.size
    scale = max(tw / w, th / h)
    nw, nh = round(w * scale), round(h * scale)
    im2 = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im2.crop((left, top, left + tw, top + th))

def analyze(path, box_w=1000, box_h=820):
    im = Image.open(path).convert("RGB")
    im = crop_to_fill(im)
    cx, cy = TARGET_W // 2, TARGET_H // 2
    left = cx - box_w // 2
    top = cy - box_h // 2
    region = im.crop((left, top, left + box_w, top + box_h))

    gray = np.asarray(region.convert("L"), dtype=np.float64)
    mean_brightness = gray.mean()  # 0-255

    # local contrast via edge magnitude (busyness under the text)
    edges = region.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_arr = np.asarray(edges, dtype=np.float64)
    busyness = edge_arr.mean()  # roughly 0-60 typical range for photos

    brightness_term = mean_brightness / 255.0          # 0..1
    busyness_term = min(busyness / 40.0, 1.0)           # 0..1, saturates around 40

    score = 0.55 * brightness_term + 0.45 * busyness_term
    alpha = 0.12 + score * 0.38  # map score 0..1 -> alpha 0.12..0.50
    alpha = max(0.12, min(0.50, alpha))

    return {
        "path": path,
        "mean_brightness": round(mean_brightness, 1),
        "busyness": round(busyness, 1),
        "score": round(score, 3),
        "shadow_alpha": round(alpha, 2),
    }

if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = analyze(p)
        print(f"{r['path']}: brightness={r['mean_brightness']} busyness={r['busyness']} "
              f"score={r['score']} -> shadow_alpha={r['shadow_alpha']}")
