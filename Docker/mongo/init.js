// Runs only when MongoDB initializes an empty volume.
// The backend seeds labelled demonstration data.
const database = db.getSiblingDB("respectdb");
database.createUser({
  user: process.env.MONGO_APP_USER,
  pwd: process.env.MONGO_APP_PASSWORD,
  roles: [{ role: "readWrite", db: "respectdb" }],
});
for (const collection of ["users", "sessions", "posts", "tournaments", "teams", "sponsors", "settings", "reports", "moderation_actions", "game_accounts"]) {
  database.createCollection(collection);
}
