"""HTTP integration tests. All accounts and content live in a temporary database."""
import concurrent.futures
import http.cookiejar
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
TEST_ADMIN_PASSWORD = "Temporary-Test-Admin-Only!42"


class Client:
    def __init__(self, base):
        self.base = base
        self.cookies = http.cookiejar.CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookies))

    def call(self, path, method="GET", data=None, origin=None):
        headers = {"Content-Type": "application/json"}
        if origin:
            headers["Origin"] = origin
        request = Request(self.base + "/api" + path, data=json.dumps(data).encode() if data is not None else None, method=method, headers=headers)
        try:
            with self.opener.open(request, timeout=15) as result:
                return result.status, json.loads(result.read())
        except HTTPError as error:
            with error:
                return error.code, json.loads(error.read())


class APIIntegrationTests(unittest.TestCase):
    def setUp(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        self.base = f"http://127.0.0.1:{self.port}"
        self.temp = tempfile.TemporaryDirectory(prefix="respect-tests-")
        assert Path(self.temp.name).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
        self.env = {**os.environ, "SQLITE_PATH": str(Path(self.temp.name) / "test.db"), "MONGO_URI": "", "MONGO_HOST": "", "BOOTSTRAP_ADMIN_USERNAME": "admin", "BOOTSTRAP_ADMIN_PASSWORD": TEST_ADMIN_PASSWORD, "RIOT_API_KEY": "", "HENRIK_API_KEY": "", "FACEIT_API_KEY": ""}
        self.process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(self.port), "--log-level", "error"], cwd=ROOT, env=self.env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for _ in range(100):
            if self.process.poll() is not None:
                raise RuntimeError(self.process.stderr.read().decode())
            try:
                if Client(self.base).call("/health")[0] == 200:
                    return
            except OSError:
                pass
            time.sleep(0.05)
        raise RuntimeError("API did not start")

    def tearDown(self):
        self.process.terminate()
        self.process.communicate(timeout=10)
        self.temp.cleanup()

    def player(self):
        client = Client(self.base)
        suffix = uuid4().hex[:12]
        credentials = {"email": f"{suffix}@test.example", "password": "StrongTestPass42", "username": f"p_{suffix}", "name": f"Player {suffix}"}
        status, user = client.call("/auth/register", "POST", credentials)
        self.assertEqual(status, 201, user)
        return client, user, credentials

    def admin(self):
        client = Client(self.base)
        status, user = client.call("/auth/login", "POST", {"identifier": "admin", "password": TEST_ADMIN_PASSWORD})
        self.assertEqual(status, 200, user)
        self.assertEqual(user["role"], "admin")
        return client, user

    def sponsor(self):
        client = Client(self.base)
        suffix = uuid4().hex[:12]
        credentials = {"email": f"company_{suffix}@test.example", "password": "StrongCompanyPass42", "username": f"company_{suffix}", "name": "Independent Company", "account_type": "sponsor"}
        status, user = client.call("/auth/register", "POST", credentials)
        self.assertEqual(status, 201, user)
        status, sponsor = client.call(f"/sponsors/{user['sponsor_id']}")
        self.assertEqual(status, 200, sponsor)
        return client, user, credentials, sponsor

    def tournament(self, client, **overrides):
        data = {"title": "Integration Cup", "game": "Valorant", "description": "A fair competition with final results and a complete elimination bracket.", "prize": "Por la gloria", "capacity": 4, "starts_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(), "region": "LATAM", **overrides}
        status, tournament = client.call("/tournaments", "POST", data)
        self.assertEqual(status, 201, tournament)
        return tournament

    def team(self, client, name="Test squad"):
        data = {"name": name, "tag": "TST", "headline": "Together we compete", "bio": "A temporary squad for integration testing only.", "games": ["Valorant", "League of Legends"], "competition_game": "Valorant", "country": "Colombia", "recruiting": True, "max_members": 5}
        status, team = client.call("/teams", "POST", data)
        self.assertEqual(status, 201, team)
        return team

    def test_01_auth_privacy_and_no_public_role_escalation(self):
        client, user, credentials = self.player()
        self.assertNotIn("password_hash", user)
        self.assertEqual(user["role"], "player")
        self.assertIn("HttpOnly", list(client.cookies)[0]._rest)
        self.assertEqual(client.call("/auth/register", "POST", {**credentials, "role": "admin"})[0], 422)
        self.assertEqual(client.call("/admin/summary")[0], 403)
        self.assertEqual(Client(self.base).call("/admin/summary")[0], 401)
        self.assertEqual(Client(self.base).call("/posts", "POST", {"content": "Unauthorized"})[0], 401)
        self.assertEqual(client.call("/posts", "POST", {"content": "   "})[0], 422)
        self.assertEqual(client.call("/posts", "POST", {"content": "Invalid origin"}, origin="https://untrusted.example")[0], 403)
        for public in client.call("/users")[1]:
            self.assertNotIn("password_hash", public)
            self.assertNotIn("email", public)
            self.assertNotEqual(public["username"], "admin")
        client.call("/auth/logout", "POST")
        self.assertEqual(client.call("/auth/me")[0], 401)
        self.assertEqual(client.call("/auth/login", "POST", {"identifier": credentials["username"], "password": credentials["password"]})[0], 200)

    def test_02_profile_connections_posts_and_rank_spoofing(self):
        client, user, _ = self.player()
        other, target, _ = self.player()
        payload = {"name": "Updated player", "headline": "Building a squad", "bio": "A gamer story", "games": ["Valorant", "League of Legends"], "game": "Valorant", "rank": "Fake Challenger", "game_profiles": {"Valorant": {"current_rank": "Fake Radiant"}}, "role": "admin", "country": "Colombia", "available": True}
        updated = client.call("/users/me", "PUT", payload)[1]
        self.assertEqual(updated["role"], "player")
        self.assertEqual(updated["rank"], "Sin sincronizar")
        self.assertEqual(updated["game_profiles"], {})
        self.assertIn(target["id"], client.call(f"/users/{target['id']}/connect", "POST")[1]["connections"])
        self.assertIn(user["id"], other.call("/auth/me")[1]["connections"])
        post = client.call("/posts", "POST", {"content": "A community achievement", "game": "Valorant"})[1]
        self.assertEqual(post["publisher"]["id"], user["id"])
        self.assertIn(target["id"], other.call(f"/posts/{post['id']}/like", "POST")[1]["likes"])
        self.assertNotIn(target["id"], other.call(f"/posts/{post['id']}/like", "POST")[1]["likes"])
        self.assertEqual(other.call(f"/posts/{post['id']}/comments", "POST", {"content": "GG, well played!"})[1]["comments"][0]["author"]["id"], target["id"])
        self.assertTrue(all(post["game"] == "Valorant" for post in client.call("/posts?game=Valorant")[1]))

    def test_03_concurrent_capacity_and_bracket(self):
        owner, _, _ = self.player()
        tournament = self.tournament(owner)
        clients = [self.player()[0] for _ in range(5)]
        base = f"/tournaments/{tournament['id']}"
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            statuses = list(pool.map(lambda client: client.call(base + "/join", "POST")[0], clients))
        self.assertEqual(statuses.count(200), 4)
        self.assertEqual(statuses.count(409), 1)
        self.assertEqual(clients[0].call(base + "/start", "POST")[0], 403)
        live = owner.call(base + "/start", "POST")[1]
        for matches in live["rounds"]:
            for match in matches:
                path = base + f"/matches/{match['id']}"
                if match["a"] and match["b"] and not match["winner"]:
                    self.assertEqual(owner.call(path, "PUT", {"score_a": 1, "score_b": 1})[0], 422)
                    status, live = owner.call(path, "PUT", {"score_a": 2, "score_b": 0})
                    self.assertEqual(status, 200)
            live = owner.call(base)[1]
        # Resolve the final populated by semifinal winners.
        final = live["rounds"][-1][0]
        if not final["winner"]:
            live = owner.call(base + f"/matches/{final['id']}", "PUT", {"score_a": 2, "score_b": 0})[1]
        self.assertEqual(live["status"], "finished")

    def test_04_only_admins_create_admins_without_switching_their_session(self):
        client, actor = self.admin()
        data = {"username": "moderator_new", "name": "New Moderator", "email": "moderator_new@test.example", "password": "New-Temporary-Moderator!42"}
        status, created = client.call("/admin/admins", "POST", data)
        self.assertEqual(status, 201, created)
        self.assertEqual(created["role"], "admin")
        self.assertEqual(client.call("/auth/me")[1]["id"], actor["id"])
        self.assertEqual(client.call("/admin/admins", "POST", {**data, "username": "weak_admin", "email": "weak@test.example", "password": "weak12345"})[0], 422)
        self.assertNotIn("password_hash", created)

    def test_05_reports_threshold_evidence_entity_bans_and_session_revocation(self):
        admin, _ = self.admin()
        owner, user, credentials = self.player()
        reporters = [self.player()[0] for _ in range(6)]
        team = self.team(owner, "Reported squad")
        sponsor_data = {"name": "Reported Company", "headline": "A community company", "bio": "A temporary company profile for moderation tests.", "country": "Colombia", "games": ["Valorant"], "team_ids": [], "website": ""}
        company, company_user, company_credentials, sponsor = self.sponsor()
        sponsor = company.call(f"/sponsors/{sponsor['id']}", "PUT", sponsor_data)[1]
        for kind, target, account, account_credentials in [("team", team, owner, credentials), ("sponsor", sponsor, company, company_credentials), ("player", user, owner, credentials)]:
            post_data = {"content": f"Preserved evidence for {kind}", "game": "Valorant", "publisher_type": kind, "publisher_id": target["id"]}
            status, post = account.call("/posts", "POST", post_data)
            self.assertEqual(status, 201, post)
            payload = {"target_type": kind, "target_id": target["id"], "publication_id": post["id"], "category": "acoso", "reason": "An abusive publication with sufficient context for review."}
            self.assertEqual(account.call("/reports", "POST", payload)[0], 400)
            for reporter in reporters[:5]:
                self.assertEqual(reporter.call("/reports", "POST", payload)[0], 201)
            cases = admin.call("/admin/cases")[1]
            self.assertFalse(any(case["target_id"] == target["id"] for case in cases))
            self.assertEqual(reporters[0].call("/reports", "POST", payload)[0], 409)
            self.assertEqual(reporters[-1].call("/reports", "POST", payload)[0], 201)
            review = admin.call(f"/admin/cases/{kind}/{target['id']}")[1]
            self.assertEqual(review["pending_count"], 6)
            self.assertEqual(review["reports"][0]["publication"]["content"], post_data["content"])
            self.assertTrue(any(case["target_id"] == target["id"] for case in admin.call("/admin/cases")[1]))
            if kind == "team":
                dismissed = admin.call(f"/admin/cases/{kind}/{target['id']}/decision", "POST", {"action": "dismiss", "reason": "Reviewed evidence does not justify suspending this profile.", "report_ids": [report["id"] for report in review["reports"]]})
                self.assertEqual(dismissed[0], 200)
                self.assertFalse(dismissed[1]["banned"])
                self.assertEqual(dismissed[1]["pending_count"], 0)
                for reporter in reporters:
                    self.assertEqual(reporter.call("/reports", "POST", payload)[0], 201)
                review = admin.call(f"/admin/cases/{kind}/{target['id']}")[1]
            decision = {"action": "ban", "reason": "Evidence reviewed and a confirmed violation was found.", "report_ids": [report["id"] for report in review["reports"] if report["status"] == "pending"]}
            self.assertEqual(reporters[0].call(f"/admin/cases/{kind}/{target['id']}/decision", "POST", decision)[0], 403)
            status, banned = admin.call(f"/admin/cases/{kind}/{target['id']}/decision", "POST", decision)
            self.assertEqual(status, 200, banned)
            self.assertTrue(banned["banned"])
            self.assertEqual(banned["reports"][0]["publication"]["content"], post_data["content"])
            public_path = {"team": "/teams/", "sponsor": "/sponsors/", "player": "/users/"}[kind] + target["id"]
            self.assertEqual(reporters[0].call(public_path)[0], 404)
            self.assertFalse(any(item["id"] == post["id"] for item in reporters[0].call("/posts")[1]))
            if kind in ("player", "sponsor"):
                self.assertIn(account.call("/auth/me")[0], (401, 403))
                self.assertEqual(account.call("/auth/login", "POST", account_credentials)[0], 403)
            unbanned = admin.call(f"/admin/cases/{kind}/{target['id']}/unban", "POST", {"reason": "The appeal was reviewed and access can be restored."})
            self.assertEqual(unbanned[0], 200)
            self.assertFalse(unbanned[1]["banned"])
            if kind in ("player", "sponsor"):
                self.assertEqual(account.call("/auth/me")[0], 401)
                self.assertEqual(account.call("/auth/login", "POST", account_credentials)[0], 200)
        self.assertEqual(owner.call("/auth/login", "POST", credentials)[0], 200)

    def test_06_missing_keys_and_unsupported_games_do_not_invent_ranks(self):
        client, _, _ = self.player()
        data = {"name": "Rank Player", "headline": "Checking ranks", "bio": "", "game": "League of Legends", "games": ["League of Legends", "Rocket League"], "country": "Colombia", "available": True}
        client.call("/users/me", "PUT", data)
        request = {"game": "League of Legends", "identifier": "Player#LAN", "region": "la1", "queue": "solo", "consent": True}
        self.assertEqual(client.call("/game-accounts/sync", "POST", {**request, "consent": False})[0], 422)
        status, user = client.call("/game-accounts/sync", "POST", request)
        self.assertEqual(status, 200, user)
        self.assertEqual(user["game_profiles"]["League of Legends"]["status"], "not_configured")
        self.assertFalse(user["game_profiles"]["League of Legends"].get("current_rank"))
        self.assertEqual(client.call("/game-accounts/sync", "POST", request)[0], 429)
        unsupported = client.call("/game-accounts/sync", "POST", {**request, "game": "Rocket League"})[1]
        self.assertEqual(unsupported["game_profiles"]["Rocket League"]["status"], "unsupported")
        self.assertFalse(unsupported["game_profiles"]["Rocket League"].get("current_rank"))
        self.assertNotIn("League of Legends", client.call("/game-accounts/League%20of%20Legends", "DELETE")[1]["game_profiles"])

    def test_07_players_need_no_team_and_companies_have_independent_logins(self):
        admin, _ = self.admin()
        before = admin.call("/admin/summary")[1]
        player, gamer, _ = self.player()
        self.assertEqual(gamer["account_type"], "player")
        self.assertEqual(admin.call("/admin/summary")[1]["teams"], before["teams"])
        self.assertFalse(any(gamer["id"] in team["members"] for team in player.call("/teams")[1]))

        company, user, credentials, sponsor = self.sponsor()
        self.assertEqual(user["role"], "player")
        self.assertEqual(user["account_type"], "sponsor")
        self.assertEqual(user["profile_href"], f"/sponsors/{sponsor['id']}")
        self.assertEqual(sponsor["owner_id"], user["id"])
        self.assertEqual(sponsor["owner"]["profile_href"], user["profile_href"])
        self.assertEqual(sponsor["team_ids"], [])
        self.assertEqual(sponsor["games"], [])
        self.assertNotIn("password_hash", user)
        self.assertNotIn("email", sponsor["owner"])
        self.assertFalse(any(item["id"] == user["id"] for item in company.call("/users")[1]))
        self.assertEqual(company.call(f"/users/{user['username']}")[0], 404)
        after = admin.call("/admin/summary")[1]
        self.assertEqual(after["players"], before["players"] + 1)
        self.assertEqual(after["sponsors"], before["sponsors"] + 1)

        profile = {"name": "Company Updated", "headline": "We support competitive players", "bio": "An independent company with its own login and profile.", "games": ["Valorant"], "country": "Colombia", "website": "https://example.com", "team_ids": []}
        self.assertEqual(player.call(f"/sponsors/{sponsor['id']}", "PUT", profile)[0], 403)
        self.assertEqual(company.call(f"/sponsors/{sponsor['id']}", "PUT", profile)[0], 200)
        current = company.call("/auth/me")[1]
        self.assertEqual(current["name"], profile["name"])
        self.assertEqual(current["games"], profile["games"])
        self.assertEqual(current["account_type"], "sponsor")
        self.assertEqual(company.call("/auth/logout", "POST")[0], 200)
        for identifier in (credentials["username"], credentials["email"]):
            status, logged_in = company.call("/auth/login", "POST", {"identifier": identifier, "password": credentials["password"]})
            self.assertEqual(status, 200, logged_in)
            self.assertEqual(logged_in["sponsor_id"], sponsor["id"])

        status, post = company.call("/posts", "POST", {"content": "A post from an independent company", "game": "Valorant"})
        self.assertEqual(status, 201, post)
        self.assertEqual(post["publisher"]["type"], "sponsor")
        self.assertEqual(post["publisher"]["id"], sponsor["id"])
        self.assertEqual(post["publisher"]["href"], user["profile_href"])
        comment = company.call(f"/posts/{post['id']}/comments", "POST", {"content": "Company reply"})[1]["comments"][-1]
        self.assertEqual(comment["author"]["profile_href"], user["profile_href"])
        self.assertEqual(company.call("/posts", "POST", {"content": "Impersonation", "publisher_type": "sponsor", "publisher_id": "not-owned"})[0], 403)
        self.assertEqual(company.call("/admin/summary")[0], 403)
        self.assertEqual(company.call("/admin/admins", "POST", {"username": "fake_admin", "name": "Fake Admin", "email": "fake@tests.example", "password": "Strong-Fake-Admin-Password!42"})[0], 403)

        team_data = {"name": "Forbidden Squad", "tag": "NOPE", "headline": "Not a player", "bio": "A company cannot be added as a player to a team.", "games": ["Valorant"], "competition_game": "Valorant", "country": "Colombia", "recruiting": True, "max_members": 5}
        self.assertEqual(company.call("/teams", "POST", team_data)[0], 403)
        team = self.team(player, "Player owned squad")
        self.assertEqual(company.call(f"/teams/{team['id']}/requests", "POST")[0], 403)
        self.assertEqual(company.call("/sponsors", "POST", profile)[0], 409)
        self.assertEqual(player.call("/sponsors", "POST", profile)[0], 403)
        self.assertEqual(company.call("/users/me", "PUT", {"name": "Fake Gamer", "headline": "", "bio": "", "game": "Valorant", "games": ["Valorant"], "country": "Colombia", "available": True})[0], 403)
        self.assertEqual(company.call("/game-accounts/sync", "POST", {"game": "Valorant", "identifier": "Name#TAG", "region": "latam", "consent": True})[0], 403)
        tournament = self.tournament(company)
        self.assertEqual(tournament["owner_href"], user["profile_href"])
        self.assertEqual(company.call(f"/tournaments/{tournament['id']}/join", "POST")[0], 403)
        self.assertEqual(player.call(f"/tournaments/{tournament['id']}/join", "POST")[0], 200)
        self.assertEqual(player.call("/reports", "POST", {"target_type": "player", "target_id": user["id"], "category": "spam", "reason": "Wrong target type should not create a separate company case."})[0], 404)
        for extra in ({"account_type": "admin"}, {"account_type": "sponsor", "role": "admin"}, {"account_type": "sponsor", "sponsor_id": sponsor["id"]}):
            self.assertEqual(player.call("/auth/register", "POST", {**credentials, **extra})[0], 422)
