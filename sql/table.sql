/*
SQLyog Enterprise v12.5.0 (64 bit)
MySQL - 5.6.26 : Database - api_platform
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Table structure for table `api_execution` */

DROP TABLE IF EXISTS `api_execution`;

CREATE TABLE `api_execution` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `response_data` longtext,
  `status_code` int(11) DEFAULT NULL,
  `testplan_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `result` varchar(16) DEFAULT NULL,
  `diff` longtext,
  `execute_time` datetime DEFAULT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `testcase_id` int(11) NOT NULL,
  `server_ip` varchar(256) DEFAULT NULL,
  `client_ip` varchar(256) NOT NULL,
  `request_data` longtext NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_TestplanId` (`testplan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=98876 DEFAULT CHARSET=utf8;

/*Table structure for table `api_info` */

DROP TABLE IF EXISTS `api_info`;

CREATE TABLE `api_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `api_name` varchar(256) NOT NULL,
  `system_alias` varchar(64) NOT NULL,
  `protocol_type` varchar(32) NOT NULL,
  `method` varchar(16) NOT NULL,
  `api_desc` varchar(1024) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `api_level` varchar(2) NOT NULL,
  `request_header` longtext NOT NULL,
  `response_header` longtext NOT NULL,
  `tag` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2281 DEFAULT CHARSET=utf8;

/*Table structure for table `api_params` */

DROP TABLE IF EXISTS `api_params`;

CREATE TABLE `api_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `api_id` int(11) NOT NULL,
  `request_data` mediumtext NOT NULL,
  `response_data` mediumtext NOT NULL,
  `status_code` int(11) NOT NULL,
  `source` varchar(32) NOT NULL,
  `params_desc` varchar(1024) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `run_env` int(11) NOT NULL,
  `link_script` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_params_api_id` (`api_id`)
) ENGINE=InnoDB AUTO_INCREMENT=158392 DEFAULT CHARSET=utf8;

/*Table structure for table `api_testcase` */

DROP TABLE IF EXISTS `api_testcase`;

CREATE TABLE `api_testcase` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `summary` varchar(256) NOT NULL,
  `api_id` int(11) NOT NULL,
  `params_id` int(11) NOT NULL,
  `desc` varchar(1024) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `status` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31491 DEFAULT CHARSET=utf8;

/*Table structure for table `api_testplan` */

DROP TABLE IF EXISTS `api_testplan`;

CREATE TABLE `api_testplan` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `desc` varchar(1024) NOT NULL,
  `status` int(11) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `is_auto` int(11) NOT NULL,
  `start_time` datetime NOT NULL,
  `actual_start_time` datetime DEFAULT NULL,
  `actual_end_time` datetime DEFAULT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `run_env` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5813 DEFAULT CHARSET=utf8;

/*Table structure for table `auth_group` */

DROP TABLE IF EXISTS `auth_group`;

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `auth_group_permissions` */

DROP TABLE IF EXISTS `auth_group_permissions`;

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group_permissi_permission_id_84c5c92e_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `auth_permission` */

DROP TABLE IF EXISTS `auth_permission`;

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permissi_content_type_id_2f476e4b_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8;

/*Table structure for table `auth_user` */

DROP TABLE IF EXISTS `auth_user`;

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `auth_user_groups` */

DROP TABLE IF EXISTS `auth_user_groups`;

CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `auth_user_user_permissions` */

DROP TABLE IF EXISTS `auth_user_user_permissions`;

CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_perm_permission_id_1fbb5f2c_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_user_user_perm_permission_id_1fbb5f2c_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `cmdb_info` */

DROP TABLE IF EXISTS `cmdb_info`;

CREATE TABLE `cmdb_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(64) DEFAULT NULL COMMENT '应用别名',
  `product_team` varchar(64) DEFAULT NULL COMMENT '研发组',
  `product_line` varchar(64) DEFAULT NULL COMMENT '业务线',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `owner` varchar(64) DEFAULT NULL COMMENT '负责人',
  `description` varchar(1024) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `product_team_id` int(11) DEFAULT NULL,
  `product_line_id` int(11) DEFAULT NULL,
  `arch_type` varchar(32) DEFAULT NULL COMMENT '应用架构(.net,java,python)',
  `domain_name` varchar(512) DEFAULT NULL COMMENT '域名',
  `language` varchar(64) DEFAULT NULL COMMENT '语言类型',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1087 DEFAULT CHARSET=utf8;

/*Table structure for table `datascript` */

DROP TABLE IF EXISTS `datascript`;

CREATE TABLE `datascript` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `script_id` varchar(128) NOT NULL,
  `dept_name` varchar(1000) NOT NULL,
  `script_bu` varchar(1000) NOT NULL,
  `last_runtime` datetime NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `auto_run` int(11) NOT NULL,
  `run_times` int(11) NOT NULL,
  `run_cron` varchar(100) NOT NULL,
  `api_list` varchar(1000) NOT NULL,
  `testplan_id` varchar(300) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8;

/*Table structure for table `datascript_runlist` */

DROP TABLE IF EXISTS `datascript_runlist`;

CREATE TABLE `datascript_runlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `script_id` varchar(128) NOT NULL,
  `run_status` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `run_data` longtext NOT NULL,
  `testplan_id` varchar(300) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=312 DEFAULT CHARSET=utf8;

/*Table structure for table `db_config` */

DROP TABLE IF EXISTS `db_config`;

CREATE TABLE `db_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `system_alias` varchar(64) NOT NULL,
  `run_env` int(11) NOT NULL,
  `db_host` varchar(32) NOT NULL,
  `db_port` varchar(16) NOT NULL,
  `db_user` varchar(32) NOT NULL,
  `db_pwd` varchar(256) NOT NULL,
  `db_name` varchar(32) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

/*Table structure for table `db_restore_his` */

DROP TABLE IF EXISTS `db_restore_his`;

CREATE TABLE `db_restore_his` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `system_alias` varchar(64) NOT NULL,
  `db_conf_id` int(11) NOT NULL,
  `backup_table_name` varchar(64) NOT NULL,
  `origin_table_name` varchar(64) NOT NULL,
  `old_count` int(11) NOT NULL,
  `new_count` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `message` varchar(1024) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `testplan_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13498 DEFAULT CHARSET=utf8;

/*Table structure for table `django_admin_log` */

DROP TABLE IF EXISTS `django_admin_log`;

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin__content_type_id_c4bce8eb_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `django_content_type` */

DROP TABLE IF EXISTS `django_content_type`;

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;

/*Table structure for table `django_migrations` */

DROP TABLE IF EXISTS `django_migrations`;

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8;

/*Table structure for table `django_session` */

DROP TABLE IF EXISTS `django_session`;

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `project_env` */

DROP TABLE IF EXISTS `project_env`;

CREATE TABLE `project_env` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `domain` varchar(256) DEFAULT NULL,
  `project_id` int(11) DEFAULT NULL,
  `is_default` int(11) DEFAULT NULL,
  `is_delete` int(11) DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

/*Table structure for table `projects` */

DROP TABLE IF EXISTS `projects`;

CREATE TABLE `projects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `type` varchar(32) NOT NULL,
  `access_type` int(11) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `api_count` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=950 DEFAULT CHARSET=utf8;

/*Table structure for table `script_api_info` */

DROP TABLE IF EXISTS `script_api_info`;

CREATE TABLE `script_api_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `api_name` varchar(256) NOT NULL,
  `system_alias` varchar(64) NOT NULL,
  `protocol_type` varchar(32) NOT NULL,
  `method` varchar(16) NOT NULL,
  `api_desc` varchar(1024) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `api_level` varchar(2) NOT NULL,
  `request_header` longtext NOT NULL,
  `response_header` longtext NOT NULL,
  `tag` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2155 DEFAULT CHARSET=utf8;

/*Table structure for table `script_api_params` */

DROP TABLE IF EXISTS `script_api_params`;

CREATE TABLE `script_api_params` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `api_id` int(11) NOT NULL,
  `request_data` mediumtext NOT NULL,
  `response_data` mediumtext NOT NULL,
  `status_code` int(11) NOT NULL,
  `source` varchar(32) NOT NULL,
  `params_desc` varchar(1024) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  `run_env` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_params_api_id` (`api_id`)
) ENGINE=InnoDB AUTO_INCREMENT=141706 DEFAULT CHARSET=utf8;

/*Table structure for table `sys_config` */

DROP TABLE IF EXISTS `sys_config`;

CREATE TABLE `sys_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group` varchar(64) NOT NULL,
  `key` varchar(32) NOT NULL,
  `value` varchar(256) NOT NULL,
  `is_delete` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

/*Table structure for table `testcase_checkpoint` */

DROP TABLE IF EXISTS `testcase_checkpoint`;

CREATE TABLE `testcase_checkpoint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `testcase_id` int(11) NOT NULL,
  `check_type` varchar(16) NOT NULL,
  `check_param` varchar(256) NOT NULL,
  `operate` varchar(16) NOT NULL,
  `expect_value` varchar(256) NOT NULL,
  `weight` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;

/*Table structure for table `user_info` */

DROP TABLE IF EXISTS `user_info`;

CREATE TABLE `user_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `chName` varchar(50) NOT NULL,
  `empCode` varchar(50) NOT NULL,
  `ssoRedirectUrl` varchar(100) NOT NULL,
  `systemAlias` varchar(100) NOT NULL,
  `orgTitlePkid` varchar(50) NOT NULL,
  `loginName` varchar(50) NOT NULL,
  `pwd` varchar(50) NOT NULL,
  `isProd` varchar(50) DEFAULT NULL,
  `run_env` int(11) NOT NULL,
  `api_id` int(11) NOT NULL,
  `is_delete` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

/*Table structure for table `user_log` */

DROP TABLE IF EXISTS `user_log`;

CREATE TABLE `user_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(64) NOT NULL,
  `login_name` varchar(32) NOT NULL,
  `user_token` varchar(256) NOT NULL,
  `client_ip` varchar(16) NOT NULL,
  `server_ip` varchar(16) NOT NULL,
  `access_url` varchar(1024) NOT NULL,
  `create_time` datetime NOT NULL,
  `creator` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `updater` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2265 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
