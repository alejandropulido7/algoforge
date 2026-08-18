import os
import io
import zipfile
from pathlib import Path

class CustomIndicatorsExporter:
    """Packages the official custom MT5 indicators (.mq5) from backend/indicators."""

    def __init__(self):
        # Base indicators folder located at backend/indicators
        self.indicators_dir = Path(__file__).resolve().parent.parent.parent / "indicators"

    def get_all_indicators(self) -> dict[str, str]:
        """Load all .mq5 indicator source files from backend/indicators."""
        files = {}
        if self.indicators_dir.exists():
            for root, _, filenames in os.walk(self.indicators_dir):
                for f in sorted(filenames):
                    if f.endswith(".mq5"):
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, self.indicators_dir)
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as file_handle:
                            files[rel_path] = file_handle.read()
        return files

    def get_zip_buffer(self) -> io.BytesIO:
        """Create a zip archive with all indicators placed in the AlgoForge/ folder."""
        indicators = self.get_all_indicators()
        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for rel_path, content in sorted(indicators.items()):
                # Normalize path with forward slashes for zip standard
                zip_path = f"AlgoForge/{rel_path.replace(os.sep, '/')}"
                zf.writestr(zip_path, content)
        mem_zip.seek(0)
        return mem_zip
