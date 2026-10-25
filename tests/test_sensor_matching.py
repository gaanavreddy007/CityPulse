"""
CITYPULSE - Gate 3 Candidate Sensor Matching Unit Tests
Validates non-forcing candidate generation, ambiguity flagging,
and multi-sensor junction conflict detection.
Runs 100% offline.
"""

import os
import unittest
import pandas as pd

from citypulse.map.candidate import MappingStatus, CandidateEdge, SensorMappingRecord
from citypulse.map.matcher import CandidateMatcher, geodetic_distance_meters, point_to_segment_distance_meters

class TestSensorMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a small, controlled synthetic road network for offline testing
        cls.test_network = pd.DataFrame([
            {
                "edge_id": "EDGE_MAIN_NB", "u": 1, "v": 2,
                "u_lat": 55.8600, "u_lon": -4.2700, "v_lat": 55.8650, "v_lon": -4.2700,
                "name": "Main Street Northbound", "highway": "primary", "oneway": True, "lanes": 2
            },
            {
                "edge_id": "EDGE_CROSS_EB", "u": 3, "v": 4,
                "u_lat": 55.8625, "u_lon": -4.2750, "v_lat": 55.8625, "v_lon": -4.2650,
                "name": "Cross Street Eastbound", "highway": "secondary", "oneway": True, "lanes": 2
            },
            {
                "edge_id": "EDGE_REMOTE", "u": 5, "v": 6,
                "u_lat": 55.8900, "u_lon": -4.2900, "v_lat": 55.8950, "v_lon": -4.2900,
                "name": "Remote Bypass", "highway": "trunk", "oneway": True, "lanes": 3
            }
        ])
        cls.matcher = CandidateMatcher(cls.test_network, max_search_radius_m=50.0)

    def test_high_confidence_match(self):
        """Verify detector placed directly on an isolated edge receives high confidence match."""
        # Point on Main Street Northbound (lat 55.8610, lon -4.2700)
        rec = self.matcher.match_detector("GA001_A", 55.8610, -4.2700)
        
        self.assertEqual(rec.status, MappingStatus.MATCHED_HIGH_CONFIDENCE)
        self.assertEqual(rec.selected_edge_id, "EDGE_MAIN_NB")
        self.assertLess(rec.min_distance_meters, 2.0)
        self.assertGreaterEqual(rec.mapping_confidence, 0.85)

    def test_ambiguity_flagging_at_crossroads(self):
        """Verify detector placed near intersection of two streets flags multi-candidate ambiguity."""
        # Intersection is at (55.8625, -4.2700). Place detector at (55.86252, -4.27002) - equidistant (~2m to both)
        rec = self.matcher.match_detector("GA002_X", 55.86252, -4.27002)
        
        self.assertEqual(rec.status, MappingStatus.AMBIGUOUS_MULTI_CANDIDATE)
        self.assertGreaterEqual(rec.candidate_count, 2)
        self.assertLessEqual(rec.mapping_confidence, 0.50)
        self.assertIn("Ambiguous", rec.rationale)

    def test_unmatched_distance_exceeded(self):
        """Verify detector placed far from any road edge is marked unmatched without forced snapping."""
        # Point far from any edge (lat 55.8750, lon -4.2800)
        rec = self.matcher.match_detector("GA999_Z", 55.8750, -4.2800)
        
        self.assertEqual(rec.status, MappingStatus.UNMATCHED_DISTANCE_EXCEEDED)
        self.assertIsNone(rec.selected_edge_id)
        self.assertEqual(rec.mapping_confidence, 0.0)

    def test_multi_sensor_junction_conflict_detection(self):
        """Verify multiple detectors from same junction snapping to same edge are flagged for conflict."""
        batch_sensors = pd.DataFrame([
            {"id": "GA0151_A", "latitude": 55.8610, "longitude": -4.2700},
            {"id": "GA0151_B", "latitude": 55.8615, "longitude": -4.2700}
        ])
        results_df, stats = self.matcher.match_batch(batch_sensors)
        
        # Both share junction GA0151 and snap to EDGE_MAIN_NB
        self.assertEqual(len(results_df), 2)
        self.assertTrue((results_df['status'] == MappingStatus.AMBIGUOUS_MULTI_CANDIDATE.value).all())
        self.assertTrue((results_df['mapping_confidence'] <= 0.40).all())
        self.assertTrue(results_df['rationale'].str.contains("Conflict").all())

if __name__ == "__main__":
    unittest.main()
