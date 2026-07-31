# Dialogs and Overlays Recipe

**Use:** Dialog, Button
**Also covers:** Sheet, Drawer, AlertDialog

New, create, add, invite, and edit forms launched from a list or detail screen are `Dialog` flows by default. Trigger the dialog from the page/header action, put fields in `Dialog.Body`, and put Cancel/Submit actions in `Dialog.Footer`. Do not create a standalone page just to host a transient form.

```tsx
import { useState } from 'react'
import {
  Dialog,
  AlertDialog,
  Button,
  Input
} from '@humain/ui'
import { CheckCircle } from 'lucide-react'

// Basic confirmation dialog with trigger
function ConfirmationDialog() {
  return (
    <Dialog>
      <Dialog.Trigger render={<Button />}>Open Dialog</Dialog.Trigger>
      <Dialog.Popup>
        <Dialog.Header>
          <Dialog.Icon variant="success">
            <CheckCircle />
          </Dialog.Icon>
          <Dialog.HeaderContent>
            <Dialog.Title>Blog post published</Dialog.Title>
            <Dialog.Description>
              This blog post has been published. Team members will be able to
              edit this post and republish changes.
            </Dialog.Description>
          </Dialog.HeaderContent>
        </Dialog.Header>
        <Dialog.Footer>
          <Dialog.Cancel>Cancel</Dialog.Cancel>
          <Dialog.Action>Confirm</Dialog.Action>
        </Dialog.Footer>
      </Dialog.Popup>
    </Dialog>
  )
}

// Form dialog with controlled state
function EditProfileDialog() {
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSave = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsLoading(false)
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Dialog.Trigger render={<Button />}>Edit Profile</Dialog.Trigger>
      <Dialog.Popup>
        <Dialog.Header>
          <Dialog.Title>Edit Profile</Dialog.Title>
          <Dialog.Description>
            Make changes to your profile here. Click save when you're done.
          </Dialog.Description>
        </Dialog.Header>
        <Dialog.Body>
          <Input label="Name" placeholder="Enter your name" defaultValue="John Doe" />
          <Input label="Email" type="email" placeholder="Enter your email" />
        </Dialog.Body>
        <Dialog.Footer>
          <Dialog.Cancel disabled={isLoading}>
            Cancel
          </Dialog.Cancel>
          <Dialog.Action onClick={handleSave} loading={isLoading}>
            Save Changes
          </Dialog.Action>
        </Dialog.Footer>
      </Dialog.Popup>
    </Dialog>
  )
}

// Destructive action dialog
function DeleteDialog() {
  return (
    <AlertDialog>
      <AlertDialog.Trigger render={<Button variant="destructive" appearance="solid" />}>
        Delete Item
      </AlertDialog.Trigger>
      <AlertDialog.Popup>
        <AlertDialog.Header>
          <AlertDialog.Title>Delete Item</AlertDialog.Title>
          <AlertDialog.Description>
            Are you sure you want to delete this item? This action cannot be undone.
          </AlertDialog.Description>
        </AlertDialog.Header>
        <AlertDialog.Footer>
          <AlertDialog.Cancel render={<Button appearance="outline" />}>Cancel</AlertDialog.Cancel>
          <AlertDialog.Action render={<Button variant="destructive" />}>Delete</AlertDialog.Action>
        </AlertDialog.Footer>
      </AlertDialog.Popup>
    </AlertDialog>
  )
}
```

**Key props:**
- `Dialog`: open, onOpenChange, defaultOpen, modal
- `Dialog.Trigger`: render (polymorphic element)
- `Dialog.Popup`: size (sm|md|lg|xl|full), showCloseButton, disableAnimation
- `Dialog.Header`: layout (stacked|horizontal|centered), divider, paddingBottom
- `Dialog.HeaderContent`: Wraps title and description text
- `Dialog.Body`: Content area between header and footer (for forms)
- `Dialog.Footer`: layout (horizontal|horizontal-fill|horizontal-right|stacked|vertical-fill|wizard), divider
- `Dialog.Action`: Primary footer action button
- `Dialog.Cancel`: Secondary footer action button that closes the dialog
- `Dialog.Icon`: variant (success|warning|destructive|info), size (sm|md|lg)
- `Dialog.Close`: Closes dialog when clicked, use render prop for custom button

**Sheet** (side panel):
- `SheetPopup`: side (top|right|bottom|left), width (sm|md|lg|xl|full)

**Drawer** (slide-out):
- `Drawer`: direction (top|right|bottom|left), open, onOpenChange
