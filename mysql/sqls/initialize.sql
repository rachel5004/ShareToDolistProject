CREATE DATABASE IF NOT EXISTS todolist;
USE todolist;

CREATE TABLE IF NOT EXISTS `member` (
	`ID` VARCHAR(50) NOT NULL,
	`PWD` VARCHAR(50) NULL DEFAULT NULL,
	PRIMARY KEY (`ID`)
);