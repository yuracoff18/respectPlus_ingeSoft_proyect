import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from modules.game_accounts.schemas import SyncAccount
from modules.game_accounts.providers import riot, henrik, faceit, osirion, steam
from modules.game_accounts.providers.http import IntegrationError


class RankProviderTests(unittest.TestCase):
    def setUp(self):
        with henrik._rate_lock:
            henrik._request_times.clear()

    def test_steam_account_lookup_does_not_invent_a_premier_rank(self):
        def client(url, headers=None):
            self.assertTrue(url.startswith("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"))
            return {"response": {"players": [{"personaname": "Steam Player"}]}}
        with patch.dict(os.environ, {"STEAM_WEB_API_KEY": "fixture"}):
            result = steam.fetch(SyncAccount(game="Counter-Strike 2", identifier="76561198000000000", platform="steam", consent=True), client)
        self.assertEqual(result["provider_account_name"], "Steam Player")
        self.assertIsNone(result["current_rank"])
        self.assertIsNone(result["peak_rank"])
        self.assertEqual(result["status"], "unavailable")

    def test_riot_queries_puuid_and_keeps_queue_specific_rank(self):
        calls = []
        def client(url, headers=None):
            calls.append((url, headers))
            if "/riot/account/" in url:
                return {"puuid": "test-puuid"}
            return [{"queueType": "RANKED_FLEX_SR", "tier": "SILVER", "rank": "II", "leaguePoints": 3}, {"queueType": "RANKED_SOLO_5x5", "tier": "EMERALD", "rank": "I", "leaguePoints": 82}]
        with patch.dict(os.environ, {"RIOT_API_KEY": "fixture-key"}):
            result = riot.fetch(SyncAccount(game="League of Legends", identifier="A Name#LAN", region="la1", queue="solo", consent=True), client)
        self.assertEqual(result["current_rank"], "Esmeralda I")
        self.assertIsNone(result["peak_rank"])
        self.assertEqual(result["rank_points"], 82)
        self.assertIn("/entries/by-puuid/test-puuid", calls[1][0])
        self.assertIn("A%20Name/LAN", calls[0][0])
        self.assertNotIn("fixture-key", calls[0][0])

    def test_riot_missing_key_and_invalid_region_never_call_network(self):
        def forbidden(*args):
            raise AssertionError("Network should not be called")
        data = SyncAccount(game="League of Legends", identifier="Name#TAG", region="evil.test", consent=True)
        with patch.dict(os.environ, {"RIOT_API_KEY": ""}):
            with self.assertRaises(IntegrationError) as error:
                riot.fetch(data, forbidden)
            self.assertEqual(error.exception.status, "not_configured")
        with patch.dict(os.environ, {"RIOT_API_KEY": "fixture"}):
            with self.assertRaises(IntegrationError):
                riot.fetch(data, forbidden)

    def test_valorant_maps_current_and_peak_separately(self):
        def client(url, headers=None):
            self.assertIn("/valorant/v3/mmr/latam/pc/Name/TAG", url)
            self.assertEqual(headers, {"Authorization": "fixture"})
            self.assertNotIn("fixture", url)
            return {"data": {"current": {"tier": {"name": "Diamond 1"}, "rr": 38}, "peak": {"tier": {"name": "Ascendant 1"}}}}
        with patch.dict(os.environ, {"HENRIK_API_KEY": "fixture"}):
            result = henrik.fetch(SyncAccount(game="Valorant", identifier="Name#TAG", region="latam", consent=True), client)
        self.assertEqual(result["current_rank"], "Diamond 1")
        self.assertEqual(result["peak_rank"], "Ascendant 1")

    def test_valorant_quota_is_shared_between_concurrent_accounts_and_recovers(self):
        from concurrent.futures import ThreadPoolExecutor

        def query(index):
            data = SyncAccount(game="Valorant", identifier=f"Player{index}#TAG", region="latam", consent=True)
            try:
                henrik.fetch(data, lambda *_: {"data": {"current": {"tier": {"name": "Gold 1"}}}})
                return True
            except IntegrationError as error:
                self.assertIn("30 consultas por minuto", str(error))
                return False

        with patch.dict(os.environ, {"HENRIK_API_KEY": "fixture"}), patch.object(henrik.time, "monotonic", return_value=100):
            with ThreadPoolExecutor(max_workers=8) as executor:
                outcomes = list(executor.map(query, range(45)))
            self.assertEqual(sum(outcomes), 30)
            self.assertEqual(len(henrik._request_times), 30)
            with patch.object(henrik.time, "monotonic", return_value=159.99):
                self.assertFalse(query(46))
            with patch.object(henrik.time, "monotonic", return_value=160):
                self.assertTrue(query(47))

    def test_valorant_failures_count_toward_quota_but_invalid_inputs_do_not(self):
        calls = []

        def rejected(*args):
            calls.append(args)
            raise IntegrationError("Provider rejected request")

        data = SyncAccount(game="Valorant", identifier="Player#TAG", region="latam", consent=True)
        with patch.dict(os.environ, {"HENRIK_API_KEY": ""}):
            with self.assertRaises(IntegrationError):
                henrik.fetch(data, rejected)
        with patch.dict(os.environ, {"HENRIK_API_KEY": "fixture"}), patch.object(henrik.time, "monotonic", return_value=100):
            for identifier in ("#TAG", "Name#"):
                with self.assertRaises(IntegrationError):
                    henrik.fetch(data.model_copy(update={"identifier": identifier}), rejected)
            self.assertEqual(len(henrik._request_times), 0)
            for _ in range(30):
                with self.assertRaises(IntegrationError):
                    henrik.fetch(data, rejected)
            with self.assertRaisesRegex(IntegrationError, "30 consultas por minuto"):
                henrik.fetch(data, rejected)
        self.assertEqual(len(calls), 30)

    def test_faceit_is_explicitly_distinct_from_premier(self):
        def client(url, headers=None):
            return {"games": {"cs2": {"skill_level": 8, "faceit_elo": 1700}}}
        with patch.dict(os.environ, {"FACEIT_API_KEY": "fixture"}):
            result = faceit.fetch(SyncAccount(game="Counter-Strike 2", identifier="Nickname", consent=True), client)
        self.assertEqual(result["current_rank"], "FACEIT nivel 8")
        self.assertIn("No es Premier", result["queue"])
        self.assertIsNone(result["peak_rank"])

    def test_fortnite_uses_current_season_instead_of_historical_rank(self):
        now = datetime.now(timezone.utc)
        def client(url, headers=None):
            if "/account-ranks?" in url:
                return {"modes": [{"rankingType": "ranked-br", "rankingTrackId": "old", "currentDivision": {"divisionName": "Unreal"}, "highestDivision": {"divisionName": "Unreal"}}, {"rankingType": "ranked-br", "rankingTrackId": "current", "currentDivision": {"divisionName": "Diamond I"}, "highestDivision": {"divisionName": "Diamond III"}, "promotionProgress": 20}]}
            return {"modes": [{"rankingType": "ranked-br", "seasons": [{"seasonStart": (now - timedelta(days=2)).isoformat(), "seasonEnd": (now + timedelta(days=2)).isoformat(), "seasonRankingTrackId": "current"}]}]}
        result = osirion.fetch(SyncAccount(game="Fortnite", identifier="a" * 32, queue="ranked-br", consent=True), client)
        self.assertEqual(result["current_rank"], "Diamond I")
        self.assertEqual(result["peak_rank"], "Diamond III")
        self.assertEqual(result["peak_scope"], "Temporada actual")
