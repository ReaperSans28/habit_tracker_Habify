CREATE TABLE `users`(
    `telegram_id` BIGINT UNSIGNED NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `notifications_enabled` BOOLEAN NOT NULL DEFAULT '0',
    `time_zone` SMALLINT NOT NULL DEFAULT '3' COMMENT 'UTC+ N time zone',
    PRIMARY KEY(`telegram_id`)
);
CREATE TABLE `habits`(
    `telegram_id` BIGINT UNSIGNED NOT NULL,
    `habit_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `created_at` DATETIME NOT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT '1',
    `reminder_time` TIME NOT NULL,
    `schedule` JSON NOT NULL COMMENT '{Mon: T/F, Tue: T/F, Wed: T/F, Thu: T/F, Fri: T/F, Sat: T/F, Sun: T/F}',
    `image_path` VARCHAR(255) NULL,
    `public` BOOLEAN NOT NULL DEFAULT '0',
    PRIMARY KEY(`telegram_id`)
);
ALTER TABLE
    `habits` ADD PRIMARY KEY(`habit_id`);
CREATE TABLE `habit_filters`(
    `habit_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `habit_type` VARCHAR(255) NOT NULL,
    `season` JSON NULL COMMENT '{Winter: T/F, Spring: T/F, Summer: T/F, Autumn: T/F}',
    `duration_minutes` SMALLINT NOT NULL,
    `location` VARCHAR(255) NOT NULL
);
ALTER TABLE
    `habits` ADD CONSTRAINT `habits_habit_id_foreign` FOREIGN KEY(`habit_id`) REFERENCES `habit_filters`(`habit_id`);
ALTER TABLE
    `habits` ADD CONSTRAINT `habits_telegram_id_foreign` FOREIGN KEY(`telegram_id`) REFERENCES `users`(`telegram_id`);