import cv2
import numpy as np

_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB — Claude API hard limit
_MAX_LONG_EDGE = 1568


class PreprocessingPipeline:
    """Resize image bytes to fit Claude's API limits and return JPEG bytes."""

    def run(self, image_bytes: bytes) -> bytes:
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image bytes — unsupported or corrupt format")
        img = self._resize(img)
        return self._encode(img)

    def _resize(self, img: np.ndarray) -> np.ndarray:
        h, w = img.shape[:2]
        long_edge = max(h, w)
        if long_edge <= _MAX_LONG_EDGE:
            return img
        scale = _MAX_LONG_EDGE / long_edge
        return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    def _encode(self, img: np.ndarray) -> bytes:
        for quality in range(95, 5, -5):
            success, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
            if success and len(buf) <= _MAX_FILE_SIZE:
                return buf.tobytes()
        _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 10])
        return buf.tobytes()
