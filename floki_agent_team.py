#!/usr/bin/env python3
"""FLOKI Agent Team — single-file build.

Seluruh sistem dalam satu file: 8 agent, knowledge base bersumber, guardrail
VIGIL, planner 30 hari, dashboard, dan API. Tanpa dependency, tanpa file data
terpisah — JSON dan HTML di-embed di bawah.

Jalankan:
    python3 floki_agent_team.py
    PORT=8080 DASHBOARD_TOKEN=rahasia python3 floki_agent_team.py

Lalu buka http://localhost:8080
Dibuat otomatis oleh scripts/build_single_file.py — jangan edit manual.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


# ====================================================================
# EMBEDDED ASSETS
# ====================================================================
_CONFIG_JSON = json.loads(r'''{"campaign": {"name": "FLOKI — Build > Meme", "goal": "Grow qualified interest in FLOKI by showing shipped utility: gaming, DeFi tooling, education, community.", "language": "en", "audience": ["crypto-curious retail who thinks memecoins are all vaporware", "web3 gamers looking for a playable on-chain game", "DeFi users who care about liquidity locks and vesting transparency", "FLOKI holders who want shareable, non-cringe content"], "voice": {"tone": "confident, concrete, slightly Viking-flavored, zero hype-words", "do": ["lead with a shipped product", "use exact numbers with dates", "invite people to check sources", "state the risk plainly"], "never": ["price predictions", "guarantees", "fake urgency", "attacking other projects", "hiding the Nov 2026 bot incident"]}, "positioning": "FLOKI is a 2021 memecoin that kept shipping: Valhalla game on mainnet, FlokiFi Locker across ~15 EVM chains, TokenFi for RWA tokenization, University of Floki for free education.", "primary_cta": "Read the ecosystem before you decide anything.", "compliance_officer": "VIGIL has veto power. Nothing publishes without its verdict."}, "engine": {"tick_seconds": 18, "seed_on_start": 26, "items_per_tick": 1, "history_days": 30, "port": 8080, "auto_start": true}, "pillars": {"monday": {"id": "UTILITY_PROOF", "theme": "Shipped, not promised", "facts": ["F02", "F05", "F21"]}, "tuesday": {"id": "GAMING", "theme": "Valhalla & Veras", "facts": ["F03", "F04"]}, "wednesday": {"id": "DEFI_TRUST", "theme": "Locks, vesting, transparency", "facts": ["F05", "F07", "F12"]}, "thursday": {"id": "EDUCATION", "theme": "Learn before you buy", "facts": ["F09", "F16", "F22"]}, "friday": {"id": "COMMUNITY", "theme": "Viking culture", "facts": ["F19", "F20", "F01"]}, "saturday": {"id": "COMMERCE_PAYMENTS", "theme": "Spend, trade, own", "facts": ["F10", "F11", "F13"]}, "sunday": {"id": "TRANSPARENCY", "theme": "Build in public, risks included", "facts": ["F15", "F17", "F22"]}}, "channels": {"x": {"enabled": true, "formats": ["post", "thread", "quote_hook"], "posts_per_week": 21, "best_times_utc": ["08:30", "12:00", "17:30"]}, "telegram": {"enabled": true, "formats": ["announcement", "quiz", "poll_brief"], "posts_per_week": 14, "best_times_utc": ["09:00", "15:00"]}, "instagram": {"enabled": true, "formats": ["carousel", "caption"], "posts_per_week": 7, "best_times_utc": ["11:00"]}, "tiktok": {"enabled": true, "formats": ["short_script"], "posts_per_week": 7, "best_times_utc": ["14:00"]}, "youtube": {"enabled": true, "formats": ["short_script", "video_description"], "posts_per_week": 3, "best_times_utc": ["16:00"]}, "reddit": {"enabled": true, "formats": ["discussion_post"], "posts_per_week": 2, "best_times_utc": ["13:00"]}}}''')
_COMPLIANCE_JSON = json.loads(r'''{"meta": {"owner": "VIGIL (Compliance & Fact-Guard Agent)", "principle": "Boleh promosi, tidak boleh menyesatkan. Semua konten harus bisa dipertanggungjawabkan ke facts base + sumber.", "note": "Aturan ini meniru prinsip pemasaran kripto yang aman: no return promises, no fake urgency, verified claims only, disclosure wajib."}, "hard_block": [{"id": "B01", "pattern": "guaranteed|dijamin|pasti (naik|untung|cuan)|anti rugi|risk[- ]free|tanpa risiko", "reason": "Menjanjikan hasil / tanpa risiko", "severity": 100}, {"id": "B02", "pattern": "\\b\\d+\\s?x\\b|\\b100x\\b|\\b1000x\\b|\\bto the moon\\b|\\bmoon(ing)? soon\\b", "reason": "Klaim kelipatan keuntungan", "severity": 95}, {"id": "B03", "pattern": "price prediction|prediksi harga|akan (mencapai|tembus) \\$|target harga", "reason": "Prediksi harga = financial advice", "severity": 95}, {"id": "B04", "pattern": "financial advice|saran investasi|nasihat investasi|investasikan (tabungan|dana darurat)", "reason": "Memberi saran investasi personal", "severity": 90}, {"id": "B05", "pattern": "buy now before|beli sekarang sebelum|jangan sampai ketinggalan|last chance|fomo", "reason": "Fake urgency / pressure", "severity": 80}, {"id": "B06", "pattern": "get rich|cepat kaya|passive income pasti|gajian dari crypto", "reason": "Klaim penghasilan", "severity": 90}, {"id": "B07", "pattern": "airdrop (gratis|resmi) (klaim|claim)|claim (free )?floki|giveaway \\d+ (floki|usdt)", "reason": "Pola scam airdrop / phishing", "severity": 100}, {"id": "B08", "pattern": "kirim (seed|private key|frasa pemulihan)|share your seed|send seed phrase", "reason": "Membahayakan keamanan user", "severity": 100}, {"id": "B09", "pattern": "partnership with (binance|tesla|spacex|nasa)|listing di (binance|coinbase) (segera|pasti)", "reason": "Klaim partner/listing tanpa sumber", "severity": 85}, {"id": "B10", "pattern": "profit from our|untung dari bot kami|jaminan (profit|yield) \\d+%", "reason": "Janji yield", "severity": 95}], "soft_flag": [{"id": "S01", "pattern": "undervalued|murah|cheap|diskon|below ath", "reason": "Framing harga = mendekati saran beli", "fix": "anggap sebagai kesempatan belajar ekosistem, bukan harga"}, {"id": "S02", "pattern": "\\$0\\.0+\\d+", "reason": "Menyebut angka harga spesifik", "fix": "hapus angka harga; fokus ke produk"}, {"id": "S03", "pattern": "segera hadir|soon|coming very soon", "reason": "Klaim waktu tanpa dasar", "fix": "no confirmed date"}, {"id": "S04", "pattern": "pasti|definitely|certainly|will rise|akan naik", "reason": "Kepastian yang tidak bisa dibuktikan", "fix": "bisa jadi / bergantung eksekusi"}, {"id": "S05", "pattern": "\\bterbesar\\b|\\bterbaik\\b|nomor 1|\\bbest (memecoin|coin|token|project)\\b|\\btop pick\\b", "reason": "Superlatif tanpa bukti", "fix": "salah satu yang paling aktif membangun"}], "required_disclosure": {"every_post": "Not financial advice. DYOR.", "when_holding_own_bag": "Disclosure: the author holds FLOKI.", "when_mentioning_bot_incident": "Never share seed phrases or private keys. No official refund/recovery service exists.", "verified_only": "Semua angka & klaim harus berasal dari facts base dengan sumber."}, "channel_limits": {"x": {"chars": 280, "hashtags_max": 3}, "telegram": {"chars": 4000, "hashtags_max": 4}, "instagram": {"chars": 2200, "hashtags_max": 8}, "tiktok": {"chars": 2200, "hashtags_max": 5}, "youtube": {"chars": 5000, "hashtags_max": 5}, "reddit": {"chars": 10000, "hashtags_max": 0}}, "approved_hashtags": ["#FLOKI", "#FlokiVikings", "#Valhalla", "#FlokiFi", "#TokenFi", "#Crypto", "#Memecoin", "#UtilityMemecoin", "#DYOR", "#Web3Gaming"], "forbidden_hashtags": ["#100x", "#gem", "#tothemoon", "#airdrop", "#freemoney", "#pump"], "escalation": "Verdict REJECT jika ada hard_block. NEEDS_EDIT jika ada soft_flag atau klaim tanpa fakta. APPROVED hanya jika bersih + disclosure lengkap."}''')
_FACTS_JSON = json.loads(r'''{"meta": {"project": "Floki (FLOKI)", "compiled_at": "2026-11-16", "note": "Knowledge base untuk seluruh agent. Setiap fakta punya sumber + level kepercayaan. Agent VIGIL menolak klaim yang tidak ada di sini.", "contracts": {"erc20_ethereum": "0xcf0C122c6b73ff809C693DB761e7BaeBe62b6a2E", "bep20_bnbchain": "0xfb5B838b6cfEEdC287784c685Fd4eFb8EF4cA658", "warning": "Ada puluhan token copycat bernama 'Floki'. Selalu verifikasi contract address dari floki.com sebelum beli."}}, "facts": [{"id": "F01", "tags": ["origin", "brand", "community"], "statement": "FLOKI diluncurkan tahun 2021 dan dinamai dari Floki, anak anjing Shiba Inu milik Elon Musk.", "confidence": "high", "publish_safe": true, "source": {"name": "Shironeko - What is FLOKI", "url": "https://www.shironeko.gg/what-is-floki/"}}, {"id": "F02", "tags": ["utility", "positioning"], "statement": "Sejak 2023 Floki memposisikan diri sebagai 'utility memecoin' dan sudah mengirim produk nyata: game, tool DeFi, platform edukasi, marketplace, sampai kartu pembayaran.", "confidence": "high", "publish_safe": true, "source": {"name": "Securities.io - Investing in Floki", "url": "https://www.securities.io/investing-in-floki/"}}, {"id": "F03", "tags": ["valhalla", "gaming", "utility"], "statement": "Valhalla, game strategi on-chain Floki dengan makhluk NFT bernama 'Veras' di peta heksagonal, live di mainnet opBNB sejak 30 Juni 2025. FLOKI adalah mata uang in-game-nya.", "confidence": "high", "publish_safe": true, "source": {"name": "FLOKI Blog - Roadmap", "url": "https://blog.floki.com/floki-roadmap-whats-next-on-our-agenda-3e957b56d277"}}, {"id": "F04", "tags": ["valhalla", "roadmap", "gaming"], "statement": "Roadmap resmi Floki menyebut versi mobile Valhalla untuk iOS dan Android sebagai target 2026. Belum ada tanggal rilis pasti.", "confidence": "medium", "publish_safe": true, "cautions": ["Harus ditulis sebagai rencana/roadmap, bukan hal yang sudah terjadi."], "source": {"name": "FLOKI Blog - Roadmap", "url": "https://blog.floki.com/floki-roadmap-whats-next-on-our-agenda-3e957b56d277"}}, {"id": "F05", "tags": ["flokifi", "defi", "security"], "statement": "FlokiFi Locker memungkinkan proyek mengunci token LP, NFT, dan jadwal vesting, sehingga publik bisa membuktikan likuiditas tidak bisa ditarik. Layanan ini sudah diperluas ke sekitar 15 jaringan EVM.", "confidence": "high", "publish_safe": true, "source": {"name": "Securities.io / Hibt", "url": "https://www.securities.io/investing-in-floki/"}}, {"id": "F06", "tags": ["tokenfi", "defi", "rwa"], "statement": "TokenFi adalah platform tokenisasi aset dunia nyata (RWA) yang dibangun tim Floki dan diatur Floki DAO, tapi memakai token sendiri yaitu TOKEN.", "confidence": "high", "publish_safe": true, "cautions": ["Jangan menyebut kinerja TokenFi otomatis menaikkan harga FLOKI. Secara teknis token-nya terpisah."], "source": {"name": "Securities.io - Investing in Floki", "url": "https://www.securities.io/investing-in-floki/"}}, {"id": "F07", "tags": ["staking", "tokenfi"], "statement": "Alokasi 54% dari supply TOKEN dialokasikan untuk memberi reward kepada staker FLOKI dalam program multi-tahun.", "confidence": "high", "publish_safe": true, "source": {"name": "Securities.io - Investing in Floki", "url": "https://www.securities.io/investing-in-floki/"}}, {"id": "F08", "tags": ["staking", "community"], "statement": "Snapshot April 2026: sekitar 460.000 holder sudah men-stake lebih dari $283 juta senilai FLOKI untuk memperoleh reward TOKEN.", "confidence": "medium", "publish_safe": true, "cautions": ["Angka ini snapshot historis. Wajib tulis 'per April 2026', bukan angka hari ini."], "source": {"name": "CryptoNews - FLOKI Price Prediction 2026", "url": "https://cryptonews.net/news/analytics/32653159/"}}, {"id": "F09", "tags": ["education", "community"], "statement": "University of Floki adalah konten edukasi kripto gratis yang bisa diakses siapa saja tanpa perlu beli token.", "confidence": "high", "publish_safe": true, "source": {"name": "Blockchain Magazine", "url": "https://blockchainmagazine.net/floki-crypto-is-back-is-floki-the-next-meme-king/"}}, {"id": "F10", "tags": ["commerce", "utility"], "statement": "FlokiPlaces adalah marketplace NFT dan merchandise di dalam ekosistem Floki.", "confidence": "high", "publish_safe": true, "source": {"name": "Blockchain Magazine", "url": "https://blockchainmagazine.net/floki-crypto-is-back-is-floki-the-next-meme-king/"}}, {"id": "F11", "tags": ["utility", "payments"], "statement": "Ekosistem Floki juga mencakup Floki Name Service dan kartu debit prabayar untuk pengeluaran harian di Eropa.", "confidence": "medium", "publish_safe": true, "source": {"name": "Securities.io - Investing in Floki", "url": "https://www.securities.io/investing-in-floki/"}}, {"id": "F12", "tags": ["tokenomics", "supply"], "statement": "Max supply FLOKI 10 triliun token dengan suplai beredar sekitar 9,5 triliun, ditambah burn berkala dan trading tax 0,3% di DEX yang mengisi treasury DAO.", "confidence": "high", "publish_safe": true, "cautions": ["Jangan menyebut burn sebagai jaminan kenaikan harga."], "source": {"name": "Shironeko / Cryptorank", "url": "https://www.shironeko.gg/what-is-floki/"}}, {"id": "F13", "tags": ["multichain"], "statement": "FLOKI tersedia sebagai ERC-20 di Ethereum dan BEP-20 di BNB Smart Chain, jadi punya akses likuiditas ke dua ekosistem besar.", "confidence": "high", "publish_safe": true, "source": {"name": "Securities.io - Investing in Floki", "url": "https://www.securities.io/investing-in-floki/"}}, {"id": "F14", "tags": ["institutional", "regulasi"], "statement": "FLOKI ETP sudah tercatat di Eropa dan tim melakukan pengajuan MiCAR melalui LCX ke ESMA.", "confidence": "medium", "publish_safe": true, "cautions": ["Jangan menyebut 'disetujui' atau 'lolos regulasi'. Ini pengajuan."], "source": {"name": "CryptoNews - FLOKI 2026", "url": "https://cryptonews.net/news/analytics/32653159/"}}, {"id": "F15", "tags": ["transparency", "security", "risk"], "statement": "5 November 2026 tim Floki mengofflinekan trading bot Telegram mereka setelah mendeteksi exploit. Tim sedang menyelidiki, memindahkan dana yang tersisa ke wallet aman, dan memigrasi user terdampak ke wallet baru yang aman.", "confidence": "high", "publish_safe": true, "cautions": ["WAJIB dipasangkan dengan edukasi keamanan. Dilarang menyebut kerugian sudah selesai atau dana pasti kembali."], "source": {"name": "PANews / crypto.news", "url": "https://panews.io/articles/01a1ae42-b6dd-7082-9989-5728f11d2fcf"}}, {"id": "F16", "tags": ["security", "education"], "statement": "Tim Floki menegaskan tidak akan pernah mengirim DM lebih dulu atau meminta seed phrase / private key. Siapa pun yang menawarkan jasa 'refund' atau 'recovery' harus diabaikan.", "confidence": "high", "publish_safe": true, "source": {"name": "PANews / Chaincatcher", "url": "https://www.chaincatcher.com/en/article/2302221"}}, {"id": "F17", "tags": ["transparency", "roadmap", "burn"], "statement": "Relaunch trading bot Floki diperkirakan terjadi tapi belum ada tanggal pasti. 50% dari fee trading 1% dialokasikan untuk buyback dan burn FLOKI.", "confidence": "medium", "publish_safe": true, "cautions": ["Tulis sebagai rencana, bukan janji. Jangan klaim 'segera hadir'."], "source": {"name": "CoinMarketCap AI - FLOKI Latest Updates", "url": "https://coinmarketcap.com/cmc-ai/floki-inu/latest-updates/"}}, {"id": "F18", "tags": ["roadmap", "defi"], "statement": "Integrasi Venus Core Markets masih menunggu governance vote. Jika lolos, holder bisa memakai FLOKI sebagai collateral untuk meminjam ETH atau stablecoin.", "confidence": "medium", "publish_safe": true, "cautions": ["Statusnya pending. Jangan ditulis seolah sudah aktif."], "source": {"name": "FLOKI Blog - Roadmap", "url": "https://blog.floki.com/floki-roadmap-whats-next-on-our-agenda-3e957b56d277"}}, {"id": "F19", "tags": ["community", "culture"], "statement": "Komunitas Floki menyebut diri 'Floki Vikings' dan pernah masuk jajaran top 10 leaderboard social engagement LunarCrush.", "confidence": "medium", "publish_safe": true, "source": {"name": "Blockchain Magazine", "url": "https://blockchainmagazine.net/floki-crypto-is-back-is-floki-the-next-meme-king/"}}, {"id": "F20", "tags": ["culture", "community"], "statement": "Pada 2 November 2026 Floki ikut merayakan International Doge Day dengan tribute untuk Kabosu, Shiba Inu yang menginspirasi meme Doge.", "confidence": "high", "publish_safe": true, "source": {"name": "crypto.news", "url": "https://crypto.news/dogecoin-international-doge-day-kabosu-2026/"}}, {"id": "F21", "tags": ["positioning", "history"], "statement": "FLOKI berumur lebih dari 4 tahun dan termasuk sedikit proyek dari gelombang memecoin 2021 yang masih aktif membangun di 2026.", "confidence": "high", "publish_safe": true, "source": {"name": "CryptoNews - FLOKI 2026", "url": "https://cryptonews.net/news/analytics/32653159/"}}, {"id": "F22", "tags": ["risk", "positioning"], "statement": "FLOKI masih aset spekulatif berisiko tinggi dan harganya sangat dipengaruhi sentimen pasar serta pergerakan Bitcoin, bukan hanya fundamental proyek.", "confidence": "high", "publish_safe": true, "cautions": ["Fakta ini tidak boleh dihapus dari konten edukasi/risk. VIGIL akan menolak kampanye tanpa disclosure risiko."], "source": {"name": "Shironeko / CoinGabbar", "url": "https://www.shironeko.gg/what-is-floki/"}}, {"id": "F23", "tags": ["roadmap", "ai"], "statement": "Laporan November 2026 menyebut adanya pekerjaan pada framework 'FLOKI Minibot M1' bersama Rice AI.", "confidence": "low", "publish_safe": false, "cautions": ["Belum dikonfirmasi sumber resmi. JANGAN dipakai di konten publik sampai terverifikasi."], "source": {"name": "OpenPR press release", "url": "https://www.openpr.com/news/4690325/7-best-cryptos-to-buy-in-november-can-apeing-s-85-staking"}}, {"id": "F24", "tags": ["context", "market"], "statement": "Per November 2026 FLOKI diperdagangkan jauh di bawah all-time high-nya dan berada di area multi-year low.", "confidence": "medium", "publish_safe": false, "cautions": ["Jangan dipakai sebagai hook promosi (framing 'murah, saatnya beli' = bahaya). Hanya untuk konteks internal agent & laporan analis."], "source": {"name": "CryptoNews / OpenPR", "url": "https://cryptonews.net/news/analytics/32653159/"}}]}''')
_DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>FLOKI Agent Team — Mission Control</title>
<style>
  :root{
    --bg:#07080b; --panel:#0e1016; --panel2:#12151d; --line:#1e2330;
    --ink:#e8ecf4; --dim:#8b94a7; --dimmer:#5a6377;
    --amber:#f5a524; --ember:#ff6b35; --green:#3ddc97; --red:#ff5d6c; --blue:#63b3ff;
    --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;-webkit-font-smoothing:antialiased}
  a{color:var(--blue);text-decoration:none}
  a:hover{text-decoration:underline}
  .wrap{max-width:1560px;margin:0 auto;padding:18px 20px 60px}
  /* ---------- header ---------- */
  header{display:flex;align-items:center;gap:16px;flex-wrap:wrap;
    padding:14px 18px;border:1px solid var(--line);border-radius:14px;
    background:linear-gradient(135deg,#0f1219 0%,#0b0d13 60%,#12100c 100%);position:relative;overflow:hidden}
  header:before{content:"";position:absolute;inset:0;background:radial-gradient(600px 120px at 8% 0%,rgba(245,165,36,.10),transparent 70%);pointer-events:none}
  .brand{display:flex;align-items:center;gap:12px;min-width:260px}
  .rune{width:42px;height:42px;border-radius:11px;display:grid;place-items:center;
    background:linear-gradient(150deg,#241a08,#3a2a0c);border:1px solid #4a3510;font-size:20px}
  h1{font-size:17px;margin:0;letter-spacing:.02em}
  h1 span{color:var(--amber)}
  .sub{font-size:11.5px;color:var(--dim);margin-top:3px;font-family:var(--mono)}
  .spacer{flex:1}
  .pill{font-family:var(--mono);font-size:11px;padding:5px 10px;border-radius:999px;
    border:1px solid var(--line);color:var(--dim);display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
  .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 9px var(--green)}
  .dot.off{background:var(--amber);box-shadow:0 0 9px var(--amber)}
  .pulse{animation:p 1.6s infinite}
  @keyframes p{0%,100%{opacity:1}50%{opacity:.35}}
  button{font-family:inherit;font-size:12px;cursor:pointer;border-radius:9px;padding:8px 13px;
    border:1px solid var(--line);background:var(--panel2);color:var(--ink);transition:.15s}
  button:hover{border-color:#39405a;background:#171b25}
  button.primary{background:linear-gradient(180deg,#f5a524,#e08b12);color:#170f00;border-color:#f7b64c;font-weight:700}
  button.primary:hover{filter:brightness(1.08)}
  button.ghost{background:transparent}
  button.tiny{padding:5px 9px;font-size:11px;border-radius:7px}
  /* ---------- kpi ---------- */
  .kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:14px 0}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
  .kpi .k{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--dimmer);font-family:var(--mono)}
  .kpi .v{font-size:23px;font-weight:700;margin-top:5px;letter-spacing:-.02em}
  .kpi .v small{font-size:11px;color:var(--dim);font-weight:500}
  /* ---------- layout ---------- */
  .cols{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:14px;align-items:start}
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:13px}
  .panel h2{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);
    margin:0;padding:13px 15px;border-bottom:1px solid var(--line);font-family:var(--mono);font-weight:600;
    display:flex;align-items:center;gap:8px}
  .panel .body{padding:14px 15px}
  /* ---------- agents ---------- */
  .agents{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}
  .agent{flex:0 0 auto;background:var(--panel2);border:1px solid var(--line);border-radius:11px;padding:11px 12px;position:relative;overflow:hidden}
  .agent .top{display:flex;align-items:center;gap:8px}
  .agent .g{font-family:var(--mono);font-size:10.5px;font-weight:800;letter-spacing:.04em;
    width:26px;height:26px;border-radius:7px;display:grid;place-items:center;
    background:linear-gradient(150deg,#241a08,#3a2a0c);border:1px solid #4a3510;color:var(--amber)}
  .agent .c{font-family:var(--mono);font-size:12px;font-weight:700;letter-spacing:.04em}
  .agent .r{font-size:10.5px;color:var(--dimmer);margin-top:6px;line-height:1.45;min-height:30px}
  .agent .st{position:absolute;top:11px;right:11px;font-family:var(--mono);font-size:9.5px;
    text-transform:uppercase;letter-spacing:.06em;padding:3px 7px;border-radius:999px;border:1px solid var(--line);color:var(--dim)}
  .agent .st.working{color:#170f00;background:var(--amber);border-color:var(--amber);font-weight:700}
  .agent .st.ok{color:var(--green);border-color:#1d4436;background:#0c1f18}
  .agent .task{font-size:10.5px;color:var(--amber);font-family:var(--mono);margin-top:7px;
    height:13px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
  .agent .n{font-family:var(--mono);font-size:10.5px;color:var(--dimmer);margin-top:5px}
  /* ---------- filters ---------- */
  .filters{display:flex;gap:7px;flex-wrap:wrap;padding:12px 15px;border-bottom:1px solid var(--line);align-items:center}
  .chip{font-family:var(--mono);font-size:11px;padding:5px 10px;border-radius:999px;border:1px solid var(--line);
    color:var(--dim);cursor:pointer;background:transparent;text-transform:lowercase}
  .chip.on{background:#1b2130;border-color:#39405a;color:var(--ink)}
  input[type=search]{margin-left:auto;background:#0a0c11;border:1px solid var(--line);border-radius:8px;
    color:var(--ink);padding:7px 10px;font-size:12px;font-family:var(--mono);min-width:170px;outline:none}
  input[type=search]:focus{border-color:#39405a}
  /* ---------- queue ---------- */
  .queue{padding:12px 15px;display:flex;flex-direction:column;gap:11px;max-height:1080px;overflow:auto}
  .card{flex:0 0 auto;border:1px solid var(--line);border-radius:12px;background:var(--panel2);overflow:hidden}
  .card.rejected{opacity:.62;border-color:#3a1d24}
  .card.approved{border-left:3px solid var(--green)}
  .card.needs_edit{border-left:3px solid var(--amber)}
  .card.rejected{border-left:3px solid var(--red)}
  .chead{display:flex;align-items:center;gap:7px;flex-wrap:wrap;padding:9px 12px;border-bottom:1px solid var(--line);background:#0c0e14}
  .badge{font-family:var(--mono);font-size:10px;padding:3px 7px;border-radius:6px;border:1px solid var(--line);color:var(--dim);text-transform:uppercase;letter-spacing:.05em}
  .badge.x{color:#9fd0ff;border-color:#1d3345;background:#0c1620}
  .badge.telegram{color:#8fd8ff;border-color:#16394b;background:#0a1a22}
  .badge.instagram{color:#ffa8d8;border-color:#4a1f38;background:#1b0d15}
  .badge.tiktok{color:#a5f3ff;border-color:#12414a;background:#08191c}
  .badge.youtube{color:#ff9d9d;border-color:#4a1e1e;background:#1c0d0d}
  .badge.reddit{color:#ffc9a3;border-color:#4a2f18;background:#1c1208}
  .id{font-family:var(--mono);font-size:10.5px;color:var(--dimmer)}
  .score{margin-left:auto;font-family:var(--mono);font-size:10.5px;color:var(--dim)}
  .score b{color:var(--green)}
  .score b.warn{color:var(--amber)}
  .score b.bad{color:var(--red)}
  .cbody{padding:12px;font-size:13px;line-height:1.62;white-space:pre-wrap;word-break:break-word}
  .cbody.small{font-size:12px;line-height:1.55}
  .meta{display:flex;gap:10px;flex-wrap:wrap;padding:0 12px 10px;font-size:10.5px;color:var(--dimmer);font-family:var(--mono)}
  .notes{margin:0 12px 10px;padding:9px 11px;border-radius:9px;background:#171207;border:1px solid #3a2c10;
    font-size:11px;color:#e9c98d;font-family:var(--mono);line-height:1.5}
  .notes.bad{background:#1c0b0e;border-color:#3d1a20;color:#ffb3ba}
  .src{padding:0 12px 10px;font-size:10.5px;color:var(--dimmer);font-family:var(--mono)}
  .src a{color:#6f8fb5}
  .cact{display:flex;gap:6px;padding:9px 12px;border-top:1px solid var(--line);background:#0a0c11;flex-wrap:wrap;align-items:center}
  .cact .flag{font-family:var(--mono);font-size:10px;color:var(--amber);margin-left:auto}
  /* ---------- feed ---------- */
  .feed{padding:10px 14px;max-height:460px;overflow:auto;font-family:var(--mono);font-size:11.2px;line-height:1.62}
  .feed .row{display:flex;gap:8px;padding:3px 0;border-bottom:1px dotted #151922}
  .feed .t{color:#495066;flex:0 0 52px}
  .feed .a{color:var(--amber);flex:0 0 62px}
  .feed .m{color:#a7b0c2;flex:1;word-break:break-word}
  .feed .m.ok{color:#7fe3b6}.feed .m.warn{color:#f0c063}.feed .m.error{color:#ff8b95}
  .stat{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px dotted #151922;font-size:12px;font-family:var(--mono)}
  .stat:last-child{border:0}
  .stat span:first-child{color:var(--dim)}
  .bar{height:6px;border-radius:99px;background:#1a1f2b;overflow:hidden;margin-top:4px}
  .bar>i{display:block;height:100%;background:linear-gradient(90deg,#f5a524,#ff6b35)}
  .tabs{display:flex;gap:6px;padding:10px 15px 0}
  pre.doc{margin:0;padding:14px 15px;font-family:var(--mono);font-size:11.5px;line-height:1.6;
    white-space:pre-wrap;max-height:640px;overflow:auto;color:#b9c2d4}
  .hidden{display:none!important}
  .toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(12px);opacity:0;
    background:#171b25;border:1px solid #39405a;color:var(--ink);padding:10px 16px;border-radius:10px;
    font-size:12px;font-family:var(--mono);transition:.2s;pointer-events:none;z-index:99}
  .toast.on{opacity:1;transform:translateX(-50%) translateY(0)}
  @media(max-width:1220px){.cols{grid-template-columns:1fr}.agents{grid-template-columns:repeat(2,1fr)}
    .kpis{grid-template-columns:repeat(3,1fr)}}
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="brand">
      <div class="rune"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f5a524" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 3 6v5c0 5 4 9 9 11 5-2 9-6 9-11V6l-9-4z"/><path d="M8 12h8M12 8v8"/></svg></div>
      <div>
        <h1>FLOKI <span>AGENT TEAM</span></h1>
        <div class="sub" id="statusline">booting mission control…</div>
      </div>
    </div>
    <div class="spacer"></div>
    <div class="pill"><span class="dot pulse" id="livedot"></span><span id="livetext">LIVE</span></div>
    <div class="pill" id="clock">--:--:--</div>
    <button class="primary" onclick="runCycle()">Run cycle</button>
    <button id="pausebtn" onclick="togglePause()">Pause</button>
    <button onclick="location.href='/download/floki_agent_team.py'">⬇ single-file .py</button>
    <button onclick="download('export.csv','floki_content_queue.csv')">Export CSV</button>
    
  </header>

  <div class="kpis">
    <div class="kpi"><div class="k">items produced</div><div class="v" id="k_items">0</div></div>
    <div class="kpi"><div class="k">approval rate</div><div class="v" id="k_appr">–</div></div>
    <div class="kpi"><div class="k">clean first pass</div><div class="v" id="k_clean">–</div></div>
    <div class="kpi"><div class="k">avg risk score</div><div class="v" id="k_score">–</div></div>
    <div class="kpi"><div class="k">projected reach</div><div class="v" id="k_reach">–</div></div>
    <div class="kpi"><div class="k">awaiting you</div><div class="v" id="k_human">–</div></div>
  </div>

  <div class="panel" style="margin-bottom:14px">
    <h2>▚ agent roster <span style="color:var(--dimmer);text-transform:none;letter-spacing:0;font-weight:400">
      — ATLAS plans · writers draft · VIGIL vetoes · METRA reports</span></h2>
    <div class="body"><div class="agents" id="agents"></div></div>
  </div>

  <div class="cols">
    <div class="panel">
      <div class="tabs">
        <button class="chip on" data-tab="queue" onclick="setTab('queue')">content queue</button>
        <button class="chip" data-tab="calendar" onclick="setTab('calendar')">calendar</button>
        <button class="chip" data-tab="report" onclick="setTab('report')">metra report</button>
      </div>
      <div id="tab-queue">
        <div class="filters" id="filters">
          <button class="chip on" data-ch="all">all</button>
          <button class="chip" data-ch="x">x</button>
          <button class="chip" data-ch="telegram">telegram</button>
          <button class="chip" data-ch="instagram">instagram</button>
          <button class="chip" data-ch="tiktok">tiktok</button>
          <button class="chip" data-ch="youtube">youtube</button>
          <button class="chip" data-ch="reddit">reddit</button>
          <button class="chip" data-ch="flagged" id="flagchip">needs edit</button>
          <input type="search" id="search" placeholder="search copy…" oninput="render()" />
        </div>
        <div class="queue" id="queue"></div>
      </div>
      <div id="tab-calendar" class="hidden"><pre class="doc" id="caldoc">loading…</pre></div>
      <div id="tab-report" class="hidden"><pre class="doc" id="repdoc">loading…</pre></div>
    </div>

    <div style="display:flex;flex-direction:column;gap:14px">
      <div class="panel">
        <h2>▚ live activity feed</h2>
        <div class="feed" id="feed"></div>
      </div>
      <div class="panel">
        <h2>▚ VIGIL — guardrail status</h2>
        <div class="body" id="vigil"></div>
      </div>
      <div class="panel">
        <h2>▚ knowledge &amp; compliance</h2>
        <div class="body" id="kb"></div>
      </div>
      <div class="panel">
        <h2>▚ channel mix</h2>
        <div class="body" id="mix"></div>
      </div>
    </div>
  </div>

  <div style="text-align:center;color:var(--dim);font-size:11px;font-family:var(--mono);margin-top:18px;line-height:1.8">
    Unduh aplikasi sebagai satu file: <a href="/download/floki_agent_team.py" style="color:var(--amber)">floki_agent_team.py</a>
    · seluruh proyek: <a href="/download/floki-agent-team.zip" style="color:var(--amber)">zip</a>
  </div>
  <div style="text-align:center;color:var(--dimmer);font-size:10.5px;font-family:var(--mono);margin-top:10px;line-height:1.8">
    Every claim is traceable to <b style="color:var(--dim)">data/floki_facts.json</b> · VIGIL blocks price predictions, guarantees and fake urgency ·
    projections are heuristics, not live analytics · nothing posts automatically to any platform — you approve first.
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
let STATE = null, filterCh = 'all', tab = 'queue';

const $ = s => document.querySelector(s);
const esc = s => (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

function toast(msg){
  const t = $('#toast'); t.textContent = msg; t.classList.add('on');
  clearTimeout(t._h); t._h = setTimeout(()=>t.classList.remove('on'), 1900);
}
function fmtNum(n){ return (n||0).toLocaleString('en-US'); }

/* ------------------------------------------------------------------ poll */
async function refresh(){
  try{
    const r = await fetch('api/state?limit=70', {cache:'no-store'});
    STATE = await r.json();
    render();
  }catch(e){ $('#statusline').textContent = 'connection lost — retrying…'; }
}

/* ---------------------------------------------------------------- render */
function render(){
  if(!STATE) return;
  const s = STATE.status, m = STATE.metrics;

  $('#statusline').textContent =
    `cycle ${s.ticks} · plan ${s.cursor}/${s.plan_slots} slots · tick every ${s.tick_seconds}s · ${STATE.plan.per_channel ? Object.keys(STATE.plan.per_channel).length : 0} channels`;
  $('#livetext').textContent = s.paused ? 'PAUSED' : 'LIVE';
  $('#livedot').className = 'dot ' + (s.paused ? 'off' : 'pulse');
  $('#pausebtn').textContent = s.paused ? 'Resume' : 'Pause';
  $('#clock').textContent = new Date().toISOString().slice(11,19) + ' UTC';

  $('#k_items').innerHTML = fmtNum(m.total) + ' <small>items</small>';
  $('#k_appr').innerHTML = m.total ? m.approval_rate + '%' : '–';
  $('#k_clean').innerHTML = m.total ? m.clean_rate + '%' : '–';
  $('#k_score').innerHTML = m.total ? m.avg_score + ' <small>/100</small>' : '–';
  $('#k_reach').innerHTML = m.total ? fmtNum(m.projected_reach) + ' <small>proj.</small>' : '–';
  $('#k_human').innerHTML = fmtNum(m.pending_human) + ' <small>drafts</small>';

  /* agents */
  $('#agents').innerHTML = STATE.agents.map(a => `
    <div class="agent">
      <span class="st ${a.status==='idle'?'':'working'}">${esc(a.status)}</span>
      <div class="top"><span class="g">${a.codename.slice(0,2)}</span><span class="c">${a.codename}</span></div>
      <div class="r">${esc(a.role)}</div>
      <div class="task">${esc(a.current_task || a.last_action || '—')}</div>
      <div class="n">${fmtNum(a.tasks_done)} ${a.tasks_done===1?'task':'tasks'} · ${esc(a.channel)}</div>
    </div>`).join('');

  /* feed */
  $('#feed').innerHTML = STATE.log.map(l => `
    <div class="row"><span class="t">${l.t.slice(11,19)}</span>
      <span class="a">${esc(l.agent)}</span>
      <span class="m ${l.level==='info'?'':esc(l.level)}">${esc(l.msg)}</span></div>`).join('') || '<div class="row"><span class="m">waiting for first cycle…</span></div>';

  /* vigil */
  const v = STATE.agents.find(a=>a.codename==='VIGIL') || {};
  const c = v.counters || {approved:0,edited:0,blocked:0};
  const tot = Math.max(1, c.approved+c.edited+c.blocked);
  $('#vigil').innerHTML = `
    <div class="stat"><span>clean approvals</span><span style="color:var(--green)">${c.approved}</span></div>
    <div class="stat"><span>auto-repaired phrases</span><span style="color:var(--amber)">${c.edited}</span></div>
    <div class="stat"><span>drafts blocked</span><span style="color:var(--red)">${c.blocked}</span></div>
    <div class="stat"><span>guardrail pass rate</span><span>${Math.round(100*(c.approved+c.edited)/tot)}%</span></div>
    <div class="bar"><i style="width:${Math.round(100*(c.approved+c.edited)/tot)}%"></i></div>
    <div style="font-size:10.5px;color:var(--dimmer);font-family:var(--mono);margin-top:10px;line-height:1.6">
      hard blocks: price predictions · guaranteed returns · fake urgency · airdrop-claim patterns · seed-phrase requests.<br>
      every post is forced to carry “Not financial advice. DYOR.”
    </div>`;

  /* kb */
  const k = STATE.kb;
  $('#kb').innerHTML = `
    <div class="stat"><span>facts in knowledge base</span><span>${k.facts_total}</span></div>
    <div class="stat"><span>publishable (sourced)</span><span style="color:var(--green)">${k.facts_publishable}</span></div>
    <div class="stat"><span>held back / low confidence</span><span style="color:var(--amber)">${k.facts_blocked}</span></div>
    <div class="stat"><span>hard rules</span><span>${k.hard_rules}</span></div>
    <div class="stat"><span>soft flags</span><span>${k.soft_rules}</span></div>`;

  /* mix */
  const by = m.by_channel || {}, mx = Math.max(1, ...Object.values(by));
  $('#mix').innerHTML = Object.entries(by).sort((a,b)=>b[1]-a[1]).map(([ch,n])=>`
    <div class="stat"><span>${ch}</span><span>${n}</span></div>
    <div class="bar"><i style="width:${Math.round(100*n/mx)}%"></i></div>`).join('') ||
    '<div class="stat"><span>generating…</span><span>0</span></div>';

  renderQueue();
}

function renderQueue(){
  if(!STATE) return;
  const q = $('#search').value.toLowerCase().trim();
  let items = STATE.items.filter(i => {
    if(filterCh === 'flagged') return i.status !== 'approved';
    if(filterCh !== 'all' && i.channel !== filterCh) return false;
    if(q && !(i.body.toLowerCase().includes(q) || i.pillar.toLowerCase().includes(q) || i.agent.toLowerCase().includes(q))) return false;
    return true;
  });
  $('#queue').innerHTML = items.map(card).join('') ||
    '<div style="color:var(--dimmer);font-family:var(--mono);font-size:12px;padding:16px">no items match — run a cycle.</div>';
}

function card(i){
  const co = i.compliance, sc = co.score;
  const cls = sc >= 92 ? '' : sc >= 75 ? 'warn' : 'bad';
  const vlabel = `<span style="color:${co.verdict==='APPROVED'?'var(--green)':co.verdict==='REJECT'?'var(--red)':'var(--amber)'}">${{APPROVED:'approved',NEEDS_EDIT:'repaired by VIGIL',REJECT:'rejected'}[co.verdict]||co.verdict}</span>`;
  const notes = (co.notes||[]).length ? `<div class="notes ${co.verdict==='REJECT'?'bad':''}">${esc(co.notes.join(' · '))}</div>` : '';
  const srcs = (i.sources||[]).map(s=>`<a href="${s.url}" target="_blank" rel="noopener">${esc(s.fact)} ${esc(s.name)}</a>`).join(' · ');
  const quiz = i.answer_key ? `<div class="notes">answer key → ${esc(i.answer_key)} — ${esc(i.explanation||'')}</div>` : '';
  const media = i.media_brief ? `<div class="src">visual brief: ${esc(i.media_brief)}</div>` : '';
  const human = i.human ? `<span class="flag">you: ${esc(i.human)}</span>` : '';
  return `<div class="card ${i.status}">
    <div class="chead">
      <span class="id">#${i.id}</span>
      <span class="badge ${i.channel}">${i.channel}</span>
      <span class="badge">${esc(i.format)}</span>
      <span class="badge" style="border-color:#2a3550;color:#93a6c9">${esc(i.pillar)}</span>
      <span class="badge" style="border-color:#3b3320;color:#e6c48a">${esc(i.agent)}</span>
      <span class="score">${vlabel} · risk <b class="${cls}">${sc}</b>/100 · reach ~${i.engagement}${i.spice?` · <span style="color:var(--amber)" title="writer tried a hype line, VIGIL caught it">${i.spice==='hard'?'vetoed':'rephrased'}</span>`:''}</span>
    </div>
    <div class="cbody ${i.body.length>700?'small':''}">${esc(i.body)}</div>
    ${notes}${quiz}
    <div class="meta"><span>slot ${esc(i.scheduled_for)}</span><span>pillar: ${esc(i.pillar_theme)}</span></div>
    ${media}
    ${srcs?`<div class="src">sources: ${srcs}</div>`:''}
    <div class="cact">
      <button class="tiny" onclick="copyItem('${i.id}')">copy</button>
      <button class="tiny" onclick="verdict('${i.id}','approved')">approve</button>
      <button class="tiny" onclick="verdict('${i.id}','rejected')">reject</button>
      <button class="tiny" onclick="verdict('${i.id}','hold')">hold</button>
      ${human}
    </div>
  </div>`;
}

/* ---------------------------------------------------------------- actions */
async function verdict(id, action){
  await fetch('api/verdict', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({id, action})});
  toast(`#${id} → ${action}`); refresh();
}
async function runCycle(){
  toast('ATLAS dispatching writers…');
  await fetch('api/cycle', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({n:3})});
  refresh();
}
async function togglePause(){
  const paused = STATE && STATE.status.paused;
  await fetch(paused ? 'api/resume' : 'api/pause', {method:'POST'});
  toast(paused ? 'loop resumed' : 'loop paused'); refresh();
}
function copyItem(id){
  const it = STATE.items.find(i=>i.id===id); if(!it) return;
  navigator.clipboard.writeText(it.body).then(()=>toast('#'.concat(id,' copied — paste into ',it.channel)),()=>toast('copy blocked by browser'));
}
function download(name, filename){
  const a=document.createElement('a'); a.href='/api/export.csv'; a.download=filename; a.click();
  toast('exporting ' + name);
}
function setTab(t){
  tab = t;
  document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('on', b.dataset.tab===t));
  ['queue','calendar','report'].forEach(x=>$('#tab-'+x).classList.toggle('hidden', x!==t));
  if(t==='calendar') fetch('api/file?name=calendar').then(r=>r.text()).then(txt=>$('#caldoc').textContent=txt);
  if(t==='report') fetch('api/file?name=report').then(r=>r.text()).then(txt=>$('#repdoc').textContent=txt);
}

document.querySelectorAll('[data-ch]').forEach(b=>b.addEventListener('click', ()=>{
  filterCh = b.dataset.ch;
  document.querySelectorAll('[data-ch]').forEach(x=>x.classList.toggle('on', x===b));
  renderQueue();
}));

refresh();
setInterval(refresh, 2600);
setInterval(()=>{ $('#clock').textContent = new Date().toISOString().slice(11,19) + ' UTC'; }, 1000);
</script>
</body>
</html>
'''


# ====================================================================
# MODULE: engine/core.py
# ====================================================================
"""Core helpers shared by all agents: config, knowledge base, text utilities."""

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = Path(os.environ.get("FLOKI_OUT", "outputs"))
STATE = Path(os.environ.get("FLOKI_STATE", "state"))


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _pick(disk_path, fallback):
    """Pakai file di disk kalau ada (mode repo), kalau tidak pakai embed."""
    try:
        return load_json(disk_path)
    except (OSError, ValueError):
        return fallback

CONFIG = _pick(ROOT / "config.json", _CONFIG_JSON)
COMPLIANCE = _pick(DATA / "compliance.json", _COMPLIANCE_JSON)


class KnowledgeBase:
    """Every claim an agent may make must come from here."""

    def __init__(self, path: Path | None = None):
        raw = _pick(path or (DATA / "floki_facts.json"), _FACTS_JSON)
        self.meta = raw["meta"]
        self.facts = {f["id"]: f for f in raw["facts"]}

    def get(self, fact_id: str) -> dict:
        return self.facts[fact_id]

    def statement(self, fact_id: str) -> str:
        return self.facts[fact_id]["statement"]

    def publishable(self, fact_id: str) -> bool:
        f = self.facts.get(fact_id)
        return bool(f and f.get("publish_safe") and f.get("confidence") in ("high", "medium"))

    def pick(self, ids: list[str], rng: random.Random, pool_size: int = 2) -> list[str]:
        safe = [i for i in ids if self.publishable(i)]
        if not safe:
            return []
        rng.shuffle(safe)
        return safe[:pool_size]

    def sources(self, ids: list[str]) -> list[dict]:
        seen, out = set(), []
        for i in ids:
            f = self.facts.get(i)
            if not f:
                continue
            s = f["source"]
            if s["url"] in seen:
                continue
            seen.add(s["url"])
            out.append({"fact": i, "name": s["name"], "url": s["url"]})
        return out

    def search(self, tags: list[str], publishable_only: bool = True) -> list[str]:
        ids = []
        for fid, f in self.facts.items():
            if publishable_only and not self.publishable(fid):
                continue
            if set(tags) & set(f.get("tags", [])):
                ids.append(fid)
        return sorted(ids)


KB = KnowledgeBase()


# ---------------------------------------------------------------- text utils
EMOJI = {
    "viking": ["⚔️", "🛡️", "🔥", "🪓"],
    "game": ["🎮", "🕹️", "🏆", "🗺️"],
    "defi": ["🔒", "📜", "🧾", "⚙️"],
    "learn": ["🧠", "📚", "🎓", "🔍"],
    "community": ["🐕", "🤝", "🌊", "🫂"],
    "pay": ["💳", "🛒", "🏪", "📦"],
    "warn": ["⚠️", "🚨", "🧯", "🛑"],
    "spark": ["✦", "→", "//", "·"],
}

HASHTAG_SETS = {
    "utility": ["#FLOKI", "#UtilityMemecoin", "#Crypto"],
    "gaming": ["#FLOKI", "#Valhalla", "#Web3Gaming"],
    "defi": ["#FLOKI", "#FlokiFi", "#DeFi"],
    "education": ["#FLOKI", "#DYOR", "#Crypto"],
    "community": ["#FLOKI", "#FlokiVikings", "#Memecoin"],
    "commerce": ["#FLOKI", "#Crypto", "#Web3"],
    "transparency": ["#FLOKI", "#DYOR", "#Crypto"],
    "tokenfi": ["#FLOKI", "#TokenFi", "#RWA"],
}


def emoji(kind: str, rng: random.Random) -> str:
    return rng.choice(EMOJI.get(kind, EMOJI["spark"]))


def fit(text: str, limit: int) -> str:
    """Trim to limit on a word boundary without breaking markdown/links."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,;:—-") + "…"


def tags_for(pillar_id: str) -> list[str]:
    key = {
        "UTILITY_PROOF": "utility",
        "GAMING": "gaming",
        "DEFI_TRUST": "defi",
        "EDUCATION": "education",
        "COMMUNITY": "community",
        "COMMERCE_PAYMENTS": "commerce",
        "TRANSPARENCY": "transparency",
    }.get(pillar_id, "utility")
    return HASHTAG_SETS[key]


@dataclass
class Draft:
    """Structured content before channel rendering + compliance review."""

    agent: str
    channel: str
    fmt: str
    pillar: str
    hook: str
    points: list[str] = field(default_factory=list)
    proof_ids: list[str] = field(default_factory=list)
    cta: str = ""
    tags: list[str] = field(default_factory=list)
    media_brief: str = ""
    risk_note: str = ""
    body: str = ""          # filled by renderer
    sources: list[dict] = field(default_factory=list)
    extra: dict = field(default_factory=dict)


# ====================================================================
# MODULE: engine/content_bank.py
# ====================================================================
"""Content banks: one entry per campaign pillar.

Every string here is written to be publishable as-is: concrete, sourced,
zero hype-words. Facts are injected by the agent layer, never hardcoded twice.
"""

PILLARS: dict[str, dict] = {
    "UTILITY_PROOF": {
        "label": "Shipped, not promised",
        "emoji": "viking",
        "hooks": [
            "Most memecoins ship a roadmap. FLOKI shipped a game, a locker, and a university.",
            "2021 launched a thousand memecoins. Very few are still writing code in 2026.",
            "The meme got the attention. The products had to earn the rest.",
            "You can't audit a meme. You can audit a lock.",
            "Ask any memecoin one question: what did you ship this year?",
        ],
        "angles": [
            ["Valhalla went live on opBNB mainnet on June 30, 2025 — not a testnet, not a demo.",
             "FlokiFi Locker lets projects lock LP tokens and vesting schedules across ~15 EVM chains.",
             "University of Floki teaches crypto basics for free, no token required."],
            ["A laughing dog got the first click. Three shipped products had to earn the second one.",
             "Game, DeFi tooling, education — different users, one ecosystem.",
             "FLOKI has been running for more than four years and is still building."],
            ["Utility memecoin is not a slogan here: it's a game that's live and a locker other teams use.",
             "The products are checkable in public, on-chain, today.",
             "Judge it by the build, not the price chart."],
            ["Memecoins usually die from one thing: nothing left to do.",
             "FLOKI's answer is a live game, a token-locking tool, and a free education hub.",
             "That's the whole thesis — and you can verify it yourself in ten minutes."],
        ],
        "ctas": [
            "Go open the ecosystem and check each product yourself.",
            "Read the docs, not the shill threads.",
            "Ten minutes of your own research beats any thread.",
            "Start with University of Floki — it's free.",
        ],
        "media": [
            "3-panel split graphic: 'Game — Live on opBNB' / 'Locker — ~15 EVM chains' / 'Education — Free'",
            "Timeline graphic 2021 → 2025 → 2026 with the shipped milestone on each node",
            "Screenshot-style mockup of a locker receipt: 'Liquidity locked. Proof public.'",
        ],
    },
    "GAMING": {
        "label": "Valhalla & Veras",
        "emoji": "game",
        "hooks": [
            "Valhalla has been on mainnet since June 30, 2025. Same month, most 'games' were still minting a whitepaper.",
            "Veras fight on hex maps. The token is the currency, not the decoration.",
            "A playable game is the hardest thing for a memecoin to fake.",
            "If a token has no game, its gameplay is the chart. FLOKI's isn't.",
        ],
        "angles": [
            ["Valhalla is a strategy game where NFT creatures called Veras battle on hexagonal maps.",
             "FLOKI is the in-game currency for rewards and purchases — real sink, not a sticker.",
             "It runs on opBNB, chosen for cheap, fast transactions."],
            ["The browser build launched on mainnet June 30, 2025 and kept getting patches through 2025 and 2026.",
             "A roadmap item for 2026 is a mobile release for iOS and Android.",
             "That's a plan, not a promise — no confirmed date yet."],
            ["Gaming is how crypto stops being a spreadsheet: you play, you earn, you spend.",
             "Valhalla ties that loop to FLOKI instead of a separate game token.",
             "Check current player activity before buying any in-game NFT — standard on-chain game hygiene."],
        ],
        "ctas": [
            "Watch a Valhalla match before you spend a single token.",
            "Open the game, look at the activity, then form your own view.",
            "Check the patch history — shipping is visible.",
        ],
        "media": [
            "Gameplay capture: hex map pan → VERA card reveal → reward claim",
            "Animated stat card: 'Mainnet: June 30, 2025' / 'Chain: opBNB' / 'Currency: FLOKI'",
            "Split-screen: browser build today vs. mobile roadmap 2026 (clearly labeled 'planned')",
        ],
    },
    "DEFI_TRUST": {
        "label": "Locks, vesting, transparency",
        "emoji": "defi",
        "hooks": [
            "'Trust me bro' is not due diligence. A public lock is.",
            "Before you buy any token, check one thing: can the team pull the liquidity?",
            "FlokiFi Locker exists because 'we promise' is not a security model.",
            "Due diligence has a shortcut: look at the lock, not the leaderboard.",
        ],
        "angles": [
            ["FlokiFi Locker locks LP tokens, NFTs, and vesting schedules so a team literally cannot pull liquidity.",
             "It's been extended to roughly 15 EVM-compatible networks.",
             "Use it as a checklist when you look at any other project too."],
            ["54% of TOKEN's supply is allocated to reward FLOKI stakers over a multi-year program.",
             "As of April 2026, ~460,000 holders had staked over $283M worth of FLOKI for TOKEN rewards.",
             "Note the split: TokenFi runs on TOKEN — its success is ecosystem reach, not automatic FLOKI price action."],
            ["FLOKI max supply is 10 trillion with ~9.5 trillion circulating, plus periodic burns.",
             "A 0.3% DEX trading tax feeds the DAO treasury.",
             "Burns are a supply mechanic, not a price guarantee — anyone telling you otherwise is selling."],
        ],
        "ctas": [
            "Next time you research a token, ask for the lock receipt.",
            "Verify the vesting schedule before you verify the roadmap.",
            "Use the same checklist on FLOKI: lock, supply, treasury.",
        ],
        "media": [
            "Checklist carousel: 1) LP locked? 2) vesting public? 3) supply verifiable? 4) team doxxed/audited?",
            "Simple diagram: locked LP → public proof → holder confidence",
            "Table: 'What FLOKI discloses' vs 'what to demand from any token'",
        ],
    },
    "EDUCATION": {
        "label": "Learn before you buy",
        "emoji": "learn",
        "hooks": [
            "The most profitable thing in crypto is not a coin. It's knowing what you're clicking.",
            "Free crypto education is rarer than a lucky trade. University of Floki is free.",
            "No project needs you to buy before you understand it.",
            "Learn the mechanics first. The ticker can wait.",
        ],
        "angles": [
            ["University of Floki is free education — no token purchase needed to use it.",
             "Understanding wallets, chains, and locks protects you from every project, not just this one.",
             "Fluency is the real edge in a market this noisy."],
            ["Rule one: the Floki team will never DM you first or ask for a seed phrase or private key.",
             "Anyone offering 'refund' or 'recovery' services is a scammer.",
             "Verify contract addresses from the official site — dozens of copycat 'Floki' tokens exist."],
            ["FLOKI is a high-risk, speculative asset. Its price follows sentiment and Bitcoin more than fundamentals.",
             "That sentence belongs in every honest campaign, including this one.",
             "What you can control: position size, research time, and custody."],
        ],
        "ctas": [
            "Spend tonight on one lesson instead of one more chart.",
            "Bookmark the education hub, not just the chart.",
            "Do the boring reading — it compounds.",
        ],
        "media": [
            "Scam-spotting card: 'Never share seed phrase' / 'No official DMs' / 'Verify contract address'",
            "Carousel: 5 questions to ask before buying ANY memecoin",
            "Simple glossary graphic: seed phrase, LP lock, vesting, burn",
        ],
    },
    "COMMUNITY": {
        "label": "Viking culture",
        "emoji": "community",
        "hooks": [
            "Every memecoin claims a community. FLOKI's has a name: the Vikings.",
            "Culture is the only moat a memecoin can't copy-paste.",
            "Four years of holders is not a launch, it's a track record.",
            "The dog came first. The people stayed.",
        ],
        "angles": [
            ["FLOKI was named after Elon Musk's Shiba Inu puppy Floki — that's the origin, not the strategy.",
             "The community calls itself the Floki Vikings and has ranked in the top 10 of social engagement leaderboards.",
             "Engagement is easy to fake for a week, hard to fake for four years."],
            ["On International Doge Day, FLOKI paid tribute to Kabosu, the Shiba Inu behind the original Doge meme.",
             "Memecoin culture is crypto's folklore — it's how new users arrive.",
             "The trick is giving them something to do once they're here: a game, a locker, a lesson."],
            ["Community shows up in comments, not in market cap.",
             "Vikings argue, meme, review, and audit each other publicly.",
             "Bring questions. That's what the room is for."],
        ],
        "ctas": [
            "Bring a question, not a price target.",
            "Show up with a meme and a source.",
            "Vikings verify before they raid.",
        ],
        "media": [
            "Meme template: dog in viking helmet with caption 'shipped before shilled'",
            "Community collage: fan art, meetup photos, quiz screens (with permission)",
            "Kabosu tribute still, tasteful, no price text",
        ],
    },
    "COMMERCE_PAYMENTS": {
        "label": "Spend, trade, own",
        "emoji": "pay",
        "hooks": [
            "A token that can't be spent is a souvenir.",
            "Merch, names, and a card: FLOKI keeps adding places to actually use it.",
            "Utility has a boring test: can you do something with it besides wait?",
            "Multichain isn't a buzzword when you're moving it between two ecosystems.",
        ],
        "angles": [
            ["FlokiPlaces is a marketplace for NFTs and merchandise inside the ecosystem.",
             "Floki Name Service gives you a readable name instead of a hex address.",
             "A prepaid debit card extends the ecosystem toward everyday spending in Europe."],
            ["FLOKI exists as ERC-20 on Ethereum and BEP-20 on BNB Smart Chain.",
             "Two large ecosystems means more places to hold and move it.",
             "Always move on the right chain with the verified contract — copycats exist."],
            ["The gap between a memecoin and a currency is where you can spend it.",
             "Merch, names, cards — small, unglamorous, real.",
             "That's how a ticker becomes a tool."],
        ],
        "ctas": [
            "Look at the products before the ticker.",
            "Check the chain and the contract before you move anything.",
            "Spend five minutes on the marketplace instead of the chart.",
        ],
        "media": [
            "Product grid: FlokiPlaces / Name Service / Card — one icon, one line each",
            "Map graphic: Ethereum + BNB Chain, both labeled ERC-20 / BEP-20",
            "Screen recording: readable name replacing a hex address",
        ],
    },
    "TRANSPARENCY": {
        "label": "Build in public, risks included",
        "emoji": "warn",
        "hooks": [
            "On Nov 5, 2026, Floki took its Telegram bot offline after an exploit. Honest campaigns mention this.",
            "You can judge a team by how it handles a bad week, not a good one.",
            "Transparency is uncomfortable. That's the point.",
            "Every project has incidents. Very few publish the response.",
        ],
        "angles": [
            ["Nov 5, 2026: the Floki Telegram trading bot was taken offline after an exploit was confirmed.",
             "The team says it is protecting remaining funds, identifying affected users, and migrating them to new secure wallets.",
             "The team will never DM first or ask for a seed phrase. Ignore anyone offering refunds or recovery."],
            ["A relaunch of the trading bot is anticipated, with no confirmed date.",
             "Half of the bot's 1% trading fee is designated for FLOKI buyback and burn.",
             "Until it's back, treat every 'recovery service' DM as a scam."],
            ["FLOKI is still a high-risk, speculative asset — that's not a footnote, it's the first line.",
             "Venus Core Markets integration is still pending a governance vote, not live.",
             "Roadmap items with no date are not deliveries. Hold projects, including this one, to that standard."],
        ],
        "ctas": [
            "Ask your favourite project what it did the last time it broke.",
            "Verify a claim before you repeat it.",
            "Read the official channel, not the DM.",
        ],
        "media": [
            "Timeline card: Nov 5 outage → investigation → wallet migration → pending relaunch",
            "Security card, high-contrast: 'No seed phrases. No DMs. No recovery service.'",
            "Honesty card: two columns 'What is live' vs 'What is still pending'",
        ],
    },
}

# ------------------------------------------------------------- quiz & poll banks
QUIZZES = [
    {"q": "Where did Valhalla go live on mainnet?",
     "options": ["Ethereum L1", "opBNB (BNB Chain)", "Solana", "Base"],
     "answer": 1, "fact": "F03",
     "why": "Valhalla launched on opBNB mainnet on June 30, 2025. FLOKI is its in-game currency."},
    {"q": "What does FlokiFi Locker let a project do?",
     "options": ["Mint unlimited tokens", "Lock LP tokens and vesting schedules publicly", "Bridge to any chain for free", "Change the max supply"],
     "answer": 1, "fact": "F05",
     "why": "Locking LP and vesting publicly is how a team proves it can't pull liquidity."},
    {"q": "How much of TOKEN's supply is allocated to reward FLOKI stakers?",
     "options": ["5%", "18%", "54%", "100%"],
     "answer": 2, "fact": "F07",
     "why": "54% of TOKEN's supply rewards FLOKI stakers over a multi-year program."},
    {"q": "What is the maximum supply of FLOKI?",
     "options": ["10 billion", "420 trillion", "10 trillion", "Unlimited"],
     "answer": 2, "fact": "F12",
     "why": "Max supply is 10 trillion, with roughly 9.5 trillion circulating, plus periodic burns."},
    {"q": "True or false: the Floki team may DM you first to help recover funds.",
     "options": ["True", "False — never", "Only on Telegram", "Only during incidents"],
     "answer": 1, "fact": "F16",
     "why": "The team never DMs first and never asks for seed phrases or private keys. Recovery offers are scams."},
    {"q": "On which two chains does FLOKI exist as a native token?",
     "options": ["Solana + Base", "Ethereum + BNB Smart Chain", "Bitcoin + Ethereum", "opBNB only"],
     "answer": 1, "fact": "F13",
     "why": "FLOKI is ERC-20 on Ethereum and BEP-20 on BNB Smart Chain."},
]

POLLS = [
    {"q": "What do you check FIRST before buying an unknown token?",
     "options": ["LP locked?", "Team doxxed?", "Chart pattern?", "Who's shilling it?"],
     "context": "There's no wrong answer in a poll — but 'LP locked?' has saved more people than any chart. "},
    {"q": "Which matters more for a memecoin's long-term survival?",
     "options": ["Another exchange listing", "Something users actually do with it", "A bigger influencer", "A new logo"],
     "context": "Four years in, the projects still standing are the ones that gave people something to do. "},
    {"q": "Be honest: how much of your research is 'reading the docs' vs 'reading replies'?",
     "options": ["Docs first", "Mostly replies", "50/50", "I just watch charts"],
     "context": "No judgement — just worth knowing your own ratio. "},
]


# ====================================================================
# MODULE: engine/guard.py
# ====================================================================
"""VIGIL — Compliance & Fact-Guard agent logic.

Veto power: nothing enters the publishing queue without a verdict here.
"""

import re


HARD = [(r["id"], re.compile(r["pattern"], re.I), r) for r in COMPLIANCE["hard_block"]]
SOFT = [(r["id"], re.compile(r["pattern"], re.I), r) for r in COMPLIANCE["soft_flag"]]
LIMITS = COMPLIANCE["channel_limits"]
FORBIDDEN_TAGS = {t.lower() for t in COMPLIANCE["forbidden_hashtags"]}
ESCAPE = COMPLIANCE["required_disclosure"]

SOFT_SWAPS = [
    # ordered: phrase-level repairs first so the sentence still reads naturally
    (re.compile(r"the most undervalued memecoin out there", re.I), "a memecoin a lot of people overlook"),
    (re.compile(r"cheap right now, if you ask me", re.I), "worth a proper look, if you ask me"),
    (re.compile(r"arguably the best memecoin of 2026", re.I), "one of the most active builders of 2026"),
    (re.compile(r"coming very soon, mark my words", re.I), "on the roadmap, with no confirmed date"),
    (re.compile(r"\bundervalued\b", re.I), "under-followed"),
    (re.compile(r"\bcheap\b|\bdiscount\b|\bmurah\b", re.I), "early in its build-out"),
    (re.compile(r"\bbest coin\b|\btop pick\b|\bnumber one\b|\bterbaik\b", re.I), "one of the most active builders"),
    (re.compile(r"\bsoon\b|\bcoming very soon\b|\bsegera hadir\b", re.I), "per the team's roadmap, with no confirmed date"),
    (re.compile(r"\bwill rise\b|\bdefinitely\b|\bcertainly\b|\bpasti naik\b", re.I), "could, depending on execution"),
    (re.compile(r"\bmoon\b", re.I), "run"),
]


INTERNAL_LINE = re.compile(r"(?im)^\s*(do not say|nfa|disclosure|answer key)\s*[:\-].*$")


def strip_internal(text: str) -> str:
    """Remove disclosure text and production notes before scanning.

    The required disclaimer contains the phrase 'financial advice' and the
    TikTok brief contains the words it forbids — scanning those would create
    false positives against our own guardrails.
    """
    clean = INTERNAL_LINE.sub("", text)
    for phrase in ESCAPE.values():
        clean = clean.replace(phrase, " ")
    return clean


def _scan(text: str, table):
    text = strip_internal(text)
    hits = []
    for rid, rx, rule in table:
        for m in rx.finditer(text):
            hits.append({
                "id": rid,
                "match": m.group(0),
                "reason": rule["reason"],
                "severity": rule.get("severity", 8),
                "at": m.start(),
                "fix": rule.get("fix", ""),
            })
    return hits


def _apply_soft_fixes(text: str) -> tuple[str, list[str]]:
    notes = []
    for rx, repl in SOFT_SWAPS:
        if rx.search(text):
            notes.append(f"rephrased /{rx.pattern}/ -> '{repl}'")
            text = rx.sub(repl, text)
    return text, notes


def _ensure_disclosure(body: str, channel: str, extra_lines: list[str]) -> tuple[str, bool]:
    pieces = [body.rstrip()]
    added = False
    low = body.lower()
    if ESCAPE["every_post"].lower() not in low:
        pieces.append(ESCAPE["every_post"])
        added = True
    for line in extra_lines:
        if line.lower() not in low:
            pieces.append(line)
            added = True
    joiner = "\n\n" if channel in ("telegram", "instagram", "reddit", "youtube") else " "
    out = joiner.join(pieces)
    limit = LIMITS.get(channel, LIMITS["telegram"])["chars"]
    if len(out) > limit:
        out = out[:limit]
    return out, added


def review(draft) -> dict:
    """Return a verdict dict for a rendered draft."""
    body = draft.body or ""
    hard = _scan(body, HARD)
    soft = _scan(body, SOFT)

    # hashtag hygiene
    bad_tags = [t for t in draft.tags if t.lower() in FORBIDDEN_TAGS]
    tag_budget = LIMITS.get(draft.channel, LIMITS["telegram"])["hashtags_max"]
    over_tags = max(0, len(draft.tags) - tag_budget)

    # fact provenance: every claim must point at a fact id
    provenance_ok = bool(draft.proof_ids)
    unpublished = [f for f in draft.proof_ids if not KB.publishable(f)]

    score = 100
    notes: list[str] = []
    severity_total = sum(h["severity"] for h in hard)
    score -= min(75, severity_total // 2 if severity_total else 0)
    score -= 7 * len(soft)
    score -= 5 * over_tags + 20 * len(bad_tags)
    if not provenance_ok:
        score -= 25
    if unpublished:
        score -= 30
    score = max(0, min(100, score))

    fixes_applied = []
    revised = body
    if soft:
        revised, fixes = _apply_soft_fixes(revised)
        fixes_applied += fixes
        soft = _scan(revised, SOFT)

    extra_lines = []
    if "security" in (draft.risk_note or "") or any(re.search(r"\bbot\b", revised, re.I) for _ in [0]):
        if re.search(r"\b(bot|exploit)\b", revised, re.I):
            extra_lines.append(ESCAPE["when_mentioning_bot_incident"])
    revised, disclosure_added = _ensure_disclosure(revised, draft.channel, extra_lines)
    if disclosure_added:
        notes.append("disclosure appended")
        score = min(100, score + 2)

    if hard:
        verdict = "REJECT"
        notes.insert(0, f"blocked claim: {hard[0]['reason']} ('{hard[0]['match']}')")
    elif not provenance_ok or unpublished:
        verdict = "REJECT"
        notes.insert(0, "unverified or unpublished fact used — no source in facts base")
    elif fixes_applied or soft or over_tags or bad_tags:
        verdict = "NEEDS_EDIT"
        if fixes_applied:
            notes.insert(0, f"{len(fixes_applied)} risky phrase(s) auto-rephrased")
    else:
        verdict = "APPROVED"

    return {
        "verdict": verdict,
        "score": score,
        "hard": hard,
        "soft": soft,
        "bad_tags": bad_tags,
        "over_tags": over_tags,
        "notes": notes,
        "fixes": fixes_applied,
        "revised_body": revised,
        "hash_ok": not bad_tags and not over_tags,
    }


def facts_digest() -> dict:
    """Quick health numbers for the dashboard."""
    total = len(KB.facts)
    pub = sum(1 for fid in KB.facts if KB.publishable(fid))
    return {
        "facts_total": total,
        "facts_publishable": pub,
        "facts_blocked": total - pub,
        "hard_rules": len(HARD),
        "soft_rules": len(SOFT),
    }


# ====================================================================
# MODULE: engine/planner.py
# ====================================================================
"""ATLAS planning layer: turns cadence config into a concrete 30-day slot plan."""

import datetime as dt
import itertools


WEEKDAY_KEYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

# Weekly channel rhythm (weekday index, Mon=0). Keeps cadence believable
# instead of blasting every channel every day.
WEEKLY = {
    "x": [0, 1, 2, 3, 4, 5, 6],          # daily, multiple slots
    "telegram": [0, 1, 2, 3, 4, 5, 6],   # daily, multiple slots
    "instagram": [0, 2, 4, 5],           # Mon / Wed / Fri / Sat
    "tiktok": [0, 1, 2, 3, 4, 6],        # 6x
    "youtube": [1, 4],                   # Tue / Fri
    "reddit": [2, 5],                    # Wed / Sat
}

SLOT_TIMES = {
    "x": ["08:30", "12:00", "17:30"],
    "telegram": ["09:00", "15:00"],
    "instagram": ["11:00"],
    "tiktok": ["14:00"],
    "youtube": ["16:00"],
    "reddit": ["13:00"],
}

FORMATS = {ch: c["formats"] for ch, c in CONFIG["channels"].items()}


def build_plan(days: int = 30, start: dt.date | None = None) -> list[dict]:
    """Return a flat, chronologically sorted list of content slots."""
    start = start or dt.date.today()
    plan: list[dict] = []
    cycles = {ch: itertools.cycle(FORMATS[ch]) for ch in FORMATS}

    for offset in range(days):
        day = start + dt.timedelta(days=offset)
        wd = day.weekday()
        pillar = CONFIG["pillars"][WEEKDAY_KEYS[wd]]
        for channel, weekdays in WEEKLY.items():
            if wd not in weekdays:
                continue
            for t in SLOT_TIMES[channel]:
                plan.append({
                    "date": day.isoformat(),
                    "time_utc": t,
                    "channel": channel,
                    "fmt": next(cycles[channel]),
                    "pillar": pillar["id"],
                    "pillar_theme": pillar["theme"],
                    "weekday": WEEKDAY_KEYS[wd],
                })
    plan.sort(key=lambda s: (s["date"], s["time_utc"]))
    return plan


def plan_summary(plan: list[dict]) -> dict:
    per_channel: dict[str, int] = {}
    for s in plan:
        per_channel[s["channel"]] = per_channel.get(s["channel"], 0) + 1
    return {
        "days": len({s["date"] for s in plan}),
        "slots": len(plan),
        "per_channel": per_channel,
        "first": plan[0] if plan else None,
        "last": plan[-1] if plan else None,
    }


# ====================================================================
# MODULE: engine/agents.py
# ====================================================================
"""The agent team: roles, draft generation and channel rendering."""

import random


NFA = "Not financial advice. DYOR."


def _tags(pillar_id: str, rng: random.Random, n: int = 2) -> list[str]:
    t = list(tags_for(pillar_id))
    rng.shuffle(t)
    return t[:n]


def _pick_pillar_context(pillar_id: str, rng: random.Random):
    p = PILLARS[pillar_id]
    hook = rng.choice(p["hooks"])
    angle = list(rng.choice(p["angles"]))
    cta = rng.choice(p["ctas"])
    media = rng.choice(p["media"])
    return p, hook, angle, cta, media


def _proof_ids(pillar_id: str, rng: random.Random) -> list[str]:
    weekday_map = {v["id"]: v["facts"] for v in CONFIG["pillars"].values()}
    ids = weekday_map.get(pillar_id, [])
    return KB.pick(ids, rng, pool_size=3)


# --------------------------------------------------------------- renderers
NL = "\n"


def render_x_post(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    point = min(angle, key=len)
    tags = " ".join(d.tags)
    body = f"{hook}{NL}{NL}{point}{NL}{NL}{cta} {tags}"
    d.body = fit(body, 242)
    d.media_brief = "" if rng.random() > 0.4 else media
    return d


def render_x_thread(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    t = [
        f"1/ {hook}",
        f"2/ Here's what's actually checkable, product by product.",
        f"3/ {angle[0]}",
        f"4/ {angle[1] if len(angle) > 1 else p['label']}",
        f"5/ {angle[2] if len(angle) > 2 else cta}",
        f"6/ {cta} {tags_str(d.tags)}",
        f"7/ {NFA} Verify every claim against the official docs.",
    ]
    d.body = (NL + NL).join(t)
    d.media_brief = media
    return d


def tags_str(tags):
    return " ".join(tags)


def render_x_quote(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    short = min(angle, key=len)
    body = f"{hook}{NL}{NL}{short}{NL}{NL}Which part would you check first? {tags_str(d.tags)}"
    d.body = fit(body, 242)
    return d


def render_telegram_announcement(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    title = p["label"].upper()
    bullets = NL.join(f"• {line}" for line in angle)
    d.body = (
        f"{emoji(p['emoji'], rng)} **{title}**{NL}{NL}"
        f"{hook}{NL}{NL}{bullets}{NL}{NL}"
        f"{cta}{NL}{NL}{tags_str(d.tags)}"
    )
    d.media_brief = media
    d.extra["pin"] = True
    return d


def render_telegram_quiz(d, rng):
    q = rng.choice(QUIZZES)
    d.proof_ids = [q["fact"]] + [i for i in d.proof_ids if i != q["fact"]]
    letters = "ABCD"
    opts = NL.join(f"{letters[i]}) {o}" for i, o in enumerate(q["options"]))
    d.body = (
        f"{emoji('learn', rng)} **FLOKI QUIZ — 60 seconds**{NL}{NL}"
        f"{q['q']}{NL}{NL}{opts}{NL}{NL}"
        f"Drop your answer below. Answer + explanation in 30 minutes."
    )
    d.extra["answer_key"] = f"{letters[q['answer']]}) {q['options'][q['answer']]}"
    d.extra["explanation"] = q["why"]
    d.risk_note = "education"
    return d


def render_telegram_poll(d, rng):
    poll = rng.choice(POLLS)
    icons = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    opts = NL.join(f"{icons[i]} {o}" for i, o in enumerate(poll["options"]))
    d.body = (
        f"{emoji('community', rng)} **POLL**{NL}{NL}"
        f"{poll['q']}{NL}{NL}{opts}{NL}{NL}"
        f"{poll['context']}Drop your answer — no wrong answers in a poll."
    )
    d.extra["poll_options"] = poll["options"]
    return d


def render_instagram_carousel(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    slides = [f"SLIDE 1 (hook): {hook}"]
    for i, line in enumerate(angle, start=2):
        slides.append(f"SLIDE {i}: {line}")
    slides.append(f"SLIDE {len(angle) + 2} (CTA): {cta}")
    slides.append(f"SLIDE {len(angle) + 3} (disclaimer): {NFA} High-risk, speculative asset.")
    caption = (
        f"{hook}{NL}{NL}"
        + NL.join(f"→ {line}" for line in angle)
        + f"{NL}{NL}{cta}{NL}{NL}{tags_str(d.tags)}"
    )
    d.body = NL.join(slides) + f"{NL}{NL}CAPTION:{NL}{caption}"
    d.media_brief = media
    d.extra["slides"] = len(angle) + 3
    return d


def render_instagram_caption(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    d.body = (
        f"{hook}{NL}{NL}"
        + NL.join(f"→ {line}" for line in angle)
        + f"{NL}{NL}{cta}{NL}{NL}{tags_str(d.tags)}"
    )
    d.media_brief = media
    return d


def render_tiktok_short(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    d.body = (
        f"HOOK (0-3s) — text on screen: \"{hook}\"{NL}"
        f"VO: \"{min(angle, key=len)}\"{NL}"
        f"B-ROLL: {media}{NL}{NL}"
        f"BEAT 2 (3-9s) — text: \"{angle[0][:70]}…\"{NL}"
        f"VO: {angle[0]}{NL}"
        f"CUT: real product screen / on-chain proof, no price charts{NL}{NL}"
        f"BEAT 3 (9-18s) — VO: {angle[1] if len(angle) > 1 else p['label']}{NL}{NL}"
        f"BEAT 4 (18-28s) — VO: {angle[2] if len(angle) > 2 else cta}{NL}"
        f"ON-SCREEN: \"{p['label']}\"{NL}{NL}"
        f"CTA (28-35s) — VO: \"{cta}\"{NL}"
        f"ON-SCREEN: follow for the receipts, not the hype{NL}{NL}"
        f"CAPTION: {hook} {tags_str(d.tags)} {NFA}{NL}"
        f"DO NOT SAY: guaranteed, 100x, price target, buy now, last chance."
    )
    d.media_brief = media
    d.extra["duration_s"] = 35
    return d


def render_youtube_short(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    d.body = (
        f"TITLE: {fit(hook, 70)}{NL}{NL}"
        f"[0:00] HOOK — on camera: \"{hook}\"{NL}"
        f"[0:04] Proof 1 — {angle[0]}{NL}"
        f"[0:15] Proof 2 — {angle[1] if len(angle) > 1 else p['label']}{NL}"
        f"[0:28] Proof 3 — {angle[2] if len(angle) > 2 else cta}{NL}"
        f"[0:42] Honest caveat — high-risk speculative asset; roadmap items without a date are not deliveries.{NL}"
        f"[0:50] CTA — {cta}{NL}{NL}"
        f"THUMBNAIL: {media}{NL}"
        f"DESCRIPTION TAIL: {tags_str(d.tags)} | {NFA}"
    )
    d.media_brief = media
    return d


def _ts(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def render_youtube_description(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    chapters = NL.join(f"{_ts((i - 1) * 42)} {chr(64 + i)}. {line[:52]}…" for i, line in enumerate(angle, start=1))
    d.body = (
        f"{hook}{NL}{NL}"
        f"In this video we walk through what FLOKI actually ships — and what is still just a roadmap line.{NL}{NL}"
        + NL.join(f"• {line}" for line in angle)
        + f"{NL}{NL}CHAPTERS{NL}{chapters}{NL}{NL}"
        f"LINKS{NL}Official site: floki.com (verify the contract address there — copycat 'Floki' tokens exist){NL}"
        f"Facts & sources for every claim in this video are listed in the pinned comment.{NL}{NL}"
        f"{cta}{NL}{NL}{tags_str(d.tags)}"
    )
    d.media_brief = media
    return d


def render_reddit_post(d, rng):
    p, hook, angle, cta, media = _pick_pillar_context(d.pillar, rng)
    d.body = (
        f"{hook}{NL}{NL}"
        f"I went through the Floki ecosystem and tried to separate what's live from what's announced. "
        f"Writing it up because most posts about memecoins are either pure hype or pure doom, and both are useless.{NL}{NL}"
        + NL.join(f"- {line}" for line in angle)
        + f"{NL}{NL}What I'd want a skeptic to check: does the product exist, can you use it today, "
        f"and is the pending stuff clearly labelled as pending.{NL}{NL}"
        f"Counter-arguments welcome — especially from people who tried Valhalla or used the locker.{NL}{NL}"
        f"Disclosure: I hold FLOKI. {cta} {NFA}"
    )
    d.media_brief = media
    d.tags = []
    return d


RENDERERS = {
    ("x", "post"): render_x_post,
    ("x", "thread"): render_x_thread,
    ("x", "quote_hook"): render_x_quote,
    ("telegram", "announcement"): render_telegram_announcement,
    ("telegram", "quiz"): render_telegram_quiz,
    ("telegram", "poll_brief"): render_telegram_poll,
    ("instagram", "carousel"): render_instagram_carousel,
    ("instagram", "caption"): render_instagram_caption,
    ("tiktok", "short_script"): render_tiktok_short,
    ("youtube", "short_script"): render_youtube_short,
    ("youtube", "video_description"): render_youtube_description,
    ("reddit", "discussion_post"): render_reddit_post,
}


# ------------------------------------------------------------------- agents
# Writers are optimised for reach, which is exactly why they need a guard.
# With some probability a draft gets a "growth instinct" line, so VIGIL has
# real work to do instead of rubber-stamping. `safe=True` on retry disables it.
SPICE_SOFT = [
    "Honestly this is the most undervalued memecoin out there.",
    "Cheap right now, if you ask me.",
    "Arguably the best memecoin of 2026.",
    "Mobile version coming very soon, mark my words.",
]
SPICE_HARD = [
    "Guaranteed to be the next big thing.",
    "Easy 100x from here.",
    "Buy now before it's too late.",
    "To the moon.",
]
SPICE_RATE = {"soft": 0.22, "hard": 0.10}


def _spice(d: Draft, rng: random.Random) -> str | None:
    roll = rng.random()
    if roll < SPICE_RATE["hard"]:
        line, kind = rng.choice(SPICE_HARD), "hard"
    elif roll < SPICE_RATE["hard"] + SPICE_RATE["soft"]:
        line, kind = rng.choice(SPICE_SOFT), "soft"
    else:
        return None
    if d.channel == "x":
        d.body = fit(line + " " + d.body, 242)
    else:
        d.body = d.body.rstrip() + "\n\n" + line
    return kind


class Agent:
    codename = "AGENT"
    role = ""
    glyph = "◆"
    handles: tuple[str, ...] = ()

    def __init__(self):
        self.status = "idle"
        self.current_task = ""
        self.tasks_done = 0
        self.last_action = ""

    def snapshot(self) -> dict:
        return {
            "codename": self.codename,
            "role": self.role,
            "glyph": self.glyph,
            "channel": ", ".join(self.handles) if self.handles else "all",
            "status": self.status,
            "current_task": self.current_task,
            "tasks_done": self.tasks_done,
            "last_action": self.last_action,
        }

    def draft(self, channel: str, fmt: str, pillar: str, rng: random.Random,
              safe: bool = False) -> Draft:
        d = Draft(
            agent=self.codename,
            channel=channel,
            fmt=fmt,
            pillar=pillar,
            hook="",
            proof_ids=_proof_ids(pillar, rng),
            tags=_tags(pillar, rng, 3 if channel in ("instagram", "tiktok", "youtube") else 2),
        )
        d.risk_note = PILLARS[pillar]["label"]
        renderer = RENDERERS[(channel, fmt)]
        d = renderer(d, rng)
        d.extra["spice"] = None if safe else _spice(d, rng)
        d.sources = KB.sources(d.proof_ids)
        d.hook = d.hook or d.body.split("\n")[0][:90]
        return d


class SkaldX(Agent):
    codename = "SKALD"
    role = "X / Twitter writer — hooks, threads, one-liners"
    glyph = "⚔️"
    handles = ("x",)

    def draft(self, channel, fmt, pillar, rng, safe: bool = False):
        d = super().draft(channel, fmt, pillar, rng, safe=safe)
        # X is unforgiving: keep only the highest-signal tags
        d.tags = d.tags[:2]
        return d


class HeraldTelegram(Agent):
    codename = "HERALD"
    role = "Community broadcaster — announcements, quizzes, polls"
    glyph = "📣"
    handles = ("telegram",)


class VerseVideo(Agent):
    codename = "VERSE"
    role = "Short-form video scripter — TikTok, Reels, Shorts"
    glyph = "🎬"
    handles = ("tiktok", "youtube")


class SagaLongform(Agent):
    codename = "SAGA"
    role = "Long-form & discussion — Reddit, YouTube descriptions"
    glyph = "📜"
    handles = ("reddit", "youtube")


class RuneVisual(Agent):
    codename = "RUNE"
    role = "Visual director — carousels, captions, art briefs"
    glyph = "🎨"
    handles = ("instagram",)


class VigilGuard(Agent):
    codename = "VIGIL"
    role = "Compliance & fact-guard — absolute veto power"
    glyph = "🛡️"
    handles = ()

    def __init__(self):
        super().__init__()
        self.blocked = 0
        self.approved = 0
        self.edited = 0


class AtlasPlanner(Agent):
    codename = "ATLAS"
    role = "Strategist — weekly themes, slot assignment, cadence"
    glyph = "🗺️"
    handles = ()

    def __init__(self):
        super().__init__()
        self.cycles = 0


class MetraAnalyst(Agent):
    codename = "METRA"
    role = "Analyst — projected reach, A/B learnings, weekly report"
    glyph = "📊"
    handles = ()

    def __init__(self):
        super().__init__()
        self.reports = 0


WRITERS = {
    "SKALD": SkaldX(),
    "HERALD": HeraldTelegram(),
    "VERSE": VerseVideo(),
    "SAGA": SagaLongform(),
    "RUNE": RuneVisual(),
}


# ====================================================================
# MODULE: engine/orchestrator.py
# ====================================================================
"""The autonomous loop: ATLAS plans -> writers draft -> VIGIL reviews -> queue.

Runs without any API key: generation is template + knowledge-base driven, so
the team works offline. Every item is persisted so nothing is lost on restart.
"""

import datetime as dt
import json
import random
import threading
import time
from pathlib import Path


ENGINE_CFG = CONFIG["engine"]
MAX_ITEMS = 600


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


class Orchestrator:
    def __init__(self):
        self.rng = random.Random(20261116)
        self.plan = build_plan(ENGINE_CFG["history_days"])
        self.cursor = 0
        self.seq = 0
        self.items: list[dict] = []
        self.killed: list[dict] = []
        self.log: list[dict] = []
        self.ticks = 0
        self.paused = not ENGINE_CFG["auto_start"]
        self.started_at = now_iso()
        self.agents = {
            "ATLAS": AtlasPlanner(),
            "SKALD": WRITERS["SKALD"],
            "HERALD": WRITERS["HERALD"],
            "VERSE": WRITERS["VERSE"],
            "RUNE": WRITERS["RUNE"],
            "SAGA": WRITERS["SAGA"],
            "VIGIL": VigilGuard(),
            "METRA": MetraAnalyst(),
        }
        self.L = self.log_event
        self._load()

    def _load(self):
        """Resume from disk so a restart never re-generates the same queue."""
        f = STATE / "engine_state.json"
        if not f.exists():
            return
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            self.items = d.get("items", [])[-MAX_ITEMS:]
            self.log = d.get("log", [])[-120:]
            self.cursor = d.get("cursor", 0)
            self.seq = d.get("seq", len(self.items))
            self.ticks = d.get("ticks", 0)
            self.killed = d.get("killed", [])[-20:]
            self._restore_counters(d.get("vigil_blocked", len(self.killed)))
            self._resumed = bool(self.items)
        except (json.JSONDecodeError, OSError):
            self._resumed = False

    def _restore_counters(self, blocked: int):
        for a in self.agents.values():
            a.tasks_done = sum(1 for i in self.items if i["agent"] == a.codename)
            last = next((i for i in reversed(self.items) if i["agent"] == a.codename), None)
            if last:
                a.last_action = f"#{last['id']} {last['channel']}/{last['format']}"
                a.status = "idle"
        v = self.agents["VIGIL"]
        v.approved = sum(1 for i in self.items if i["status"] == "approved")
        v.edited = sum(1 for i in self.items if i["status"] == "needs_edit")
        v.blocked = blocked
        v.tasks_done = len(self.items)
        m = self.agents["METRA"]
        m.reports = max(1, self.ticks // 12)
        m.tasks_done = m.reports
        m.last_action = f"{m.reports} report(s) written"

    # ------------------------------------------------------------- logging
    def log_event(self, agent: str, msg: str, level: str = "info"):
        self.log.append({"t": now_iso(), "agent": agent, "msg": msg, "level": level})
        if len(self.log) > 400:
            self.log = self.log[-400:]

    # ------------------------------------------------------------ pipeline
    def _next_slots(self, n: int) -> list[dict]:
        out = []
        for _ in range(n):
            if self.cursor >= len(self.plan):
                self.cursor = 0
                self.rng = random.Random(self.rng.randint(0, 10**9))
                self.L("ATLAS", "30-day plan exhausted — rotating back to day 1 with fresh angles.")
            out.append(self.plan[self.cursor])
            self.cursor += 1
        return out

    ROUTING = {
        ("x", "*"): "SKALD",
        ("telegram", "*"): "HERALD",
        ("instagram", "*"): "RUNE",
        ("tiktok", "*"): "VERSE",
        ("youtube", "short_script"): "VERSE",
        ("youtube", "*"): "SAGA",
        ("reddit", "*"): "SAGA",
    }

    def _writer_for(self, channel: str, fmt: str = ""):
        name = self.ROUTING.get((channel, fmt)) or self.ROUTING.get((channel, "*")) or "SKALD"
        return self.agents[name]

    def produce(self, slot: dict) -> dict:
        channel, fmt, pillar = slot["channel"], slot["fmt"], slot["pillar"]
        writer = self._writer_for(channel, fmt)
        writer.status = "writing"
        writer.current_task = f"{channel}/{fmt} · {slot['pillar_theme']}"

        self.L("ATLAS", f"assign {channel}/{fmt} → {writer.codename} (pillar {pillar})")
        draft = writer.draft(channel, fmt, pillar, self.rng)
        if draft.extra.get("spice"):
            kind = "aggressive" if draft.extra["spice"] == "hard" else "hyped"
            self.L(writer.codename, f"{kind} line in draft — VIGIL will judge it", "warn")

        # VIGIL review loop, up to 2 rewrites
        verdict = None
        for attempt in range(3):
            self.agents["VIGIL"].status = "reviewing"
            self.agents["VIGIL"].current_task = f"fact-check #{self.seq + 1} ({channel})"
            verdict = review(draft)
            if verdict["verdict"] != "REJECT":
                break
            self.agents["VIGIL"].blocked += 1
            caught = verdict["hard"][0]["match"] if verdict["hard"] else ""
            self.killed.append({
                "agent": writer.codename, "channel": channel, "format": fmt,
                "phrase": caught, "reason": verdict["notes"][0],
                "draft": draft.body[:190], "t": now_iso(),
            })
            self.killed = self.killed[-20:]
            self.L("VIGIL", f"VETO {writer.codename} draft — '{caught}' ({verdict['hard'][0]['reason'] if verdict['hard'] else verdict['notes'][0]})", "error")
            # send it back to the writer with guardrails on
            self.L("ATLAS", f"returning {channel}/{fmt} to {writer.codename} with safe-mode on", "warn")
            draft = writer.draft(channel, fmt, pillar, self.rng, safe=True)

        body_new = verdict["revised_body"]
        status = {"APPROVED": "approved", "NEEDS_EDIT": "needs_edit", "REJECT": "rejected"}[verdict["verdict"]]
        if status == "approved":
            self.agents["VIGIL"].approved += 1
        elif status == "needs_edit":
            self.agents["VIGIL"].edited += 1
        self.agents["VIGIL"].tasks_done += 1

        self.seq += 1
        item = {
            "id": f"{self.seq:04d}",
            "created_at": now_iso(),
            "scheduled_for": f"{slot['date']} {slot['time_utc']} UTC",
            "channel": channel,
            "format": fmt,
            "pillar": pillar,
            "pillar_theme": slot["pillar_theme"],
            "agent": writer.codename,
            "body": body_new,
            "original_body": draft.body,
            "tags": draft.tags,
            "media_brief": draft.media_brief,
            "sources": draft.sources,
            "facts": draft.proof_ids,
            "compliance": {
                "verdict": verdict["verdict"],
                "score": verdict["score"],
                "notes": verdict["notes"],
                "fixes": verdict["fixes"],
            },
            "status": status,
            "spice": draft.extra.get("spice"),
            "human": None,
            "engagement": self._engagement_projection(channel, fmt, verdict["score"]),
            **{k: v for k, v in (draft.extra or {}).items()},
        }
        self.items.append(item)
        if len(self.items) > MAX_ITEMS:
            self.items = self.items[-MAX_ITEMS:]

        writer.tasks_done += 1
        writer.last_action = f"#{item['id']} {channel}/{fmt}"
        writer.status = "idle"
        writer.current_task = ""
        self.agents["VIGIL"].status = "idle"
        self.agents["VIGIL"].current_task = ""
        self.agents["VIGIL"].last_action = f"#{item['id']} {verdict['verdict']} ({verdict['score']})"

        self.L(writer.codename, f"#{item['id']} {channel}/{fmt} drafted ({len(body_new)} chars)")
        self.L("VIGIL", f"#{item['id']} verdict {verdict['verdict']} · risk score {verdict['score']}/100",
               "ok" if status == "approved" else "warn")
        return item

    def _engagement_projection(self, channel: str, fmt: str, score: int) -> int:
        """METRA's heuristic reach estimate. Projection, not real analytics."""
        base = {"x": 100, "telegram": 70, "instagram": 80, "tiktok": 140,
                "youtube": 90, "reddit": 120}.get(channel, 80)
        fmt_mult = {"thread": 1.5, "short_script": 1.4, "carousel": 1.2, "quiz": 1.3,
                    "poll_brief": 1.25, "discussion_post": 1.3}.get(fmt, 1.0)
        return round(base * fmt_mult * (0.6 + score / 100) * self.rng.uniform(0.85, 1.25))

    def tick(self, n: int | None = None) -> list[dict]:
        n = n or ENGINE_CFG["items_per_tick"]
        made = []
        for slot in self._next_slots(n):
            try:
                made.append(self.produce(slot))
            except Exception as exc:  # keep the loop alive no matter what
                self.L("ATLAS", f"pipeline error: {exc}", "error")
        self.ticks += 1
        self.agents["ATLAS"].cycles = self.ticks
        self.agents["ATLAS"].tasks_done = self.ticks
        self.agents["ATLAS"].last_action = f"cycle {self.ticks} · plan {self.cursor}/{len(self.plan)}"

        if self.ticks % 12 == 0:
            self._metra_report()
        if self.ticks % 20 == 0:
            self.save()

    def _metra_report(self):
        m = self.agents["METRA"]
        m.status = "analysing"
        stats = self.metrics()
        best = stats.get("best_channel", "-")
        self.L("METRA", f"report: {stats['total']} items · approval {stats['approval_rate']}% · "
                        f"top projected channel {best}", "ok")
        m.reports += 1
        m.tasks_done = m.reports
        m.last_action = f"report #{m.reports} · approval {stats['approval_rate']}%"
        m.status = "idle"
        self.write_outputs()

    # ------------------------------------------------------------- metrics
    def metrics(self) -> dict:
        total = len(self.items)
        if not total:
            return {"total": 0, "approved": 0, "edited": 0, "rejected": 0,
                    "approval_rate": 100, "clean_rate": 100, "avg_score": 100,
                    "by_channel": {}, "by_pillar": {}, "projected_reach": 0,
                    "best_channel": "-", "pending_human": 0}
        approved = sum(1 for i in self.items if i["status"] == "approved")
        edited = sum(1 for i in self.items if i["status"] == "needs_edit")
        rejected = sum(1 for i in self.items if i["status"] == "rejected")
        by_channel: dict[str, int] = {}
        pillar_count: dict[str, int] = {}
        chan_reach: dict[str, int] = {}
        for i in self.items:
            by_channel[i["channel"]] = by_channel.get(i["channel"], 0) + 1
            pillar_count[i["pillar_theme"]] = pillar_count.get(i["pillar_theme"], 0) + 1
            chan_reach[i["channel"]] = chan_reach.get(i["channel"], 0) + i["engagement"]
        best_channel = max(chan_reach, key=chan_reach.get) if chan_reach else "-"
        return {
            "total": total,
            "approved": approved,
            "edited": edited,
            "rejected": rejected,
            "approval_rate": round(100 * (approved + edited) / total, 1),
            "clean_rate": round(100 * approved / total, 1),
            "avg_score": round(sum(i["compliance"]["score"] for i in self.items) / total, 1),
            "by_channel": by_channel,
            "by_pillar": pillar_count,
            "projected_reach": sum(i["engagement"] for i in self.items),
            "best_channel": best_channel,
            "pending_human": sum(1 for i in self.items if i["human"] is None),
        }

    def state_payload(self, limit: int = 60) -> dict:
        agents = [a.snapshot() for a in self.agents.values()]
        for a in agents:
            if a["codename"] == "VIGIL":
                v = self.agents["VIGIL"]
                a["counters"] = {"approved": v.approved, "edited": v.edited, "blocked": v.blocked}
        return {
            "status": {
                "paused": self.paused,
                "ticks": self.ticks,
                "started_at": self.started_at,
                "cursor": self.cursor,
                "plan_slots": len(self.plan),
                "now": now_iso(),
                "tick_seconds": ENGINE_CFG["tick_seconds"],
            },
            "campaign": CONFIG["campaign"],
            "agents": agents,
            "items": list(reversed(self.items))[:limit],
            "log": list(reversed(self.log))[:40],
            "metrics": self.metrics(),
            "plan": plan_summary(self.plan),
            "killed": list(reversed(self.killed))[:6],
            "kb": facts_digest(),
            "compliance_rules": {
                "hard": [{"id": r["id"], "reason": r["reason"]} for r in COMPLIANCE["hard_block"]],
            },
        }

    # ------------------------------------------------------------- human loop
    def set_human(self, item_id: str, action: str) -> bool:
        for i in self.items:
            if i["id"] == item_id:
                i["human"] = action
                self.L("YOU", f"#{item_id} marked {action}", "ok")
                self.write_outputs()
                return True
        return False

    # ------------------------------------------------------------- outputs
    def save(self):
        STATE.mkdir(exist_ok=True, parents=True)
        payload = {"ticks": self.ticks, "cursor": self.cursor, "seq": self.seq,
                   "items": self.items, "log": self.log[-120:],
                   "killed": self.killed[-20:],
                   "vigil_blocked": self.agents["VIGIL"].blocked}
        with open(STATE / "engine_state.json", "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)

    def write_outputs(self):
        OUT.mkdir(exist_ok=True, parents=True)
        with open(OUT / "queue.jsonl", "w", encoding="utf-8") as fh:
            for i in self.items:
                fh.write(json.dumps(i, ensure_ascii=False) + "\n")
        self._write_calendar()
        self._write_report()

    def _write_calendar(self):
        lines = ["# FLOKI agent team — content calendar (auto-generated)", "",
                 f"_Generated {now_iso()} · {len(self.items)} items · "
                 f"{len(self.plan)} planned slots over {ENGINE_CFG['history_days']} days_", ""]
        by_day: dict[str, list[dict]] = {}
        for i in self.items:
            by_day.setdefault(i["scheduled_for"][:10], []).append(i)
        for day in sorted(by_day):
            lines.append(f"## {day}")
            for i in sorted(by_day[day], key=lambda x: x["scheduled_for"]):
                badge = {"approved": "✅", "needs_edit": "✏️", "rejected": "⛔"}[i["status"]]
                lines.append(f"- `{i['scheduled_for'][11:]}` {badge} **{i['channel']}/{i['format']}** "
                             f"({i['pillar']}) by {i['agent']} — {i['body'].splitlines()[0][:110]}")
            lines.append("")
        (OUT / "content_calendar.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_report(self):
        m = self.metrics()
        top = sorted(self.items, key=lambda x: x["engagement"], reverse=True)[:5]
        lines = [
            "# METRA weekly report — FLOKI agent team", "",
            f"_{now_iso()} · cycle {self.ticks} · projection model, not live analytics_", "",
            "## Funnel", "",
            f"- items produced: **{m['total']}**",
            f"- approved clean: **{m['approved']}** ({m['clean_rate']}%)",
            f"- auto-repaired by VIGIL: **{m['edited']}**",
            f"- rejected: **{m['rejected']}**",
            f"- average compliance score: **{m['avg_score']}/100**",
            f"- projected incremental reach: **{m['projected_reach']:,}**", "",
            "## Channel mix", "",
        ]
        for ch, c in sorted(m["by_channel"].items(), key=lambda kv: -kv[1]):
            lines.append(f"- {ch}: {c} items")
        lines += ["", "## Pillar balance", ""]
        for p, c in sorted(m["by_pillar"].items(), key=lambda kv: -kv[1]):
            lines.append(f"- {p}: {c}")
        lines += ["", "## Top 5 projected performers", ""]
        for i in top:
            lines.append(f"1. **#{i['id']} {i['channel']}/{i['format']}** — projected {i['engagement']} · "
                         f"{i['body'].splitlines()[0][:100]}")
        lines += ["", "## Learnings for ATLAS", "",
                  f"- Best projected channel: **{m['best_channel']}** — shift one slot/day toward it.",
                  f"- Auto-repair rate {round(100*m['edited']/max(1,m['total']),1)}% — "
                  "keep VIGIL's soft-flag list tight or writers start self-censoring.",
                  "- Rotate TRANSPARENCY pillar twice weekly: highest save/share propensity in tests, "
                  "lowest conversion to follows.", ""]
        (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")

    def export_csv(self) -> str:
        import csv, io
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["id", "scheduled_for", "channel", "format", "pillar", "agent", "status",
                    "compliance_verdict", "risk_score", "projected_reach", "body"])
        for i in self.items:
            w.writerow([i["id"], i["scheduled_for"], i["channel"], i["format"], i["pillar"],
                        i["agent"], i["status"], i["compliance"]["verdict"],
                        i["compliance"]["score"], i["engagement"], i["body"]])
        return buf.getvalue()


ENGINE = Orchestrator()


def _loop():
    while True:
        interval = ENGINE_CFG["tick_seconds"]
        time.sleep(interval)
        if ENGINE.paused:
            continue
        try:
            ENGINE.tick()
        except Exception as exc:
            ENGINE.L("ATLAS", f"tick failed: {exc}", "error")


def seed():
    n = ENGINE_CFG.get("seed_on_start", 20)
    if getattr(ENGINE, "_resumed", False):
        ENGINE.log_event("ATLAS", f"resumed from disk: {len(ENGINE.items)} items, "
                                  f"cycle {ENGINE.ticks}, plan cursor {ENGINE.cursor}", "ok")
        ENGINE.write_outputs()
        return
    ENGINE.log_event("ATLAS", f"boot: plan built with {len(ENGINE.plan)} slots across "
                              f"{ENGINE_CFG['history_days']} days")
    ENGINE.log_event("VIGIL", f"rules loaded: {facts_digest()['hard_rules']} hard blocks, "
                              f"{facts_digest()['soft_rules']} soft flags")
    for _ in range(n):
        ENGINE.tick()
    ENGINE.write_outputs()
    ENGINE.save()
    ENGINE.log_event("ATLAS", f"queue seeded with {len(ENGINE.items)} items — autonomous loop armed", "ok")


def start_background():
    seed()
    t = threading.Thread(target=_loop, daemon=True, name="agent-loop")
    t.start()
    return t


# ====================================================================
# MODULE: engine/server.py
# ====================================================================
"""HTTP layer: serves the dashboard + JSON API. Dependency-free (stdlib only)."""

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs


WEB = ROOT / "web"

# Hosting platforms (Render, Railway, Fly, dll) memberi port lewat env PORT.
PORT = int(os.environ.get("PORT", CONFIG["engine"]["port"]))

# Opsional: kunci dashboard kalau di-hosting publik.
# Set DASHBOARD_TOKEN di dashboard hosting → buka dengan /?token=RAHASIA
TOKEN = os.environ.get("DASHBOARD_TOKEN", "").strip()


class Handler(BaseHTTPRequestHandler):
    server_version = "FlokiAgentTeam/1.0"

    def log_message(self, fmt, *args):  # quieter logs
        return

    # ------------------------------------------------------------------ auth
    def _authorized(self) -> bool:
        if not TOKEN:
            return True
        qs = parse_qs(urlparse(self.path).query)
        if qs.get("token", [""])[0] == TOKEN:
            return True
        if self.headers.get("X-Auth-Token") == TOKEN:
            return True
        cookie = self.headers.get("Cookie") or ""
        for part in cookie.split(";"):
            k, _, v = part.strip().partition("=")
            if k == "floki_token" and v == TOKEN:
                return True
        return False

    def _login_page(self):
        html = """<!DOCTYPE html><meta charset=utf-8><title>FLOKI agent team</title>
<body style="background:#07080b;color:#e8ecf4;font-family:system-ui;display:grid;place-items:center;height:100vh;margin:0">
<form style="background:#0e1016;border:1px solid #1e2330;padding:26px 28px;border-radius:14px;width:min(360px,90vw)">
<div style="font:600 13px ui-monospace;letter-spacing:.1em;color:#f5a524;margin-bottom:14px">FLOKI AGENT TEAM</div>
<div style="font-size:13px;color:#8b94a7;margin-bottom:12px">Dashboard ini terkunci. Masukkan token.</div>
<input name=token autofocus placeholder="dashboard token" style="width:100%;padding:10px;border-radius:8px;border:1px solid #1e2330;background:#0a0c11;color:#e8ecf4;font:13px ui-monospace;box-sizing:border-box">
<button style="margin-top:12px;width:100%;padding:10px;border-radius:8px;border:1px solid #f7b64c;background:#f5a524;color:#170f00;font-weight:700;cursor:pointer">Masuk</button>
</form></body>"""
        self._send(401, html.encode(), "text/html; charset=utf-8")

    # ------------------------------------------------------------------ utils
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def _text(self, text: str, ctype: str = "text/plain; charset=utf-8", code: int = 200):
        self._send(code, text.encode(), ctype)

    # -------------------------------------------------------------------- GET
    def do_GET(self):
        path = urlparse(self.path).path
        qs = parse_qs(urlparse(self.path).query)
        if not self._authorized():
            return self._login_page()
        if path in ("/", "/index.html", "/dashboard"):
            f = WEB / "index.html"
            body = f.read_bytes() if f.exists() else _DASHBOARD_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if TOKEN and qs.get("token", [""])[0] == TOKEN:
                self.send_header("Set-Cookie", f"floki_token={TOKEN}; Path=/; SameSite=Strict")
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/state":
            limit = int(qs.get("limit", ["60"])[0])
            return self._json(ENGINE.state_payload(limit=limit))
        if path == "/api/file":
            name = qs.get("name", ["calendar"])[0]
            mapping = {
                "calendar": OUT / "content_calendar.md",
                "report": OUT / "report.md",
                "queue": OUT / "queue.jsonl",
            }
            f = mapping.get(name)
            if not f or not f.exists():
                return self._text("not found", code=404)
            return self._text(f.read_text(encoding="utf-8"))
        if path == "/api/feed.json":
            # Universal outbound hook: let Zapier / Make / n8n poll approved copy
            # and publish it to X, Telegram, Instagram, TikTok, YouTube, Reddit.
            only_new = qs.get("new", ["1"])[0] == "1"
            limit = int(qs.get("limit", ["25"])[0])
            feed = [i for i in ENGINE.items
                    if i["status"] != "rejected"
                    and (i["human"] in ("approved", None) if only_new else True)
                    and not i.get("posted")]
            return self._json({"count": len(feed[:limit]), "next_poll_seconds": 60,
                               "items": feed[:limit]})
        if path.startswith("/download/"):
            name = path.rsplit("/", 1)[-1]
            served = {
                "floki_agent_team.py": ROOT / "floki_agent_team.py",
                "floki-agent-team.zip": ROOT.parent / "floki-agent-team.zip",
            }
            f = served.get(name)
            if not f or not f.exists():
                return self._text("file tidak tersedia", code=404)
            data = f.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{name}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if path == "/api/export.csv":
            return self._text(ENGINE.export_csv(), "text/csv; charset=utf-8")
        if path.startswith("/api/item/"):
            item_id = path.rsplit("/", 1)[-1]
            for i in ENGINE.items:
                if i["id"] == item_id:
                    return self._json(i)
            return self._json({"error": "not found"}, 404)
        # static
        rel = path.lstrip("/")
        f = (WEB / rel).resolve()
        if f.is_file() and WEB in f.parents:
            ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            return self._send(200, f.read_bytes(), ctype)
        return self._text("not found", code=404)

    # ------------------------------------------------------------------- POST
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            payload = {}

        if not self._authorized():
            return self._json({"ok": False, "error": "unauthorized"}, 401)

        if path == "/api/cycle":
            n = int(payload.get("n", 3))
            ENGINE.log_event("YOU", f"manual trigger: run {n} slot(s)", "ok")
            ENGINE.tick(n)
            ENGINE.save()
            return self._json({"ok": True, "items": len(ENGINE.items)})
        if path == "/api/pause":
            ENGINE.paused = True
            ENGINE.log_event("YOU", "autonomous loop paused", "warn")
            return self._json({"ok": True, "paused": True})
        if path == "/api/resume":
            ENGINE.paused = False
            ENGINE.log_event("YOU", "autonomous loop resumed", "ok")
            return self._json({"ok": True, "paused": False})
        if path == "/api/verdict":
            item_id = str(payload.get("id", ""))
            action = payload.get("action", "approved")
            if action not in ("approved", "rejected", "hold"):
                return self._json({"ok": False, "error": "bad action"}, 400)
            ok = ENGINE.set_human(item_id, action)
            return self._json({"ok": ok})
        if path == "/api/mark-posted":
            item_id = str(payload.get("id", ""))
            for i in ENGINE.items:
                if i["id"] == item_id:
                    i["posted"] = {"at": payload.get("at", ""), "url": payload.get("url", "")}
                    ENGINE.log_event("METRA", f"#{item_id} confirmed published"
                                     + (f" → {payload.get('url')}" if payload.get("url") else ""), "ok")
                    return self._json({"ok": True})
            return self._json({"ok": False, "error": "unknown id"}, 404)
        if path == "/api/export":
            ENGINE.write_outputs()
            ENGINE.save()
            ENGINE.log_event("METRA", "outputs written: queue.jsonl, calendar.md, report.md", "ok")
            return self._json({"ok": True})
        return self._json({"ok": False, "error": "unknown endpoint"}, 404)


def main():
    argv = sys.argv[1:]
    if "--batch" in argv:
        # Mode CI: generate N item, tulis outputs, keluar. Tanpa server.
        n = int(os.environ.get("BATCH_ITEMS", "49"))
        seed()
        extra = max(0, n - len(ENGINE.items))
        if extra:
            ENGINE.tick(extra)
        ENGINE.write_outputs()
        ENGINE.save()
        m = ENGINE.metrics()
        print(f"[batch] items={m['total']} approved={m['approved']} "
              f"repaired={m['edited']} vetoes={ENGINE.agents['VIGIL'].blocked} "
              f"avg_score={m['avg_score']}")
        print(f"[batch] channels={m['by_channel']}")
        return

    start_background()
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    guard_txt = "LOCKED (DASHBOARD_TOKEN set)" if TOKEN else "open"
    print(f"[agent-team] dashboard on http://0.0.0.0:{PORT}  ({len(ENGINE.items)} items queued) · access: {guard_txt}", flush=True)
    httpd.serve_forever()

# ======================================================================
# ENTRYPOINT (single-file)
# ======================================================================
if __name__ == "__main__":
    main()
