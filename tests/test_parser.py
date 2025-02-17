# tests/test_parser.py

from src.parser import parse_feedback, parse_footer


def test_parse_footer_valid():
    footer_text = "Collection: 183 , Document ID: 9846 , Self-paced ID: 1378"
    expected = {"collection": "183", "document_id": "9846", "self_paced_id": "1378"}
    result = parse_footer(footer_text)
    assert result == expected


def test_parse_footer_invalid():
    footer_text = "No valid footer info here"
    expected = {"collection": None, "document_id": None, "self_paced_id": None}
    result = parse_footer(footer_text)
    assert result == expected


MULTI_COURSE_SAMPLE = """
<div id="main-column">
  <h3 class="p-0 m-0">Prealgebra 1 Self-Paced</h3>
  <p>prealgebra1-sp</p>
  <div class="card mb-4">
    <div class="card-header">
      Lesson 1.1.9 Videos<br>
    </div>
    <div class="card-body">
      <p>
        1 students responded<br>
        100% 'yes this was helpful'; 0% 'no this was not helpful'
      </p>
    </div>
    <div class="card-footer">
      Collection: 183 , Document ID: 9846 , Self-paced ID: 1378
    </div>
  </div>
  <h3 class="p-0 m-0">B2B Prealgebra 1 Self-Paced</h3>
  <p>b2b-prealgebra1-sp</p>
  <div class="card mb-4">
    <div class="card-header">
      Lesson 1.1.3 Welcome<br>
    </div>
    <div class="card-body">
      <p>
        36 students responded<br>
        92% 'yes this was helpful'; 8% 'no this was not helpful'
      </p>
    </div>
    <div class="card-footer">
      Collection: 491 , Document ID: 9745 , Self-paced ID: 11705
    </div>
  </div>
  <h3 class="p-0 m-0">Prealgebra 2 Self-Paced</h3>
  <p>prealgebra2-sp</p>
  <div class="card mb-4">
    <div class="card-header">
      Lesson 9.1.3 Introduction to Square Roots<br>
    </div>
    <div class="card-body">
      <p>
        1 students responded<br>
        100% 'yes this was helpful'; 0% 'no this was not helpful'
      </p>
    </div>
    <div class="card-footer">
      Collection: 198 , Document ID: 10325 , Self-paced ID: 1578
    </div>
  </div>
</div>
"""


def test_multi_course_parsing():
    df = parse_feedback(MULTI_COURSE_SAMPLE)
    assert len(df) == 3
    # First card should have course "Prealgebra 1 Self-Paced"
    row0 = df.iloc[0]
    assert row0["course"] == "Prealgebra 1 Self-Paced"
    # Second card should have course "B2B Prealgebra 1 Self-Paced"
    row1 = df.iloc[1]
    assert row1["course"] == "B2B Prealgebra 1 Self-Paced"
    # Third card should have course "Prealgebra 2 Self-Paced"
    row2 = df.iloc[2]
    assert row2["course"] == "Prealgebra 2 Self-Paced"
