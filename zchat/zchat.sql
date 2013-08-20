CREATE DATABASE IF NOT EXISTS `zchat`;
USE `zchat`;

CREATE TABLE IF NOT EXISTS `tb_user` (
	`user_name` 		CHAR(32) 	NOT NULL,
	`password` 			CHAR(32) 	NOT NULL,
	`user_type` 		INT(1) 		NOT NULL DEFAULT '1',
	`last_login_time` 	DATETIME 	NOT NULL DEFAULT '1970-01-01 00:00:00',
	`shutup_until` 		DATETIME 	NOT NULL DEFAULT '1970-01-01 00:00:00',
	`online` 			INT(1) 		NOT NULL DEFAULT '0',
	`shutup` 			INT(1) 		NOT NULL DEFAULT '0',
	`total_online_time` INT(10) 	NOT NULL DEFAULT '0',
	PRIMARY KEY (`user_name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `tb_msg` (
	`id`				INT(10)		NOT NULL AUTO_INCREMENT,
	`user_name` 		CHAR(32)	NOT NULL,
	`recv_time` 		DATETIME 	NOT NULL,
	`msg` 				TEXT 	 	NOT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB;
