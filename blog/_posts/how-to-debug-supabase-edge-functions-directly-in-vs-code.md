---
title: 'How to Debug Supabase Edge Functions in VS Code'
description: 'Step-by-step walkthrough of setting up debugging in VS Code for Supabase'
date: 'Jun 25, 2026'
category: Supabase
summary: "Set breakpoints in Supabase Edge Functions and your Vite frontend straight from VS Code — no console.log required. Here's the five-minute setup."
image: 'img/blog/debug-edge-functions-cover.svg'
image_alt: 'How to Debug Supabase Edge Functions in VS Code'
cta: 'Get your Supabase issue fixed'

---


Console logging works for quick troubleshooting, but breakpoints make it so much easier to understand what’s happening inside a request.

This article will show you how to debug both Supabase Edge Functions and a Vite frontend directly from VS Code using breakpoints. No log statements or jumping between debuggers. And it all works directly from VS Code.

We will keep things simple in this article and just show the pieces that you need to add to an existing project to get debugging set up in five minutes.

> *Looking for a complete walkthrough from scratch? Watch the accompanying* [YouTube video](https://youtu.be/lPFVhmd5LAM). 
>
> Just want the code? Here's the [GitHub repo](https://github.com/MattBrown88/supabase-debug-vscode.git)

## Create launch.json debug configuration

In VS Code, `launch.json` is used to specify debug configurations. Adding these configurations to the `launch.json` is the only code change required to enable debugging. This config file has two debugger profiles:

```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Vite Frontend",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:8080",
      "webRoot": "${workspaceFolder}/src"
    },
    {
      "name": "Debug Edge Functions",
      "type": "node",
      "request": "attach",
      "address": "127.0.0.1",
      "port": 8083,
      "sourceMaps": true,
      "enableContentValidation": false,
      "restart": true,
      "timeout": 1000000,
      "sourceMapPathOverrides": {
        "file:///var/tmp/sb-compile-edge-runtime/*": "${workspaceFolder}/supabase/functions/*"
      }
    }
  ]
}
```

The Edge Function debugger attaches to port `8083`, which is the default Supabase inspector port.

The most important setting is `sourceMapPathOverrides`.

This tells VS Code how to map the compiled Edge Function code back to your original TypeScript source files. This is the only setting you typically need to update.

### Find the compiled Edge Function path

1. Start the Edge Function runtime in debug mode:

   ````
   supabase functions serve --inspect-mode brk
   ````

2. Navigate to `chrome://inspect` in Chrome

3. Trigger an Edge Function request

4. Highlighted below is the compiled script path shown on `chrome://inspect`  

   

![Chrome Inspect showing the compiled Edge Function path](/img/blog/chrome-inspect.png)



Supabase officially documents debugging through Chrome DevTools. We can use the same inspector information to configure VS Code debugging. Update sourceMapPathOverrides `file:///var/tmp/sb-compile-edge-runtime/*` to match what's shown in Chrome. 

If Chrome shows:

````
file:///var/tmp/sb-compile-edge-runtime/greet/index.ts
````

Then the left side of your mapping should be:

`````
file:///var/tmp/sb-compile-edge-runtime/*
`````

Remove the function-specific portion of the path (`greet/index.ts`) and keep only the common root directory.

> The compiled path may differ between operating systems and Supabase CLI versions. If breakpoints are not being hit, check the path shown in `chrome://inspect` and update `sourceMapPathOverrides` accordingly.



## Debugging

You can debug both the frontend and Edge Functions at the same time.

This provides a much smoother debugging workflow than relying solely on console logs.

### Frontend

1. Start the **Debug Vite Frontend** configuration.
2. Set a breakpoint somewhere in your frontend code.
3. Trigger the code path from the browser.
4. If VS Code stops at the breakpoint, frontend debugging is working.

### Edge Functions

1. Start the Edge Function runtime:

   `````
   supabase functions serve --inspect-mode brk
   `````

2. In VS Code, start the "Debug Edge Functions" configuration. The Debug toolbar should appear.

3. Set a breakpoint in 

````
supabase/functions/<function-name>/index.ts
````

4. Trigger the function from your frontend or browser.

The debugger will stop on the Edge Runtime bootstrap code first because of `--inspect-mode brk`.

Press **Continue** once and execution will proceed to your breakpoint.

To debug a different Edge function, you will need to restart the function server.

## Troubleshooting

### Breakpoint is hollow or never gets hit

Your `sourceMapPathOverrides` path is likely incorrect.

Verify the compiled path in `chrome://inspect` and update the mapping.

### Debugger attaches but execution never stops

Make sure:

```bash
supabase functions serve --inspect-mode brk
```

is running before attaching the VS Code debugger.

### Debugger stops in bootstrap code

This is expected behavior when using:

```bash
--inspect-mode brk
```

Press **Continue** and execution will continue to your breakpoint.

### Debugging a different Edge Function

You will need to restart:

```
supabase functions serve --inspect-mode brk
```

when switching to a different Edge Function.

Once configured, you only need to:

1. Start `supabase functions serve --inspect-mode brk`
2. Press F5 in VS Code
3. Set breakpoints


After that, debugging works much like any Node.js backend project.

## Conclusion

Once configured, debugging Supabase Edge Functions feels much more like debugging a traditional backend application.

You can inspect variables, step through code, and trace requests across both your frontend and Edge Functions without filling your codebase with temporary `console.log` statements.



