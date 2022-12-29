# Introduction

## What is SQL?

Structured Query Language. It's a domain-specific language designed to manage data in a Relational Database Management System (RDBMS). It's been extended and updated many times, both in its official ANSI definition, and in implementations of it like MySQL and PostgreSQL.

### What is MySQL?

It's an extremely popular row-based relational database implementing and extending ANSI SQL. It's unfortunately owned by Oracle, but if you'd prefer, the MariaDB fork is essentially the same thing.

### How is it pronounced?

Officially, "My Ess Que Ell," but since the SQL language was originally called SEQUEL ("Structured English Query Language"), and only changed due to trademark issues, I feel at ease saying "My Sequel." However, this tends to bring out pedants who love to haughtily correct your pronunciation, so do what you will. For what it's worth, I also pronounce kubectl (the Kubernetes CLI tool) as "kube cuddle," so I may not be the greatest influence.

### What is PostgreSQL?

It's another extremely popular row-based (but not always) relational database implementing and extending ANSI SQL. There are many forks and plugins, which allow it to perform a variety of roles that strict SQL would struggle with.

### How is it prounounced?

"Post Gres Que Ell," but it's also common and acceptable to drop the suffix and say "Post Gres," written Postgres.

## Basic definitions

### SQL sub-languages

All of these can be grouped as SQL, and some of them can also be combined - `DQL` is often merged with `DML`, for example. Knowing that `DML` is generally operating on a single record at a time (but may be batched), and that `DDL` is generally operating on an entire table or schema at a time suffices for now.

* DCL
  * Data Control Language. `GRANT`, `REVOKE`.
* DDL
  * Data Definition Language. `ALTER`, `CREATE`, `DROP`, `TRUNCATE`.
* DML
  * Data Manipulation Language. `CALL`, `DELETE`, `INSERT`, `LOCK`, `SELECT (with FROM or WHERE)`, `UPDATE`.
* DQL
  * Data Query Language. `SELECT`.
* TCL
  * Transaction Control Language. `COMMIT`, `ROLLBACK`, `SAVEPOINT`.

### Other definitions

* B+ tree
  * An `_m_-ary tree`  data structure that is self-balancing, with a variable number of children per node. It differs from the `B-tree` in that an individual data node can have either keys or children, but not both. It has `O(log(n))` time complexity for insertion, search, and deletion. It is frequently used both for filesystems and for RDBMS.
* Block
  * The lowest reasonable level of data storage (above individual bits). Historically sized at 512 bytes due to hard drive sector sizes, but generally sized at 4 KiB in modern drives, and SSDs. Enterprise drives sometimes have 520 byte block sizes (or 4160 bytes for the 4 KiB-adjacent size), with the extra 8 bytes being used for data integrity calculations.
* Filesystem
  * A method for the operating system to store data. May include features like copy-on-write, encryption, journaling, pre-allocation, SSD management, volume management, and more. Modern examples include APFS (default for Apple products), ext4 (default for most Linux distributions), NTFS (default for Windows), XFS (default for Red Hat and its downstream), and ZFS (default for FreeBSD).
* Schema
  * A logical grouping of database objects, e.g. tables, indices, etc. Often called a database, but technically, the database may contain any number of schemas, each with its own unique (or shared!) set of data, access policies, etc.
* Table
  * A logical grouping of data, of varying or similar types. May contain constraints, indices, etc.
* Tablespace
  * The link between the logical storage layer (tables, indices) and the physical storage layer (the disk's filesystem).

## What is a relational database?

It's what most people probably think of when they think of a database. Broadly speaking, data is related to other data in some manner. For example, observe these two tables (tl;dr a logical grouping of data):

```sql
mysql> SHOW COLUMNS FROM users;
+------------+----------+------+-----+---------+----------------+
| Field      | Type     | Null | Key | Default | Extra          |
+------------+----------+------+-----+---------+----------------+
| id         | bigint   | NO   | PRI | NULL    | auto_increment |
| first_name | char(64) | YES  |     | NULL    |                |
| last_name  | char(64) | YES  |     | NULL    |                |
| user_id    | bigint   | NO   | UNI | NULL    |                |
+------------+----------+------+-----+---------+----------------+
4 rows in set (0.09 sec)
```

```sql
mysql> SHOW COLUMNS FROM zaps;
+-----------------+-----------+------+-----+---------+----------------+
| Field           | Type      | Null | Key | Default | Extra          |
+-----------------+-----------+------+-----+---------+----------------+
| id              | bigint    | NO   | PRI | NULL    | auto_increment |
| zap_id          | bigint    | NO   | UNI | NULL    |                |
| created_at      | timestamp | YES  |     | NULL    |                |
| last_updated_at | timestamp | YES  |     | NULL    |                |
| owned_by        | bigint    | NO   |     | NULL    |                |
| used_by         | bigint    | NO   |     | NULL    |                |
+-----------------+-----------+------+-----+---------+----------------+
6 rows in set (0.02 sec)
```

Table `users` has four columns - `id`, `first_name`, `last_name`, and `user_id`. Table `zaps` has six columns - `id`, `zap_id`, `created_at`, `last_updated_at`, `owned_by`, and `used_by`.

Although it isn't explicitly defined or enforced, there is an implicit relationship between these two tables via `users.user_id` and `zaps.owned_by`. Thus, a query like `SELECT zap_id, owned_by FROM zaps JOIN users ON user_id = owned_by;` could use that relationship. Ideally, there would be additional constraints like foreign keys established to ensure referential integrity, but this example suffices for now.

Also, generally speaking, RDBMS are ACID-compliant (but not always).

## What is ACID?

ACID is a set of four properties that, if implemented correctly, guarantee data validity:

* Atomicity
  * In a given transaction, each statement must either completely succeed, or fail. If any statement in a transaction fails, the entire transaction must fail.
* Consistency
  * A given transaction can only move a database from one valid and consistent state to another.
* Isolation
  * Even with concurrent transactions executing, the database must end up in the same state as if each transaction were executed sequentially.
* Durability
  * Once a transaction is committed, it must remain committed in the event of a system failure.

Note that the lack of one or more of these properties does not necessarily mean that data committed is invalid, only that the guarantees granted by that particular property must be accounted for elsewhere. A common counter-example of this is Eventual Consistency with distributed systems.

# MySQL Components

As of MySQL 8.0, this is the official architecture drawing:

[!MySQL 8.0 architecture](https://cdn.zappy.app/a92561fb248524eb0927cc0ed618de52.png)

* Connector
  * Also known as the Client, this is how you interact with the database, be it manually via a CLI client tool, or via a program using the DB.
* Server
  * Parser
    * This component receives a human-readable query, and translates it into machine-readable commands, via a lexical scanner and a grammar rule module.
  * Optimizer
    * This component attempts to optimize a given query using its knowledge of the stored data, such that the relative compute time of the query is minimized.
  * Caches/Buffers
    * This component has various caches to store frequently-accessed data, temporary tables created for use by other queries, etc.
  * SQL Interface
    * This component is the link between the Connector and the rest of the Server.
* Storage Engine
  * This component stores and manages the actual databases. Historically MySQL used the MyISAM engine, but switched to InnoDB with version 5.6. Both - and others - remain available if desired.

# MySQL Operations

## Assumptions

* All examples here are using MySQL 8.0.23, with the InnoDB engine.
* You're using the `mysql` client, available via Homebrew: `brew install mysql-client`
* You're connecting to the TODO database, using the credentials in 1Pass.

## Notes

* MySQL is case-insenitive for most, but not all operations. I'll use `UPPERCASE` to designate commands, and `lowercase` to desginate arguments and schema, table, and column names, but you're welcome to use all lowercase.
* The `;` suffix to commands serves as both the command terminator, and specifies that the output format should be in an ASCII table.
* The `\G` suffix to commands is an alternative terminator, and specifies that the output format should be in horizontal rows.
  * For Postgres, the equivalent is either by by entering `\x` in a session, at which point every query issued - terminated with `;` - will show this format; or by ending a given query with `\gx` to set the output for only that query.`
* I'm formatting my queries with statements and clauses on the left, their arguments indented by two spaces, and any qualifiers on the same line, where possible.
* This was developed on a Debian VM with 16 cores of a Xeon E5-2650 v2, 64 GiB of DDR3 RAM, and a working directory which is an NFS export over a 1GBe network, consisting of a ZFS RAIDZ2 array of spinning disks; ashift=12, blocksize=128K. Your times will vary, based mostly on the disk and RAM speed.

## Schemata

A brand-new installation of MySQL will typically have four schemata - `information_schema`, `mysql`, `performance_schema`, and `sys`.

* `information_schema` contains, as the name implies, information about the schema in the database. This includes columns, column types, indices, foreign keys, and tables.
* `mysql` generally contains configuration and logs
* `sys` generally contains information about the SQL engine (InnoDB here), including currently executing processes, and query metrics.
* `performance_schema` contains some specific performance information about the schema in the database, such as deadlocks, locks, memory consumption, mutexes, and threads.

## Schema spelunking

As mentioned, `databases` is often used to mean `schema`, and in fact in MySQL they're synonyms for this statement - `SHOW schemas` results in the exact same output. You won't have the `test` database yet, but you should see the other four shown below. NOTE: I'll demonstrate both output formats here, and will switch as needed to easily display the information.

mysql> SHOW schemas;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| northwind          |
| performance_schema |
| sys                |
| test               |
+--------------------+
6 rows in set (0.01 sec)

```sql
mysql> SHOW schemas\G
*************************** 1. row ***************************
Database: information_schema
*************************** 2. row ***************************
Database: mysql
*************************** 3. row ***************************
Database: northwind
*************************** 4. row ***************************
Database: performance_schema
*************************** 5. row ***************************
Database: sys
*************************** 6. row ***************************
Database: test
6 rows in set (0.01 sec)
```

The `SHOW` statement behind the scenes is gathering and formatting data in a way that's easy for humans to see and understand. Often, it comes from the `information_schema` or `performance_schema` schema, as seen below. This query also demonstrates the use of the `AS` statement, which allows you to alias a column or sub-query. NOTE: Due to how queries are ran, you can't use the alias for certain clauses, such as `WHERE` - but if it's an aggregated result (`GROUP BY`, either explicitly or implicitly), you can use `HAVING` with the alias.

```sql
mysql > 
SELECT 
  schema_name AS 'Database' 
FROM 
  information_schema.schemata;
+--------------------+
| Database           |
+--------------------+
| mysql              |
| information_schema |
| performance_schema |
| sys                |
| test               |
+--------------------+
5 rows in set (0.01 sec)
```

```sql
mysql > 
SELECT 
  schema_name AS `Database` 
FROM 
  information_schema.schemata 
WHERE 
  `Database` LIKE 'test';
ERROR 1054 (42S22): Unknown column 'Database' in 'where clause'
```

```sql
mysql > 
SELECT 
  schema_name AS `Database` 
FROM 
  information_schema.schemata 
WHERE 
  schema_name = 'test';

+----------+
| Database |
+----------+
| test     |
+----------+
1 row in set (0.00 sec)

```

```sql
mysql>
SELECT 
  schema_name AS `Database` 
FROM 
  information_schema.schemata 
HAVING 
  `Database` = 'test';

+----------+
| Database |
+----------+
| test     |
+----------+
1 row in set (0.01 sec)
```

### String literals and you

You may have noticed that in the above examples, sometimes a column or table name was enclosed with a single quote (`'`), sometimes a backtick (`\``), and other times nothing at all. This is deliberate.

In ANSI SQL, string literals are represented with single quotation marks, e.g. 'test.' This mode is disabled by default in MySQL, so you're free to use double quotation marks if you'd prefer; however if you were trying to pass in a command to the client from a shell (e.g. `mysql -e 'SELECT foo FROM bar'`), you might run into shell expansion issues depending on your query. Also, since you'll probably be working with other SQL implementations like Postgres, it's best to try to stay as neutral as possible.

Backticks may be used at any time, and are called quoted identifiers. They tell the SQL parser to consider anything enclosed in them as a string literal. This may be useful if, for example, you created a table named `table` (please don't), had a column named `count`, etc. The full list of keywords / reserved words [is here](https://dev.mysql.com/doc/refman/8.0/en/keywords.html) if you want to see what to avoid.

```sql
mysql> CREATE TABLE table (id INT);
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'table (id INT)' at line 1
```

vs.

```sql
mysql> CREATE TABLE `table` (id INT);
Query OK, 0 rows affected (0.15 sec)
```

#### Hands-on example

First, let's check the current `SQL_MODE`. System variables can be viewed with either `SHOW VARIABLES` or `SELECT @@<[GLOBAL, SESSION]>`.

```sql
mysql> SHOW VARIABLES LIKE 'sql_mode'\G
*************************** 1. row ***************************
Variable_name: sql_mode
        Value: ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
1 row in set (0.01 sec)
```

If neither `GLOBAL` or `SESSION` are specified when using the `@@` method, the session value is returned if it exists, otherwise the global value is returned.

```sql
mysql> SELECT @@sql_mode\G
*************************** 1. row ***************************
@@sql_mode: ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
1 row in set (0.00 sec)
```

We'll use the `mysql.user` table for this example. First, no quotes of any kind. As expected, we get the rows from those two columns.

```sql
mysql> SELECT host, user FROM mysql.user;
+-----------+------------------+
| host      | user             |
+-----------+------------------+
| %         | sgarland         |
| localhost | mysql.infoschema |
| localhost | mysql.session    |
| localhost | mysql.sys        |
| localhost | root             |
+-----------+------------------+
5 rows in set (0.00 sec)
```

Now, we'll mix single and double quotes.

```sql
mysql> SELECT 'host', "user" FROM mysql.user;
+------+------+
| host | user |
+------+------+
| host | user |
| host | user |
| host | user |
| host | user |
| host | user |
+------+------+
5 rows in set (0.00 sec)
```

In MySQL's default mode, these two are treated the same, and you get the respective string literals printed as rows for the selected columns.

If single (or double) quotes are combined with backticks, you get partial results.

```sql
mysql> SELECT 'host', `user` FROM mysql.user;
+------+------------------+
| host | user             |
+------+------------------+
| host | sgarland         |
| host | mysql.infoschema |
| host | mysql.session    |
| host | mysql.sys        |
| host | root             |
+------+------------------+
5 rows in set (0.00 sec)
```

Now, we'll modify the session's `sql_mode`. You don't have permission to set any global variables, but you can set most session variables. Unlike for the selection, if you don't specify `GLOBAL` or `SESSION`, the `SET` will always assume `SESSION`.

```sql
mysql> SET @@sql_mode = ANSI_QUOTES;
Query OK, 0 rows affected (0.00 sec)

mysql> SELECT @@sql_mode\G
*************************** 1. row ***************************
@@sql_mode: ANSI_QUOTES
1 row in set (0.00 sec)
```

Oh no, we've overridden all of the other settings! Luckily, the global variable hasn't been modified, so we can use it to build the correct setting. To do so, we'll use the `CONCAT_WS` function, which as the name implies, concatenates things with a separator. It takes the form `CONCAT_WS(sep, <expressions>)`. We'll also run a `SELECT` of the global variable, nesting it as a sub-query.

```sql
mysql> SET @@sql_mode = (SELECT CONCAT_WS(',', 'ANSI_QUOTES', (SELECT @@GLOBAL.sql_mode)));
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT @@sql_mode\G
*************************** 1. row ***************************
@@sql_mode: ANSI_QUOTES,ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
1 row in set (0.00 sec)
```

Whew. Now we can try out the quoting differences again.

```sql
mysql> SELECT 'host', "user" FROM mysql.user;
+------+------------------+
| host | user             |
+------+------------------+
| host | sgarland         |
| host | mysql.infoschema |
| host | mysql.session    |
| host | mysql.sys        |
| host | root             |
+------+------------------+
5 rows in set (0.01 sec)
```

This time, only single quotes are treated as string literals, with double quotes being treated as identifiers.

Now, set the `SESSION.sql_mode` back to its original value, using a sub-query like before.

```sql
mysql> SET @@sql_mode = (SELECT @@GLOBAL.sql_mode);
Query OK, 0 rows affected (0.00 sec)
```

## Table operations

### Create a schema

Let's create some tables! First, we need a schema There aren't a lot of options here to be covered, so we can just create one named `test`. Ideally, we would also enable encryption at rest. This can be globally set, or specified at schema creation - any tables in the schema inherit its setting. If you're curious, InnoDB uses AES, with ECB mode for tablespaces, and CBC mode for data. Also notably, [undo logs](https://dev.mysql.com/doc/refman/8.0/en/innodb-undo-logs.html) and [redo logs](https://dev.mysql.com/doc/refman/8.0/en/innodb-redo-log.html) have their encryption handled by separate variables. However, since this requires some additional work (all of the easy options are only available with MySQL Enterprise; MySQL Community requires you to generate and store the key yourself), we'll skip it.

```sql
mysql> CREATE SCHEMA test;
Query OK, 1 row affected (0.02 sec)
```

### Create tables

First, we'll select our new schema so we don't have to constantly specify it.

```sql
mysql> USE test;
Database changed
```

Now, we'll create the `users` table.

```sql
mysql>
CREATE TABLE users (
  id BIGINT PRIMARY KEY, 
  first_name CHAR(64), 
  last_name CHAR(64), 
  uid BIGINT
);
Query OK, 0 rows affected (0.17 sec)

mysql> SHOW COLUMNS FROM users;
+------------+----------+------+-----+---------+-------+
| Field      | Type     | Null | Key | Default | Extra |
+------------+----------+------+-----+---------+-------+
| id         | bigint   | NO   | PRI | NULL    |       |
| first_name | char(64) | YES  |     | NULL    |       |
| last_name  | char(64) | YES  |     | NULL    |       |
| uid        | bigint   | YES  |     | NULL    |       |
+------------+----------+------+-----+---------+-------+
4 rows in set (0.02 sec)
```

Hmm, something's not quite right as compared to the original example - we're missing `AUTO_INCREMENT`! Without it, you'd have to manually specify the `id` value (which is this table's `PRIMARY KEY`), which is annoying. Additionally, while `id` was automatically made to be `NOT NULL` since it's the PK, `uid` was not, so we need to change those. Finally, `uid` should actually be named `user_id`, and it should have a `UNIQUE` constraint. Note that when redefining a column, it's like a `POST`, not a `PUT` - if you only specify what you want to be changed, the pre-existing definitions will be deleted.

```sql
mysql> ALTER TABLE users MODIFY uid BIGINT NOT NULL UNIQUE;
Query OK, 0 rows affected (0.27 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> ALTER TABLE users MODIFY id BIGINT AUTO_INCREMENT;
Query OK, 0 rows affected (0.34 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> SHOW COLUMNS FROM users;
+------------+----------+------+-----+---------+----------------+
| Field      | Type     | Null | Key | Default | Extra          |
+------------+----------+------+-----+---------+----------------+
| id         | bigint   | NO   | PRI | NULL    | auto_increment |
| first_name | char(64) | YES  |     | NULL    |                |
| last_name  | char(64) | YES  |     | NULL    |                |
| uid        | bigint   | NO   | UNI | NULL    |                |
+------------+----------+------+-----+---------+----------------+
4 rows in set (0.02 sec)
```

If you wanted to rename a column without specifying its definition, you can use `RENAME COLUMN`.

```sql
mysql> ALTER TABLE users RENAME COLUMN uid TO user_id;
Query OK, 0 rows affected (0.12 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

#### Data types

What is the difference between a `VARCHAR` and a `CHAR`, and what is the integer after it? `CHAR` allocates precisely the amount of space required. If you specify that a column is 64 bytes wide, then you can store 64 bytes in it, and no matter if you're storing 1 byte or 64 bytes, the actual column usage will take 64 bytes - this is because the value is right-padded with spaces, and the trailing spaces are them removed when retrieved (by default - the trimming behavior can be modified, if desired).

Let's try adding a 65-byte string to a column with a strict 64-byte limit - this can be done with the `LPAD` function, which takes the form `LPAD(<string>, <padding>, <padding_character>).`

```sql
mysql>
INSERT INTO users (first_name, last_name, user_id) 
VALUES 
  (
    "Stephan", 
    (
      SELECT 
        LPAD("Garland", 65, " ")
    ), 
    1
  );
ERROR 1406 (22001): Data too long for column 'last_name' at row 1
```

Since people in different cultures may have longer names than I'm used to, making this column allowed to be wider than 64 bytes is probably a good idea, especially if there isn't a storage penalty for doing so. While a `VARCHAR` can technically be up to `2^16 - 1` bytes - the same as the row width limit - it's still a good idea to have some kind of reasonable limits in place, lest someone exploit a security hole and starting using your DB for Chia mining or something. 255 bytes was the historic maximum length allowed in older SQL implementations, and it's the maximum value that a `VARCHAR` can be stored with while having a 1-byte length prefix. Thus, we'll modify our columns to this standard.

```sql
mysql>
ALTER TABLE users
  MODIFY first_name VARCHAR(255), 
  MODIFY last_name VARCHAR(255);
Query OK, 0 rows affected (0.13 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> SHOW COLUMNS FROM users;
+------------+--------------+------+-----+---------+----------------+
| Field      | Type         | Null | Key | Default | Extra          |
+------------+--------------+------+-----+---------+----------------+
| id         | bigint       | NO   | PRI | NULL    | auto_increment |
| first_name | varchar(255) | YES  |     | NULL    |                |
| last_name  | varchar(255) | YES  |     | NULL    |                |
| user_id    | bigint       | NO   | UNI | NULL    |                |
+------------+--------------+------+-----+---------+----------------+
4 rows in set (0.01 sec)
```

What about ints? You may sometimes see an integer following an integer-type column definition, like `int(4)`. Confusingly, this has nothing to do with the maximum amount of data that can be stored in that column, and is only used for display. Even more confusingly, the MySQL client itself will ignore it, and show the entire stored number. Applications can choose whether or not to use the display width. In general, there's little reason to use this feature, and if you want to constrain display width, do so in your application.

For floating points, MySQL supports `FLOAT` and `DOUBLE`, with the former being 4 bytes, and the latter 8 bytes.

For exact precision numbers, MySQL supports `DECIMAL` and `NUMERIC`, and they are identical.

There are also sub-types of `INT`, such as `SMALLINT` (2 bytes, storing a maximum value of `2^16 - 1` if unsigned), and `BIGINT`, as seen previously - it's 8 bytes, and stores a maximum value of `2^63 - 1` if signed, and `2^64 - 1` if unsigned. Since there's not much reason to have negative IDs, let's alter those definitions as well:

```sql
msyql> ALTER TABLE users
  MODIFY id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, 
  MODIFY user_id BIGINT UNSIGNED NOT NULL UNIQUE;
Query OK, 0 rows affected, 1 warning (0.10 sec)
Records: 0  Duplicates: 0  Warnings: 1
```

A warning? Huh?

```sql
mysql> SHOW WARNINGS\G
*************************** 1. row ***************************
  Level: Warning
   Code: 1831
Message: Duplicate index 'user_id_2' defined on the table 'test.users'. This is deprecated and will be disallowed in a future release.
1 row in set (0.00 sec)
```

Ah - constraints like `UNIQUE` don't have to be redefined along with the rest of the column definition, and in doing so, we've duplicated a constraint. While allowed for now, it's not a good practice, so we'll get rid of it.

```sql
mysql> ALTER TABLE users DROP CONSTRAINT user_id_2;
Query OK, 0 rows affected (0.16 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> SHOW COLUMNS FROM users;
+------------+-----------------+------+-----+---------+----------------+
| Field      | Type            | Null | Key | Default | Extra          |
+------------+-----------------+------+-----+---------+----------------+
| id         | bigint unsigned | NO   | PRI | NULL    | auto_increment |
| first_name | varchar(255)    | YES  |     | NULL    |                |
| last_name  | varchar(255)    | YES  |     | NULL    |                |
| user_id    | bigint unsigned | NO   | UNI | NULL    |                |
+------------+-----------------+------+-----+---------+----------------+
4 rows in set (0.01 sec)
```

Now, we'll make the `zaps` table. You have noticed by now that the PK column `id` has been the first column in all of these definitions. While nothing stops you from placing it last, or in the middle, this is a bad idea for a variety of reasons, not least of which it's confusing for anyone used to normal ordering. There may be some small binpacking gains to be made by carefully matching column widths to page sizes (the default pagesize for InnoDB is 16 KB, and the default pagesize for most disks today is 4 KB), which can also impact performance on spinning disks. Also, prior to MySQL 8.0.13, temporary tables (usually, tables that InnoDB creates as part of a query) would silently cast `VARCHAR` and `VARBINARY` columns to their respective `CHAR` or `BINARY`. If you had some `VARCHAR` columns with a large maximum size, this could cause the required space to store them to rapidly balloon, filling up the disk.

In general, column ordering in a table doesn't tremendously matter for MySQL (but it does for queries, as we'll see later), so stick to convention.

```sql
mysql>
CREATE TABLE zaps (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, 
  zap_id BIGINT UNSIGNED NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL, 
  last_updated_at TIMESTAMP,
  owned_by BIGINT UNSIGNED NOT NULL, 
  used_by BIGINT UNSIGNED NOT NULL
);
Query OK, 0 rows affected (0.24 sec)

mysql> SHOW COLUMNS FROM zaps;
+-----------------+-----------------+------+-----+---------+----------------+
| Field           | Type            | Null | Key | Default | Extra          |
+-----------------+-----------------+------+-----+---------+----------------+
| id              | bigint unsigned | NO   | PRI | NULL    | auto_increment |
| zap_id          | bigint unsigned | NO   | UNI | NULL    |                |
| created_at      | timestamp       | NO   |     | NULL    |                |
| last_updated_at | timestamp       | YES  |     | NULL    |                |
| owned_by        | bigint unsigned | NO   |     | NULL    |                |
| used_by         | bigint unsigned | NO   |     | NULL    |                |
+-----------------+-----------------+------+-----+---------+----------------+
6 rows in set (0.02 sec)
```

### Foreign keys

These tables seem fine to start with, but the columns that we are implicitly designing to have relationships don't have any method of enforcement. While this is a valid design - placing all referential integrity requirements onto the application - SQL was designed to handle this for us, so let's make use of it. NOTE: foreign keys bring with them a huge array of problems that will likely not be seen until your scale is large, so keep that in mind, and have a plan to migrate off of them if necessary.

#### Why you might want FKs

Let's create a user, and give them a Zap.

```sql
mysql>
INSERT INTO users (
  first_name, last_name, user_id
) 
VALUES 
  ('Stephan', 'Garland', 1);
Query OK, 1 row affected (0.02 sec)

mysql>
INSERT INTO zaps (
  zap_id, created_at, last_updated_at, 
  owned_by, used_by
) 
VALUES 
  (1, NOW(), NOW(), 1, 1);
Query OK, 1 row affected (0.02 sec)
```

We can `JOIN` on this if we want.

```sql
mysql>
SELECT * FROM users
  JOIN zaps ON 
    users.user_id = zaps.owned_by\G
*************************** 1. row ***************************
             id: 1
     first_name: Stephan
      last_name: Garland
        user_id: 1
             id: 1
         zap_id: 1
     created_at: 2022-12-21 15:15:40
last_updated_at: 2022-12-21 15:15:40
       owned_by: 1
        used_by: 1
1 row in set (0.00 sec)
```

That's all well and good, but what if I want to delete my account? Wouldn't it be nice if devs didn't have to worry about deleting every trace of my existence? Or what if everyone's user ID has to change for a migration? Enter FKs.

#### Creating a FK

```sql
ALTER TABLE 
  zaps 
ADD 
  FOREIGN KEY (owned_by)
  REFERENCES users (user_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE;
Query OK, 1 row affected (0.50 sec)
Records: 1  Duplicates: 0  Warnings: 0

mysql> SHOW CREATE TABLE zaps\G
*************************** 1. row ***************************
       Table: zaps
Create Table: CREATE TABLE `zaps` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `zap_id` bigint unsigned NOT NULL,
  `created_at` timestamp NOT NULL,
  `last_updated_at` timestamp NULL DEFAULT NULL,
  `owned_by` bigint unsigned NOT NULL,
  `used_by` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `zap_id` (`zap_id`),
  KEY `owned_by` (`owned_by`),
  CONSTRAINT `zaps_ibfk_1` FOREIGN KEY (`owned_by`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
```

Note that not only do we now have a `FOREIGN KEY` linking `zaps.owned_by` to `users.user_id`, but InnoDB has added an index on `zaps.owned_by` - this is required, and despite the documentation informing you that you must do this before adding the FK, it actually does it for you if you don't.

#### Demonstrating the FK

```sql
mysql> UPDATE users SET user_id = 9 WHERE id = 1;
Query OK, 1 row affected (0.02 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql>
SELECT * FROM users
  JOIN zaps ON 
    users.user_id = zaps.owned_by\G
*************************** 1. row ***************************
             id: 1
     first_name: Stephan
      last_name: Garland
        user_id: 9
             id: 1
         zap_id: 1
     created_at: 2022-12-21 15:15:40
last_updated_at: 2022-12-21 15:15:40
       owned_by: 9
        used_by: 1
1 row in set (0.00 sec)
```

And just like that, `zaps` has updated its `owned_by` value for that Zap to equal the new value in `users`. And if we delete the `users` entry, the same `CASCADE` action will follow.

```sql

mysql> DELETE FROM users WHERE id = 1;
Query OK, 1 row affected (0.02 sec)

mysql> SELECT * FROM zaps;
Empty set (0.00 sec)
```

## Queries

### Fill the tables

We're going to need some more data to play around with, so it's time to shift gears. [Northwind Traders](https://en.wikiversity.org/wiki/Database_Examples/Northwind) is the Hello World of databases. It was created by Microsoft in the 1990s for Access, and is publicly licensed. I've loaded it into this instance, under the schema `northwind`.

```sql
mysql> USE northwind;
Database changed
```

In order to find out how many rows are in each table, there a few ways of doing so. InnoDB maintains information about tables in the `INFORMATION_SCHEMA.TABLES` table, including an estimate of row count. However, it's just that - an estimate. It can be made to be accurate if you use `ANALYZE TABLE`, but in production, you should not do this, since it places a table-wide read lock during the process. You can also use the query `SELECT COUNT(*)`, but that will perform a table scan (where the entire table is read sequentially, without indices), so it may have a performance impact on the database, as it's consuming a lot of available IOPS. Finally, assuming you have an auto-incrementing `id` field in the table, you can use `SELECT id FROM <table> ORDER BY id DESC LIMIT 1` to get the last incremented value. This is also an estimate, since it doesn't take any deletions into account (auto-increment is monotonic), but it's extremely fast.

Since this isn't production, we can force a refresh of our table statistics to get accurate counts. This will cause viewing the table's statistics to refresh the table statistics, and the variable is reset to its old value afterwards.

```sql
mysql> SET @old_innodb_stats_on_metadata = @@global.innodb_stats_on_metadata;
mysql> SET GLOBAL innodb_stats_on_metadata='ON';

mysql> SELECT table_name, table_rows FROM information_schema.tables WHERE table_schema = 'northwind';
+-----------------------------+------------+
| TABLE_NAME                  | TABLE_ROWS |
+-----------------------------+------------+
| customers                   |         29 |
| employee_privileges         |          1 |
| employees                   |          9 |
| inventory_transaction_types |          4 |
| inventory_transactions      |        102 |
| invoices                    |         35 |
| order_details               |         58 |
| order_details_status        |          6 |
| orders                      |         48 |
| orders_status               |          4 |
| orders_tax_status           |          2 |
| privileges                  |          1 |
| products                    |         45 |
| purchase_order_details      |         55 |
| purchase_order_status       |          4 |
| purchase_orders             |         28 |
| sales_reports               |          5 |
| shippers                    |          3 |
| strings                     |         62 |
| suppliers                   |         10 |
+-----------------------------+------------+
20 rows in set (0.22 sec)

mysql> SET GLOBAL innodb_stats_on_metadata = @old_innodb_stats_on_metadata;
```

### Relational alegbra

Not a lot of it, I promise; just what we need to discuss joins.

* Union : `R ∪ S --- R OR S`
* Intersection: `R ∩ S --- R AND S`
* Difference: `R ≏ S --- R - S`

If you're intersted in exploring relational alegbra, [this application](https://dbis-uibk.github.io/relax/calc/local/uibk/local/3) is quite useful to convert SQL to relational alegbra, and display the results.

### Joins

* Cartesian AKA Cross Join
  * Rarely used. This produces `n x m` rows for the two groups being joined.
  * That said, every other join can be thought of as a cross join with a predicate.

```sql
mysql> SELECT * FROM orders_status CROSS JOIN orders_tax_status;
+----+-------------+----+-----------------+
| id | status_name | id | tax_status_name |
+----+-------------+----+-----------------+
|  0 | New         |  1 | Taxable         |
|  0 | New         |  0 | Tax Exempt      |
|  1 | Invoiced    |  1 | Taxable         |
|  1 | Invoiced    |  0 | Tax Exempt      |
|  2 | Shipped     |  1 | Taxable         |
|  2 | Shipped     |  0 | Tax Exempt      |
|  3 | Closed      |  1 | Taxable         |
|  3 | Closed      |  0 | Tax Exempt      |
+----+-------------+----+-----------------+
8 rows in set (0.00 sec)
```

* Inner Join
  * The default (i.e. `JOIN` == `INNER JOIN`). This is `customers AND orders` with a predicate.
  * We're also using `DISTINCT` here to limit the returned values - it returns unique tuples of all queried columns.
    * In MySQL 5.x, it was often more performant to use a `GROUP BY` aggregation, but the optimizer now (usually) returns the same results for both. It's important to measure the relative performance of having the database peform your filtering vs. having your application do so. Be mindful of the performance impact to other tenants (other queries for the database, and other Kubernetes pods for the application) in both scenarios, as well as the user experience.

```sql
mysql>
SELECT DISTINCT
  company, 
  job_title, 
  ship_name 
FROM 
  customers 
  JOIN orders ON customers.id = orders.customer_id;

+------------+---------------------------+-------------------------+
| company    | job_title                 | ship_name               |
+------------+---------------------------+-------------------------+
| Company AA | Purchasing Manager        | Karen Toh               |
| Company D  | Purchasing Manager        | Christina Lee           |
| Company L  | Purchasing Manager        | John Edwards            |
| Company H  | Purchasing Representative | Elizabeth Andersen      |
| Company CC | Purchasing Manager        | Soo Jung Lee            |
| Company C  | Purchasing Representative | Thomas Axen             |
| Company F  | Purchasing Manager        | Francisco Pérez-Olaeta  |
| Company BB | Purchasing Manager        | Amritansh Raghav        |
| Company J  | Purchasing Manager        | Roland Wacker           |
| Company G  | Owner                     | Ming-Yang Xie           |
| Company K  | Purchasing Manager        | Peter Krschne           |
| Company A  | Owner                     | Anna Bedecs             |
| Company I  | Purchasing Manager        | Sven Mortensen          |
| Company Y  | Purchasing Manager        | John Rodman             |
| Company Z  | Accounting Assistant      | Run Liu                 |
+------------+---------------------------+-------------------------+
15 rows in set (0.02 sec)
```

* Left Outer Join
  * Left and Right Joins are both a type of Outer Join, and often just called Left or Right Join.
  * This is `customers OR orders` with a predicate and default value (`NULL`) for `orders`.

```sql
mysql>
SELECT DISTINCT
  company, 
  job_title, 
  ship_name 
FROM 
  customers 
  LEFT JOIN orders ON customers.id = orders.customer_id;

+------------+---------------------------+-------------------------+
| company    | job_title                 | ship_name               |
+------------+---------------------------+-------------------------+
| Company A  | Owner                     | Anna Bedecs             |
| Company B  | Owner                     | NULL                    |
| Company C  | Purchasing Representative | Thomas Axen             |
| Company D  | Purchasing Manager        | Christina Lee           |
| Company E  | Owner                     | NULL                    |
| Company F  | Purchasing Manager        | Francisco Pérez-Olaeta  |
| Company G  | Owner                     | Ming-Yang Xie           |
| Company H  | Purchasing Representative | Elizabeth Andersen      |
| Company I  | Purchasing Manager        | Sven Mortensen          |
| Company J  | Purchasing Manager        | Roland Wacker           |
| Company K  | Purchasing Manager        | Peter Krschne           |
| Company L  | Purchasing Manager        | John Edwards            |
| Company M  | Purchasing Representative | NULL                    |
| Company N  | Purchasing Representative | NULL                    |
| Company O  | Purchasing Manager        | NULL                    |
| Company P  | Purchasing Representative | NULL                    |
| Company Q  | Owner                     | NULL                    |
| Company R  | Purchasing Representative | NULL                    |
| Company S  | Accounting Assistant      | NULL                    |
| Company T  | Purchasing Manager        | NULL                    |
| Company U  | Accounting Manager        | NULL                    |
| Company V  | Purchasing Assistant      | NULL                    |
| Company W  | Purchasing Manager        | NULL                    |
| Company X  | Owner                     | NULL                    |
| Company Y  | Purchasing Manager        | John Rodman             |
| Company Z  | Accounting Assistant      | Run Liu                 |
| Company AA | Purchasing Manager        | Karen Toh               |
| Company BB | Purchasing Manager        | Amritansh Raghav        |
| Company CC | Purchasing Manager        | Soo Jung Lee            |
+------------+---------------------------+-------------------------+
29 rows in set (0.00 sec)
```

* Right Outer Join
  * Knowing how Left Join works, what do you think the results would be for a Right Join of the same data? What if the join order was reversed?

* Full Outer Join
  * This is `customers OR orders` with a predicate and default value (`NULL`) for both tables.
  * MySQL doesn't support `FULL JOIN` as a keyword, but it can be performed using `UNION` (or `UNION ALL` if duplicates are desired).
  * In order to give meaningful information, we'll join three tables here.
  
```sql
SELECT DISTINCT
  company, 
  job_title, 
  ship_name 
FROM 
  customers 
  LEFT JOIN orders ON customers.id = orders.customer_id 
UNION 
SELECT DISTINCT
  company, 
  job_title, 
  ship_name 
FROM 
  orders 
  RIGHT JOIN shippers ON orders.shipper_id = shippers.id;

+--------------------+---------------------------+-------------------------+
| company            | job_title                 | ship_name               |
+--------------------+---------------------------+-------------------------+
| Company A          | Owner                     | Anna Bedecs             |
| Company B          | Owner                     | NULL                    |
| Company C          | Purchasing Representative | Thomas Axen             |
| Company D          | Purchasing Manager        | Christina Lee           |
| Company E          | Owner                     | NULL                    |
| Company F          | Purchasing Manager        | Francisco Pérez-Olaeta  |
| Company G          | Owner                     | Ming-Yang Xie           |
| Company H          | Purchasing Representative | Elizabeth Andersen      |
| Company I          | Purchasing Manager        | Sven Mortensen          |
| Company J          | Purchasing Manager        | Roland Wacker           |
| Company K          | Purchasing Manager        | Peter Krschne           |
| Company L          | Purchasing Manager        | John Edwards            |
| Company M          | Purchasing Representative | NULL                    |
| Company N          | Purchasing Representative | NULL                    |
| Company O          | Purchasing Manager        | NULL                    |
| Company P          | Purchasing Representative | NULL                    |
| Company Q          | Owner                     | NULL                    |
| Company R          | Purchasing Representative | NULL                    |
| Company S          | Accounting Assistant      | NULL                    |
| Company T          | Purchasing Manager        | NULL                    |
| Company U          | Accounting Manager        | NULL                    |
| Company V          | Purchasing Assistant      | NULL                    |
| Company W          | Purchasing Manager        | NULL                    |
| Company X          | Owner                     | NULL                    |
| Company Y          | Purchasing Manager        | John Rodman             |
| Company Z          | Accounting Assistant      | Run Liu                 |
| Company AA         | Purchasing Manager        | Karen Toh               |
| Company BB         | Purchasing Manager        | Amritansh Raghav        |
| Company CC         | Purchasing Manager        | Soo Jung Lee            |
| Shipping Company A | NULL                      | Christina Lee           |
| Shipping Company A | NULL                      | Roland Wacker           |
| Shipping Company A | NULL                      | Sven Mortensen          |
| Shipping Company A | NULL                      | John Rodman             |
| Shipping Company B | NULL                      | Karen Toh               |
| Shipping Company B | NULL                      | John Edwards            |
| Shipping Company B | NULL                      | Soo Jung Lee            |
| Shipping Company B | NULL                      | Thomas Axen             |
| Shipping Company B | NULL                      | Francisco Pérez-Olaeta  |
| Shipping Company B | NULL                      | Roland Wacker           |
| Shipping Company B | NULL                      | Elizabeth Andersen      |
| Shipping Company C | NULL                      | Elizabeth Andersen      |
| Shipping Company C | NULL                      | Christina Lee           |
| Shipping Company C | NULL                      | Amritansh Raghav        |
| Shipping Company C | NULL                      | Peter Krschne           |
| Shipping Company C | NULL                      | Run Liu                 |
| Shipping Company C | NULL                      | Francisco Pérez-Olaeta  |
| Shipping Company C | NULL                      | Anna Bedecs             |
+--------------------+---------------------------+-------------------------+
47 rows in set (0.02 sec)
```

It's worth noting here that thus far, we've avoided using specifying the table for a given column, because the columns have been unique. If there were multiple tables with a given column (e.g. `id`), we'd have to specify it. This is done by prefixing the column name with the table name, e.g. `suppliers.job_title`. Note that you can also alias a table name by immediately following it with the desired alias, e.g. `FROM suppliers s`, and the alias can then be used to specify the table for a given column.

```sql
mysql>
SELECT 
  CONCAT_WS(', ', last_name, first_name) AS name, 
  job_title 
FROM 
  suppliers 
  JOIN employees ON job_title = job_title;
ERROR 1052 (23000): Column 'last_name' in field list is ambiguous

mysql>
SELECT DISTINCT
  CONCAT_WS(', ', s.last_name, s.first_name) AS name, 
  s.job_title 
FROM 
  suppliers s 
  JOIN employees e ON s.job_title = e.job_title;

+-----------------------------+----------------------+
| name                        | job_title            |
+-----------------------------+----------------------+
| Andersen, Elizabeth A.      | Sales Manager        |
| Weiler, Cornelia            | Sales Manager        |
| Kelley, Madeleine           | Sales Representative |
| Hernandez-Echevarria, Amaya | Sales Manager        |
| Dunton, Bryn Paul           | Sales Representative |
| Sandberg, Mikael            | Sales Manager        |
| Sousa, Luis                 | Sales Manager        |
+-----------------------------+----------------------+
7 rows in set (0.00 sec)
```

The above query isn't tremendously useful, of course, since it ambiguously names the first column `name` without specifying which table it's pulling from, and it removes duplicates (which in this case, would be the additional employes who share a job title). If a true join between these two was desired, and it was desired that the data was being presented in a way that makes visual sense to the reader, something like this would be preferable.

```sql
mysql>
SELECT 
  CONCAT_WS(', ', s.last_name, s.first_name) AS supplier_name, 
  s.job_title, 
  CONCAT_WS(', ', e.last_name, e.first_name) AS employee_name 
FROM 
  suppliers s 
  JOIN employees e ON s.job_title = e.job_title;

+-----------------------------+----------------------+----------------------+
| supplier_name               | job_title            | employee_name        |
+-----------------------------+----------------------+----------------------+
| Andersen, Elizabeth A.      | Sales Manager        | Thorpe, Steven       |
| Weiler, Cornelia            | Sales Manager        | Thorpe, Steven       |
| Kelley, Madeleine           | Sales Representative | Hellung-Larsen, Anne |
| Kelley, Madeleine           | Sales Representative | Zare, Robert         |
| Kelley, Madeleine           | Sales Representative | Neipper, Michael     |
| Kelley, Madeleine           | Sales Representative | Sergienko, Mariya    |
| Kelley, Madeleine           | Sales Representative | Kotas, Jan           |
| Kelley, Madeleine           | Sales Representative | Freehafer, Nancy     |
| Hernandez-Echevarria, Amaya | Sales Manager        | Thorpe, Steven       |
| Dunton, Bryn Paul           | Sales Representative | Hellung-Larsen, Anne |
| Dunton, Bryn Paul           | Sales Representative | Zare, Robert         |
| Dunton, Bryn Paul           | Sales Representative | Neipper, Michael     |
| Dunton, Bryn Paul           | Sales Representative | Sergienko, Mariya    |
| Dunton, Bryn Paul           | Sales Representative | Kotas, Jan           |
| Dunton, Bryn Paul           | Sales Representative | Freehafer, Nancy     |
| Sandberg, Mikael            | Sales Manager        | Thorpe, Steven       |
| Sousa, Luis                 | Sales Manager        | Thorpe, Steven       |
+-----------------------------+----------------------+----------------------+
17 rows in set (0.00 sec)
```

When data is being returned to an application, the ordering of columns or their names don't matter very much, but it's a good idea to at least be aware of how to present data in different ways.

### Indices

Indices, or indexes, _may_ speed up queries. Each table **should** have a primary key (it's not required, but, please don't do this), which is one index. Additional indices, on single or multiple columns, may be created. Most of them are stored in [B+ trees](https://en.wikipedia.org/wiki/B%2B_tree), which are similar to [B-trees](https://en.wikipedia.org/wiki/B-tree).

Indices aren't free, however - when you create an index on a column, that column's values are copied to the aforementioned B+ tree. While disk space is relatively cheap, creating dozens of indices for columns that are infrequently queried should be avoided. Also, since `INSERTs` must also write to the index, they'll be slowed down somewhat.

#### Single indices

We'll again look at the `test` schema, this time, the `ref_users` table. This table has 1 million rows, and was created by taking a [list of names](https://github.com/dominictarr/random-name/blob/master/names.txt) with 21985 rows, generating the schema with a program (as an aside, I got to play with C, which is always fun and frustrating), then loading it into the table. Since the table is two orders of magnitude larger than the input, there are obviously duplicated names, including some duplicated tuples of `first_name, last_name`. My table has nearly two orders of magnitude more duplicates than could be expected from a uniform distribution (962 duplicate tuples vs. the expected 45), which means my future as a statistician isn't great.

```sql
mysql> SELECT * FROM ref_users WHERE last_name = 'Safko';
+--------+------------+-----------+---------+
| id     | first_name | last_name | user_id |
+--------+------------+-----------+---------+
|  17862 | Coleen     | Safko     |   17862 |
|  23768 | Schiro     | Safko     |   23768 |
|  30136 | Aspasia    | Safko     |   30136 |
| ...... | .......... | ......... | ....... |
| 923109 | Toy        | Safko     |  923109 |
| 951230 | Brittne    | Safko     |  951230 |
| 952186 | Tran       | Safko     |  952186 |
+--------+------------+-----------+---------+
50 rows in set (6.73 sec)
```

`last_name` doesn't have an index. Let's create one on `first_name` and repeat the search (since the names were randomly distributed from the same list, a given first name has the same probability as being a last name). First, we create the index, which takes some time since the column's entries must be written out to a B+ tree. Next, we run `ANALYZE TABLE` to ensure that MySQL's optimizer is aware of the key distribution.

```sql
mysql> CREATE INDEX first_name ON ref_users (first_name);
Query OK, 0 rows affected (36.93 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> ANALYZE TABLE ref_users;
+----------------+---------+----------+----------+
| Table          | Op      | Msg_type | Msg_text |
+----------------+---------+----------+----------+
| test.ref_users | analyze | status   | OK       |
+----------------+---------+----------+----------+
1 row in set (0.11 sec)
```

```sql
mysql> SELECT * FROM ref_users WHERE first_name = 'Safko';
+--------+------------+-------------+---------+
| id     | first_name | last_name   | user_id |
+--------+------------+-------------+---------+
|  25136 | Safko      | Juanita     |   25136 |
| 101574 | Safko      | Lundquist   |  101574 |
| 125275 | Safko      | Harolda     |  125275 |
| ...... | .......... | ........... | ....... |
| 988638 | Safko      | Christoffer |  988638 |
| 991054 | Safko      | Pump        |  991054 |
| 999043 | Safko      | Phillip     |  999043 |
+--------+------------+-------------+---------+
40 rows in set (0.01 sec)
```

The lookup is now essentially instantaneous. If this is a frequently performed query, this may be a wise decision.

#### Composite indices

An index can also be created across multiple columns - for InnoDB, up to 16.

```sql
mysql> CREATE INDEX full_name ON ref_users (first_name, last_name);
Query OK, 0 rows affected (40.09 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

First, we'll use `IGNORE INDEX` to direct SQL to ignore the index we just created. This query counts the duplicate name tuples. Since the `id` is being included, and `GROUPing` it would result in an empty set (as it's the PK, and thus guaranteed to be unique), `ANY VALUE` must be specified to let MySQL know that the result can be non-deterministic. Finally, `EXPLAIN ANALYZE` is being used to run the query, and explain what it's doing. This differs from `EXPLAIN`, which guesses at what would be done, but doesn't actually perform the query. Be careful using `EXPLAIN ANALYZE`, especially with destructive actions, since those queries will actually be performed!

```sql
mysql>
EXPLAIN ANALYZE 
SELECT 
  ANY_VALUE(id), 
  first_name, 
  last_name, 
  COUNT(*) c 
FROM 
  ref_users IGNORE INDEX(full_name) 
GROUP BY 
  first_name, 
  last_name 
HAVING 
  c > 1\G

*************************** 1. row ***************************
EXPLAIN: -> Filter: (c > 1)  (actual time=17726.018..19132.446 rows=962 loops=1)
    -> Table scan on <temporary>  (actual time=0.005..927.857 rows=999037 loops=1)
        -> Aggregate using temporary table  (actual time=17725.897..18864.869 rows=999037 loops=1)
            -> Table scan on ref_users  (cost=100560.90 rows=997354) (actual time=0.405..7162.749 rows=1000000 loops=1)

1 row in set (19.58 sec)
```

The query took 19.58 seconds, and resulted in 962 rows. The output is read from the bottom up - a table scan was performed on the entire table, then a temporary table with the `GROUP BY` aggregation was created, and finally a second table scan on that temporary table was performed to find the duplicated tuples.

If you're curious, `actual time` is in milliseconds, and consists of two timings - the first is the time to initiate the step and return the first row; the second is the time to initiate the step and return all rows. `cost` is an arbitrary number indicating what the query cost optimizer thinks the query costs to perform, and is meaningless.

```sql
mysql>
EXPLAIN ANALYZE 
SELECT 
  ANY_VALUE(id), 
  first_name, 
  last_name, 
  COUNT(*) c 
FROM 
  ref_users 
GROUP BY 
  first_name, 
  last_name 
HAVING 
  c > 1\G

*************************** 1. row ***************************
EXPLAIN: -> Filter: (c > 1)  (actual time=8.627..9276.021 rows=962 loops=1)
    -> Group aggregate: count(0)  (actual time=0.756..8703.629 rows=999037 loops=1)
        -> Index scan on ref_users using full_name  (cost=100560.90 rows=997354) (actual time=0.683..5574.086 rows=1000000 loops=1)

1 row in set (9.28 sec)
```

With the index in place, an index scan is performed instead of two table scans, resulting in a ~2x speedup.

Another example, retreiving a specific doubled tuple that I know exists:

```sql
mysql>
SELECT 
  * 
FROM 
  ref_users USE INDEX() 
WHERE 
  first_name = 'Zoltai' 
  AND
  last_name = 'Tupler';

+--------+------------+-----------+---------+
| id     | first_name | last_name | user_id |
+--------+------------+-----------+---------+
| 173469 | Zoltai     | Tupler    |  173469 |
| 923085 | Zoltai     | Tupler    |  923085 |
+--------+------------+-----------+---------+
2 rows in set (6.72 sec)
```

Note that `USE INDEX()` is valid syntax to tell MySQL to ignore all indexes.

If instead, either the `full_name` or `first_name` index is ignored on its own, its complement will be used, and they're effectively equally fast due to the filtered result set (although as shown, the query ignoring the `full_name` index is an order of magnitude slower):

```sql
mysql>
EXPLAIN ANALYZE 
SELECT 
  * 
FROM 
  ref_users IGNORE INDEX(full_name) 
WHERE 
  first_name = 'Zoltai' 
  AND
  last_name = 'Tupler'\G

*************************** 1. row ***************************
EXPLAIN: -> Filter: (ref_users.last_name = 'Tupler')  (cost=11.18 rows=4) (actual time=3.944..4.044 rows=2 loops=1)
    -> Index lookup on ref_users using first_name (first_name='Zoltai')  (cost=11.18 rows=43) (actual time=3.922..4.003 rows=43 loops=1)

1 row in set (0.01 sec)

mysql>
EXPLAIN ANALYZE 
SELECT 
  * 
FROM 
  ref_users IGNORE INDEX(first_name) 
WHERE 
  first_name = 'Zoltai' 
  AND
  last_name = 'Tupler'\G

*************************** 1. row ***************************
EXPLAIN: -> Index lookup on ref_users using full_name (first_name='Zoltai', last_name='Tupler')  (cost=0.70 rows=2) (actual time=0.369..0.394 rows=2 loops=1)

1 row in set (0.00 sec)
```

### Predicates

For these, we'll shift back to the `northwind` schema.

#### WHERE

`WHERE` is the easiest to understand and apply, and will cover most of your needs.

```sql
mysql>
SELECT 
  id, 
  CONCAT_WS(', ', last_name, first_name) AS name, 
  city, 
  job_title 
FROM 
  customers 
WHERE 
  city = 'Seattle';

+----+----------------------+---------+-----------+
| id | name                 | city    | job_title |
+----+----------------------+---------+-----------+
|  1 | Bedecs, Anna         | Seattle | Owner     |
| 17 | Bagel, Jean Philippe | Seattle | Owner     |
+----+----------------------+---------+-----------+
2 rows in set (0.00 sec)
```

You may also have seen or used the wildcard `%` with `LIKE` and `NOT LIKE`.

```sql
mysql>
SELECT 
  id, 
  CONCAT_WS(', ', last_name, first_name) AS name, 
  city, 
  job_title 
FROM 
  customers 
WHERE 
  city LIKE 'Sea%';

+----+----------------------+---------+-----------+
| id | name                 | city    | job_title |
+----+----------------------+---------+-----------+
|  1 | Bedecs, Anna         | Seattle | Owner     |
| 17 | Bagel, Jean Philippe | Seattle | Owner     |
+----+----------------------+---------+-----------+
2 rows in set (0.00 sec)
```

These two are functionally equivalent queries. However, if there is an index on the predicate column, and you use a leading wildcard (e.g. `LIKE '%attle'`), MySQL cannot use the index, and will instead perform a table scan. If you can avoid using leading wildcards on large tables, do so. It's also worth noting that there are many times when the query optimizer determines that the table scan would be faster than using an index, and so will do so anyway. [Index usage can be hinted](https://dev.mysql.com/doc/refman/8.0/en/index-hints.html), forced, and ignored, although as of MySQL 8.0.20, the old syntax (which included hints) [is deprecated](https://dev.mysql.com/doc/refman/8.0/en/optimizer-hints.html#optimizer-hints-index-level). Examples of both are below with an `EXPLAIN SELECT`.

```sql
mysql>
EXPLAIN SELECT
  id, 
  city, 
  CONCAT_WS(', ', last_name, first_name) AS name, 
  job_title 
FROM 
  customers USE INDEX(city) 
WHERE 
  city LIKE 'Sea%'\G

*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: customers
   partitions: NULL
         type: range
possible_keys: city
          key: city
      key_len: 153
          ref: NULL
         rows: 2
     filtered: 100.00
        Extra: Using index condition
1 row in set, 1 warning (0.00 sec)

-- Note that with the leading wildcard, the index is disabled, even if FORCED
mysql>
EXPLAIN SELECT
  id, 
  city, 
  CONCAT_WS(', ', last_name, first_name) AS name, 
  job_title 
FROM 
  customers FORCE INDEX(city) 
WHERE 
  city LIKE '%Sea%'\G

*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: customers
   partitions: NULL
         type: ALL
possible_keys: NULL
          key: NULL
      key_len: NULL
          ref: NULL
         rows: 29
     filtered: 11.11
        Extra: Using where
1 row in set, 1 warning (0.00 sec)

-- Note that the new syntax requires the table and columnm to be specified
mysql>
EXPLAIN 
SELECT 
  id, 
  city, 
  CONCAT_WS(', ', last_name, first_name) AS name, 
  job_title 
FROM 
  customers 
    /*+ INDEX(customers city) */
WHERE 
  city LIKE 'Sea%' \G

*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: customers
   partitions: NULL
         type: range
possible_keys: city
          key: city
      key_len: 153
          ref: NULL
         rows: 2
     filtered: 100.00
        Extra: Using index condition
1 row in set, 1 warning (0.00 sec)
```

#### HAVING

Earlier, we used `HAVING` in a `GROUP BY` aggregation. The difference between the two is that `WHERE` filters the results before they're sent to be aggregated, whereas `HAVING` filters the aggregation, and thus predicates relying on the aggregation result can be used. It's not limited to only aggregation results, though - a common use case is to allow the use of aliases or subquery results in filtering.

```sql
mysql>
SELECT 
  c.first_name, 
  c.last_name, 
  c.city, 
  (
    SELECT 
      status_name 
    FROM 
      orders_status os 
    WHERE 
      os.id = o.status_id
  ) AS order_status 
FROM 
  customers c 
  JOIN orders o ON c.id = o.customer_id 
WHERE 
  c.job_title LIKE 'Purchasing%' 
  AND
  order_status = 'New';
ERROR 1054 (42S22): Unknown column 'order_status' in 'where clause'
```

The desired output here is to produce the name and city of any customer who has a job title starting with `Purchasing` and has placed a new order. Since the `order_status` column is the result of a subquery (returning the text name of a given order status ID), it can't be filterd with `WHERE`.

```sql
mysql>
SELECT 
  c.first_name, 
  c.last_name, 
  c.city, 
  (
    SELECT 
      status_name 
    FROM 
      orders_status os 
    WHERE 
      os.id = o.status_id
  ) AS order_status 
FROM 
  customers c 
  JOIN orders o ON c.id = o.customer_id 
WHERE 
  c.job_title LIKE 'Purchasing%' 
HAVING 
  order_status = 'New';

+------------+---------------+-------------+--------------+
| first_name | last_name     | city        | order_status |
+------------+---------------+-------------+--------------+
| Thomas     | Axen          | Los Angelas | New          |
| Christina  | Lee           | New York    | New          |
| Christina  | Lee           | New York    | New          |
| Francisco  | Pérez-Olaeta  | Milwaukee   | New          |
| Elizabeth  | Andersen      | Portland    | New          |
| Roland     | Wacker        | Chicago     | New          |
| Peter      | Krschne       | Miami       | New          |
| Peter      | Krschne       | Miami       | New          |
| John       | Edwards       | Las Vegas   | New          |
| Karen      | Toh           | Las Vegas   | New          |
| Amritansh  | Raghav        | Memphis     | New          |
| Soo Jung   | Lee           | Denver      | New          |
+------------+---------------+-------------+--------------+
12 rows in set (0.02 sec)
```

This is somewhat of a contrived example, since it's not necessary to return the actual `order_status` text at. However, if desired, it can be simplified with another `JOIN` instead of `HAVING`:

```sql
mysql>
SELECT 
  c.first_name, 
  c.last_name, 
  c.city, 
  os.status_name AS order_status 
FROM 
  customers c 
  JOIN orders o ON c.id = o.customer_id 
  JOIN orders_status os ON os.id = o.status_id 
WHERE 
  c.job_title LIKE 'Purchasing%' 
  AND
  os.status_name = 'New';

+------------+---------------+-------------+--------------+
| first_name | last_name     | city        | order_status |
+------------+---------------+-------------+--------------+
| Thomas     | Axen          | Los Angelas | New          |
| Christina  | Lee           | New York    | New          |
| Christina  | Lee           | New York    | New          |
| Francisco  | Pérez-Olaeta  | Milwaukee   | New          |
| Elizabeth  | Andersen      | Portland    | New          |
| Roland     | Wacker        | Chicago     | New          |
| Peter      | Krschne       | Miami       | New          |
| Peter      | Krschne       | Miami       | New          |
| John       | Edwards       | Las Vegas   | New          |
| Karen      | Toh           | Las Vegas   | New          |
| Amritansh  | Raghav        | Memphis     | New          |
| Soo Jung   | Lee           | Denver      | New          |
+------------+---------------+-------------+--------------+
12 rows in set (0.02 sec)
```

Examining the two with `EXPLAIN ANALYZE` shows the differences:

```sql
--- HAVING query
*************************** 1. row ***************************
EXPLAIN: -> Filter: (order_status = 'New')  (actual time=0.701..4.597 rows=12 loops=1)
    -> Nested loop inner join  (cost=6.60 rows=10) (actual time=0.574..3.200 rows=42 loops=1)
        -> Filter: (c.job_title like 'Purchasing%')  (cost=3.15 rows=3) (actual time=0.349..0.505 rows=20 loops=1)
            -> Table scan on c  (cost=3.15 rows=29) (actual time=0.333..0.444 rows=29 loops=1)
        -> Index lookup on o using customer_id (customer_id=c.id)  (cost=0.85 rows=3) (actual time=0.107..0.132 rows=2 loops=20)
    -> Select #2 (subquery in condition; dependent)
        -> Single-row index lookup on os using PRIMARY (id=o.status_id)  (cost=0.35 rows=1) (actual time=0.022..0.022 rows=1 loops=54)
-> Select #2 (subquery in projection; dependent)
    -> Single-row index lookup on os using PRIMARY (id=o.status_id)  (cost=0.35 rows=1) (actual time=0.022..0.022 rows=1 loops=54)

1 row in set, 1 warning (0.00 sec)

-- This is less of a warning, and more of a note stating that the query optimizer decided to resolve order.status_id in the first SELECT, rather than the subquery where it's referenced.
mysql> SHOW WARNINGS\G
*************************** 1. row ***************************
  Level: Note
   Code: 1276
Message: Field or reference 'northwind.o.status_id' of SELECT #2 was resolved in SELECT #1
1 row in set (0.00 sec)
```

```sql
--- Multiple JOIN query
*************************** 1. row ***************************
EXPLAIN: -> Nested loop inner join  (cost=6.33 rows=0) (actual time=1.645..8.714 rows=12 loops=1)
    -> Inner hash join (no condition)  (cost=3.80 rows=0) (actual time=1.161..1.665 rows=20 loops=1)
        -> Filter: (c.job_title like 'Purchasing%')  (cost=3.15 rows=3) (actual time=0.669..1.062 rows=20 loops=1)
            -> Table scan on c  (cost=3.15 rows=29) (actual time=0.640..0.922 rows=29 loops=1)
        -> Hash
            -> Filter: (os.status_name = 'New')  (cost=0.65 rows=1) (actual time=0.262..0.338 rows=1 loops=1)
                -> Table scan on os  (cost=0.65 rows=4) (actual time=0.251..0.319 rows=4 loops=1)
    -> Filter: (o.status_id = os.id)  (cost=0.78 rows=1) (actual time=0.301..0.348 rows=1 loops=20)
        -> Index lookup on o using customer_id (customer_id=c.id)  (cost=0.78 rows=3) (actual time=0.283..0.338 rows=2 loops=20)

1 row in set (0.01 sec)
```

Although difficult to see here with the small tables, generally `JOINs` are to be preferred over sub-queries, as they're typically more performant.

