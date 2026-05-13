import unittest

from aio_reports.markdown import escape_markdown_cell


class TestMarkdown(unittest.TestCase):
    def test_escape_pipe(self):
        self.assertEqual(escape_markdown_cell("A|B"), "A\\|B")


if __name__ == "__main__":
    unittest.main()
