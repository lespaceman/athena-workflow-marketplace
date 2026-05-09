import unittest

from marketplace.semver import bump_part


class TestBumpPart(unittest.TestCase):
    def test_patch(self):
        self.assertEqual(bump_part("0.1.2", "patch"), "0.1.3")
        self.assertEqual(bump_part("0.1.9", "patch"), "0.1.10")
        self.assertEqual(bump_part("1.0.0", "patch"), "1.0.1")

    def test_minor(self):
        self.assertEqual(bump_part("0.1.5", "minor"), "0.2.0")
        self.assertEqual(bump_part("0.9.99", "minor"), "0.10.0")
        self.assertEqual(bump_part("3.5.7", "minor"), "3.6.0")

    def test_major(self):
        self.assertEqual(bump_part("0.1.5", "major"), "1.0.0")
        self.assertEqual(bump_part("9.99.99", "major"), "10.0.0")

    def test_unknown_part(self):
        with self.assertRaises(ValueError):
            bump_part("0.1.0", "build")

    def test_invalid_version(self):
        with self.assertRaises(ValueError):
            bump_part("0.1", "patch")
        with self.assertRaises(ValueError):
            bump_part("v1.0.0", "patch")
        with self.assertRaises(ValueError):
            bump_part("1.0.0-alpha", "patch")


if __name__ == "__main__":
    unittest.main()
