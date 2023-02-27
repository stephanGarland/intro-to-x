# MySQL 102 - WIP

### WITH (Common Table Expressions)

[MySQL docs.](https://dev.mysql.com/doc/refman/8.0/en/with.html)

`WITH` can be used to create a temporary named result set, scoped to the statement in which it exists. They can also be recursive. A demonstration that's probably not useful in reality follows, but it does demonstrate how MySQL can be made to use indexes, even when it normally couldn't. Here, we're trying to select a random row from a large table. The row ID is selected with a sub-query that multiplies the output of `RAND()` (a float between 0-1) by the last `id` row in the table.

```sql
mysql>
EXPLAIN ANALYZE SELECT
  *
FROM
  ref_users
WHERE
  id = (
    SELECT
      FLOOR(
        (
          SELECT
            RAND() * (
              SELECT
                id
              FROM
                ref_users
              ORDER BY
                id DESC
              LIMIT
                1
            )
        )
      )
  );
*************************** 1. row ***************************
EXPLAIN: -> Filter: (ref_users.id = floor((rand() * (select #4))))  (cost=10799.04 rows=99735) (actual time=1545.462..8220.073 rows=3 loops=1)
    -> Table scan on ref_users  (cost=10799.04 rows=997354) (actual time=0.441..6723.994 rows=1000000 loops=1)
    -> Select #4 (subquery in condition; run only once)
        -> Limit: 1 row(s)  (cost=0.00 rows=1) (actual time=0.079..0.079 rows=1 loops=1)
            -> Index scan on ref_users using PRIMARY (reverse)  (cost=0.00 rows=1) (actual time=0.077..0.077 rows=1 loops=1)

1 row in set, 2 warnings (8.22 sec)
```

Since `RAND()` is evaluated for every row [when used with WHERE](https://dev.mysql.com/doc/refman/8.0/en/mathematical-functions.html#function_rand), it's not constant, and thus can't be used with indices. Also, you may wind up with more than one result!

If instead the `RAND()` call is placed into a CTE, it can be optimized:

```sql
mysql>
EXPLAIN ANALYZE
WITH rand AS (
  SELECT
    FLOOR(
      (
        SELECT
          RAND() * (
            SELECT
              id
            FROM
              ref_users
            ORDER BY
              id DESC
            LIMIT
              1
          )
      )
    )
)
SELECT
  *
FROM
  ref_users
WHERE
  id IN (TABLE rand);
*************************** 1. row ***************************
EXPLAIN: -> Nested loop inner join  (cost=0.55 rows=1) (actual time=0.569..0.583 rows=1 loops=1)
    -> Filter: (`<subquery2>`.`FLOOR((SELECT RAND() * (SELECT id FROM ref_users ORDER BY id DESC LIMIT 1)))` is not null)  (cost=0.20 rows=1) (actual time=0.085..0.095 rows=1 loops=1)
        -> Table scan on <subquery2>  (cost=0.20 rows=1) (actual time=0.005..0.012 rows=1 loops=1)
            -> Materialize with deduplication  (cost=0.00 rows=1) (actual time=0.082..0.090 rows=1 loops=1)
                -> Filter: (rand.`FLOOR((SELECT RAND() * (SELECT id FROM ref_users ORDER BY id DESC LIMIT 1)))` is not null)  (cost=0.00 rows=1) (actual time=0.017..0.023 rows=1 loops=1)
                    -> Table scan on rand  (cost=2.61 rows=1) (actual time=0.010..0.014 rows=1 loops=1)
                        -> Materialize CTE rand  (cost=0.00 rows=1) (actual time=0.013..0.018 rows=1 loops=1)
                            -> Rows fetched before execution  (cost=0.00 rows=1) (never executed)
                            -> Select #5 (subquery in projection; run only once)
                                -> Limit: 1 row(s)  (cost=0.00 rows=1) (actual time=0.313..0.314 rows=1 loops=1)
                                    -> Index scan on ref_users using PRIMARY (reverse)  (cost=0.00 rows=1) (actual time=0.310..0.310 rows=1 loops=1)
    -> Filter: (ref_users.id = `<subquery2>`.`FLOOR((SELECT RAND() * (SELECT id FROM ref_users ORDER BY id DESC LIMIT 1)))`)  (cost=0.35 rows=1) (actual time=0.477..0.479 rows=1 loops=1)
        -> Single-row index lookup on ref_users using PRIMARY (id=`<subquery2>`.`FLOOR((SELECT RAND() * (SELECT id FROM ref_users ORDER BY id DESC LIMIT 1)))`)  (cost=0.35 rows=1) (actual time=0.468..0.469 rows=1 loops=1)

1 row in set, 1 warning (0.00 sec)
```

## Stored Procedures

[MySQL docs.](https://dev.mysql.com/doc/refman/8.0/en/create-procedure.html)

Stored Procedures (and Stored Functions) are a way to write SQL as functions, to be called as needed. Most normal SQL queries are accepted, as well as conditionals, loops, and the ability to accept arguments and return values. The main difference between the two is that Stored Procedures may accept arguments and write out data to variables, whereas Stored Functions may accept arguments, and return a value.

Their main advantage is that known, tested queries can be stored and later called from an application. Their main disadvantage is that they require people with reasonably good SQL skills to write them, else it's unlikely they'll exceed the performance of an ORM like Django.

As an example, I used this to fill `zaps` with data (NOTE: this is not an example of a well-designed stored procedure, merely one that demonstrates a variety of concepts):

```sql
DELIMITER // -- This is needed so that the individual commands don't end the stored procedure
CREATE PROCEDURE insert_zaps(IN num_rows int, IN pct_shared float) -- Two input args are needed
BEGIN
  DECLARE loop_count bigint; -- Variables are initialized with a type
  DECLARE len_table bigint;
  DECLARE rand_base float;
  DECLARE rand_offset float;
  DECLARE rand_ts timestamp;
  DECLARE rand_user bigint;
  DECLARE shared_with_user bigint;
  SELECT id INTO len_table FROM test.ref_users ORDER BY id DESC LIMIT 1; -- SELECT INTO can be used
  SET loop_count = 1; -- Or, if the value is simple, simply assigned
  WHILE loop_count <= num_rows DO
    SET rand_base = RAND();
    SET rand_offset = RAND();
    SET rand_ts = TIMESTAMP(
                    FROM_UNIXTIME(
                      UNIX_TIMESTAMP(NOW()) - FLOOR(
                        0 + (
                          RAND() * 86400 * 365 * 10
                        )
                      )
                    )
                  ); -- This creates a random timestamp between now and 10 years ago
    WITH rand AS (
        SELECT
          FLOOR(
            (
              SELECT
                rand_base * len_table
            )
          )
      )
      SELECT
        id
      INTO rand_user
      FROM
        test.ref_users
      WHERE
        id IN (TABLE rand); -- This is the CTE demonstrated earlier to determine the table length
    INSERT INTO zaps (zap_id, created_at, owned_by) VALUES (loop_count, rand_ts, rand_user);
    IF ROUND(rand_base, 1) > (1 - pct_shared) THEN -- Roughly determine the amount of shared Zaps
      SELECT CAST(FLOOR(rand_base * rand_offset * len_table) AS unsigned) INTO shared_with_user;
      UPDATE
        zaps
      SET
        shared_with = JSON_ARRAY_APPEND(
          shared_with,
          '$',
          shared_with_user
        ) -- JSON_ARRAY_APPEND(array, key, value)
      WHERE
        id = loop_count;
    END IF;
    SET loop_count = loop_count + 1;
  END WHILE;
  END //
  DELIMITER ;
```
