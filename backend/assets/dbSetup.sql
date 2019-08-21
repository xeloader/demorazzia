DROP DATABASE demorazzia;
CREATE DATABASE demorazzia;
USE demorazzia;

CREATE TABLE propositions (
  id int NOT NULL AUTO_INCREMENT,
  type varchar(255),
  body LONGTEXT,
  title varchar(255),
  motion_id varchar(255) UNIQUE,
  url TEXT,
  pdf_url TEXT,
  dedicated_to varchar(255),
  yrkanden LONGTEXT,
  added date,
  category varchar(255),

  PRIMARY KEY (id)
);

CREATE TABLE parties (
  id int NOT NULL AUTO_INCREMENT,
  symbol varchar(255),

  PRIMARY KEY (id)
);

CREATE TABLE politicians (
  id int NOT NULL AUTO_INCREMENT,
  party_id int,
  name varchar(255),
  picture_url TEXT,
  url TEXT,

  PRIMARY KEY (id),
  FOREIGN KEY (party_id) REFERENCES parties(id)
);

CREATE TABLE proposition_senders (
  id int NOT NULL AUTO_INCREMENT,
  proposition_id int,
  politician_id int,
  PRIMARY KEY (id),
  FOREIGN KEY (proposition_id) REFERENCES propositions(id),
  FOREIGN KEY (politician_id) REFERENCES politicians(id)
);

CREATE TABLE proposition_votes (
  id int NOT NULL AUTO_INCREMENT,
  proposition_id int,
  vote int,
  PRIMARY KEY (id),
  FOREIGN KEY (proposition_id) REFERENCES propositions(id)
);