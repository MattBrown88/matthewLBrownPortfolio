## Example: Family Information Hub

In this section, I will show an example of the product development process from writing requirements to defining the data model to giving to AI to build.

### Requirements

#### Problem

Older adults sometimes forget everyday information and appointments and have no easy way to retrieve that information without repeatedly asking family members. 

#### Customer / User

Primary user: An older adult who wants simple answers to everyday questions.

Secondary users: Family members who add and maintain trusted information.

#### Workflows

1. A family member creates a shared family hub.
2. Users can add information as free text, such as:
   - Upcoming visits, Birthdays, Wi-Fi password, Trash pickup day, Where important items are kept, Instructions for using the TV
3. Shows a daily summary of relevant information
4. Users can ask questions and the assistant only answers from available info and can cite the source
5. Users can interact with voice or text (future)

#### Non-Functional Requirements

- The interface should be extremely simple and require minimal navigation.
- The primary experience should work well on mobile devices and tablets.
- Text should be large and easy to read.
- Answers should be short and understandable by non-technical users.

### Technical Requirements

- Use Next.js, React and TypeScript for the frontend application.
- Use Supabase for authentication, database, and row-level security.
- Use email/password authentication.
- Use a Supabase Edge Function for AI requests so the OpenAI API key is never exposed to the browser.
- Use OpenAI for question answering and daily summaries.
- Use a small, low-cost model such as `gpt-4.1-mini` for the MVP.
- Store user-provided information in `information_entries`.
- For V1, retrieve all active information entries for the signed-in user instead of using embeddings or semantic search.
- The model must answer only from the retrieved information entries.
- The model must return citations that can be stored in `answer_sources`.
- Store each question, answer, status, and citation record.
- Do not use user-provided information to train the model.
- The application should be designed so retrieval can be replaced with embeddings or semantic search in the future.

#### Rules

- The assistant should only answer from family-approved information.
- Every answer should cite the information it came from.
- If the assistant does not know the answer, it should say so instead of guessing.

#### Edge Cases

- There is conflicting information in the hub.
- Information becomes outdated.
- User asks a vague question.
- User asks something that is not in the hub.

####  Success Criteria

- Family members can add useful information in under two minutes.
- The older adult can ask a natural-language question and receive a simple answer.
- Every answer cites its source.
- Family members can easily keep information up to date.

Now we take these requirements and build a data model from them.

### Data Model

**users**: id, household_id, name, role (older adult | caretaker), email, created_at

**households**: id, name, created_at

**information_entries**: id, household_id, created_by_user_id, content,  created_at, status (active, inactive), updated_at, archived_at

**question_answers**: id, household_id, user_id, question, answer, status (answered | not_found | ambiguous) created_at

**Answer_sources**: id, household_id, question_answer_id, information_entry_id, citation_text, created_at

### Relationships

- A `household` has many `users`
- A `household` has many `information_entries`
- A `household` has many `question_answers`
- A `question_answer` can cite one or more `information_entries` through `answer_sources`

### Constraints

- Users can only access records from their own `household`
- Only `active` `information_entries` can be used to answer questions
- An `answered` question must have at least one source
- `not_found` questions should not have sources
- `answer_sources` must reference entries from the same `household` as the question

### AI Prompt

We now have enough information to write the AI prompt. We want to specify as much as we can in the business logic. Then we can reiterate in the AI prompt while including guardrails in our data model and application logic to ensure that it follows spec.

---------------------

You are a helpful assistant for older adults.

You are given:

- A user's question
- A list of active information entries

Rules:

- Answer only using the provided information entries.
- Do not use outside knowledge or make assumptions.
- Keep answers short, simple, and easy to understand.
- If the information is conflicting, explain that the saved information conflicts and include the conflicting information.
- If the answer is not available in the information entries, respond with: "I don't know that yet."
- Every answered question must reference one or more information entries.

Return JSON in the following format:

```json
{
  "answer": "Granddaughter Emma is visiting on July 12 at 2 PM.",
  "status": "answered",
  "sources": [
    {
      "information_entry_id": "uuid",
      "citation_text": "Granddaughter Emma is visiting on July 12 at 2 PM."
    }
  ]
}
```

------------------

### UI/UX Design

#### Design Principles

- Extremely simple and uncluttered interface
- Large, readable text and high-contrast colors
- Mobile-first design
- Minimal navigation with only two primary screens

#### Screen 1: Home

**Header**

- Greeting and today's date

**Today's Summary**

- Displays relevant information for today, such as appointments, upcoming visits, or reminders

**Ask a Question**

- Large text input with placeholder text such as "Ask me a question..."
- Optional microphone button for future voice support

**Answer Area**

- Displays a short, plain-language answer
- If the information is unavailable, clearly states that the answer is not known

**Navigation**

- Button to manage family information

#### Screen 2: Family Information

**Information List**

- Displays all information entries
- Search and category filtering
- Indicators for inactive or expired information

**Add/Edit Information**

- Simple form with:
  - Title
  - Information text
  - Category
  - Optional start and end dates
- Ability to edit, archive, or deactivate information

**Navigation**

- Button to return to the Home screen

#### Accessibility Considerations

- Large touch targets
- Large default font sizes
- Support for screen readers
- Clear confirmation messages after actions
- Avoid technical terminology and unnecessary options



### Build MVP

We have now written enough context to start building the application. But we still won't reach to AI quite yet. We want to build the app scaffolding manually.

Here are the steps to create the Next.js and Supabase scaffolding. After we build the scaffolding, then we will begin using AI to build the functionality.

#### 1. Create the Next.js app

```bash
npx create-next-app@latest family-information-hub
cd family-information-hub
npm install @supabase/supabase-js
```

#### 2. Initialize Supabase

```
npm install -g supabase
supabase init
```

#### 3. Create Migrations

Add the code below to the respective files

```
supabase migration new enums
supabase migration new tables
supabase migration new rls
```

```
# 001_enums.sql
create type INFORMATION_ENTRY_STATUS as enum (
  'active',
  'inactive'
);

create type QUESTION_ANSWER_STATUS as enum (
  'answered',
  'not_found',
  'ambiguous'
);
```

```
# 002_tables.sql
create table users (
  id uuid primary key references auth.users(id) on delete cascade,
  name text not null,
  email text not null,
  created_at timestamptz not null default now()
);

create table information_entries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  content text not null,
  created_at timestamptz not null default now(),
  status INFORMATION_ENTRY_STATUS not null default 'active',
  updated_at timestamptz not null default now(),
  archived_at timestamptz,

  constraint information_entries_content_not_empty
    check (length(trim(content)) > 0),

  constraint information_entries_archived_if_inactive
    check (status = 'active' or archived_at is not null)
);

create table question_answers (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  question text not null,
  answer text,
  status QUESTION_ANSWER_STATUS not null,
  created_at timestamptz not null default now(),

  constraint question_answers_question_not_empty
    check (length(trim(question)) > 0),

  constraint question_answers_answered_requires_answer
    check (status != 'answered' or answer is not null)
);

create table answer_sources (
  id uuid primary key default gen_random_uuid(),
  question_answer_id uuid not null references question_answers(id) on delete cascade,
  information_entry_id uuid not null references information_entries(id) on delete cascade,
  citation_text text not null,
  created_at timestamptz not null default now(),

  constraint answer_sources_citation_text_not_empty
    check (length(trim(citation_text)) > 0)
);
```

```
# 003_rls.sql
alter table users enable row level security;
alter table information_entries enable row level security;
alter table question_answers enable row level security;
alter table answer_sources enable row level security;

create policy "Users can view their profile"
on users
for select
using (id = auth.uid());

create policy "Users can update their profile"
on users
for update
using (id = auth.uid())
with check (id = auth.uid());

create policy "Users can view their information"
on information_entries
for select
using (user_id = auth.uid());

create policy "Users can insert their information"
on information_entries
for insert
with check (user_id = auth.uid());

create policy "Users can update their information"
on information_entries
for update
using (user_id = auth.uid())
with check (user_id = auth.uid());

create policy "Users can view their question answers"
on question_answers
for select
using (user_id = auth.uid());

create policy "Users can insert their question answers"
on question_answers
for insert
with check (user_id = auth.uid());

create policy "Users can view their answer sources"
on answer_sources
for select
using (
  exists (
    select 1
    from question_answers
    where question_answers.id = answer_sources.question_answer_id
      and question_answers.user_id = auth.uid()
  )
);

create policy "Users can insert their answer sources"
on answer_sources
for insert
with check (
  exists (
    select 1
    from question_answers
    where question_answers.id = answer_sources.question_answer_id
      and question_answers.user_id = auth.uid()
  )
  and exists (
    select 1
    from information_entries
    where information_entries.id = answer_sources.information_entry_id
      and information_entries.user_id = auth.uid()
      and information_entries.status = 'active'
  )
);
```

#### 4. Apply Migrations

```
supabase start
supabase db reset
```

#### 5. Create Edge Functions

```
supabase functions new ask-question
supabase functions new daily-summary
```

#### 6. Specify env vars

Create two environment files:

**Next.js**

```
./.env.local
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_local_anon_key
```

These values are safe to expose to the browser and are used by the Next.js application. Anon key can be pulled by running `supabase status` 

**Supabase Edge Functions**

```
./supabase/.env
OPENAI_API_KEY=your_openai_key
```

This file contains server-side secrets and should never be exposed to the browser.

When developing locally:

```bash
supabase start
supabase functions serve ask-question --env-file ./.env.backend
npm run dev
```



The project scaffolding is now built. Now I like to implement functionality step by step, and ask AI if it has any questions with each step. My goal is a critical review of everything that I build.

