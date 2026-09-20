import unittest

from jev.questions import THRESHOLDS, decide


def answers(lane="proceed", conf=0.9, risk=0.0, reversible=0.95, external=0.02, necessary=0.9, done=0.05, looping=0.05, specialist="none", spec_conf=0.9):
    return {
        "lane": {"type": "choice", "choice": lane, "confidence": conf, "probabilities": {lane: conf}},
        "risk": {"type": "score", "score": risk},
        "reversible": {"type": "noul", "noul": reversible},
        "external": {"type": "noul", "noul": external},
        "necessary": {"type": "noul", "noul": necessary},
        "done": {"type": "noul", "noul": done},
        "looping": {"type": "noul", "noul": looping},
        "specialist": {"type": "choice", "choice": specialist, "confidence": spec_conf, "probabilities": {specialist: spec_conf}},
    }


class DecideTests(unittest.TestCase):
    def test_safe_action_proceeds(self):
        self.assertEqual(decide(answers())["action"], "proceed")

    def test_done_skips_first(self):
        d = decide(answers(lane="proceed", done=0.9, external=0.9))
        self.assertEqual(d["action"], "skip")

    def test_external_needs_human_even_if_lane_says_proceed(self):
        self.assertEqual(decide(answers(external=0.7))["action"], "ask_human")

    def test_critical_risk_needs_human(self):
        self.assertEqual(decide(answers(risk=3.0))["action"], "ask_human")

    def test_irreversible_needs_human(self):
        self.assertEqual(decide(answers(reversible=0.1))["action"], "ask_human")

    def test_looping_needs_human(self):
        self.assertEqual(decide(answers(looping=0.8))["action"], "ask_human")

    def test_too_many_attempts_needs_human(self):
        self.assertEqual(decide(answers(), attempts=THRESHOLDS["max_attempts"])["action"], "ask_human")

    def test_low_confidence_needs_human(self):
        self.assertEqual(decide(answers(conf=0.3))["action"], "ask_human")

    def test_unnecessary_skips(self):
        self.assertEqual(decide(answers(necessary=0.1))["action"], "skip")

    def test_dry_run_passes_through(self):
        self.assertEqual(decide(answers(lane="dry_run"))["action"], "dry_run")

    def test_handoff_only_when_confident(self):
        self.assertEqual(decide(answers(specialist="paid_ads_manager", spec_conf=0.9))["handoff"], "paid_ads_manager")
        self.assertIsNone(decide(answers(specialist="paid_ads_manager", spec_conf=0.4))["handoff"])
        self.assertIsNone(decide(answers(specialist="none"))["handoff"])

    def test_missing_answers_fail_safe(self):
        self.assertEqual(decide({})["action"], "ask_human")


if __name__ == "__main__":
    unittest.main()
