export type GameProfile = {
  game: string; account_name?: string; region?: string; platform?: string;
  current_rank?: string | null; peak_rank?: string | null; peak_scope?: string;
  rank_points?: number | null; queue?: string; provider?: string | null;
  source_url?: string; note?: string; synced_at?: string; provider_account_name?: string;
  status: "synced" | "unranked" | "not_configured" | "unsupported" | "unavailable" | "error" | "stale";
};
export type AccountType = "player" | "sponsor";
export type Player = {
  id: string; username: string; name: string; headline: string; bio: string;
  game: string; games: string[]; rank: string; country: string; available: boolean;
  color: string; connections: string[]; demo?: boolean; seeded?: boolean;
  game_profiles: Record<string, GameProfile>;
  account_type: AccountType; profile_href: string; sponsor_id?: string;
};
export type User = Player & { email: string; role: "player" | "admin" };
export type Comment = { id: string; author: Player; content: string; created_at: string };
export type Publisher = { id: string; type: "player" | "team" | "sponsor"; name: string; color: string; href: string };
export type Post = { id: string; author: Player; publisher: Publisher; content: string; game: string; created_at: string; likes: string[]; comments: Comment[]; demo?: boolean };
export type Match = { id: string; a: string | null; b: string | null; winner: string | null; score_a: number | null; score_b: number | null };
export type TeamSummary = {
  id: string; name: string; tag: string; headline: string; bio: string; games: string[];
  rank: string; country: string; recruiting: boolean; max_members: number;
  owner_id: string; members: string[]; color: string; demo?: boolean;
  competition_game: string;
};
export type Team = TeamSummary & { captain: Player; roster: Player[] };
export type Sponsor = {
  id: string; name: string; headline: string; bio: string; country: string;
  website: string; games: string[]; team_ids: string[]; owner_id: string;
  color: string; owner: Player; supported_teams: TeamSummary[]; demo?: boolean;
};
export type Participant = { id: string; name: string; type: "team" | "player"; href: string | null };
export type Tournament = {
  id: string; title: string; game: string; description: string; prize: string;
  capacity: number; starts_at: string; region: string; owner_id: string; owner_name: string; owner_href?: string | null;
  participants: string[]; status: "open" | "live" | "finished";
  rounds: Match[][]; demo?: boolean;
  mode: "solo" | "team"; team_size: number; rosters: Record<string, string[]>;
  participant_details: Participant[];
};
export const GAMES = ["Valorant", "League of Legends", "Counter-Strike 2", "Rocket League", "Fortnite", "EA Sports FC"];
