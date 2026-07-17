---
title: 'How to Fix "new row violates row-level security policy" in Supabase'
description: 'Learn why Supabase returns this RLS error and how to fix common insert policy, auth, and user_id issues.'
date: 'Jun 25, 2026'
category: Supabase
summary: "This error means your insert was blocked by Row Level Security. Here's why it happens and how to fix it for good."
image: 'img/blog/rls-supabase-cover.svg'
image_alt: 'Supabase row-level security policy error, fixed'
cta: 'Get your Supabase issue fixed'

---

RLS errors in Supabase can be vague and hard to diagnose. 

```
new row violates row-level security policy for table "<table_name>"
```

What does this even mean??

These messages come directly from PostgreSQL which returns a generic error for all RLS violations to avoid leaking schema or authorization rules to an attacker.

Supabase applications generally communicate directly with PostgreSQL from the frontend, so these generic error messages often bubble all the way up to the UI. In a more traditional backend, an API layer would intercept the database error and return a more user-friendly message. Direct database access is a tradeoff of Supabase's frontend first approach which allows for faster development and less boilerplate code but can make debugging more difficult.

## Most common issues

### Calling `.select()` after `.insert()` requires a SELECT policy

Here is a simple migration script for a `projects` table. It creates the table, turns on RLS then allows the user to create a project associated with their `user_id` 

```
create table projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  user_id uuid not null references auth.users
);

-- Turn on Row Level Security. With RLS enabled and no policy,
-- ALL access is denied by default.
alter table projects enable row level security;

-- Allow a user to insert a project only when the row's user_id
-- matches the currently authenticated user.
create policy "Users can create their own projects"
on projects
for insert
to authenticated
with check ( (select auth.uid()) = user_id );
```

And here's code to create a new project for that user.

```
  const ok = await supabase
    .from('projects')
    .insert({ name: 'My Project', user_id: user.id })
    .select();
```

This code would fail and return the dreaded `new row violates row-level security policy for table "<table_name>"` 

Why? 

Every operation needs to be allowed by an RLS policy: `INSERT`, `SELECT`, `UPDATE`, and `DELETE`. Because you chained `.select()`, PostgreSQL also needs permission to return the newly inserted row. Without the `SELECT` policy, the entire statement fails and the row is not inserted.

Adding this policy would fix it

```
create policy "Users can select their own projects"
on projects
for select
to authenticated
using ( (select auth.uid()) = user_id );
```

Debugging can be tricky if you don't know what to look for in the RLS policies.

Another common cause is inserting a row without the `user_id` required by the policy. 

```
  const fail = await supabase.from('projects').insert({ name: 'My Project' });
```

Notice that the `user_id` associated with the project is missing. The confusing thing is that this would output the same error

```
new row violates row-level security policy for table "<table_name>"
```

You would fix like this. You need to explicitly include the user_id in the statement because the policy compares `auth.uid()` to the `user_id` you provided.

```
const { data: { user } } = await supabase.auth.getUser();

if (!user) {
  throw new Error('User is not logged in');
}

await supabase
  .from('projects')
  .insert({
    name: 'My Project',
    user_id: user.id
  });
```



## Quick checklist

When you see this error, check:

1. Am I calling `.select()` after `.insert()`, `.update()`, or `.upsert()`?
2. Do I have a SELECT policy for the row I’m trying to return?
3. Is the user actually logged in?
4. Does the row’s `user_id` match `auth.uid()`?

The key is to debug the RLS policies and not just the frontend code.

You can view the sample repo with the entire example here

 [GitHub Repo](https://github.com/MattBrown88/supabase-new-row-violates-rls-policy)



Or watch the video walkthrough here

