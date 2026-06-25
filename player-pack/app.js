(function () {
  const pack = window.THE_CURE_PACK;
  if (!pack) {
    document.body.innerHTML =
      "<p>Pack data missing. Run <code>py -3 build-player-pack.py</code> in this folder.</p>";
    return;
  }

  const { characters, hostResources, documents } = pack;
  const root = document.getElementById("app");

  const ICONS = {
  back: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>`,
  chevron: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>`,
  file: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>`,
  folder: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`,
  alert: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  user: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
  host: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
};

  function icon(name) {
    return `<span class="icon">${ICONS[name] || ""}</span>`;
  }

  function heroMarkHtml() {
    return `
      <div class="hero-mark" aria-hidden="true">
        <svg class="pulse-line" viewBox="0 0 120 32" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 16 H24 L30 6 L36 26 L42 10 L48 22 L54 16 H120"/>
        </svg>
      </div>`;
  }

  function launcherHeaderHtml(subtitle) {
    return `
      <header class="app-header app-header--hero">
        ${heroMarkHtml()}
        <h1 class="mystery-title">The Cure</h1>
        <p class="subtitle">${subtitle}</p>
      </header>`;
  }

  function calloutHtml(type, text) {
    const iconName = type === "warning" ? "alert" : "file";
    return `
      <div class="callout callout-${type} callout-with-icon">
        ${icon(iconName)}
        <span>${text}</span>
      </div>`;
  }

  function resourceBtnHtml(attrs, label, hint) {
    return `
      <button type="button" class="resource-btn" ${attrs}>
        <span class="resource-btn-content">
          <span class="btn-with-icon">
            ${icon("file")}
            <span class="resource-label">${label}</span>
          </span>
          ${hint ? `<span class="resource-hint">${hint}</span>` : ""}
        </span>
        <span class="resource-chevron icon">${ICONS.chevron}</span>
      </button>`;
  }

  function backBtnHtml(id, label) {
    return `
      <button type="button" class="btn btn-ghost btn-with-icon" id="${id}">
        ${icon("back")}
        ${label}
      </button>`;
  }

  function setBodyView(view) {
    document.body.classList.remove("view-launcher", "view-page");
    document.body.classList.add(view === "launcher" ? "view-launcher" : "view-page");
  }

  function findCharacter(id) {
    return characters.find((c) => c.id === id);
  }

  function findCharacterResource(character, docId) {
    return character.resources.find((r) => r.id === docId);
  }

  function findHostResource(docId) {
    return hostResources.find((r) => r.id === docId);
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function setHash(parts) {
    const hash = parts.filter(Boolean).join("/");
    if (location.hash.replace(/^#/, "") !== hash) {
      location.hash = hash;
    }
    render();
  }

  function parseHash() {
    const parts = location.hash.replace(/^#/, "").split("/").filter(Boolean);
    const head = parts[0] || "launcher";

    let launcherMode = "player";
    if (head === "launcher" && parts[1] === "host") launcherMode = "host";
    if (head === "launcher" && parts[1] === "player") launcherMode = "player";

    return {
      head,
      launcherMode,
      characterId: head === "folder" ? parts[1] : null,
      docId:
        head === "folder" ? parts[2] : head === "host" ? parts[1] : null,
    };
  }

  function modeToggleHtml(activeMode) {
    return `
      <div class="mode-toggle mode-toggle--centered" role="tablist" aria-label="Player or host">
        <button type="button" role="tab" class="mode-btn ${activeMode === "player" ? "active" : ""}" data-mode="player">
          ${icon("user")} Player
        </button>
        <button type="button" role="tab" class="mode-btn ${activeMode === "host" ? "active" : ""}" data-mode="host">
          ${icon("host")} Host
        </button>
      </div>`;
  }

  function bindModeToggle() {
    root.querySelectorAll("[data-mode]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = btn.dataset.mode;
        setHash(["launcher", mode]);
      });
    });
  }

  function renderLauncher(mode) {
    setBodyView("launcher");
    const isHost = mode === "host";

    if (isHost) {
      const resources = hostResources
        .map((r) =>
          resourceBtnHtml(
            `data-host-doc="${escapeHtml(r.id)}"`,
            escapeHtml(r.label),
            r.hint ? escapeHtml(r.hint) : ""
          )
        )
        .join("");

      root.innerHTML = `
        <div class="view-launcher-wrap">
          ${launcherHeaderHtml("Facilitator / Host reference pack")}
          ${modeToggleHtml("host")}
          ${calloutHtml(
            "warning",
            "Facilitator only. Players should only see their dossier, player script (act by act), and extras in their character folder."
          )}
          <h2 class="section-title">Host resources</h2>
          <div class="resource-list">${resources}</div>
          <p class="footer-note">${hostResources.length} files</p>
        </div>`;

      bindModeToggle();
      root.querySelectorAll("[data-host-doc]").forEach((btn) => {
        btn.addEventListener("click", () => setHash(["host", btn.dataset.hostDoc]));
      });
      return;
    }

    function characterCard(c) {
      const optionalBadge = c.optional
        ? `<span class="card-badge">Optional 12th</span>`
        : "";
      return `
      <button type="button" class="card${c.optional ? " card-optional" : ""}" data-character="${escapeHtml(c.id)}">
        ${optionalBadge}
        <span class="card-title">${escapeHtml(c.name)}</span>
        <span class="card-role">${escapeHtml(c.role)}</span>
      </button>`;
    }

    const mainCast = characters.filter((c) => !c.optional);
    const optionalCast = characters.filter((c) => c.optional);
    const mainCards = mainCast.map(characterCard).join("");
    const optionalCards = optionalCast.map(characterCard).join("");
    const optionalSection = optionalCast.length
      ? `
      <h2 class="section-title">Optional 12th player</h2>
      <p class="section-note">Storm overflow security. Arrives after The Gathering. Full dossier and script inside.</p>
      <div class="grid grid-optional" id="optional-cast-grid">${optionalCards}</div>`
      : "";

    root.innerHTML = `
      <div class="view-launcher-wrap">
        ${launcherHeaderHtml("St. Saphicca&apos;s Progressive Care: choose who you are playing tonight")}
        ${modeToggleHtml("player")}
        ${calloutHtml("info", "Pick your character to open their dossier and script. Twelve players.")}
        <h2 class="section-title">Cast (${mainCast.length} players)</h2>
        <div class="grid" id="cast-grid">${mainCards}</div>
        ${optionalSection}
      </div>`;

    bindModeToggle();
    root.querySelectorAll("[data-character]").forEach((btn) => {
      btn.addEventListener("click", () => setHash(["folder", btn.dataset.character]));
    });
  }

  function renderFolder(characterId) {
    setBodyView("page");
    const character = findCharacter(characterId);
    if (!character) {
      setHash(["launcher", "player"]);
      return;
    }

    const resources = character.resources
      .map((r) =>
        resourceBtnHtml(
          `data-doc="${escapeHtml(r.id)}"`,
          escapeHtml(r.label),
          r.hint ? escapeHtml(r.hint) : ""
        )
      )
      .join("");

    root.innerHTML = `
      <div class="view-page-wrap">
        <nav class="nav-bar">
          ${backBtnHtml("back-launcher", "Back to launcher")}
        </nav>
        <header class="app-header">
          <h1>${escapeHtml(character.name)}</h1>
          <p class="subtitle">${escapeHtml(character.role)}</p>
        </header>
        ${calloutHtml(
          "warning",
          "Read your dossier first. In the player script, only open the act the facilitator has announced. Do not read ahead."
        )}
        <h2 class="section-title">Your folder</h2>
        <div class="resource-list">${resources}</div>
      </div>`;

    document.getElementById("back-launcher").addEventListener("click", () => setHash(["launcher", "player"]));
    root.querySelectorAll("[data-doc]").forEach((btn) => {
      btn.addEventListener("click", () => setHash(["folder", characterId, btn.dataset.doc]));
    });
  }

  function renderPlayerDocument(characterId, docId) {
    setBodyView("page");
    const character = findCharacter(characterId);
    const resource = character ? findCharacterResource(character, docId) : null;
    const html = documents[docId];

    if (!character || !resource || !html) {
      if (characterId) setHash(["folder", characterId]);
      else setHash(["launcher", "player"]);
      return;
    }

    root.innerHTML = `
      <div class="view-page-wrap">
        <nav class="nav-bar">
          ${backBtnHtml("back-files", "Back to files")}
        </nav>
        <header class="app-header">
          <h1>${escapeHtml(resource.label)}</h1>
          <p class="doc-meta">${escapeHtml(character.name)} · ${escapeHtml(character.role)}</p>
        </header>
        ${resource.hint ? calloutHtml("info", escapeHtml(resource.hint)) : ""}
        <article class="doc-body">${html}</article>
      </div>`;

    document.getElementById("back-files").addEventListener("click", () => setHash(["folder", characterId]));
  }

  function renderHostDocument(docId) {
    setBodyView("page");
    const resource = findHostResource(docId);
    const html = documents[docId];

    if (!resource || !html) {
      setHash(["launcher", "host"]);
      return;
    }

    root.innerHTML = `
      <div class="view-page-wrap">
        <nav class="nav-bar">
          ${backBtnHtml("back-files", "Back to files")}
        </nav>
        <header class="app-header">
          <h1>${escapeHtml(resource.label)}</h1>
          <p class="doc-meta">Facilitator / Host</p>
        </header>
        ${resource.hint ? calloutHtml("info", escapeHtml(resource.hint)) : ""}
        <article class="doc-body">${html}</article>
      </div>`;

    document.getElementById("back-files").addEventListener("click", () => setHash(["launcher", "host"]));
  }

  function render() {
    const { head, launcherMode, characterId, docId } = parseHash();

    if (head === "host" && docId) {
      renderHostDocument(docId);
      return;
    }

    if (head === "folder" && characterId && docId) {
      renderPlayerDocument(characterId, docId);
      return;
    }

    if (head === "folder" && characterId) {
      renderFolder(characterId);
      return;
    }

    renderLauncher(launcherMode);
  }

  window.addEventListener("hashchange", render);
  if (!location.hash) location.hash = "launcher/player";
  else render();
})();
