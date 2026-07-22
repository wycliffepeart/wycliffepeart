export function Path({ items }: { items: string[] }) {
  return (
    <div className="path" aria-label="Relationship path">
      {items.map((item) => (
        <span key={item}>{item}</span>
      ))}
    </div>
  );
}
