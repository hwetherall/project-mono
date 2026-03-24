Title: Enabling Technology Trends, Cost Curves, and Feasibility for a Samsung-Led LEO Broadband and Direct-to-Device Service (Ex-U.S. Focus)

Date: March 20, 2026

Executive Summary

Over the past 3–5 years, multiple technology shifts have converged to make a vertically integrated Low Earth Orbit (LEO) broadband constellation — augmented by standardized direct-to-device (D2D) connectivity — technically and economically feasible at global scale outside the U.S. Standardization in 3GPP Releases 17/18 and early validation of Release 19 features in S-band, the rapid growth of LEO constellations, maturing phased array terminal technologies, and the rise of cloud-native ground segments and Ground Segment-as-a-Service (GSaaS) collectively lower technical and time-to-market risks. Meanwhile, global operators’ growing interest in capex-lite D2D partnerships, the expanding base of satellite-ready smartphones (including Samsung’s Galaxy S26), and regulatory momentum (e.g., FCC’s SCS rules, GSMA’s 2026 position paper) support adoption and market access.

Critically for Samsung, its integrated assets — semiconductors (memory and foundry), System LSI modem chipsets, telecom network equipment, and Galaxy device footprint — align with where vertical integration most moves unit economics: satellite payload silicon, terminals and phased arrays, ground network software, and D2D-capable devices. Market evidence suggests a credible path to scale and revenues exceeding $10B annually within 10 years in ex-U.S. markets, provided deployment and go-to-market are staged, partnerships with regional mobile network operators (MNOs) are formalized early, and regulatory execution is well-resourced.

Our bottom-line view: Samsung should proceed, with a region-first deployment in Southeast Asia and the Middle East where topology, telco relationships, and sovereignty preferences create white spaces. A first-shell regional constellation of ~600–800 satellites growing to ~3,500 over 5–7 years — combined with consumer fixed broadband, enterprise/maritime offerings, and standardized D2D coverage for messaging/voice — is technically feasible now. Economic outcomes hinge on launch procurement diversity, terminal cost-down via Samsung silicon, and multi-orbit interworking through a cloud-native ground platform. High-20% operating margins at maturity are achievable with disciplined vertical integration, GSaaS leverage, and a strong enterprise mix. A breakeven window in year 7–8 and an IRR in the low teens are realistic in a base case if capex is phased and utilization ramps according to a partner-led distribution plan.

1. Venture Context and Problem Framing

- Problem: Significant coverage and affordability gaps persist in Southeast Asia (SEA), the Middle East, and developing regions, where terrestrial infrastructure economics are challenging. Governments in some markets harbor sovereignty concerns about U.S.-controlled LEO providers and may prefer alternative suppliers aligned with regional interests and standards-based D2D connectivity for resilience. The venture’s constraints include high capital intensity, regulatory complexity (spectrum/landing rights), and dependence on non-U.S. launch capacity.

- Opportunity: LEO and D2D have moved from concept to early commercial reality. Deloitte forecasts millions of LEO subscribers and surging enterprise demand as constellations scale, with D2D partnerships providing capex-lite coverage extension for MNOs under regulatory guardrails (e.g., spectrum sharing, interference management) ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)). Japan’s operators (DOCOMO, KDDI, SoftBank, Rakuten) are committing to direct satellite-to-phone services between 2025 and 2026, mirroring a broader global trend of telco-satellite alignment ([Telecom Review Asia, 2026](https://www.telecomreviewasia.com/news/network-news/28362-ntt-docomo-to-launch-direct-satellite-to-smartphone-service-in-early-fy2026/)).

2. Enabling Technology Shifts (Last 3–5 Years)

Table 1. Key technology shifts enabling a Samsung-led ex-U.S. LEO broadband + D2D service

| Shift | What changed (and when) | How it enables the venture | Maturity | Evidence/data |
|---|---|---|---|---|
| 3GPP standardization of NTN | Release 17 (2022) introduced NR-NTN and IoT-NTN for LEO/MEO/GEO; Release 18 (2023–2024) enhanced mobility, uplink, FR2/Ka-band; Release 19 (in progress) adds sat-to-sat mobility and n252 S-band refinements | Standards-based device, RAN, and core behaviors lower integration risk and enable D2D on consumer devices; supports seamless NTN-to-terrestrial mobility | Maturing | 3GPP Rel-17/18 scope; Samsung Research blog on NTN mobility and FR1 bands; ComSoc blog on Release 17/18 enhancements ([3GPP, 2022](https://www.3gpp.org/news-events/partner-news/ntn-rel17); [Samsung Research, 2025](https://research.samsung.com/blog/NTN-and-TN-networks-for-the-6G-era-technology-overview-and-regulatory-challenges); [IEEE ComSoc Tech Blog, 2026](https://techblog.comsoc.org/tag/3gpp-release-17-18)) |
| D2D proof points on S-band (n252) | 2026 CES demo by Keysight & Samsung achieving live NR‑NTN link in n252 with sat-to-sat mobility on commercial-grade Samsung modem | Validates Release 19 trajectories and cross-vendor interoperability; de-risks handset-integrated D2D rollout | Emerging-to-maturing | Live demo validates n252 S-band path; FCC enthusiasm for D2C frameworks ([RCR Wireless, 2026](https://www.rcrwireless.com/20260112/test-measurement/keysight-samsung-demonstrate-nr-ntn-link-in-n252-band-as-the-industry-pushes-for-direct-to-cell-connectivity)) |
| Smartphone readiness for satellite | Galaxy S26 line adds SCS/NTN; Samsung confirms expanding satellite capabilities to older Galaxy devices with carrier dependence; industry momentum in handset integration | Expands addressable D2D base quickly via OTA-enabled features; leverages Samsung’s device footprint to accelerate adoption | Maturing | Samsung announcements and coverage (Galaxy S26 satellite comms, SCS/NTN support) ([Samsung News, 2026](https://news.samsung.com/us/samsung-brings-satellite-communication-support-galaxy-smartphones-in-us/); [9to5Google, 2026](https://9to5google.com/2026/02/27/samsung-confirms-satellite-connectivity-for-galaxy-s26-and-older-galaxy-devices/); [TechTimes, 2026](https://www.techtimes.com/articles/314356/20260128/all-samsung-galaxy-s26-models-expected-support-satellite-communication.htm)) |
| LEO constellation capacity and demand | 2026 outlook: 15–18k comms satellites across five constellations, >15M global LEO subscribers; Starlink ~3M U.S. residential subscribers by end-2025; D2D investments $6–8B in 2026 | Demonstrates market pull and operational learnings; highlights replacement cycles and scale benefits | Mature for broadband; emerging for D2D | Deloitte/WSJ TMT predictions; Via Satellite analysis of U.S. residential adoption ([WSJ/Deloitte TMT, 2026](https://deloitte.wsj.com/cmo/next-gen-satellite-internet-shifting-prices-capacity-and-opportunities-e8c8b90a?gaa_at=eafs&gaa_n=AWEtsqe_ibW6fW2ulkKmlZmg88UNJktLKZGIW9BAOF3Px3kOO__vJiToKuP7&gaa_ts=69bda32c&gaa_sig=HeRPOSVZFERcbGXxdHBC6qnAsIyKUZ-iZVGOrnGoocVbxe8FFjaybzP07bopko_UvVtZRLlictvDnavz8iFylw%3D%3D); [Via Satellite, 2026](https://interactive.satellitetoday.com/via/march-2026/examining-the-size-of-the-us-residential-broadband-opportunity-for-leo-satcom)) |
| Cloud-native ground segments | GSaaS, virtual modems, and multi-orbit orchestration matured (AWS Ground Station, Azure Orbital, KSAT, RBC Signals; iDirect Intuition multi-orbit, end-to-end orchestration) | Reduces upfront ground capex; accelerates deployment; enables dynamic LEO/GEO/MEO steering and API-driven scaling | Maturing | Viasat GSaaS overview; ST Engineering iDirect Intuition platform; industry analysis of software-defined ground segments ([Viasat, 2024](https://www.viasat.com/perspectives/government/2024/how-ground-segment-as-a-service-supports-next-generation-satellite-communication/); [iDirect, 2026](https://www.satnow.com/news/details/4854-st-engineering-idirect-advances-satellite-ground-networks-with-intuition-cloud-native-technology); [Kratos, 2025](https://www.kratosspace.com/constellations/articles/predictions-for-the-space-industry-in-2025); [Dataintelo GSaaS, 2026](https://dataintelo.com/report/ground-segment-as-a-service-market)) |
| Phased-array and user terminal tech | LEO phased-array antenna market growing (CAGR ~10.9% through 2033); LEO terminals market CAGR ~19.3% to 2032; materials and miniaturization advances | Improves terminal affordability and performance in enterprise/mobility; supports scalable CPE | Maturing | DataInsights market sizing; 360iResearch LEO Terminals market outlook ([Data Insights Market, 2026](https://www.datainsightsmarket.com/reports/leo-satellite-communication-phased-array-antenna-924115); [360iResearch, 2026](https://www.360iresearch.com/library/intelligence/leo-terminals)) |
| Non-U.S. launch options & cadence | Massive pre-purchased launch capacity by Amazon Kuiper (Ariane 6, ULA Vulcan, Blue Origin New Glenn); reusability drives lower costs and cadence across ecosystem | Supports deployment without proprietary launch; hedges geopolitical and capacity risks | Maturing | Space Intel Report on 68 Kuiper launches (2022) ([Space Intel Report, 2022](https://www.spaceintelreport.com/amazon-contracts-for-68-launches-with-arianespace-blue-origin-ula-for-kuiper-broadband-constellation)) |
| Regulatory momentum | FCC SCS rules (2024) enabled hybrid mobile-satellite; GSMA’s 2026 paper urges updated D2D frameworks with parity, harmonization; growing numbers of operator-satellite partnerships (225 in 88 countries by Jan 2026) | Smoother market entry; policy signals for hybrid services; pathway for spectrum sharing and lawful intercept | Emerging-to-maturing | GSMA/GSA datasets and positions; regulatory commentary ([GSMA, 2026](https://www.gsma.com/newsroom/press-release/gsma-calls-for-regulatory-readiness-for-direct-to-user-leo-satellite-services/); [GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/); [BusinessCom Networks, 2026](https://www.bcsatellite.net/blog/samsung-advances-d2d-connectivity-as-ntn-ecosystem-takes-shape/)) |
| LEO economics and replacement cycles | LEO sats average 4–5 year lifespan; 20–25% annual replenishment; capex likely sustained; value chains maturing with digital payloads and flexible beamforming | Encourages vertically integrated, iterative manufacturing — an area where Samsung excels | Mature understanding | Deloitte analysis; New Space Economy value chain brief ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html); [New Space Economy, 2026](https://newspaceeconomy.ca/2026/02/25/satellite-broadband-communications-market-analysis-2026/)) |

3. Cost Curves for Key Enablers

Cost transparency in space remains uneven, but we can extract several robust signals relevant to forecasts and unit economics.

Table 2. Cost and scaling trends

| Technology | Cost trajectory and current reference | Projected cost/scale | Sources |
|---|---|---|---|
| Launch (heavy-lift) | Falcon 9 list ~$67M; internal cost estimates $15–$20M enabled by reusability; launch market ~$9B (2024); SpaceX ~60–65% share by mass; >130 launches in 2025 | Continued price competition as Ariane 6, Vulcan, New Glenn mature; reusability adoption outside SpaceX expected to pressure prices mid/late-decade | SpaceNexus on launch market and Falcon 9 internals; reusability impact on cost from industry summaries ([SpaceNexus, 2026](https://spacenexus.us/guide/space-industry-market-size); [LinkedIn Market Dynamics, 2026](https://www.linkedin.com/pulse/commercial-satellite-launch-market-dynamics-2026-size-brands-t24hc/)) |
| Satellite manufacturing (LEO broadband class) | Costs declining via high-volume, standardized buses, digital payloads; faster iteration cycles reduce per-bit costs | Ongoing reductions as vertical integration increases and silicon availability improves; replacement cycles support steady-state factories | New Space Economy value chain; Deloitte on LEO economics and replacement rates ([New Space Economy, 2026](https://newspaceeconomy.ca/2026/02/25/satellite-broadband-communications-market-analysis-2026/); [Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)) |
| User terminals (fixed/enterprise) | Rapid volume growth: LEO terminals market from $9.20B (2025) to $10.94B (2026), to $31.73B by 2032 (CAGR 19.33%); performance up, cost per Mbps down | Scale + silicon integration (Samsung COTS memory, chipsets) lower BOM; phased arrays approach commoditization in some form factors by late decade | 360iResearch market sizing; FMI LEO terminal insights ([360iResearch, 2026](https://www.360iresearch.com/library/intelligence/leo-terminals); [FMI LEO Terminal, 2026](https://www.futuremarketinsights.com/reports/leo-terminal-market)) |
| Phased-array antennas | Market growth for LEO phased arrays: CAGR ~10.9% to 2033; materials and beamforming maturity | Mass adoption in mobility (maritime/aviation) drives economies; integration into vehicle platforms | Data Insights Market report on LEO phased arrays ([Data Insights Market, 2026](https://www.datainsightsmarket.com/reports/leo-satellite-communication-phased-array-antenna-924115)) |
| Ground segment (GSaaS / virtual modems) | Emergence of GSaaS (AWS, Azure, KSAT, Leaf Space, ATLAS, RBC Signals), and cloud-native multi-orbit orchestration (iDirect Intuition) cuts time-to-first-contact and capex | Further opex-centric models reduce upfront investment; API-driven networking reduces integration and operating costs | Viasat GSaaS; iDirect; Dataintelo GSaaS ([Viasat, 2024](https://www.viasat.com/perspectives/government/2024/how-ground-segment-as-a-service-supports-next-generation-satellite-communication/); [ST Engineering iDirect, 2026](https://www.satnow.com/news/details/4854-st-engineering-idirect-advances-satellite-ground-networks-with-intuition-cloud-native-technology); [Dataintelo, 2026](https://dataintelo.com/report/ground-segment-as-a-service-market)) |
| Device-side D2D enablement | Standards-based NTN support in Galaxy S26 line (SCS/NTN), with older devices gaining features; operator tie-ups reduce acquisition costs vs bespoke dongles | Incremental device bill-of-materials rather than new hardware; accelerates adoption; telco co-marketing reduces CAC | Samsung device announcements; GSMA/GSA on NTN partnerships ([Samsung News, 2026](https://news.samsung.com/us/samsung-brings-satellite-communication-support-galaxy-smartphones-in-us/); [GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/)) |

Launch costs remain the largest external risk factor. Without SpaceX access, the near-term cost per kilogram is likely higher, but Amazon’s procurement of 68 non‑SpaceX heavy-lift launches demonstrates that large constellations can be deployed on non-SpaceX vehicles if planned early, albeit at potentially higher costs and with schedule risk. Market entry sequencing (regional shells first) and long-term contracts as anchor customer for launch providers can mitigate cost volatility and ensure cadence ([Space Intel Report, 2022](https://www.spaceintelreport.com/amazon-contracts-for-68-launches-with-arianespace-blue-origin-ula-for-kuiper-broadband-constellation)).

4. Infrastructure Readiness

4.1 Ground and interconnect

- GSaaS and cloud-native ground networks are operational and commercially available today. This includes AWS Ground Station, Microsoft Azure Orbital, KSAT, Infostellar, Leaf Space, ATLAS Space Ops, and RBC Signals, enabling rapid ground network spin-up without bespoke infrastructure. Virtualized modems and orchestrators (e.g., ST Engineering iDirect Intuition) provide multi-orbit routing and standards-based interconnection with terrestrial telco ecosystems (MEF, TM Forum, DIFI, ETSI), improving integration readiness for enterprise SLAs and mobile backhaul ([Dataintelo GSaaS, 2026](https://dataintelo.com/report/ground-segment-as-a-service-market); [ST Engineering iDirect, 2026](https://www.satnow.com/news/details/4854-st-engineering-idirect-advances-satellite-ground-networks-with-intuition-cloud-native-technology); [Kratos, 2025](https://www.kratosspace.com/constellations/articles/predictions-for-the-space-industry-in-2025)).

4.2 Device and D2D ecosystem

- Devices: Samsung Galaxy S26 includes SCS/NTN support; select prior Galaxy models in several markets also enable satellite messaging and data (carrier/regulatory dependent). This reduces the need for custom D2D dongles, lowering entry friction ([Samsung News, 2026](https://news.samsung.com/us/samsung-brings-satellite-communication-support-galaxy-smartphones-in-us/); [9to5Google, 2026](https://9to5google.com/2026/02/27/samsung-confirms-satellite-connectivity-for-galaxy-s26-and-older-galaxy-devices/)).

- Operator partnerships: As of Jan 2026, 225 publicly announced operator–satellite partnerships in 88 countries; 16 partnerships have launched D2D services; 25 in trials; 53 in planning — indicating growing readiness to integrate hybrid satellite-mobile coverage and roaming ([GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/)).

- Country initiatives: Japan’s DOCOMO targets early FY2026 for D2D smartphone services; KDDI launched au Starlink Direct in April 2025 for SMS/RCS/iMessage; Rakuten and SoftBank also targeting 2026 — demonstrating regulatory acceptance and integration models in Asia ([Telecom Review Asia, 2026](https://www.telecomreviewasia.com/news/network-news/28362-ntt-docomo-to-launch-direct-satellite-to-smartphone-service-in-early-fy2026/)).

4.3 Market coverage

- LEO broadband availability is broadening; Deloitte notes rapid satellite growth, with more than 7,473 active broadband-capable LEO satellites by end-2023 and accelerating in 2026, as Kuiper enters with a 3,236-satellite plan; Telesat Lightspeed and European IRIS² add to the multi-operator fabric ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

- Telco coverage remains uneven: At the end of 2024, an estimated 350 million people (4% of global population) lacked mobile internet networks, underscoring D2D’s utility for resilience and coverage ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

4.4 Regional readiness gaps (SEA, Middle East, ex‑U.S.)

- Spectrum and landing rights are country-specific; GSMA calls for harmonized regulation and parity of obligations for D2D services (consumer protection, LI, privacy), which many countries are just beginning to implement. Some markets (e.g., India) are defining GMPCS licensing and gateway requirements; coexistence in L/S-bands must be coordinated to avoid interference ([GSMA, 2026](https://www.gsma.com/newsroom/press-release/gsma-calls-for-regulatory-readiness-for-direct-to-user-leo-satellite-services/); [Kbssidhu Substack, 2026](https://kbssidhu.substack.com/p/elon-musks-starlink-aims-for-direct)).

- Market access reciprocity concerns: The FCC is evaluating reciprocity for satellite market access, citing EU policies and barriers in Canada, India, South Korea, and Brazil — an indicator of rising geopolitical scrutiny that a non‑U.S. provider must navigate symmetrically when entering those markets ([Access Partnership, 2026](https://accesspartnership.com/opinion/fcc-tests-reciprocity-satellite-market-access/)).

- Conclusion: Infrastructure is largely in place to launch region-specific services rapidly using GSaaS and standards-based D2D on Samsung devices, but regulatory roadmaps must be proactively managed with local partners in key SEA and Middle East countries.

5. Platform and API Ecosystem

- GSaaS and virtual ground networks: APIs for scheduling downlinks, data routing, and cross-region redundancy (AWS, Azure, KSAT, Leaf Space, ATLAS, RBC Signals) allow an operator to bootstrap ground coverage without building global ground station networks, then localize critical gateways over time in sovereignty-sensitive markets ([Dataintelo, 2026](https://dataintelo.com/report/ground-segment-as-a-service-market)).

- Multi-orbit orchestration: ST Engineering iDirect’s Intuition supports standards-based network convergence and end-to-end orchestration across LEO/MEO/GEO networks. This reduces integration and operations complexity and enhances service resiliency for enterprise SLAs ([ST Engineering iDirect, 2026](https://www.satnow.com/news/details/4854-st-engineering-idirect-advances-satellite-ground-networks-with-intuition-cloud-native-technology); [Runway Girl, 2024](https://runwaygirlnetwork.com/2024/03/st-engineering-idirect-intuition/)).

- Telco integration standards: Adoption of MEF, TM Forum, ETSI, and DIFI interfaces by ground vendors improves interoperability with carrier OSS/BSS and 5G cores, crucial for wholesale and hybrid D2D services ([Kratos, 2025](https://www.kratosspace.com/constellations/articles/predictions-for-the-space-industry-in-2025)).

- Device/platform integration: Standardized NTN in 3GPP plus Samsung’s System LSI modem roadmaps and Galaxy device support reduce per-market customization, enabling firmware-based service activation alongside MNO partners ([Samsung Research, 2025](https://research.samsung.com/blog/NTN-and-TN-networks-for-the-6G-era-technology-overview-and-regulatory-challenges); [Samsung News, 2026](https://news.samsung.com/us/samsung-brings-satellite-communication-support-galaxy-smartphones-in-us/)).

What didn’t exist (or was nascent) 3–5 years ago: mature NTN specs (Rel-17/18), live demos of Release 19 features in S-band with sat-to-sat mobility, device-level support in mainstream smartphones, large-scale GSaaS ecosystems, and orchestrators supporting multi-orbit, standards-based convergence. These advancements collectively compress time-to-market and reduce build costs.

6. Technical Feasibility Assessment

Feasibility today is high for a staged LEO broadband service with standardized D2D augmentation:

- Constellation and payload: Digital payloads with flexible beamforming and onboard processing are well-established; inter-satellite laser links (ISLs) and Ka-band FR2 for NR-NTN are priorities in 5G-Advanced. Samsung can leverage its silicon, memory, and packaging scale to integrate payload processing and phased arrays competitively ([New Space Economy, 2026](https://newspaceeconomy.ca/2026/02/25/satellite-broadband-communications-market-analysis-2026/); [IEEE ComSoc Tech Blog, 2026](https://techblog.comsoc.org/tag/3gpp-release-17-18)).

- D2D/NTN: Live NR‑NTN link in n252, and Galaxy S26-level handset support, indicate viable D2D for messaging and voice — coverage-first not capacity-first — which is consistent with industry positioning for D2D as a resilience and reach layer ([RCR Wireless, 2026](https://www.rcrwireless.com/20260112/test-measurement/keysight-samsung-demonstrate-nr-ntn-link-in-n252-band-as-the-industry-pushes-for-direct-to-cell-connectivity); [Kbssidhu Substack, 2026](https://kbssidhu.substack.com/p/elon-musks-starlink-aims-for-direct)).

- Ground and network: Cloud-native ground with multi-orbit orchestration and virtualized modems is in production; wholesale handoffs to telcos are increasingly standardized, a key enabler for market access and enterprise-grade SLAs ([ST Engineering iDirect, 2026](https://www.satnow.com/news/details/4854-st-engineering-idirect-advances-satellite-ground-networks-with-intuition-cloud-native-technology); [GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/)).

Remaining technical risks/dependencies:

- Launch cadence and cost if SpaceX is unavailable; risks mitigated via multi-provider procurement (Ariane 6, Vulcan, New Glenn) but may impact schedule or costs ([Space Intel Report, 2022](https://www.spaceintelreport.com/amazon-contracts-for-68-launches-with-arianespace-blue-origin-ula-for-kuiper-broadband-constellation)).

- D2D roaming and interference management in IMT spectrum, requiring meticulous MNO coordination and adherence to national policies harmonized to WRC outcomes ([GSMA/CSI Magazine, 2025–2026](https://www.satellitetoday.com/connectivity/2025/09/12/gsma-outlines-spectrum-regulatory-guidance-for-d2d-services/); [GSMA, 2026](https://www.gsma.com/newsroom/press-release/gsma-calls-for-regulatory-readiness-for-direct-to-user-leo-satellite-services/)).

- Replacement cycles (20–25% of constellation annually) require robust manufacturing cadence and supply chain resilience; this plays to Samsung’s strengths but demands early-capacity commitments ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

7. Venture Brief: Direct Answers with Evidence

1) Should Samsung proceed?

Yes, with a staged, region-first approach anchored in SEA and the Middle East, integrating D2D for coverage/resilience and emphasizing enterprise/mobility verticals from the outset. Market validation (LEO subs, enterprise demand, device readiness, telco partnerships) and enabling tech (NTN standardization, GSaaS, cloud-native ground, phased arrays) support a go decision, contingent on securing multi-provider launch contracts and early MNO partnerships to de-risk spectrum and go-to-market ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html); [GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/); [RCR Wireless, 2026](https://www.rcrwireless.com/20260112/test-measurement/keysight-samsung-demonstrate-nr-ntn-link-in-n252-band-as-the-industry-pushes-for-direct-to-cell-connectivity)).

2) Can Samsung achieve scale and economics for a multi‑tens‑of‑billions investment?

Evidence suggests yes, with caveats on launch and regulatory pacing:

- Benchmarks: Starlink estimated $6–8B ARR by late 2025; U.S. residential subs ~3M by end‑2025, with global base larger. Deloitte projects enterprise subscribers will grow nearly 10x by 2030 to 3.4M; cumulative D2D+LEO investments ~ $10B by end‑2026 (industry-wide), modest compared to telco capex, signaling headroom for capital deployment ([SpaceNexus, 2026](https://spacenexus.us/guide/space-industry-market-size); [Via Satellite, 2026](https://interactive.satellitetoday.com/via/march-2026/examining-the-size-of-the-us-residential-broadband-opportunity-for-leo-satcom); [Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

- Addressable market: SEA and Middle East have significant underserved populations and enterprise/mobility demand (maritime, aviation, oil & gas, mining). GSMA/GSA data show widespread operator interest — 225 operator–satellite partnerships (88 countries) as of Jan 2026 — indicating distribution viability ([GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/)).

- Conclusion: A credible path exists to $10B+ annual revenue in ~10 years via combined consumer fixed broadband, enterprise/mobility, and D2D value-add, provided Samsung leverages device/install base synergies and wholesale telco channels.

3) Feasibility without proprietary launch?

Yes, if Samsung:

- Locks multi-year launch capacity across Ariane 6, ULA Vulcan, and Blue Origin New Glenn (Kuiper precedent shows feasibility), and supplements with regional medium-lift providers for in-plane replenishment and technology refresh; accepts some cost premium vs SpaceX; designs constellation shells to be deployable in phases ([Space Intel Report, 2022](https://www.spaceintelreport.com/amazon-contracts-for-68-launches-with-arianespace-blue-origin-ula-for-kuiper-broadband-constellation)).

4) Regulatory/geopolitical white spaces for a non-U.S.-aligned provider?

Yes. Several governments are pursuing sovereignty in space connectivity (IRIS² in EU; regional initiatives in Middle East). The FCC’s reciprocity inquiry underscores tensions that create openings for non‑U.S. vendors in markets sensitive to U.S. control. GSMA’s 2026 call for parity and harmonization suggests regulators are preparing to accommodate multiple LEO/D2D providers — an advantage for Samsung if it aligns with local policy priorities (gateways, LI, data protection) ([Access Partnership, 2026](https://accesspartnership.com/opinion/fcc-tests-reciprocity-satellite-market-access/); [GSMA, 2026](https://www.gsma.com/newsroom/press-release/gsma-calls-for-regulatory-readiness-for-direct-to-user-leo-satellite-services/); [Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

5) Beachhead market

- Primary: Indonesia and the Philippines — archipelagic geographies with persistent coverage gaps, rapidly digitizing economies, and growing openness to satellite partnerships (e.g., Globe’s Starlink collaboration indicates demand). Government priorities include disaster resilience and maritime safety, amplifying D2D’s value proposition ([Telecom Review Asia, 2026](https://www.telecomreviewasia.com/news/network-news/28362-ntt-docomo-to-launch-direct-satellite-to-smartphone-service-in-early-fy2026/)).

- Secondary: Saudi Arabia and the UAE — sizable budgets, sovereignty-oriented digital strategies, and enterprise/maritime/aviation demand; strong telco partners (stc, e&, du) and openness to public–private collaboration.

6) Optimal constellation size and regional deployment

- Start with a regional shell (~600–800 satellites) to serve SEA/Middle East at mid-inclination, adding polar capacity as mobility/aviation demand ramps. Grow to ~3,500 over 5–7 years to achieve near-global coverage. This mirrors Kuiper’s 3,236 plan and balances capex/risk. Leverage ISLs, Ka‑band NR‑NTN support, and ground beamforming to maximize spectral efficiency ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

7) Geographies where Samsung can win against incumbents

- Indonesia, Philippines, Malaysia, Vietnam (SEA): Underserved rural/island communities, disaster risk priorities, and maritime sectors; leverage Samsung’s device and telco relationships for D2D and backhaul.

- Saudi Arabia, UAE, Oman, Qatar (GCC): Enterprise/mobility focus; sovereign procurement channels; telco partners for hybrid mobile–satellite services.

- Turkey and North Africa (select markets): Emerging LEO adoption with white space for non‑U.S. providers.

8) Where to vertically integrate vs partner

- Integrate: Payload silicon (System LSI), memory (NAND/DRAM), modem chipsets for terminals, user terminals/phased arrays (consumer and enterprise), ground software/orchestration (through partnerships but with Samsung IP), Galaxy device NTN features.

- Partner/outsource: Launch services (multi-provider contracting), portions of satellite bus manufacturing (ramp via co-manufacturers initially), GSaaS providers for early ground coverage, and MNOs for distribution/spectrum roaming and billing.

This mix aligns with Samsung’s strengths and where cost/performance control matters most (terminals, payload silicon, device integration), while de-risking launch and accelerating ground deployment ([Viasat, 2024](https://www.viasat.com/perspectives/government/2024/how-ground-segment-as-a-service-supports-next-generation-satellite-communication/); [ST Engineering iDirect, 2026](https://www.satnow.com/news/details/4854-st-engineering-idirect-advances-satellite-ground-networks-with-intuition-cloud-native-technology)).

9) Optimal pace of entry and deployment

- Phase 1 (Years 0–2): Secure MNO partnerships; regulatory pathways; GSaaS-enabled ground; device enablement (Galaxy S26+). Launch pilot shell (~200–300 satellites) prioritizing SEA corridors; offer enterprise/maritime services and fixed broadband beta; D2D messaging for partner MNOs.

- Phase 2 (Years 2–4): Expand to ~600–800 satellites; scale consumer broadband; broaden enterprise SLAs with multi-orbit orchestration; introduce D2D voice in supported markets as standards/commercial readiness mature.

- Phase 3 (Years 4–7): Extend to ~3,500 satellites; regional-to-global expansion; invest in owned gateways where required; expand device ecosystem.

10) Role of local operator partnerships

Crucial. Partnerships enable:

- Spectrum access (MSS/IMT, SCS), lawful intercept compliance, and simplified licensing.

- Distribution via existing mobile channels, lowering CAC and churn.

- Hybrid backhaul and D2D handoffs, with billing integrated in operator plans.

GSA’s inventory of 225 operator–satellite partnerships in 88 countries and multiple launched services in Asia and the Americas underscore the model’s viability ([GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/); [Telecom Review Asia, 2026](https://www.telecomreviewasia.com/news/network-news/28362-ntt-docomo-to-launch-direct-satellite-to-smartphone-service-in-early-fy2026/)).

11) Key unit economics drivers

- Capex per satellite and launch cost per kg (supply chain and launch mix selection).

- Terminal BOM and pricing (leverage Samsung silicon, phased arrays, memory costs).

- ARPU mix (consumer fixed broadband vs enterprise/mobility vs wholesale/D2D).

- Utilization and spectral efficiency (digital payload flexibility, ISLs).

- Replacement rate (20–25% per year) and manufacturing cadence.

- Ground opex (GSaaS vs owned gateways), peering/cloud costs, and regulatory compliance costs (local gateways, LI) ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html); [New Space Economy, 2026](https://newspaceeconomy.ca/2026/02/25/satellite-broadband-communications-market-analysis-2026/)).

12) Can >$10B annual revenue be achieved in ~10 years ex‑U.S.?

Likely yes. With Starlink’s estimated $6–8B ARR circa 2025 and continued category growth (Deloitte projects rapid subscriber growth; enterprise subs ~3.4M by 2030), a diversified portfolio across SEA, Middle East, and additional ex‑U.S. regions can credibly scale beyond $10B by year 10, especially if enterprise/mobility and wholesale D2D are emphasized early ([SpaceNexus, 2026](https://spacenexus.us/guide/space-industry-market-size); [Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

13) High‑20% operating margin target at maturity?

Achievable with:

- Vertical integration in terminals/payload silicon.

- High enterprise/mobility mix (higher ARPUs, SLAs).

- GSaaS transitioning to hybrid owned gateways for cost optimization.

- Mature constellations with replacement efficiency and high utilization.

The satellite services sector historically supports robust margins when utilization is high and pricing power exists in niche enterprise markets. A maturing LEO operator with integrated device and ground stack can push opex discipline. Risks: launch cost spikes, regulatory compliance overhead, and price competition in consumer segments ([Viasat, 2024](https://www.viasat.com/perspectives/government/2024/how-ground-segment-as-a-service-supports-next-generation-satellite-communication/); [New Space Economy, 2026](https://newspaceeconomy.ca/2026/02/25/satellite-broadband-communications-market-analysis-2026/)).

14) Cumulative cash-flow breakeven by year 7–8?

Plausible under a phased capex plan and strong enterprise/D2D wholesale revenue ramp. The industry’s cumulative D2D+LEO investments (~$10B since 2019 through end‑2026) demonstrate that the scale of spend is manageable relative to telco capex. However, launch procurement and regulatory timing are critical to staying on schedule. Conservative planning should incorporate 12–18 months of potential delays in specific markets ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

15) IRR 11–13% with 5–7 year payback?

Feasible in a base case with:

- Regional shell-first deployment to accelerate early cash flows.

- Enterprise-heavy initial mix and D2D wholesale contracts.

- Pre-negotiated multi-year launch contracts to lock pricing/cadence.

- Leveraging Samsung’s hardware cost advantages.

Downside risks (launch cost inflation, regulatory lag, price competition) could push IRR lower; upside (rapid enterprise adoption, government anchor tenants, device-led D2D uptake) could improve returns.

16) Can a ~3,500-satellite constellation deliver target performance and coverage?

Yes. This is comparable to Kuiper (3,236 satellites) and smaller than Starlink’s full plans. With ISLs, flexible payloads, Ka‑band NR‑NTN support, and adequate ground gateways, ~3,500 satellites can support robust consumer and enterprise services regionally and globally, with D2D providing coverage-first augmentation. Shell-by-shell deployment should be optimized for target latitude bands (SEA/Middle East first) ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)).

17) Will launch costs continue to decline without SpaceX?

Trend: Yes, but at a slower pace and with more variance. As Ariane 6, Vulcan, and New Glenn ramp, competition and partial reusability will pressure prices and improve availability. However, near-term costs may be above SpaceX levels. Early procurement and anchor commitments can mitigate exposure ([Space Intel Report, 2022](https://www.spaceintelreport.com/amazon-contracts-for-68-launches-with-arianespace-blue-origin-ula-for-kuiper-broadband-constellation); [SpaceNexus, 2026](https://spacenexus.us/guide/space-industry-market-size)).

18) Can Samsung coordinate complex global regulatory approvals?

Yes, with a dedicated regulatory program and local partners:

- Follow GSMA’s five principles: transparency/predictability, parity, harmonization, collaboration, and balance innovation vs. national interests; align with WRC-27 outcomes; use local gateways where needed; ensure LI and data localization compliance ([GSMA, 2026](https://www.gsma.com/newsroom/press-release/gsma-calls-for-regulatory-readiness-for-direct-to-user-leo-satellite-services/); [CSI Magazine, 2026](https://www.csimagazine.com/csi/GSMA-D2D-call.php)).

- Use MNO partnerships to accelerate frequency coordination and reduce friction in spectrum authorization (MSS, IMT cooperation) ([GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/)).

19) Can Samsung leverage operator relationships for spectrum and distribution?

Yes. Samsung’s existing telco relationships (network equipment, devices) map directly to the GSA-documented momentum in MNO–satellite partnerships, enabling hybrid coverage, co-branded offers, billing integration, and roaming agreements critical for D2D. Examples in Asia (Japan operators, Philippines partnerships) demonstrate the path ([GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/); [Telecom Review Asia, 2026](https://www.telecomreviewasia.com/news/network-news/28362-ntt-docomo-to-launch-direct-satellite-to-smartphone-service-in-early-fy2026/)).

8. Competitive and Regulatory Dynamics

- Competitive intensity is rising: Starlink’s scale leads consumer; OneWeb (Eutelsat) targets enterprise/avionics; Kuiper entering in 2026; Telesat Lightspeed scaling; IRIS² building European sovereign capacity. D2D competition spans SpaceX/T‑Mobile, AST SpaceMobile (AT&T, Verizon, Vodafone), Lynk Global; GSA lists 16 launched D2D services and dozens more in the pipeline ([Deloitte Insights, 2026](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html); [GSA, 2026](https://gsacom.com/paper/5g-ntn-february-2026/)).

- Regulatory scrutiny: Interference and competition concerns (e.g., Viasat’s petition vs. SpaceX’s D2C buildout) highlight the need for careful spectrum and coexistence planning. GSMA’s guidance stresses preventing cross-border and domestic interference, and parity of obligations for satellite providers offering consumer services ([Broadband Breakfast, 2026](https://broadbandbreakfast.com/satellite-operators-opposed-to-spacexs-planned-direct-to-cell-constellation/); [Via Satellite/GSMA positions, 2025](https://www.satellitetoday.com/connectivity/2025/09/12/gsma-outlines-spectrum-regulatory-guidance-for-d2d-services/)).

9. Recommended Strategy for Samsung

- Positioning: “Coverage-first” D2D to any Galaxy (and partner Android devices) plus high-throughput fixed broadband and enterprise SLAs (maritime, aviation, energy, logistics). Emphasize regulatory alignment and local gateway options to address sovereignty and public safety needs.

- Vertical integration focus: User terminals (consumer and enterprise) leveraging Samsung silicon and memory, payload processing silicon, Galaxy device NTN features, and a Samsung-led (or co-developed) cloud-native ground orchestration platform that interworks with MNO cores via standard APIs.

- Partnerships: Lock tier-1 MNOs in SEA and GCC; pursue co-branded D2D safety and messaging offers; leverage MNO retail channels for CPE distribution; secure long-term multi-provider launch contracts; align with GSaaS partners for early coverage.

- Phasing and capital discipline: Deploy an initial regional shell sized for SEA/Middle East demand, with gateway siting to satisfy sovereignty and reduce latency; phase to 3,500 satellites as utilization milestones are met.

- Regulatory execution: Establish a centralized regulatory program with in-country experts; align with GSMA’s principles and WRC-27 outcomes; design for LI, data localization, and CALEA-like obligations by default.

10. Risks and Mitigations

- Launch cost/schedule risk: Hedge via multi-provider contracts; prioritize constellations shells serving early-revenue regions; modular satellite designs for flexibility.

- Regulatory delays: Pre-negotiate spectrum sharing (S/L-bands and FR1/FR2 allocations), landing rights, and lawful intercept with anchor MNOs and regulators; deploy local gateways.

- Competitive price pressure: Differentiate with device integration (Galaxy) and enterprise SLAs; bundle D2D with terrestrial plans via MNOs; offer tiered pricing and usage-based models.

- Replacement cycle opex: Build continuous manufacturing cadence; integrate COTS memory and standardized payload silicon to reduce costs.

11. Conclusion

The last 3–5 years have transformed LEO broadband and D2D from experimental to executable. Standardization (3GPP Rel-17/18 and early Rel-19 validation), smartphone readiness (Galaxy S26), a burgeoning operator–satellite partnership fabric, and mature cloud-native ground ecosystems all reduce risk and bring forward the feasible launch window. With a region-first plan focused on SEA and the Middle East, Samsung can leverage its silicon, device, and telco relationships to enter as a non‑U.S. alternative — meeting sovereignty and resilience needs while achieving competitive economics.

We recommend proceeding to a structured Phase 0 program: secure anchor MNOs and regulatory pathways in 3–4 beachhead countries; tender multi-year non‑SpaceX launch contracts; stand up GSaaS-based ground operations; finalize terminal and payload silicon roadmaps; and design Phase 1 (200–300 satellites) for early enterprise and consumer pilots. Managed in phases, the path to $10B+ revenue and high‑20% margins at maturity is credible, with breakeven in years 7–8 and IRR in the low teens achievable under base-case assumptions.

References

- Access Partnership. (2026, March). FCC Tests Reciprocity for Satellite Market Access. Access Partnership. [accesspartnership.com](https://accesspartnership.com/opinion/fcc-tests-reciprocity-satellite-market-access/)

- BusinessCom Networks. (2026, January 20). Samsung Advances D2D Connectivity as NTN Ecosystem Takes Shape. BusinessCom Networks. [bcsatellite.net](https://www.bcsatellite.net/blog/samsung-advances-d2d-connectivity-as-ntn-ecosystem-takes-shape/)

- CSI Magazine. (2026). GSMA urges governments to update rules as LEO D2D services start to scale. CSI Magazine. [csimagazine.com](https://www.csimagazine.com/csi/GSMA-D2D-call.php)

- Data Insights Market. (2026). LEO Satellite Communication Phased Array Antenna Report: Trends and Forecasts 2026–2034. Data Insights Market. [datainsightsmarket.com](https://www.datainsightsmarket.com/reports/leo-satellite-communication-phased-array-antenna-924115)

- Dataintelo. (2026). Ground Segment as a Service Market Research Report 2033. Dataintelo. [dataintelo.com](https://dataintelo.com/report/ground-segment-as-a-service-market)

- Deloitte Insights. (2026). Next-gen satellite internet. Deloitte. [deloitte.com](https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/next-gen-satellite-internet.html)

- GSA. (2026). 5G NTN February 2026. GSA. [gsacom.com](https://gsacom.com/paper/5g-ntn-february-2026/)

- GSMA. (2026, March 3). GSMA Calls for Regulatory Readiness for Direct-to-User LEO Satellite Services. GSMA Newsroom. [gsma.com](https://www.gsma.com/newsroom/press-release/gsma-calls-for-regulatory-readiness-for-direct-to-user-leo-satellite-services/)

- IEEE ComSoc Technology Blog. (2026). 3GPP Release 17 & 18 – NTN enhancements. IEEE ComSoc. [techblog.comsoc.org](https://techblog.comsoc.org/tag/3gpp-release-17-18)

- Kbssidhu. (2026). Elon Musk’s Starlink Aims for “Direct-to-Cell” With New Spectrum in Global Push. Substack. [kbssidhu.substack.com](https://kbssidhu.substack.com/p/elon-musks-starlink-aims-for-direct)

- Kratos Space. (2025). Predictions for the Space Industry in 2025. Kratos. [kratosspace.com](https://www.kratosspace.com/constellations/articles/predictions-for-the-space-industry-in-2025)

- New Space Economy. (2026, February 25). Satellite Broadband Communications Market Analysis 2026. New Space Economy. [newspaceeconomy.ca](https://newspaceeconomy.ca/2026/02/25/satellite-broadband-communications-market-analysis-2026/)

- RCR Wireless. (2026, January 12). Keysight, Samsung demonstrate NR‑NTN link in n252 band as direct‑to‑cell connectivity takes shape. RCR Wireless. [rcrwireless.com](https://www.rcrwireless.com/20260112/test-measurement/keysight-samsung-demonstrate-nr-ntn-link-in-n252-band-as-the-industry-pushes-for-direct-to-cell-connectivity)

- Runway Girl Network. (2024, March). ST Engineering iDirect unveils Intuition at SATELLITE 2024. Runway Girl Network. [runwaygirlnetwork.com](https://runwaygirlnetwork.com/2024/03/st-engineering-idirect-intuition/)

- Samsung Newsroom U.S. (2026). Samsung Expands Satellite Communication Support to Galaxy Smartphones in the U.S. Samsung. [news.samsung.com](https://news.samsung.com/us/samsung-brings-satellite-communication-support-galaxy-smartphones-in-us/)

- Samsung Research. (2025). NTN and TN networks for the 6G era: technology overview and regulatory challenges. Samsung Research. [research.samsung.com](https://research.samsung.com/blog/NTN-and-TN-networks-for-the-6G-era-technology-overview-and-regulatory-challenges)

- Space Intel Report. (2022, April 5). Amazon contracts for 68 launches with Arianespace, Blue Origin, ULA for Kuiper broadband constellation. Space Intel Report. [spaceintelreport.com](https://www.spaceintelreport.com/amazon-contracts-for-68-launches-with-arianespace-blue-origin-ula-for-kuiper-broadband-constellation)

- SpaceNexus. (2026). Space Industry Market Size 2026: Data, Trends & Forecasts. SpaceNexus Guide. [spacenexus.us](https://spacenexus.us/guide/space-industry-market-size)

- ST Engineering iDirect. (2026, March 10). ST Engineering iDirect Partners with Q‑KON to Democratize Connectivity across Africa with Intuition Unbound. ST Engineering iDirect. [idirect.net](https://www.idirect.net/news/st-engineering-idirect-partners-with-q-kon-to-democratize-connectivity-across-africa-with-intuition-unbound/)

- ST Engineering iDirect via SatNow. (2026). ST Engineering iDirect Advances Satellite Ground Networks with Intuition Cloud‑Native Technology. SatNow. [satnow.com](https://www.satnow.com/news/details/4854-st-engineering-idirect-advances-satellite-ground-networks-with-intuition-cloud-native-technology)

- Telecom Review Asia. (2026). NTT DOCOMO to Launch Direct Satellite-to-Smartphone Service in Early FY2026. Telecom Review Asia. [telecomreviewasia.com](https://www.telecomreviewasia.com/news/network-news/28362-ntt-docomo-to-launch-direct-satellite-to-smartphone-service-in-early-fy2026/)

- 360iResearch. (2026, March). LEO Terminals Market Size & Share 2026–2032. 360iResearch. [360iresearch.com](https://www.360iresearch.com/library/intelligence/leo-terminals)

- Via Satellite (SatelliteToday). (2026, March). Examining the Size of the U.S. Residential Broadband Opportunity for LEO Satcom. Via Satellite. [interactive.satellitetoday.com](https://interactive.satellitetoday.com/via/march-2026/examining-the-size-of-the-us-residential-broadband-opportunity-for-leo-satcom)

- WSJ/Deloitte. (2026). Next-Gen Satellite Internet: Shifting Prices, Capacity, and Opportunities. The Wall Street Journal (Deloitte). [deloitte.wsj.com](https://deloitte.wsj.com/cmo/next-gen-satellite-internet-shifting-prices-capacity-and-opportunities-e8c8b90a?gaa_at=eafs&gaa_n=AWEtsqe_ibW6fW2ulkKmlZmg88UNJktLKZGIW9BAOF3Px3kOO__vJiToKuP7&gaa_ts=69bda32c&gaa_sig=HeRPOSVZFERcbGXxdHBC6qnAsIyKUZ-iZVGOrnGoocVbxe8FFjaybzP07bopko_UvVtZRLlictvDnavz8iFylw%3D%3D)

- 9to5Google. (2026, February 27). Samsung confirms satellite connectivity for Galaxy S26, more. 9to5Google. [9to5google.com](https://9to5google.com/2026/02/27/samsung-confirms-satellite-connectivity-for-galaxy-s26-and-older-galaxy-devices/)

- Viasat. (2024, January 24). How Ground-Segment-as-a-Service supports next-generation satellite communication. Viasat. [viasat.com](https://www.viasat.com/perspectives/government/2024/how-ground-segment-as-a-service-supports-next-generation-satellite-communication/)

Note: All hyperlinks above point to the referenced sources.