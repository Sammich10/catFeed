DROP TABLE IF EXISTS feedtimes;
DROP TABLE IF EXISTS feedlog;
DROP TABLE IF EXISTS users;

CREATE TABLE feedtimes(
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"time" TEXT,
	"size" TEXT
);

CREATE TABLE feedlog(
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"time" TEXT,
	"date" TEXT,
	"size" TEXT,
	"type" TEXT
);

CREATE TABLE users(
	"user_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"email" TEXT,
	"password" TEXT
);

INSERT INTO feedtimes ("id") VALUES (1),(2)
