# Chat Interface Recipe

**Use:** AIContainer, AIMessage, AIInput
**Optional:** AIEmptyState, AIPromptSuggestion, AIFeedbackBar

```tsx
import { useState } from 'react'
import {
  AIContainer,
  AIEmptyState,
  AIPromptSuggestion,
  type ChatMessage
} from '@humain/ui'

function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')

  const handleSend = (message: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'sent',
      content: message,
      timestamp: new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'received',
        content: 'This is an AI response.',
        senderName: 'AI Assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }),
        avatar: { src: '/avatar.png', alt: 'AI' },
        isAgent: true,
        showActions: true
      }
      setMessages(prev => [...prev, aiMessage])
    }, 1000)
  }

  return (
    <AIContainer messages={messages}>
      <AIContainer.Messages
        emptyContent={
          <AIEmptyState title="How can I help you today?">
            <AIPromptSuggestion onClick={() => setInputValue('Summarize my tasks')}>
              Summarize my tasks
            </AIPromptSuggestion>
            <AIPromptSuggestion onClick={() => setInputValue('Schedule a meeting')}>
              Schedule a meeting
            </AIPromptSuggestion>
          </AIEmptyState>
        }
      />
      <AIContainer.Input
        inputProps={{
          value: inputValue,
          onChange: setInputValue,
          onSubmit: handleSend,
          placeholder: 'Type a message...'
        }}
      />
    </AIContainer>
  )
}
```

When rendering transcript rows as custom children instead of using the
`messages` prop, pass one stable `autoScrollKey` from the latest message,
streaming chunk, or response revision:

```tsx
<AIContainer autoScrollKey={messages.at(-1)?.id ?? null}>
  <AIContainer.Messages>
    {messages.map((message) => (
      <CustomMessageRow key={message.id} message={message} />
    ))}
  </AIContainer.Messages>
  <AIContainer.Input inputProps={{ onSubmit: handleSend }} />
</AIContainer>
```

If only the message region owns the transcript state, put the key on
`AIContainer.Messages` instead. Do not pass both root and message-level keys
for the same list.

Auto-scroll still respects `autoScrollOnNewMessage`: it pauses when the user
scrolls away from the bottom and resumes after they return to the bottom.

**Key props:**
- `AIMessage`: type (sent|received), content, markdown, avatar, isAgent, showActions
- `AIInput`: value, onChange, onSubmit, placeholder, disabled, onFilesSelected, accept, multiple, dropText, uploadingFiles, onRemoveFile, pasteAsFile
- `AIContainer`: Uses compound components (Header, Messages, Footer, Input); use one root or `Messages` `autoScrollKey` when children render the transcript
- `AIEmptyState`: title, subtitle, children (for prompt suggestions)

## Chat + Generated Output Panel

For assistant workspaces that switch the generated output between table, chart,
dashboard, and detail views, keep the chat chrome and generated-output chrome
separate. Chat applications that produce generated content should look like a
left conversation rail beside a right generated-output workspace:

- Use `AppShell.Root` with exactly two sibling `AppShell.Panel` children.
- Put `AIContainer` directly in the left chat panel.
- Put generated output in a sibling right `AppShell.Panel` with `AppShellCard`.
- Do not combine the transcript, input, and generated table/chart/dashboard in
  one `AppShellCard` or one single-column surface.
- Do not compute `bodyPadding` with a ternary. Render separate `AppShellCard`
  branches for table, chart, and detail views.
- Use literal `bodyPadding="none"` on table and chart branches.
- Let detail/form/copy branches use default `AppShellCard` padding.

```tsx
<AppShell.Root defaultPanelSizes={[35, 65]}>
  <AppShell.Panel minWidth={320} label="Assistant">
    <AIContainer messages={messages}>
      <AIContainer.Messages emptyContent={<AIEmptyState title="Ask anything" />} />
      <AIContainer.Input inputProps={{ onSubmit: handleSend }} />
    </AIContainer>
  </AppShell.Panel>

  <AppShell.Panel minWidth="45%" label="Generated output">
    {activeView === 'table' && (
      <AppShellCard bodyPadding="none">
        <AppShellCard.Header>
          <AppShellCard.Title>Generated rows</AppShellCard.Title>
          <AppShellCard.Subtitle>Sortable analysis output</AppShellCard.Subtitle>
        </AppShellCard.Header>
        <DataTable columns={columns} data={rows} getRowId={(row) => row.id} />
      </AppShellCard>
    )}

    {activeView === 'chart' && (
      <AppShellCard bodyPadding="none">
        <AppShellCard.Header>
          <AppShellCard.Title>Resolution trend</AppShellCard.Title>
          <AppShellCard.Subtitle>Token-backed chart series</AppShellCard.Subtitle>
        </AppShellCard.Header>
        <BarChart data={chartData} series={chartSeries} />
      </AppShellCard>
    )}

    {activeView === 'detail' && (
      <AppShellCard>
        <AppShellCard.Header>
          <AppShellCard.Title>Recommended action</AppShellCard.Title>
          <AppShellCard.Subtitle>Decision-ready summary</AppShellCard.Subtitle>
        </AppShellCard.Header>
        <DetailView />
      </AppShellCard>
    )}
  </AppShell.Panel>
</AppShell.Root>
```
