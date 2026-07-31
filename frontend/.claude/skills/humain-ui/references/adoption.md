# Adoption Guide

Migrate an existing project to `@humain/ui`. Work through each section in order: scan first, then migrate bottom-up.

---

## 1. Scan Protocol

Run these steps before touching any code. Report findings to the user before proceeding.

### Step 1 — Dependencies

Identify the current UI library and version:

```bash
# Check package.json for known libraries
grep -E '"(@mui|@chakra-ui|@radix-ui|shadcn|antd|mantine|react-bootstrap|styled-components|@emotion|tailwindcss)' package.json

# Check installed versions
npm ls @mui/material @chakra-ui/react tailwindcss 2>/dev/null
```

Record: library name, version, peer dependencies (emotion, styled-system, etc.).

### Step 2 — CSS Approach

Determine how styles are applied:

```bash
# CSS-in-JS (emotion/styled-components)
grep -r "styled\." src/ --include="*.tsx" -l | head -5
grep -r "css\`" src/ --include="*.tsx" -l | head -5

# CSS Modules
find src/ -name "*.module.css" | head -10

# Tailwind
grep -r "className=\"" src/ --include="*.tsx" -l | head -5
cat tailwind.config.* 2>/dev/null

# Global CSS / BEM
find src/ -name "*.css" -not -name "*.module.css" | head -10
```

Record: CSS-in-JS, modules, Tailwind, global CSS, or mixed.

### Step 3 — Component Inventory

Count usage of library components:

```bash
# MUI example
grep -r "from '@mui/material'" src/ --include="*.tsx" -h | \
  grep -oP "(?<=import \{)[^}]+" | tr ',' '\n' | tr -d ' ' | sort | uniq -c | sort -rn

# Chakra example
grep -r "from '@chakra-ui/react'" src/ --include="*.tsx" -h | \
  grep -oP "(?<=import \{)[^}]+" | tr ',' '\n' | tr -d ' ' | sort | uniq -c | sort -rn

# Count total component files
find src/ -name "*.tsx" | wc -l
```

Record: top 10 most-used components, total file count.

### Step 4 — Color Usage

Find hardcoded colors that need token migration:

```bash
# Hex colors in JSX/TSX
grep -rn "#[0-9a-fA-F]\{3,6\}" src/ --include="*.tsx" | grep -v "\/" | head -20

# Named colors in Tailwind classes
grep -rn "text-gray-\|bg-gray-\|border-gray-\|text-red-\|bg-red-\|text-green-\|bg-green-\|text-blue-\|bg-blue-" \
  src/ --include="*.tsx" | head -20

# CSS custom properties
grep -rn "var(--" src/ --include="*.css" | head -20
```

Record: hardcoded hex count, Tailwind color utilities used, custom CSS variables.

### Step 5 — Layout Patterns

Identify layout primitives in use:

```bash
# MUI Box/Stack/Grid
grep -rn "<Box\|<Stack\|<Grid " src/ --include="*.tsx" | wc -l

# Chakra Flex/Box/Grid
grep -rn "<Flex\|<Box\|<VStack\|<HStack" src/ --include="*.tsx" | wc -l

# Custom layout components
grep -rn "<Layout\|<Page\|<Sidebar\|<AppBar\|<Navbar" src/ --include="*.tsx" | wc -l
```

Record: layout component count per type.

### Step 6 — Theme & Dark Mode

Check current theme/dark mode implementation:

```bash
# Theme provider usage
grep -rn "ThemeProvider\|createTheme\|useTheme\|ColorModeProvider\|useColorMode" \
  src/ --include="*.tsx" | head -20

# Manual dark mode
grep -rn "dark:\|classList.*dark\|data-theme\|prefers-color-scheme" \
  src/ --include="*.tsx" --include="*.css" | head -20

# localStorage theme key
grep -rn "localStorage.*theme\|localStorage.*dark\|localStorage.*color-mode" \
  src/ --include="*.tsx" --include="*.ts" | head -10
```

Record: theme approach, dark mode strategy, localStorage keys used.

Report findings before migrating.

---

## 2. Migration Steps

### Step 1 — Install

```bash
npm install @humain/ui lucide-react
# or
bun add @humain/ui lucide-react
```

### Step 2 — CSS Import

Add once at the app entry point (e.g., `src/main.tsx` or `app/layout.tsx`):

```tsx
import '@humain/ui/styles.css'
```

If the project already uses Tailwind v4 and only needs tokens:

```tsx
import '@humain/ui/tokens.css'
```

Remove any conflicting reset or base CSS from the old library.

### Step 3 — ThemeProvider Wrap

Wrap the root of the app:

```tsx
import { ThemeProvider } from '@humain/ui'

// React apps (src/main.tsx)
createRoot(document.getElementById('root')!).render(
  <ThemeProvider>
    <App />
  </ThemeProvider>
)

// Next.js App Router (app/layout.tsx)
import { ThemeProvider, ThemeScript } from '@humain/ui'
export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head><ThemeScript /></head>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
```

If customizing SSR defaults, pass matching `defaultTheme` and `storageKey` values to both `ThemeScript` and `ThemeProvider`.

Remove the old provider (MuiThemeProvider, ChakraProvider, etc.) once all components are migrated.

### Step 4 — Bottom-Up Migration

Migrate leaf components before containers. Recommended order:

1. Atoms: Button, Input, Checkbox, Switch, Select, Slider, Badge, Skeleton
2. Molecules: Field (wraps Input+label+error), Tabs, Accordion, Avatar, Pagination
3. Organisms: Dialog, Sheet, DropdownMenu, Tooltip, DataTable, Sonner
4. Templates: AppShell, AppShellCard, AppSidebar, PageHeader
5. Remove old provider and uninstall old library

Migrate one component type at a time, run tests after each batch.

### Step 5 — Remove Old Dependencies

```bash
npm uninstall @mui/material @mui/icons-material @emotion/react @emotion/styled
# or
npm uninstall @chakra-ui/react @emotion/react @emotion/styled framer-motion
```

### Step 6 — Verify

```bash
# Type-check
npx tsc --noEmit

# Visual check (run Storybook or dev server)
npm run dev

# Lint
npm run lint

# Tests
npm test
```

---

## 3. Component Migration Maps

### MUI (@mui/material)

| Source | Humain | Notes |
|--------|--------|-------|
| `<Button variant="contained">` | `Button` | `appearance="solid" variant="primary"` |
| `<Button variant="outlined">` | `Button` | `appearance="outline"` |
| `<Button variant="text">` | `Button` | `appearance="ghost"` |
| `<Button color="error">` | `Button` | `variant="destructive"` |
| `<TextField label="X" />` | `Input` | label is a direct prop |
| `<TextField multiline />` | `Textarea` |  |
| `<TextField error helperText="..." />` | `Input` | error prop accepts string |
| `<Select><MenuItem value="a">A</MenuItem></Select>` | `Select` | use `<SelectItem>` instead of `<MenuItem>` |
| `<FormControlLabel control={<Checkbox />} label="X" />` | `Checkbox` | label is a direct prop |
| `<Switch />` | `Switch` | same API shape |
| `<RadioGroup><FormControlLabel control={<Radio />} /></RadioGroup>` | `RadioGroup` | use `<RadioGroupItem value="a" label="A" />` |
| `<Slider />` | `Slider` | same API shape |
| `<Dialog open={open} onClose={...}>` | `Dialog` | use compound sub-components; `onOpenChange` replaces `onClose` |
| `<Drawer anchor="right" open={open}>` | `Sheet` | `side="right"` replaces `anchor` |
| `<Snackbar>` + `<Alert>` | `Sonner` | call `toast.success()`, `toast.error()` etc. |
| `<Tooltip title="X">` | `Tooltip` | compound pattern: `<Tooltip.Trigger>` + `<Tooltip.Content>` |
| `<Menu><MenuItem>` | `DropdownMenu` | compound pattern: `<DropdownMenu.Item>` |
| `<Tabs value={tab} onChange={...}><Tab label="X" />` | `Tabs` | use `<Tabs.List><Tabs.Trigger>` sub-components |
| `<Accordion>` | `Accordion` | use `<Accordion.Item>`, `<Accordion.Trigger>`, `<Accordion.Content>` |
| `<Skeleton variant="rectangular" />` | `Skeleton` | size via className |
| `<Avatar src="..." />` | `Avatar` | add required `fallback` prop |
| `<Breadcrumbs>` | `Breadcrumb` | compound pattern: `<Breadcrumb.List>` + `<Breadcrumb.Item>` |
| `<Pagination count={10} page={page} />` | `Pagination` | `totalPages` + `currentPage` + `onPageChange` |
| `<DataGrid rows={rows} columns={cols} />` | `DataTable` | TanStack Table-based |
| `<AppBar>` + `<Drawer variant="permanent">` | `AppShell` | pair with AppSidebar; see templates.md |
| `<LinearProgress value={n} />` | `Progress` |  |
| `<CircularProgress />` | `LoadingIndicator` | indeterminate spinner |
| `<Chip label="X" />` | `Badge` | Use `closable` for removable selections |

### Chakra UI (@chakra-ui/react)

| Source | Humain | Notes |
|--------|--------|-------|
| `<Button colorScheme="blue">` | `Button` | `appearance="solid" variant="primary"` |
| `<Button variant="outline">` | `Button` | `appearance="outline"` |
| `<Button variant="ghost">` | `Button` | `appearance="ghost"` |
| `<Button colorScheme="red">` | `Button` | `variant="destructive"` |
| `<Input />` + `<FormControl><FormLabel>` | `Input` | label is a direct prop |
| `<NumberInput>` | `NumberInput` | same component name |
| `<Textarea />` | `Textarea` | same component name |
| `<Select><option value="a">A</option></Select>` | `Select` | use `<SelectItem>` instead of `<option>` |
| `<Checkbox>Label</Checkbox>` | `Checkbox` | label is a direct prop |
| `<Switch />` | `Switch` | same API shape |
| `<Modal isOpen={open} onClose={...}>` | `Dialog` | compound sub-components; `onOpenChange` replaces `onClose` |
| `<Drawer isOpen={open} placement="right">` | `Sheet` | `side="right"` replaces `placement` |
| `useToast()` → `toast({ title: '...' })` | `Sonner` | import `toast` from `@humain/ui` |
| `<Menu><MenuButton><MenuList><MenuItem>` | `DropdownMenu` | compound: `<DropdownMenu.Trigger>` + `<DropdownMenu.Item>` |
| `<Tabs><TabList><Tab>` | `Tabs` | use `<Tabs.List><Tabs.Trigger>` sub-components |
| `<Accordion allowToggle>` | `Accordion` | `type="single" collapsible` |
| `<Tooltip label="X">` | `Tooltip` | compound pattern: `<Tooltip.Trigger>` + `<Tooltip.Content>` |
| `<Avatar src="..." name="AB" />` | `Avatar` | `fallback` prop replaces `name` |
| `<Badge colorScheme="green">` | `Badge` | `color="success"` |
| `<Tag>X</Tag>` | `Badge` | Use `closable` for removable selections |
| `<Skeleton height="20px" />` | `Skeleton` | use className instead: `className="h-5 w-full"` |
| `<Progress value={n} />` | `Progress` | same API shape |

### shadcn/ui (shadcn)

| Source | Humain | Notes |
|--------|--------|-------|
| `<Button variant="default">` | `Button` | `appearance="solid" variant="primary"` |
| `<Button variant="secondary">` | `Button` | `appearance="soft" variant="secondary"` |
| `<Button variant="destructive">` | `Button` | `variant="destructive"` |
| `<Button variant="outline">` | `Button` | `appearance="outline"` |
| `<Button variant="ghost">` | `Button` | `appearance="ghost"` |
| `<Button variant="link">` | `Button` | `appearance="link"` |
| `<Input />` (no label) | `Input` | add `label` prop; use Field for complex layouts |
| `<Dialog><Dialog.Trigger>` | `Dialog` | dot notation: `<Dialog.Trigger>`; same Radix base |
| `<Sheet><SheetTrigger>` | `Sheet` | dot notation: `<Sheet.Trigger>` |
| `<AlertDialog><AlertDialog.Trigger>` | `AlertDialog` | dot notation: `<AlertDialog.Trigger>` |
| `<DropdownMenu><DropdownMenu.Trigger>` | `DropdownMenu` | dot notation: `<DropdownMenu.Trigger>` |
| `<Command><CommandInput>` | `CommandMenu` | use `open` prop for controlled |
| `<Popover><PopoverTrigger>` | `Popover` | dot notation: `<Popover.Trigger>` |
| `<Tooltip><TooltipTrigger>` | `Tooltip` | dot notation: `<Tooltip.Trigger>` |
| `<Tabs><TabsList><TabsTrigger>` | `Tabs` | dot notation: `<Tabs.List><Tabs.Trigger>` |
| `<Accordion type="single"><AccordionItem>` | `Accordion` | dot notation: `<Accordion.Item>` |
| `<Select><SelectTrigger><SelectContent>` | `Select` | simplified flat API with `<SelectItem>` |
| `<Checkbox />` | `Checkbox` | add `label` prop |
| `<Switch />` | `Switch` | same API shape |
| `<Skeleton className="h-4 w-[250px]" />` | `Skeleton` | identical API |
| `<Avatar><AvatarImage /><AvatarFallback />` | `Avatar` | simplified: `<Avatar src="..." fallback="AB" />` |
| `<Badge variant="outline">` | `Badge` | outline is supported; use `color` for semantic intent |
| `<Progress value={n} />` | `Progress` | same API shape |
| `<Separator />` | `Separator` | same component name |
| `<ScrollArea>` | `ScrollArea` | same component name |
| Local DataTable (TanStack) | `DataTable` | built-in; see organisms.md |

---

## 4. Plain HTML/CSS

| HTML/CSS pattern | Humain | Notes |
|------------------|--------|-------|
| `<button class="btn btn-primary">` | `Button` | `variant="primary"` |
| `<button class="btn btn-secondary">` | `Button` | `variant="secondary"` |
| `<input type="text" class="form-input" />` | `Input` | add `label` and `placeholder` props |
| `<select class="form-select">` | `Select` | use `<SelectItem>` children |
| `<textarea class="form-textarea">` | `Textarea` | add `label` prop |
| `<input type="checkbox">` + `<label>` | `Checkbox` | `label` is a direct prop |
| Custom modal (div + overlay) | `Dialog` | compound component |
| Custom dropdown (div + ul) | `DropdownMenu` | compound component |

---

## 5. Token Migration

Replace hardcoded colors with semantic tokens. These auto-switch in dark mode without extra code.

### Text Colors

| Find (CSS / Tailwind) | Replace with | Token |
|-----------------------|--------------|-------|
| `#000`, `#000000`, `black`, `text-black` | `text-foreground` | Primary text |
| `#374151`, `text-gray-700`, `text-zinc-700` | `text-foreground` | |
| `#6b7280`, `text-gray-500`, `text-zinc-500` | `text-secondary-foreground` | Secondary text |
| `#9ca3af`, `text-gray-400`, `text-zinc-400` | `text-muted-foreground` | Icons, placeholders, decorative metadata only |
| `#d1d5db`, `text-gray-300`, `text-zinc-300` | `text-text-quaternary` | Very muted |
| `#fff`, `#ffffff`, `white`, `text-white` | `text-foreground` (or `text-primary-foreground` on dark bg) | Context-dependent |
| `#ef4444`, `text-red-500` | `text-destructive` | Error/danger |
| `#22c55e`, `text-green-500` | `text-success` | Success |
| `#eab308`, `text-yellow-500` | `text-warning` | Warning |
| `#3b82f6`, `text-blue-500` | `text-info` | Info/link |

### Background Colors

| Find | Replace with | Token |
|------|--------------|-------|
| `#fff`, `#ffffff`, `bg-white` (full page/app canvas) | `bg-app` | Default app background |
| `#fff`, `#ffffff`, `bg-white` (intentionally solid page) | `bg-background` | Flat solid surface |
| `bg-white` (cards, panels) | `bg-card` | Card/modal surfaces |
| `#f9fafb`, `bg-gray-50` | `bg-muted` | Subtle backgrounds |
| `#f3f4f6`, `bg-gray-100` | `bg-muted` | |
| `#e5e7eb`, `bg-gray-200` | `bg-surface-2` | Elevated sections |
| `#3b82f6`, `bg-blue-500` | `bg-primary` or `bg-primary` | Brand/primary action |
| `#ef4444`, `bg-red-500` | `bg-destructive` | Error states |

### Border Colors

| Find | Replace with | Token |
|------|--------------|-------|
| `border-gray-200`, `#e5e7eb` | `border-border` | Default border |
| `border-gray-300`, `#d1d5db` | `border-border` | |
| `border-blue-500`, `#3b82f6` | `border-primary` | Focused/active border |
| `border-red-500`, `#ef4444` | `border-destructive` | Error border |

---

## 6. Dark Mode Migration

`ThemeProvider` handles dark mode automatically via CSS custom properties. Remove all manual dark mode logic:

- Remove `document.documentElement.classList.toggle('dark')` calls — use `setTheme('dark')` from `useTheme()` instead.
- Remove `dark:` overrides on semantic tokens — `text-foreground`, `bg-app`, `bg-background`, `border-border` etc. already switch automatically.
- Remove old color mode providers (MuiThemeProvider with `palette.mode`, `ChakraProvider`, `next-themes` ThemeProvider) and replace with `<ThemeProvider>` from `@humain/ui`.
- Add `<ThemeScript />` inside `<head>` for SSR apps (Next.js/Remix) to prevent flash of unstyled content. If customizing SSR defaults, pass matching `defaultTheme` and `storageKey` values to both `ThemeScript` and `ThemeProvider`.
