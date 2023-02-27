- [Prerequisites](#prerequisites)
- [Introduction](#introduction)
  - [What is SQL?](#what-is-sql)
  - [What is a relational database?](#what-is-a-relational-database)
  - [What is ACID?](#what-is-acid)
    - [What is MySQL?](#what-is-mysql)
      - [How is it pronounced?](#how-is-it-pronounced)
  - [Basic definitions](#basic-definitions)
    - [SQL sub-languages](#sql-sub-languages)
    - [Other definitions](#other-definitions)
- [MySQL Components](#mysql-components)
- [MySQL Operations](#mysql-operations)
  - [Assumptions](#assumptions)
  - [Notes](#notes)
  - [Schemata](#schemata)
  - [Schema spelunking](#schema-spelunking)
    - [String literals](#string-literals)
      - [SQL\_MODE](#sql_mode)
    - [Create a schema](#create-a-schema)
  - [Table operations](#table-operations)
    - [Create tables](#create-tables)
      - [Data types](#data-types)
    - [Foreign keys](#foreign-keys)
      - [Why you might want foreign keys](#why-you-might-want-foreign-keys)
      - [Creating a foreign key](#creating-a-foreign-key)
      - [Demonstrating a foreign key](#demonstrating-a-foreign-key)
  - [Column operations](#column-operations)
    - [Adding columns](#adding-columns)
    - [Modfying columns](#modfying-columns)
    - [Dropping columns](#dropping-columns)
    - [Copied table definitions](#copied-table-definitions)
      - [Copied table data and truncating](#copied-table-data-and-truncating)
    - [Transactions](#transactions)
    - [Generated columns](#generated-columns)
    - [Invisible columns](#invisible-columns)
  - [Queries](#queries)
    - [SELECT](#select)
    - [INSERT](#insert)
    - [TABLE](#table)
  - [Joins](#joins)
    - [Relational alegbra](#relational-alegbra)
    - [Types of joins](#types-of-joins)
      - [Cross](#cross)
      - [Inner Join](#inner-join)
      - [Left Outer Join](#left-outer-join)
      - [Right Outer Join](#right-outer-join)
      - [Full Outer Join](#full-outer-join)
    - [Specifying a column's table](#specifying-a-columns-table)
    - [Indices](#indices)
      - [Single indices](#single-indices)
      - [JSON / Longtext](#json--longtext)
      - [Composite indices](#composite-indices)
      - [Testing indices](#testing-indices)
      - [Descending indices](#descending-indices)
      - [When indicies aren't helpful](#when-indicies-arent-helpful)
    - [Predicates](#predicates)
      - [WHERE](#where)
      - [HAVING](#having)
  - [Query optimization](#query-optimization)
    - [SELECT \*](#select-)
    - [OFFSET / LIMIT](#offset--limit)
    - [DISTINCT](#distinct)
  - [Cleanup](#cleanup)

# Prerequisites

You'll need to have a MySQL client. In no particular order, options are [DBeaver](https://dbeaver.io/) (GUI), [MySQL Workbench](https://www.mysql.com/products/workbench/) (GUI), [mysql-client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html) (TUI), and others. Note that the server is currently using a self-signed TLS certificate, which some clients may complain about. MySQL Workbench and msyql-client are proven to work without issue. Also note that mysql-client is available via [Homebrew](https://formulae.brew.sh/formula/mysql-client), but it won't symlink by default, so you'll need to do something like `brew link --force mysql-client`.

# Introduction

## What is SQL?

Structured Query Language. It's a domain-specific language designed to manage data in a Relational Database Management System (RDBMS). It's been extended and updated many times, both in its official ANSI definition, and in implementations of it like MySQL and PostgreSQL.

## What is a relational database?

It's what most people probably think of when they think of a database. Broadly speaking, data is related to other data in some manner. For example, observe these two tables (tl;dr a logical grouping of data):

```sql
SHOW COLUMNS FROM users;
```

```sql
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
SHOW COLUMNS FROM zaps;
```

```sql
+-----------------+-----------------+------+-----+-------------------+-----------------------------+
| Field           | Type            | Null | Key | Default           | Extra                       |
+-----------------+-----------------+------+-----+-------------------+-----------------------------+
| id              | bigint unsigned | NO   | PRI | NULL              | auto_increment              |
| zap_id          | bigint unsigned | NO   | UNI | NULL              |                             |
| created_at      | timestamp       | NO   |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED           |
| last_updated_at | timestamp       | YES  |     | NULL              | on update CURRENT_TIMESTAMP |
| owned_by        | bigint unsigned | NO   | MUL | NULL              |                             |
| shared_with     | json            | YES  |     | json_array()      | DEFAULT_GENERATED           |
+-----------------+-----------------+------+-----+-------------------+-----------------------------+
6 rows in set (0.01 sec)
```

Table `users` has four columns - `id`, `first_name`, `last_name`, and `user_id`. Table `zaps` has six columns - `id`, `zap_id`, `created_at`, `last_updated_at`, `owned_by`, and `shared_with`.

Although it isn't explicitly defined or enforced, there is an implicit relationship between these two tables via `users.user_id` and `zaps.owned_by`. Thus, a query like `SELECT zap_id, owned_by FROM zaps JOIN users ON user_id = owned_by;` could use that relationship. Ideally, there would be additional constraints like foreign keys established to ensure referential integrity, but this example suffices for now.

Also, generally speaking, RDBMS are ACID-compliant (but not always).

## What is ACID?

ACID is a set of four properties that, if implemented correctly, guarantee data validity:

- Atomicity
  - In a given transaction, each statement must either completely succeed, or fail. If any statement in a transaction fails, the entire transaction must fail.
- Consistency
  - A given transaction can only move a database from one valid and consistent state to another.
- Isolation
  - Even with concurrent transactions executing, the database must end up in the same state as if each transaction were executed sequentially.
- Durability
  - Once a transaction is committed, it must remain committed in the event of a system failure.

Note that the lack of one or more of these properties does not necessarily mean that data committed is invalid, only that the guarantees granted by that particular property must be accounted for elsewhere. A common counter-example of this is Eventual Consistency with distributed systems.

### What is MySQL?

It's an extremely popular row-based relational database implementing and extending ANSI SQL. It's unfortunately owned by Oracle, but if you'd prefer, the MariaDB fork is essentially the same thing.

#### How is it pronounced?

Officially, "My Ess Que Ell," but since the SQL language was originally called SEQUEL ("Structured English Query Language"), and only changed due to trademark issues, I feel at ease saying "My Sequel." However, this tends to bring out pedants who love to haughtily correct your pronunciation, so do what you will. For what it's worth, I also pronounce kubectl (the Kubernetes CLI tool) as "kube cuddle," so I may not be the greatest influence.

## Basic definitions

### SQL sub-languages

All of these can be grouped as SQL, and some of them can also be combined - `DQL` is often merged with `DML`, for example. Knowing that `DML` is generally operating on a single record at a time (but may be batched), and that `DDL` is generally operating on an entire table or schema at a time suffices for now.

- DCL
  - Data Control Language. `GRANT`, `REVOKE`.
- DDL
  - Data Definition Language. `ALTER`, `CREATE`, `DROP`, `TRUNCATE`.
- DML
  - Data Manipulation Language. `CALL`, `DELETE`, `INSERT`, `LOCK`, `SELECT (with FROM or WHERE)`, `UPDATE`.
- DQL
  - Data Query Language. `SELECT`.
- TCL
  - Transaction Control Language. `COMMIT`, `ROLLBACK`, `SAVEPOINT`.

### Other definitions

- B+ tree
  - An _m_`-ary tree` data structure that is self-balancing, with a variable number of children per node. It differs from the `B-tree` in that an individual data node can have either keys or children, but not both. It has `O(log(n))` time complexity for insertion, search, and deletion. It is frequently used both for filesystems and for RDBMS.
- Block
  - The lowest reasonable level of data storage (above individual bits). Historically sized at 512 bytes due to hard drive sector sizes, but generally sized at 4 KiB in modern drives, and SSDs. Enterprise drives sometimes have 520 byte block sizes (or 4160 bytes for the 4 KiB-adjacent size), with the extra 8 bytes being used for data integrity calculations.
- Filesystem
  - A method for the operating system to store data. May include features like copy-on-write, encryption, journaling, pre-allocation, SSD management, volume management, and more. Modern examples include APFS (default for Apple products), ext4 (default for most Linux distributions), NTFS (default for Windows), XFS (default for Red Hat and its downstream), and ZFS (default for FreeBSD).
- Schema
  - A logical grouping of database objects, e.g. tables, indices, etc. Often called a database, but technically, the database may contain any number of schemas, each with its own unique (or shared!) set of data, access policies, etc.
- Table
  - A logical grouping of data, of varying or similar types. May contain constraints, indices, etc.
- Tablespace
  - The link between the logical storage layer (tables, indices) and the physical storage layer (the disk's filesystem). This is an actual file that exists on the disk, contained in `$MYSQL_DATA_DIR`, nominally `/var/lib/mysql`.
    - As an aside, this fact, combined with [RDS MySQL file size limits](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MySQL.KnownIssuesAndLimitations.html#MySQL.Concepts.Limits.FileSize) yields some interesting information about RDS. Since they used to (anything created before April 2014) limit a table to 2 TiB*, that means that they were using ext3, as that is its maximum file size. Instances created after April 2014 are limited to 16 TiB* files, indicating that they are probably now using ext4, as that is generally its maximum file size. 16 TB is also the limit for InnoDB with 4 KB InnoDB page sizes, so it's possible the underlying disk's filesystem is XFS or something else, but since that value defaults to 16 KB, it seems unlikely.

\* AWS' docs state that the limits are in TB (terabytes) instead of TiB (tebibytes). It's possible that their VM subsystem limits the size to n TB, but the actual filesystem is capable of n TiB.

# MySQL Components

As of MySQL 8.0, this is the official architecture drawing:

![MySQL 8.0 architecture](https://cdn.zappy.app/a92561fb248524eb0927cc0ed618de52.png)

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
  * This component stores and manages the actual databases. Historically MySQL used the MyISAM engine, but switched to InnoDB with version 5.6. Both (and others) remain available if desired, but unless you have an extremely specific use case, you should use InnoDB.

# MySQL Operations

## Assumptions

* All examples here are using MySQL 8.0.23, with the InnoDB engine.
* All examples here are using the mysql-client TUI program, but others may work as well.

## Notes

* MySQL is case-insenitive for most, but not all operations. I'll use `UPPERCASE` to designate commands, and `lowercase` to desginate arguments and schema, table, and column names, but you're welcome to use all lowercase.
* The `;` suffix to commands serves as both the command terminator, and specifies that the output format should be in an ASCII table.
* The `\G` suffix to commands is an alternative terminator, and specifies that the output format should be in horizontal rows.
* I'm formatting my queries with statements and clauses on the left, their arguments indented by two spaces, and any qualifiers on the same line, where possible.
* This was developed on a Debian VM with 16 cores of a Xeon E5-2650 v2, 64 GiB of DDR3 RAM, and a working directory which is an NFS export over a 1GBe network, consisting of a ZFS RAIDZ2 array of spinning disks; ashift=12, blocksize=128K. Your times will vary, based mostly on the disk and RAM speed.

## Schemata

A brand-new installation of MySQL will typically have four schemata - `information_schema`, `mysql`, `performance_schema`, and `sys`.

* `information_schema` contains information about the schema in the database. This includes columns, column types, indices, foreign keys, and tables.
* `mysql` generally contains configuration and logs.
* `sys` generally contains information about the SQL engine (InnoDB here), including currently executing processes, and query metrics.
* `performance_schema` contains some specific performance information about the schema in the database, such as deadlocks, locks, memory consumption, mutexes, and threads.

## Schema spelunking

As mentioned, `databases` is often used to mean `schema`, and in fact in MySQL they're synonyms for this statement - `SHOW schemas` results in the exact same output. You won't have the `test` database yet, but you should see the other four shown below. NOTE: I'll demonstrate both output formats here, and will switch as needed to easily display the information.

```sql
SHOW schemas;
```

```sql
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
```

```sql
SHOW schemas\G
```

```sql
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

The `SHOW` statement behind the scenes is gathering and formatting data in a way that's easy for humans to see and understand. Often, it comes from the `information_schema` or `performance_schema` schema, as seen below. This query also demonstrates the use of the `AS` statement, which allows you to alias a column or sub-query.

```sql
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
| northwind          |
+--------------------+
6 rows in set (0.01 sec)
```

### String literals

You may have noticed that in the above examples, sometimes a column or table name was enclosed with a single quote (`'`), sometimes a backtick ( \` ), and other times nothing at all. This is deliberate.

In ANSI SQL, string literals are represented with single quotation marks, e.g. 'test.' This mode is disabled by default in MySQL, so you're free to use double quotation marks if you'd prefer; however if you were trying to pass in a command to the client from a shell (e.g. `mysql -e 'SELECT foo FROM bar'`), you might run into shell expansion issues depending on your query. Also, since you'll probably be working with other SQL implementations like Postgres, it's best to try to stay as neutral as possible.

Backticks may be used at any time, and are called quoted identifiers. They tell the SQL parser to consider anything enclosed in them as a string literal. This may be useful if, for example, you created a table named `table` (please don't), had a column named `count`, etc. The full list of keywords / reserved words [is here](https://dev.mysql.com/doc/refman/8.0/en/keywords.html) if you want to see what to avoid.

```sql
CREATE TABLE table (id INT);
```

```sql
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'table (id INT)' at line 1
```

vs.

```sql
CREATE TABLE `table` (id INT);
```

```sql
Query OK, 0 rows affected (0.15 sec)
```

#### SQL_MODE

As it turns out, you can alter this behavior. First, let's check the current `SQL_MODE`. System variables can be viewed with either `SHOW VARIABLES` or `SELECT @@<[GLOBAL, SESSION]>`.

```sql
SHOW VARIABLES LIKE 'sql_mode'\G
```

```sql
*************************** 1. row ***************************
Variable_name: sql_mode
        Value: ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
1 row in set (0.01 sec)
```

If neither `GLOBAL` or `SESSION` are specified when using the `@@` method, the session value is returned if it exists, otherwise the global value is returned.

```sql
SELECT @@sql_mode\G
```

```sql
*************************** 1. row ***************************
@@sql_mode: ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
1 row in set (0.00 sec)
```

We'll use the `mysql.user` table for this example. First, no quotes of any kind. As expected, we get the rows from those two columns.

```sql
SELECT host, user FROM mysql.user;
```

```sql
mysql> SELECT host, user FROM mysql.user;
+-------------+------------------+
| host        | user             |
+-------------+------------------+
| %           | zapier           |
| %           | zapier_training  |
| 192.168.1.% | sgarland         |
| localhost   | mysql.infoschema |
| localhost   | mysql.session    |
| localhost   | mysql.sys        |
| localhost   | root             |
+-------------+------------------+
7 rows in set (0.01 sec)
```

Now, we'll mix single and double quotes.

```sql
SELECT 'host', "user" FROM mysql.user;
```

```sql
+------+------+
| host | user |
+------+------+
| host | user |
| host | user |
| host | user |
| host | user |
| host | user |
| host | user |
| host | user |
+------+------+
7 rows in set (0.00 sec)
```

In MySQL's default mode, these two are treated the same, and you get the respective string literals printed as rows for the selected columns.

If single (or double) quotes are combined with backticks, you get partial results.

```sql
SELECT 'host', `user` FROM mysql.user;
```

```sql
+------+------------------+
| host | user             |
+------+------------------+
| host | zapier           |
| host | zapier_training  |
| host | sgarland         |
| host | mysql.infoschema |
| host | mysql.session    |
| host | mysql.sys        |
| host | root             |
+------+------------------+
7 rows in set (0.00 sec)
```

Now, we'll modify the session's `sql_mode`. You don't have permission to set any global variables, but you can set most session variables. Unlike for the selection, if you don't specify `GLOBAL` or `SESSION`, the `SET` will always assume `SESSION`.

```sql
SET @@sql_mode = ANSI_QUOTES;
```

```sql
Query OK, 0 rows affected (0.00 sec)

mysql> SELECT @@sql_mode\G
*************************** 1. row ***************************
@@sql_mode: ANSI_QUOTES
1 row in set (0.00 sec)
```

Oh no, we've overridden all of the other settings! Luckily, the global variable hasn't been modified, so we can use it to build the correct setting. To do so, we'll use the `CONCAT_WS` function, which as the name implies, concatenates things with a separator. It takes the form `CONCAT_WS(sep, <expressions>)`. We'll also run a `SELECT` of the global variable, nesting it as a sub-query.

```sql
SET @@sql_mode = (SELECT CONCAT_WS(',', 'ANSI_QUOTES', (SELECT @@GLOBAL.sql_mode)));
```

```sql
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT @@sql_mode\G
*************************** 1. row ***************************
@@sql_mode: ANSI_QUOTES,ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION
1 row in set (0.00 sec)
```

Whew. Now we can try out the quoting differences again.

```sql
SELECT 'host', "user" FROM mysql.user;
```

```sql
+------+------------------+
| host | USER             |
+------+------------------+
| host | zapier           |
| host | zapier_training  |
| host | sgarland         |
| host | mysql.infoschema |
| host | mysql.session    |
| host | mysql.sys        |
| host | root             |
+------+------------------+
7 rows in set (0.00 sec)
```

This time, only single quotes are treated as string literals, with double quotes being treated as identifiers.

Now, set the `SESSION.sql_mode` back to its original value, using a sub-query like before.

```sql
SET @@sql_mode = (SELECT @@GLOBAL.sql_mode);
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

### Create a schema

Let's create some tables! First, we need a schema. There aren't a lot of options here to be covered, so we can just create one. I'll be using `foo`, but you should substitute any name you'd like that's not already in use. Ideally, we would also enable encryption at rest. This can be globally set, or specified at schema creation - any tables in the schema inherit its setting. If you're curious, InnoDB uses AES, with ECB mode for tablespaces, and CBC mode for data. Also notably, [undo logs](https://dev.mysql.com/doc/refman/8.0/en/innodb-undo-logs.html) and [redo logs](https://dev.mysql.com/doc/refman/8.0/en/innodb-redo-log.html) have their encryption handled by separate variables. However, since this requires some additional work (all of the easy options are only available with MySQL Enterprise; MySQL Community requires you to generate and store the key yourself), we'll skip it.

```sql
CREATE SCHEMA foo;
```

```sql
Query OK, 1 row affected (0.02 sec)
```

## Table operations

### Create tables

First, we'll select our new schema so we don't have to constantly specify it. I'll be using `test` here, but you should substitute whatever you created in the last step.

```sql
USE foo;
```

```sql
Database changed
```

Now, we'll create the `users` table.

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  first_name CHAR(64),
  last_name CHAR(64),
  uid BIGINT
);
Query OK, 0 rows affected (0.17 sec)
```

```sql
SHOW COLUMNS FROM users;
```

```sql
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

Hmm, something's not quite right as compared to the original example - we're missing `AUTO_INCREMENT`! Without it, you'd have to manually specify the `id` value (which is this table's `PRIMARY KEY`), which is annoying. Additionally, while `id` was automatically made to be `NOT NULL` since it's the primary key, `uid` was not, so we need to change those (if you don't specify `NOT NULL`, MySQL defaults to `NULL`). Finally, `uid` should actually be named `user_id`, and it should have a `UNIQUE` constraint.

NOTE: when redefining a column, it's like a `POST`, not a `PUT` - if you only specify what you want to be changed, the pre-existing definitions will be deleted.

```sql
ALTER TABLE users MODIFY uid BIGINT NOT NULL UNIQUE;
```

```sql
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
ALTER TABLE users RENAME COLUMN uid TO user_id;
```

```sql
Query OK, 0 rows affected (0.12 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

Now, we'll make the `zaps` table. You have noticed by now that the primary key column `id` has been the first column in all of these definitions. While nothing stops you from placing it last, or in the middle, this is a bad idea for a variety of reasons, not least of which it's confusing for anyone used to normal ordering. There may be some small binpacking gains to be made by carefully matching column widths to page sizes (the default pagesize for InnoDB is 16 KB, and the default pagesize for most disks today is 4 KB), which can also impact performance on spinning disks. Also, prior to MySQL 8.0.13, temporary tables (usually, tables that InnoDB creates as part of a query) would silently cast `VARCHAR` and `VARBINARY` columns to their respective `CHAR` or `BINARY`. If you had some `VARCHAR` columns with a large maximum size, this could cause the required space to store them to rapidly balloon, filling up the disk.

In general, column ordering in a table doesn't tremendously matter for MySQL (but it does for queries, as we'll see later), so stick to convention.

```sql
CREATE TABLE zaps (
  `id` BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  `zap_id` BIGINT UNSIGNED NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT NOW(),
  `last_updated_at` TIMESTAMP NULL ON UPDATE NOW(),
  `owned_by` BIGINT UNSIGNED NOT NULL,
  UNIQUE(zap_id)
);
```

```sql
SHOW COLUMNS FROM zaps;
```

```sql
+-----------------+-----------------+------+-----+-------------------+-----------------------------+
| Field           | Type            | Null | Key | Default           | Extra                       |
+-----------------+-----------------+------+-----+-------------------+-----------------------------+
| id              | bigint unsigned | NO   | PRI | NULL              | auto_increment              |
| zap_id          | bigint unsigned | NO   | UNI | NULL              |                             |
| created_at      | timestamp       | NO   |     | CURRENT_TIMESTAMP | DEFAULT_GENERATED           |
| last_updated_at | timestamp       | YES  |     | NULL              | on update CURRENT_TIMESTAMP |
| owned_by        | bigint unsigned | NO   |     | NULL              |                             |
+-----------------+-----------------+------+-----+-------------------+-----------------------------+
5 rows in set (0.00 sec)
```

We're introducing some new defaults here:
* DEFAULT NOW()
  * With this, much like an `AUTO INCREMENTING` column, the current timestamp will be added to the `created_at` column when a new row is created. NOTE: This doesn't make the column immutable, and nothing stops someone from altering this value manually later.
* ON UPDATE NOW()
  * For `last_updated_at`, while the default is `NULL`, whenever the row is updated, the current timestamp is added.

`NOW()` is an alias for `CURRENT_TIMESTAMP`, and no, I didn't forget the function call on the right. For historical reasons, `CURRENT_TIMESTAMP` may be called with or without parentheses, but `NOW()` requires them. Similarly, generally any default value being declared that isn't a literal (e.g. `0`, `NULL`, etc.) is required to be wrapped in parentheses - see `(JSON_ARRAY())`. Again, for historical reasons, `TIMESTAMP` and `DATETIME` columns don't require this. Also, `JSON` _requires_ its default value to be wrapped in parentheses, even if the default is a literal (as do `BLOB`, `GEOMETRY`, and `TEXT`). See [MySQL docs on defaults](https://dev.mysql.com/doc/refman/8.0/en/data-type-defaults.html) for more information on this behavior, and [MySQL docs on timestamp initialization](https://dev.mysql.com/doc/refman/8.0/en/timestamp-initialization.html) for more information on timestamp column defaults.

#### Data types

What is the difference between a `VARCHAR` and a `CHAR`, and what is the integer after it? `CHAR` allocates precisely the amount of space required. If you specify that a column is 64 bytes wide, then you can store 64 bytes in it, and no matter if you're storing 1 byte or 64 bytes, the actual column usage will take 64 bytes - this is because the value is right-padded with spaces, and the trailing spaces are them removed when retrieved (by default - the trimming behavior can be modified, if desired).

Let's try adding a 65-byte string to a column with a strict 64-byte limit - this can be done with the `LPAD` function, which takes the form `LPAD(<string>, <padding>, <padding_character>).`

```sql
INSERT INTO users (first_name, last_name, user_id)
```

```sql
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
ALTER TABLE users
  MODIFY first_name VARCHAR(255),
  MODIFY last_name VARCHAR(255);
Query OK, 0 rows affected (0.13 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
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
ALTER TABLE users
  MODIFY id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  MODIFY user_id BIGINT UNSIGNED NOT NULL UNIQUE;
```

```sql
Query OK, 0 rows affected, 1 warning (0.10 sec)
Records: 0  Duplicates: 0  Warnings: 1
```

A warning? Huh?

```sql
SHOW WARNINGS\G
```

```sql
*************************** 1. row ***************************
  Level: Warning
   Code: 1831
Message: Duplicate index 'user_id' defined on the table 'test.users'. This is deprecated and will be disallowed in a future release.
1 row in set (0.00 sec)
```

Ah - constraints like `UNIQUE` don't have to be redefined along with the rest of the column definition, and in doing so, we've duplicated a constraint. While allowed for now, it's not a good practice, so we'll get rid of it.

```sql
ALTER TABLE users DROP CONSTRAINT uid;
```

```sql
Query OK, 0 rows affected (0.16 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
SHOW COLUMNS FROM users;
```

```sql
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

### Foreign keys

These tables seem fine to start with, but the columns that we are implicitly designing to have relationships don't have any method of enforcement. While this is a valid design - placing all referential integrity requirements onto the application - SQL was designed to handle this for us, so let's make use of it. NOTE: foreign keys bring with them a huge array of problems that will likely not be seen until your scale is large, so keep that in mind, and have a plan to migrate off of them if necessary.

#### Why you might want foreign keys

Let's create a user, and give them a Zap.

```sql
INSERT INTO users (
  first_name, last_name, user_id
)
VALUES
  ('Stephan', 'Garland', 1);
```

```sql
Query OK, 1 row affected (0.02 sec)
```

```sql
INSERT INTO zaps (zap_id, owned_by) VALUES (1, 1);
```

```sql
Query OK, 1 row affected (0.03 sec)
```

```sql
TABLE zaps;
```

<details>
  <summary>What is `TABLE`?</summary>

  Syntactic sugar (a shortcut) for `SELECT * FROM <table>`.

```sql
+----+--------+---------------------+-----------------+----------+
| id | zap_id | created_at          | last_updated_at | owned_by |
+----+--------+---------------------+-----------------+----------+
|  1 |      1 | 2023-02-27 10:25:01 | NULL            |        1 |
+----+--------+---------------------+-----------------+----------+
1 row in set (0.00 sec)
```

</details>

We can `JOIN` on this if we want.

```sql
SELECT
  *
FROM
  users
JOIN zaps ON users.user_id = zaps.owned_by\G
*************************** 1. row ***************************
             id: 1
     first_name: Stephan
      last_name: Garland
        user_id: 1
          email: NULL
             id: 1
         zap_id: 1
     created_at: 2023-02-27 10:25:01
last_updated_at: NULL
       owned_by: 1
1 row in set (0.01 sec)
```

That's all well and good, but what if I want to delete my account? Wouldn't it be nice if devs didn't have to worry about deleting every trace of my existence? Or what if everyone's user ID has to change for a migration? Enter foreign keys.

#### Creating a foreign key

```sql
ALTER TABLE
  zaps
ADD
  FOREIGN KEY (owned_by)
  REFERENCES users (user_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE;
```

```sql
Query OK, 1 row affected (0.50 sec)
Records: 1  Duplicates: 0  Warnings: 0
```

```sql
SHOW CREATE TABLE zaps\G
```

<details>
  <summary>What is this?</summary>

  `SHOW CREATE TABLE` is a command that lets you view the query that would be used to create the table in its current state. It's safe to do, and is a good way to view columns, their types, indexes, foreign keys, etc. for a given table.
  </summary>
</details>

```sql
*************************** 1. row ***************************
       Table: zaps
Create Table: CREATE TABLE `zaps` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `zap_id` bigint unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `owned_by` bigint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `zap_id` (`zap_id`),
  KEY `owned_by` (`owned_by`),
  CONSTRAINT `zaps_ibfk_1` FOREIGN KEY (`owned_by`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
```

Note that not only do we now have a `FOREIGN KEY` linking `zaps.owned_by` to `users.user_id`, but InnoDB has added an index on `zaps.owned_by` - this is required, and despite the documentation informing you that you must do this before adding the foreign key, it actually does it for you if you don't.

#### Demonstrating a foreign key

```sql
UPDATE users SET user_id = 9 WHERE id = 1;
```

Note the `WHERE` predicate - we'll go more into that later, but the most important thing to take away here is that there are very few instances where you should issue DML like `UPDATE`without a `WHERE`.

<details>
  <summary> Why not?</summary>

  If there was no predicate, the query would apply to everything in the table, e.g. every user would be modified.

</details>

```sql
Query OK, 1 row affected (0.02 sec)
Rows matched: 1  Changed: 1  Warnings: 0
```

```sql
SELECT * FROM users
  JOIN zaps ON
users.user_id = zaps.owned_by\G
```

```sql
*************************** 1. row ***************************
             id: 1
     first_name: Stephan
      last_name: Garland
        user_id: 9
          email: NULL
             id: 1
         zap_id: 1
     created_at: 2023-02-27 10:25:01
last_updated_at: NULL
       owned_by: 9
1 row in set (0.01 sec)
```

And just like that, `zaps` has updated its `owned_by` value for that Zap to equal the new value in `users`. And if we delete the `users` entry, the same `CASCADE` action will follow.

```sql
DELETE FROM users WHERE id = 1;
```

```sql
Query OK, 1 row affected (0.02 sec)
```

```sql
SELECT * FROM zaps;
```

```sql
Empty set (0.00 sec)
```

## Column operations

### Adding columns

Adding columns is done with `ALTER TABLE`:

```sql
ALTER TABLE
  zaps
ADD COLUMN
  shared_with
JSON;
```

```sql
Query OK, 0 rows affected (0.18 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

Just as with a table definition, the column's name (`shared_with`) and type (`JSON`) are required; additonal qualifiers like `DEFAULT`, `UNIQUE`, etc. may be appended. To add some types of default values, like a JSON array, you must call the function.

  * [MySQL supports JSON](https://dev.mysql.com/doc/refman/8.0/en/json.html) as a data type! While you can of course simply store JSON strings in a text column, there are some benefits to using the native JSON datatype; among them that you can index scalars from the JSON objects, and that you can extract specific keys/values from the objects instead of the entire string.
  * Please don't use this as an excuse to treat MySQL as a Document DB, though. If you want NoSQL, you should use NoSQL. RDBMS are optimized for relations. Storing some information in JSON is fine, but it shouldn't be the default.

### Modfying columns

This was covered earlier during [table operations](#table-operations), but as a refresher, we'll again use `ALTER TABLE` to add a `DEFAULT` value of an empty JSON array, which must be called as its function:

```sql
ALTER TABLE
  zaps
MODIFY COLUMN
shared_with
  JSON
  DEFAULT (
    JSON_ARRAY()
  );
```

```sql
Query OK, 0 rows affected (0.09 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

### Dropping columns

If there are foreign keys relying on the column you're trying to drop, you will first need to either disable foreign key checks, or remove those checks before you can drop the column.

```sql
DROP TABLE users;
```

```sql
ERROR 3730 (HY000): Cannot drop table 'users' referenced by a foreign key constraint 'zaps_ibfk_1' on table 'zaps'.
```

```sql
SET foreign_key_checks = 0;
```

```sql
Query OK, 0 rows affected (0.01 sec)
```

```sql
DROP TABLE users;
Query OK, 0 rows affected (0.30 sec)
```

```sql
SHOW CREATE TABLE zaps\G
```

```sql
*************************** 1. row ***************************
       Table: zaps
Create Table: CREATE TABLE `zaps` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `zap_id` bigint unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_updated_at` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `owned_by` bigint unsigned NOT NULL,
  `shared_with` json DEFAULT (json_array()),
  PRIMARY KEY (`id`),
  UNIQUE KEY `zap_id` (`zap_id`),
  KEY `owned_by` (`owned_by`),
  CONSTRAINT `zaps_ibfk_1` FOREIGN KEY (`owned_by`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
1 row in set (0.00 sec)
```

Just because MySQL let us drop the table, it doesn't mean it cleaned up after us.
<details>
  <summary>How can we remove the FK?</summary>

  ```sql
  ALTER TABLE zaps DROP CONSTRAINT `zaps_ibfk_1`;
  ```

  ```sql
  Query OK, 0 rows affected (0.20 sec)
  Records: 0  Duplicates: 0  Warnings: 0
  ```
</details>

Also, don't forget to re-enable `foreign_key_checks` for your session.

```sql
SET foreign_key_checks = 1;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

But wait, how are we going to get back the `users` table? We could scroll back up and find the definition, but wouldn't it be nice if we could copy the definition from somewhere else?

### Copied table definitions

Luckily, this exists in the form of `CREATE TABLE LIKE`. [MySQL docs](https://dev.mysql.com/doc/refman/8.0/en/create-table-like.html). You do need `SELECT` privileges from the schema/table you're copying from, which is enabled for `test.ref_%` with this user. You'll also need to specify the schema the table exists in, since it's outside of the currently selected schema.

NOTE: This schema is somewhat different from what we created before; most of it is additional, but one big change is that there is no longer an explicit `id` column, instead, the `user_id` column takes its place.

```sql
CREATE TABLE users LIKE test.ref_users;
```

```sql
Query OK, 0 rows affected (0.34 sec)
```

There are some restrictions. The documentation lists all of them, but the biggest one is that any foreign keys aren't copied. We deleted ours so it doesn't really matter, but this could catch you by surprise if you expected them to come over with the schema definition. Also, depending on the version of MySQL you're using, a bug may exist where tables copied in this manner will logically reside (that is, within a given tablespace file) in the original table's tablespace. A way around this is with this alternative query:

```sql
CREATE TABLE users SELECT * FROM test.ref_users LIMIT 0;
```

Finally, note that both of these _only_ copy the schema definition, not the data. The table you're copying from actually has thousands of rows in it, but none of those will be in your table.

<details>
  <summary>What if you wanted to copy data as well?</summary>

  The above alternative query hopefully hinted at it!

  ```sql
  DROP TABLE users; CREATE TABLE users SELECT * FROM test.ref_users LIMIT 1000;
  ```

  ```sql
  Query OK, 0 rows affected (0.30 sec)

  Query OK, 1000 rows affected (1.14 sec)
  Records: 1000  Duplicates: 0  Warnings: 0
  ```
</details>

#### Copied table data and truncating

Now that we have `users` back, let's actually fill it with more than just 1000 rows. `test.ref_users_big` has 1,000,000 rows. That would take a while to fill for everyone (my poor spinning disks), but 10,000 is reasonable.

First, let's dump the existing values, but leave the table definition. While there are a few ways to do this, the fastest is `TRUNCATE` ([MySQL docs](https://dev.mysql.com/doc/refman/8.0/en/truncate-table.html)). This is a `DDL` operation vs. `DML`, as instead of iterating through the table and deleting each row, it stores the table definition, drops the table, then re-creates it. This does have several limitations, especially with foreign keys, but it works fine here.

```sql
TRUNCATE TABLE users;
```

```sql
Query OK, 0 rows affected (0.42 sec)
```

`0 rows affected` may be confusing, as we in fact just affected 1000 rows, but remember that this is the same as a `DROP TABLE`, which similarly doesn't report on the number of rows removed.

Now, we can copy into the table:

```sql
INSERT INTO users SELECT * FROM test.ref_users_big LIMIT 10000;
```

```sql
Query OK, 10000 rows affected (5.33 sec)
Records: 10000  Duplicates: 0  Warnings: 0
```

### Transactions

Remember the discussion about doing `DML` without a predicate? There's a fix for that.

```sql
START TRANSACTION;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

```sql
UPDATE users SET city = "Asheville";
```

```sql
Query OK, 9999 rows affected (6.96 sec)
Rows matched: 10000  Changed: 9999  Warnings: 0
```

Uh-oh. Looks like everyone has moved to Western North Carolina.

```sql
ROLLBACK;
```

```sql
Query OK, 0 rows affected (5.45 sec)
```

Whew, not fired.

NOTE: Canceling a query (`Ctrl-C`), _regardless of whether or not you're in a transaction_, has the same effect, assuming the InnoDB storage engine is being used. This is the `A` in `ACID` at work - either the entire query succeeds, or none of it does. However, the rollback may take some time depending on how many rows have been affected. Also, if you don't manage to cancel the query before it completes, you're out of luck.

### Generated columns

What if you wanted a column that automatically created data for you based on other columns?

```sql
ALTER TABLE
  users
ADD COLUMN
  full_name VARCHAR(510) GENERATED ALWAYS AS (
    CONCAT_WS(', ', last_name, first_name)
  );
```

```sql
Query OK, 0 rows affected (0.34 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
SELECT user_id, full_name, city, country
  FROM users
LIMIT 10;
```

```sql
+---------+-------------------+-------------+----------------+
| user_id | full_name         | city        | country        |
+---------+-------------------+-------------+----------------+
|       1 | MacPherson, Addie | Latina      | Italy          |
|       2 | Airla, Valaree    | Pribram     | Czech Republic |
|       3 | Nett, Sheppard    | Hamada      | Japan          |
|       4 | Kirschner, Robby  | Bikaner     | India          |
|       5 | Bilski, Lewiss    | Vörderås    | Sweden         |
|       6 | Yamauchi, Marleah | Rotterdam   | Netherlands    |
|       7 | Calore, Ania      | Miyakojima  | Japan          |
|       8 | Breger, Gratiana  | Valkeakoski | Finland        |
|       9 | Serafina, Janith  | Morant Bay  | Jamaica        |
|      10 | Beckman, Pavla    | Wackersdorf | Germany        |
+---------+-------------------+-------------+----------------+
10 rows in set (0.01 sec)
```

Note that by default, this will create a `VIRTUAL` column (you can specify `STORED` after `AS` if you'd rather have a normal column), which is not actually stored, but instead calculated at query time. While this takes no storage space, it does add some amount of computational load, and more importantly comes with a [huge list](https://dev.mysql.com/doc/refman/8.0/en/create-table-generated-columns.html) of limitations. One large benefit, however, is that since the columns aren't actually created when the query is ran, the operation takes as long as a normal `ALTER TABLE` operation. If stored, the data must be written to the table, which will necessitate taking write locks. Also, since the column isn't actually being written anywhere, you can actually place the columns in any table position (by default, adding a column just appends to the end of the table) while still using the `INSTANT` algorithm, despite what the docs imply.

The creation and deletion time in particular is markedly better when compared to `STORED` columns:

```sql
ALTER TABLE
  users
ADD COLUMN
  full_name VARCHAR(510) GENERATED ALWAYS AS (
    CONCAT_WS(', ', last_name, first_name)
  ) STORED;
```

```sql
Query OK, 10000 rows affected (7.23 sec)
Records: 10000  Duplicates: 0  Warnings: 0
```

```sql
ALTER TABLE
  users
DROP COLUMN full_name;
```

```sql
Query OK, 0 rows affected (2.24 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

Demonstrating column positioning:

```sql
ALTER TABLE
  users
ADD COLUMN
  full_name VARCHAR(510) GENERATED ALWAYS AS (
    CONCAT_WS(', ', last_name, first_name)
  )
AFTER
  last_name;
```

```sql
Query OK, 0 rows affected (0.27 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
SELECT * FROM users LIMIT 1\G
```

```sql
*************************** 1. row ***************************
        user_id: 1
     first_name: Addie
      last_name: MacPherson
      full_name: MacPherson, Addie
          email: addie.macpherson@lizard.com
           city: Latina
        country: Italy
     created_at: 2001-05-27 19:47:17
last_updated_at: NULL
1 row in set (0.01 sec)
```

### Invisible columns

You can make columns `INVISIBLE` if you'd rather they not show up unless specifically queried for. This is done with the `INVISIBLE` keyword after the type (`VARCHAR(510)` here) if being created, or modified later with `ALTER COLUMN`:

```sql
ALTER TABLE users ALTER COLUMN full_name SET INVISIBLE;
```

```sql
Query OK, 0 rows affected (0.19 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
SELECT * FROM users LIMIT 1\G
```

```sql
*************************** 1. row ***************************
        user_id: 1
     first_name: Addie
      last_name: MacPherson
          email: addie.macpherson@lizard.com
           city: Latina
        country: Italy
     created_at: 2001-05-27 19:47:17
last_updated_at: NULL
1 row in set (0.00 sec)
Query OK, 0 rows affected (0.19 sec)
Records: 0  Duplicates: 0  Warnings: 0
1 row in set (0.00 sec)
```

To set them back to visible, use `SET VISIBLE`:

```sql
ALTER TABLE users ALTER COLUMN full_name SET VISIBLE;
```

```sql
Query OK, 0 rows affected (0.08 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

## Queries

In order to find out how many rows are in each table, there are a few ways of doing so. InnoDB maintains information about tables in the `INFORMATION_SCHEMA.TABLES` table, including an estimate of row count. However, it's just that - an estimate. It can be made to be accurate if you use `ANALYZE TABLE`, but in production, you shouldn't do this (to be clear, it should be done, but carefully), since it places a table-wide read lock during the process. You can also use the query `SELECT COUNT(*)`, but that will perform a table scan (where the entire table is read sequentially, without indices), so it may have a performance impact on the database, as it's consuming a lot of available IOPS. Finally, assuming you have an auto-incrementing `id` field in the table, you can use `SELECT id FROM <table> ORDER BY id DESC LIMIT 1` to get the last incremented value. This is also an estimate, since it doesn't take any deletions into account (auto-increment is monotonic), but it's extremely fast.

```sql
SELECT table_name, table_rows
FROM
  information_schema.tables
WHERE table_schema = 'test';
```

```sql
+---------------+------------+
| TABLE_NAME    | TABLE_ROWS |
+---------------+------------+
| gensql        |       1000 |
| ref_users     |       1000 |
| ref_users_big |     992839 |
| ref_zaps      |          0 |
| ref_zaps_big  |          0 |
| users         |       1000 |
| zaps          |          0 |
+---------------+------------+
7 rows in set (0.01 sec)
```

```sql
ANALYZE TABLE ref_zaps; ANALYZE TABLE ref_zaps_big;
```

```sql
+---------------+---------+----------+----------+
| Table         | Op      | Msg_type | Msg_text |
+---------------+---------+----------+----------+
| test.ref_zaps | analyze | status   | OK       |
+---------------+---------+----------+----------+
1 row in set (0.03 sec)

+-------------------+---------+----------+----------+
| Table             | Op      | Msg_type | Msg_text |
+-------------------+---------+----------+----------+
| test.ref_zaps_big | analyze | status   | OK       |
+-------------------+---------+----------+----------+
1 row in set (0.05 sec)
```

```sql
SELECT table_name, table_rows
FROM
  information_schema.tables
WHERE table_schema = 'test';
```

```sql
+---------------+------------+
| TABLE_NAME    | TABLE_ROWS |
+---------------+------------+
| gensql        |       1000 |
| ref_users     |       1000 |
| ref_users_big |     992839 |
| ref_zaps      |       1000 |
| ref_zaps_big  |     997211 |
| users         |       1000 |
| zaps          |          0 |
+---------------+------------+
7 rows in set (0.02 sec)
```

Actual row count:

```sql
SELECT
  'ref_users_big' AS 'table_name',
  COUNT(*) AS 'row_count'
FROM
  ref_users_big
UNION
SELECT
  'ref_zaps_big',
  COUNT(*)
FROM
  ref_zaps_big;
```

```sql
+---------------+-----------+
| table_name    | row_count |
+---------------+-----------+
| ref_users_big |   1000000 |
| ref_zaps_big  |   1000000 |
+---------------+-----------+
2 rows in set (2.42 sec)
```

<details>
  <summary>What's a UNION?</summary>

  A way to combine query results, regardless of any relation between tables or queries.
</details>

### SELECT

[MySQL docs.](https://dev.mysql.com/doc/refman/8.0/en/select.html)

You use it to select data from tables (or `/dev/stdin`). Any questions?

```sql
SELECT * FROM ref_zaps LIMIT 10 OFFSET 15;
```

```sql
+--------+----------+----------------------+---------------------+-----------------+
| zap_id | owned_by | shared_with          | created_at          | last_updated_at |
+--------+----------+----------------------+---------------------+-----------------+
|     16 |      788 | []                   | 2013-10-16 21:25:30 | NULL            |
|     17 |      689 | []                   | 2016-07-21 03:05:33 | NULL            |
|     18 |      735 | []                   | 2020-12-16 13:51:04 | NULL            |
|     19 |      802 | []                   | 2009-11-22 03:33:19 | NULL            |
|     20 |      297 | [529, 805, 541, 498] | 1997-07-11 15:05:07 | NULL            |
|     21 |      649 | []                   | 2015-05-18 20:08:31 | NULL            |
|     22 |      438 | []                   | 2006-12-14 15:28:30 | NULL            |
|     23 |      607 | []                   | 2013-04-15 17:57:19 | NULL            |
|     24 |      460 | []                   | 2018-01-28 02:05:59 | NULL            |
|     25 |      677 | []                   | 1995-06-07 21:46:30 | NULL            |
+--------+----------+----------------------+---------------------+-----------------+
10 rows in set (0.01 sec)
```

<details>
  <summary>Can you think of anything missing from this table? (HINT: SHOW CREATE TABLE)</summary>

  There's no foreign key linking `owned_by` to a given user! In fact, they're just randomly generated numbers, but there are pairings. Let's create a foreign key now:
  ```sql
  ALTER TABLE ref_zaps ADD CONSTRAINT zap_owner_id FOREIGN KEY (owned_by) REFERENCES ref_users (user_id);
  ```

  ```sql
  Query OK, 1000 rows affected (0.90 sec)
  Records: 1000  Duplicates: 0  Warnings: 0
  ```
<details>

### INSERT

[MySQL docs.](https://dev.mysql.com/doc/refman/8.0/en/insert.html)

`INSERT` is used to insert rows into a table. There is also an `UPSERT` equivalent, with the `ON DUPLICATE KEY UPDATE` clause. With this, if an `INSERT` would cause a key collision with a `UNIQUE` index (explicit or implicit, e.g. `PRIMARY KEY`), then an `UPDATE` of that row occurs instead.

```sql
INSERT INTO users
  first_name, last_name, user_id)
VALUES
  ("Leeroy", "Jenkins", 42);
```

```sql
ERROR 1062 (23000): Duplicate entry '42' for key 'users.PRIMARY'
```

Expectedly, that failed since `user_id`, which is our primary key, already has an entry at `42`.

```sql
SELECT * FROM
  users
WHERE
  user_id = 42\G
```

```sql
*************************** 1. row ***************************
        user_id: 42
     first_name: Ramona
      last_name: Odelet
      full_name: Odelet, Ramona
          email: ramona.odelet@lucid.com
           city: Foligno
        country: Italy
     created_at: 2003-07-29 07:34:15
last_updated_at: NULL
1 row in set (0.01 sec)
```

Now we can try again, this time with an instruction to perform an UPSERT.

```sql
INSERT INTO users
  (first_name, last_name, user_id)
VALUES
  ("Leeroy", "Jenkins", 42) AS vals
ON DUPLICATE KEY UPDATE
  first_name = vals.first_name,
  last_name = vals.last_name;
```

```sql
Query OK, 2 rows affected (0.21 sec)
```

```sql
SELECT * FROM users WHERE user_id = 42\G
```

```sql
*************************** 1. row ***************************
        user_id: 42
     first_name: Leeroy
      last_name: Jenkins
      full_name: Jenkins, Leeroy
          email: ramona.odelet@lucid.com
           city: Foligno
        country: Italy
     created_at: 2003-07-29 07:34:15
last_updated_at: 2023-02-27 13:24:26
1 row in set (0.01 sec)
```

While `full_name` updated, since it's a `GENERATED` column, `email` is now incorrect. Also, note that `last_updated_at` has changed from `NULL`, since we've modified the row.

Let's put the row back to how it was before.

<details>
  <summary>How can this be accomplished?</summary>

  ```sql
  -- first, let's be safe with a transaction
  START TRANSACTION;
  ```

  ```sql
  Query OK, 0 rows affected (0.01 sec)
  ```

  ```sql
  -- then, use UPDATE
  UPDATE users SET first_name = 'Ramona', last_name = 'Odelet' WHERE user_id = 42;
  ```

  ```sql
  Query OK, 1 row affected (0.01 sec)
  Rows matched: 1  Changed: 1  Warnings: 0
  ```

  ```sql
  -- next, verify the work
  SELECT * FROM users WHERE user_id = 42\G
  ```

  ```sql
  *************************** 1. row ***************************
          user_id: 42
       first_name: Ramona
        last_name: Odelet
        full_name: Odelet, Ramona
            email: ramona.odelet@lucid.com
             city: Foligno
          country: Italy
       created_at: 2003-07-29 07:34:15
  last_updated_at: 2023-02-27 13:30:10
  1 row in set (0.00 sec)
  ```

  ```sql
  -- finally, commit the result
  COMMIT;
  ```

  ```sql
  Query OK, 0 rows affected (0.08 sec)
  ```
</details>

### TABLE

[MySQL docs.](https://dev.mysql.com/doc/refman/8.0/en/table.html)

`TABLE` is syntactic sugar for `SELECT * FROM <table>`. Works great if you know the table is small, but be careful on large tables!

```sql
TABLE users\G
```

```sql
-- 9999 rows are above this...
*************************** 10000. row ***************************
        user_id: 10000
     first_name: Gabrila
      last_name: Lemmueu
      full_name: Lemmueu, Gabrila
          email: gabrila.lemmueu@urgent.com
           city: Itanagar
        country: India
     created_at: 2020-12-10 01:58:35
last_updated_at: NULL
10000 rows in set (0.48 sec)
```

## Joins

### Relational alegbra

Not a lot of it, I promise; just what we need to discuss joins.

* Union: `R ∪ S --- R OR S`
  * Implemented in MySQL via the `UNION` keyword
* Intersection: `R ∩ S --- R AND S`
  * Implemented in MySQL via `INNER JOIN`, or in MySQL 8.0.31, the `INTERSECT` keyword
* Difference: `R ≏ S --- R - S`
  * Implemented in MySQL 8.0.31 via the `EXCEPT` keyword, and can be emulated using `UNION` and `NOT IN`

If you're intersted in exploring relational alegbra, [this application](https://dbis-uibk.github.io/relax/calc/local/uibk/local/3) is quite useful to convert SQL to relational alegbra, and display the results.

### Types of joins

#### Cross

Before we demonstrate a cross join, you should have two small (very small, like < 10 rows) tables. You can either use what we learned earlier to create a new table from an existing one, or you can use any two of the following two tables: `northwind.orders_status`, `northwind.tax_status_name`, `test.ref_users_tiny`, `test.ref_users_zaps`. You can cross join across schemas if you'd like, although I can't promise the information will make any sense.

Also called a Cartesian Join. This produces `n x m` rows for the two groups being joined. That said, every other join can be thought of as a cross join with a predicate. In fact, `CROSS JOIN`, `JOIN`, and `INNER JOIN` are actually syntactically equivalent in MySQL (not ANSI SQL!), but for readability, it's preferred to only use `CROSS JOIN` if you actually intend to use it.

```sql
SELECT * FROM northwind.orders_status CROSS JOIN northwind.orders_tax_status;
```

```sql
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

#### Inner Join

The default (i.e. `JOIN` == `INNER JOIN`). This is `customers AND orders` with a predicate. We're also using `DISTINCT` here to limit the returned values - it returns unique tuples of all queried columns.

In MySQL 5.x, it was often more performant to use a `GROUP BY` aggregation, but the optimizer now (usually) returns the same results for both. It's important to measure the relative performance of having the database peform your filtering vs. having your application do so. Be mindful of the performance impact to other tenants (other queries for the database, and other Kubernetes pods for the application) in both scenarios, as well as the user experience.

```sql
SELECT DISTINCT
  company,
  job_title,
  ship_name
FROM
  northwind.customers
  JOIN northwind.orders ON customers.id = orders.customer_id;
```

```sql
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

<details>
<summary>What would it look like without DISTINCT?</summary>


</details>

#### Left Outer Join

Left and Right Joins are both a type of Outer Join, and often just called Left or Right Join. This is `customers OR orders` with a predicate and default value (`NULL`) for `orders`.

```sql
SELECT DISTINCT
```

```sql
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

#### Right Outer Join

Knowing how Left Join works, what do you think the results would be for a Right Join of the same data? What if the join order was reversed?

#### Full Outer Join

This is `customers OR orders` with a predicate and default value (`NULL`) for both tables. MySQL doesn't support `FULL JOIN` as a keyword, but it can be performed using `UNION` (or `UNION ALL` if duplicates are desired). In order to give meaningful information, we'll join three tables here.

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

### Specifying a column's table

It's worth noting here that thus far, we've avoided using specifying the table for a given column, because the columns have been unique. If there were multiple tables with a given column (e.g. `id`), we'd have to specify it. This is done by prefixing the column name with the table name, e.g. `suppliers.job_title`. Note that you can also alias a table name by immediately following it with the desired alias, e.g. `FROM suppliers s`, and the alias can then be used to specify the table for a given column.

```sql
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
SELECT
  CONCAT_WS(', ', s.last_name, s.first_name) AS supplier_name,
  s.job_title,
  CONCAT_WS(', ', e.last_name, e.first_name) AS employee_name
FROM
  suppliers s
  JOIN employees e ON s.job_title = e.job_title;
```

```sql
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

Indices, or indexes, _may_ speed up queries. Each table **should** have a primary key (it's not required*, but, please don't do this), which is one index. Additional indices, on single or multiple columns, may be created. Most of them are stored in [B+ trees](https://en.wikipedia.org/wiki/B%2B_tree), which are similar to [B-trees](https://en.wikipedia.org/wiki/B-tree).

Indices aren't free, however - when you create an index on a column, that column's values are copied to the aforementioned B+ tree. While disk space is relatively cheap, creating dozens of indices for columns that are infrequently queried should be avoided. Also, since `INSERTs` must also write to the index, they'll be slowed down somewhat. Finally, InnoDB limits a given table to a maximum of 64 secondary indices (that is, other than primary keys).

\* Prior to MySQL 8.0.30, if you don't create a primary key, the first `UNIQUE NOT NULL` index created is automatically promoted to become the primary key. If you don't have one of those either, the table will have no primary key†. Starting with MySQL 8.0.30, if no primary key is declared, an invisible column will be created called `my_row_id` and set to be the primary key.

† Not entirely true. A hidden index named `GEN_CLUST_INDEX` is created on an invisible (but a special kind of invisible, that you can never view) column named `ROW_ID` containing row IDs, but it's a monotonically increasing index that's shared globally across the entire database, not just that schema. Don't make InnoDB do this.

#### Single indices

We'll again look at the `test` schema, this time, the `ref_users` table. This table has 1 million rows, and was created by taking a [list of names](https://github.com/dominictarr/random-name/blob/master/names.txt) with 21985 rows, generating the schema with a program (as an aside, I got to play with C, which is always fun and frustrating), then loading it into the table. Since the table is two orders of magnitude larger than the input, there are obviously duplicated names, including some duplicated tuples of `first_name, last_name`. My table has nearly two orders of magnitude more duplicates than could be expected from a uniform distribution (962 duplicate tuples vs. the expected 45), which means my future as a statistician isn't great.

```sql
USE test;
```

```sql
Database changed
```

```sql
SELECT * FROM ref_users WHERE last_name = 'Safko';
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
CREATE INDEX first_name ON ref_users (first_name);
```

```sql
Query OK, 0 rows affected (36.93 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
ANALYZE TABLE ref_users;
+----------------+---------+----------+----------+
| Table          | Op      | Msg_type | Msg_text |
+----------------+---------+----------+----------+
| test.ref_users | analyze | status   | OK       |
+----------------+---------+----------+----------+
1 row in set (0.11 sec)
```

```sql
SELECT * FROM ref_users WHERE first_name = 'Safko';
```

```sql
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

The lookup is now essentially instantaneous. If this is a frequently performed query, this may be a wise decision. There are also times when you may not need an index - for example, remember that a `UNIQUE` constraint is also an index! Since `user_id` has a `UNIQUE` constraint on it, lookups via it are just as fast as by `id`. Whether or not you need a separate integer column as a key is a valid debate - in this case, simply using `user_id` as as the primary key would be reasonable.

#### JSON / Longtext

JSON has its own special requirements to be indexed, mostly if you're storing strings. First, you must select a specific part of the column's rows to be the indexed key, known as a functional key part. Additionally, the key has to have a prefix length assigned to it, but functional key parts don't allow that. Finally if you `CAST(foo) AS CHAR(n)` the selected part so the index is stored properly, the returned string has the `utf8mb4_0900_ai_ci` collation, but `JSON_UNQUOTE()` (which is done implicitly as part of selecting a part of a row to be indexed) has the `utf8mb4_bin` collation. The easiest workaround is to specify the latter's collation as part of the index creation. Also, this requires the stored data to be `k:v` objects, rather than arrays.

```sql
CREATE INDEX owned_idx ON zaps (
```

```sql
  (
    CAST(
      used_by ->> "$.user_id" AS CHAR(16)
    ) COLLATE utf8mb4_bin
  )
);
Query OK, 0 rows affected (0.50 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

Alternatively, if the key you want to index can be cast to an `int`, you can use generated columns to accomplish this; you can even (as of MySQL 8.0.23) make them invisible so they don't show up for normal queries:

```sql
ALTER TABLE
  zaps
ADD
  COLUMN used_by_idx_col BIGINT UNSIGNED GENERATED ALWAYS AS (
    CAST(
      used_by ->> "$.user_id" AS UNSIGNED
    )
  ) INVISIBLE;
```

```sql
Query OK, 0 rows affected (0.09 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
CREATE INDEX used_by_idx ON zaps (used_by_idx_col);
```

```sql
Query OK, 0 rows affected (0.36 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

This creates an invisible column `used_by_idx_col` which automatically generates a value based on the key `user_id` in the column `used_by`, casting it to an `UNSIGNED BIGINT`. The column is invisible unless specified:

```sql
SELECT * FROM zaps\G
```

```sql
*************************** 1. row ***************************
             id: 1
         zap_id: 1
     created_at: 2022-12-30 11:46:04
last_updated_at: NULL
       owned_by: 42
        used_by: {"user_id": "42"}
1 row in set (0.00 sec)
```

```sql
SELECT *, used_by_idx_col  FROM zaps\G
```

```sql
*************************** 1. row ***************************
             id: 1
         zap_id: 1
     created_at: 2022-12-30 11:46:04
last_updated_at: NULL
       owned_by: 42
        used_by: {"user_id": "42"}
used_by_idx_col: 42
1 row in set (0.00 sec)
```

#### Composite indices

An index can also be created across multiple columns - for InnoDB, up to 16.

```sql
CREATE INDEX full_name ON ref_users (first_name, last_name);
```

```sql
Query OK, 0 rows affected (40.09 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

First, we'll use `IGNORE INDEX` to direct SQL to ignore the index we just created. This query counts the duplicate name tuples. Since the `id` is being included, and `GROUPing` it would result in an empty set (as it's the primary key, and thus guaranteed to be unique), `ANY VALUE` must be specified to let MySQL know that the result can be non-deterministic. Finally, `EXPLAIN ANALYZE` is being used to run the query, and explain what it's doing. This differs from `EXPLAIN`, which guesses at what would be done, but doesn't actually perform the query. Be careful using `EXPLAIN ANALYZE`, especially with destructive actions, since those queries will actually be performed!

```sql
EXPLAIN ANALYZE
```

```sql
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
```

```sql
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
EXPLAIN ANALYZE
```

```sql
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
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Filter: (c > 1)  (actual time=8.627..9276.021 rows=962 loops=1)
    -> Group aggregate: count(0)  (actual time=0.756..8703.629 rows=999037 loops=1)
        -> Index scan on ref_users using full_name  (cost=100560.90 rows=997354) (actual time=0.683..5574.086 rows=1000000 loops=1)

1 row in set (9.28 sec)
```

With the index in place, an index scan is performed instead of two table scans, resulting in a ~2x speedup.

Another example, retreiving a specific doubled tuple that I know exists:

```sql
SELECT
  *
FROM
  ref_users USE INDEX()
WHERE
  first_name = 'Zoltai'
AND
  last_name = 'Tupler';
```

```sql
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
EXPLAIN ANALYZE
```

```sql
SELECT
  *
FROM
  ref_users IGNORE INDEX(full_name)
WHERE
  first_name = 'Zoltai'
  AND
  last_name = 'Tupler'\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Filter: (ref_users.last_name = 'Tupler')  (cost=11.18 rows=4) (actual time=3.944..4.044 rows=2 loops=1)
    -> Index lookup on ref_users using first_name (first_name='Zoltai')  (cost=11.18 rows=43) (actual time=3.922..4.003 rows=43 loops=1)

1 row in set (0.01 sec)
```

```sql
EXPLAIN ANALYZE
SELECT
  *
FROM
  ref_users IGNORE INDEX(first_name)
WHERE
  first_name = 'Zoltai'
AND
  last_name = 'Tupler'\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Index lookup on ref_users using full_name (first_name='Zoltai', last_name='Tupler')  (cost=0.70 rows=2) (actual time=0.369..0.394 rows=2 loops=1)

1 row in set (0.00 sec)
```

#### Testing indices

MySQL 8 added the ability to toggle an index on and off, without actually dropping it. This way, if you want to test whether or not an index is helpful, you can toggle it off, observe query performance, and then decide whether or not to leave it.

```sql
ALTER TABLE ref_users ALTER INDEX first_name INVISIBLE;
```

```sql
Query OK, 0 rows affected (0.28 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

#### Descending indices

By default, indices are sorted in ascending order. While they can still be used when reversed, it's not as fast (although the performance difference may be minimal - test your theory before committing to it). If you are frequently querying something with `ORDER BY <row> DESC`, it may be helpful to instead create an index in descending order.

```sql
CREATE INDEX first_desc ON ref_users (first_name DESC);
```

```sql
Query OK, 0 rows affected (41.18 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

#### When indicies aren't helpful

You may have noticed in a few of the previous `EXPLAIN ANALYZE` statements two different kinds of inner joins - `nested loop inner join`, and `inner hash join`. A nested loop join is exactly what it sounds like:

```python
for tuple_i in table_1:
    for tuple_j in table_2
        if join_is_satisfied(tuple_i, tuple_j):
            yield (tuple_i, tuple_j)
```

This has `O(MN)` time complexity, where `M` and `N` are the number of tuples in each table. If there's an index, the 2nd loop is using it for the lookup rather than another table scan, which makes the time complexity `O(Mlog(N))`, but with large sizes this is still quite bad. Here is an example on two tables with one million rows each:

```sql
EXPLAIN ANALYZE
SELECT
  full_name
FROM
  ref_users
JOIN
  zaps
ON
  ref_users.user_id = zaps.owned_by\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Nested loop inner join  (cost=498015.60 rows=993197) (actual time=6.998..360927.896 rows=1000000 loops=1)
    -> Table scan on zaps  (cost=100160.95 rows=993197) (actual time=6.685..8804.370 rows=1000000 loops=1)
    -> Single-row index lookup on ref_users using user_id (user_id=zaps.owned_by)  (cost=0.30 rows=1) (actual time=0.350..0.350 rows=1 loops=1000000)

1 row in set (6 min 2.41 sec)
```

A better solution is a hash join, specifically a grace hash join, named after the GRACE database created in the 1980s at the University of Tokyo, which pioneered this method.

```python
dict_table_1 = {id: row for id, row in table_1}
dict_table_2 = {id: row for id, row in table_2}
for tuple_i in dict_table_1.items():
    for tuple_j in dict_table_2.items():
        if join_is_satisfied(tuple_i, tuple_j):
            yield (tuple_i, tuple_j)
```

While this looks very similar, there are details I've glossed over about the partioning method (it's recursive), and of course hash lookups are (optimally) `O(1)`, which speeds things up tremendously. The total time complexity for this method is `3(M+N)`.

MySQL [added a hash join in 8.0.18](https://dev.mysql.com/blog-archive/hash-join-in-mysql-8/), but it comes with some limitations; chiefly that a table must fit into memory, and annoyingly, that the optimizer will often decide to use a nested loop if indexes exist. If it can be used, though, compare the difference:

```sql
EXPLAIN ANALYZE
SELECT
  full_name
FROM
  ref_users
IGNORE INDEX (user_id)
JOIN
  zaps
ON
  ref_users.user_id = zaps.owned_by\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Inner hash join (ref_users.user_id = zaps.owned_by)  (cost=98991977261.77 rows=993197) (actual time=7814.295..21403.160 rows=1000000 loops=1)
    -> Table scan on ref_users  (cost=0.03 rows=996699) (actual time=0.402..9319.650 rows=1000000 loops=1)
    -> Hash
        -> Table scan on zaps  (cost=100160.95 rows=993197) (actual time=4.566..6810.026 rows=1000000 loops=1)

1 row in set (21.93 sec)
```

### Predicates

For these, we'll shift back to the `northwind` schema.

```sql
USE northwind;
```

```sql
Database changed
```

#### WHERE

`WHERE` is the easiest to understand and apply, and will cover most of your needs.

```sql
SELECT
  id,
  CONCAT_WS(', ', last_name, first_name) AS name,
  city,
  job_title
FROM
  customers
WHERE
  city = 'Seattle';
```

``sql
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
SELECT
  id,
  CONCAT_WS(', ', last_name, first_name) AS name,
  city,
  job_title
FROM
  customers
WHERE
  city LIKE 'Sea%';
```

```sql
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
EXPLAIN SELECT
  id,
  city,
  CONCAT_WS(', ', last_name, first_name) AS name,
  job_title
FROM
  customers USE INDEX(city)
WHERE
  city LIKE 'Sea%'\G
```

```sql
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

```sql
-- NOTE: with the leading wildcard, the index is disabled, even if FORCED
EXPLAIN SELECT
  id,
  city,
  CONCAT_WS(', ', last_name, first_name) AS name,
  job_title
FROM
  customers FORCE INDEX(city)
WHERE
  city LIKE '%Sea%'\G
```

```sql
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
```

```sql
-- NOTE: the new syntax requires the table and column to be specified
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
  city LIKE 'Sea%'\G
```

```sql
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

Earlier, we used `HAVING` in a `GROUP BY` aggregation. The difference between the two is that `WHERE` filters the results before they're sent to be aggregated, whereas `HAVING` filters the aggregation, and thus predicates relying on the aggregation result can be used. It's not limited to only aggregation results, though - a common use case is to allow the use of aliases or subquery results in filtering. Be aware that it's generally more performant to use `WHERE` if possible (consider re-writing your query if it isn't).

```sql
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

The desired output here is to produce the name and city of any customer who has a job title starting with `Purchasing` and has placed a new order. Since the `order_status` column is the result of a subquery (returning the text name of a given order status ID), it can't be filtered with `WHERE`.

```sql
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
```

```sql
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
```

```sql
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
```

```sql
-- This is less of a warning, and more of a note stating that the query optimizer decided to resolve order.status_id in the first SELECT, rather than the subquery where it's referenced.
SHOW WARNINGS\G
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

## Query optimization

Finally into the fun stuff!

First, I'll spoil a lot of this - it's likely that you won't have to do much of this. MySQL's optimizer is actually pretty decent. That said, there are times when you will, and knowing what _should_ be happening, and how to compare it to what is actually happening is a useful skill.

### SELECT *

If you're just exploring a schema, there's nothing wrong with `SELECT * FROM <table> LIMIT 10` or some other small number (< ~1000). It will be nearly instantaneous. However, the problem arises when you're also using `ORDER BY`. Recall that we had a composite index on `(first_name, last_name)` called `full_name`. Compare these two:

```sql
EXPLAIN ANALYZE
SELECT
  *
FROM
  ref_users
ORDER BY
  first_name,
  last_name\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Sort: ref_users.first_name, ref_users.last_name  (cost=100495.40 rows=996699) (actual time=12199.513..12603.379 rows=1000000 loops=1)
    -> Table scan on ref_users  (cost=100495.40 rows=996699) (actual time=1.755..7039.004 rows=1000000 loops=1)

1 row in set (13.68 sec)
```

```sql
EXPLAIN ANALYZE
SELECT
  id,
  first_name,
  last_name
FROM
  ref_users
ORDER BY
  first_name,
  last_name\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Index scan on ref_users using full_name  (cost=100495.40 rows=996699) (actual time=0.433..5413.188 rows=1000000 loops=1)

1 row in set (6.39 sec)
```

Since the the table includes columns not covered by the index (`user_id`), it would take longer to use the index and then find columns not in the index than to just do a table scan. Observe:

```sql
EXPLAIN ANALYZE
SELECT
  *
FROM
  ref_users
FORCE INDEX(full_name)
ORDER BY
  first_name,
  last_name\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Index scan on ref_users using full_name  (cost=348844.90 rows=996699) (actual time=11.273..65858.816 rows=1000000 loops=1)

1 row in set (1 min 7.13 sec)
```

In comparison, if your `ORDER BY` is covered by the index (the primary key - `id` here - is implicitly part of indices, and thus doesn't cause a slowdown), queries can use it, and are much faster! If you're writing software that will be accessing a database, and you don't actually need all of the columns, don't request them. Take the time to be deliberate in what you request.

### OFFSET / LIMIT

If you need to get `n` rows from the middle of a table, unless you have a really good reason to do so, please don't do this:

```sql
USE test;
Database changed
```

```sql
-- The alternate form (and, IMO, the clearer one) is LIMIT 10 OFFSET 500000
SELECT * FROM ref_users LIMIT 500000,10;
```

```sql
+--------+------------+-----------+---------+
| id     | first_name | last_name | user_id |
+--------+------------+-----------+---------+
| 500001 | Cutlor     | Marlee    |  500001 |
| 500002 | Schaper    | Tol       |  500002 |
| 500003 | Toney      | Wait      |  500003 |
| 500004 | Robbin     | Jordanson |  500004 |
| 500005 | Weiner     | Mendelson |  500005 |
| 500006 | Willow     | Joses     |  500006 |
| 500007 | Weatherby  | Reginald  |  500007 |
| 500008 | Frendel    | Hoxsie    |  500008 |
| 500009 | Schonfeld  | Charmion  |  500009 |
| 500010 | O'Doneven  | Theone    |  500010 |
+--------+------------+-----------+---------+
10 rows in set (3.10 sec)
```

Doing this causes a table scan up to the specified offset. Far better, if you have a known monotonic number (like `id`), is to use a `WHERE` predicate:

```sql
SELECT * FROM ref_users WHERE id > 500000 LIMIT 10;
```

```sql
+--------+------------+-----------+---------+
| id     | first_name | last_name | user_id |
+--------+------------+-----------+---------+
| 500001 | Cutlor     | Marlee    |  500001 |
| 500002 | Schaper    | Tol       |  500002 |
| 500003 | Toney      | Wait      |  500003 |
| 500004 | Robbin     | Jordanson |  500004 |
| 500005 | Weiner     | Mendelson |  500005 |
| 500006 | Willow     | Joses     |  500006 |
| 500007 | Weatherby  | Reginald  |  500007 |
| 500008 | Frendel    | Hoxsie    |  500008 |
| 500009 | Schonfeld  | Charmion  |  500009 |
| 500010 | O'Doneven  | Theone    |  500010 |
+--------+------------+-----------+---------+
10 rows in set (0.01 sec)
```

Using `id` as the filter allows it to be used for an index range scan, which is nearly instant. If you were doing this programmatically to support pagination, the last value of `id` could be used for the next iteration's predicate.

### DISTINCT

`DISTINCT` is a very useful keyword for many operations when you want to not show duplicates. Unfortunately, it also adds a fairly hefty load to the database. That's not to say you _can't_ use it, but when writing code that will end up using this, ask yourself if you could intead handle de-duplication in the application. This also comes with tradeoffs, of course - you're now pulling more data over the network, and increasing load on the application. Generally speaking, databases are bound first by disk and memory, rather than CPU or network, so using compression (increased CPU load) and/or sending more data (not using `DISTINCT`) tends to increase overall performance, but you should experiment and profile your code.

This also tends to be something that works well early on with little load, but as either the database or application grows, it becomes unwieldy.

```sql
EXPLAIN ANALYZE
SELECT
  first_name,
  last_name
FROM
  ref_users\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Index scan on ref_users using full_name  (cost=101977.37 rows=996699) (actual time=1.163..6200.004 rows=1000000 loops=1)

1 row in set (7.09 sec)
```

```sql
EXPLAIN ANALYZE
SELECT DISTINCT
  first_name,
  last_name
FROM
  ref_users\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Group (no aggregates)  (actual time=0.429..9110.455 rows=999037 loops=1)
    -> Index scan on ref_users using full_name  (cost=101977.37 rows=996699) (actual time=0.403..6004.725 rows=1000000 loops=1)

1 row in set (9.96 sec)
```

Bear in mind that the above was using an index scan! If there isn't a covering index available, this is the `DISTINCT` result:

```sql
EXPLAIN ANALYZE
SELECT DISTINCT
  first_name,
  last_name
FROM
  ref_users
USE INDEX()\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Table scan on <temporary>  (actual time=0.015..694.662 rows=999037 loops=1)
    -> Temporary table with deduplication  (cost=100495.40 rows=996699) (actual time=13580.563..14471.841 rows=999037 loops=1)
        -> Table scan on ref_users  (cost=100495.40 rows=996699) (actual time=0.973..7443.480 rows=1000000 loops=1)

1 row in set (15.72 sec)
```

## Cleanup

This isn't something you'll do often, if at all, so may as well do so now, eh?

```sql
DROP SCHEMA foo;
```

```sql
Query OK, 0 rows affected (0.05 sec)
```
