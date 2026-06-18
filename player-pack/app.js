(function () {
  const pack = window.THE_CURE_PACK;
  if (!pack) {
    document.body.innerHTML =
      "<p>Pack data missing. Run <code>py -3 build-player-pack.py</code> in this folder.</p>";
    return;
  }

  const { characters, hostResources, documents } = pack;
  const root = document.getElementById("app");

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
      <div class="mode-toggle" role="tablist" aria-label="Player or host">
        <button type="button" role="tab" class="mode-btn ${activeMode === "player" ? "active" : ""}" data-mode="player">Player</button>
        <button type="button" role="tab" class="mode-btn ${activeMode === "host" ? "active" : ""}" data-mode="host">Host</button>
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
    const isHost = mode === "host";

    if (isHost) {
      const resources = hostResources
        .map(
          (r) => `
        <button type="button" class="resource-btn" data-host-doc="${escapeHtml(r.id)}">
          <span class="resource-label">${escapeHtml(r.label)}</span>
          ${r.hint ? `<span class="resource-hint">${escapeHtml(r.hint)}</span>` : ""}
        </button>`
        )
        .join("");

      root.innerHTML = `
        <header class="app-header">
          <h1 class="mystery-title">The Cure</h1>
          <p class="subtitle">Facilitator / Host reference pack</p>
        </header>
        ${modeToggleHtml("host")}
        <div class="callout callout-warning">
          Facilitator only. Players should only see their dossier, player script (act by act), and extras in their character folder.
        </div>
        <h2 class="section-title">Host resources</h2>
        <div class="resource-list">${resources}</div>
        <p class="footer-note">${hostResources.length} files</p>
      `;

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
      <header class="app-header">
        <h1 class="mystery-title">The Cure</h1>
        <p class="subtitle">St. Saphicca&apos;s Progressive Care: choose who you are playing tonight</p>
      </header>
      ${modeToggleHtml("player")}
      <div class="callout callout-info">
        Pick your character to open their resource folder. Eleven suspects plus optional Officer Marz.
      </div>
      <h2 class="section-title">Cast (${mainCast.length} players)</h2>
      <div class="grid" id="cast-grid">${mainCards}</div>
      ${optionalSection}
    `;

    bindModeToggle();
    root.querySelectorAll("[data-character]").forEach((btn) => {
      btn.addEventListener("click", () => setHash(["folder", btn.dataset.character]));
    });
  }

  function renderFolder(characterId) {
    const character = findCharacter(characterId);
    if (!character) {
      setHash(["launcher", "player"]);
      return;
    }

    const resources = character.resources
      .map(
        (r) => `
      <button type="button" class="resource-btn" data-doc="${escapeHtml(r.id)}">
        <span class="resource-label">${escapeHtml(r.label)}</span>
        ${r.hint ? `<span class="resource-hint">${escapeHtml(r.hint)}</span>` : ""}
      </button>`
      )
      .join("");

    root.innerHTML = `
      <nav class="nav-bar">
        <button type="button" class="btn btn-ghost" id="back-launcher">Back to launcher</button>
      </nav>
      <header class="app-header">
        <h1>${escapeHtml(character.name)}</h1>
        <p class="subtitle">${escapeHtml(character.role)}</p>
      </header>
      <div class="callout callout-warning">
        Read your dossier first. In the player script, only open the act the facilitator has announced. Do not read ahead.
      </div>
      <h2 class="section-title">Your folder</h2>
      <div class="resource-list">${resources}</div>
    `;

    document.getElementById("back-launcher").addEventListener("click", () => setHash(["launcher", "player"]));
    root.querySelectorAll("[data-doc]").forEach((btn) => {
      btn.addEventListener("click", () => setHash(["folder", characterId, btn.dataset.doc]));
    });
  }

  function renderPlayerDocument(characterId, docId) {
    const character = findCharacter(characterId);
    const resource = character ? findCharacterResource(character, docId) : null;
    const html = documents[docId];

    if (!character || !resource || !html) {
      if (characterId) setHash(["folder", characterId]);
      else setHash(["launcher", "player"]);
      return;
    }

    root.innerHTML = `
      <nav class="nav-bar">
        <button type="button" class="btn btn-ghost" id="back-files">Back to files</button>
      </nav>
      <header class="app-header">
        <h1>${escapeHtml(resource.label)}</h1>
        <p class="doc-meta">${escapeHtml(character.name)} · ${escapeHtml(character.role)}</p>
      </header>
      ${resource.hint ? `<div class="callout callout-info">${escapeHtml(resource.hint)}</div>` : ""}
      <article class="doc-body">${html}</article>
    `;

    document.getElementById("back-files").addEventListener("click", () => setHash(["folder", characterId]));
  }

  function renderHostDocument(docId) {
    const resource = findHostResource(docId);
    const html = documents[docId];

    if (!resource || !html) {
      setHash(["launcher", "host"]);
      return;
    }

    root.innerHTML = `
      <nav class="nav-bar">
        <button type="button" class="btn btn-ghost" id="back-files">Back to files</button>
      </nav>
      <header class="app-header">
        <h1>${escapeHtml(resource.label)}</h1>
        <p class="doc-meta">Facilitator / Host</p>
      </header>
      ${resource.hint ? `<div class="callout callout-info">${escapeHtml(resource.hint)}</div>` : ""}
      <article class="doc-body">${html}</article>
    `;

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
