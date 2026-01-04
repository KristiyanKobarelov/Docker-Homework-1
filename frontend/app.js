async function loadItems() {
  const res = await fetch("/api/items");
  const items = await res.json();
  const list = document.getElementById("list");
  list.innerHTML = "";
  items.forEach(i => {
    const li = document.createElement("li");
    li.textContent = `${i.text} (${new Date(i.created_at).toLocaleString()})`;
    list.appendChild(li);
  });
}

async function addItem() {
  const text = document.getElementById("text").value.trim();
  if (!text) return;

  await fetch("/api/items", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });

  document.getElementById("text").value = "";
  await loadItems();
}

document.getElementById("add").addEventListener("click", addItem);
loadItems();