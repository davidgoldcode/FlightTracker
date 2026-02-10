#!/usr/bin/env python3
"""tests for the get_now() debug date helper."""
import sys
import types
import unittest
from datetime import datetime


class TestGetNow(unittest.TestCase):
    """test utilities.datenow.get_now() function."""

    def setUp(self):
        self._original_config = sys.modules.get('config')
        # clear cached modules for fresh imports each test
        for mod in ['utilities.datenow', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]

    def tearDown(self):
        for mod in ['utilities.datenow', 'config']:
            if mod in sys.modules:
                del sys.modules[mod]
        if self._original_config is not None:
            sys.modules['config'] = self._original_config

    def _set_config(self, **attrs):
        """helper to create a fake config module with given attributes."""
        fake = types.ModuleType('config')
        for k, v in attrs.items():
            setattr(fake, k, v)
        sys.modules['config'] = fake

    def _set_demo_mode(self):
        """simulate test_animation.py's FakeConfigModule."""
        class FakeConfigModule:
            def __getattr__(self, name):
                raise ImportError("demo mode - no config")
        sys.modules['config'] = FakeConfigModule()

    def test_no_config_returns_real_now(self):
        self._set_demo_mode()
        from utilities.datenow import get_now
        result = get_now()
        self.assertAlmostEqual(result.timestamp(), datetime.now().timestamp(), delta=1)

    def test_no_debug_date_attr_returns_real_now(self):
        self._set_config()  # config exists but no DEBUG_DATE
        from utilities.datenow import get_now
        result = get_now()
        self.assertAlmostEqual(result.timestamp(), datetime.now().timestamp(), delta=1)

    def test_empty_debug_date_returns_real_now(self):
        self._set_config(DEBUG_DATE="")
        from utilities.datenow import get_now
        result = get_now()
        self.assertAlmostEqual(result.timestamp(), datetime.now().timestamp(), delta=1)

    def test_none_debug_date_returns_real_now(self):
        self._set_config(DEBUG_DATE=None)
        from utilities.datenow import get_now
        result = get_now()
        self.assertAlmostEqual(result.timestamp(), datetime.now().timestamp(), delta=1)

    def test_overrides_month_and_day(self):
        self._set_config(DEBUG_DATE="12-31")
        from utilities.datenow import get_now
        result = get_now()
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 31)

    def test_preserves_real_time(self):
        self._set_config(DEBUG_DATE="02-14")
        from utilities.datenow import get_now
        result = get_now()
        now = datetime.now()
        self.assertEqual(result.month, 2)
        self.assertEqual(result.day, 14)
        self.assertEqual(result.year, now.year)
        # hour should match (minute could roll over between calls)
        self.assertEqual(result.hour, now.hour)

    def test_preserves_current_year(self):
        self._set_config(DEBUG_DATE="10-31")
        from utilities.datenow import get_now
        result = get_now()
        self.assertEqual(result.year, datetime.now().year)

    def test_returns_datetime_instance(self):
        self._set_config(DEBUG_DATE="07-04")
        from utilities.datenow import get_now
        self.assertIsInstance(get_now(), datetime)

    def test_strftime_works(self):
        self._set_config(DEBUG_DATE="03-17")
        from utilities.datenow import get_now
        self.assertEqual(get_now().strftime("%m-%d"), "03-17")

    def test_date_comparison_works(self):
        self._set_config(DEBUG_DATE="06-15")
        from utilities.datenow import get_now
        result = get_now()
        self.assertEqual(result.date().month, 6)
        self.assertEqual(result.date().day, 15)

    def test_invalid_format_falls_back(self):
        self._set_config(DEBUG_DATE="not-a-date")
        from utilities.datenow import get_now
        result = get_now()
        self.assertAlmostEqual(result.timestamp(), datetime.now().timestamp(), delta=1)

    def test_invalid_month_falls_back(self):
        self._set_config(DEBUG_DATE="13-01")
        from utilities.datenow import get_now
        result = get_now()
        self.assertAlmostEqual(result.timestamp(), datetime.now().timestamp(), delta=1)

    def test_feb_29_non_leap_year_falls_back(self):
        self._set_config(DEBUG_DATE="02-29")
        from utilities.datenow import get_now
        result = get_now()
        now = datetime.now()
        # if current year is a leap year, this succeeds; otherwise falls back
        if now.year % 4 != 0:
            self.assertAlmostEqual(result.timestamp(), now.timestamp(), delta=1)
        else:
            self.assertEqual(result.month, 2)
            self.assertEqual(result.day, 29)


if __name__ == '__main__':
    unittest.main()
