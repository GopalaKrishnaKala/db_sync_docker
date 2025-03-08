# Database Sync with Docker & Python

## Assumptions and Prerequisite
- Docker is installed in the machine
- Docker version 3.8 is being used
- I am building a PostgreSQL database to run and insert data into it. 
- db1 and db2 are the databases being created.
- I have created a table with two columns (id and name) where id is the primary key and inserted random 100 rows into the Database.
- Python 3.x is installed in the machine along with psycopg2 library
- Run "pip install psycopg2" in command line to install the psycopg2 library
- Verified on MacOS Sequoia and Windows OS

## Project Overview
- This project sets up two PostgreSQL databases with Docker Compose.
- It populates the first database (db1) with 100 records, replicates them to the second database (db2).
- Verifies data consistency and integrity by computing and comparing the hash of the tables. Second verification is done by validating the row count.
- Once it is done, it tears down the database instances.
- Overview of docker-compose.yml:
	- Version is 3.8
	- Two database services (db1 and db2)
	- They both use Postgres:15
	- Containers used are: database_1 and database_2
	- They restart when there is a failure
	- Port mapping used is 5433:5432
	- db1 executes the init.sql script and db2 syncs the data from db1

## How to Run

### 1️. Clone the Repository and move into the directory

git clone https://github.com/GopalaKrishnaKala/db_sync_docker

cd db_sync_docker

### 2. Start docker-compose
docker-compose up -d
- With this container for database1 and database2 will be up and running.
- Note: If docker-compose up -d fails, ensure Docker is running. (Use the command "docker ps" to verify if the docker is up and running)
- Note: If you get any warning, please ignore it.

### 3. Run the python script
python sync_script.py
- This will do the following:
	- 1. Insert 100 rows into the database.
	- 2. Synchronize data from db1 to db2.
	- 3. Verifies the sync:
		- 3.1 Checks row count
		- 3.2 Hash verification to check if both the tables are identical (Verifies data consistency and integrity by computing and comparing the hash of the tables).
	- 4. Display the First 5 rows from db1 and db2 to view the data

### 4. Tear down the database instances
docker-compose down
- This will tear down the database instance.