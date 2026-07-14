import importlib.util
import unittest
from pathlib import Path


class MobilePageFallbackTests(unittest.TestCase):
    def test_mobile_page_fallback_runs_when_renderer_raises(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        spec = importlib.util.spec_from_file_location("app_under_test", app_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        calls = []

        def failing_renderer():
            raise RuntimeError("boom")

        def fallback_renderer():
            calls.append("fallback")

        result = module.run_mobile_page_with_fallback(
            "Escalas",
            failing_renderer,
            fallback_renderer,
        )

        self.assertFalse(result)
        self.assertEqual(calls, ["fallback"])


if __name__ == "__main__":
    unittest.main()
