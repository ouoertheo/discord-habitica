import unittest
from  registration_cache import RegistrationCache, REGISTRATION_CACHE
import os

class RegistrationCacheTest(unittest.TestCase):
    def test_verify_file(self):
        rc = RegistrationCache()
        rc.verify_file()
        self.assertTrue(os.path.exists(REGISTRATION_CACHE))
    def test_read_write_cache(self):
        rc = RegistrationCache()
        rc.save_channel("test_channel","test_group")
        self.assertEqual(rc.get_channel("test_group"),"test_channel")
    def test_is_channel_registered(self):
        rc = RegistrationCache()
        rc.verify_file()
        rc.save_channel("test_channel","test_group")
        self.assertFalse(rc.is_channel_registered("test_channel_bad"))
        self.assertTrue(rc.is_channel_registered("test_channel"))





