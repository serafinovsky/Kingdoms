db = db.getSiblingDB(process.env.CABINET_MONGO_DB);

db.createUser({
  user: process.env.CABINET_MONGO_USER,
  pwd: process.env.CABINET_MONGO_PASSWORD,
  roles: [
    {
      role: "readWrite",
      db: process.env.CABINET_MONGO_DB,
    },
  ],
});
