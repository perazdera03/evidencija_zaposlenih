-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: evidencija_zaposlenih
-- ------------------------------------------------------
-- Server version	9.7.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'abd156c3-7a18-11f1-a65a-74563c9c9f75:1-366';

--
-- Table structure for table `korisnici`
--

DROP TABLE IF EXISTS `korisnici`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `korisnici` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ime` varchar(100) NOT NULL,
  `prezime` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `lozinka` varchar(255) NOT NULL,
  `rola` varchar(50) NOT NULL,
  `zaposleni_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `zaposleni_id` (`zaposleni_id`),
  CONSTRAINT `korisnici_ibfk_1` FOREIGN KEY (`zaposleni_id`) REFERENCES `zaposleni` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `korisnici`
--

LOCK TABLES `korisnici` WRITE;
/*!40000 ALTER TABLE `korisnici` DISABLE KEYS */;
INSERT INTO `korisnici` VALUES (7,'Admin','Administratorski','admin@test.com','scrypt:32768:8:1$i2kvZMmvqx6HoMxA$bf10a4b958ff8c59efdb76fd3ed786938e20a024e9af2844c4417cdd7ef76f042a5b2ec9ae8e664a49bb5bbc2c6b040b9b1343f5f97b7192a6d54c39b58deb44','administrator',9),(8,'Petar','Milojevic','petar@test.com','scrypt:32768:8:1$RJMvUwCfjHdTzMkw$d0e52409b391e1a0162f70730c94b67c405ce294ef925053659d876ad10bcd6cc19e28542ca98ac1cc79df9aa24dadf65a088df7e27b241d6c51253ee2b86a7b','administrator',11),(9,'Stefan','Jovanovic','stefan@test.com','scrypt:32768:8:1$vtUi3dHftrX4obm0$9cd491fb1cbe7a90ea560a3a07104d4f79061ec2c88b7469ef824eb7d0d9074c2296a75a878488f74d162d96fde302d0fab9e200902a895aed7994e0d7500125','menadzer',12),(10,'Vanja','Petrovic','vanja@test.com','scrypt:32768:8:1$HHa0snYbOjasnv0y$d96a7714cc7e413203619d8239faf79a71556667fc5fa3b9319436415c51c5664e71acdeb06a5f43033aa6253de49d0ab7b29f4dd4620fdac3f26d94364ba662','zaposleni',13),(11,'Nikola','Nikolic','nikola@test.com','scrypt:32768:8:1$p0qBkamWp9HMLpqH$d5a97dc1629ededaeeefcf8458f9bfbb2670ca2f9003b1585ab10be07f238cd018c2755cbe9aaeda7196569a19277db0d4063f49f8701fa1d75399c0236249c2','zaposleni',14),(12,'Zeljko','Mitrovic','zeljko@test.com','scrypt:32768:8:1$b8EaTZhra9NI0Wzz$9ad10bd213b5172572f7e5af03c6cc3ffe963244ed786236dca69600e336cb44fc25198deb4d94544ebfef8716398d21db96e0607ab8fb57841db3b3d6c44f5d','zaposleni',15),(13,'Danilo','Danilovic','danilo@test.com','scrypt:32768:8:1$SMqIr0i30De1dprY$57cf9d906828cb8bd770ac4488400b104abc5871e6941ec5f04133676ff86006761c17cd67fa9dfb9e75ab95730be76363638b2b40ca8d5dd9ab805cc7eecf7f','zaposleni',16);
/*!40000 ALTER TABLE `korisnici` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ocene_ucinka`
--

DROP TABLE IF EXISTS `ocene_ucinka`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ocene_ucinka` (
  `id` int NOT NULL AUTO_INCREMENT,
  `zaposleni_id` int NOT NULL,
  `projekat_id` int NOT NULL,
  `ocena` smallint NOT NULL,
  `datum` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `zaposleni_id` (`zaposleni_id`),
  KEY `projekat_id` (`projekat_id`),
  CONSTRAINT `ocene_ucinka_ibfk_1` FOREIGN KEY (`zaposleni_id`) REFERENCES `zaposleni` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ocene_ucinka_ibfk_2` FOREIGN KEY (`projekat_id`) REFERENCES `projekti` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ocene_ucinka`
--

LOCK TABLES `ocene_ucinka` WRITE;
/*!40000 ALTER TABLE `ocene_ucinka` DISABLE KEYS */;
INSERT INTO `ocene_ucinka` VALUES (1,13,8,2,'1111-11-11'),(2,13,9,3,'2222-05-23'),(3,14,9,3,'6666-06-06');
/*!40000 ALTER TABLE `ocene_ucinka` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projekti`
--

DROP TABLE IF EXISTS `projekti`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projekti` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sifra` varchar(30) NOT NULL,
  `naziv` varchar(100) NOT NULL,
  `bodovi_vrednosti` int NOT NULL,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projekti`
--

LOCK TABLES `projekti` WRITE;
/*!40000 ALTER TABLE `projekti` DISABLE KEYS */;
INSERT INTO `projekti` VALUES (8,'1234','Projekat1',5,'zavrsen'),(9,'12345','Projekat2',4,'aktivan');
/*!40000 ALTER TABLE `projekti` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zaposleni`
--

DROP TABLE IF EXISTS `zaposleni`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `zaposleni` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ime` varchar(100) NOT NULL,
  `prezime` varchar(100) NOT NULL,
  `maticni_broj` varchar(20) NOT NULL,
  `jmbg` bigint NOT NULL,
  `datum_rodjenja` date DEFAULT NULL,
  `broj_telefona` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `godina_zaposlenja` smallint DEFAULT NULL,
  `ukupno_bodova` int DEFAULT '0',
  `prosecna_ocena` float DEFAULT '0',
  `slika` varchar(255) DEFAULT NULL,
  `bracni_status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zaposleni`
--

LOCK TABLES `zaposleni` WRITE;
/*!40000 ALTER TABLE `zaposleni` DISABLE KEYS */;
INSERT INTO `zaposleni` VALUES (9,'Admin','Administratorski','ADMIN-001',1,NULL,'None','admin@test.com',NULL,0,0,'9_monkey-thinking-meme-monkey-thinking-sticker.gif','udovac_udovica'),(11,'Petar','Milojevic','11111111',11,NULL,'123','petar@test.com',NULL,0,0,NULL,'neozenjen_neudata'),(12,'Stefan','Jovanovic','666666666',3333,NULL,'312314','stefan@test.com',NULL,0,0,NULL,NULL),(13,'Vanja','Petrovic','312331',222,NULL,'131231','vanja@test.com',NULL,9,2.5,NULL,NULL),(14,'Nikola','Nikolic','55555',5555,NULL,'5555','nikola@test.com',NULL,4,3,NULL,NULL),(15,'Zeljko','Mitrovic','5555',1223,'3333-03-31','421421','zeljko@test.com',5,0,0,'1223_usertile14.bmp','neozenjen_neudata'),(16,'Danilo','Danilovic','111111111',3213132312,'7777-05-06','0629627944','danilo@test.com',3232,0,0,'3213132312_usertile12.bmp','neozenjen_neudata');
/*!40000 ALTER TABLE `zaposleni` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-11 17:14:57
