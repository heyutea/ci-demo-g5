import unittest

from duckfine import DuckFine


class TestDuckFineInit(unittest.TestCase):
    def test_stores_member_id(self):
        fine = DuckFine("member-1")
        self.assertEqual(fine.member_id, "member-1")

    def test_starts_with_zero_owed(self):
        fine = DuckFine("member-1")
        self.assertEqual(fine.total_owed, 0.0)


class TestDuckFineCharge(unittest.TestCase):
    def setUp(self):
        self.fine = DuckFine("member-1")

    def test_zero_days_late_charges_nothing(self):
        fee = self.fine.charge(0)
        self.assertEqual(fee, 0.0)

    def test_within_grace_period_charges_nothing(self):
        fee = self.fine.charge(DuckFine.GRACE_DAYS)
        self.assertEqual(fee, 0.0)

    def test_one_day_past_grace_charges_daily_fee(self):
        fee = self.fine.charge(DuckFine.GRACE_DAYS + 1)
        self.assertEqual(fee, DuckFine.DAILY_FEE)

    def test_multiple_days_past_grace_charges_pro_rata(self):
        days_late = DuckFine.GRACE_DAYS + 3
        fee = self.fine.charge(days_late)
        self.assertEqual(fee, 3 * DuckFine.DAILY_FEE)

    def test_deluxe_doubles_the_fee(self):
        days_late = DuckFine.GRACE_DAYS + 1
        fee = self.fine.charge(days_late, deluxe=True)
        self.assertEqual(fee, 2 * DuckFine.DAILY_FEE)

    def test_fee_is_capped_at_max_fee(self):
        fee = self.fine.charge(days_late=100)
        self.assertEqual(fee, DuckFine.MAX_FEE)

    def test_deluxe_fee_is_capped_at_max_fee(self):
        fee = self.fine.charge(days_late=100, deluxe=True)
        self.assertEqual(fee, DuckFine.MAX_FEE)

    def test_negative_days_late_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)

    def test_charge_accumulates_into_total_owed(self):
        self.fine.charge(DuckFine.GRACE_DAYS + 1)
        self.fine.charge(DuckFine.GRACE_DAYS + 2)
        expected = DuckFine.DAILY_FEE + 2 * DuckFine.DAILY_FEE
        self.assertEqual(self.fine.total_owed, expected)

    def test_failed_charge_does_not_change_total_owed(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)
        self.assertEqual(self.fine.total_owed, 0.0)


if __name__ == "__main__":
    unittest.main()
