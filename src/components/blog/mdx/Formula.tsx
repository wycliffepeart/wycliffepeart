export function Formula({ left, result }: { left: string; result: string }) {
  return (
    <div className="formula">
      <span>{left}</span>
      <b>=</b>
      <span className="result">{result}</span>
    </div>
  );
}
