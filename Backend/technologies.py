"""Detección heurística a partir de señales públicas, sin peticiones adicionales."""
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def detect_technologies(html: str, headers: dict, resource_urls: list[str]) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    headers = {key.lower(): value for key, value in headers.items()}
    resources = set(resource_urls)
    resources.update(tag.get("src", "") for tag in soup.select("script[src], iframe[src]"))
    resources.update(tag.get("href", "") for tag in soup.select('link[rel="stylesheet"]'))
    # No se usan textos visibles ni URLs completas como firmas: evitan coincidencias
    # con artículos que mencionan tecnologías y no exponen tokens de las URLs.
    paths = [urlparse(url).path.lower() for url in resources if url]
    hosts = [urlparse(url).hostname or "" for url in resources if url]
    findings = {}

    def add(name, category, evidence, confidence="alta"):
        item = findings.setdefault(name, {
            "name": name, "category": category,
            "confidence": confidence, "evidence": [],
        })
        if confidence == "alta":
            item["confidence"] = "alta"
        if evidence not in item["evidence"]:
            item["evidence"].append(evidence)

    dom_rules = [
        ("Next.js", "Framework", "#__next, script#__NEXT_DATA__"),
        ("React", "Biblioteca", "[data-reactroot]"),
        ("Angular", "Framework", "[ng-version]"),
        ("Vue.js", "Framework", "[data-v-app]"),
        ("Nuxt", "Framework", "#__nuxt, script#__NUXT_DATA__"),
        ("Svelte", "Framework", "[data-svelte-h]"),
        ("Astro", "Framework", "astro-island"),
        ("Webflow", "CMS / Constructor", "html[data-wf-site]"),
    ]
    for name, category, selector in dom_rules:
        if soup.select_one(selector):
            add(name, category, "Marcador DOM: " + selector)

    path_rules = [
        ("Next.js", "Framework", r"/_next/"),
        ("Nuxt", "Framework", r"/_nuxt/"),
        ("WordPress", "CMS / Constructor", r"/wp-(?:content|includes)/"),
        ("WooCommerce", "Comercio electrónico", r"/plugins/woocommerce/"),
        ("Drupal", "CMS / Constructor", r"/sites/(?:default|all)/"),
        ("jQuery", "Biblioteca", r"(?:^|/)jquery(?:[-.][0-9][\w.-]*)?(?:\.min)?\.js$"),
        ("Bootstrap", "Estilos / UI", r"(?:^|/)bootstrap(?:\.bundle)?(?:\.min)?\.(?:css|js)$"),
        ("Tailwind CSS", "Estilos / UI", r"(?:^|/)tailwind(?:\.min)?\.css$"),
        ("React", "Biblioteca", r"(?:^|/)react(?:-dom)?(?:\.production)?(?:\.min)?\.js$"),
        ("Vue.js", "Framework", r"(?:^|/)vue(?:\.runtime)?(?:\.global)?(?:\.prod)?(?:\.min)?\.js$"),
    ]
    for name, category, pattern in path_rules:
        if any(re.search(pattern, path) for path in paths):
            add(name, category, "Ruta de recurso característica", "media")

    host_rules = [
        ("Google Analytics", "Analítica", "google-analytics.com"),
        ("Google Tag Manager", "Gestión de etiquetas", "googletagmanager.com"),
        ("Hotjar", "Analítica", "hotjar.com"),
        ("Microsoft Clarity", "Analítica", "clarity.ms"),
        ("Shopify", "Comercio electrónico", "cdn.shopify.com"),
        ("Wix", "CMS / Constructor", "wixstatic.com"),
        ("Squarespace", "CMS / Constructor", "squarespace.com"),
        ("Stripe", "Pagos", "js.stripe.com"),
        ("Google Fonts", "Tipografías", "fonts.googleapis.com"),
        ("Tailwind CSS", "Estilos / UI", "cdn.tailwindcss.com"),
    ]
    for name, category, domain in host_rules:
        if any(host == domain or host.endswith("." + domain) for host in hosts):
            add(name, category, "Recurso del dominio: " + domain)

    for tag in soup.select('meta[name="generator" i]'):
        generator = tag.get("content", "")
        for name in ("WordPress", "Drupal", "Joomla", "Hugo", "Gatsby", "Astro", "Wix", "Webflow"):
            if re.search(r"\b" + re.escape(name) + r"\b", generator, re.I):
                add(name, "CMS / Constructor", "Metadato generator: " + name)

    for header, signatures in {
        "server": [("nginx", "Nginx"), ("apache", "Apache"), ("cloudflare", "Cloudflare"), ("microsoft-iis", "Microsoft IIS")],
        "x-powered-by": [("php", "PHP"), ("express", "Express"), ("asp.net", "ASP.NET"), ("next.js", "Next.js")],
    }.items():
        for signature, name in signatures:
            if re.search(r"(?<![a-z0-9])" + re.escape(signature) + r"(?![a-z0-9])", headers.get(header, ""), re.I):
                add(name, "Servidor / Infraestructura", "Cabecera " + header, "media")
    if "cf-ray" in headers:
        add("Cloudflare", "Servidor / Infraestructura", "Cabecera cf-ray")
    if "x-vercel-id" in headers:
        add("Vercel", "Servidor / Infraestructura", "Cabecera x-vercel-id")

    items = sorted(findings.values(), key=lambda item: (item["category"], item["name"]))
    return {
        "items": items,
        "total": len(items),
        "notice": "Detección heurística basada en señales públicas. La confianza expresa la fuerza del indicio, no una confirmación. No permite identificar toda la infraestructura ni la base de datos.",
    }
