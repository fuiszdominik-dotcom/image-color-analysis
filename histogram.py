import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def create_hsv_histogram(image_path, output_dir="histograms"):

    os.makedirs(output_dir, exist_ok=True)

    image = Image.open(image_path).convert('RGB')
    image = image.resize((150, 150))

    # RGB → HSV átalakítás
    hsv_image = image.convert('HSV')
    hsv_array = np.array(hsv_image)
    h, s, v = hsv_array[:, :, 0], hsv_array[:, :, 1], hsv_array[:, :, 2]

    h = (h / 255) * 360
    s = (s / 255) * 100
    v = (v / 255) * 100

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={'hspace': 0.4}, sharey=False)
    ax1.hist(s.flatten(), bins=50, alpha=0.5, color='orange', label='S – Telítettség')
    ax1.hist(v.flatten(), bins=50, alpha=0.5, color='gray', label='V – Fényesség')
    ax1.set_xlim(0, 100)
    ax1.set_xticks(np.arange(0, 101, 5))
    ax1.set_xlabel("Érték (%)")
    ax1.set_ylabel("Pixelek száma")
    ax1.set_title("S és V eloszlása")
    ax1.legend()

    ax2.hist(h.flatten(), bins=60, color='blue', label='H – Színárnyalat')
    ax2.set_xlim(0, 360)
    ax2.set_xticks(np.arange(0, 361, 25))
    ax2.set_xlabel("Érték (Fok)")
    ax2.set_ylabel("Pixelek száma")
    ax2.set_title("Hue (H) eloszlása")
    ax2.legend()

    output_path = os.path.join(output_dir, f"hisztogram_{os.path.basename(image_path)}.png")
    fig.savefig(output_path, bbox_inches='tight')
    plt.close(fig)

    return output_path
