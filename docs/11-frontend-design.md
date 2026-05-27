# 10 — Frontend Design (UI/UX)

## 10.1 Prinsip Desain

1. **Familiar** — pengalaman seperti ChatGPT/Claude, tidak bingung user baru.
2. **Density tinggi** untuk power user, namun tetap clean (terinspirasi Linear, Vercel).
3. **Fokus ke konten** — tidak ada chrome berlebih di area chat.
4. **Responsive** — desktop first, tablet & mobile (PWA installable).
5. **Aksesibel** — kontras AA, keyboard navigation, screen reader.
6. **Dark mode** default; light mode toggle.

---

## 10.2 Stack Frontend

- **Next.js 15** App Router + RSC
- **React 19**
- **TailwindCSS** + **shadcn/ui** (Radix primitives)
- **Vercel AI SDK** (`useChat`, `useCompletion`)
- **Zustand** untuk client state (sidebar collapse, theme, dll)
- **TanStack Query** untuk server state + cache
- **react-plotly.js** untuk chart
- **react-markdown** + **remark-gfm** + **rehype-katex** + **mermaid**
- **react-pdf** atau native `<iframe>` untuk preview PDF
- **Framer Motion** untuk micro-interaction
- **next-themes** dark/light
- **lucide-react** icons
- **Sonner** toast

---

## 10.3 Routing (App Router)

```
app/
├── (marketing)/
│   ├── page.tsx                # Landing
│   └── pricing/page.tsx
├── (auth)/
│   ├── signin/page.tsx
│   └── signup/page.tsx
├── (app)/
│   ├── layout.tsx              # Sidebar + topbar shell
│   ├── chat/
│   │   ├── page.tsx            # Default new chat
│   │   └── [id]/page.tsx
│   ├── files/page.tsx
│   ├── knowledge/page.tsx
│   ├── reports/
│   │   ├── page.tsx
│   │   └── [id]/page.tsx
│   └── settings/
│       ├── page.tsx            # Profile
│       ├── providers/page.tsx
│       └── billing/page.tsx
└── api/
    └── chat/route.ts           # Proxy ke FastAPI (atau direct edge stream)
```

---

## 10.4 Komponen Inti

### `<AppShell>`
- Sidebar kiri (collapsible)
- Top bar (search, user menu)
- Main content slot

### `<ConversationList>`
- Group: Today / Yesterday / Last 7 days / Older
- Hover action: rename, pin, archive, delete
- Drag-reorder (V1)

### `<ChatComposer>`
- Textarea autoresize (max 8 baris)
- File upload chip (drag-drop area)
- Model dropdown (default: Auto)
- Tombol "Generate Report" (muncul jika ada file/data context)
- Slash commands: `/report`, `/csv`, `/clear`

### `<MessageBubble>`
- Avatar + role
- **Tabs internal**: `Answer` | `Sources` | `Code` | `Data`
- Tombol: Copy, Regenerate, Continue, Pin, Quote
- Citations rendered as superscript badges → modal popup teks chunk asli

### `<MarkdownRenderer>`
- Code highlight (Shiki / Prism)
- Tabel responsive (horizontal scroll)
- Math (KaTeX)
- Mermaid diagram
- **Custom blocks**:
  - `[chart:id]` → render `<PlotlyChart id={id}/>`
  - `[table:id]` → render `<DataGrid id={id}/>`

### `<PlotlyChart>`
- Lazy-load `react-plotly.js`
- Toolbar: Download PNG, fullscreen, "Re-prompt this chart"

### `<DataGrid>`
- Virtualized (TanStack Table)
- Sortable, sticky header, freeze pane

### `<FilePanel>` (right drawer, retractable)
- List file conversation
- Preview tabel sample
- Stats column (missing %, dtype)
- Tombol "Use in next message"

### `<KnowledgeManager>` (page `/knowledge`)
- Grid card per dokumen
- Status badge (processing / ready / failed)
- Tag editor inline
- Bulk: delete, re-embed

### `<ReportEditor>` (page `/reports/[id]`)
- Layout 3-pane:
  - Kiri: outline tree (drag-drop)
  - Tengah: Markdown editor (CodeMirror) atau rich preview
  - Kanan: PDF live preview
- Per-section toolbar: Regenerate, Edit instruction, Lock
- Tombol global: Save, Export PDF/DOCX

### `<ChartPromptModal>`
Quick form: pilih chart type, x/y, color, agregasi → langsung generate via `make_chart` tool.

---

## 10.5 Streaming UI

Pakai `useChat` (Vercel AI SDK) yang dibungkus custom transport:

```ts
const { messages, input, handleSubmit, isLoading } = useChat({
  api: "/api/chat",          // Next route.ts proxy
  experimental_throttle: 50, // ms
  onResponse: (res) => { /* parse custom SSE events */ },
});
```

Custom event handler untuk `chart`, `table`, `tool_*` events → store di Zustand keyed by message_id.

---

## 10.6 Mobile (Responsive + PWA)

- Sidebar jadi off-canvas (sheet) di mobile
- Composer sticky bottom
- File panel via tab di header
- PWA: manifest + service worker (cache shell + offline message queue)

---

## 10.7 Accessibility Checklist

- ✅ Semua interactive component punya focus ring
- ✅ ARIA label di icon button
- ✅ Kontras teks min 4.5:1 (WCAG AA)
- ✅ Skip-to-main link
- ✅ Keyboard shortcut: `⌘/` cheatsheet, `⌘K` command palette, `⌘Enter` send

---

## 10.8 Theming

Token TailwindCSS (`tailwind.config.ts`):
```ts
colors: {
  background: "hsl(var(--bg))",
  surface: "hsl(var(--surface))",
  primary: { DEFAULT: "hsl(var(--primary))", fg: "..." },
  muted: ...,
  accent: ...,
}
```

CSS variables:
```css
:root {
  --bg: 0 0% 100%;
  --surface: 0 0% 98%;
  --primary: 217 91% 35%;       /* navy-blue uReport AI */
}
.dark {
  --bg: 224 16% 8%;
  --surface: 224 14% 12%;
  --primary: 217 91% 60%;
}
```

---

## 10.9 Empty States

- Chat kosong: tampilkan 4 tombol prompt-suggestion + animasi subtle
- Sidebar kosong: ilustrasi + CTA "Mulai chat baru"
- Knowledge kosong: drag-drop area besar dengan format yang didukung

---

## 10.10 Error & Loading States

- Skeleton loader untuk message bubble
- Inline retry button saat error
- Toast (Sonner) untuk error global
- Connection lost banner saat SSE drop → auto-resume

---

## 10.11 Performance Target

| Metric | Target |
|---|---|
| LCP (landing) | < 2.0s |
| TTI (chat page) | < 2.5s |
| Time to first token (chat) | < 800ms |
| Bundle size (route /chat) | < 250 KB gz |

Strategi:
- Code-split Plotly (lazy on demand)
- Suspense + RSC untuk shell
- Image optimization (Next/Image)
- Edge caching landing
