# SQL JOINs

## Planning Notes

Topic: SQL JOINs

Working angle: JOINs are one of the most important SQL concepts because they let you combine related data across multiple tables. This topic should help someone understand what each JOIN returns, when to use it, and how to recognize the result set.

Audience:
- Backend developers
- Data analysts
- Data engineers
- SQL beginners moving beyond single-table queries

Core message:
JOINs combine rows from multiple tables using related columns. The type of JOIN controls which rows are included when matches exist or do not exist.

Example tables:
- `Users`
- `Orders`
- `Products`
- `Employees`

Common join key examples:
- `Users.id = Orders.user_id`
- `Employees.manager_id = Employees.id`

Sample data for examples:

`Users`

| id | name  |
|---:|-------|
| 1  | Ana   |
| 2  | Ben   |
| 3  | Cara  |

`Orders`

| id  | user_id | total |
|----:|--------:|------:|
| 101 | 1       | 50    |
| 102 | 1       | 25    |
| 103 | 4       | 80    |

What this setup demonstrates:
- Ana has two matching orders.
- Ben and Cara have no orders.
- Order `103` points to a missing user.
- One-to-many joins can return more rows than the left table contains.

## Content Outline

### 1. SQL JOINs

Subtitle: The Most Important SQL Concept

JOINs combine data from multiple tables using related columns. Mastering JOINs is essential for backend development, data engineering, analytics, and database design.

Key idea:
Use JOINs when the answer to a question requires data that lives in more than one table.

Important vocabulary:
- Join key: the column or columns used to match rows.
- Join predicate: the condition after `ON`.
- Primary key: a column that uniquely identifies a row in its own table.
- Foreign key: a column that points to a row in another table.
- Preserved table: the table whose unmatched rows are still returned in an outer join.

Basic query shape:

```sql
SELECT columns
FROM table_a a
JOIN table_b b ON a.key = b.key;
```

### 2. INNER JOIN

Subtitle: Only Matching Rows

Returns records that exist in both tables. Rows without a matching key are excluded.

Diagram concept:
- Left table: `Users`
- Right table: `Orders`
- Highlight: intersection only

SQL example:

```sql
SELECT *
FROM Users u
INNER JOIN Orders o ON u.id = o.user_id;
```

Use when:
You only want users who have matching orders.

Result idea with the sample data:
- Ana appears twice because she has two orders.
- Ben and Cara are excluded because they have no orders.
- Order `103` is excluded because it has no matching user.

### 3. LEFT JOIN

Subtitle: Everything From the Left Table

Returns every row from the left table and matching rows from the right table. If no match exists, right-side columns return `NULL`.

Diagram concept:
- Left table: `Users`
- Right table: `Orders`
- Highlight: all left rows plus matches

SQL example:

```sql
SELECT *
FROM Users u
LEFT JOIN Orders o ON u.id = o.user_id;
```

Use when:
You want all users, even users who have no orders.

Result idea with the sample data:
- Ana appears twice.
- Ben appears once with `NULL` order columns.
- Cara appears once with `NULL` order columns.
- Order `103` is excluded because it is only on the right side.

Common pattern:
Find users with no orders.

```sql
SELECT u.id, u.name
FROM Users u
LEFT JOIN Orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

### 4. RIGHT JOIN

Subtitle: Everything From the Right Table

Returns every row from the right table and matching rows from the left table. If no match exists, left-side columns return `NULL`.

Diagram concept:
- Left table: `Users`
- Right table: `Orders`
- Highlight: all right rows plus matches

SQL example:

```sql
SELECT *
FROM Users u
RIGHT JOIN Orders o ON u.id = o.user_id;
```

Use when:
You want all orders, even if a matching user row is missing.

Note:
Many teams prefer rewriting `RIGHT JOIN` as a `LEFT JOIN` by switching table order because it is often easier to read.

Equivalent `LEFT JOIN` rewrite:

```sql
SELECT *
FROM Orders o
LEFT JOIN Users u ON u.id = o.user_id;
```

### 5. FULL OUTER JOIN

Subtitle: Everything From Both Tables

Returns all rows from both tables. Matching rows are merged, while non-matching rows contain `NULL` values for the missing side.

Diagram concept:
- Left table: `Users`
- Right table: `Orders`
- Highlight: both tables

SQL example:

```sql
SELECT *
FROM Users u
FULL OUTER JOIN Orders o ON u.id = o.user_id;
```

Use when:
You need to see all records from both sides, including unmatched users and unmatched orders.

Result idea with the sample data:
- Ana appears with her matching orders.
- Ben and Cara appear with `NULL` order columns.
- Order `103` appears with `NULL` user columns.

Database note:
PostgreSQL and SQL Server support `FULL OUTER JOIN`. MySQL does not support it directly; it is commonly simulated with `LEFT JOIN`, `RIGHT JOIN`, and `UNION`.

MySQL-style simulation:

```sql
SELECT *
FROM Users u
LEFT JOIN Orders o ON u.id = o.user_id

UNION

SELECT *
FROM Users u
RIGHT JOIN Orders o ON u.id = o.user_id;
```

### 6. CROSS JOIN

Subtitle: Every Combination

Produces the Cartesian product of two tables. Every row from the first table is paired with every row from the second table.

Diagram concept:
- Left table: `3 Users`
- Right table: `4 Products`
- Result: `12 Rows`

SQL example:

```sql
SELECT *
FROM Users
CROSS JOIN Products;
```

Use when:
You intentionally need every possible combination, such as users by products, dates by employees, or sizes by colors.

Warning:
Result size grows quickly. If one table has 1,000 rows and the other has 1,000 rows, the result has 1,000,000 rows.

### 7. SELF JOIN

Subtitle: A Table Joins Itself

Useful for hierarchical data such as managers, employees, categories, and organizational structures.

SQL example:

```sql
SELECT
  e.name,
  m.name AS manager
FROM Employees e
LEFT JOIN Employees m ON e.manager_id = m.id;
```

Use when:
Rows in a table relate to other rows in the same table.

### 8. Anti Join

Subtitle: Find Missing Matches

An anti join returns rows from one table that do not have a match in another table. SQL does not usually have a literal `ANTI JOIN` keyword, so this is commonly written with `LEFT JOIN ... WHERE right_table.id IS NULL` or `NOT EXISTS`.

Example with `LEFT JOIN`:

```sql
SELECT u.id, u.name
FROM Users u
LEFT JOIN Orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

Example with `NOT EXISTS`:

```sql
SELECT u.id, u.name
FROM Users u
WHERE NOT EXISTS (
  SELECT 1
  FROM Orders o
  WHERE o.user_id = u.id
);
```

Use when:
You need records that are missing a relationship, such as users with no orders, products never sold, or employees without assigned equipment.

### 9. Semi Join

Subtitle: Find Rows That Have a Match

A semi join returns rows from one table when at least one match exists in another table, without duplicating the left-side row for every match. SQL does not usually require a `SEMI JOIN` keyword; use `EXISTS`.

Example:

```sql
SELECT u.id, u.name
FROM Users u
WHERE EXISTS (
  SELECT 1
  FROM Orders o
  WHERE o.user_id = u.id
);
```

Use when:
You only need to know whether a match exists, not return columns from the joined table.

Why it matters:
An `INNER JOIN` can duplicate users when they have multiple orders. `EXISTS` keeps each user row once.

### 10. Non-Equi Join

Subtitle: Join With More Than Equals

Most examples use equality conditions, but joins can also use ranges or other comparisons.

Example:

```sql
SELECT
  o.id,
  o.total,
  d.discount_rate
FROM Orders o
JOIN DiscountBands d
  ON o.total BETWEEN d.min_total AND d.max_total;
```

Use when:
You need to match rows by range, date windows, pricing tiers, geographic bounds, or other non-exact conditions.

### 11. Joining Multiple Tables

Subtitle: Build Results Step by Step

Real queries often join more than two tables. Each join should have a clear reason and a clear predicate.

Example:

```sql
SELECT
  u.name,
  o.id AS order_id,
  p.name AS product_name
FROM Users u
JOIN Orders o ON u.id = o.user_id
JOIN OrderItems oi ON o.id = oi.order_id
JOIN Products p ON oi.product_id = p.id;
```

Use when:
The final answer needs related data across a chain of tables.

Planning reminder:
Sketch the relationship path before writing the query: `Users -> Orders -> OrderItems -> Products`.

### 12. Filtering JOINs

Subtitle: `ON` vs `WHERE`

For `INNER JOIN`, putting a condition in `ON` or `WHERE` often produces the same final rows. For outer joins, the placement can change the result.

Keeps all users, only matching paid orders:

```sql
SELECT *
FROM Users u
LEFT JOIN Orders o
  ON u.id = o.user_id
  AND o.status = 'paid';
```

Accidentally removes users with no paid orders:

```sql
SELECT *
FROM Users u
LEFT JOIN Orders o ON u.id = o.user_id
WHERE o.status = 'paid';
```

Key idea:
Conditions in `WHERE` run after the join result is formed. A `WHERE` condition on the right table can turn a `LEFT JOIN` into behavior closer to an `INNER JOIN`.

### 13. Many-to-Many Joins

Subtitle: Use a Bridge Table

Many-to-many relationships need a third table that stores the relationship between two entities.

Example tables:
- `Students`
- `Classes`
- `Enrollments`

Relationship path:
`Students -> Enrollments -> Classes`

Example:

```sql
SELECT
  s.name AS student_name,
  c.name AS class_name
FROM Students s
JOIN Enrollments e ON s.id = e.student_id
JOIN Classes c ON e.class_id = c.id;
```

Use when:
Both sides can have many related rows. A student can enroll in many classes, and a class can have many students.

Key idea:
Do not store comma-separated IDs in one column. Use a bridge table so the database can join, index, validate, and query the relationship cleanly.

### 14. `ON`, `USING`, and `NATURAL JOIN`

Subtitle: Be Explicit

`ON` is the clearest and most flexible way to write join conditions.

```sql
SELECT *
FROM Users u
JOIN Orders o ON u.id = o.user_id;
```

`USING` can be shorter when both tables have the same join column name.

```sql
SELECT *
FROM Orders
JOIN Payments USING (order_id);
```

`NATURAL JOIN` automatically joins columns with the same names.

Recommendation:
Prefer `ON` for teaching and production examples. Use `USING` only when it improves clarity. Avoid `NATURAL JOIN` because schema changes can silently change query behavior.

### 15. JOIN vs UNION

Subtitle: Columns vs Rows

JOINs combine columns from related rows.

```sql
SELECT u.name, o.total
FROM Users u
JOIN Orders o ON u.id = o.user_id;
```

UNION stacks rows from compatible result sets.

```sql
SELECT email FROM Customers
UNION
SELECT email FROM Leads;
```

Key idea:
Use a JOIN when data belongs side by side in the same row. Use `UNION` when separate queries produce the same kind of rows.

### 16. Aggregating After JOINs

Subtitle: Count Carefully

Joins often change row counts. Aggregations should account for one-to-many relationships.

Example:

```sql
SELECT
  u.id,
  u.name,
  COUNT(o.id) AS order_count,
  SUM(o.total) AS lifetime_value
FROM Users u
LEFT JOIN Orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

Use when:
You need totals, counts, averages, or summaries after combining related data.

Common mistake:
Counting rows after joining multiple one-to-many tables can inflate totals. Aggregate each relationship separately when needed.

### 17. Which JOIN Should You Use?

Subtitle: Quick Reference

- `INNER JOIN`: matching rows only
- `LEFT JOIN`: all left rows
- `RIGHT JOIN`: all right rows
- `FULL OUTER JOIN`: everything from both tables
- `CROSS JOIN`: every combination
- `SELF JOIN`: same table joined to itself
- Many-to-many join: two joins through a bridge table
- Anti join pattern: rows without a match
- Semi join pattern: rows where a match exists, without duplicates from the matched table
- Non-equi join: range or comparison-based matching

Decision guide:
- Need only matching records? Use `INNER JOIN`.
- Need all records from the primary table? Use `LEFT JOIN`.
- Need every record from both tables? Use `FULL OUTER JOIN`.
- Need every possible pairing? Use `CROSS JOIN`.
- Need parent-child relationships in one table? Use `SELF JOIN`.
- Need two entities that both relate to many rows? Use a bridge table.
- Need rows with no match? Use a `LEFT JOIN ... IS NULL` anti join or `NOT EXISTS`.
- Need rows that have a match but do not need matched table columns? Use `EXISTS`.
- Need to match ranges? Use a non-equi join.

### 18. SQL JOIN Best Practices

Subtitle: Write Better Queries

- Join using indexed keys when possible.
- Select only the columns you need.
- Avoid `SELECT *` in production queries.
- Use clear table aliases.
- Understand the query execution plan for expensive joins.
- Filter early when it reduces the dataset before joining.
- Confirm whether unmatched rows should be included before choosing the JOIN type.
- Know the relationship cardinality: one-to-one, one-to-many, or many-to-many.
- Expect duplicate-looking rows when one left row matches multiple right rows.
- Use `EXISTS` when checking for existence instead of joining only to filter.
- Be careful with `NULL` values in join keys because `NULL = NULL` is not true in normal SQL comparisons.
- Avoid `NATURAL JOIN` in production examples because it joins by same-named columns implicitly and can break when schemas change.
- Use composite join conditions when a relationship depends on more than one column.
- Check row counts before and after each join while debugging.
- Add indexes on foreign keys and heavily used join/filter columns.

### 19. Common Mistakes

- Missing the `ON` condition and accidentally creating a Cartesian product.
- Joining on the wrong column because names look similar.
- Using `INNER JOIN` when unmatched rows should still be reported.
- Putting right-table filters in `WHERE` after a `LEFT JOIN` and unintentionally removing unmatched rows.
- Assuming `JOIN` removes duplicates. It does not; it combines matching rows.
- Joining many-to-many tables without understanding the bridge table.
- Using `SELECT *` and creating unclear duplicate column names like `id`, `created_at`, or `status`.
- Aggregating after joins without checking whether the join multiplied rows.
- Confusing `JOIN` with `UNION`.

### 20. Visual Concepts to Include

- Venn-style diagrams for `INNER`, `LEFT`, `RIGHT`, and `FULL OUTER`.
- Grid multiplication diagram for `CROSS JOIN`.
- Organization chart for `SELF JOIN`.
- Before-and-after tables for `INNER JOIN` and `LEFT JOIN`.
- Small row-count callouts showing why joins can increase result size.
- Bridge-table diagram for many-to-many joins.

### 21. Database Compatibility Notes

- `INNER JOIN`, `LEFT JOIN`, and `CROSS JOIN` are broadly supported.
- `RIGHT JOIN` is supported by many databases, but some teams avoid it for readability.
- `FULL OUTER JOIN` is not available in MySQL as a direct keyword.
- SQLite supports `RIGHT JOIN` and `FULL OUTER JOIN` in modern versions, but older versions did not.
- Syntax details can vary around quoted identifiers, date functions, execution plans, and optimizer hints.

## Open Questions

- Should the examples use generic table names like `Users` and `Orders`, or a more realistic schema?
- Should the final content be written as a carousel, long-form article, or tutorial script?
- Should the topic include visual Venn-style diagrams, table result examples, or both?
- Should database-specific differences be a short footnote or a dedicated section?
- Should we include performance details for indexes and execution plans, or keep this beginner-focused?
- Should the examples use `SELECT *` for visual simplicity, or explicit columns for best-practice consistency?

## Next Draft Ideas

- Include one practical business question per JOIN.
- Turn the sample data into actual result tables for `INNER JOIN`, `LEFT JOIN`, `FULL OUTER JOIN`, anti join, and semi join.
- Add a short performance sidebar about indexes and query plans.
- Create a compact cheat sheet from the decision guide.
- Add a quiz section with "Which JOIN would you use?" scenarios.
