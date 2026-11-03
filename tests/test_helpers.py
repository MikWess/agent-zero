import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

from agent_zero.calculator import calculator

spec = importlib.util.spec_from_file_location("memory", Path(__file__).resolve().parents[1] / "examples/04_memory_agent/memory.py")
memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory)


class HelpersTest(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(calculator("(144 / 12) + 7 * 8"), "68.0")
        self.assertEqual(calculator("-5 + 12 // 2"), "1")

    def test_non_arithmetic_and_unbounded_values_are_rejected(self):
        for expression in ["(1).__class__", "__import__('os')", "2 ** 1000000", "True", "1 / 0", "1e999", "1+" * 200]:
            with self.subTest(expression=expression):
                self.assertTrue(calculator(expression).startswith("Error:"))

    def test_memory_with_bare_filename_and_unicode(self):
        with tempfile.TemporaryDirectory() as root:
            previous = Path.cwd()
            try:
                os.chdir(root)
                memory.save_memory("MEMORY.md", "café")
                memory.append_memory("MEMORY.md", "日本語")
                self.assertIn("café", memory.load_memory("MEMORY.md"))
                self.assertIn("日本語", memory.load_memory("MEMORY.md"))
                memory.append_memory("new/nested.md", "remember this")
                self.assertIn("remember this", memory.load_memory("new/nested.md"))
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
