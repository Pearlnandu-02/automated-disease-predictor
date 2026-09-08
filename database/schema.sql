-- AI-Based Personalized Healthcare Risk Assessment System Database Schema

CREATE DATABASE IF NOT EXISTS `healthcare_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `healthcare_db`;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Health Assessments Table
CREATE TABLE IF NOT EXISTS `health_assessments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `disease` VARCHAR(50) NOT NULL, -- 'Diabetes' or 'Heart Disease'
  `input_data` LONGTEXT NOT NULL, -- JSON string of input parameters
  `risk_level` VARCHAR(20) NOT NULL, -- 'LOW', 'MODERATE', 'HIGH'
  `probability` FLOAT NOT NULL, -- e.g., 0.68 for 68%
  `feature_importance` LONGTEXT DEFAULT NULL, -- JSON string of key contributing factors
  `recommendations` LONGTEXT DEFAULT NULL, -- JSON string of preventive recommendations
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
