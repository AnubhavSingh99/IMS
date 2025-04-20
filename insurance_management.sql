-- Please create the database 'mysql_python' manually before running this script.
-- For example, run: CREATE DATABASE mysql_python;

-- USE mysql_python;

-- Create customer_info table
CREATE TABLE IF NOT EXISTS customer_info (
  Customer_id INT PRIMARY KEY,
  Customer_Name VARCHAR(255) NOT NULL,
  Customer_Age INT NOT NULL,
  Customer_Gender VARCHAR(10) NOT NULL, -- Allowed values: Male, Female, Other
  Contact_Number VARCHAR(20) NOT NULL,
  Email_Id VARCHAR(255) NOT NULL,
  Password VARCHAR(255) NOT NULL,
  Address TEXT NOT NULL,
  Nominee_Name VARCHAR(255) NOT NULL,
  Nominee_relationship VARCHAR(255) NOT NULL
);

-- Create policy_info table
CREATE TABLE IF NOT EXISTS policy_info (
  Customer_id INT,
  Policy_id INT,
  Policy_Name VARCHAR(255) NOT NULL,
  Sum_Assured INT NOT NULL,
  Premium VARCHAR(20) NOT NULL,
  Term VARCHAR(255) NOT NULL,
  FOREIGN KEY (Customer_id) REFERENCES customer_info(Customer_id)
);
