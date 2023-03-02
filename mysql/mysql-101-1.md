# MySQL 101 Part II

- [MySQL 101 Part II](#mysql-101-part-ii)
  - [Queries](#queries)
    - [Predicates](#predicates)
      - [WHERE](#where)
    - [SELECT](#select)
      - [Working with JSON](#working-with-json)
        - [Finding non-null arrays](#finding-non-null-arrays)
        - [Checking for a value inside an array](#checking-for-a-value-inside-an-array)
        - [Extracting scalars from an object](#extracting-scalars-from-an-object)
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
      - [Partial indices](#partial-indices)
      - [Functional indices](#functional-indices)
      - [JSON / Longtext](#json--longtext)
      - [Composite indices](#composite-indices)
      - [Testing indices](#testing-indices)
      - [Descending indices](#descending-indices)
      - [When indicies aren't helpful](#when-indicies-arent-helpful)
      - [HAVING](#having)
  - [Query optimization](#query-optimization)
    - [SELECT \*](#select-)
    - [OFFSET / LIMIT](#offset--limit)
    - [DISTINCT](#distinct)
  - [Cleanup](#cleanup)

## Queries

### Predicates

A predicate is a function which asserts that something is true or false. You can think of it like a filter.

#### WHERE

`WHERE` is the easiest to understand and apply, and will cover most of your needs.

```sql
SELECT
  user_id, first_name, last_name
FROM
  users
WHERE
  country = 'Zimbabwe';
```

```sql
+---------+------------+-----------+
| user_id | first_name | last_name |
+---------+------------+-----------+
|     106 | Ivonne     | Barmen    |
|    1149 | Myca       | Flieger   |
|    2143 | Dallas     | Nimesh    |
|    4401 | Jeana      | Naga      |
|    4623 | Godiva     | Adal      |
|    5582 | Lexie      | Fenwick   |
|    5586 | Carrie     | Nich      |
|    5793 | Marten     | Casady    |
|    6072 | Feliza     | Culhert   |
|    6467 | Wood       | O'Connor  |
|    7093 | Miriam     | Galliett  |
|    7669 | Cele       | Belden    |
|    7675 | Araldo     | Hoes      |
|    8106 | Imojean    | Beaudoin  |
|    9438 | Sibby      | Luedtke   |
|    9566 | Eb         | Cattima   |
|    9606 | Alard      | Frodina   |
+---------+------------+-----------+
17 rows in set (0.22 sec)
```

Note that we filtered the results with a predicate that wasn't even in the result set (`country`).

You may also have seen or used the wildcard `%` with `LIKE` and `NOT LIKE`.

```sql
SELECT
  user_id, first_name, last_name
FROM
  users
WHERE
  country
LIKE 'Zim%';
```

```sql
+---------+------------+-----------+
| user_id | first_name | last_name |
+---------+------------+-----------+
|     106 | Ivonne     | Barmen    |
|    1149 | Myca       | Flieger   |
|    2143 | Dallas     | Nimesh    |
|    4401 | Jeana      | Naga      |
|    4623 | Godiva     | Adal      |
|    5582 | Lexie      | Fenwick   |
|    5586 | Carrie     | Nich      |
|    5793 | Marten     | Casady    |
|    6072 | Feliza     | Culhert   |
|    6467 | Wood       | O'Connor  |
|    7093 | Miriam     | Galliett  |
|    7669 | Cele       | Belden    |
|    7675 | Araldo     | Hoes      |
|    8106 | Imojean    | Beaudoin  |
|    9438 | Sibby      | Luedtke   |
|    9566 | Eb         | Cattima   |
|    9606 | Alard      | Frodina   |
+---------+------------+-----------+
17 rows in set (0.22 sec)
```

These two are functionally equivalent queries. However, if there is an index on the predicate column, and you use a leading wildcard (e.g. `LIKE '%babwe'`), MySQL cannot use the index, and will instead perform a table scan. If you can avoid using leading wildcards on large tables, do so. It's also worth noting that there are many times when the query optimizer determines that the table scan would be faster than using an index, and so will do so anyway. [Index usage can be hinted](https://dev.mysql.com/doc/refman/8.0/en/index-hints.html), forced, and ignored, although as of MySQL 8.0.20, the old syntax (which included hints) [is deprecated](https://dev.mysql.com/doc/refman/8.0/en/optimizer-hints.html#optimizer-hints-index-level). Examples of both are below with an `EXPLAIN SELECT`. They're from a different schema and table, as I've already set up the index.

```sql
EXPLAIN SELECT
  user_id, first_name, last_name
FROM
  test.ref_users
USE INDEX (country)
WHERE
  country
LIKE 'Zim%'\G
```

```sql
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ref_users
   partitions: NULL
         type: range
possible_keys: country
          key: country
      key_len: 1023
          ref: NULL
         rows: 3
     filtered: 100.00
        Extra: Using index condition
1 row in set, 1 warning (0.01 sec)
```

```sql
EXPLAIN SELECT
  user_id, first_name, last_name
FROM
  test.ref_users
FORCE INDEX (country)
WHERE
  country
LIKE '%babwe'\G

```sql
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ref_users
   partitions: NULL
         type: ALL
possible_keys: NULL
          key: NULL
      key_len: NULL
          ref: NULL
         rows: 1000
     filtered: 11.11
        Extra: Using where
1 row in set, 1 warning (0.00 sec)
```

Even when using `FORCE INDEX`, it's not being used, because it can't.

```sql
EXPLAIN SELECT
  user_id, first_name, last_name
FROM
  test.ref_users
/*+ INDEX(ref_users country) */
WHERE
  country
LIKE 'Zim%'\G
```

The new syntax, which looks like a C-style comment, requires both the table and column to be listed.

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
</details>

#### Working with JSON

Both JSON arrays and objects can be stored in JSON columns. Using them in queries isn't as straight-forward as other column types.

##### Finding non-null arrays

```sql
SELECT *
FROM
  ref_zaps
WHERE JSON_LENGTH(shared_with) > 0
LIMIT 10;
```

```sql
+--------+----------+----------------------+---------------------+-----------------+
| zap_id | owned_by | shared_with          | created_at          | last_updated_at |
+--------+----------+----------------------+---------------------+-----------------+
|     20 |      297 | [529, 805, 541, 498] | 1997-07-11 15:05:07 | NULL            |
|     40 |      312 | [395, 721, 397, 930] | 2016-11-15 03:42:41 | NULL            |
|     60 |      469 | [261, 565, 326, 637] | 2011-09-21 11:40:22 | NULL            |
|     80 |      505 | [753, 766, 812, 521] | 2001-07-04 15:28:08 | NULL            |
|    100 |      459 | [884, 23, 163, 654]  | 2008-08-30 12:53:32 | NULL            |
|    120 |      411 | [730, 484, 530, 449] | 2012-09-02 00:42:20 | NULL            |
|    140 |      191 | [611, 798, 984, 583] | 2004-12-14 04:08:09 | NULL            |
|    160 |      310 | [941, 353, 499, 668] | 2003-01-22 01:05:04 | NULL            |
|    180 |      463 | [679, 639, 760, 784] | 2022-01-22 04:31:00 | NULL            |
|    200 |       36 | [308, 955, 485, 298] | 2015-10-17 21:42:16 | NULL            |
+--------+----------+----------------------+---------------------+-----------------+
10 rows in set (0.02 sec)
```

##### Checking for a value inside an array

```sql
SELECT
  zap_id,
  owned_by,
  shared_with,
  user_id,
  full_name
FROM ref_zaps
JOIN
  ref_users ON
JSON_CONTAINS(shared_with, JSON_ARRAY(ref_users.user_id))
LIMIT 10;
```

```sql
+--------+----------+---------------------+---------+--------------------+
| zap_id | owned_by | shared_with         | user_id | full_name          |
+--------+----------+---------------------+---------+--------------------+
|    240 |      697 | [3, 854, 486, 907]  |       3 | Gorlin, Alene      |
|    100 |      459 | [884, 23, 163, 654] |      23 | Schnurr, Sissie    |
|    700 |      947 | [28, 173, 33, 899]  |      28 | Russi, Bab         |
|    560 |      869 | [258, 197, 724, 31] |      31 | Quince, Caryl      |
|    700 |      947 | [28, 173, 33, 899]  |      33 | Langille, Tonya    |
|    740 |      888 | [41, 221, 402, 301] |      41 | Kruter, Bonni      |
|    460 |      566 | [45, 793, 553, 162] |      45 | Schuh, Gasparo     |
|    940 |      211 | [497, 973, 323, 48] |      48 | Aylsworth, Steffen |
|    260 |      861 | [313, 52, 334, 457] |      52 | Delwyn, Karoline   |
|    420 |      667 | [524, 527, 948, 60] |      60 | Magen, Sherill     |
+--------+----------+---------------------+---------+--------------------+
10 rows in set (0.88 sec)
```

##### Extracting scalars from an object

You can select a JSON column mixed in with non-JSON as you'd expect, and the entire contents will be displayed.

```sql
SELECT
  user_id,
  email,
  user_json
FROM
  gensql
LIMIT 10;
```

```sql
+---------+-------------------------------+-----------------------------------------------------------------------------------------------+
| user_id | email                         | user_json                                                                                     |
+---------+-------------------------------+-----------------------------------------------------------------------------------------------+
|       1 | abba.wilder@bodacious.com     | {"a_key": "playable", "b_key": {"c_key": ["unscathed", "humongous", "surplus", "mousiness"]}} |
|       2 | antonetta.bosson@chaplain.com | {"a_key": "obedience", "b_key": {"c_key": ["depletion", "carve", "driveway", "primate"]}}     |
|       3 | cobb.fondea@contusion.com     | {"a_key": "activity", "b_key": {"c_key": ["famine", "huskiness", "unleash", "unknotted"]}}    |
|       4 | hanan.keelin@aspect.com       | {"a_key": "iron", "b_key": {"c_key": ["exact", "postcard", "sauciness", "dispatch"]}}         |
|       5 | kinna.lytle@epidermis.com     | {"a_key": "flannels", "b_key": {"c_key": ["sherry", "graded", "crusader", "rumble"]}}         |
|       6 | carolynn.sewoll@starch.com    | {"a_key": "extrude", "b_key": {"c_key": ["harmony", "ferris", "confirm", "elevate"]}}         |
|       7 | ola.pride@defile.com          | {"a_key": "blurt", "b_key": {"c_key": ["expectant", "half", "coming", "remover"]}}            |
|       8 | orella.acima@subwoofer.com    | {"a_key": "grape", "b_key": {"c_key": ["wrist", "galley", "fragment", "scurvy"]}}             |
|       9 | odilia.thorr@daredevil.com    | {"a_key": "numbing", "b_key": {"c_key": ["glutinous", "repacking", "reliant", "polygon"]}}    |
|      10 | berrie.marybella@undertow.com | {"a_key": "unadvised", "b_key": {"c_key": ["grove", "cornhusk", "darkening", "grazing"]}}     |
+---------+-------------------------------+-----------------------------------------------------------------------------------------------+
10 rows in set (0.01 sec)
```

You can also extract specific keys:

```sql
-- the ->> operator is shorthand for JSON_UNQUOTE(JSON_EXTRACT())
SELECT
  email,
  user_json->>'$.b_key'
FROM
  gensql
LIMIT 10;
```

```sql
+---------+-------------------------------+---------------------------------------------------------------+
| user_id | email                         | user_json->>'$.b_key'                                         |
+---------+-------------------------------+---------------------------------------------------------------+
|       1 | abba.wilder@bodacious.com     | {"c_key": ["unscathed", "humongous", "surplus", "mousiness"]} |
|       2 | antonetta.bosson@chaplain.com | {"c_key": ["depletion", "carve", "driveway", "primate"]}      |
|       3 | cobb.fondea@contusion.com     | {"c_key": ["famine", "huskiness", "unleash", "unknotted"]}    |
|       4 | hanan.keelin@aspect.com       | {"c_key": ["exact", "postcard", "sauciness", "dispatch"]}     |
|       5 | kinna.lytle@epidermis.com     | {"c_key": ["sherry", "graded", "crusader", "rumble"]}         |
|       6 | carolynn.sewoll@starch.com    | {"c_key": ["harmony", "ferris", "confirm", "elevate"]}        |
|       7 | ola.pride@defile.com          | {"c_key": ["expectant", "half", "coming", "remover"]}         |
|       8 | orella.acima@subwoofer.com    | {"c_key": ["wrist", "galley", "fragment", "scurvy"]}          |
|       9 | odilia.thorr@daredevil.com    | {"c_key": ["glutinous", "repacking", "reliant", "polygon"]}   |
|      10 | berrie.marybella@undertow.com | {"c_key": ["grove", "cornhusk", "darkening", "grazing"]}      |
+---------+-------------------------------+---------------------------------------------------------------+
10 rows in set (0.00 sec)
```


Or nest extractions:

```sql
SELECT
  user_id,
  email,
  user_json->>'$.b_key.c_key'
FROM
  gensql
LIMIT 10;
```

```sql
+---------+-------------------------------+----------------------------------------------------+
| user_id | email                         | user_json->>'$.b_key.c_key'                        |
+---------+-------------------------------+----------------------------------------------------+
|       1 | abba.wilder@bodacious.com     | ["unscathed", "humongous", "surplus", "mousiness"] |
|       2 | antonetta.bosson@chaplain.com | ["depletion", "carve", "driveway", "primate"]      |
|       3 | cobb.fondea@contusion.com     | ["famine", "huskiness", "unleash", "unknotted"]    |
|       4 | hanan.keelin@aspect.com       | ["exact", "postcard", "sauciness", "dispatch"]     |
|       5 | kinna.lytle@epidermis.com     | ["sherry", "graded", "crusader", "rumble"]         |
|       6 | carolynn.sewoll@starch.com    | ["harmony", "ferris", "confirm", "elevate"]        |
|       7 | ola.pride@defile.com          | ["expectant", "half", "coming", "remover"]         |
|       8 | orella.acima@subwoofer.com    | ["wrist", "galley", "fragment", "scurvy"]          |
|       9 | odilia.thorr@daredevil.com    | ["glutinous", "repacking", "reliant", "polygon"]   |
|      10 | berrie.marybella@undertow.com | ["grove", "cornhusk", "darkening", "grazing"]      |
+---------+-------------------------------+----------------------------------------------------+
10 rows in set (0.01 sec)
```

```sql
-- the -> operator is shorthand for JSON_EXTRACT()
-- arrays are 0-indexed, so this is a slice, like lst[1:3]
SELECT
  email,
  user_json->'$.b_key.c_key[1 to 2]'
FROM
  gensql
LIMIT 10;
```

```sql
+--------------------------------+------------------------------------+
| email                          | user_json->'$.e_key.d_key[1 to 2]' |
+--------------------------------+------------------------------------+
| donelle.labors@amused.com      | ["idealness", "unplug"]            |
| mackenzie.youngran@abridge.com | ["waffle", "scion"]                |
| elset.kramer@tiny.com          | ["dimple", "manpower"]             |
| theresita.faxen@plentiful.com  | ["appetizer", "huskiness"]         |
| salomi.pasco@each.com          | ["tiptop", "unsnap"]               |
| ashia.garate@varied.com        | ["bauble", "mayflower"]            |
| jonathan.aulea@chastise.com    | ["senior", "silicon"]              |
| gillan.mcnalley@slain.com      | ["provider", "gradient"]           |
| madelon.harleigh@defiling.com  | ["evoke", "tidy"]                  |
| dagny.iverson@entryway.com     | ["baton", "skillful"]              |
+--------------------------------+------------------------------------+
10 rows in set (0.02 sec)
```

See [MySQL docs](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html) for much more about JSON operations.

### INSERT

[MySQL docs.](https://dev.mysql.com/doc/refman/8.0/en/insert.html)

`INSERT` is used to insert rows into a table. There is also an `UPSERT` equivalent, with the `ON DUPLICATE KEY UPDATE` clause. With this, if an `INSERT` would cause a key collision with a `UNIQUE` index (explicit or implicit, e.g. `PRIMARY KEY`), then an `UPDATE` of that row occurs instead.

```sql
INSERT INTO users
  (first_name, last_name, user_id)
VALUES
  ('Leeroy', 'Jenkins', 42);
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
SELECT
  z.zap_id,
  u.user_id,
  u.full_name
FROM
  ref_users_tiny u
CROSS JOIN
  ref_zaps_tiny z;
```

```sql
+--------+---------+-------------------+
| zap_id | user_id | full_name         |
+--------+---------+-------------------+
|      1 |       4 | McGrody, Cointon  |
|      1 |       3 | Gorlin, Alene     |
|      1 |       2 | Marienthal, Shirl |
|      1 |       1 | Jemena, Wyatt     |
|      2 |       4 | McGrody, Cointon  |
|      2 |       3 | Gorlin, Alene     |
|      2 |       2 | Marienthal, Shirl |
|      2 |       1 | Jemena, Wyatt     |
|      3 |       4 | McGrody, Cointon  |
|      3 |       3 | Gorlin, Alene     |
|      3 |       2 | Marienthal, Shirl |
|      3 |       1 | Jemena, Wyatt     |
|      4 |       4 | McGrody, Cointon  |
|      4 |       3 | Gorlin, Alene     |
|      4 |       2 | Marienthal, Shirl |
|      4 |       1 | Jemena, Wyatt     |
+--------+---------+-------------------+
16 rows in set (0.01 sec)
```

#### Inner Join

The default (i.e. `JOIN` == `INNER JOIN`). This is `users AND zaps` with a predicate.

```sql
SELECT
  z.zap_id,
  u.full_name,
  u.city,
  u.country
FROM
  ref_users u
JOIN
  ref_zaps z
ON
  u.user_id = z.owned_by
LIMIT 10;
```

```sql
+--------+-------------------+-------------+----------------+
| zap_id | full_name         | city        | country        |
+--------+-------------------+-------------+----------------+
|    411 | MacPherson, Addie | Latina      | Italy          |
|    794 | Airla, Valaree    | Pribram     | Czech Republic |
|    830 | Kirschner, Robby  | Bikaner     | India          |
|    697 | Bilski, Lewiss    | Vörderås    | Sweden         |
|    110 | Yamauchi, Marleah | Rotterdam   | Netherlands    |
|    942 | Yamauchi, Marleah | Rotterdam   | Netherlands    |
|    772 | Calore, Ania      | Miyakojima  | Japan          |
|    676 | Breger, Gratiana  | Valkeakoski | Finland        |
|    715 | Serafina, Janith  | Morant Bay  | Jamaica        |
|    405 | Beckman, Pavla    | Wackersdorf | Germany        |
+--------+-------------------+-------------+----------------+
10 rows in set (0.02 sec)
```

#### Left Outer Join

Left and Right Joins are both a type of Outer Join, and often just called Left or Right Join. This is `users OR zaps` with a predicate and default value (`NULL`) for `zaps`.

```sql
SELECT
  u.user_id,
  u.full_name,
  z.zap_id,
  z.owned_by
FROM
  ref_users u
LEFT JOIN
  ref_zaps_joins z
ON
  u.user_id = z.owned_by
LIMIT 10;
```

```sql
+---------+-------------------+--------+----------+
| user_id | full_name         | zap_id | owned_by |
+---------+-------------------+--------+----------+
|       1 | MacPherson, Addie |    411 |        1 |
|       2 | Airla, Valaree    |    794 |        2 |
|       3 | Nett, Sheppard    |   NULL |     NULL |
|       4 | Kirschner, Robby  |    830 |        4 |
|       5 | Bilski, Lewiss    |    697 |        5 |
|       6 | Yamauchi, Marleah |    942 |        6 |
|       6 | Yamauchi, Marleah |    110 |        6 |
|       7 | Calore, Ania      |    772 |        7 |
|       8 | Breger, Gratiana  |    676 |        8 |
|       9 | Serafina, Janith  |    715 |        9 |
+---------+-------------------+--------+----------+
10 rows in set (0.09 sec)
```

Of course, we previously put a foreign key on `zaps.owned_by`, precisely to prevent this kind of thing from happening. Still, you can see how this kind of query could be useful.

#### Right Outer Join

This is the same thing, but with the tables reversed:

```sql
SELECT
  u.user_id,
  u.full_name,
  z.zap_id,
  z.owned_by
FROM
  ref_users u
RIGHT JOIN
  ref_zaps_joins z
ON
  u.user_id = z.owned_by
LIMIT 10;
```

```sql
+---------+------------------+--------+----------+
| user_id | full_name        | zap_id | owned_by |
+---------+------------------+--------+----------+
|     602 | Hirz, Datha      |      1 |      602 |
|     593 | Meldoh, Vergil   |      2 |      593 |
|    NULL | NULL             |      3 |        0 |
|     548 | Philps, Ardelia  |      4 |      548 |
|     957 | Joash, Electra   |      5 |      957 |
|     777 | Levinson, Lenore |      6 |      777 |
|     648 | Vas, Tiphanie    |      7 |      648 |
|     959 | Brink, Kaia      |      8 |      959 |
|     569 | Lasser, Garrard  |      9 |      569 |
|     429 | Adamsen, Justen  |     10 |      429 |
+---------+------------------+--------+----------+
10 rows in set (0.09 sec)
```

You can translate any `LEFT JOIN` to a `RIGHT JOIN` simply by swapping the order of the tables being joined:

```sql
SELECT
  u.user_id,
  u.full_name,
  z.zap_id,
  z.owned_by
FROM
  ref_zaps_joins z
RIGHT JOIN
  ref_users u
ON
  u.user_id = z.owned_by
LIMIT 10;
```

```sql
+---------+-------------------+--------+----------+
| user_id | full_name         | zap_id | owned_by |
+---------+-------------------+--------+----------+
|       1 | MacPherson, Addie |    411 |        1 |
|       2 | Airla, Valaree    |    794 |        2 |
|       3 | Nett, Sheppard    |   NULL |     NULL |
|       4 | Kirschner, Robby  |    830 |        4 |
|       5 | Bilski, Lewiss    |    697 |        5 |
|       6 | Yamauchi, Marleah |    942 |        6 |
|       6 | Yamauchi, Marleah |    110 |        6 |
|       7 | Calore, Ania      |    772 |        7 |
|       8 | Breger, Gratiana  |    676 |        8 |
|       9 | Serafina, Janith  |    715 |        9 |
+---------+-------------------+--------+----------+
10 rows in set (0.15 sec)
```

#### Full Outer Join

This is `users OR zaps` with a predicate and default value (`NULL`) for both tables. MySQL doesn't support `FULL JOIN` as a keyword, but it can be performed using `UNION` (or `UNION ALL` if duplicates are desired).

NOTE: This query will produce 1150 rows as written.

```sql
SELECT
  u.user_id,
  u.full_name,
  z.zap_id,
  z.owned_by
FROM
  ref_users u
  LEFT JOIN ref_zaps_joins z ON u.user_id = z.owned_by
UNION ALL
SELECT
  u.user_id,
  u.full_name,
  z.zap_id,
  z.owned_by
FROM
  ref_users u
  RIGHT JOIN ref_zaps_joins z ON u.user_id = z.owned_by
WHERE
  u.user_id IS NULL;
```

To efficiently see what it's doing, you can run two queries, appending `ORDER BY -user_id DESC` and `ORDER BY user_id`, which represents the top and bottom of the result. Don't forget to add a `LIMIT` as well!

<details>
  <summary>What is -user_id?</summary>

  It's shorthand for the math expression `(0 - user_id)`, which effectively is the same thing as `ORDER BY ... ASC`, but it places `NULL` values last. Postgres avoids this weird trick and just has the `NULLS {FIRST, LAST}` option for ordering.
</details>

### Specifying a column's table

You may have noticed that we've used aliases for many tables, e.g. `ref_users u`, and then notating columns with that alias as a prefix, e.g. `u.user_id`. This is not required for single tables, of course, nor is it requires with joins if every column name is unique. However, it's considered a good practice when using multiple tables.

### Indices

Indices, or indexes, _may_ speed up queries. Each table **should** have a primary key (it's not required*, but, please don't do this), which is one index. Additional indices, on single or multiple columns, may be created. Most of them are stored in [B+ trees](https://en.wikipedia.org/wiki/B%2B_tree), which are similar to [B-trees](https://en.wikipedia.org/wiki/B-tree).

Indices aren't free, however - when you create an index on a column, that column's values are copied to the aforementioned B+ tree. While disk space is relatively cheap, creating dozens of indices for columns that are infrequently queried should be avoided. Also, since `INSERTs` must also write to the index, they'll be slowed down somewhat. Finally, InnoDB limits a given table to a maximum of 64 secondary indices (that is, other than primary keys).

<details>
<summary>Obscure facts about tables without primary keys</summary>

\* Prior to MySQL 8.0.30, if you don't create a primary key, the first `UNIQUE NOT NULL` index created is automatically promoted to become the primary key. If you don't have one of those either, the table will have no primary key†. Starting with MySQL 8.0.30, if no primary key is declared, an invisible column will be created called `my_row_id` and set to be the primary key.

† Not entirely true. A hidden index named `GEN_CLUST_INDEX` is created on an invisible (but a special kind of invisible, that you can never view) column named `ROW_ID` containing row IDs, but it's a monotonically increasing index that's shared globally across the entire database, not just that schema. Don't make InnoDB do this.
</details>

#### Single indices

Here, we'll switch over to `%_big` tables, which have 1,000,000 rows each.

```sql
SELECT
  user_id,
  full_name,
  city,
  country
FROM
  ref_users_big
WHERE
  last_name = 'Safko';
```

```sql
+---------+------------------+------------------------+----------------+
| user_id | full_name        | city                   | country        |
+---------+------------------+------------------------+----------------+
|   66826 | Safko, Elwyn     | Arad                   | Romania        |
|   68759 | Safko, Vance     | Saint-Jérôme           | Canada         |
|   81384 | Safko, Robinett  | Hornchurch             | United Kingdom |
|   92580 | Safko, Daisi     | Sherwood Park          | Canada         |
|  121219 | Safko, Karalee   | Miami Gardens          | United States  |
|  124408 | Safko, Kyrstin   | Hawick                 | United Kingdom |
|  150615 | Safko, Kleon     | Leigh                  | United Kingdom |
|  151266 | Safko, Elita     | Abag Qi                | China          |
|  155926 | Safko, Berthe    | Tullebølle             | Denmark        |
|  168897 | Safko, Hazlett   | Valletta               | Malta          |
|   ...   |     ...          |         ...            |      ...       |
|  900935 | Safko, Tommy     | Paris                  | France         |
|  925514 | Safko, Rancell   | Nampa                  | United States  |
|  928486 | Safko, Garry     | Bardhaman              | India          |
|  932457 | Safko, Desiree   | Kherson                | Ukraine        |
|  945316 | Safko, Courtnay  | Saint Marys            | Canada         |
|  947072 | Safko, Leonie    | Durango                | Mexico         |
|  948263 | Safko, Jarred    | Las Vegas              | United States  |
|  959464 | Safko, Gordie    | Madison                | United States  |
|  972002 | Safko, Adriena   | Ubud                   | Indonesia      |
|  982089 | Safko, Gan       | Milpitas               | United States  |
+---------+------------------+------------------------+----------------+
76 rows in set (12.24 sec)
```

Let's create an index on the last name.

```sql
CREATE INDEX last_name ON ref_users_big (last_name);
```

```sql
Query OK, 0 rows affected (45.08 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

```sql
SELECT * FROM ref_users_big WHERE last_name = 'Safko';
```

```sql
-- the same results as above
76 rows in set (0.04 sec)
```

The lookup is now essentially instantaneous. If this is a frequently performed query, this may be a wise decision. There are also times when you may not need an index - for example, remember that a `UNIQUE` constraint is also an index. Since all of our users in this table have an email address which is `first.last@domain.com`, you might be tempted to add a predicate of `WHERE email LIKE '%safko%'` instead of adding an index, but alas - leading wildcards disallow the use of indexes, so it requires a full table scan.

#### Partial indices

Starting with MySQL 8.0.13, you can also create an index on a prefix of a column for string types (`CHAR`, `VARCHAR`, etc.), and for `TEXT` and `BLOB` columns you must do this.

This will create an index on the first 3 characters of last_name:

```sql
ALTER TABLE ref_users_big DROP INDEX user_name;
CREATE INDEX last_name_partial ON ref_users_big (last_name(3));
```

```sql
Query OK, 0 rows affected (0.31 sec)
Records: 0  Duplicates: 0  Warnings: 0

Query OK, 0 rows affected (37.85 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

Speed for the new query is slower than before (0.16 seconds vs. 0.04 seconds), as expected, but 160 milliseconds for hashing three characters honestly isn't that bad. If you have tremendously large tables, limited disk space, or are worried about the write performance impact, this may be a good option for you.

#### Functional indices

You can also create an index that is itself an expression:

```sql
CREATE INDEX
  created_month
ON ref_users_big ((MONTH(created_at)));
```

Note the double parentheses around the expression.

```sql
Query OK, 0 rows affected (41.15 sec)
Records: 0  Duplicates: 0  Warnings: 0
```

What this specifically allows you to do is treat the `created_at` month value as an integer:

```sql
EXPLAIN ANALYZE SELECT
  user_id, email, created_at
FROM
  ref_users_big
WHERE
  MONTH(created_at) = 6\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Index lookup on ref_users_big using created_month (month(created_at)=6)  (cost=19952.91 rows=153858) (actual time=2.303..12051.690 rows=82815 loops=1)

1 row in set (15.49 sec)
```

Note that in this case, it's actually _slower_ with the index, likely due to the cardinality of the month.

```sql
EXPLAIN ANALYZE SELECT
  user_id, email, created_at
FROM
  ref_users_big
USE INDEX()
WHERE
  MONTH(created_at) = 6\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Filter: (month(ref_users_big.created_at) = 6)  (cost=100955.37 rows=994330) (actual time=1.114..11135.192 rows=82815 loops=1)
    -> Table scan on ref_users_big  (cost=100955.37 rows=994330) (actual time=1.010..9733.530 rows=1000000 loops=1)

1 row in set (11.43 sec)
```

#### JSON / Longtext

JSON has its own special requirements to be indexed, mostly if you're storing strings. First, you must select a specific part of the column's rows to be the indexed key, known as a functional key part. Additionally, the key has to have a prefix length assigned to it. Depending on the version of MySQL you're using, there may also be collation differences between the return value from various JSON functions and native storage of strings. Finally, this requires the stored data to be `k:v` objects, rather than arrays.

Here, we're using a multi-valued index, which behind the scenes is creating a virtual, invisible column to store the extracted JSON array as a character array.

```sql
CREATE INDEX user_json_array_key ON gensql (
  (
    CAST(
      user_json -> '$.b_key.c_key' AS CHAR(64) ARRAY
    )
  )
);
```

See [MySQL docs](https://dev.mysql.com/doc/refman/8.0/en/create-index.html#create-index-multi-valued) for more information on indexing JSON values, and properly using them.

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
SELECT
  ANY_VALUE(id),
  first_name,
  last_name,
  COUNT(*) c
FROM
  ref_users_big
IGNORE INDEX(full_name)
GROUP BY
  first_name,
  last_name
HAVING
  c > 1\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Filter: (c > 1)  (actual time=23295.903..24686.641 rows=4318 loops=1)
    -> Table scan on <temporary>  (actual time=0.005..903.621 rows=995670 loops=1)
        -> Aggregate using temporary table  (actual time=23295.727..24415.358 rows=995670 loops=1)
            -> Table scan on ref_users_big  (cost=104920.32 rows=995522) (actual time=2.329..10156.102 rows=1000000 loops=1)

1 row in set (25.26 sec)
```

The query took 25.26 seconds, and resulted in 4318 rows. The output is read from the bottom up - a table scan was performed on the entire table, then a temporary table with the `GROUP BY` aggregation was created, and finally a second table scan on that temporary table was performed to find the duplicated tuples.

If you're curious, `actual time` is in milliseconds, and consists of two timings - the first is the time to initiate the step and return the first row; the second is the time to initiate the step and return all rows. `cost` is an arbitrary number indicating what the query cost optimizer thinks the query costs to perform, and is meaningless.

```sql
EXPLAIN ANALYZE
SELECT
  ANY_VALUE(id),
  first_name,
  last_name,
  COUNT(*) c
FROM
  ref_users_big
GROUP BY
  first_name,
  last_name
HAVING
  c > 1\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Filter: (c > 1)  (actual time=6.318..12202.646 rows=4318 loops=1)
    -> Group aggregate: count(0)  (actual time=0.864..11447.233 rows=995670 loops=1)
        -> Index scan on ref_users_big using full_name  (cost=104920.32 rows=995522) (actual time=0.815..7315.098 rows=1000000 loops=1)

1 row in set (12.32 sec)
```

With the index in place, an index scan is performed instead of two table scans, resulting in a ~2x speedup.

Another example, retreiving a specific doubled tuple that I know exists:

```sql
SELECT
  user_id,
  full_name,
  email,
  city,
  country
FROM
  ref_users_big
WHERE
  first_name = 'Ashlie'
AND
  last_name = 'Godred';
```

```sql
+---------+----------------+-------------------------+----------+--------------+
| user_id | full_name      | email                   | city     | country      |
+---------+----------------+-------------------------+----------+--------------+
|  974206 | Godred, Ashlie | ashlie.godred@mushy.com | Mikkeli  | Finland      |
|  987301 | Godred, Ashlie | ashlie.godred@suave.com | Pretoria | South Africa |
+---------+----------------+-------------------------+----------+--------------+
2 rows in set (0.01 sec)
```

vs. if `USE INDEX()` is added to the query:

```sql
+---------+----------------+-------------------------+----------+--------------+
| user_id | full_name      | email                   | city     | country      |
+---------+----------------+-------------------------+----------+--------------+
|  974206 | Godred, Ashlie | ashlie.godred@mushy.com | Mikkeli  | Finland      |
|  987301 | Godred, Ashlie | ashlie.godred@suave.com | Pretoria | South Africa |
+---------+----------------+-------------------------+----------+--------------+
2 rows in set (14.60 sec)
```

Note that `USE INDEX()` is valid syntax to tell MySQL to ignore all indexes.

If instead, either the `full_name` or `last_name_partial` index we made perviously is ignored on its own, its complement will be used, and they're effectively equally fast due to the filtered result set - here, using the partial index on `last_name` dropped the candidate tuples from 1,000,000 to 1,066.

```sql
EXPLAIN ANALYZE
SELECT
  user_id,
  full_name,
  email,
  city,
  country
FROM
  ref_users_big IGNORE INDEX(full_name)
WHERE
  first_name = 'Ashlie'
  AND
  last_name = 'Godred'\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Filter: ((ref_users_big.last_name = 'Godred') and (ref_users_big.first_name = 'Ashlie'))  (cost=641.79 rows=0) (actual time=315.346..322.278 rows=2 loops=1)
    -> Index lookup on ref_users_big using last_name_partial (last_name='Godred')  (cost=641.79 rows=1066) (actual time=6.602..317.360 rows=1066 loops=1)

1 row in set (0.34 sec)
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

```sql
EXPLAIN ANALYZE
SELECT
  user_id,
  full_name,
  email,
  city,
  country
FROM
  ref_users_big
WHERE
  first_name = 'Ashlie'
  AND
  last_name = 'Godred'\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Filter: ((ref_users_big.last_name = 'Godred') and (ref_users_big.first_name = 'Ashlie'))  (cost=641.79 rows=0) (actual time=315.346..322.278 rows=2 loops=1)
    -> Index lookup on ref_users_big using last_name_partial (last_name='Godred')  (cost=641.79 rows=1066) (actual time=6.602..317.360 rows=1066 loops=1)

1 row in set (0.34 sec)
```

#### Descending indices

By default, indices are sorted in ascending order. While they can still be used when reversed, it's not as fast (although the performance difference may be minimal - test your theory before committing to it). If you are frequently querying something with `ORDER BY <row> DESC`, it may be helpful to instead create an index in descending order.

```sql
CREATE INDEX first_desc ON ref_users_big (first_name DESC);
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
  ref_users_big
JOIN
  ref_zaps_big
ON
  ref_users_big.user_id = ref_zaps_big.owned_by\G
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

#### HAVING

Earlier, we used `HAVING` in a `GROUP BY` aggregation. The difference between the two is that `WHERE` filters the results before they're sent to be aggregated, whereas `HAVING` filters the aggregation, and thus predicates relying on the aggregation result can be used. It's not limited to only aggregation results, though - a common use case is to allow the use of aliases or subquery results in filtering. Be aware that it's generally more performant to use `WHERE` if possible (consider re-writing your query if it isn't), but sometimes, you need it.

```sql
SELECT
  ref_users_big.city,
  COUNT(ref_zaps_big.zap_id) as zap_count
FROM
  ref_users_big
LEFT JOIN
  ref_zaps_big
ON
  ref_users_big.user_id = ref_zaps_big.owned_by
GROUP BY
  ref_users_big.city
HAVING
  zap_count > 250;
```

```sql
+----------+-----------+
| city     | zap_count |
+----------+-----------+
| Hsin-chu |       260 |
| Vitória  |       293 |
| Cordoba  |       290 |
| Gdañsk   |       292 |
+----------+-----------+
4 rows in set (32.86 sec)
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
  ref_users_big
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
  user_id,
  first_name,
  last_name
FROM
  ref_users_big
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

In comparison, if your `ORDER BY` is covered by the index (the primary key - `user_id` here - is implicitly part of indices, and thus doesn't cause a slowdown), queries can use it, and are much faster! If you're writing software that will be accessing a database, and you don't actually need all of the columns, don't request them. Take the time to be deliberate in what you request.

### OFFSET / LIMIT

If you need to get `n` rows from the middle of a table, unless you have a really good reason to do so, please don't do this:

```sql
-- The alternate form (and, IMO, the clearer one) is LIMIT 10 OFFSET 500000
SELECT
  user_id,
  full_name
FROM
  ref_users_big
LIMIT 500000,10;
```

```sql
+---------+-------------------+
| user_id | full_name         |
+---------+-------------------+
|  500001 | Ader, Wilona      |
|  500002 | Lindsley, Angy    |
|  500003 | Scarito, Vladimir |
|  500004 | Hoenack, Rossy    |
|  500005 | Cooley, Theobald  |
|  500006 | Pineda, Gaven     |
|  500007 | Harberd, Odie     |
|  500008 | Engleman, Mendy   |
|  500009 | Michon, Dionysus  |
|  500010 | Seaden, Leigha    |
+---------+-------------------+
10 rows in set (6.29 sec)
```

Doing this causes a table scan up to the specified offset. Far better, if you have a known monotonic number (like `id`), is to use a `WHERE` predicate:

```sql
SELECT
  user_id,
  full_name
FROM
  ref_users_big
WHERE user_id > 500000
LIMIT 10;
```

```sql
+---------+-------------------+
| user_id | full_name         |
+---------+-------------------+
|  500001 | Ader, Wilona      |
|  500002 | Lindsley, Angy    |
|  500003 | Scarito, Vladimir |
|  500004 | Hoenack, Rossy    |
|  500005 | Cooley, Theobald  |
|  500006 | Pineda, Gaven     |
|  500007 | Harberd, Odie     |
|  500008 | Engleman, Mendy   |
|  500009 | Michon, Dionysus  |
|  500010 | Seaden, Leigha    |
+---------+-------------------+
10 rows in set (0.02 sec)
```

Using `user_id` as the filter allows it to be used for an index range scan, which is nearly instant. If you were doing this programmatically to support pagination, the last value of `id` could be used for the next iteration's predicate.

### DISTINCT

`DISTINCT` is a very useful keyword for many operations when you want to not show duplicates. Unfortunately, it also adds a fairly hefty load to the database. That's not to say you _can't_ use it, but when writing code that will end up using this, ask yourself if you could intead handle de-duplication in the application. This also comes with tradeoffs, of course - you're now pulling more data over the network, and increasing load on the application. Generally speaking, databases are bound first by disk and memory, rather than CPU or network, so using compression (increased CPU load) and/or sending more data (not using `DISTINCT`) tends to increase overall performance, but you should experiment and profile your code.

This also tends to be something that works well early on with little load, but as either the database or application grows, it becomes unwieldy.

```sql
EXPLAIN ANALYZE
SELECT
  first_name,
  last_name
FROM
  ref_users_big\G
```

```sql
*************************** 1. row ***************************
EXPLAIN: -> Table scan on ref_users_big  (cost=101365.53 rows=995522) (actual time=1.815..7213.716 rows=1000000 loops=1)

1 row in set (8.13 sec)
```

```sql
EXPLAIN ANALYZE
SELECT DISTINCT
  first_name,
  last_name
FROM
  ref_users_big\G
```

```sql
EXPLAIN: -> Table scan on <temporary>  (actual time=0.005..765.220 rows=995670 loops=1)
    -> Temporary table with deduplication  (cost=101050.45 rows=995522) (actual time=15306.678..16296.289 rows=995670 loops=1)
        -> Table scan on ref_users_big  (cost=101050.45 rows=995522) (actual time=0.825..8718.651 rows=1000000 loops=1)

1 row in set (17.73 sec)
```
## Cleanup

This isn't something you'll do often, if at all, so may as well do so now, eh?

```sql
DROP SCHEMA foo;
```

```sql
Query OK, 0 rows affected (0.05 sec)
```
