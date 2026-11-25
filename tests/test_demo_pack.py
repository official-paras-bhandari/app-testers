"""scripts/demo_pack.py: only what the online demo needs leaves a run."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import demo_pack  # noqa: E402


class DemoPackTest(unittest.TestCase):
    def test_only_screens_traces_and_short_findings_are_copied(self):
        run = Path(tempfile.mkdtemp()) / "run"
        tester = run / "android-anna" / "results" / "anna"
        tester.mkdir(parents=True)
        (tester / "trace.json").write_text('{"schema": "ecr.trace/0", "steps": []}')
        for name in ("01.png", "01.xml", "01.saliency.json", "trace.params.json", "report.md", "actions.tsv", "tree-3.xml"):
            (tester / name).write_text("x")
        (tester / "findings.json").write_text(json.dumps({"score": 6, "issues": [
            {"title": "Cut text", "severity": "minor", "screens": ["01"], "steps": "private notes"}], "notes": "private"}))
        (run / "android-anna" / "results" / "agent-output.json").write_text("{}")
        out = Path(tempfile.mkdtemp()) / "demo-data"
        self.assertEqual(demo_pack.pack([run], out, "https://github.com/localsend/localsend"), 1)
        kept = out / "android-anna" / "results" / "anna"
        self.assertEqual(sorted(f.name for f in kept.iterdir()),
                         ["01.png", "01.saliency.json", "01.xml", "findings.json", "trace.json"])
        self.assertEqual(json.loads((kept / "findings.json").read_text()),
                         {"score": 6, "issues": [{"title": "Cut text", "severity": "minor", "screens": ["01"]}]})
        self.assertFalse(list(out.rglob("agent-output.json")))
        self.assertIn("localsend", (out / "SOURCE.md").read_text())


if __name__ == "__main__":
    unittest.main()
