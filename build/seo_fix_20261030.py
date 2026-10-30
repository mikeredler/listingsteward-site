#!/usr/bin/env python3
"""Oct 30 2026 SEO pass (Marketo audit). Idempotent-ish: run once on 6eb66de."""
import json, re, html, os, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
os.chdir(R)
SITE = "https://listingsteward.com"
C149 = "https://buy.stripe.com/fZu4gygLT5T49jG8GA4Ja00"
C199 = "https://buy.stripe.com/3cI6oG67f6X853q9KE4Ja01"
ADDR = {"@type": "PostalAddress", "streetAddress": "867 Boylston Street, 5th Floor #1586",
        "addressLocality": "Boston", "addressRegion": "MA", "postalCode": "02116", "addressCountry": "US"}
def grader(slug): return f"{SITE}/grader/?utm_source=google&utm_medium=organic&utm_campaign=seo_listingsteward&utm_content={slug}"
ORG = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "ListingSteward", "url": f"{SITE}/",
       "logo": f"{SITE}/assets/logo-512.png", "address": ADDR, "email": "lorenzo@listingsteward.com",
       "contactPoint": {"@type": "ContactPoint", "contactType": "sales", "email": "lorenzo@listingsteward.com", "areaServed": "US"}}
AREA = [{"@type": "State", "name": "Massachusetts"}, {"@type": "City", "name": "Boston"}, {"@type": "City", "name": "Worcester"}]
OFFERS = [{"@type": "Offer", "name": "Profile Cleanup & Audit", "price": "149", "priceCurrency": "USD", "url": C149},
          {"@type": "Offer", "name": "Monthly Management", "price": "199", "priceCurrency": "USD", "url": C199,
           "priceSpecification": {"@type": "UnitPriceSpecification", "price": "199", "priceCurrency": "USD", "unitText": "MONTH", "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitText": "location"}}}]
BIZ = {"@type": "ProfessionalService", "@id": f"{SITE}/#biz", "name": "ListingSteward", "url": f"{SITE}/",
       "description": "Google Business Profile management for Massachusetts plumbers, HVAC companies, roofers and electricians: weekly posts, replies to every review within 24 hours, and a plain-English monthly report.",
       "image": f"{SITE}/assets/og-image.png", "logo": f"{SITE}/assets/logo-512.png", "email": "lorenzo@listingsteward.com",
       "address": ADDR, "areaServed": AREA, "priceRange": "$149-$199/mo", "makesOffer": OFFERS,
       "parentOrganization": {"@id": f"{SITE}/#org"}}
def service(name, area=None):
    return {"@type": "Service", "name": name, "serviceType": "Google Business Profile management",
            "provider": {"@id": f"{SITE}/#biz"}, "areaServed": area or AREA,
            "audience": {"@type": "BusinessAudience", "audienceType": "Local trades: plumbers, HVAC companies, roofers and electricians"},
            "offers": OFFERS}
def faq_ld(qs): return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qs]}
def faq_html(qs): return '<section class="faq" aria-labelledby="fq"><div class="w"><h2 id="fq">Questions, answered</h2>' + "".join(f"<details><summary><h3>{html.escape(q, False)}</h3></summary><p>{html.escape(a, False)}</p></details>" for q, a in qs) + "</div></section>"
def crumbs(name, path): return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"}, {"@type": "ListItem", "position": 2, "name": name, "item": f"{SITE}{path}"}]}
def ld(graph): return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")) + "</script>"
LD_RE = re.compile(r'<script type="application/ld\+json">.*?</script>', re.S)

def set_meta(s, title=None, desc=None):
    if desc:
        assert len(desc) <= 155, (len(desc), desc)
        e = html.escape(desc, True)
        s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + e + m.group(2), s)
        s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + e + m.group(2), s)
        s = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + e + m.group(2), s)
    if title:
        e = html.escape(title, False)
        s = re.sub(r'<title>[^<]*</title>', f'<title>{e}</title>', s)
        s = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + e + m.group(2), s)
        s = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + e + m.group(2), s)
    return s

HOME_FAQ = [
 ("Do you need my Google password?", "No. You add ListingSteward as a Manager on your Business Profile. You stay the owner and can remove us anytime."),
 ("Do you guarantee a #1 ranking?", "No, and nobody honestly can. We guarantee the work: accurate info, weekly posts, and every review answered within 24 hours."),
 ("Do you write or buy reviews?", "Never. Fake reviews break Google's policies and can get a listing suspended. We help you ask real customers."),
 ("How fast will I see changes?", "The Cleanup is finished within 5 business days. Calls and direction requests are tracked in your monthly report."),
 ("Can I cancel?", "Yes, anytime and with no fees. Your profile stays exactly as we left it.")]

NEWLINKS = '<a href="/google-business-profile-cleanup/">$149 profile cleanup</a><a href="/google-business-profile-management-boston/">Boston, MA</a><a href="/google-business-profile-management-worcester/">Worcester, MA</a>'
def footer_links(s):
    i = s.find("<footer")
    if i < 0 or 'worcester/">Worcester, MA' in s[i:]: return s
    return s[:i] + s[i:].replace('<a href="/google-business-profile-management-boston/">Boston, MA</a>', NEWLINKS, 1)

# ---------- home ----------
p = pathlib.Path("index.html"); s = p.read_text()
s = set_meta(s, "Google Business Profile Management for MA Trades | ListingSteward",
             "Google Business Profile management for Massachusetts plumbers, HVAC, roofers and electricians. $149 cleanup or $199/mo. No contract, you keep ownership.")
s = LD_RE.sub(lambda m: ld([ORG, BIZ, service("Google Business Profile Management"), faq_ld(HOME_FAQ),
    {"@type": "WebSite", "@id": f"{SITE}/#website", "name": "ListingSteward", "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}}]), s, 1)
s = s.replace('<p class="eyebrow">Google Business Profile management</p>\n<h1>Turn your Google listing into your <span class="grad">best salesperson.</span></h1>',
              '<h1>Google Business Profile management for <span class="grad">Massachusetts trades</span></h1>\n<p class="eyebrow">Turn your Google listing into your best salesperson.</p>')
s = s.replace('<p class="micro">No contract · You keep ownership · Live in 5 business days</p>',
              '<p class="micro">No contract · You keep ownership · Live in 5 business days</p>\n<p class="micro">Serving plumbers, HVAC companies, roofers and electricians across Massachusetts, including <a href="/google-business-profile-management-boston/">Boston</a> and <a href="/google-business-profile-management-worcester/">Worcester</a>. <a href="/google-business-profile-cleanup/">What the $149 cleanup fixes</a>.</p>', 1)
s = footer_links(s); p.write_text(s)

# ---------- grader ----------
GRADER_FAQ = [
 ("Is the Google Business Profile grader free?", "Yes. It takes about 2 minutes, there's no signup, and nothing is sent anywhere unless you choose to email us."),
 ("How is my score worked out?", "You answer 12 yes/no questions about your listing, such as categories, hours, services, photos, posts and review replies. Each answer is weighted, and you get a score out of 100 plus your top 3 fixes."),
 ("Is the grader score the same as your free audit?", "No. The grader is a self-check, so the score depends on your answers. Our free 1-page audit checks your real listing against your top 3 local competitors. Email lorenzo@listingsteward.com your business name and town."),
 ("What if my score is low?", "Start with the top 3 fixes it shows you. If you'd rather we do it, the $149 Profile Cleanup & Audit is finished within 5 business days, and you keep ownership of your profile."),
 ("Do you need my Google password?", "No. You add ListingSteward as a Manager on your Business Profile. You stay the owner and can remove us anytime.")]
p = pathlib.Path("grader/index.html"); s = p.read_text()
WEBAPP = {"@type": "WebApplication", "name": "ListingSteward Google Listing Grader", "url": f"{SITE}/grader/", "applicationCategory": "BusinessApplication",
          "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "provider": {"@id": f"{SITE}/#org"}}
s = LD_RE.sub(lambda m: ld([ORG, BIZ, WEBAPP, service("Google Business Profile Management"), faq_ld(GRADER_FAQ), crumbs("Free listing grader", "/grader/")]), s, 1)
s = s.replace('<h1>How strong is your <span class="grad">Google listing?</span></h1>',
              '<h1>Free Google Business Profile grader: how strong is your <span class="grad">Google listing?</span></h1>')
if 'id="fq"' not in s:
    s = s.replace('<section class="close">', faq_html(GRADER_FAQ) + '<section class="close">', 1)
s = footer_links(s); p.write_text(s)

# ---------- meta trims on other indexable pages ----------
TRIMS = {
 "google-business-profile-management-boston": "Boston plumbers, HVAC, roofers and electricians: we clean up and manage your Google Business Profile. $149 cleanup or $199/mo. No contract.",
 "google-business-profile-management-plumbers": "Plumbers: fix what's costing you calls on Google Maps. Categories, emergency hours and review replies done for you. $149 cleanup or $199/mo. MA.",
 "google-business-profile-management-hvac": "HVAC companies: fix what's costing you calls on Google Maps. Categories, seasonal posts and review replies done for you. $149 or $199/mo. MA.",
 "google-business-profile-management-roofers": "Roofers: fix what's costing you calls on Google Maps. Categories, photos and review replies done for you. $149 cleanup or $199/mo. Massachusetts.",
 "google-business-profile-management-electricians": "Electricians: fix what's costing you calls on Google Maps. Categories, service area and review replies done for you. $149 cleanup or $199/mo. MA.",
 "google-business-profile-suspended": "Google Business Profile suspended? Common causes, the evidence Google wants, and a reinstatement appeal prepared for a flat $149. No password needed.",
 "partners": "Refer local businesses to ListingSteward's Google Business Profile management and earn 20% of the monthly fee for 12 months.",
}
for d, desc in TRIMS.items():
    p = pathlib.Path(d, "index.html"); s = p.read_text(); s = set_meta(s, desc=desc); s = footer_links(s); p.write_text(s)
for d in ["contact", "privacy", "terms", "thanks"]:
    p = pathlib.Path(d, "index.html")
    if p.exists(): s = p.read_text(); p.write_text(footer_links(s))

# ---------- new pages ----------
home = pathlib.Path("index.html").read_text()
HEADER = home[home.find("<body>"):home.find('<main id="main">')]
FOOTER = home[home.find("</main>") + 7:]
PRICING = home[home.find('<section id="pricing"'):home.find('<section class="faq"')]
STATS = home[home.find('<section class="stats"'):home.find('<section id="how"')]
HOW = home[home.find('<section id="how"'):home.find('<section id="pricing"')]
def head(path, title, desc):
    assert len(desc) <= 155, (len(desc), desc)
    t = html.escape(title, False); d = html.escape(desc, True)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title><meta name="description" content="{d}">
<link rel="canonical" href="{SITE}{path}"><meta name="theme-color" content="#0A0D16">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="/assets/favicon-32.png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/space-grotesk-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
<meta property="og:type" content="website"><meta property="og:site_name" content="ListingSteward"><meta property="og:url" content="{SITE}{path}"><meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:image" content="{SITE}/assets/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="ListingSteward: Google Business Profile management for local businesses">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{SITE}/assets/og-image.png">
'''
def page(path, title, desc, graph, main):
    out = head(path, title, desc) + ld(graph) + "</head>" + HEADER + '<main id="main">' + main + "</main>" + FOOTER
    pathlib.Path(path.strip("/")).mkdir(parents=True, exist_ok=True)
    pathlib.Path(path.strip("/"), "index.html").write_text(out)

def cta(slug, text="Run the free listing grader"):
    return f'<div class="ctas"><a class="btn" href="{grader(slug)}">{text}</a><a class="btn ghost" href="{C149}">Get the $149 Cleanup</a></div>'

# Cleanup page
slug = "google-business-profile-cleanup"
CL_FAQ = [
 ("What does the $149 Google Business Profile cleanup include?", "An audit against your top 3 local competitors; categories, services, hours and description fixed; up to 25 unanswered reviews replied to; 5 FAQs and 2 posts published; and a before/after report within 5 business days."),
 ("How do I give you access to my Google Business Profile?", "You add ListingSteward as a Manager inside your profile. It takes about two minutes. You stay the owner, we never need your Google password, and you can remove us anytime."),
 ("How long does the cleanup take?", "It's finished within 5 business days of you adding us as a Manager."),
 ("What if I want monthly management afterwards?", "Upgrade to Monthly Management ($199/mo per location) within 30 days of your Cleanup and we credit the $149 to your first month. No contract, cancel anytime."),
 ("Can you promise a higher Google ranking?", "No, and nobody honestly can. We commit to the work: an accurate, complete profile and answered reviews."),
 ("Do you write or buy reviews?", "Never. Fake reviews break Google's policies and can get a listing suspended. We help you ask real customers.")]
page(f"/{slug}/", "Google Business Profile Cleanup Service, MA Trades | $149",
     "A $149 Google Business Profile cleanup for Massachusetts trades: categories, services, hours, description, reviews and posts fixed in 5 business days.",
     [ORG, BIZ, {"@type": "Service", "name": "Google Business Profile Cleanup & Audit", "serviceType": "Google Business Profile cleanup",
                 "description": "One-time cleanup of a Google Business Profile: competitor audit, categories, services, hours and description fixed, up to 25 review replies, 5 FAQs, 2 posts and a before/after report within 5 business days.",
                 "provider": {"@id": f"{SITE}/#biz"}, "areaServed": AREA, "url": f"{SITE}/{slug}/",
                 "offers": {"@type": "Offer", "name": "Profile Cleanup & Audit", "price": "149", "priceCurrency": "USD", "url": C149}},
      faq_ld(CL_FAQ), crumbs("Profile cleanup", f"/{slug}/")],
     f'''<section class="hero"><div class="w"><p class="eyebrow">Profile Cleanup &amp; Audit · $149 one-time</p><h1>Google Business Profile cleanup for Massachusetts trades: <span class="grad">$149, done in 5 business days</span></h1>
<p class="lede">If your Google listing has the wrong category, old hours, a thin description or a backlog of unanswered reviews, it's costing you calls. We fix it in one pass, for plumbers, HVAC companies, roofers and electricians across Massachusetts.</p>
{cta(slug)}<p class="micro">No contract · You keep ownership · No Google password needed</p></div></section>
<section><div class="w"><h2>What we fix</h2><ul class="ticks"><li>An audit of your listing against your top 3 local competitors</li><li>Primary and secondary categories set for the services you actually sell</li><li>Services listed in the words customers search</li><li>Regular and holiday hours corrected</li><li>A clear business description: what you do, where, and for whom</li><li>Up to 25 unanswered reviews replied to</li><li>5 FAQs and 2 posts published</li><li>A before/after report when we're done</li></ul></div></section>
<section><div class="w"><h2>How access works</h2><p>You add ListingSteward as a <strong>Manager</strong> on your Business Profile. It takes about two minutes. You stay the owner, we never ask for your Google password, and you can remove us anytime.</p></div></section>
{HOW}
<section><div class="w"><h2>Timeline</h2><ol><li>Check out securely via Stripe (about 60 seconds).</li><li>Add us as a Manager (about 2 minutes).</li><li>We fix your listing and send the before/after report within 5 business days.</li></ol></div></section>
<section><div class="w"><h2>Upgrade within 30 days and the $149 is credited</h2><p>Want us to keep it sharp every week? Move to <a href="/#pricing">Monthly Management</a> ($199/mo per location: a new post every week, every review answered within 24 hours, and a plain-English monthly report) within 30 days of your Cleanup and we credit the $149 to your first month. No contract, cancel anytime.</p></div></section>
<section><div class="w"><h2>What we don't do</h2><ul class="ticks"><li>No ranking promises. Nobody can honestly promise a position on Google.</li><li>We never write or buy reviews. That breaks Google's policies and can get a listing suspended.</li><li>We never invent addresses or create fake locations.</li></ul><p class="note">Profile already suspended? See <a href="/google-business-profile-suspended/">suspended profile help</a>.</p></div></section>
{STATS}{PRICING}{faq_html(CL_FAQ)}
<section class="close"><div class="w"><h2>Not sure what your listing needs?</h2><p>Score it in 2 minutes, free, no signup.</p><a class="btn" href="{grader(slug)}">Run the free listing grader</a></div></section>''')

# Worcester page
slug = "google-business-profile-management-worcester"
WAREA = [{"@type": "City", "name": "Worcester"}, {"@type": "State", "name": "Massachusetts"}]
W_FAQ = [
 ("Do you work with businesses in Worcester and Central Massachusetts?", "Yes. We work with plumbers, HVAC companies, roofers and electricians across Massachusetts, including Worcester and the surrounding towns. Everything happens remotely, so there's no need for an in-person visit."),
 ("Can you set my service area to the Worcester-area towns I cover?", "Yes. We set your service area to the places you actually serve. We never invent addresses or create fake locations, because that breaks Google's rules."),
 ("Do you need my Google password?", "No. You add ListingSteward as a Manager on your profile. You stay the owner and can remove us anytime."),
 ("Can you promise a top spot on the Map in Worcester?", "No, and nobody honestly can. We commit to the work: accurate information, weekly posts, and every review answered within 24 hours."),
 ("What does it cost?", "$149 one-time for the Profile Cleanup & Audit, or $199/mo per location for Monthly Management. No contract and no setup fee. Upgrade within 30 days of a Cleanup and the $149 is credited to your first month.")]
page(f"/{slug}/", "Google Business Profile Management in Worcester, MA | $149",
     "Worcester-area plumbers, HVAC, roofers and electricians: we clean up and manage your Google Business Profile. $149 cleanup or $199/mo. No contract.",
     [ORG, {"@type": "ProfessionalService", "@id": f"{SITE}/#biz-worcester", "name": "ListingSteward", "url": f"{SITE}/{slug}/",
            "image": f"{SITE}/assets/og-image.png", "email": "lorenzo@listingsteward.com", "address": ADDR, "areaServed": WAREA,
            "priceRange": "$149-$199/mo", "parentOrganization": {"@id": f"{SITE}/#org"}},
      service("Google Business Profile Management in Worcester", WAREA), faq_ld(W_FAQ), crumbs("Worcester, MA", f"/{slug}/")],
     f'''<section class="hero"><div class="w"><p class="eyebrow">Worcester, MA · Central Massachusetts</p><h1>Google Business Profile management in <span class="grad">Worcester</span></h1>
<p class="lede">When a pipe bursts or the furnace quits in Worcester, people pick from the map in seconds. ListingSteward keeps local trades' Google listings accurate, active and answering, so the call comes to you. We work remotely, with no contract and no site visit.</p>
{cta(slug)}<p class="micro">No contract · You keep ownership · Live in 5 business days</p></div></section>
<section><div class="w"><h2>Worcester-area towns we serve</h2><p>We work with trades in Worcester and across Central Massachusetts. Your Google service area should list the towns you really cover, for example Shrewsbury, Auburn, Millbury, Holden, Leicester, Grafton, West Boylston, Boylston or Paxton. We set it to match where you actually work, and we never create fake locations.</p></div></section>
<section><div class="w"><h2>Plumbers, HVAC, roofers and electricians</h2><ul class="ticks"><li><a href="/google-business-profile-management-plumbers/">Plumbers</a>: honest emergency hours and the right primary category</li><li><a href="/google-business-profile-management-hvac/">HVAC companies</a>: heating and cooling services listed, seasonal posts timed ahead of demand</li><li><a href="/google-business-profile-management-roofers/">Roofers</a>: project photos and storm-season updates</li><li><a href="/google-business-profile-management-electricians/">Electricians</a>: service areas, honest emergency hours, and every service you offer listed</li></ul></div></section>
<section><div class="w"><h2>Seasonal posts for Central Mass winters</h2><p>With Monthly Management we publish a new post every week. In the cold months that means posts like:</p><ul class="ticks"><li>Frozen pipes: how to prevent them, and what to do before you thaw one</li><li>Heating tune-ups booked before the coldest weeks</li><li>Ice dams and storm damage: what to look for along the roof edge</li><li>Holiday hours, so you're never shown as closed by mistake</li></ul></div></section>
<section><div class="w"><h2>Review replies within 24 hours</h2><p>Every review gets a reply within 24 hours, written in your voice, including the tough ones. Industry data from BrightLocal's 2025 survey: 89% of consumers would use a business that responds to all of its reviews, vs. 44% for one that doesn't respond. We never write or buy reviews.</p></div></section>
{PRICING}{faq_html(W_FAQ)}
<section class="close"><div class="w"><h2>How does your Worcester listing stack up?</h2><p>Score it in 2 minutes, free, no signup.</p><a class="btn" href="{grader(slug)}">Run the free listing grader</a></div></section>''')

# Boston page: link to Worcester + cleanup
p = pathlib.Path("google-business-profile-management-boston/index.html"); s = p.read_text()
if "worcester/\">Worcester" not in s.split("<footer")[0]:
    s = s.replace('<p class="note">Profile suspended? See our <a href="/google-business-profile-suspended/">suspension recovery guide</a>.</p>',
                  '<p class="note">Profile suspended? See our <a href="/google-business-profile-suspended/">suspension recovery guide</a>. Outside Boston? See <a href="/google-business-profile-management-worcester/">Worcester</a>, or <a href="/google-business-profile-cleanup/">what the $149 cleanup fixes</a>.</p>', 1)
p.write_text(s)

# ---------- sitemap ----------
urls = ["/", "/grader/", "/google-business-profile-cleanup/", "/google-business-profile-management-boston/", "/google-business-profile-management-worcester/",
        "/google-business-profile-management-plumbers/", "/google-business-profile-management-hvac/", "/google-business-profile-management-roofers/",
        "/google-business-profile-management-electricians/", "/google-business-profile-suspended/", "/partners/", "/contact/", "/privacy/", "/terms/"]
old = dict(re.findall(r"<loc>https://listingsteward.com(/[^<]*)</loc><lastmod>([^<]+)</lastmod>", pathlib.Path("sitemap.xml").read_text()))
changed = {"/", "/grader/", "/google-business-profile-cleanup/", "/google-business-profile-management-worcester/", "/google-business-profile-management-boston/",
           "/google-business-profile-management-plumbers/", "/google-business-profile-management-hvac/", "/google-business-profile-management-roofers/",
           "/google-business-profile-management-electricians/", "/google-business-profile-suspended/", "/partners/"}
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"<url><loc>{SITE}{u}</loc><lastmod>{'2026-10-30' if u in changed else old.get(u, '2026-10-30')}</lastmod></url>\n" for u in urls) + "</urlset>\n"
pathlib.Path("sitemap.xml").write_text(sm)
print("ok")
