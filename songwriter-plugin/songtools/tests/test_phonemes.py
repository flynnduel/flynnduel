from songtools.phonemes import family, relatives


def test_plosive_partner_first_then_companions():
    r = relatives("T")
    assert r[0] == "D" and set(r[1:3]) == {"K", "P"} and set(r[3:5]) == {"B", "G"}


def test_fricative_companions_before_partner():
    r = relatives("F")
    assert r[:3] == ["S", "SH", "CH"] and r.index("V") > r.index("TH")


def test_nasal_family():
    assert family("M") == "nasal" and set(relatives("N")) == {"M", "NG"}
