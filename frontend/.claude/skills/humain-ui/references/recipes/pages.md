# App Shell and Pages Recipe

**Use:** AppShell, AppShellCard, AppSidebar, SidebarProvider
**Optional:** Switch theme variants, SidebarTrigger, PageHeader

```tsx
import {
  AppShell,
  AppShellCard,
  AppSidebar,
  SidebarProvider,
} from '@humain/ui'
import { Home, Calendar, FileText, MessageCircle } from 'lucide-react'

function AppLayout() {
  return (
    <AppShell.Root gap={12}>
      <AppShell.Sidebar>
        <SidebarProvider connected>
          <AppSidebar logoSubtext="Dashboard">
            <AppSidebar.Nav>
              <AppSidebar.NavItem icon={<Home />} label="Dashboard" isActive />
              <AppSidebar.NavItem icon={<Calendar />} label="Calendar" />
              <AppSidebar.NavItem icon={<FileText />} label="Files" />
              <AppSidebar.NavItem icon={<MessageCircle />} label="Chat" />
            </AppSidebar.Nav>
            <AppSidebar.Account
              name="Tareq Amin"
              subtitle="tareq@humain.ai"
              isOnline
              onExpand={() => console.log('Expand account')}
            />
          </AppSidebar>
        </SidebarProvider>
      </AppShell.Sidebar>
      <AppShell.Panel flex={1} label="Dashboard">
        <AppShellCard bodyPadding="md">
          <AppShellCard.Header>
            <AppShellCard.Title>Dashboard</AppShellCard.Title>
            <AppShellCard.Subtitle>Welcome back!</AppShellCard.Subtitle>
          </AppShellCard.Header>
          <div className="space-y-2">
            <h2 className="text-xl font-semibold">Main Content</h2>
            <p className="text-secondary-foreground">Your page content goes here.</p>
          </div>
        </AppShellCard>
      </AppShell.Panel>
    </AppShell.Root>
  )
}
```

**Key props:**
- `AppShell.Root`: background (default: var(--app-background)), height, padding, mobilePadding, gap, connected, activePanel, onActivePanelChange, resizablePanels (default: true for eligible two-panel desktop layouts), defaultPanelSizes, panelSizes, onPanelSizesChange, expandedPanel, defaultExpandedPanel, onExpandedPanelChange, expandThreshold
- `AppShell.Panel`: width (fixed px), flex (flex-grow), minWidth, expanded, label (mobile tab), onExpandedChange
- `AppShellCard`: Card wrapper for panels. Sub-components: Header, Title, Subtitle, Actions, Menu. Fills panels by default, supports inset, and auto expand/collapse via PanelExpansionContext.
- `AppSidebar`: logoSubtext, side (left|right), collapsible (offcanvas|icon|none), rounded, sidebarBgColor
- `AppSidebar.NavItem`: icon, label, isActive, badge, href, onClick, children (NavSub items)
- `AppSidebar.ChatItem`: title, time, isSelected, onClick
- `AppSidebar.Account`: name, subtitle, avatarSrc, isOnline, onExpand
- `PageHeader`: variant (simple|avatar|banner-*), title, supportingText, breadcrumbs, actions, showDivider
- `SidebarProvider`: connected, contentBgColor

**Default background:** App/product pages should omit the `background` prop. `AppShell.Root` already applies `var(--app-background)` / `bg-app` in light and dark mode; use `bg-background` only for a deliberately flat solid surface.

## Data/content app pages

Data/content app pages with long-form platform, product, documentation, knowledge, or article content use one `AppShellCard` document shell. Put the app title and supporting context in `AppShellCard.Header`, then put the main content and Quick Link rail inside the same `AppShellCard` body. Use an internal responsive grid: main content on the left, Quick Link on the right with a desktop divider, stacked on mobile. Do not split Quick Link into a separate top-level card or bare sidebar (`DATA_APP_QUICKLINK_001`).

```tsx
<AppShell.Panel flex={1} label="Data">
  <AppShellCard bodyPadding="none">
    <AppShellCard.Header>
      <AppShellCard.Title>HUMAIN Nexus</AppShellCard.Title>
      <AppShellCard.Subtitle>Built internally. Secured by design. AI-native from the ground up.</AppShellCard.Subtitle>
    </AppShellCard.Header>
    <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_220px]">
      <main className="space-y-6 px-6 py-5">
        <p className="text-secondary-foreground">
          HUMAIN Nexus is an enterprise-grade, end-to-end data platform.
        </p>
        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Built for the AI Era</h2>
          <p className="text-secondary-foreground">
            Use structured content, article cards, logo rows, and product data inside the main column.
          </p>
        </section>
      </main>
      <aside className="border-t border-border-subtle px-6 py-5 lg:border-l lg:border-t-0 lg:px-4">
        <p className="text-sm font-medium">Quick Link</p>
        <nav className="mt-3 flex flex-col gap-3 text-sm text-secondary-foreground">
          <a href="#overview">Overview</a>
          <a href="#security">Link</a>
          <a href="#cloud">Link</a>
        </nav>
      </aside>
    </div>
  </AppShellCard>
</AppShell.Panel>
```

## Authentication Pages

Use `AuthPageLayout` for custom auth flows and the page recipes when the standard flow matches your product route. All auth pages accept `title`, `description`, `logo`, `aside`, `showAside`, `showAsideOnMobile`, `backgroundPattern`, `formMaxWidthClassName`, field prop bags, action objects, loading state, and `onSubmit` where relevant.
Recipe fields include native `name` attributes, and required route fields include native `required` validation by default, so pass field prop bags only to override labels, placeholders, or validation.
Auth pages use a plain background by default; pass `backgroundPattern` only when a decorative page pattern is desired. Configured aside objects render the standard notched aside card with HUMAIN badge, bottom-right avatar cluster, and configurable avatar overflow. Use `showAsideOnMobile` only when the aside context should stack on small screens.

```tsx
import {
  AuthPageLayout,
  LoginPage,
  RegisterPage,
  ForgotPasswordPage,
  ResetPasswordPage,
  TwoFactorAuthenticationPage,
  VerifyEmailPage,
} from '@humain/ui'

<LoginPage
  onSubmit={handleLogin}
  forgotPasswordAction={{ label: 'Forgot password?', href: '/forgot-password' }}
  registerAction={{ label: 'Create account', href: '/register' }}
/>

<RegisterPage
  onSubmit={handleRegister}
  termsProps={{ checked: acceptedTerms, onCheckedChange: setAcceptedTerms }}
  loginAction={{ label: 'Log in', href: '/login' }}
/>

<ForgotPasswordPage onSubmit={handleForgotPassword} />
<ResetPasswordPage onSubmit={handleResetPassword} />
<TwoFactorAuthenticationPage otpProps={{ value: code, onChange: setCode }} />
<VerifyEmailPage email="name@company.com" resendAction={{ label: 'Resend', onClick: resend }} />
```

`VerifyEmail` is a compatibility alias for `VerifyEmailPage`.

For a custom flow, keep the shared shell and provide your own form body:

```tsx
<AuthPageLayout
  title="Confirm workspace access"
  description="Use your enterprise credentials to continue."
  showAsideOnMobile
  aside={{
    title: 'Secure access for enterprise teams',
    cardTitle: 'Protected session',
    cardDescription: 'Use this panel for trust, security, or onboarding context.',
    avatarOverflowCount: 12,
  }}
>
  {/* Your form composed from Input, Button, Checkbox, InputOTP, etc. */}
</AuthPageLayout>
```

**Auth page components:** `LoginPage`, `RegisterPage`, `ForgotPasswordPage`, `ResetPasswordPage`, `TwoFactorAuthenticationPage`, `VerifyEmailPage` (`VerifyEmail` alias).
