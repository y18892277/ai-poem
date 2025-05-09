/*
 Navicat Premium Data Transfer

 Source Server         : pythontry
 Source Server Type    : MySQL
 Source Server Version : 80037 (8.0.37)
 Source Host           : localhost:3306
 Source Schema         : poetry_battle

 Target Server Type    : MySQL
 Target Server Version : 80037 (8.0.37)
 File Encoding         : 65001

 Date: 09/05/2025 09:19:47
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for battles
-- ----------------------------
DROP TABLE IF EXISTS `battles`;
CREATE TABLE `battles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `season_id` int NOT NULL,
  `score` int NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `current_poetry_id` int NULL DEFAULT NULL,
  `rounds` int NULL DEFAULT NULL,
  `current_round` int NULL DEFAULT NULL,
  `battle_records` json NULL,
  `total_time` int NULL DEFAULT NULL,
  `avg_response_time` float NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `season_id`(`season_id` ASC) USING BTREE,
  INDEX `current_poetry_id`(`current_poetry_id` ASC) USING BTREE,
  INDEX `ix_battles_id`(`id` ASC) USING BTREE,
  CONSTRAINT `battles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `battles_ibfk_2` FOREIGN KEY (`season_id`) REFERENCES `seasons` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `battles_ibfk_3` FOREIGN KEY (`current_poetry_id`) REFERENCES `poetry` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of battles
-- ----------------------------
INSERT INTO `battles` VALUES (1, 1, 1, 0, 'active', NULL, 0, 1, '{}', 0, 0, '2025-05-09 00:39:55', '2025-05-09 00:39:55');
INSERT INTO `battles` VALUES (2, 1, 1, 0, 'active', NULL, 0, 1, '{}', 0, 0, '2025-05-09 00:40:08', '2025-05-09 00:40:08');
INSERT INTO `battles` VALUES (3, 1, 1, 0, 'active', NULL, 0, 1, '{}', 0, 0, '2025-05-09 00:40:10', '2025-05-09 00:40:10');
INSERT INTO `battles` VALUES (4, 1, 1, 0, 'active', NULL, 0, 1, '{}', 0, 0, '2025-05-09 00:42:14', '2025-05-09 00:42:14');

-- ----------------------------
-- Table structure for poetry
-- ----------------------------
DROP TABLE IF EXISTS `poetry`;
CREATE TABLE `poetry`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `author` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `dynasty` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `tags` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `difficulty` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_poetry_id`(`id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of poetry
-- ----------------------------
INSERT INTO `poetry` VALUES (1, '静夜思', '李白', '唐', '床前明月光，疑是地上霜。举头望明月，低头思故乡。', '诗', '思乡,月亮', 1, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (2, '春晓', '孟浩然', '唐', '春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。', '诗', '春天,自然', 1, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (3, '登鹳雀楼', '王之涣', '唐', '白日依山尽，黄河入海流。欲穷千里目，更上一层楼。', '诗', '登高,壮志', 1, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (4, '望庐山瀑布', '李白', '唐', '日照香炉生紫烟，遥看瀑布挂前川。飞流直下三千尺，疑是银河落九天。', '诗', '山水,壮观', 2, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (5, '江雪', '柳宗元', '唐', '千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。', '诗', '冬天,孤独', 1, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (6, '咏柳', '贺知章', '唐', '碧玉妆成一树高，万条垂下绿丝绦。不知细叶谁裁出，二月春风似剪刀。', '诗', '春天,柳树', 2, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (7, '登高', '杜甫', '唐', '风急天高猿啸哀，渚清沙白鸟飞回。无边落木萧萧下，不尽长江滚滚来。', '诗', '秋天,登高', 2, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (8, '相思', '王维', '唐', '红豆生南国，春来发几枝。愿君多采撷，此物最相思。', '诗', '爱情,相思', 1, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (9, '山居秋暝', '王维', '唐', '空山新雨后，天气晚来秋。明月松间照，清泉石上流。', '诗', '秋天,山水', 1, '2025-05-08 22:41:02', '2025-05-08 22:41:02');
INSERT INTO `poetry` VALUES (10, '鹿柴', '王维', '唐', '空山不见人，但闻人语响。返景入深林，复照青苔上。', '诗', '山水,禅意', 2, '2025-05-08 22:41:02', '2025-05-08 22:41:02');

-- ----------------------------
-- Table structure for seasons
-- ----------------------------
DROP TABLE IF EXISTS `seasons`;
CREATE TABLE `seasons`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_seasons_id`(`id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of seasons
-- ----------------------------
INSERT INTO `seasons` VALUES (1, '第一赛季', '2025-05-08 22:41:02', '2025-06-07 22:41:02', 'active', '2025-05-08 22:41:02', '2025-05-08 22:41:02');

-- ----------------------------
-- Table structure for user_favorite_poetry
-- ----------------------------
DROP TABLE IF EXISTS `user_favorite_poetry`;
CREATE TABLE `user_favorite_poetry`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `poetry_id` int NOT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `poetry_id`(`poetry_id` ASC) USING BTREE,
  INDEX `ix_user_favorite_poetry_id`(`id` ASC) USING BTREE,
  CONSTRAINT `user_favorite_poetry_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `user_favorite_poetry_ibfk_2` FOREIGN KEY (`poetry_id`) REFERENCES `poetry` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_favorite_poetry
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `hashed_password` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `avatar` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `is_active` tinyint(1) NULL DEFAULT NULL,
  `total_score` int NULL DEFAULT NULL,
  `win_count` int NULL DEFAULT NULL,
  `lose_count` int NULL DEFAULT NULL,
  `draw_count` int NULL DEFAULT NULL,
  `win_rate` float NULL DEFAULT NULL,
  `max_win_streak` int NULL DEFAULT NULL,
  `current_win_streak` int NULL DEFAULT NULL,
  `highest_score` int NULL DEFAULT NULL,
  `current_rank` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `rank_score` int NULL DEFAULT NULL,
  `total_battles` int NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE,
  INDEX `ix_users_id`(`id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'y123', '937670285@qq.com', '$2b$12$NV7yBulRkAV8Q3zHIe3zpuL9V.i.5NumdKCdg8Qu.UhasWpQy/42G', 'chen', NULL, 1, 0, 0, 0, 0, 0, 0, 0, 0, '新手', 0, 0, '2025-05-09 00:39:45', '2025-05-09 00:39:45');

SET FOREIGN_KEY_CHECKS = 1;
