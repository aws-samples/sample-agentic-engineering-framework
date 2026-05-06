import "./style.css";

const features = [
  {
    icon: "🤖",
    title: "Agent-Driven Development",
    description:
      "AI agents that plan, code, and test autonomously — delivering working software faster.",
  },
  {
    icon: "📋",
    title: "Spec-First Workflow",
    description:
      "Every change starts with a researched specification grounded in your actual codebase.",
  },
  {
    icon: "🔄",
    title: "Phase-Based Execution",
    description:
      "A structured Plan → Implement → Validate pipeline that keeps quality high.",
  },
  {
    icon: "🛡️",
    title: "Built-In Safety",
    description:
      "Production guardrails and confirmation gates prevent accidental damage.",
  },
  {
    icon: "👤",
    title: "Human-in-the-Loop",
    description:
      "Review points at every critical decision so you stay in control.",
  },
];

const grid = document.getElementById("features-grid");
features.forEach((f) => {
  const card = document.createElement("article");
  card.className = "card";
  const icon = document.createElement("div");
  icon.className = "icon";
  icon.textContent = f.icon;
  const h3 = document.createElement("h3");
  h3.textContent = f.title;
  const p = document.createElement("p");
  p.textContent = f.description;
  card.append(icon, h3, p);
  grid.appendChild(card);
});
