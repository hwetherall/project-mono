Title: Regulatory and Platform-Policy Landscape for LEO Satellite Broadband: Implications for a Samsung-Led Service (Southeast Asia, Middle East, Global ex-U.S.)

Executive summary

- Bottom line: A full Starlink-style, global megaconstellation is not the optimal path for Samsung. A phased, regional-first strategy focused on Southeast Asia and the Middle East—starting with enterprise/mobility/backhaul services and government-oriented offerings, with clear data-sovereignty controls—can credibly reach multi‑billion‑dollar revenues without owning a launcher. Success requires deep regulatory work, MNO partnerships, selective vertical integration (terminals, payloads, network software, gateways), and disciplined capex pacing. Evidence from current market/regulatory shifts, including GCC and ASEAN licensing trends, GSMA/ITU frameworks for NTN/D2D, and the EU’s sovereignty push (IRIS2, draft Space Act/Digital Networks Act), indicates both demand and access will be mediated by policy rather than technology alone. Samsung’s unique advantages—device scale, silicon/RAN partnerships, and brand trust in Asia/MENA—support a sovereign‑neutral positioning that some governments and enterprises will prefer over U.S.-controlled services. But matching Starlink’s economics without vertical launch integration is challenging; Samsung should avoid a “global day‑one” footprint, target a constellation in the low hundreds initially (growing to ~1,500–2,000), localize gateways/data, and leverage direct‑to‑cell (NTN) where feasible. This approach can plausibly achieve >$10B revenue in ~10 years with high‑20% operating margins at maturity, contingent on regulatory beachheads (Vietnam/Thailand in SEA; Oman/UAE/Jordan/Kuwait in MENA), tight opex discipline, and partnership‑led spectrum access. ([Deloitte, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html); [GSMA/DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html); [Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [Capacity, 2026](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/); [RCR Wireless, 2024](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device); [Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html))

Market context and demand drivers

- Demand is real and diversifying:
  - LEO broadband spend projected at $14.8B in 2026 as use cases expand beyond remote consumer access into enterprise backhaul, mobility (aviation/maritime), and emerging D2D (direct‑to‑device) services ([Computer Weekly, 2025](https://www.computerweekly.com/news/366628292/Global-LEO-satellite-comms-services-spend-set-to-hit-148bn-in-2026)).
  - Deloitte estimates enterprise LEO subscribers could grow almost tenfold by 2030 to 3.4 million, with complex spectrum-sharing and interference-management regimes requiring satellite–terrestrial collaboration ([Deloitte, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).
- Policy, not physics, is the primary gate:
  - GCC and broader MENA have begun licensing Starlink but impose stringent oversight, spectrum and import controls, and reliance on local resellers—demonstrating that licensing and national-security conditions govern access more than technology readiness ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).
  - In ASEAN, regulators are updating frameworks to accommodate LEO: Vietnam licensed Starlink under a pilot with gateways and up to 600k terminals; Thailand drafted rules but awaits NBTC operational guidelines—both indicating structured openness with strong state control ([VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp); [Bangkok Post, 2025](https://www.bangkokpost.com/business/general/2967541/leo-satellite-tie-up-awaits-guidelines); [Tilleke & Gibbins, 2025](https://www.tilleke.com/insights/thailand-proposes-new-rules-for-foreign-satellite-services/3/)).
- Sovereignty is reshaping competition:
  - The EU’s IRIS2 aims to reduce dependence on non‑European providers, with service prioritization for government users and potential preemption of commercial traffic in crises, illustrating how sovereignty requirements can directly impact commercial service availability and economics ([Capacity, 2026](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/); [Space Intel Report, 2026](https://www.spaceintelreport.com/eu-commission-iris2-will-be-free-to-govt-users-whose-comms-will-be-anomymous-non-govt-service-to-be-preempted-in-crises/)).

A. Regulatory landscape

1) Named regulatory regimes affecting the market

- Market access and licensing (national):
  - Country‑specific telecom/satellite licensing; import controls on user terminals; spectrum assignments; lawful intercept (LI); universal service obligations; public emergency access. Examples:
    - UAE TDRA 10‑year license to Starlink for maritime, later expanded to aero; consumer channel still clarified via resellers/consultations—tight national‑security direction clauses apply ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).
    - Jordan TRC license via authorized reseller Sama X to distribute across the Kingdom, targeting remote regions ([TechAfrica News, 2026](https://techafricanews.com/2026/01/05/sama-x-to-provide-reliable-high-speed-internet-across-jordan-with-starlink-leo-satellites/)).
    - Vietnam pilot licensing with gateways and terminal caps; separate spectrum and equipment approval under RF Department; five‑year pilot under PM Decision 659/QD‑TTg (no foreign ownership limit during pilot) ([VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp)).
    - Thailand: proposed frameworks for foreign satellite services; NBTC still shaping LEO broadband supervision for marketing/operations ([Tilleke & Gibbins, 2025](https://www.tilleke.com/insights/thailand-proposes-new-rules-for-foreign-satellite-services/3/); [Bangkok Post, 2025](https://www.bangkokpost.com/business/general/2967541/leo-satellite-tie-up-awaits-guidelines)).
- Spectrum and interference management (regional/international):
  - ITU Radio Regulations govern MSS/FSS allocations; CEPT FM44 studying direct‑to‑handset frequency management and interference; ITU–R WP4B advancing IMT‑2030 satellite radio interfaces and NTN harmonization ([ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/)).
- D2D/Supplemental Coverage from Space (platform/regulatory frameworks):
  - FCC SCS framework enabling satellite–MNO collaborations for NTN direct‑to‑device; similar considerations emerging in CEPT/EU contexts, though EU is also debating market access reciprocity and potential re‑licensing ([RCR Wireless, 2024](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device); [Greenberg Traurig, 2026](https://www.gtlaw.com/en/insights/2026/3/fcc-seeks-comment-on-satellite-market-access-reciprocity)).
- Market-access reciprocity and sovereignty (global trade/policy):
  - FCC 2026 proceeding on international reciprocity notes potential barriers for U.S. operators abroad (e.g., EU Space Act/Digital Networks Act drafts), and may adjust U.S. stances—sets tone for global tit‑for‑tat constraints ([FCC PN DA 26‑208, 2026](https://docs.fcc.gov/public/attachments/DA-26-208A1.pdf); [Access Partnership, 2026](https://accesspartnership.com/opinion/fcc-tests-reciprocity-satellite-market-access/)).
  - EU sovereignty initiatives (IRIS2) reshape competitive space through state‑backed capacity and prioritization rules ([Capacity, 2026](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/)).
- National security, data sovereignty, and enforcement:
  - GCC/EM operators flag data sovereignty and cross‑border traffic routing as core concerns; regulators require enforceable LI/data policies, often via local entities and trackable/confiscable hardware regimes ([DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html); [Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).

2) Key regulatory agencies and oversight bodies

- National telecom/satellite regulators:
  - TDRA (UAE), CITRA (Kuwait), TRC (Jordan), NBTC (Thailand), Vietnam’s Authority of Telecommunications and Radio Frequency Department, and analogous bodies across MENA/SEA establish licensing, spectrum allocation, import controls, LI obligations, and consumer protections ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html); [VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp)).
- Regional and international standards/policy bodies:
  - ITU–R (spectrum allocations, NTN studies), CEPT (FM44 for D2D), GSMA (industry position papers urging modernized, harmonized LEO regulation), and national space/telecom agencies collaborating on NTN/D2D standards ([ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/); [Mobile World Live, 2024/2026](https://www.mobileworldlive.com/gsma/gsma-posits-leo-requires-regulation/)).

3) Regulatory shifts with enacting body and effective date

- UAE TDRA: Starlink 10‑year license (maritime in 2024, later including aero), with national‑security compliance clause; 2025 public consultation to enable third‑party LEO distribution—paved path for Emirates/flydubai inflight and eventual consumer routes via resellers ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).
- Kuwait/CITRA: 2026 operator license enabling Sama X to resell Starlink, demonstrating that formal licensing and local distribution gate access despite technical availability ([DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19973-sama-x-launches-starlink-in-kuwait-following-regulatory-approval.html)).
- Jordan/TRC: 2026 reseller approval to Sama X for nationwide Starlink services including remote region coverage ([TechAfrica News, 2026](https://techafricanews.com/2026/01/05/sama-x-to-provide-reliable-high-speed-internet-across-jordan-with-starlink-leo-satellites/)).
- Vietnam: 2026 license to Starlink Services Vietnam with gateways, equipment/spectrum approval, and five‑year pilot under PM Decision 659/QD‑TTg (pilot ends by Jan 1, 2031) ([VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp)).
- Thailand: 2025 draft regulations to permit foreign satellite operators; NBTC indicates LEO broadband service provision will require clear supervisory guidelines for marketing/operations ([Tilleke & Gibbins, 2025](https://www.tilleke.com/insights/thailand-proposes-new-rules-for-foreign-satellite-services/3/); [Bangkok Post, 2025](https://www.bangkokpost.com/business/general/2967541/leo-satellite-tie-up-awaits-guidelines)).
- ITU/CEPT/GSMA: Ongoing studies and position calls (2023–2026) to integrate NTN into 3GPP standards and facilitate spectrum-sharing while ensuring interference protections; GSMA urges harmonized, fair-entry regimes governing both satellite and mobile players ([ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/); [Mobile World Live, 2026](https://www.mobileworldlive.com/gsma/gsma-posits-leo-requires-regulation/)).
- FCC reciprocity proceeding: 2026 Public Notice (DA 26‑208) seeking comment on foreign market access/restrictions given evolving EU Space Act/DNA; could influence global reciprocity norms even for ex‑U.S. operators via policy signaling and bilateral pressure ([FCC PN DA 26‑208, 2026](https://docs.fcc.gov/public/attachments/DA-26-208A1.pdf); [Greenberg Traurig, 2026](https://www.gtlaw.com/en/insights/2026/3/fcc-seeks-comment-on-satellite-market-access-reciprocity)).

4) Demand-side effects of policy shifts

- Sovereign programs (IRIS2) and national‑security clauses can preempt or prioritize government traffic during crises—this may suppress some commercial demand in peak/critical periods unless operators carve out protected enterprise SLAs or multi‑orbit redundancy ([Space Intel Report, 2026](https://www.spaceintelreport.com/eu-commission-iris2-will-be-free-to-govt-users-whose-comms-will-be-anomymous-non-govt-service-to-be-preempted-in-crises/)).
- Regulatory modernization (NTN/D2D) boosts consumer safety and coverage expectations (e.g., emergency messaging, fallback connectivity), expanding the addressable market for hybrid satellite–terrestrial bundles ([RCR Wireless, 2024](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device); [ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/)).
- Emerging-market operator calls for parity and consumer protection deter predatory pricing and push LEO services toward complementary roles (backhaul, critical coverage), but also confer legitimacy that can accelerate enterprise adoption once rules are in place ([DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html)).

5) Access-side effects of policy shifts

- Licensing via local entities/resellers and gateway requirements create enforceable control points that open markets but increase compliance friction (e.g., UAE, Kuwait, Jordan, Vietnam) ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19973-sama-x-launches-starlink-in-kuwait-following-regulatory-approval.html); [VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp)).
- National controls on imports, spectrum, and device tracking empower governments to restrict unlicensed terminals and manage interference, which can slow viral adoption but protect market stability ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).
- Geopolitical exclusions persist (e.g., China, Russia), and selected regions have been slow to approve Western‑affiliated LEO networks—this is an opening for a sovereign‑neutral or Asia‑aligned entrant, but navigating sensitive markets requires tight compliance and local political alignment ([Valour Consultancy, 2025](https://valourconsultancy.com/seeking-approval-geopolitics-blocking-satellite-coverage/)).

6) Compliance cost benchmarks (qualitative)

- Core compliance cost drivers (direct/indirect):
  - Market‑entry legal/regulatory: licensing applications, local incorporation, spectrum coordination, import approvals; recurring license/spectrum fees.
  - Gateway build‑outs: real estate, earth stations, spectrum filters, secure enclaves for LI; integration with national IXPs; telemetry/TT&C redundancy.
  - Security and privacy: LI systems, data‑localization (where required), audit/compliance staff, incident response; end‑to‑end encryption with lawful access accommodations.
  - Terminal/device compliance: national equipment certification, reseller/retail controls, device tracking and logistics; firmware update governance.
  - Interference management: dynamic spectrum coordination, beam shaping, geofencing for restricted zones, cross‑border traffic controls; testing/certification.
  - Local operations: customer support (multilingual), field installation/maintenance, government relations, compliance reporting.
- Industry context indicates that gateways, local entities, and LI/data regimes are mandatory in many MENA/ASEAN markets; operators emphasizing sovereign control (e.g., Vietnam’s gateway requirements) will incur higher opex/capex in exchange for durable access rights ([VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html)).

7) Data privacy and cybersecurity requirements

- Lawful intercept and data sovereignty:
  - Regulators demand LI and data handling that conforms to national law; GCC/EM operator testimony underscores complexity of cross‑border routing and the need for enforceable controls (often the end user and local distributor are enforcement levers) ([DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html)).
  - UAE’s Starlink license explicitly binds the operator to comply with directions from authorities concerning public interest, safety, and national security—implying mandatory traffic controls and cooperation obligations ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).
- Platform‑level security expectations:
  - NTN/D2D frameworks foresee emergency access integration and standardization (3GPP) with spectrum‑sharing and interference safeguards; cybersecurity hardening of space/ground systems is a growing regulatory expectation as satellite connectivity becomes core critical infrastructure ([RCR Wireless, 2024](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device); [ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/); [APNIC Blog, 2026](https://blog.apnic.net/2026/02/04/thousands-of-leo-satellites-wont-save-us-but-good-regulation-will/)).

Country/regional access snapshot (selected SEA and MENA)

| Jurisdiction | Status/Recent Action | Access Implications |
|---|---|---|
| UAE | 10‑year Starlink license for maritime; updated to include aero; consumer rollout via reseller remains to be clarified; strong public interest/national security clauses ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)) | Maritime/aviation open; consumer access via licensed channels; compliance with TDRA directions |
| Kuwait | 2026: CITRA granted Starlink operating license; Sama X reselling with local support; typical latency ~20 ms; >300 Mbps plans ([DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19973-sama-x-launches-starlink-in-kuwait-following-regulatory-approval.html); [Telecompaper, 2026](https://www.telecompaper.com/satellite)) | Opens B2C/B2B with enforced local presence; model likely replicable for others |
| Jordan | 2026: TRC licensed Sama X to offer Starlink nationwide, targeting remote gov/enterprise segments ([TechAfrica News, 2026](https://techafricanews.com/2026/01/05/sama-x-to-provide-reliable-high-speed-internet-across-jordan-with-starlink-leo-satellites/)) | Clear path for high‑need segments; reseller model is template |
| Saudi Arabia | Aviation/maritime Starlink approvals announced; broader residential rollout pending regulatory approval ([ANDDORO, 2025](https://www.anddoro.com/starlink-in-the-uae-telecom-regulator-launches-consultations-on-satellite-reseller-services/)) | Mobility greenlighted; fixed services await framework—opportunity for entrants aligned with policy priorities |
| Oman, Qatar, Bahrain | Early GCC adopters; Bahrain licensed Starlink’s local entity for marketing in 2022; Oman allowed fixed services first ([Eicon, 2024](https://www.eicon-me.com/publications/ei_starlink_mena-5_2783.pdf); [Stimson, 2025](https://www.stimson.org/2025/gcc-welcomes-starlink-but-limits-its-reach/)) | Friendly to LEO with caveats—national controls persist |
| Vietnam | 2026: Starlink licensed; up to 4 gateways, 600k terminals; 5‑year pilot until 2031; spectrum/equipment authorized separately ([VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp)) | Structured opening favoring operators willing to localize data/infra |
| Thailand | 2025: Legal framework proposed; NBTC indicates LEO broadband requires clear guidelines for operations/marketing ([Tilleke & Gibbins, 2025](https://www.tilleke.com/insights/thailand-proposes-new-rules-for-foreign-satellite-services/3/); [Bangkok Post, 2025](https://www.bangkokpost.com/business/general/2967541/leo-satellite-tie-up-awaits-guidelines)) | Imminent pathway; co‑development with NT/MNOs likely needed |

B. Platform dynamics

8) Named platform policies or rule changes affecting the market

- 3GPP NTN for D2D and backhaul:
  - 3GPP Releases 17–19 define NTN for IoT/mobile broadband and introduce bands (e.g., n252) enabling standard smartphones to connect via satellites; Samsung/Keysight validated satellite‑to‑satellite, direct‑to‑cell 5G mobility with n252, demonstrating maturing D2D tech stack ([Computer Weekly, 2026](https://www.computerweekly.com/news/366637233/Samsung-Keysight-validate-satellite-to-satellite-direct-to-cell-5G-mobility)).
- FCC SCS framework (2024):
  - Creates a model for MNO–satellite collaboration to ensure seamless connectivity beyond terrestrial coverage; shapes global expectations for similar frameworks and boosts OEM incentives to support D2D features in devices ([RCR Wireless, 2024](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device)).
- GSMA position on LEO/D2D regulation (2026):
  - Calls for clear rules for market entry, parity of obligations between satellite and mobile players, and alignment of standards—guidance likely to influence ASEAN/MENA regulators working through new LEO regimes ([Mobile World Live, 2026](https://www.mobileworldlive.com/gsma/gsma-posits-leo-requires-regulation/)).

9) Platform changes with owner and effective date

- Samsung device platform support (2026):
  - Samsung announced expansion of satellite communication capabilities across Galaxy S26 and other smartphones through operator partnerships in North America/Europe/Japan; this strengthens a handset‑level platform for D2D that Samsung could leverage in SEA/MENA with local MNOs ([Samsung Newsroom UK, 2026](https://news.samsung.com/uk/samsung-brings-satellite-communication-support-to-galaxy-smartphones-across-the-globe)).
- Operator–LEO partnership momentum (2025–2026):
  - European and global operators are aligning with LEO platforms for backhaul and D2D pilots (e.g., Vodafone–AST, Orange–Starlink/OneWeb; Deutsche Telekom–Starlink pilots), signaling distribution pathways that reduce capex burdens but also shift strategic control to satellite owners ([Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

C. Broader policy exposure

10) Environmental, trade, and labor rule exposure

- Space environment and debris mitigation:
  - Even ex‑U.S. operators face customer expectation for credible debris‑mitigation policies as major regulators (e.g., FCC) reduce deorbit timelines (5‑year rule for LEO satellites post end‑of‑life), which shapes global best practice and procurement standards ([SpaceNexus, 2026](https://spacenexus.us/blog/fcc-satellite-licensing-guide-2026)).
- Trade/reciprocity risks:
  - FCC’s 2026 reciprocity inquiry reflects concern that EU acts could centralize licensing and re‑license non‑EU systems, increasing barriers for global operators; reciprocally, foreign regulators may also harden stances against U.S. or allied operators—Samsung must plan for asymmetric access across blocs ([FCC PN DA 26‑208, 2026](https://docs.fcc.gov/public/attachments/DA-26-208A1.pdf); [Greenberg Traurig, 2026](https://www.gtlaw.com/en/insights/2026/3/fcc-seeks-comment-on-satellite-market-access-reciprocity)).
- Labor/supply chain:
  - Vertical integration (à la SpaceX) provides cost/scale advantages; lack thereof elevates supply‑chain/labor exposure for satellite manufacturing and launch slots—key in periods of rocket scarcity and constellation ramp‑ups ([Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html); [CNBC, 2026](https://www.cnbc.com/2026/02/10/amazon-gets-fcc-approval-to-launch-4500-leo-internet-satellites.html)).

11) Subsidies, grants, and public incentives

- Sovereign programs:
  - EU IRIS2 (multi‑orbit, government‑priority access) indicates significant public funding that can shift competitive dynamics and procurement preferences in Europe and neighboring regions; its commercial viability will hinge on parity with Starlink/Kuiper on performance/price ([Capacity, 2026](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/); [Domain‑b, 2026](https://www.domain-b.com/technology/technology-general/iris2-vs-starlink-europe-satellite-project)).
- Development and inclusion:
  - Though U.S. BEAD changes boost LEO eligibility (domestic), similar “technology‑neutral” subsidy philosophies are being debated internationally as LEO becomes mainstream in universal service strategies; in emerging markets, multilateral/bilateral development funds may support remote connectivity and emergency resilience if services meet local compliance/sovereignty conditions ([Deloitte, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html); [ITU State of Satellite Broadband, 2025](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/)).

Competitive and geopolitical white spaces

- Active competitors:
  - Starlink retains scale/latency/cost advantages; OneWeb (Eutelsat), Telesat Lightspeed, Viasat, and regional GEO incumbents (Yahsat, Thaicom) target enterprise/mobility; Amazon Leo (Kuiper) accelerated by FCC approvals and dozens of launches planned through 2027 ([CNBC, 2026](https://www.cnbc.com/2026/02/10/amazon-gets-fcc-approval-to-launch-4500-leo-internet-satellites.html); [Via Satellite, 2026](https://interactive.satellitetoday.com/via/march-2026/the-coming-wave-of-competition-in-leo-constellations)).
- Geopolitical openings:
  - Countries wary of U.S. control (e.g., certain Middle Eastern, Central Asian, or Global South markets) are exploring alternatives, including Chinese‑aligned constellations (e.g., SpaceSail/Qianfan testing or partnerships in Brazil/Thailand/Malaysia)—yet such offerings may be unacceptable to Western‑aligned states, creating demand for “trusted, non‑U.S.” but also “non‑Chinese” options ([WIRED, 2026](https://www.wired.com/story/china-starlink-competitor-satellites/); [Xinhua, 2025](https://english.news.cn/20251212/00b310c1e30e40869389a38783d506b8/c.html)).
  - EU’s sovereignty posture plus GCC regulators’ assertive licensing show appetite for diversified suppliers, but insist on state control over data and security—an opening for a Korean‑origin, sovereign‑neutral brand with strong compliance posture ([Capacity, 2026](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/); [Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).

Venture brief: direct answers (evidence-based)

1) Should Samsung proceed with launching a satellite-based broadband communications business similar to Starlink?

- Proceed only with a phased, regional-first, partnership‑heavy model—not a Starlink‑scale global clone. Market and policy signals show:
  - Demand exists in SEA/MENA for enterprise/backhaul/mobility, resilience, and D2D—particularly where fiber/5G are scarce or for backup in crises ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [Deloitte, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).
  - Access depends on licensing via local entities/gateways and adherence to national security/data rules—Samsung’s brand/regional relationships can accelerate this relative to new entrants ([VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19973-sama-x-launches-starlink-in-kuwait-following-regulatory-approval.html)).
  - Competing directly with Starlink’s vertically integrated economics on a global footprint is not advisable without similar integration; a differentiated, sovereignty‑aware, MNO‑integrated service has a clearer path ([Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

2) Can a Samsung-led service achieve the scale/economics for multi‑tens‑of‑billions capex?

- Yes, with disciplined scope: focus on SEA/MENA first, target enterprise/mobility/backhaul and selective residential, leverage D2D integration with Samsung devices and MNOs, and stage constellation investments. Global LEO services spend at $14.8B (2026) with ~20% annual growth in operator revenues to 2030 imply a >$50B market; a credible 10–20% regional share across target verticals can support >$10B revenue at maturity without a global footprint ([Computer Weekly, 2025](https://www.computerweekly.com/news/366628292/Global-LEO-satellite-comms-services-spend-set-to-hit-148bn-in-2026); [Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

3) Is it feasible without owning a launch vehicle?

- Feasible but at a structural cost disadvantage vs. SpaceX. Amazon’s filings highlight rocket‑availability constraints; however, multiple providers (Ariane, Blue Origin emerging, ISRO, others) plus rideshares can support a phased 300–500 satellite regional build. Expect higher cost per kg and schedule risk; mitigate via multi‑provider launch contracts and temporal phasing ([CNBC, 2026](https://www.cnbc.com/2026/02/10/amazon-gets-fcc-approval-to-launch-4500-leo-internet-satellites.html); [Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

4) Are there regulatory/geopolitical white spaces preferring non‑U.S. providers?

- Yes. EU sovereignty posture (IRIS2), GCC emphasis on control, and parts of Global South seeking alternatives to U.S. and Chinese systems create demand for “trusted, non‑U.S./non‑Chinese” providers—Korean origin is advantageous in ASEAN and some MENA contexts. However, each market requires strict local compliance and security commitments ([Capacity, 2026](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html)).

5) Beachhead market

- Vietnam (clear pilot framework, gateway/localization, openness to multiple providers) and Thailand (rules in progress; strong need for rural/archipelago coverage; state operator NT active) in SEA; Oman/UAE/Jordan/Kuwait in GCC (proven LEO licensing models, reseller templates; focus enterprise/mobility and crisis backup) ([VietnamPlus, 2026](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp); [Tilleke & Gibbins, 2025](https://www.tilleke.com/insights/thailand-proposes-new-rules-for-foreign-satellite-services/3/); [Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19973-sama-x-launches-starlink-in-kuwait-following-regulatory-approval.html)).

6) Optimal constellation size and regional deployment strategy

- Recommendation:
  - Phase 1 (Years 1–3): ~300–500 satellites focused on 20°–35°N/S bands covering SEA + MENA with priority on enterprise/backhaul/mobility; build gateways in Vietnam, Thailand, UAE/Oman/Jordan/Kuwait.
  - Phase 2 (Years 3–6): Expand to ~1,000–1,500 for added capacity, D2D overlays (n252/n255/n256 where permitted), and maritime/aviation corridors.
  - Phase 3 (Years 6–10): Scale to ~1,500–2,000 based on uptake; only consider ~3,500+ if D2D drives mass‑market consumer substitution (today’s signals suggest complementary, not replacement, in urban cores) ([ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/); [Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

7) Credible geographies to win vs incumbents

- SEA: Vietnam, Thailand (regulatory readiness, strong OEM/government relationships), possibly Malaysia/Philippines later as frameworks mature.
- MENA: Oman, Jordan, Kuwait, UAE (via reseller/government channels), later Saudi for fixed services post‑framework finalization (aviation/maritime now).
- Israel/Gulf aviation/maritime corridors for mobility. These markets show licensing precedents and appetite for multi‑provider ecosystems ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [TechAfrica News, 2026](https://techafricanews.com/2026/01/05/sama-x-to-provide-reliable-high-speed-internet-across-jordan-with-starlink-leo-satellites/)).

8) Where to vertically integrate vs. partner

- Integrate:
  - User terminals (CPE) and chipset/software stack (tight linkage to Samsung devices), phased array tech for mobility terminals.
  - Network software (routing, beam/traffic orchestration, LI hooks) and security.
  - Payload design for D2D/backhaul flexibility; limited in‑house satellite manufacturing for critical buses/payloads with strategic partners.
  - Gateway/edge POPs (to assure sovereignty/data localization and SLAs).
- Partner:
  - Launch (multi‑vendor contracts to avoid single‑point risk); MNOs for spectrum leasing and D2D SCS; incumbents (Yahsat/Thaicom) for distribution/backhaul in early markets; airlines/shipping for mobility channels; local resellers/government integrators (analogous to Sama X model) ([RCR Wireless, 2024](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device); [Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

9) Optimal pace of market entry/constellation deployment

- Pursue 24–30 month cycles aligned to regulatory approvals and gateway readiness; cluster launches in tranches of 50–100 satellites to match demand. Avoid front‑loading global coverage; instead, deepen capacity where licenses and resellers are live. This reduces capex exposure and aligns with potential rocket bottlenecks ([CNBC, 2026](https://www.cnbc.com/2026/02/10/amazon-gets-fcc-approval-to-launch-4500-leo-internet-satellites.html)).

10) Partnerships with local operators for access/adoption

- Essential. MNOs provide:
  - D2D spectrum leasing and retail reach; backhaul integration; shared customer care; regulatory cover for LI/data obligations; universal service alignment. GSMA and operator positions favor parity rules and structured integration, not competition with MNOs—work with, not against, MNOs ([Mobile World Live, 2026](https://www.mobileworldlive.com/gsma/gsma-posits-leo-requires-regulation/); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html)).

11) Key factors influencing unit economics

- Terminal BOM and pricing (CPE vs. mobility terminals), ARPU by segment (residential vs. enterprise/maritime/aviation), gateway opex, launch $/kg and cadence, spectrum access costs/revenue‑share with MNOs, churn, and regulatory compliance overhead (LI/data localization). Starlink’s GCC residential pricing suggests ARPU bands ~USD 50–80/month with ~$300–600 hardware; enterprise/mobility ARPUs are far higher ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)).

12) Can revenue >$10B scale be reached ex‑U.S.?

- Yes, with SEA/MENA/Global South focus across enterprise/mobility/backhaul and selective residential; overall LEO operator market headed toward ~$50B by 2030—Samsung can capture a meaningful share in target regions if it leverages device/MNO ecosystems and sovereignty compliance ([Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html); [Computer Weekly, 2025](https://www.computerweekly.com/news/366628292/Global-LEO-satellite-comms-services-spend-set-to-hit-148bn-in-2026)).

13) Will certain governments/enterprises prefer non‑U.S.-controlled infrastructure?

- Evidence indicates yes: EU’s sovereignty drive and GCC insistence on licensed, controllable LEO services demonstrate preferences for providers who localize and accept national‑security directives; some markets are also exploring Chinese alternatives, suggesting a lane for a Korean‑origin, sovereignty‑respecting provider ([Capacity, 2026](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/); [DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html); [WIRED, 2026](https://www.wired.com/story/china-starlink-competitor-satellites/)).

14) Can ~3,500 satellites deliver sufficient performance/coverage?

- For targeted SEA/MENA markets and initial D2D overlays: yes, technically sufficient; but business prudence suggests starting with ~300–500 and scaling to ~1,500–2,000. A 15,000‑satellite scale is associated with full 5G‑class D2D capacity; Samsung does not need that to win initial markets and segments ([Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

15) Will launch cost reductions continue if access to lowest‑cost launchers is constrained?

- Likely moderate declines via competition (Ariane 6, Blue Origin ramp, national launchers) but nowhere near SpaceX’s internalized economies; plan for higher $/kg and schedule buffers. Phased launches and mixed providers mitigate risk ([Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html); [CNBC, 2026](https://www.cnbc.com/2026/02/10/amazon-gets-fcc-approval-to-launch-4500-leo-internet-satellites.html)).

16) Can Samsung coordinate global regulatory approvals without prohibitive delays?

- Yes, if it sequences beachheads, works through local partners, and builds gateways/local entities as required. Recent GCC/ASEAN cases show approvals can be achieved within 12–24 months where frameworks exist; others (e.g., Saudi fixed services, Thailand operations) are maturing now ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [Bangkok Post, 2025](https://www.bangkokpost.com/business/general/2967541/leo-satellite-tie-up-awaits-guidelines)).

17) Can Samsung leverage local operator relationships for spectrum and distribution?

- Strongly yes. D2D requires MNO spectrum leasing; GSMA and CEPT paths favor collaborative models. Backhaul and enterprise deals with MNOs/ISPs can accelerate adoption and compliance ([Mobile World Live, 2026](https://www.mobileworldlive.com/gsma/gsma-posits-leo-requires-regulation/); [ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/)).

18) >$10B annual revenue in ~10 years?

- Achievable with the staged strategy, mixed segment focus (enterprise/mobility/backhaul/D2D), and multi‑regional presence (SEA+MENA with expansion nodes). TAM growth supports the target; execution risk centers on regulatory pacing and capex discipline ([Computer Weekly, 2025](https://www.computerweekly.com/news/366628292/Global-LEO-satellite-comms-services-spend-set-to-hit-148bn-in-2026); [Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

19) High‑20% operating margins at maturity?

- Possible with:
  - In‑house terminals/software, selective satellite manufacturing, gateways/data localization, and MNO‑bundled distribution—which reduce SAC/CPA and increase ARPU/retention. Not owning a launcher depresses margins vs. SpaceX but is offset by focus on higher‑ARPU segments and device ecosystem synergies ([Roland Berger, 2026](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)).

20) Cumulative cash‑flow breakeven by year 7–8?

- Plausible under phased capex (≤$8–12B over 6–8 years), multi‑orbit partnerships early, and rapid enterprise/mobility monetization; an all‑at‑once global build would not clear this hurdle. Regulatory sequencing is crucial to avoid stranded capacity ([Deloitte, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

21) IRR of 11–13% with 5–7 year payback?

- Achievable only with disciplined phasing, targeted segments, and strong MNO/government partnerships; a cautious green‑light is warranted with explicit stage gates tied to licensing, gateway readiness, and contracted enterprise/mobility demand ([DevelopingTelecoms, 2026](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html)).

Strategic recommendations for Samsung

- Positioning and product:
  - “Sovereignty‑ready” LEO connectivity with in‑country gateways, data‑path transparency, and LI compliance. Offer enterprise‑grade SLAs and disaster‑resilience bundles; integrate with Samsung devices for D2D safety and limited messaging at launch.
- Beachheads and sequencing:
  - Phase 1: Vietnam and Thailand (SEA); Oman, Jordan, Kuwait, UAE (MENA). Build 1–2 gateways per country, co‑locate with IXPs, and sign MNO spectrum/D2D frameworks aligned with 3GPP.
  - Phase 2: Expand to Saudi fixed (post framework), Malaysia/Philippines/Indonesia (as rules mature), and mobility corridors.
- Partnerships:
  - MNOs for spectrum/D2D/backhaul; incumbents (e.g., Yahsat, Thaicom) for early enterprise channels; airlines/shipping; local resellers (Sama X‑like) for distribution/compliance.
- Constellation and launch:
  - Start with 300–500 satellites (regional shells), scale to ~1,500–2,000 over 6–8 years; multi‑provider launch strategy; assess selective manufacturing integration for key buses/payloads.
- Compliance and governance:
  - Country‑by‑country compliance playbooks covering licensing, LI, data localization, spectrum/terminal certification, and enforcement cooperation. Adopt ITU/CEPT/GSMA‑aligned interference and spectrum‑sharing mechanisms.
- Go‑to‑market and economics:
  - Enterprise/mobility/backhaul ARPU leadership; residential only where fiber/5G are absent or as outage backup. Bundle D2D with Samsung smartphones via operator channels for safety/coverage add‑ons.

Policy-shift ledger

- Demand creation/acceleration:
  - NTN/D2D frameworks (3GPP; FCC SCS), MNO‑satellite partnerships, state digital inclusion/resilience agendas, enterprise need for low‑latency backhaul and mobility services ([RCR Wireless, 2024](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device); [Deloitte, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).
- Access friction/constraints:
  - Sovereignty and LI requirements; importer/spectrum/device controls; reciprocity tensions (EU draft Space Act/DNA; FCC inquiry); potential government preemption of commercial traffic (IRIS2); launch bottlenecks ([Wired Middle East, 2026](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know); [Greenberg Traurig, 2026](https://www.gtlaw.com/en/insights/2026/3/fcc-seeks-comment-on-satellite-market-access-reciprocity); [Space Intel Report, 2026](https://www.spaceintelreport.com/eu-commission-iris2-will-be-free-to-govt-users-whose-comms-will-be-anomymous-non-govt-service-to-be-preempted-in-crises/); [CNBC, 2026](https://www.cnbc.com/2026/02/10/amazon-gets-fcc-approval-to-launch-4500-leo-internet-satellites.html)).
- Neutral/background:
  - ITU/CEPT ongoing standardization; GSMA policy guidance; evolving market competition (Kuiper/OneWeb/Telesat); macro TAM growth trends ([ITU, 2023](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/); [Mobile World Live, 2026](https://www.mobileworldlive.com/gsma/gsma-posits-leo-requires-regulation/); [Via Satellite, 2026](https://interactive.satellitetoday.com/via/march-2026/the-coming-wave-of-competition-in-leo-constellations)).

Cited sources (APA-style list with hyperlinks)

- Access Partnership. (2026, March). FCC tests reciprocity for satellite market access. [accesspartnership.com](https://accesspartnership.com/opinion/fcc-tests-reciprocity-satellite-market-access/)
- APNIC Blog. (2026, Feb 4). Thousands of LEO satellites won’t save us (but good regulation will). [blog.apnic.net](https://blog.apnic.net/2026/02/04/thousands-of-leo-satellites-wont-save-us-but-good-regulation-will/)
- Bangkok Post. (2025, Feb 25). LEO satellite tie-up awaits guidelines. [bangkokpost.com](https://www.bangkokpost.com/business/general/2967541/leo-satellite-tie-up-awaits-guidelines)
- Capacity. (2026, Jan 28). Europe launches IRIS2 satellites as war looms and Starlink threatens sovereignty. [capacityglobal.com](https://capacityglobal.com/news/europe-launches-iris2-satellites-as-war-looms-and-starlink-threatens-sovereignty/)
- CNBC. (2026, Feb 10). Amazon gets FCC approval to launch 4,500 LEO internet satellites. [cnbc.com](https://www.cnbc.com/2026/02/10/amazon-gets-fcc-approval-to-launch-4500-leo-internet-satellites.html)
- Computer Weekly. (2025, Jul 30). Global LEO satellite comms services spend set to hit $14.8bn in 2026. [computerweekly.com](https://www.computerweekly.com/news/366628292/Global-LEO-satellite-comms-services-spend-set-to-hit-148bn-in-2026)
- Computer Weekly. (2026, Jan). Samsung, Keysight validate satellite-to-satellite, direct-to-cell 5G mobility. [computerweekly.com](https://www.computerweekly.com/news/366637233/Samsung-Keysight-validate-satellite-to-satellite-direct-to-cell-5G-mobility)
- Deloitte Insights. (2026). Next-gen satellite internet. [deloitte.com](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)
- Developing Telecoms. (2026, Mar). Emerging market operators push for tighter LEO satellite rules as competitive tensions rise. [developingtelecoms.com](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19980-emerging-market-operators-push-for-tighter-leo-satellite-rules-as-competitive-tensions-rise.html)
- Developing Telecoms. (2026, Mar 18). Sama X launches Starlink in Kuwait following regulatory approval. [developingtelecoms.com](https://www.developingtelecoms.com/telecom-technology/satellite-communications-networks/19973-sama-x-launches-starlink-in-kuwait-following-regulatory-approval.html)
- Eicon. (2024, Feb 23). Regulatory approvals for Starlink services in MENA countries. [eicon-me.com](https://www.eicon-me.com/publications/ei_starlink_mena-5_2783.pdf)
- FCC (Space Bureau & OIA). (2026, Mar 2). Public Notice DA 26‑208: Satellite market access reciprocity. [docs.fcc.gov](https://docs.fcc.gov/public/attachments/DA-26-208A1.pdf)
- Greenberg Traurig. (2026, Mar). FCC seeks comment on satellite market access reciprocity. [gtlaw.com](https://www.gtlaw.com/en/insights/2026/3/fcc-seeks-comment-on-satellite-market-access-reciprocity)
- ITU. (2023, Oct 23). Direct satellite connectivity to mobile. [itu.int](https://www.itu.int/hub/2023/10/direct-satellite-connectivity-to-mobile/)
- Mobile World Live. (2026). GSMA posits LEO requires regulation. [mobileworldlive.com](https://www.mobileworldlive.com/gsma/gsma-posits-leo-requires-regulation/)
- RCR Wireless News. (2024, Mar 15). FCC approves rules for NTN direct-to-device service. [rcrwireless.com](https://www.rcrwireless.com/20240315/featured/fcc-approves-rules-for-ntn-direct-to-device)
- Roland Berger. (2026). Satellite convergence: How satellite constellations are reshaping telecoms. [rolandberger.com](https://www.rolandberger.com/en/Insights/Publications/Satellite-convergence.html)
- Samsung Newsroom UK. (2026). Samsung brings satellite communication support to Galaxy smartphones. [news.samsung.com](https://news.samsung.com/uk/samsung-brings-satellite-communication-support-to-galaxy-smartphones-across-the-globe)
- Space Intel Report. (2026, Feb 18). EU Commission: IRIS2 will be free to govt users; non-govt service preempted in crises. [spaceintelreport.com](https://www.spaceintelreport.com/eu-commission-iris2-will-be-free-to-govt-users-whose-comms-will-be-anomymous-non-govt-service-to-be-preempted-in-crises/)
- SpaceNexus. (2026). FCC satellite licensing guide (deorbit rule context). [spacenexus.us](https://spacenexus.us/blog/fcc-satellite-licensing-guide-2026)
- Stimson Center. (2025). GCC welcomes Starlink but limits its reach. [stimson.org](https://www.stimson.org/2025/gcc-welcomes-starlink-but-limits-its-reach/)
- TechAfrica News. (2026, Jan 5). Sama X to provide reliable high-speed internet across Jordan with Starlink LEO satellites. [techafricanews.com](https://techafricanews.com/2026/01/05/sama-x-to-provide-reliable-high-speed-internet-across-jordan-with-starlink-leo-satellites/)
- Telecompaper. (2026, Mar 18). Sama X brings Starlink services to Kuwait. [telecompaper.com](https://www.telecompaper.com/satellite)
- Tilleke & Gibbins. (2025, Sep 2). Thailand proposes new rules for foreign satellite services. [tilleke.com](https://www.tilleke.com/insights/thailand-proposes-new-rules-for-foreign-satellite-services/3/)
- Via Satellite. (2026, Feb 23). The coming wave of competition in LEO constellations. [satellitetoday.com](https://interactive.satellitetoday.com/via/march-2026/the-coming-wave-of-competition-in-leo-constellations)
- VietnamPlus. (2026). Satellite internet provider Starlink officially licensed to operate in Vietnam. [vietnamplus.vn](https://en.vietnamplus.vn/satellite-internet-provider-starlink-officially-licenced-to-operate-in-vietnam-post337914.vnp)
- Valour Consultancy. (2025). Seeking approval: Geopolitics blocking satellite coverage. [valourconsultancy.com](https://valourconsultancy.com/seeking-approval-geopolitics-blocking-satellite-coverage/)
- WIRED Middle East. (2026). Starlink is apparently available in the UAE—here’s what you need to know. [wired.me](https://www.wired.me/story/starlink-is-apparently-available-in-the-uae-heres-what-you-need-to-know)
- WIRED. (2026). China’s effort to build a competitor to Starlink is off to a bumpy start. [wired.com](https://www.wired.com/story/china-starlink-competitor-satellites/)