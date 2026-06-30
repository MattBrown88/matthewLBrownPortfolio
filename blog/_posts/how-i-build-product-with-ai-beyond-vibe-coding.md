---
title: 'How I Build Products with AI: Think First, Code Second'
description: 'Step by step AI-assisted MVP development process'
date: 'Jun 30, 2026'
category: AI-assisted development
summary: "Step by step AI-assisted MVP development process."
image: 'blog/images/ai-assisted-dev.png'
image_alt: 'How I Build Products with AI: Think First, Code Second'
cta: 'Work with me on AI-assisted development'

---


AI doesn't eliminate product development. It compresses it. Vibe-coding is the rage these days. But effective product development starts way before the prompt.

The biggest gains don't come from asking AI to build an app from scratch. They come from using AI to critique your thinking at every stage of product development.

1. **Define requirements:** Problem, Customer / User, Workflow, Non-functional Requirements, Technical Requirements, Rules, Edge cases, Success Criteria
2. **Build data model:** Tables, Relationships, Enums, Constraints, Permissions
3. **UI/UX design**
4. **Initial MVP build**

At each step, I get as far as I can alone before sharing with AI to critique the requirements, identify blind spots and refine the design

I don't use AI to build a product from scratch. I use it to improve my thought process and accelerate the entire product development process, not just write code faster. By the time I ask AI to write code, I've already constrained the problem. The requirements are clear, the data model exists, and the workflows are defined. AI performs dramatically better when given this context.

## Product Development Process Overview

### 1. Define requirements

Start with 1 or 2 key features to keep initial scope small. Describe the problem you're solving and the customer who is experiencing it, the workflows that solve it, the rules that must be true, any edge cases that could break the workflows, and the success criteria to validate the feature is working correctly.

The goal is to create clarity around what you're building. Use AI to identify ambiguity, assumptions, and unnecessary scope.

- What requirements are ambiguous?
- What assumptions am I making?
- What edge cases could i be missing?
- Does any of this introduce unnecessary scope? 
- Can I shrink this down even further?

### 2. Build the data model

Once the requirements are clear, build the data model. Define the tables, relationships, enums, constraints, and permissions that make up the system.

This step forces you to think through how the product works and create the context that allows AI to generate better solutions.

Use AI to critique the model:

- Which tables / fields are missing?
- What constraints should exist?
- What edge cases will break this design?
- Where could this model become difficult to evolve?

### 3. UI / UX Design

Before writing code, define what the user actually needs to see and do.

This does not need to be a polished design system or a full Figma file. For an MVP, I usually start by defining the core screens, the primary user actions, and the state each screen needs to handle.

For each screen, describe:

- What is the user trying to accomplish?
- What information do they need to see?
- What actions can they take?
- What happens after each action?
- What empty, loading, error, and success states are needed?
- What can be removed to keep the workflow simpler?

This is another place where AI is useful, but only after you have a rough direction. I’ll sketch the workflow first, then ask AI to critique the user experience.

Questions I ask:

- Is the primary action obvious?
- Are there too many steps?
- What would confuse a first-time user?
- What states am I forgetting?
- Can this screen be simplified?

The goal is not to design a beautiful app upfront. The goal is to make the workflow clear enough that the first version is usable, testable, and easy to build.

### 4. Build Initial MVP

Only now do we start writing code. I would say the fun part, but the nerd in me really likes building data models.

We'll keep this simple. Implement the simplest end-to-end workflow that delivers value. I never ask AI to build an entire application. I ask it to implement one feature, critique one design decision, or review one file at a time.

## Conclusion

That's my development process.

AI isn't replacing product development. It's accelerating it. The better I define the requirements, model the data, and think through the workflows, the better AI performs.

By the time I ask AI to write code, most of the hard thinking is already done.

In the next article, I'll walk through a real example and show how this process turns a seemingly simple idea into requirements, a data model, UI designs, and an implementation plan.

