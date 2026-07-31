# Bootstrap Guide — Humain Foundation UI

Scaffolding, framework setup, starter templates for `@humain/ui`.

---

## Framework Setup

### Vite + React (Recommended)

```bash
# 1. Scaffold
npm create vite@latest my-app -- --template react-ts
cd my-app

# 2. Install library
npm install @humain/ui lucide-react

# 3. Replace index.css import in main.tsx
```

**`src/main.tsx`**

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '@humain/ui/styles.css';
import { ThemeProvider } from '@humain/ui';
import App from './App.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="light">
      <App />
    </ThemeProvider>
  </StrictMode>,
);
```

---

### Next.js App Router

```bash
# 1. Scaffold
npx create-next-app@latest my-app --typescript --tailwind --app
cd my-app

# 2. Install library
npm install @humain/ui lucide-react
```

**`app/globals.css`** — replace entire file:

```css
@import '@humain/ui/styles.css';
```

**`app/layout.tsx`**

```tsx
import type { Metadata } from 'next';
import { ThemeProvider, ThemeScript } from '@humain/ui';
import './globals.css';

export const metadata: Metadata = {
  title: 'My App',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Prevents flash of wrong theme on SSR */}
        <ThemeScript defaultTheme="light" />
      </head>
      <body>
        <ThemeProvider defaultTheme="light">{children}</ThemeProvider>
      </body>
    </html>
  );
}
```

> `suppressHydrationWarning` on `<html>` required — `ThemeScript` adds class before hydration.
> If you customize `defaultTheme` or `storageKey`, pass the same values to `ThemeScript` and `ThemeProvider`.

---

### Remix

```bash
# 1. Scaffold (existing Remix project)
npm install @humain/ui lucide-react
```

**`app/root.tsx`** — add styles import, wrap with providers:

```tsx
import { Links, Meta, Outlet, Scripts, ScrollRestoration } from '@remix-run/react';
import { ThemeProvider, ThemeScript } from '@humain/ui';
import stylesheet from '@humain/ui/styles.css?url';

export const links = () => [{ rel: 'stylesheet', href: stylesheet }];

export default function App() {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <Meta />
        <Links />
        <ThemeScript defaultTheme="light" />
      </head>
      <body>
        <ThemeProvider defaultTheme="light">
          <Outlet />
        </ThemeProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
```

---

## Recommended Project Structure

```
src/
├── app/                      # Routes / pages
│   ├── layout.tsx            # Root layout with ThemeProvider
│   ├── (auth)/               # Auth routes composed from PageBackground + form primitives
│   └── (app)/                # Authenticated app (AppShell + AppSidebar layout)
├── components/               # App-specific components only
├── lib/                      # Utilities, API clients
└── hooks/                    # Custom hooks
```

**Do NOT create `components/ui/`** — primitives come from library. Only add app-specific components.

---

## Starter Templates

### Full App with Sidebar

Uses `AppShell` + `AppSidebar` compound API with `SidebarProvider` wrapping.

```tsx
import {
  AppShell,
  AppShellCard,
  AppSidebar,
  SidebarProvider,
} from '@humain/ui';
import {
  LayoutDashboard,
  Users,
  Settings,
  MessageCircle,
} from 'lucide-react';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppShell.Root gap={12}>
      <AppShell.Sidebar>
        <SidebarProvider connected >
          <AppSidebarNav />
        </SidebarProvider>
      </AppShell.Sidebar>
      <AppShell.Panel flex={1}>
        <AppShellCard bodyPadding="md">
          <AppShellCard.Header>
            <AppShellCard.Title>Dashboard</AppShellCard.Title>
          </AppShellCard.Header>
          <main id="main-content">{children}</main>
        </AppShellCard>
      </AppShell.Panel>
    </AppShell.Root>
  );
}

function AppSidebarNav() {
  return (
    <AppSidebar logo={<span className="font-semibold">My App</span>} collapsible="icon">
      <AppSidebar.Nav>
        <AppSidebar.NavItem
          icon={<LayoutDashboard />}
          label="Dashboard"
          href="/dashboard"
          isActive
        />
        <AppSidebar.NavItem
          icon={<Users />}
          label="Users"
          href="/users"
        />
        <AppSidebar.NavItem
          icon={<MessageCircle />}
          label="Chat"
          href="/chat"
          badge="New"
        />
        <AppSidebar.NavItem
          icon={<Settings />}
          label="Settings"
          href="/settings"
        />
      </AppSidebar.Nav>
      <AppSidebar.Account
        name="Jane Smith"
        subtitle="jane@example.com"
        avatarSrc="/avatars/jane.jpg"
        isOnline
      />
    </AppSidebar>
  );
}
```

---

### Auth Routes

Auth and standalone routes use `bg-app` as the default page canvas; layer `PageBackground` or cards on top, and use `bg-background` only for an intentionally flat solid page.

```tsx
import { Button, Card, Input, PageBackground } from '@humain/ui';
import { useNavigate } from 'react-router-dom'; // or Next.js router

// Login
export function LoginRoute() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen overflow-hidden bg-app">
      <PageBackground pattern="grid" offset="top" />
      <main className="relative z-10 mx-auto flex min-h-screen w-full max-w-md items-center px-4">
        <Card className="w-full">
          <Card.Header>
            <Card.Title>Sign in</Card.Title>
            <Card.Description>Continue to your workspace.</Card.Description>
          </Card.Header>
          <Card.Content>
            <form
              className="grid gap-4"
              onSubmit={(event) => {
                event.preventDefault();
                // call your auth API
              }}
            >
              <Input label="Email" name="email" type="email" autoComplete="email" />
              <Input label="Password" name="password" type="password" autoComplete="current-password" />
              <Button type="submit">Sign in</Button>
              <Button
                type="button"
                appearance="ghost"
                onClick={() => navigate('/forgot-password')}
              >
                Forgot password
              </Button>
            </form>
          </Card.Content>
        </Card>
      </main>
    </div>
  );
}

// Signup
export function SignupRoute() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-app">
      <PageBackground pattern="circular" offset="top" />
      <main className="relative z-10 mx-auto flex min-h-screen w-full max-w-md items-center px-4">
        <Card className="w-full">
          <Card.Header>
            <Card.Title>Create account</Card.Title>
            <Card.Description>Start with your work email.</Card.Description>
          </Card.Header>
          <Card.Content>
            <form className="grid gap-4">
              <Input label="Name" name="name" autoComplete="name" />
              <Input label="Email" name="email" type="email" autoComplete="email" />
              <Input label="Password" name="password" type="password" autoComplete="new-password" />
              <Button type="submit">Create account</Button>
            </form>
          </Card.Content>
        </Card>
      </main>
    </div>
  );
}
```

---

### Dashboard with Metrics

```tsx
import {
  AppShellCard,
  Button,
  DataTable,
  MetricCard,
  type ColumnDef,
} from '@humain/ui';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

const columns: ColumnDef<User, string>[] = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'email', header: 'Email' },
  { accessorKey: 'role', header: 'Role' },
];

const users: User[] = [
  { id: '1', name: 'Jane Smith', email: 'jane@example.com', role: 'Admin' },
  { id: '2', name: 'John Doe', email: 'john@example.com', role: 'Member' },
];

export function DashboardPage() {
  return (
    <div className="flex flex-col gap-4 p-6">
      <AppShellCard bodyPadding="md">
        <AppShellCard.Header>
          <AppShellCard.Title>Dashboard</AppShellCard.Title>
          <AppShellCard.Subtitle>Overview of your workspace</AppShellCard.Subtitle>
        </AppShellCard.Header>
        <AppShellCard.Actions>
          <Button appearance="outline" variant="secondary" size="sm">Export</Button>
          <Button appearance="solid" variant="primary" size="sm">Add user</Button>
        </AppShellCard.Actions>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Total Users"
            value={1284}
            change={12}
            changeSentiment="positive"
            description="vs last month"
          />
          <MetricCard
            title="Active Sessions"
            value={342}
            change={-5}
            changeSentiment="negative"
            description="vs last month"
          />
          <MetricCard
            title="Revenue"
            value={48500}
            change={8}
            changeSentiment="positive"
            description="vs last month"
            valueFormatter={(n) => `$${n.toLocaleString()}`}
          />
          <MetricCard
            title="Conversion Rate"
            value={3.2}
            changeSentiment="neutral"
            description="no change"
            valueFormatter={(n) => `${n}%`}
          />
        </div>
      </AppShellCard>

      <AppShellCard>
        <AppShellCard.Header>
          <AppShellCard.Title>Recent users</AppShellCard.Title>
          <AppShellCard.Subtitle>Users added in the last 30 days</AppShellCard.Subtitle>
        </AppShellCard.Header>
        <DataTable
          columns={columns}
          data={users}
          getRowId={(row) => row.id}
          enableSorting
          enablePagination
          pageSize={10}
        />
      </AppShellCard>
    </div>
  );
}
```

---

### AI Chat Interface

```tsx
import { useState } from 'react';
import {
  AIContainer,
  AIEmptyState,
  AIPromptSuggestion,
  AIMessage,
} from '@humain/ui';
import type { ChatMessage } from '@humain/ui';
import { Sparkles } from 'lucide-react';

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const handleSend = (text: string) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: `You said: ${text}`,
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 800);
  };

  const suggestions = [
    'Summarize this document',
    'Generate a report',
    'Help me write an email',
  ];

  return (
    <div className="h-screen p-4">
      <AIContainer
        messages={messages}
        inputProps={{
          placeholder: 'Ask anything...',
          onSubmit: handleSend,
        }}
        emptyContent={
          <AIEmptyState
            icon={<Sparkles className="size-12" />}
            title="How can I help you?"
            description="Powered by HumainOne"
          >
            <div className="flex flex-wrap gap-2 justify-center">
              {suggestions.map((s) => (
                <AIPromptSuggestion
                  key={s}
                  onClick={() => handleSend(s)}
                  showArrow
                >
                  {s}
                </AIPromptSuggestion>
              ))}
            </div>
          </AIEmptyState>
        }
      />
    </div>
  );
}
```

---

### Form Page with Validation

Smart field props — pass `label` and `error` to `Input`/`Select`/`Checkbox`, auto-wraps in `Field`.

```tsx
import { useState } from 'react';
import {
  Card,
  Input,
  Select,
  Checkbox,
  Button,
} from '@humain/ui';

interface FormValues {
  name: string;
  email: string;
  role: string;
  agreeToTerms: boolean;
}

interface FormErrors {
  name?: string;
  email?: string;
  role?: string;
  agreeToTerms?: string;
}

export function CreateUserPage() {
  const [values, setValues] = useState<FormValues>({
    name: '',
    email: '',
    role: '',
    agreeToTerms: false,
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  const validate = (): FormErrors => {
    const errs: FormErrors = {};
    if (!values.name.trim()) errs.name = 'Name is required';
    if (!values.email.includes('@')) errs.email = 'Valid email required';
    if (!values.role) errs.role = 'Please select a role';
    if (!values.agreeToTerms) errs.agreeToTerms = 'You must accept the terms';
    return errs;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    setLoading(true);
    // call API...
    setLoading(false);
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <Card.Header>
          <Card.Title>Create Account</Card.Title>
          <Card.Description>Fill in the details below to get started.</Card.Description>
        </Card.Header>
        <Card.Content>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {/* Smart field props: label + error auto-creates Field wrapper */}
            <Input
              label="Full Name"
              placeholder="Jane Smith"
              value={values.name}
              onChange={(e) =>
                setValues((v) => ({ ...v, name: e.target.value }))
              }
              error={errors.name}
            />

            <Input
              label="Email"
              type="email"
              placeholder="jane@example.com"
              value={values.email}
              onChange={(e) =>
                setValues((v) => ({ ...v, email: e.target.value }))
              }
              error={errors.email}
            />

            <Select
              label="Role"
              value={values.role}
              onValueChange={(val) =>
                setValues((v) => ({ ...v, role: val }))
              }
              error={errors.role}
              options={[
                { value: 'admin', label: 'Admin' },
                { value: 'member', label: 'Member' },
                { value: 'viewer', label: 'Viewer' },
              ]}
            />

            <Checkbox
              label="I agree to the terms and conditions"
              checked={values.agreeToTerms}
              onCheckedChange={(checked) =>
                setValues((v) => ({ ...v, agreeToTerms: checked === true }))
              }
              error={errors.agreeToTerms}
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Account'}
            </Button>
          </form>
        </Card.Content>
      </Card>
    </div>
  );
}
```

---

## Key Import Patterns

```tsx
// All from the single package entry
import {
  // Templates
  AppShell,
  AppSidebar,
  SidebarProvider,

  // Organisms
  PageHeader,
  MetricCard,
  DataTable,
  AIContainer, AIEmptyState, AIPromptSuggestion, AIMessage,

  // Atoms
  Button, Input, Select, Checkbox,

  // Molecules
  Card,

  // Theme
  ThemeProvider, ThemeScript, useTheme,
} from '@humain/ui';
```

> Icons imported separately from `lucide-react` — library does not re-export them.

```tsx
import { LayoutDashboard, Settings, Sparkles } from 'lucide-react';
```

---

## Common Gotchas

| Issue | Fix |
|-------|-----|
| Flash of wrong theme on SSR | Add `<ThemeScript />` in `<head>` + `suppressHydrationWarning` on `<html>`; keep customized `defaultTheme`/`storageKey` aligned with `ThemeProvider` |
| DataTable wrong row identity | Pass `getRowId={(row) => row.id}` |
| AppSidebar not collapsing | Wrap layout with `<SidebarProvider>` |
| Styles not applying | Import `@humain/ui/styles.css` once at app root |
| Form validation not shown | Pass `error` prop to `Input`/`Select`/`Checkbox` (smart field props) |
| Button appearance vs variant | `variant` = color intent (`primary`/`secondary`/`info`/`success`/`warning`/`destructive`); `appearance` = style (`solid`/`outline`/`ghost`/`link`/`soft`/`gradient`/`ai`) |
