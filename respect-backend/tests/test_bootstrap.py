import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from core.bootstrap import bootstrap_admin
from scripts.reset_to_admin import reset_to_admin
from store import Store


class BootstrapTests(unittest.TestCase):
    def test_clean_state_has_one_admin_and_bootstrap_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix="respect-bootstrap-") as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()))
            with patch.dict(os.environ, {"MONGO_URI": "", "MONGO_HOST": "", "SQLITE_PATH": str(Path(directory) / "test.db"), "BOOTSTRAP_ADMIN_USERNAME": "admin", "BOOTSTRAP_ADMIN_PASSWORD": "Temporary-Admin-Password!42"}):
                store = Store()
                try:
                    store.put("users", {"id": "old-test", "username": "old_test"})
                    store.put("posts", {"id": "old-post", "content": "Old demonstration"})
                    result = reset_to_admin(store)
                    self.assertEqual(result["remaining_users"], 1)
                    self.assertEqual(store.all("posts"), [])
                    user = store.all("users")[0]
                    self.assertEqual(user["role"], "admin")
                    self.assertNotIn("password", user)
                    original_hash = user["password_hash"]
                    self.assertIsNone(bootstrap_admin(store))
                    self.assertEqual(store.all("users")[0]["password_hash"], original_hash)
                finally:
                    store.close()

    def test_weak_password_is_rejected_before_deletion(self):
        with tempfile.TemporaryDirectory(prefix="respect-bootstrap-") as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()))
            with patch.dict(os.environ, {"MONGO_URI": "", "MONGO_HOST": "", "SQLITE_PATH": str(Path(directory) / "test.db"), "BOOTSTRAP_ADMIN_PASSWORD": "weak"}):
                store = Store()
                try:
                    store.put("users", {"id": "preserved", "username": "preserved"})
                    with self.assertRaises(ValueError):
                        reset_to_admin(store)
                    self.assertIsNotNone(store.get("users", "preserved"))
                finally:
                    store.close()
