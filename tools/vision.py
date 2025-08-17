from langchain.tools import tool
import base64
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io

@tool("VisionTool", return_direct=True)
def VisionTool(command: str) -> str:
    """
    An agentic tool for image analysis and plotting.

    - "analyze <image_path>": stats as dict
    - "histogram <image_path>": histogram plot as data URI (under 100KB)
    - Matplotlib code: returns plot as data URI (under 100KB)
    """
    command = command.strip()
    if command.startswith("analyze "):
        img_path = command.split(" ", 1)[1]
        try:
            img = Image.open(img_path)
            arr = np.array(img)
            stats = {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "shape": arr.shape,
                "mean_pixel": float(np.mean(arr)),
                "std_pixel": float(np.std(arr)),
                "min_pixel": int(np.min(arr)),
                "max_pixel": int(np.max(arr)),
            }
            return str(stats)
        except Exception as e:
            return f"Error analyzing image: {e}"
    elif command.startswith("histogram "):
        img_path = command.split(" ", 1)[1]
        try:
            img = Image.open(img_path)
            arr = np.array(img)
            plt.figure()
            if arr.ndim == 2:
                plt.hist(arr.flatten(), bins=256, color='gray')
            else:
                for i, col in enumerate(['r', 'g', 'b']):
                    plt.hist(arr[...,i].flatten(), bins=256, color=col, alpha=0.5)
            plt.title("Image Histogram")
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)
            data = base64.b64encode(buf.read()).decode()
            data_uri = "data:image/png;base64," + data
            if len(data_uri) > 100000:
                return "Histogram output too large."
            return data_uri
        except Exception as e:
            return f"Error generating histogram: {e}"
    else:
        buf = io.BytesIO()
        try:
            exec(command, globals())
            plt.savefig(buf, format="png", bbox_inches="tight")
            plt.close()
            buf.seek(0)
            data = base64.b64encode(buf.read()).decode()
            data_uri = "data:image/png;base64," + data
            if len(data_uri) > 100000:
                return "Plot image too large."
            return data_uri
        except Exception as e:
            return f"Error running plot code: {e}"
        finally:
            buf.close()
