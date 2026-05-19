document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("skills-container");
  const addBtn = document.getElementById("add-skill-btn");
  const inputWrapper = document.getElementById("skill-input-wrapper");
  const input = document.getElementById("skill-input");
  const suggestions = document.getElementById("skill-suggestions");

  if (!container || !addBtn || !inputWrapper || !input || !suggestions) {
    return;
  }

  const userId = container.dataset.userId;
  let debounceTimer = null;

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i += 1) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === `${name}=`) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function hideSuggestions() {
    suggestions.innerHTML = "";
    suggestions.classList.add("hidden");
  }

  function removeEmptyLabel() {
    const emptyLabel = container.querySelector(".skill-empty");
    if (emptyLabel) {
      emptyLabel.remove();
    }
  }

  function createSkillChip(skill) {
    removeEmptyLabel();

    const chip = document.createElement("span");
    chip.className = "skill-chip";
    chip.dataset.id = skill.id;
    chip.innerHTML = `
      ${skill.name}
      <button type="button" class="remove-skill-btn" aria-label="Удалить" title="Удалить">×</button>
    `;

    container.insertBefore(chip, addBtn);
  }

  async function addSkill(payload) {
    const res = await fetch(`/users/${userId}/skills/add/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      return;
    }

    const skill = await res.json();

    const exists = container.querySelector(`.skill-chip[data-id="${skill.id}"]`);
    if (!exists) {
      createSkillChip(skill);
    }

    input.value = "";
    hideSuggestions();
    inputWrapper.classList.add("hidden");
  }

  async function loadSuggestions(query) {
    const res = await fetch(`/users/skills/?q=${encodeURIComponent(query)}`);
    if (!res.ok) {
      hideSuggestions();
      return;
    }

    const data = await res.json();
    suggestions.innerHTML = "";

    data.forEach((skill) => {
      const li = document.createElement("li");
      li.className = "skill-suggestion-item";
      li.textContent = skill.name;
      li.addEventListener("click", () => addSkill({ skill_id: skill.id }));
      suggestions.appendChild(li);
    });

    const exactMatch = data.some(
      (skill) => skill.name.toLowerCase() === query.trim().toLowerCase()
    );

    if (query.trim() && !exactMatch) {
      const createItem = document.createElement("li");
      createItem.className = "skill-suggestion-item create-skill-item";
      createItem.textContent = `Создать "${query.trim()}"`;
      createItem.addEventListener("click", () => addSkill({ name: query.trim() }));
      suggestions.appendChild(createItem);
    }

    if (suggestions.children.length > 0) {
      suggestions.classList.remove("hidden");
    } else {
      hideSuggestions();
    }
  }

  addBtn.addEventListener("click", () => {
    inputWrapper.classList.toggle("hidden");
    input.focus();
  });

  input.addEventListener("input", () => {
    const query = input.value.trim();

    clearTimeout(debounceTimer);

    if (!query) {
      hideSuggestions();
      return;
    }

    debounceTimer = setTimeout(() => {
      loadSuggestions(query);
    }, 250);
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const query = input.value.trim();
      if (query) {
        addSkill({ name: query });
      }
    }
  });

  document.addEventListener("click", (event) => {
    if (!inputWrapper.contains(event.target) && event.target !== addBtn) {
      hideSuggestions();
    }
  });

  container.addEventListener("click", async (event) => {
    const removeBtn = event.target.closest(".remove-skill-btn");
    if (!removeBtn) {
      return;
    }

    const chip = removeBtn.closest(".skill-chip");
    const skillId = chip.dataset.id;

    const res = await fetch(`/users/${userId}/skills/${skillId}/remove/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });

    if (res.ok) {
      chip.remove();

      const chipsLeft = container.querySelectorAll(".skill-chip").length;
      if (chipsLeft === 0) {
        const emptyLabel = document.createElement("span");
        emptyLabel.className = "skill-empty";
        emptyLabel.textContent = "Навыки пока не добавлены";
        container.insertBefore(emptyLabel, addBtn);
      }
    }
  });
});