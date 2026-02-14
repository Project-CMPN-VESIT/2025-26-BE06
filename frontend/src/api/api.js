export async function askQuestion(question, history = []) {
  const res = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history })
  });
  return res.json();
}