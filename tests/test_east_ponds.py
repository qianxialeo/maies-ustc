"""Build the map once and check the east-campus water, island and bridges."""
from pathlib import Path
import runpy
import unittest

from PIL import Image
from shapely.geometry import LineString


ROOT = Path(__file__).resolve().parents[1]


class EastPondsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.map = runpy.run_path(str(ROOT / "source" / "make.py"), run_name="__main__")
        with Image.open(ROOT / "art" / "nav.png") as mask:
            cls.mask = mask.copy()
        with Image.open(ROOT / "art" / "ground.png") as ground:
            cls.ground = ground.copy()

    def can_walk(self, point):
        pixel = self.map["tr"](point.x, point.y)
        return bool(self.mask.getpixel(pixel))

    def test_open_water_is_drawn_and_blocks_walking(self):
        poly = self.map["poly"]
        def water_sample(pond):
            point = pond.buffer(-1).representative_point()
            x, y = self.map["tr"](point.x, point.y)
            colors = self.ground.crop((x-4, y-4, x+5, y+5)).getcolors()
            return point, max(colors)[1]

        west, water_color = water_sample(poly("290098995"))
        self.assertFalse(self.can_walk(west))
        for name, pond in (
            ("Spectacles Pond east", poly("290098996").difference(poly("840391562"))),
            ("Taohuawu", poly("306373626")),
        ):
            with self.subTest(pond=name):
                point, color = water_sample(pond)
                self.assertEqual(color, water_color)
                self.assertFalse(self.can_walk(point))

    def test_pavilion_island_and_both_footbridges(self):
        island = self.map["poly"]("840391562")
        self.assertTrue(self.can_walk(island.representative_point()))
        for way_id in ("306372996", "306372998"):
            line = LineString(self.map["pts"](self.map["ways"][way_id]))
            with self.subTest(bridge=way_id):
                for i in range(101):
                    point = line.interpolate(i / 100, normalized=True)
                    self.assertTrue(self.can_walk(point), f"blocked at {i}%")


if __name__ == "__main__":
    unittest.main()
