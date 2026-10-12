
from __future__ import annotations

import asyncio
import ipaddress
import socket
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


# ============================================================
# CONFIGURACION DE LA API
# ============================================================

app = FastAPI(
    title="WebScraping API",
    description="Analiza el diseño, estructura y SEO de páginas web.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Solo para desarrollo local
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIEWPORTS = [
    {"name": "mobile", "width": 375, "height": 812},
    {"name": "tablet", "width": 768, "height": 1024},
    {"name": "desktop", "width": 1440, "height": 900},
]


class AnalyzeRequest(BaseModel):
    url: HttpUrl


# ============================================================
# VALIDACION DE URL
# ============================================================

def validate_public_url(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten URLs HTTP o HTTPS.",
        )

    if not parsed.hostname:
        raise HTTPException(
            status_code=400,
            detail="La URL no contiene un dominio valido.",
        )

    if parsed.username or parsed.password:
        raise HTTPException(
            status_code=400,
            detail="No se permiten credenciales dentro de la URL.",
        )

    host = parsed.hostname.lower()

    if host in ("localhost", "localhost.localdomain"):
        raise HTTPException(
            status_code=400,
            detail="No se permiten direcciones locales.",
        )

    try:
        addresses = socket.getaddrinfo(
            host,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror:
        raise HTTPException(
            status_code=400,
            detail="No se pudo resolver el dominio.",
        )

    if not addresses:
        raise HTTPException(
            status_code=400,
            detail="El dominio no tiene direcciones IP.",
        )

    for address in addresses:
        ip_text = address[4][0].split("%")[0]
        ip = ipaddress.ip_address(ip_text)

        if not ip.is_global:
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten direcciones IP publicas.",
            )


# ============================================================
# ANALISIS DEL DOM Y LOS ESTILOS
# ============================================================

async def inspect_page(page) -> dict:
    return await page.evaluate(
        """() => {
            const isVisible = (el) => {
                const rect = el.getBoundingClientRect();
                const style = getComputedStyle(el);

                return rect.width > 0 &&
                       rect.height > 0 &&
                       style.display !== "none" &&
                       style.visibility !== "hidden" &&
                       Number(style.opacity) !== 0;
            };

            const elements = [
                ...document.querySelectorAll("body *")
            ].filter(isVisible);

            const frequency = (values, limit = 20) => {
                const counts = new Map();

                for (const value of values) {
                    if (!value) continue;
                    counts.set(
                        value,
                        (counts.get(value) || 0) + 1
                    );
                }

                return [...counts.entries()]
                    .map(([value, count]) => ({ value, count }))
                    .sort((a, b) => b.count - a.count)
                    .slice(0, limit);
            };

            const css = (el, property) =>
                getComputedStyle(el).getPropertyValue(property).trim();

            const normalizeColor = (color) => {
                if (!color) return null;

                const value = color.trim().toLowerCase();

                if (
                    value === "transparent" ||
                    value === "rgba(0, 0, 0, 0)"
                ) {
                    return null;
                }

                return value;
            };

            // Colores observados en los elementos visibles.
            const colors = frequency(
                elements.flatMap(el => [
                    normalizeColor(css(el, "color")),
                    normalizeColor(css(el, "background-color")),
                    normalizeColor(css(el, "border-top-color"))
                ])
            );

            const backgrounds = frequency(
                elements.map(el =>
                    normalizeColor(css(el, "background-color"))
                ).filter(Boolean),
                15
            );

            // Tipografias y tamaños.
            const fonts = frequency(
                elements.map(el => css(el, "font-family")),
                12
            );

            const fontSizes = frequency(
                elements.map(el => css(el, "font-size")),
                15
            );

            const fontWeights = frequency(
                elements.map(el => css(el, "font-weight")),
                10
            );

            // Encabezados.
            const headings = [
                ...document.querySelectorAll(
                    "h1, h2, h3, h4, h5, h6"
                )
            ].filter(isVisible).slice(0, 50).map(el => ({
                tag: el.tagName.toLowerCase(),
                text: (el.innerText || "").trim().slice(0, 250)
            }));

            // Botones y controles similares.
            const buttons = [
                ...document.querySelectorAll(
                    'button, [role="button"], ' +
                    'input[type="button"], input[type="submit"]'
                )
            ].filter(isVisible).slice(0, 60).map(el => ({
                tag: el.tagName.toLowerCase(),
                text: (
                    el.innerText ||
                    el.getAttribute("aria-label") ||
                    el.value ||
                    ""
                ).trim().slice(0, 150),
                background: css(el, "background-color"),
                color: css(el, "color"),
                borderRadius: css(el, "border-radius"),
                fontSize: css(el, "font-size"),
                fontFamily: css(el, "font-family"),
                padding: css(el, "padding"),
                border: css(el, "border")
            }));

            const links = [
                ...document.querySelectorAll("a")
            ].filter(isVisible);

            const images = [
                ...document.querySelectorAll("img")
            ].filter(isVisible);

            const imagesWithoutAlt = images.filter(
                img => !img.hasAttribute("alt") || !img.alt.trim()
            );

            // Variables CSS accesibles.
            const cssVariables = {};

            for (const sheet of [...document.styleSheets]) {
                try {
                    for (const rule of [...sheet.cssRules]) {
                        if (
                            rule.selectorText === ":root" ||
                            rule.selectorText === "html"
                        ) {
                            for (const name of [...rule.style]) {
                                if (
                                    name.startsWith("--") &&
                                    cssVariables[name] === undefined
                                ) {
                                    cssVariables[name] =
                                        rule.style.getPropertyValue(name).trim();
                                }
                            }
                        }
                    }
                } catch (_) {
                    // Las hojas de otro origen pueden ser inaccesibles.
                }
            }

            // Media queries disponibles.
            const mediaQueries = new Set();

            const readRules = (rules) => {
                for (const rule of [...rules]) {
                    if (rule.conditionText && rule.media) {
                        mediaQueries.add(rule.conditionText);
                    }

                    if (rule.cssRules) {
                        readRules(rule.cssRules);
                    }
                }
            };

            for (const sheet of [...document.styleSheets]) {
                try {
                    readRules(sheet.cssRules);
                } catch (_) {
                    // Se omiten hojas no accesibles.
                }
            }

            // Indicadores heurísticos de frameworks.
            const frameworks = [];

            if (
                document.querySelector("[data-reactroot], #__next")
            ) {
                frameworks.push("React / Next.js (indicativo)");
            }

            if (document.querySelector("[ng-version]")) {
                frameworks.push("Angular (indicativo)");
            }

            if (document.querySelector("[data-v-app]")) {
                frameworks.push("Vue (indicativo)");
            }

            if (document.querySelector("[data-svelte-h]")) {
                frameworks.push("Svelte (indicativo)");
            }

            const meta = name =>
                document.querySelector(
                    `meta[name="${name}"]`
                )?.content || null;

            const og = property =>
                document.querySelector(
                    `meta[property="og:${property}"]`
                )?.content || null;

            return {
                title: document.title || null,
                language: document.documentElement.lang || null,
                description: meta("description"),
                robots: meta("robots"),
                canonical:
                    document.querySelector(
                        'link[rel="canonical"]'
                    )?.href || null,
                viewportMeta: meta("viewport"),
                charset: document.characterSet || null,

                headings,
                colors,
                backgrounds,
                fonts,
                fontSizes,
                fontWeights,
                cssVariables:
                    Object.fromEntries(
                        Object.entries(cssVariables).slice(0, 100)
                    ),
                mediaQueries: [...mediaQueries].slice(0, 100),

                buttons,

                elements: {
                    totalVisible: elements.length,
                    links: links.length,
                    images: images.length,
                    imagesWithoutAlt: imagesWithoutAlt.length,
                    buttons: buttons.length,
                    forms: document.forms.length,
                    inputs: document.querySelectorAll(
                        "input, textarea, select"
                    ).length,
                    iframes: document.querySelectorAll("iframe").length,
                    videos: document.querySelectorAll("video").length
                },

                imagesWithoutAltExamples: imagesWithoutAlt
                    .slice(0, 20)
                    .map(img => img.currentSrc || img.src),

                frameworks,

                openGraph: {
                    title: og("title"),
                    description: og("description"),
                    image: og("image"),
                    type: og("type")
                },

                textLength: document.body?.innerText.length || 0,
                pageWidth: document.documentElement.scrollWidth,
                pageHeight: document.documentElement.scrollHeight
            };
        }"""
    )


# ============================================================
# PRUEBAS RESPONSIVE
# ============================================================

async def inspect_responsive(page, url: str) -> list:
    results = []

    for viewport in VIEWPORTS:
        await page.set_viewport_size({
            "width": viewport["width"],
            "height": viewport["height"],
        })

        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=20000,
            )

            await page.wait_for_timeout(300)

            result = await page.evaluate(
                """() => ({
                    viewportWidth: window.innerWidth,
                    documentWidth: document.documentElement.scrollWidth,
                    horizontalOverflow:
                        document.documentElement.scrollWidth >
                        window.innerWidth + 1,
                    hasViewportMeta: !!document.querySelector(
                        'meta[name="viewport"]'
                    )
                })"""
            )

            results.append({
                "name": viewport["name"],
                "width": viewport["width"],
                "height": viewport["height"],
                **result,
            })

        except PlaywrightTimeoutError:
            results.append({
                "name": viewport["name"],
                "width": viewport["width"],
                "height": viewport["height"],
                "error": "Tiempo de espera agotado.",
            })

    return results


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    return {
        "service": "WebScraping API",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "WebScraping API",
    }


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    url = str(request.url)

    # La comprobacion DNS se ejecuta fuera del event loop.
    await asyncio.to_thread(validate_public_url, url)

    browser = None

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True
            )

            context = await browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent="WebScrapingAnalyzer/1.0",
            )

            page = await context.new_page()

            try:
                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000,
                )

                try:
                    await page.wait_for_load_state(
                        "networkidle",
                        timeout=5000,
                    )
                except PlaywrightTimeoutError:
                    pass

                await page.wait_for_timeout(300)

                status_code = response.status if response else None
                final_url = page.url

                page_data = await inspect_page(page)

                responsive = await inspect_responsive(
                    page,
                    final_url,
                )

            finally:
                await context.close()

    except HTTPException:
        raise

    except PlaywrightTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="La pagina tardo demasiado en responder.",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "No se pudo analizar la pagina. "
                f"{type(exc).__name__}: {str(exc)[:250]}"
            ),
        )

    finally:
        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass

    # Estimacion orientativa del color mas frecuente.
    primary_color = next(
        (
            item["value"]
            for item in page_data["colors"]
            if item["value"].startswith("#")
            or item["value"].startswith("rgb(")
        ),
        None,
    )

    # JSON de respuesta. No se guarda en una base de datos.
    return {
        "success": True,
        "requestedUrl": url,
        "finalUrl": final_url,
        "httpStatus": status_code,
        "analyzedAt": datetime.now(timezone.utc).isoformat(),

        "summary": {
            "title": page_data["title"],
            "language": page_data["language"],
            "visibleElements": page_data["elements"]["totalVisible"],
            "images": page_data["elements"]["images"],
            "buttons": page_data["elements"]["buttons"],
            "links": page_data["elements"]["links"],
            "primaryColorEstimate": primary_color,
            "responsiveViewportsChecked": len(responsive),
        },

        "design": {
            "colors": page_data["colors"],
            "backgroundColors": page_data["backgrounds"],
            "typography": {
                "fontFamilies": page_data["fonts"],
                "fontSizes": page_data["fontSizes"],
                "fontWeights": page_data["fontWeights"],
            },
            "cssVariables": page_data["cssVariables"],
            "buttons": page_data["buttons"],
        },

        "structure": {
            "headings": page_data["headings"],
            "elements": page_data["elements"],
            "imagesWithoutAltExamples":
                page_data["imagesWithoutAltExamples"],
            "frameworkHints": page_data["frameworks"],
            "mediaQueries": page_data["mediaQueries"],
        },

        "seo": {
            "title": page_data["title"],
            "metaDescription": page_data["description"],
            "robots": page_data["robots"],
            "canonical": page_data["canonical"],
            "viewportMeta": page_data["viewportMeta"],
            "charset": page_data["charset"],
            "openGraph": page_data["openGraph"],
            "imagesWithoutAlt":
                page_data["elements"]["imagesWithoutAlt"],
        },

        "responsive": responsive,

        "notes": [
            "Los resultados son estimaciones basadas en el DOM y los estilos accesibles.",
            "La deteccion de frameworks es heuristica y no una confirmacion.",
            "No se prueban exhaustivamente los estados hover, focus y active.",
            "Los resultados no se guardan en una base de datos.",
        ],
    }
