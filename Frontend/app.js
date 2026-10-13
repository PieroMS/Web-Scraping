
"use strict";

// ============================================================
// CONFIGURACION
// ============================================================

const API_BASE = "http://127.0.0.1:8000";

let lastAnalysis = null;

const $ = (selector) => document.querySelector(selector);

const form = $("#analyzeForm");
const urlInput = $("#urlInput");
const analyzeButton = $("#analyzeButton");
const buttonText = $("#buttonText");
const buttonIcon = $("#buttonIcon");
const alertBox = $("#alertBox");
const emptyState = $("#emptyState");
const results = $("#results");
const downloadButton = $("#downloadJson");

// ============================================================
// UTILIDADES
// ============================================================

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function setText(selector, value, fallback = "No disponible") {
    const element = $(selector);

    if (element) {
        element.textContent =
            value === null || value === undefined || value === ""
                ? fallback
                : String(value);
    }
}

function formatNumber(value) {
    return Number(value || 0).toLocaleString("es-PE");
}

function formatDate(value) {
    if (!value) return "No disponible";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("es-PE", {
        dateStyle: "medium",
        timeStyle: "short"
    });
}

function showAlert(message) {
    alertBox.textContent = message;
    alertBox.classList.remove("hidden");
}

function hideAlert() {
    alertBox.textContent = "";
    alertBox.classList.add("hidden");
}

function setLoading(loading) {
    analyzeButton.disabled = loading;
    urlInput.disabled = loading;

    if (loading) {
        buttonIcon.innerHTML = '<span class="loading-spinner"></span>';
        buttonText.textContent = "Analizando...";
    } else {
        buttonIcon.textContent = "⌕";
        buttonText.textContent = "Analizar sitio";
    }
}

function setHTML(selector, html) {
    $(selector).innerHTML = html;
}

function emptyMessage(message) {
    return `<p class="muted">${escapeHTML(message)}</p>`;
}

function getArray(value) {
    return Array.isArray(value) ? value : [];
}

function getObject(value) {
    return value && typeof value === "object" && !Array.isArray(value)
        ? value
        : {};
}

function displayValue(value) {
    if (value === null || value === undefined || value === "") {
        return "No disponible";
    }

    if (typeof value === "object") {
        return JSON.stringify(value);
    }

    return String(value);
}

// ============================================================
// ESTADO DE LA API
// ============================================================

async function checkAPI() {
    const dot = $("#apiDot");
    const label = $("#apiStatus");

    try {
        const response = await fetch(`${API_BASE}/api/health`, {
            signal: AbortSignal.timeout(5000)
        });

        if (!response.ok) {
            throw new Error("API no disponible");
        }

        dot.className = "status-dot online";
        label.textContent = "API conectada";
    } catch {
        dot.className = "status-dot offline";
        label.textContent = "API desconectada";
    }
}

// ============================================================
// ANALIZAR URL
// ============================================================

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await analyzeWebsite(urlInput.value.trim());
});

$("#exampleButton").addEventListener("click", () => {
    urlInput.value = "https://example.com";
    analyzeWebsite(urlInput.value);
});

async function analyzeWebsite(url) {
    hideAlert();

    if (!url) {
        showAlert("Introduce una URL para analizar.");
        urlInput.focus();
        return;
    }

    let parsedURL;

    try {
        parsedURL = new URL(url);
    } catch {
        showAlert("La URL introducida no tiene un formato válido.");
        return;
    }

    if (!["http:", "https:"].includes(parsedURL.protocol)) {
        showAlert("Solo se admiten direcciones HTTP o HTTPS.");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch(`${API_BASE}/api/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        });

        let data;

        try {
            data = await response.json();
        } catch {
            throw new Error(
                `El servidor devolvió una respuesta no válida (HTTP ${response.status}).`
            );
        }

        if (!response.ok) {
            const detail = data.detail;

            throw new Error(
                typeof detail === "string"
                    ? detail
                    : `No se pudo analizar la página (HTTP ${response.status}).`
            );
        }

        if (data.success !== true) {
            throw new Error("La API no confirmó que el análisis se completó.");
        }

        lastAnalysis = data;
        renderDashboard(data);

        emptyState.classList.add("hidden");
        results.classList.remove("hidden");
        downloadButton.disabled = false;

        // Muestra los resultados sin perder el contexto de la página.
        $("#overview").scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        checkAPI();
    } catch (error) {
        console.error("Error de análisis:", error);

        const message = error.name === "TypeError"
            ? "No se pudo conectar con el backend. Comprueba que FastAPI está activo en http://127.0.0.1:8000."
            : error.message;

        showAlert(message);
    } finally {
        setLoading(false);
    }
}

// ============================================================
// RENDERIZADO GENERAL
// ============================================================

function renderDashboard(data) {
    const summary = getObject(data.summary);
    const design = getObject(data.design);
    const structure = getObject(data.structure);
    const seo = getObject(data.seo);

    setText("#analyzedUrl", data.requestedUrl);
    setText("#statElements", formatNumber(summary.visibleElements), "0");
    setText("#statImages", formatNumber(summary.images), "0");
    setText("#statButtons", formatNumber(summary.buttons), "0");
    setText("#statLinks", formatNumber(summary.links), "0");

    setText("#pageTitle", summary.title);
    setText("#pageLanguage", summary.language);
    setText("#finalUrl", data.finalUrl);
    setText("#analysisDate", formatDate(data.analyzedAt));

    const badge = $("#httpBadge");
    const status = Number(data.httpStatus);

    badge.textContent = status ? `HTTP ${status}` : "HTTP —";
    badge.classList.toggle("success", status >= 200 && status < 400);
    badge.classList.toggle("error", status >= 400 || !status);

    renderColors(design.colors);
    renderFonts(design.typography);
    renderFontSizes(design.typography);
    renderCSSVariables(design.cssVariables);

    renderHeadings(structure.headings);
    renderElements(structure.elements);
    renderFrameworks(structure.frameworkHints);
    renderAltImages(
        structure.imagesWithoutAltExamples,
        seo.imagesWithoutAlt
    );

    renderSEO(seo);
    renderOpenGraph(seo.openGraph);
    renderResponsive(data.responsive);
    renderMediaQueries(structure.mediaQueries);
    renderNotes(data.notes);
}

// ============================================================
// COLORES
// ============================================================

function renderColors(colors) {
    const items = getArray(colors);
    const palette = $("#colorPalette");

    setText("#colorCount", `${items.length} colores`);
    $("#copyAllColors").disabled = !items.length;
    $("#copyColorsStatus").textContent = "";

    if (!items.length) {
        palette.innerHTML = emptyMessage("No se detectaron colores.");
        return;
    }

    palette.innerHTML = items.map((item) => {
        const color = String(item.value || "");
        const safeColor = /^#[\da-f]{3,8}$/i.test(color) ||
            /^rgba?\([\d\s.,%]+\)$/i.test(color);

        return `
            <div class="color-card">
                <button
                    class="color-swatch"
                    type="button"
                    style="background-color:${safeColor ? color : "#252d40"}"
                    data-color="${escapeHTML(color)}"
                    aria-label="Copiar color ${escapeHTML(color)}"
                    title="Haz clic para copiar ${escapeHTML(color)}"
                ></button>
                <code class="color-code">${escapeHTML(color)}</code>
                <span class="color-usage">
                    ${formatNumber(item.count)} usos
                </span>
            </div>
        `;
    }).join("");

    palette.querySelectorAll("[data-color]").forEach((button) => {
        button.addEventListener("click", async () => {
            const color = button.dataset.color;

            try {
                await copyText(color);
                button.title = "¡Color copiado!";
            } catch {
                button.title = color;
            }
        });
    });
}

// Copia la lista completa, sin el límite de la paleta del backend anterior.
async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            return;
        } catch (_) { /* Se intenta la alternativa local. */ }
    }
    const field = document.createElement("textarea");
    field.value = text;
    field.style.cssText = "position:fixed;opacity:0;pointer-events:none";
    document.body.appendChild(field);
    const previous = document.activeElement;
    try {
        field.select();
        if (!document.execCommand("copy")) throw new Error("No se pudo copiar");
    } finally {
        field.remove();
        previous?.focus();
    }
}

function colorsAsRGB(colors) {
    // Canvas convierte también colores CSS modernos (lab, oklch, color) a sRGB.
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 1;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    return [...new Set(getArray(colors).map(item => {
        const value = String(item.value || "").trim();
        if (!value || !CSS.supports("color", value)) return null;
        context.clearRect(0, 0, 1, 1);
        context.fillStyle = value;
        context.fillRect(0, 0, 1, 1);
        const [r, g, b] = context.getImageData(0, 0, 1, 1).data;
        return `rgb(${r}, ${g}, ${b})`;
    }).filter(Boolean))].join(", ");
}

$("#copyAllColors").addEventListener("click", async () => {
    const status = $("#copyColorsStatus");
    const text = colorsAsRGB(getObject(lastAnalysis?.design).colors);
    if (!text) {
        status.textContent = "No hay colores disponibles para copiar.";
        return;
    }
    try {
        await copyText(text);
        status.textContent = "Colores copiados.";
    } catch {
        status.textContent = "No se pudo copiar. Inténtalo nuevamente.";
    }
});

// ============================================================
// TIPOGRAFIAS
// ============================================================

function renderFonts(typography) {
    const fonts = getArray(getObject(typography).fontFamilies);

    if (!fonts.length) {
        setHTML("#fontList", emptyMessage("No se detectaron tipografías."));
        return;
    }

    setHTML("#fontList", fonts.map((font) => `
        <div class="font-item">
            <span
                class="font-name"
                style="font-family:${escapeHTML(font.value)}"
            >${escapeHTML(font.value)}</span>
            <span class="font-count">${formatNumber(font.count)} usos</span>
        </div>
    `).join(""));
}

function renderFontSizes(typography) {
    const sizes = getArray(getObject(typography).fontSizes);
    const max = Math.max(1, ...sizes.map(item => Number(item.count) || 0));

    if (!sizes.length) {
        setHTML("#fontSizeList", emptyMessage("No hay tamaños disponibles."));
        return;
    }

    setHTML("#fontSizeList", sizes.map((item) => {
        const count = Number(item.count) || 0;
        const width = Math.min(100, (count / max) * 100);

        return `
            <div class="bar-item">
                <span class="bar-label">${escapeHTML(item.value)}</span>
                <span class="bar-value">${formatNumber(count)}</span>
                <div class="bar-track">
                    <div class="bar-fill" style="width:${width}%"></div>
                </div>
            </div>
        `;
    }).join(""));
}

// ============================================================
// VARIABLES CSS
// ============================================================

function renderCSSVariables(variables) {
    const entries = Object.entries(getObject(variables));

    if (!entries.length) {
        setHTML(
            "#cssVariables",
            emptyMessage("No se encontraron variables CSS accesibles.")
        );
        return;
    }

    setHTML("#cssVariables", entries.map(([name, value]) => `
        <div class="code-row">
            <code>${escapeHTML(name)}</code>
            <span>${escapeHTML(value)}</span>
        </div>
    `).join(""));
}

// ============================================================
// ESTRUCTURA HTML
// ============================================================

function renderHeadings(headings) {
    const items = getArray(headings);

    if (!items.length) {
        setHTML("#headingList", emptyMessage("No hay encabezados."));
        return;
    }

    setHTML("#headingList", items.map((heading) => `
        <div class="heading-row">
            <span class="heading-level">${escapeHTML(heading.tag)}</span>
            <span class="heading-text">
                ${escapeHTML(heading.text || "(Sin texto)")}
            </span>
        </div>
    `).join(""));
}

function renderElements(elements) {
    const data = getObject(elements);

    const labels = {
        totalVisible: "Elementos visibles",
        links: "Enlaces",
        images: "Imágenes",
        imagesWithoutAlt: "Imágenes sin alt",
        buttons: "Botones",
        forms: "Formularios",
        inputs: "Campos de entrada",
        iframes: "Iframes",
        videos: "Vídeos"
    };

    const entries = Object.entries(labels);

    setHTML("#elementList", entries.map(([key, label]) => `
        <div class="element-row">
            <span>${escapeHTML(label)}</span>
            <strong>${formatNumber(data[key] ?? 0)}</strong>
        </div>
    `).join(""));
}

function renderFrameworks(frameworks) {
    const items = getArray(frameworks);

    setHTML("#frameworkList", items.length
        ? items.map(item => `
            <span class="tag">${escapeHTML(item)}</span>
        `).join("")
        : emptyMessage("No se detectaron indicios conocidos."));
}

function renderAltImages(images, total) {
    const items = getArray(images);

    setText("#altCount", `${formatNumber(total)} imágenes`);

    setHTML("#altImageList", items.length
        ? items.map((url) => `
            <div class="simple-row">
                <span class="seo-value">${escapeHTML(url)}</span>
            </div>
        `).join("")
        : emptyMessage(
            Number(total) > 0
                ? `Se detectaron ${total} imágenes sin alt. La lista de ejemplos está vacía.`
                : "No se detectaron imágenes sin texto alternativo."
        ));
}

// ============================================================
// SEO Y OPEN GRAPH
// ============================================================

function renderSEO(seo) {
    const fields = [
        ["Título", seo.title],
        ["Meta description", seo.metaDescription],
        ["Robots", seo.robots],
        ["Canonical", seo.canonical],
        ["Viewport", seo.viewportMeta],
        ["Codificación", seo.charset],
        ["Imágenes sin alt", seo.imagesWithoutAlt]
    ];

    setHTML("#seoList", fields.map(([label, value]) => {
        const empty = value === null || value === undefined || value === "";

        return `
            <div class="seo-row">
                <span class="seo-key">${escapeHTML(label)}</span>
                <span class="seo-value ${empty ? "empty" : ""}">
                    ${escapeHTML(displayValue(value))}
                </span>
            </div>
        `;
    }).join(""));
}

function renderOpenGraph(openGraph) {
    const data = getObject(openGraph);

    const labels = {
        title: "og:title",
        description: "og:description",
        image: "og:image",
        type: "og:type"
    };

    setHTML("#openGraphList", Object.entries(labels).map(([key, label]) => {
        const value = data[key];
        const empty = value === null || value === undefined || value === "";

        return `
            <div class="seo-row">
                <span class="seo-key">${escapeHTML(label)}</span>
                <span class="seo-value ${empty ? "empty" : ""}">
                    ${escapeHTML(displayValue(value))}
                </span>
            </div>
        `;
    }).join(""));
}

// ============================================================
// RESPONSIVE
// ============================================================

function renderResponsive(responsive) {
    const items = getArray(responsive);

    if (!items.length) {
        setHTML(
            "#responsiveGrid",
            emptyMessage("No hay resultados responsive disponibles.")
        );
        return;
    }

    const icons = {
        mobile: "▯",
        tablet: "▤",
        desktop: "▱"
    };

    setHTML("#responsiveGrid", items.map((item) => {
        const hasError = Boolean(item.error);
        const overflow = item.horizontalOverflow === true;

        const statusClass = hasError
            ? "error"
            : overflow
                ? "warning"
                : "success";

        const statusText = hasError
            ? "No se pudo comprobar"
            : overflow
                ? "Posible desbordamiento"
                : "Sin desbordamiento horizontal";

        return `
            <article class="responsive-card">
                <div class="device-icon">
                    ${icons[item.name] || "▣"}
                </div>
                <h3>${escapeHTML(item.name || "Dispositivo")}</h3>
                <div class="device-width">
                    ${formatNumber(item.width)} × ${formatNumber(item.height)} px
                </div>
                <div class="responsive-status ${statusClass}">
                    ${escapeHTML(statusText)}
                </div>
                <div class="responsive-metrics">
                    ${hasError
                        ? `<span>${escapeHTML(item.error)}</span>`
                        : `
                            <span>Viewport: ${formatNumber(item.viewportWidth)} px</span>
                            <span>Ancho del documento: ${formatNumber(item.documentWidth)} px</span>
                            <span>Meta viewport: ${item.hasViewportMeta ? "Sí" : "No"}</span>
                        `
                    }
                </div>
            </article>
        `;
    }).join(""));
}

function renderMediaQueries(queries) {
    const items = getArray(queries);

    setHTML("#mediaQueryList", items.length
        ? items.map(query => `
            <span class="tag">${escapeHTML(query)}</span>
        `).join("")
        : emptyMessage("No se encontraron media queries accesibles."));
}

// ============================================================
// NOTAS
// ============================================================

function renderNotes(notes) {
    const items = getArray(notes);

    $("#analysisNotes").innerHTML = items.length
        ? items.map(note => `<li>${escapeHTML(note)}</li>`).join("")
        : "<li>No hay notas adicionales.</li>";
}

// ============================================================
// EXPORTAR JSON
// ============================================================

downloadButton.addEventListener("click", () => {
    if (!lastAnalysis) return;

    const blob = new Blob(
        [JSON.stringify(lastAnalysis, null, 2)],
        { type: "application/json;charset=utf-8" }
    );

    const objectURL = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectURL;
    link.download = "webscraping-analysis.json";

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(objectURL);
});

// ============================================================
// NAVEGACION Y ARRANQUE
// ============================================================

$("#footerYear").textContent = new Date().getFullYear();

document.querySelectorAll(".nav-item").forEach((link) => {
    link.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(item => {
            item.classList.remove("active");
        });

        link.classList.add("active");
    });
});

checkAPI();
