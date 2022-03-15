DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `room`;
DROP TABLE IF EXISTS `room_member`;
DROP TABLE IF EXISTS `judge`;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  `leader_card_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`)
);

CREATE TABLE `room` (
  `room_id` bigint NOT NULL AUTO_INCREMENT,
  `live_id` int DEFAULT NULL,
  `joined_user_count` int DEFAULT NULL,
  `max_user_count` int DEFAULT NULL,
  PRIMARY KEY (`room_id`)
);

CREATE TABLE `room_member` (
  `id` bigint NOT NULL,
  `room_id` bigint NOT NULL,
  `select_difficulty` int DEFAULT NULL,
  `is_host` int DEFAULT NULL,
  `score` int DEFAULT NULL,
  PRIMARY KEY (`id`, `room_id`)
);

CREATE TABLE `judge`(
  `judge_id` bigint NOT NULL AUTO_INCREMENT,
  `id` bigint DEFAULT NULL,
  `room_id` bigint DEFAULT NULL,
  `judge_count` bigint DEFAULT NULL,
  PRIMARY KEY (`judge_id`)
);

INSERT INTO `user` (`name`, `token`, `leader_card_id`) VALUES ("kamo", "abc", 4);
