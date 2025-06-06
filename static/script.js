const API = ""; // Change this if your backend runs elsewhere

function renderCard(card) {
  if (card === '??' || card.hidden) {
    return `<div class="card">??</div>`;
  }

  const suitMap = {
    'spades': '♠',
    'clubs': '♣',
    'hearts': '♥',
    'diamonds': '♦'
  };

  const isRed = card.suit === 'hearts' || card.suit === 'diamonds';
  const suitSymbol = suitMap[card.suit];
  const rank = card.rank;

  return `
    <div class="card ${isRed ? 'red' : ''}">
      <div class="rank">${rank}</div>
      <div class="suit">${suitSymbol}</div>
    </div>
  `;
}

function renderCards(cards, elementId) {
  const container = document.getElementById(elementId);
  container.innerHTML = "";
  cards.forEach(card => {
    container.innerHTML += renderCard(card);
  });
}

async function startGame() {
  const res = await fetch(`${API}/start`, { method: "POST" });
  const data = await res.json();
  renderCards(data.player, "player-hand");
  renderCards(data.dealer, "dealer-hand");
  document.getElementById("player-value").textContent = "";
  document.getElementById("dealer-value").textContent = "";
  document.getElementById("result").textContent = "";
  document.getElementById("game-count").textContent = `Games Played: ${data.games_played}`;
}

async function hit() {
  const res = await fetch(`${API}/hit`, { method: "POST" });
  const data = await res.json();
  renderCards(data.player, "player-hand");
  document.getElementById("player-value").textContent = `Value: ${data.value}`;
  if (data.bust) {
    document.getElementById("result").textContent = "You busted!";
  }
}

async function stand() {
  const res = await fetch(`${API}/stand`, { method: "POST" });
  const data = await res.json();
  renderCards(data.dealer, "dealer-hand");
  document.getElementById("dealer-value").textContent = `Value: ${data.value}`;
  document.getElementById("result").textContent = data.result;
}

function changeTheme(themeName) {
  document.body.className = themeName;
}

// Load last selected theme from localStorage (optional)
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "default";
  changeTheme(savedTheme);
  document.getElementById("theme").value = savedTheme;
});

document.getElementById("theme").addEventListener("change", (e) => {
  localStorage.setItem("theme", e.target.value);
});
