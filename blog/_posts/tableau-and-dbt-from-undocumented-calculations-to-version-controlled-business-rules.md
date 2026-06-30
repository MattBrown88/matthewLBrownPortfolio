---
title: 'Tableau and dbt: From Undocumented Calculations to Version-Controlled Business Rules'
description: 'How to move business logic out of Tableau and into dbt so your metrics are consistent, testable, and version-controlled.'
date: 'Jun 2026'
category: Data
image: 'blog/images/tableau-dbt-cover.png'
image_alt: 'Tableau dbt cover'
cta: 'Work with me'

---

Tableau is a great tool.

Your analysts are producing insights daily.

But the system continues to grow.

Numbers are no longer matching.

Analysts are taking days to answer seemingly simple questions.

## Why is this happening?

Often, it is because **data modeling and business logic are defined directly in Tableau**. Tableau is great for visualization but not as good for data modeling. This causes a variety of issues, including:

- **Repeated calculated fields and data joins.** The same logic is defined in multiple places. Difficult to handle transitional periods such as upstream API changes.
- **Slow data queries and workbooks**. Data transformations are generally faster outside of Tableau.
- **Vendor lock-in**. Keeping logic out of the BI platform makes your system more flexible.

![img](https://miro.medium.com/v2/resize:fit:700/1*mndKdidTrRxVpxa8gwylBg.png)

## Migrating Tableau Environment to dbt

The solution is to move data modeling and business logic into dbt and use Tableau as the display layer. Here’s the basic architecture:

### dbt project architecture and example files

1. Raw Data — `sales.csv`
2. Staging — `stg_sales.sql`
3. Business Logic — `sales_dashboard.sql`
4. Metadata & Testing — `_marts_models.yml`
5. Semantic Layer — `sales_dashboard.yml`
6. Visualization Tableau workbook

To do this, we need to untangle the mess that is data modeling in Tableau. But the great news is the visuals shouldn’t actually change. And these infrastructure and architectural improvements provide a series of cascading benefits.

### Benefits

- **Validation of the numbers.** Re-creating the existing logic often uncovers hidden assumptions and bugs in the existing system.
- **One source of truth.** Consistent and reliable metrics across the org.
- **Cheaper compute costs.** Less duplication and better usage of pre-aggregated datasets.
- **Higher quality data for AI applications**. Models are most effective when they have access to well-defined business concepts.

### Steps to migrate to dbt

1. Create a prioritized inventory of Tableau workbooks to move.
2. Create an inventory of data sources used in those Tableau workbooks and ensure they are in the data warehouse.

![img](https://miro.medium.com/v2/resize:fit:700/1*r-zdbcIgroDZmOdJY8Chxw.png)

3. Identify data transformations currently in Tableau and create equivalent dbt logic.

## Example

In this section, we’ll go through an example of how to move basic logic from Tableau into dbt. We will show how to migrate a *join* and a *calculated field*.

> The full project is available on GitHub:
> github.com/MattBrown88/tableau_dbt_demo

### Join

Joining `product `and `customer` reference tables to `sales_data`.

![img](https://miro.medium.com/v2/resize:fit:700/1*TjtPqhDhAnZ6Ol6kciHadw.png)

​                                                                  Create a calculated field in Tableau

### Calculated Field

Here’s a calculated field in Tableau. By defining it in a Tableau workbook, it’s not available in other workbooks or anywhere else in the org. So reuse will result in duplication.

![img](https://miro.medium.com/v2/resize:fit:534/1*xmJMmKzvyTsfHidZVIjicw.png)

We can move this logic to dbt so that it is documented and readily available. This is a simplistic example but if you’re here, you understand that Tableau data modeling can quickly become unmanageable.