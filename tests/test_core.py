import base64
import json
import tempfile
import unittest
from pathlib import Path
from reviewer.core import Config, ReviewError, build_request, parse_response, run_review, usage_summary, validate_pdf, MAX_PDF_BYTES

PDF = b"%PDF-1.4\nmock test payload only"
CFG = Config("test-model")
KEY = "test-secret-not-real"


def completed(body, key, timeout):
    assert key == KEY
    assert body["store"] is False
    return {"id": "resp_test", "model": "test-model-snapshot", "status": "completed", "output": [
        {"type": "reasoning"}, {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "# Review\nEvidence."}]}],
        "usage": {"input_tokens": 100, "output_tokens": 50, "output_tokens_details": {"reasoning_tokens": 20}, "total_tokens": 150}}


class TestCore(unittest.TestCase):
    def test_pdf_full_bytes(self):
        req = build_request(PDF, "review", CFG)
        part = req["input"][0]["content"][0]
        self.assertEqual(base64.b64decode(part["file_data"].split(",", 1)[1]), PDF)
        self.assertEqual(part["filename"], "manuscript.pdf")
        self.assertNotIn("tools", req)
        self.assertNotIn(KEY, json.dumps(req))
        self.assertEqual(req["reasoning"]["effort"], "high")

    def test_default_effort(self):
        self.assertNotIn("reasoning", build_request(PDF, "p", Config("m", effort="default")))

    def test_invalid_pdf(self):
        with self.assertRaises(ReviewError): validate_pdf(b"not pdf")
        with self.assertRaises(ReviewError): validate_pdf(b"%PDF-" + b"a" * MAX_PDF_BYTES)

    def test_empty_prompt(self):
        with self.assertRaises(ReviewError): build_request(PDF, " ", CFG)

    def test_invalid_config(self):
        for cfg in [Config(""), Config("m", effort="nonsense"), Config("m", max_output_tokens=0), Config("m", input_rate=float("nan"), output_rate=1), Config("m", input_rate=1)]:
            with self.assertRaises(ReviewError): cfg.validate()

    def test_no_consent_no_call(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ReviewError): run_review(PDF, "p", CFG, KEY, Path(d), transport=lambda *a: self.fail("paid call"))
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_missing_key_no_call(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ReviewError): run_review(PDF, "p", CFG, "", Path(d), authorized=True, transport=lambda *a: self.fail("paid call"))

    def test_completed_and_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            path, meta = run_review(PDF, "p", CFG, KEY, Path(d), authorized=True, transport=completed)
            self.assertEqual(meta["status"], "completed")
            self.assertEqual(meta["actual_model"], "test-model-snapshot")
            self.assertEqual(meta["usage"]["reasoning_tokens"], 20)
            self.assertTrue((path / "review.md").exists())
            for f in path.iterdir(): self.assertNotIn(KEY, f.read_text())
            self.assertNotIn("mock test payload", (path / "result.json").read_text())

    def test_incomplete_is_not_success(self):
        def partial(*args):
            r = completed(*args)
            r.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
            return r
        with tempfile.TemporaryDirectory() as d:
            path, meta = run_review(PDF, "p", CFG, KEY, Path(d), authorized=True, transport=partial)
            self.assertEqual(meta["status"], "incomplete_or_failed")
            self.assertEqual(meta["incomplete_reason"], "max_output_tokens")
            self.assertTrue((path / "partial.md").exists())
            self.assertFalse((path / "review.md").exists())

    def test_no_automatic_retry(self):
        calls = []
        def fail(*args):
            calls.append(1)
            raise ReviewError("timeout")
        with tempfile.TemporaryDirectory() as d:
            path, meta = run_review(PDF, "p", CFG, KEY, Path(d), authorized=True, transport=fail)
            self.assertEqual(len(calls), 1)
            self.assertEqual(meta["usage"]["status"], "unknown")
            self.assertEqual(meta["status"], "request_failed")
            self.assertFalse((path / "review.md").exists())

    def test_refusal_empty(self):
        self.assertEqual(parse_response({"status": "completed", "output": []})[0], "refused_or_empty")
        self.assertEqual(parse_response({"status": "completed", "output": [{"type": "message", "role": "assistant", "content": [{"type": "refusal", "refusal": "no"}]}]})[0], "refused_or_empty")

    def test_cost_explicit_rates(self):
        r = completed({"store": False}, KEY, 1)
        self.assertIsNone(usage_summary(r, CFG)["estimated_usd"])
        self.assertAlmostEqual(usage_summary(r, Config("m", input_rate=2, output_rate=8))["estimated_usd"], .0006)

    def test_missing_usage(self):
        self.assertEqual(usage_summary({}, CFG)["status"], "unknown")


if __name__ == "__main__": unittest.main()
