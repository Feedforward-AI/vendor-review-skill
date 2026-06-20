import eval_concordance as ec

def test_perfect_concordance():
    produced = {"detailed": [{"dimension": d, "score": s} for d, s in
                [("SEE","Fail"),("CHANGE","Partial"),("ADAPT","Partial"),
                 ("USE","Pass"),("LEARN","Fail"),("EXIT","Fail")]]}
    expected = {"scores": {"SEE":"Fail","CHANGE":"Partial","ADAPT":"Partial",
                           "USE":"Pass","LEARN":"Fail","EXIT":"Fail"}}
    r = ec.score_concordance(produced, expected)
    assert r["pct"] == 100.0 and r["mismatches"] == []

def test_partial_concordance():
    produced = {"detailed": [{"dimension":"SEE","score":"Pass"}]}
    expected = {"scores": {"SEE":"Fail"}}
    r = ec.score_concordance(produced, expected)
    assert r["pct"] == 0.0 and ("SEE", "Pass", "Fail") in [tuple(x) for x in r["mismatches"]]

def test_theme_presence():
    produced = {"executive_summary": {"key_takeaway": "proprietary knowledge graph lock-in",
                "paragraphs": [], "suitability": ""}, "detailed": []}
    r = ec.theme_presence(produced, ["knowledge graph", "missing-theme"])
    assert "knowledge graph" in r["found"] and "missing-theme" in r["missing"]


# --- FIX B: Broaden theme search to all report text ---

def test_theme_presence_finds_in_vendor_questions():
    """Theme word appearing only in vendor_questions (top-level) is correctly found."""
    produced = {
        "executive_summary": {"key_takeaway": "", "paragraphs": [], "suitability": ""},
        "detailed": [],
        "vendor_questions": [
            {"dimension": "SEE", "question": "Can you explain your vendor lock-in strategy?", "why_we_ask": ""}
        ]
    }
    # "lock-in" appears only in vendor_questions, not in executive summary or detailed assessments
    r = ec.theme_presence(produced, ["lock-in", "missing-theme"])
    assert "lock-in" in r["found"], "Theme in vendor_questions should be found"
    assert "missing-theme" in r["missing"]


def test_theme_presence_finds_in_detailed_vendor_questions():
    """Theme word appearing only in detailed vendor_questions is correctly found."""
    produced = {
        "executive_summary": {"key_takeaway": "", "paragraphs": [], "suitability": ""},
        "detailed": [
            {
                "dimension": "SEE",
                "assessment": "No mention of escrow here",
                "trade_offs": {"gain": "", "give_up": ""},
                "vendor_questions": ["What is your source code escrow policy?"]
            }
        ]
    }
    # "escrow" appears only in detailed vendor_questions
    r = ec.theme_presence(produced, ["escrow", "missing-theme"])
    assert "escrow" in r["found"], "Theme in detailed vendor_questions should be found"
    assert "missing-theme" in r["missing"]


def test_theme_presence_finds_in_trade_offs():
    """Theme word appearing only in trade_offs gain/give_up is correctly found."""
    produced = {
        "executive_summary": {"key_takeaway": "", "paragraphs": [], "suitability": ""},
        "detailed": [
            {
                "dimension": "SEE",
                "assessment": "Assessment text",
                "trade_offs": {"gain": "You gain fast onboarding", "give_up": "You give up customization"},
                "vendor_questions": []
            }
        ]
    }
    # "onboarding" and "customization" appear only in trade_offs
    r = ec.theme_presence(produced, ["onboarding", "customization", "missing-theme"])
    assert "onboarding" in r["found"]
    assert "customization" in r["found"]
    assert "missing-theme" in r["missing"]
