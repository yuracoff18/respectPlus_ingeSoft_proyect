def public_user(user):
    keys = ("id", "username", "name", "headline", "bio", "games", "country", "available", "color", "connections", "game_profiles")
    result = {key: user[key] for key in keys if key in user}
    result.setdefault("games", [user["game"]] if user.get("game") else [])
    result.setdefault("game_profiles", {})
    result["game"] = result["games"][0] if result["games"] else ""
    result["rank"] = result["game_profiles"].get(result["game"], {}).get("current_rank") or "Sin sincronizar"
    result["account_type"] = user.get("account_type", "player")
    result["profile_href"] = f"/sponsors/{user['sponsor_id']}" if result["account_type"] == "sponsor" else f"/jugadores/{user['username']}"
    if result["account_type"] == "sponsor":
        result["sponsor_id"] = user["sponsor_id"]
    return result


def own_user(user):
    return {**public_user(user), "email": user.get("email", ""), "role": user.get("role", "player")}
