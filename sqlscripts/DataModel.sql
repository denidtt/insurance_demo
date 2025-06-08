-- DDL for the data model of the received smaple data files has been modified 
-- DataModel for FACT Tables(Policy , Claim and Invoice) is built  to store  SCD type 2  data ,which is ingested ingested based on the day .This will help to study and track the chnages over time . Since this will be used for anlylytics , always good to have the history 
-- Business Layer can be built on top of this which can hold the most recent version of data (one row per  subject like policy ,invoice ,claim)



use MODELED;


CREATE TABLE if not exists `policy` (
  `id` varchar(50) primary KEY NOT NULL,
  `policy_id` varchar(50) NOT NULL,
  `policy_number` varchar(50) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `application_id` varchar(50) DEFAULT NULL,
  `product_id` varchar(50) NOT NULL,
  `insured_date_of_birth` date DEFAULT NULL,
  `insured_gender_id` varchar(50) DEFAULT null,
  `issue_date` DATETIME DEFAULT NULL,
  `effective_date` DATETIME DEFAULT null,
  `process_date` DATE not null
) ;



CREATE TABLE if not exists `claim` (
  `id` varchar(50) primary key NOT NULL,
  `claim_id`  varchar(50) NOT NULL ,
  `type` varchar(50) DEFAULT NULL,
  `status_id` varchar(50) DEFAULT NULL,
  `policy_id` varchar(50) NOT NULL,
  `submit_date` DATETIME DEFAULT NULL,
  `payment_date` DATETIME DEFAULT NULL,
  `admission_date` DATETIME DEFAULT NULL,
  `total_billed_amount` DOUBLE DEFAULT NULL,
  `total_base_payable_amount` DOUBLE DEFAULT null,
  `process_date` DATE not null
);

CREATE TABLE if not exists `invoice` (
  `id` varchar(50) primary key not NULL,
  `invoice_id` varchar(50)  not NULL,
  `invoice_type` varchar(50) DEFAULT NULL,
  `policy_id` varchar(50) NOT NULL,
  `coverage_start_date` DATETIME DEFAULT NULL,
  `coverage_end_date` DATETIME DEFAULT NULL,
  `due_date` DATETIME DEFAULT NULL,
  `status_id` varchar(50) DEFAULT NULL,
  `pre_levy_amount` DOUBLE DEFAULT NULL,
  `total_amount` DOUBLE DEFAULT NULL,
  `refund_date`  DATETIME DEFAULT NULL,
  `charge_date` DATETIME DEFAULT null,
  `process_date` DATE not null
)  ;


create table if not exists `gender` (
`id` varchar(50) primary key NOT NULL,
`gender`  varchar(50) not null ,
`process_date` DATE not null
) ;



CREATE TABLE if not exists `product` (
  `id` varchar(50) primary KEY NOT NULL,
  `product` varchar(50) DEFAULT null,
  `process_date` DATE not null
  ) ;


CREATE TABLE if not exists `status` (
`id` varchar(50) primary key NOT NULL,
`status` varchar(50) default null,
`module` varchar(50) default null,
 `process_date` DATE not null
);

