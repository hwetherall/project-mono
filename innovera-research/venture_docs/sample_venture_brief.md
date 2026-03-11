# AquaSense Technologies — Venture Brief

## Company Overview

AquaSense Technologies is a pre-revenue B2B SaaS startup developing AI-powered water infrastructure monitoring for municipal water utilities and industrial facilities. The company is headquartered in Austin, TX and targeting the North American market initially, with plans to expand to the EU.

## The Problem

Municipal water utilities across North America lose an estimated 20-30% of treated water to leaks in aging distribution networks. The American Water Works Association estimates over $1 trillion in needed infrastructure investment over the next 25 years. Current leak detection methods are overwhelmingly manual — field crews using acoustic listening devices cover 2-5 miles of pipe per day. Most utilities operate reactively, discovering leaks only after visible surface damage, customer complaints, or catastrophic pipe failures.

The consequences are severe:
- **Financial loss**: Utilities lose $2.6 billion annually in non-revenue water in the US alone
- **Safety risk**: Water main breaks cause road collapses, property damage, and service disruptions affecting public health
- **Regulatory pressure**: EPA's LCRR (Lead and Copper Rule Revisions) and state-level water loss mandates (e.g., California SB 555) are creating compliance deadlines for water loss auditing
- **Aging workforce**: 30-50% of utility operators are eligible for retirement within 5 years, with insufficient replacement hiring

## The Solution

AquaSense deploys a network of IoT acoustic sensors on water mains combined with a cloud-based AI platform that:
1. Continuously monitors pipe vibration signatures to detect leaks in real-time
2. Uses machine learning to classify leak severity and predict pipe failure probability
3. Prioritizes maintenance work orders by risk score, integrating with existing SCADA/GIS systems
4. Generates automated compliance reports for AWWA water audits

The sensor hardware uses low-power cellular (LTE-M) connectivity and is designed for non-invasive installation on existing pipe infrastructure (no excavation required).

## Target Customer

Primary: Municipal water utilities serving populations of 50,000-500,000 (approximately 1,200 utilities in the US). These mid-sized utilities have the greatest need — large enough to face significant water loss but too small to afford building proprietary monitoring systems.

Secondary: Industrial facilities with critical water infrastructure (food/beverage manufacturing, data centers, pharmaceutical plants).

Key buyer personas:
- **Utility Director / General Manager**: Budget authority, concerned with regulatory compliance and capital efficiency
- **Operations Manager**: Day-to-day operations, concerned with crew productivity and emergency response
- **Chief Financial Officer**: Focused on non-revenue water recovery ROI and capital planning

## Business Model

SaaS subscription with hardware lease:
- Hardware: Sensors leased at $150/unit/year (avg. deployment: 200-500 sensors per utility)
- Software: Platform subscription at $3-8 per service connection per year
- Target ACV: $75,000-$250,000 per utility customer
- Expected payback period for customer: 12-18 months through reduced water loss

## Competitive Landscape (Known)

- **Xylem (Visenti/Pure Technologies)**: Large incumbent, acquired several leak detection companies. Enterprise-focused, expensive, complex deployments.
- **Mueller Water Products (Echologics)**: Hardware-heavy approach, acoustic correlators. Less software sophistication.
- **FIDO AI**: UK-based, AI leak detection from acoustic data. Primarily UK/EU market presence.
- **Fracta**: AI-based pipe condition assessment (not real-time monitoring). Acquired by Kurita Water Industries.

Workarounds in use today: Manual acoustic surveys, drive-by acoustic screening, pressure monitoring with basic threshold alerts, district metered areas (DMA) with manual analysis.

## Technology Stack

IoT sensors (custom hardware), LTE-M/NB-IoT connectivity, AWS cloud infrastructure, Python/TensorFlow ML pipeline, React dashboard, REST API for SCADA/GIS integration.

## Stage & Funding

Pre-revenue. Completing pilot with 2 municipal utilities. Seeking $3M seed round. Founding team includes former Xylem engineer (CTO) and utility operations executive (CEO).

## Key Claims

- TAM: Global smart water management market valued at $15.7B by 2027 (MarketsandMarkets)
- Non-revenue water costs US utilities $2.6B/year
- AquaSense sensor deployment is 10x faster than traditional permanent acoustic monitoring
- ML model achieves 94% leak detection accuracy in controlled testing
