export default function ChatPage() {
  return (
    <div className="flex flex-col h-full">
      <header className="border-b border-border p-4">
        <h1 className="text-xl font-semibold">Chat</h1>
      </header>
      <div className="flex-1 flex items-center justify-center">
        <p className="text-muted-foreground">
          Mulai percakapan baru dengan AI assistant.
        </p>
      </div>
    </div>
  );
}
