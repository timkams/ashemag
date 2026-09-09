"""
Automated Test Suite for NCERT Biology QA & Scraper System.
"""
import unittest
from pathlib import Path
from ncert_bio.catalog import NCERT_CHAPTERS, get_chapters_by_grade
from ncert_bio.qa_engine import NCERTBioQAEngine


class TestNCERTBioSystem(unittest.TestCase):
    def setUp(self):
        self.engine = NCERTBioQAEngine()

    def test_catalog_registered_chapters(self):
        self.assertEqual(len(NCERT_CHAPTERS), 50, "Total catalog chapters should be 50")
        self.assertEqual(len(get_chapters_by_grade(9)), 6)
        self.assertEqual(len(get_chapters_by_grade(10)), 6)
        self.assertEqual(len(get_chapters_by_grade(11)), 22)
        self.assertEqual(len(get_chapters_by_grade(12)), 16)

    def test_database_chunks_indexed(self):
        with self.engine._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM chunks")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 300, f"Expected at least 300 indexed chunks, got {count}")

    def test_class_9_query(self):
        res = self.engine.answer_question("What is the function of Golgi apparatus?", grade=9)
        self.assertTrue(res["found"])
        self.assertIn("Class 9", res["primary_source"])
        self.assertGreater(len(res["citations"]), 0)

    def test_class_10_query(self):
        res = self.engine.answer_question("Explain double circulation in human beings", grade=10)
        self.assertTrue(res["found"])
        self.assertIn("Class 10", res["primary_source"])
        self.assertGreater(len(res["citations"]), 0)

    def test_class_11_query(self):
        res = self.engine.answer_question("How does nephron filter blood and form urine?", grade=11)
        self.assertTrue(res["found"])
        self.assertIn("Class 11", res["primary_source"])
        self.assertTrue(any("glomerular" in c["excerpt"].lower() or "filtration" in c["excerpt"].lower() for c in res["citations"]))

    def test_class_12_query(self):
        res = self.engine.answer_question("Describe the double helix model of DNA", grade=12)
        self.assertTrue(res["found"])
        self.assertIn("Class 12", res["primary_source"])
        self.assertTrue(any("watson" in c["excerpt"].lower() or "dna" in c["excerpt"].lower() for c in res["citations"]))


if __name__ == "__main__":
    unittest.main()
