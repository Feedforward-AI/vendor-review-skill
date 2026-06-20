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
