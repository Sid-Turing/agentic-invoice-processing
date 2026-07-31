# Form Building Recipe

**Use:** Input, Select, Checkbox, Switch, Textarea, Button
**Optional:** Autocomplete, RadioGroup, CheckboxGroup, NumberInput, FileInput, InputGroup, Form

All form controls accept field props (label, error, description, tooltip, required) directly.
When any field prop is set, the component auto-wraps in a Field internally. When none are set, it renders bare.
Use `startIcon`/`endIcon` for field icons. Do not manually place absolute-positioned icons over `Input` or `Textarea` and compensate with padding classes.
Use the flat `Select` API for form dropdowns. If compound `SelectRoot`/`SelectPopup` is required, keep `alignItemWithTrigger={false}` so the menu anchors below or above the trigger instead of covering the field.
Use `InputGroup` when addons and an editable control form one compound field, such as a protocol prefix, currency selector, tag field, or attached action. Keep unrelated fields as separate `Input` components.

\`\`\`tsx
import { useState } from 'react'
import {
  Input,
  Select,
  SelectItem,
  Checkbox,
  Button
} from '@humain/ui'

interface FormData {
  name: string
  email: string
  role: string
  agreed: boolean
}

interface FormErrors {
  name?: string
  email?: string
  role?: string
  agreed?: string
}

function ContactForm() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    role: '',
    agreed: false
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validate = (): boolean => {
    const newErrors: FormErrors = {}
    if (!formData.name) newErrors.name = 'Name is required'
    if (!formData.email) newErrors.email = 'Email is required'
    else if (!/\\S+@\\S+\\.\\S+/.test(formData.email)) newErrors.email = 'Invalid email'
    if (!formData.role) newErrors.role = 'Please select a role'
    if (!formData.agreed) newErrors.agreed = 'You must agree to terms'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setIsSubmitting(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('Form submitted:', formData)
    setIsSubmitting(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
      <Input
        label="Full Name"
        placeholder="Enter your name"
        required
        value={formData.name}
        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
        error={errors.name}
      />

      <Input
        label="Email"
        type="email"
        placeholder="name@company.com"
        required
        value={formData.email}
        onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
        error={errors.email}
        description="We'll never share your email"
      />

      <Select
        label="Role"
        required
        placeholder="Select a role"
        value={formData.role}
        onValueChange={(value) => setFormData(prev => ({ ...prev, role: value }))}
        error={errors.role}
      >
        <SelectItem value="developer">Developer</SelectItem>
        <SelectItem value="designer">Designer</SelectItem>
        <SelectItem value="manager">Manager</SelectItem>
        <SelectItem value="other">Other</SelectItem>
      </Select>

      <Checkbox
        label="I agree to the terms and conditions"
        checked={formData.agreed}
        onCheckedChange={(checked) => setFormData(prev => ({ ...prev, agreed: checked }))}
        error={errors.agreed}
      />

      <Button type="submit" variant="primary" size="md" loading={isSubmitting}>
        Submit
      </Button>
    </form>
  )
}
\`\`\`

**Key props:**
- \`Input\`: label, error, description, required, size (sm|md|lg), startIcon, endIcon, startAddon, endAddon
- \`Select\`: label, error, description, required, placeholder, size (xs|sm|md|lg), value, onValueChange
- \`Checkbox\`: label, error, description, variant, size (sm|md|lg), checked, onCheckedChange
- \`Switch\`: label, description, size (sm|default), checked, onCheckedChange
- \`Textarea\`: label, error, description, required, startIcon, endIcon
- \`InputGroup\`: size (xs|sm|md|lg), shape (rounded|round), state (default|success|destructive), filled, disabled, readOnly; compose InputGroupInput/InputGroupTextarea, InputGroupAddon, InputGroupText, and InputGroupButton
- \`Button\`: appearance (solid|outline|ghost|link|soft|gradient|ai), variant (primary|secondary|info|success|warning|destructive), shape (rounded|round), size (default|xs|sm|md|lg|xl|2xl|icon|icon-xs|icon-sm|icon-lg|icon-xl|icon-2xl), loading, startIcon, endIcon

**FieldProps (all form controls):** label, required, labelIcon, tooltip, topRight, description, bottomRight, error, fieldClassName
(Checkbox and Switch omit topRight and bottomRight)
