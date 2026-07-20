---
title: 'How to Audit a Vibe-Coded App Before Production'
description: 'A practical checklist used to review apps for security, RLS, secrets, deployments, and reliability issues.'
date: 'Jul 6, 2026'
featured: true
category: Supabase
tags: [Supabase, React, Vercel]
summary: 'A practical checklist used to review apps for security, RLS, secrets, deployments, and reliability issues.'
image: 'img/blog/production-readiness-checklist-cover.png'
image_alt: 'How to Audit a Vibe-Coded App Before Production'

---

## Overview

I put together a checklist of items to review before going live with an app. These are relevant to any application but were generally written to check vibe-coded apps that weren't as rigorously validated. This list focuses on my favorite stack, Supabase, React and Vercel but most of the steps are relevant to any stack.

## Security / data boundaries

### Review Supabase Security findings

Supabase highlights security and configuration issues. You should review each one. You don't necessarily have to fix each issue (some may not be relevant to your app) but at least write a note on why you don't need to fix.

Supabase Security Advisor is a good starting point, but it is not a complete security audit. It can flag common configuration issues, but it cannot determine whether your access rules match your app's business logic.

### Evaluate RLS to ensure that it’s not too broad

One of Supabase’s biggest strengths is that RLS can make direct client-to-database access safe, but only if the policies match the app’s actual business rules. Supabase can flag some RLS issues, but it cannot tell whether a user should have access to a specific row, team, workspace, or organization.

If RLS is enabled and no policy exists, the database request would fail. The real risk is a policy that was created to just make the app work.

A policy like this would make the app work, but would open up that table to all authenticated users.

```
create policy "Authenticated users can do anything" 
on todos 
for all 
to authenticated using (true) with check (true); 
```

As a rule of thumb, users should have access to their data and data from teams they belong to.

### Prefer the newer sb_publishable_... and sb_secret_... API keys

![Supabase API keys](/img/blog/supabase-creds.png)



Use the `sb_publishable_...` key in the browser. Use `sb_secret_...` in trusted backend code only.

`sb_secret_...` keys bypass RLS through the `service_role` role. Supabase adds browser protection for these keys: requests made from a browser return `401 Unauthorized` based on the `User-Agent` header. However, that does not make a leaked key safe. A leaked secret key could still be used outside the browser. 

If the backend uses a secret key, that route needs to do the security checks that RLS would normally handle. It needs to authenticate the user and verify that they are allowed to read or modify the data. Do not trust user-supplied values like `user_id`, `team_id`, `organization_id`, or `role` without verifying them server-side.

### Review environment variables and secrets

Environment variables should be separated into frontend and backend values. In Next.js, variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. In Vite, variables prefixed with `VITE_` are exposed to the browser. These are not secrets and should only contain values you are comfortable making public.

Search the frontend for `SUPABASE_SERVICE_ROLE_KEY`, `sb_secret_`, private API keys, webhook secrets, and other backend-only values.

Are there any hard-coded creds in the code?

If any keys may have been exposed during development, rotate them. This can also help identify hard-coded values because anything still using the old key should break.

### Review database functions and RPC permissions

Check which functions are exposed through the API. Revoke `EXECUTE` from `anon` / `authenticated` unless the function should be callable by those roles. Review any `SECURITY DEFINER` functions carefully because they may run with elevated permissions.

Also review default privileges so newly created functions are not automatically executable by roles that should not have access.

### Review storage permissions

- Are buckets public or private?
- Should users be able to list files, or only access known paths?
- Are upload, download, update, and delete policies separate?
- Are file paths scoped by user/team?
- Are signed URLs used for private files?
- Are allowed MIME types and max file size configured?

Supabase Storage buckets are private by default; private bucket downloads are subject to RLS or signed URLs. Public buckets bypass access control for retrieving files by URL, though upload/delete/move/copy operations still use access control. 

### CORS / redirect URL review

Review allowed origins, redirect URLs, and callback URLs. Make sure production auth flows cannot redirect to arbitrary or old preview URLs.

## Reliability / deployment readiness

### Verify migrations are reproducible

Run `supabase db reset` locally. The application should still function correctly after the database is rebuilt from migrations and seed data. This helps confirm that your migration history is complete and reproducible.

### Make sure the app builds from a clean clone

Clone the repo into a fresh directory and verify that a new developer could install dependencies, configure environment variables, run migrations, and start the app without relying on hidden local state.

This is one of the best checks for vibe-coded apps. These apps often work only on the original machine because of issues like hard-coded paths, missing environment variables, uncommitted files, local database state, or undocumented setup steps.

### Separate local, preview, and production environments

Local, preview, and production environments should be clearly separated. 

- Local should use local Supabase or a dedicated dev project.
- Preview deployments should not point at production data by accident.
- Production secrets should only exist in the production environment.
- OAuth redirect URLs, email redirect URLs, webhook URLs, and CORS settings should be correct per environment.

These are common places where an app works locally but breaks after deployment.

### Authentication edge cases

Test all authentication paths, including sign up, login, logout, forgot password, password reset, magic links, expired links, duplicate email registration, and redirect behavior after authentication.

Ensure that logged out users cannot access protected pages or APIs after they log out.

### Identify duplicate or unused routes and/or functions

This is an issue especially with AI-built apps. When you're moving fast, it can be easy to recreate functionality multiple times. This can create a nightmare down the line. 

To identify, separately list all of the API routes and functions alphabetically. First identify if any are not used at all. After removing unused routes or functions, look for duplicated functionality and consolidate it. Pay special attention to functions with similar names, old versions, or routes that perform the same mutation in slightly different ways.

### Database fields are the correct type

Review important columns and make sure their types match the data. Numbers should not be stored as text. Dates should use date/timestamp types. Booleans should not be stored as strings like `"true"` or `"false"`. IDs and foreign keys should be consistent across related tables.

Add constraints where possible: `not null`, foreign keys, unique constraints, check constraints, and enum types.

### Data query efficiency

- Are there any places where the app currently loads slowly?
- Are there any places where data volume could grow quickly?
- Are common filters backed by indexes?
- Are large list pages paginated?
- Are queries selecting only needed columns?
- Are expensive queries happening on every page load?

### Payment handling

Ensure that there are routes to receive webhooks for all important payment events such as failed payments, cancellations, refunds and disputes.

The app should not rely only on the frontend success screen to update payment state.

## Operations

### Add observability / error handling

Add structured logging and error tracking for critical paths. Catch expected errors and return useful messages to the user, but avoid swallowing errors silently. Unexpected production errors should be visible somewhere you will actually check.

For early-stage apps, it can also be useful to send yourself an email when a critical error occurs, such as failed payments, failed webhooks, background job failures, or exceptions in important workflows. Make sure these alerts are limited to high-signal events so you do not create noisy notifications that get ignored.

### Enable backups/PITR if production data matters

If production data matters, make sure it is backed up periodically. Also test the restore process so you know how to recover if data is deleted, corrupted, or accidentally changed.

### Add rate and spend limits

Add rate limits to public or expensive actions. This helps protect the app if there are traffic spikes, an attack or a user triggers an expensive action repeatedly. 

Also set spend limits on external APIs and hosting platform. This protects you from financial damage if usage spikes.

### Audit important mutations

Identify the mutations that can change important business state: creating records, updating ownership, changing permissions, submitting payments, deleting data, inviting users, or modifying account settings. Review each one to confirm it validates inputs, checks authorization, writes the correct data, and handles failure cases.

Consider adding an audit log that records who did what for important actions.

### Dependency and package audit

Remove unused or vulnerable dependencies and packages. 

### Admin access

Review admin screens and actions, and confirm that admin checks happen server-side and not just in frontend logic. Hiding a button or route is not sufficient because the API could still be called directly.

## Conclusion

There are many spots where apps can fall down once they get to production. Running through this list will reduce the chance of serious security, reliability, or scalability issues as your user base grows.