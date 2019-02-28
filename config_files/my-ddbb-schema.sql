-- MySQL dump 10.13  Distrib 5.7.25, for Linux (x86_64)
--
-- Host: localhost    Database: par
-- ------------------------------------------------------
-- Server version	5.7.25-0ubuntu0.16.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account_balance`
--

DROP TABLE IF EXISTS `account_balance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_balance` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_id` varchar(32) DEFAULT NULL,
  `account_name` varchar(63) DEFAULT NULL,
  `asset_id` varchar(32) DEFAULT NULL,
  `amount` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_account_balance_updated_at` (`updated_at`),
  KEY `ix_account_balance_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `block`
--

DROP TABLE IF EXISTS `block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `block` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `block_id` varchar(256) DEFAULT NULL,
  `block_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_block_block_id` (`block_id`),
  UNIQUE KEY `uq_block_block_num` (`block_num`),
  KEY `ix_block_created_at` (`created_at`),
  KEY `ix_block_updated_at` (`updated_at`)
) ENGINE=InnoDB AUTO_INCREMENT=18383449 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `last_error`
--

DROP TABLE IF EXISTS `last_error`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `last_error` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `transfer_id` int(11) NOT NULL,
  `description` text,
  `block_num` int(11) DEFAULT NULL,
  `trx_in_block` int(11) DEFAULT NULL,
  `op_in_trx` int(11) DEFAULT NULL,
  `txid` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_last_error_transfer_id` (`transfer_id`),
  KEY `ix_last_error_created_at` (`created_at`),
  KEY `ix_last_error_updated_at` (`updated_at`),
  KEY `last_error_txid` (`txid`),
  CONSTRAINT `fk_last_error_transfer_id_transfer` FOREIGN KEY (`transfer_id`) REFERENCES `transfer` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=304 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `push_info`
--

DROP TABLE IF EXISTS `push_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `push_info` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `push_id` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_push_info_name` (`name`),
  KEY `ix_push_info_updated_at` (`updated_at`),
  KEY `ix_push_info_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=1606 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transfer`
--

DROP TABLE IF EXISTS `transfer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transfer` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `block_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_id` varchar(32) DEFAULT NULL,
  `from_name` varchar(63) DEFAULT NULL,
  `to_id` varchar(32) DEFAULT NULL,
  `to_name` varchar(63) DEFAULT NULL,
  `amount` bigint(20) DEFAULT NULL,
  `amount_asset` varchar(32) DEFAULT NULL,
  `fee` int(11) DEFAULT NULL,
  `fee_asset` varchar(32) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `block_num` int(11) DEFAULT NULL,
  `trx_in_block` int(11) DEFAULT NULL,
  `op_in_trx` int(11) DEFAULT NULL,
  `processed` int(11) DEFAULT '0',
  `memo` text,
  PRIMARY KEY (`id`),
  KEY `fk_transfer_block_id_block` (`block_id`),
  KEY `ix_transfer_created_at` (`created_at`),
  KEY `ix_transfer_updated_at` (`updated_at`),
  KEY `transfer_processed_idx` (`processed`),
  CONSTRAINT `fk_transfer_block_id_block` FOREIGN KEY (`block_id`) REFERENCES `block` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6376 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_data`
--

DROP TABLE IF EXISTS `user_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_data` (
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `wallet_name` varchar(63) DEFAULT NULL,
  `emp_nombre` varchar(64) DEFAULT NULL,
  `emp_rubro` varchar(64) DEFAULT NULL,
  `emp_direccion` varchar(64) DEFAULT NULL,
  `emp_web` varchar(64) DEFAULT NULL,
  `contacto_email` varchar(64) DEFAULT NULL,
  `contacto_tel` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_user_data_created_at` (`created_at`),
  KEY `ix_user_data_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-02-28 18:43:31
