DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS `room`;
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
)

CREATE TABLE `room_member` (
  `id` bigint NOT NULL,
  `live_id` bigint NOT NULL,
)
