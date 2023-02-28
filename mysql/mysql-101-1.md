# MySQL 101 Part II

- [MySQL 101 Part II](#mysql-101-part-ii)
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
+--------+-------------------+--------------+--------------------+
| zap_id | full_name         | city         | country            |
+--------+-------------------+--------------+--------------------+
|    411 | Jemena, Wyatt     | Chhatarpur   | India              |
|    794 | Marienthal, Shirl | Guayaramerin | Bolivia            |
|    830 | McGrody, Cointon  | Guatemala    | Guatemala          |
|    697 | Harriman, Neda    | Huimin       | China              |
|    110 | Lauter, Lorelle   | Bereeda      | Somalia            |
|    942 | Lauter, Lorelle   | Bereeda      | Somalia            |
|    772 | Race, Marsha      | Matanzas     | Dominican Republic |
|    676 | Craven, Elfreda   | NanTong      | China              |
|    715 | Azral, Terese     | Askim        | Norway             |
|    405 | Hepza, Dyanne     | Heerenveen   | Netherlands        |
+--------+-------------------+--------------+--------------------+
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
  LEFT JOIN ref_zaps_joins z ON u.user_id = z.owned_by
LIMIT 10;
```

```sql
+---------+-------------------+--------+----------+
| user_id | full_name         | zap_id | owned_by |
+---------+-------------------+--------+----------+
|       1 | Jemena, Wyatt     |    411 |        1 |
|       2 | Marienthal, Shirl |    794 |        2 |
|       3 | Gorlin, Alene     |   NULL |     NULL |
|       4 | McGrody, Cointon  |    830 |        4 |
|       5 | Harriman, Neda    |    697 |        5 |
|       6 | Lauter, Lorelle   |    942 |        6 |
|       6 | Lauter, Lorelle   |    110 |        6 |
|       7 | Race, Marsha      |    772 |        7 |
|       8 | Craven, Elfreda   |    676 |        8 |
|       9 | Azral, Terese     |    715 |        9 |
+---------+-------------------+--------+----------+
10 rows in set (0.05 sec)
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
  RIGHT JOIN ref_zaps_joins z ON u.user_id = z.owned_by
LIMIT 10;
```

```sql
+---------+--------------------+--------+----------+
| user_id | full_name          | zap_id | owned_by |
+---------+--------------------+--------+----------+
|     602 | Pruchno, Kariotta  |      1 |      602 |
|     593 | Adall, Greta       |      2 |      593 |
|    NULL | NULL               |      3 |        0 |
|     548 | Creedon, Barbara   |      4 |      548 |
|     957 | Laszlo, Alleyn     |      5 |      957 |
|     777 | Kopaz, Meir        |      6 |      777 |
|     648 | Gildea, Christophe |      7 |      648 |
|     959 | Rigby, Cecile      |      8 |      959 |
|     569 | Zobkiw, Freemon    |      9 |      569 |
|     429 | Reinhart, Glynnis  |     10 |      429 |
+---------+--------------------+--------+----------+
10 rows in set (0.02 sec)
```

You can translate any `LEFT JOIN` to a `RIGHT JOIN` simply by swapping the order of the tables being joined:

```sql
SELECT
  u.user_id,
  u.full_name,
  z.zap_id,
  z.owned_by
FROM
  ref_zaps_joins u
  RIGHT JOIN ref_users u ON u.user_id = z.owned_by
LIMIT 10;
```

```sql
+---------+-------------------+--------+----------+
| user_id | full_name         | zap_id | owned_by |
+---------+-------------------+--------+----------+
|       1 | Jemena, Wyatt     |    411 |        1 |
|       2 | Marienthal, Shirl |    794 |        2 |
|       3 | Gorlin, Alene     |   NULL |     NULL |
|       4 | McGrody, Cointon  |    830 |        4 |
|       5 | Harriman, Neda    |    697 |        5 |
|       6 | Lauter, Lorelle   |    942 |        6 |
|       6 | Lauter, Lorelle   |    110 |        6 |
|       7 | Race, Marsha      |    772 |        7 |
|       8 | Craven, Elfreda   |    676 |        8 |
|       9 | Azral, Terese     |    715 |        9 |
+---------+-------------------+--------+----------+
10 rows in set (0.08 sec)
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

To efficiently see what it's doing, you can run two queries, appending `ORDER BY -user_id DESC` and `ORDER BY user_id`, which represents the top and bottom of the result.

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
CREATE INDEX user_name ON ref_users_big (last_name(3));
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

JSON has its own special requirements to be indexed, mostly if you're storing strings. First, you must select a specific part of the column's rows to be the indexed key, known as a functional key part. Additionally, the key has to have a prefix length assigned to it, but functional key parts don't allow that. Finally if you `CAST(foo) AS CHAR(n)` the selected part so the index is stored properly, the returned string has the `utf8mb4_0900_ai_ci` collation, but `JSON_UNQUOTE()` (which is done implicitly as part of selecting a part of a row to be indexed) has the `utf8mb4_bin` collation. The easiest workaround is to specify the latter's collation as part of the index creation. Also, this requires the stored data to be `k:v` objects, rather than arrays.

```sql
CREATE INDEX owned_idx ON zaps (
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
