// Cart lives in localStorage and is display-only: the server never trusts prices from it.
const MAX_QTY = 20; // mirrors the server's quantity <= 20 rule

// ---- storage helpers ----
const getCart = () => {
  try {
    return JSON.parse(localStorage.getItem("cart")) || [];
  } catch {
    return [];
  }
};

const saveCart = (cart) => {
  try {
    localStorage.setItem("cart", JSON.stringify(cart));
  } catch {
    /* storage blocked: cart just won't persist */
  }
  updateBadge();
};

// ---- cart operations ----
function addToCart({ product_id, name, price_cents }) {
  const cart = getCart();
  const line = cart.find((l) => l.product_id === product_id);
  if (line) line.quantity = Math.min(line.quantity + 1, MAX_QTY);
  else cart.push({ product_id, name, price_cents, quantity: 1 });
  saveCart(cart);
}

function removeFromCart(id) {
  saveCart(getCart().filter((l) => l.product_id !== id));
}

function setQuantity(id, qty) {
  if (qty < 1) return removeFromCart(id);
  const cart = getCart();
  const line = cart.find((l) => l.product_id === id);
  if (!line) return;
  line.quantity = Math.min(qty, MAX_QTY);
  saveCart(cart);
}

// ---- display helpers ----
const formatMoney = (cents) => (cents / 100).toFixed(2);

function updateBadge() {
  const el = document.getElementById("cart-count");
  if (el) el.textContent = getCart().reduce((n, l) => n + l.quantity, 0);
}

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text; // textContent: never injects HTML
  if (className) node.className = className;
  return node;
}

function actionButton(label, action, id, ariaLabel) {
  const b = el("button", label, "btn btn-small");
  b.type = "button";
  b.dataset.action = action;
  b.dataset.id = id;
  if (ariaLabel) b.setAttribute("aria-label", ariaLabel);
  return b;
}

// ---- cart page ----
function renderCart() {
  const container = document.getElementById("cart-items");
  if (!container) return; // not the cart page

  const cart = getCart();
  const form = document.getElementById("checkout-form");
  const totalEl = document.getElementById("cart-total");
  container.replaceChildren();

  if (cart.length === 0) {
    container.append(el("p", "Your cart is empty.", "empty"));
    if (form) form.hidden = true;
    if (totalEl) totalEl.textContent = formatMoney(0);
    return;
  }
  if (form) form.hidden = false;

  const table = el("table", undefined, "cart-table");
  const head = table.createTHead().insertRow();
  ["Item", "Price", "Qty", "Total", ""].forEach((h) => head.append(el("th", h)));
  const body = table.createTBody();

  let total = 0;
  for (const l of cart) {
    const lineTotal = l.price_cents * l.quantity;
    total += lineTotal;

    const row = body.insertRow();
    row.append(el("td", l.name));
    row.append(el("td", formatMoney(l.price_cents)));

    const qtyCell = el("td", undefined, "qty");
    qtyCell.append(
      actionButton("-", "dec", l.product_id, `Decrease ${l.name}`),
      el("span", l.quantity),
      actionButton("+", "inc", l.product_id, `Increase ${l.name}`)
    );
    row.append(qtyCell);

    row.append(el("td", formatMoney(lineTotal)));

    const rm = actionButton("Remove", "remove", l.product_id, `Remove ${l.name}`);
    const rmCell = el("td");
    rmCell.append(rm);
    row.append(rmCell);
  }
  container.append(table);
  if (totalEl) totalEl.textContent = formatMoney(total);
}

function showError(message) {
  const errorEl = document.getElementById("error");
  if (errorEl) errorEl.textContent = message;
}

async function submitOrder(e) {
  e.preventDefault();
  showError("");

  const cart = getCart();
  if (cart.length === 0) return showError("Your cart is empty.");

  const customer = Object.fromEntries(new FormData(e.target));
  const items = cart.map((l) => ({ product_id: l.product_id, quantity: l.quantity })); // no prices sent

  const submit = e.target.querySelector("[type=submit]");
  if (submit) submit.disabled = true;

  try {
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer, items }),
    });

    if (res.status === 201) {
      const order = await res.json();
      try {
        localStorage.removeItem("cart");
      } catch {
        /* ignore */
      }
      location.href = `/order/${order.id}`;
      return;
    }

    const body = await res.json().catch(() => ({}));
    const { detail } = body;
    showError(
      Array.isArray(detail)
        ? detail.map((d) => d.msg).join(", ") // 422: list of {msg}
        : detail || "Something went wrong. Please try again." // 404/409: string
    );
  } catch {
    showError("Network error. Please check your connection and try again.");
  }
  if (submit) submit.disabled = false;
}

// ---- events ----
document.addEventListener("click", (e) => {
  // products page: add to cart
  const add = e.target.closest(".add-to-cart");
  if (add) {
    addToCart({
      product_id: Number(add.dataset.id),
      name: add.dataset.name,
      price_cents: Number(add.dataset.price),
    });
    return;
  }

  // cart page: inc / dec / remove
  const btn = e.target.closest("[data-action]");
  if (!btn) return;
  const id = Number(btn.dataset.id);
  const line = getCart().find((l) => l.product_id === id);
  if (btn.dataset.action === "remove") removeFromCart(id);
  else if (line && btn.dataset.action === "inc") setQuantity(id, line.quantity + 1);
  else if (line && btn.dataset.action === "dec") setQuantity(id, line.quantity - 1);
  renderCart();
});

document.addEventListener("DOMContentLoaded", () => {
  updateBadge();
  renderCart();
  document.getElementById("checkout-form")?.addEventListener("submit", submitOrder);
});
