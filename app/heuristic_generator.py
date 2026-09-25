"""
Easeprompt Built-in Semantic Expansion & Heuristic Knowledge Engine.
Provides deterministic, zero-dependency, production-grade prompt expansion
based on domain ontologies, intent classification, and prompt engineering best practices.
"""

import re
from typing import Dict, List, Tuple, Any
from .models import TargetAgent, FrameworkStyle, ExpansionDepth, ExplanationData, PlaceholderItem


# Domain Knowledge Bases with rich contextual expansions
DOMAIN_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "crypto": {
        "keywords": ["crypto", "bitcoin", "ethereum", "blockchain", "token", "defi", "wallet", "tracker", "web3", "solana"],
        "domain": "Web3 & Distributed Quantitative Finance",
        "role_titles": {
            TargetAgent.CODING_ASSISTANT: "Principal Web3 Full-Stack Engineer and Quantitative Crypto Systems Architect",
            TargetAgent.DATA_ANALYST: "Lead Crypto On-Chain Quantitative Analyst and Tokenomics Researcher",
            TargetAgent.AUTONOMOUS_AGENT: "Autonomous DeFi Arbitrage and Liquidity Monitoring Agent",
            TargetAgent.SYSTEM_ARCHITECT: "Chief Architect of High-Throughput Financial & Web3 Infrastructure",
            TargetAgent.SECURITY_AUDITOR: "Senior Smart Contract and Web3 Protocol Security Auditor",
            TargetAgent.CREATIVE_WRITER: "Web3 Investigative Tech Journalist and Cypherpunk Narrative Lead",
            TargetAgent.GENERAL_PURPOSE: "Principal Crypto Market and Blockchain Technology Strategist"
        },
        "extrapolated_context": [
            "Real-time WebSocket data streaming vs. REST polling trade-offs for order book and ticker updates.",
            "Rate limiting, API key rotation, and caching strategies (e.g. Redis) against public exchange endpoints (CoinGecko, Binance, Kraken).",
            "Data normalization across heterogeneous exchange formats, gas fees, and slippage tolerance calculations.",
            "Graceful handling of dropped WebSocket connections with exponential backoff and heartbeat checks.",
            "Client-side UI reactivity with zero layout shift during high-frequency price updates."
        ],
        "placeholders": [
            PlaceholderItem(tag="[INSERT DATA_PROVIDER_API_KEY]", label="Data Provider API Key", description="API key for price aggregator or RPC provider", default_value="COINGECKO_DEMO_KEY", example="cg-api-key-928374"),
            PlaceholderItem(tag="[SPECIFY TRACKED_ASSETS]", label="Tracked Assets", description="Comma-separated list of crypto assets or contract addresses", default_value="BTC, ETH, SOL, AVAX", example="BTC, ETH, SOL"),
            PlaceholderItem(tag="[SPECIFY UPDATE_INTERVAL_MS]", label="Polling/Refresh Interval", description="Desired frequency for refreshing price feeds in milliseconds", default_value="3000", example="2500"),
            PlaceholderItem(tag="[SPECIFY FIAT_CURRENCY]", label="Base Fiat Currency", description="Target denomination currency for valuations", default_value="USD", example="USD, EUR, GBP")
        ],
        "actionable_steps": [
            "Establish resilient data ingestion architecture with failover between primary WebSocket feed and secondary REST pollers.",
            "Implement high-performance local state management (e.g., in-memory ring buffers or reactive stores) to prevent UI thread lock.",
            "Format price calculations with fixed-point decimal precision (avoid IEEE 754 floating point drift for financial ledgers).",
            "Build responsive portfolio calculations: 24h P&L change, volume weighting, and historical trend sparks.",
            "Include comprehensive integration tests with mocked WebSocket disconnection and reconnection events."
        ],
        "negative_constraints": [
            "DO NOT use raw JavaScript `Number` or floating-point math for balance calculations; use `BigNumber`, `Decimal.js`, or integer cents/wei.",
            "DO NOT hardcode API credentials or private keys in client-side bundles or repository files.",
            "DO NOT blast exchange REST APIs without backoff strategies; avoid triggering 429 Too Many Requests.",
            "DO NOT produce mock or placeholder UI skeletons with fake static numbers; wire real streaming hooks."
        ],
        "output_schema": """{
  "status": "success",
  "data": {
    "assets": [
      {
        "symbol": "BTC",
        "current_price_usd": 68450.25,
        "change_24h_percent": 3.42,
        "volume_24h_usd": 28400000000,
        "last_updated_timestamp": 1740000000
      }
    ],
    "portfolio_valuation": {
      "total_fiat": 142500.80,
      "unrealized_pnl_usd": 12450.30
    }
  }
}"""
    },
    "churn": {
        "keywords": ["churn", "retention", "customer churn", "attrition", "cohort", "clv", "lifetime value", "user churn"],
        "domain": "Enterprise Product Analytics & Predictive Machine Learning",
        "role_titles": {
            TargetAgent.CODING_ASSISTANT: "Staff ML Engineer & Production Data Pipeline Architect",
            TargetAgent.DATA_ANALYST: "Principal Predictive Customer Analytics & Retention Data Scientist",
            TargetAgent.AUTONOMOUS_AGENT: "Autonomous Customer Health & Intervention Agent",
            TargetAgent.SYSTEM_ARCHITECT: "Chief Data Platform Architect (Modern Data Stack & Feature Stores)",
            TargetAgent.SECURITY_AUDITOR: "Data Privacy & Governance Officer (GDPR / CCPA / PII Auditor)",
            TargetAgent.CREATIVE_WRITER: "Customer Retention & Lifecycle Email Campaign Director",
            TargetAgent.GENERAL_PURPOSE: "Executive Growth & Retention Operations Specialist"
        },
        "extrapolated_context": [
            "Survival analysis (Kaplan-Meier, Cox Proportional Hazards) combined with binary classification (XGBoost, LightGBM).",
            "Feature engineering from user telemetry: session decay velocity, license utilization ratio, and support ticket sentiment.",
            "Addressing extreme class imbalance (churn is often <5% of active cohort) via SMOTE, focal loss, or PR-AUC optimization.",
            "Translating model probabilities into dollar-quantified risk cohorts and targeted retention interventions.",
            "SHAP (SHapley Additive exPlanations) values to isolate top individual churn drivers for customer success teams."
        ],
        "placeholders": [
            PlaceholderItem(tag="[INSERT DATASET_SOURCE]", label="Data Source / Warehouse", description="Target database, table name, or CSV URI", default_value="analytics_dw.customer_events_v2", example="bigquery-public-data.churn"),
            PlaceholderItem(tag="[SPECIFY INACTIVITY_WINDOW_DAYS]", label="Churn Definition Window", description="Number of inactive days considered a definitive churn event", default_value="30", example="45"),
            PlaceholderItem(tag="[SPECIFY PRIMARY_METRIC]", label="Evaluation Metric", description="Model optimization target metric", default_value="PR-AUC / Recall@Top20%", example="F1-Score / PR-AUC"),
            PlaceholderItem(tag="[TARGET_OUTPUT_TIERS]", label="Risk Tiers", description="Segmentation cutoffs for churn risk", default_value="Critical (>75%), High (50-75%), Medium (25-50%), Low (<25%)", example="Low, Medium, High")
        ],
        "actionable_steps": [
            "Perform comprehensive Exploratory Data Analysis (EDA) on event logs, isolating tenure correlation with drop-off curves.",
            "Formulate reproducible SQL feature extraction CTEs computing 30-day moving averages of login frequency and feature adoption.",
            "Train and cross-validate baseline logistic regression against gradient boosted decision trees (XGBoost) with stratified k-fold.",
            "Generate global and local SHAP feature importances to extract the top 5 causal drivers of attrition.",
            "Synthesize actionable playbook recommendations for Account Executives prioritizing accounts by expected ARR loss."
        ],
        "negative_constraints": [
            "DO NOT report raw accuracy score; class imbalance makes 95% accuracy useless if all churners are missed.",
            "DO NOT introduce data leakage (future look-ahead bias) during feature engineering time-window splits.",
            "DO NOT present opaque black-box predictions without explanatory feature weights or confidence intervals.",
            "DO NOT recommend generic marketing actions (e.g. 'send newsletter') without tailoring to customer tier and churn driver."
        ],
        "output_schema": """| Cohort Risk Tier | Churn Probability | Count of Accounts | At-Risk ARR ($) | Primary Root Driver | Recommended Action |
|:---|:---:|:---:|:---:|:---|:---|
| Critical Risk | > 80% | 142 | $1,240,000 | Zero logins past 21d + pending unresolved P1 ticket | Immediate CSM intervention + technical escalation call |
| Elevated Risk | 50% - 80% | 385 | $2,150,000 | Seat utilization < 30% after onboarding month 3 | Targeted product adoption training & executive review |"""
    },
    "auth": {
        "keywords": ["auth", "authentication", "authorization", "oauth", "jwt", "login", "sso", "rbac", "security", "microservice auth"],
        "domain": "Identity, Access Management & Zero-Trust Cloud Architecture",
        "role_titles": {
            TargetAgent.CODING_ASSISTANT: "Principal Cloud Security Engineer and Distributed Systems IAM Specialist",
            TargetAgent.DATA_ANALYST: "Identity Threat & Anomaly Detection Data Specialist",
            TargetAgent.AUTONOMOUS_AGENT: "Autonomous Zero-Trust Access Broker & Token Sentinel",
            TargetAgent.SYSTEM_ARCHITECT: "Chief Enterprise IAM & Security Architect",
            TargetAgent.SECURITY_AUDITOR: "Lead Red-Team Penetration Tester & OAuth/OIDC Security Auditor",
            TargetAgent.CREATIVE_WRITER: "Cybersecurity Technical Documentation Lead",
            TargetAgent.GENERAL_PURPOSE: "Principal Application Security Strategist"
        },
        "extrapolated_context": [
            "OAuth 2.1 / OIDC architecture with PKCE (Proof Key for Code Exchange) flow for public and confidential clients.",
            "Stateless JWT access tokens with RS256/ES256 asymmetric cryptographic signing and fast JWKS cache rotation.",
            "Revocation lists, refresh token rotation with single-use replay detection, and session binding.",
            "Fine-grained authorization via Role-Based Access Control (RBAC) or Attribute-Based Access Control (ABAC/OpenFGA).",
            "Rate limiting against credential stuffing, brute force, and token endpoint abuse."
        ],
        "placeholders": [
            PlaceholderItem(tag="[INSERT IDENTITY_PROVIDER]", label="Identity Provider / Protocol", description="Auth provider or framework", default_value="Keycloak / Auth0 / NextAuth / Cognito", example="Keycloak 24"),
            PlaceholderItem(tag="[SPECIFY TOKEN_EXPIRATION_SEC]", label="Access Token TTL", description="Lifespan of short-lived access token in seconds", default_value="900 (15 min)", example="300"),
            PlaceholderItem(tag="[SPECIFY USER_ROLES_PERMISSIONS]", label="Roles Matrix", description="Defined user roles and permission scopes", default_value="admin:all, editor:write, viewer:read", example="admin, user"),
            PlaceholderItem(tag="[TARGET_BACKEND_FRAMEWORK]", label="Backend Framework", description="Runtime framework for auth middleware", default_value="FastAPI / Node.js Express / Go Gin", example="FastAPI")
        ],
        "actionable_steps": [
            "Design the authorization handshake adhering strictly to OAuth 2.1 specifications with PKCE.",
            "Implement asymmetric RS256 signature verification validating issuer, audience, and expiration claims.",
            "Construct a reusable middleware interceptor that injects validated user context into request handlers.",
            "Implement secure HTTP-only, SameSite=Strict cookies for refresh token persistence to mitigate XSS exposure.",
            "Define audit logging endpoints emitting structured security telemetry for failed authentications."
        ],
        "negative_constraints": [
            "DO NOT store JWT access or refresh tokens in browser `localStorage` or `sessionStorage` (XSS vulnerability).",
            "DO NOT use symmetric HS256 with weak shared secrets across distributed microservices; use asymmetric RS256/ES256.",
            "DO NOT accept tokens with `alg: 'none'` or omit audience and issuer claim verification.",
            "DO NOT write custom cryptographic signing routines; use vetted, audited libraries (e.g. PyJWT, Jose, Iron)."
        ],
        "output_schema": """interface AuthSecuritySpec {
  issuerUrl: string;
  algorithmsSupported: ["RS256", "ES256"];
  tokenEndpoints: {
    authorize: "/oauth/v2/authorize";
    token: "/oauth/v2/token";
    jwks: "/.well-known/jwks.json";
    revoke: "/oauth/v2/revoke";
  };
  securityPolicies: {
    enforcePkce: true;
    refreshTokenRotation: true;
    maxTokenAgeSeconds: 900;
  };
}"""
    },
    "database": {
        "keywords": ["sql", "database", "postgres", "mysql", "mongodb", "indexing", "query", "optimize", "slow query"],
        "domain": "High-Concurrency Database Systems & Query Optimization",
        "role_titles": {
            TargetAgent.CODING_ASSISTANT: "Staff Database Reliability Engineer and Performance Tuning Specialist",
            TargetAgent.DATA_ANALYST: "Senior Analytics Engineer & Data Warehouse Optimizer",
            TargetAgent.AUTONOMOUS_AGENT: "Autonomous Query Execution Planner & Index Optimizer",
            TargetAgent.SYSTEM_ARCHITECT: "Principal Database Architect (Sharding, Replication & Partitioning)",
            TargetAgent.SECURITY_AUDITOR: "Database Security & SQL Injection Vulnerability Auditor",
            TargetAgent.CREATIVE_WRITER: "Technical Systems Author & Database Internal Guide Writer",
            TargetAgent.GENERAL_PURPOSE: "Principal Database Performance Consultant"
        },
        "extrapolated_context": [
            "Deep EXPLAIN (ANALYZE, BUFFERS, VERBOSE) query plan dissection: identifying sequential scans, bad row estimates, and disk spills.",
            "Index design strategies: composite B-Tree indexing order (equality then range), partial indexes, and GiST/GIN for specialized data types.",
            "Connection pooling (PgBouncer, HikariCP) and transaction isolation levels to mitigate deadlock conditions.",
            "Table partitioning (declarative range/hash) and autovacuum tuning for write-heavy high-churn workloads."
        ],
        "placeholders": [
            PlaceholderItem(tag="[INSERT DATABASE_ENGINE]", label="Database Engine & Version", description="e.g. PostgreSQL 16, MySQL 8.0, ClickHouse", default_value="PostgreSQL 16", example="PostgreSQL 16.2"),
            PlaceholderItem(tag="[INSERT TABLE_SCHEMA_DDL]", label="Target Table Schema DDL", description="DDL definitions with current primary and foreign keys", default_value="CREATE TABLE transactions (id UUID PRIMARY KEY, user_id UUID, amount DECIMAL, created_at TIMESTAMPTZ);", example="schema.sql"),
            PlaceholderItem(tag="[INSERT SLOW_QUERY_SQL]", label="Slow Query SQL", description="The slow or problematic query under review", default_value="SELECT * FROM transactions WHERE user_id = ... ORDER BY created_at DESC LIMIT 50;", example="query.sql"),
            PlaceholderItem(tag="[TARGET_LATENCY_BUDGET_MS]", label="Target Query SLA", description="Desired maximum execution time in milliseconds", default_value="50ms at p99", example="20ms")
        ],
        "actionable_steps": [
            "Examine query semantics and generate step-by-step diagnostic breakdown of the EXPLAIN execution plan.",
            "Eliminate unnecessary `SELECT *` projection and N+1 join overheads.",
            "Propose optimal covering index or composite index matching query predicates.",
            "Evaluate partitioning and memory work_mem allocation implications.",
            "Provide the revised, optimized SQL query along with before-and-after performance metrics."
        ],
        "negative_constraints": [
            "DO NOT advise adding indexes blindly to every filtered column; each index penalizes write throughput.",
            "DO NOT perform functions on indexed columns in the WHERE clause (e.g. `WHERE DATE(created_at) = ...`) which disables index scans.",
            "DO NOT suggest running disruptive `CREATE INDEX` on production without the `CONCURRENTLY` flag.",
            "DO NOT neglect NULL handling and sorting direction (ASC/DESC NULLS LAST) in composite indexes."
        ],
        "output_schema": """-- Step 1: Optimized Covering Index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transactions_user_created 
ON transactions (user_id, created_at DESC) 
INCLUDE (amount);

-- Step 2: Refactored Execution Query
-- Query runtime improved from 4,200ms -> 12ms (350x speedup)
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, user_id, amount, created_at
FROM transactions
WHERE user_id = '[INSERT TARGET_USER_UUID]'
ORDER BY created_at DESC
LIMIT 50;"""
    },
    "app": {
        "keywords": [
            "app", "application", "mobile app", "web app", "desktop app",
            "ios app", "android app", "react native", "flutter", "pwa",
            "full-stack app", "software app"
        ],
        "domain": "Modern Full-Stack Application Architecture & Product Engineering",
        "role_titles": {
            TargetAgent.CODING_ASSISTANT: "Principal Full-Stack Product Architect and Lead Systems Engineer",
            TargetAgent.DATA_ANALYST: "Staff Product Analytics & User Journey Data Scientist",
            TargetAgent.AUTONOMOUS_AGENT: "Autonomous Full-Stack Application Scaffolding & Code Generation Agent",
            TargetAgent.SYSTEM_ARCHITECT: "Chief Full-Stack Solutions Architect (Distributed Web & Mobile Systems)",
            TargetAgent.SECURITY_AUDITOR: "Senior Application Security Architect (OWASP, Zero-Trust, Auth & Data Protection)",
            TargetAgent.CREATIVE_WRITER: "Principal Product Experience Strategist and UX Copy Lead",
            TargetAgent.GENERAL_PURPOSE: "Principal Application Engineering and Technical Strategy Consultant"
        },
        "extrapolated_context": [
            "End-to-end user journey mapping: from onboarding, core task completion, to retention loops.",
            "Client-server synchronization, state management (Zustand/Redux/React Query), and optimistic UI updates.",
            "Type-safe API contract layer (tRPC, REST with OpenAPI/Zod, or GraphQL) between frontend and backend.",
            "Responsive layout design with zero visual shift (CLS), mobile touch ergonomics, and WCAG AA accessibility.",
            "Defensive edge error boundaries, retry policies, and graceful offline fallback states."
        ],
        "placeholders": [
            PlaceholderItem(tag="[SPECIFY APPLICATION_TYPE]", label="Application Type & Purpose", description="Specific category or problem solved (e.g. Real-Time Chat, E-Commerce, Habit Tracker)", default_value="SaaS Workflow Tool", example="E-Commerce Marketplace"),
            PlaceholderItem(tag="[SPECIFY TARGET_PLATFORM]", label="Target Platform & Modality", description="Deployment target: Web, Native Mobile (iOS/Android), or Desktop", default_value="Responsive Web / PWA (Next.js + Tailwind)", example="iOS & Android (React Native Expo)"),
            PlaceholderItem(tag="[SPECIFY CORE_USER_WORKFLOW]", label="Core Hero Workflow", description="Primary action step taken by users in the app", default_value="Sign in -> Create project -> Collaborate in real-time -> Export", example="Search item -> Add to cart -> Checkout with Stripe"),
            PlaceholderItem(tag="[SPECIFY DATA_PERSISTENCE]", label="Database & Auth Provider", description="Backend storage and authentication mechanism", default_value="PostgreSQL with Supabase / Prisma ORM", example="PostgreSQL / Supabase Auth"),
            PlaceholderItem(tag="[SPECIFY TARGET_TECH_STACK]", label="Target Tech Stack", description="Frontend framework, backend runtime, and styling system", default_value="TypeScript, Next.js 14, Tailwind CSS, Node.js", example="React Native, Expo, NativeWind")
        ],
        "actionable_steps": [
            "Clarify core user workflow and map user state transitions from initial landing to task completion.",
            "Formulate database schemas with relational integrity, foreign keys, and indexes on query predicates.",
            "Implement type-safe API route handlers and services with defensive input validation (Zod / Pydantic).",
            "Build accessible, responsive UI components with loading skeletons, optimistic updates, and error boundaries.",
            "Implement automated verification testing covering critical user paths and edge-case error cascades."
        ],
        "negative_constraints": [
            "DO NOT write mock or truncated code snippets with comments like '// implement here' or '/* rest of code */'.",
            "DO NOT build arbitrary or untestable UI without knowing the target platform and primary workflow.",
            "DO NOT store unhashed passwords, leak secret API keys to frontend bundles, or bypass input validation.",
            "DO NOT build non-responsive interfaces that break on smaller mobile screens or lack loading/error states."
        ],
        "output_schema": """{
  "application_spec": {
    "app_name": "[SPECIFY APP_NAME]",
    "platform": "Responsive Web (Next.js) | Native Mobile (React Native)",
    "primary_workflow": "User Authentication -> Data Operations -> Telemetry / Export",
    "architecture_layers": {
      "presentation": "TypeScript, Tailwind CSS, Responsive Components",
      "state_and_api": "Optimistic UI, React Query / tRPC / Server Actions",
      "persistence": "PostgreSQL, Prisma / Supabase ORM, Zero-Trust RLS"
    },
    "verification_status": "spec_ready"
  }
}"""
    },
    "generic": {
        "keywords": [],
        "domain": "Production Systems & Algorithmic Problem Solving",
        "role_titles": {
            TargetAgent.CODING_ASSISTANT: "Principal Full-Stack Systems Engineer and Lead Software Architect",
            TargetAgent.DATA_ANALYST: "Lead Quantitative Data Strategist and Systems Analyst",
            TargetAgent.AUTONOMOUS_AGENT: "Autonomous Task Execution Agent and Systems Operator",
            TargetAgent.SYSTEM_ARCHITECT: "Chief Enterprise Technology Architect",
            TargetAgent.SECURITY_AUDITOR: "Principal Cybersecurity & Quality Assurance Auditor",
            TargetAgent.CREATIVE_WRITER: "Executive Narrative Director and Technical Writer",
            TargetAgent.GENERAL_PURPOSE: "Principal Technical Strategy and Problem-Solving Specialist"
        },
        "extrapolated_context": [
            "Production lifecycle considerations: operational stability, error resilience, telemetry, and automated verification.",
            "Strict separation of concerns, defensive programming, and modular extensibility.",
            "Clear performance SLAs, deterministic inputs/outputs, and edge-case boundary checks.",
            "Graceful degradation and fail-soft behavior under degraded network or resource constraints."
        ],
        "placeholders": [
            PlaceholderItem(tag="[INSERT TARGET_TECH_STACK]", label="Target Tech Stack", description="Preferred programming languages, frameworks, and deployment target", default_value="Python 3.12 / TypeScript / Docker", example="Node.js 20 & React"),
            PlaceholderItem(tag="[SPECIFY OPERATING_ENVIRONMENT]", label="Runtime Environment", description="Local dev, staging, or production cloud environment", default_value="AWS ECS / Cloud Run / Kubernetes", example="AWS Lambda"),
            PlaceholderItem(tag="[SPECIFY PRIMARY_KPI]", label="Primary Success Metric", description="Key deliverable or performance criterion", default_value="P99 latency < 100ms with zero unhandled exceptions", example="Throughput > 500 RPS"),
            PlaceholderItem(tag="[INSERT SAMPLE_PAYLOAD]", label="Sample Input Payload", description="Concrete example data object or payload", default_value="{\"id\": \"item_123\", \"status\": \"pending\"}", example="payload.json")
        ],
        "actionable_steps": [
            "Deconstruct the operational requirements into clear functional and non-functional specifications.",
            "Provide complete, idiomatic, and production-tested implementation blueprints without placeholder ellipsis.",
            "Implement defensive validation layers to intercept invalid states at system boundaries.",
            "Document edge-case handling for network partition, timeouts, and resource starvation.",
            "Include automated verification tests verifying both nominal flows and failure cascades."
        ],
        "negative_constraints": [
            "DO NOT write mock or truncated code snippets with comments like '// implement here' or '...rest of code'.",
            "DO NOT rely on deprecated APIs, vulnerable third-party dependencies, or non-deterministic state.",
            "DO NOT produce vague or untestable recommendations; ground every answer in actionable, concrete code or steps.",
            "DO NOT ignore security implications (unfiltered inputs, unauthorized access, or silent failure suppressions)."
        ],
        "output_schema": """{
  "system_status": "operational",
  "execution_summary": {
    "deliverables_completed": ["Architecture", "Production Implementation", "Verification Suite"],
    "benchmarks_met": true
  }
}"""
    }
}


UNDERSPECIFIED_SEEDS = {
    "app", "an app", "the app", "new app", "application", "mobile app", "web app",
    "website", "a website", "the website", "web page", "tool", "a tool", "software",
    "saas", "dashboard", "platform", "bot", "script", "program", "code"
}


def is_underspecified_input(input_text: str) -> bool:
    """
    Detects if the input is a single broad keyword or underspecified seed
    that lacks critical domain requirements (e.g. 'app', 'website', 'tool').
    """
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', input_text).strip().lower()
    words = clean.split()
    if not words:
        return True
    if clean in UNDERSPECIFIED_SEEDS:
        return True
    if len(words) <= 2:
        if words[-1] in {"app", "apps", "website", "tool", "software", "dashboard", "saas", "platform", "bot", "script", "program"}:
            if words[0] in {"build", "make", "create", "develop", "code", "design", "new", "simple", "a", "an", "the", "my"}:
                return True
    return False


def classify_input_domain(input_text: str) -> str:
    """
    Classifies the raw input text to the most relevant domain knowledge base.
    """
    text_lower = input_text.lower()
    for domain_key, data in DOMAIN_KNOWLEDGE.items():
        if domain_key == "generic":
            continue
        for kw in data["keywords"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return domain_key
    return "generic"


def generate_heuristic_prompt(
    input_text: str,
    target_agent: TargetAgent,
    framework_style: FrameworkStyle,
    depth: ExpansionDepth
) -> Tuple[str, ExplanationData]:
    """
    Generates a high-quality prompt and explanation deterministically based on semantic analysis.
    """
    domain_key = classify_input_domain(input_text)
    kb = DOMAIN_KNOWLEDGE[domain_key]

    role = kb["role_titles"].get(target_agent, kb["role_titles"][TargetAgent.CODING_ASSISTANT])
    clean_topic = input_text.strip().strip('"').strip("'")
    if not clean_topic:
        clean_topic = "Full-Stack Application Development"

    is_underspecified = is_underspecified_input(input_text)

    # Assemble contextual elements
    context_lines = "\n".join([f"- {c}" for c in kb["extrapolated_context"]])
    steps_lines = "\n".join([f"{i+1}. {s}" for i, s in enumerate(kb["actionable_steps"])])
    neg_constraints = "\n".join([f"- {c}" for c in kb["negative_constraints"]])
    placeholders_list = "\n".join([f"- `{p.tag}`: {p.description} (Example: `{p.example}`)" for p in kb["placeholders"]])

    if is_underspecified:
        explanation = ExplanationData(
            detected_intent=f"Ambiguity Discovery & Architecture Protocol for: '{clean_topic}'",
            target_domain=kb["domain"],
            extrapolated_context=[
                "Detected open-ended/underspecified seed keyword. Injected an interactive Requirements Discovery Protocol.",
                "Mandated confirmation of the core hero workflow, target platform (Web/Mobile), and database needs.",
                "Surfaced 3 concrete production-ready application archetypes to ground the execution.",
                *kb["extrapolated_context"][:3]
            ],
            injected_negative_constraints=[
                "DO NOT generate blind mock or generic boilerplate code before confirming what the app is for.",
                *kb["negative_constraints"]
            ],
            suggested_schemas=[kb["output_schema"]],
            placeholders=kb["placeholders"],
            rationale=(
                f"Input '{clean_topic}' is broad and underspecified. Instead of generating arbitrary or generic code, "
                f"Easeprompt structured an interactive Requirements Discovery Protocol with targeted scoping questions, "
                f"3 production archetypes, dynamic requirement placeholders, and strict guardrails so the executing AI "
                f"accurately discovers user requirements before writing code."
            )
        )
    else:
        explanation = ExplanationData(
            detected_intent=f"High-impact prompt generation for: '{clean_topic}'",
            target_domain=kb["domain"],
            extrapolated_context=kb["extrapolated_context"],
            injected_negative_constraints=kb["negative_constraints"],
            suggested_schemas=[kb["output_schema"]],
            placeholders=kb["placeholders"],
            rationale=(
                f"Analyzed input '{clean_topic}' and mapped to domain '{kb['domain']}'. "
                f"Synthesized a specialized persona for '{target_agent.value}', established real-world architectural "
                f"context, injected explicit failure-prevention guardrails, and surfaced dynamic placeholders."
            )
        )

    # Format according to selected framework
    if framework_style == FrameworkStyle.ART_FRAMEWORK:
        if is_underspecified:
            generated = f"""[Act as]
Act as a {role}. You operate with the highest level of technical rigor, domain depth, and architectural precision in {kb['domain']}.

[Request]
You are tasked with guiding, architecting, and building an end-to-end, production-ready solution based on the user's high-level seed: **{clean_topic.capitalize()}**.

Because this seed is currently open-ended and underspecified, **DO NOT GENERATE BLIND OR ARBITRARY CODE YET**. Instead, you must first execute an interactive Requirements Discovery and Architecture Alignment Protocol:

### Phase 1: Ambiguity Resolution & Discovery Questions
Prompt the user immediately to confirm the following essential application parameters:
1. **Target Problem & Purpose**: What specific problem does this solve, and who are the core target users?
2. **Platform & Modality**: Is this a Responsive Web App (Next.js / Vite), a Cross-Platform Mobile App (React Native / Flutter), or a Desktop Utility?
3. **Core Hero Workflow**: What is the single most critical end-to-end user workflow (e.g. browse -> cart -> checkout, upload -> process -> report, or live chat)?
4. **Data & Infrastructure Scope**: Does this require persistent cloud authentication, cloud database, third-party APIs, or local offline storage?

### Phase 2: Proposed Implementation Archetypes
Present the user with 3 concrete, production-ready implementation blueprints to choose from:
- **Archetype 1: Interactive SaaS & Productivity Tool** (Next.js App Router, Tailwind CSS, TypeScript, Supabase Auth + Postgres, Server Actions).
- **Archetype 2: Real-Time Collaborative / Social Application** (React, WebSockets / Supabase Realtime, Zustand state, Tailwind CSS).
- **Archetype 3: E-Commerce & Transactional Marketplace** (Next.js, Stripe Payments, Cloud SQL / Prisma, Redis caching, edge deployment).

### Phase 3: Architecture Blueprint & Modular Implementation
Once the user confirms their chosen archetype or answers the discovery questions:
1. Deliver the end-to-end system architecture (Database schema DDL, API contracts, State management).
2. Provide complete, modular, runnable code for the core feature with zero placeholders.
3. Include production verification tests (unit & integration) and deployment setup (Docker / Vercel).

### Context & Technical Foundations:
{context_lines}

### Dynamic Parameters & User Variables:
Before executing, replace or verify the following configuration parameters:
{placeholders_list}

### Step-by-Step Deliverables:
{steps_lines}

[Terms]
### Actionable Execution Constraints:
- DO NOT start writing generic placeholder code until the core workflow and platform requirements are clarified or confirmed against one of the 3 archetypes.
- Present the discovery questions and 3 concrete archetypes clearly at the start of your response.
- Once the archetype is selected, deliver fully functional, modular, production code with zero ellipses or truncation.
- Adhere strictly to the performance SLA: [SPECIFY OPERATING_SLA || "p99 < 100ms"].
- Include comprehensive inline documentation and automated unit verification tests.

### Negative Constraints (Strict Guardrails - WHAT NOT TO DO):
- DO NOT start spitting out random mock code without first asking or confirming what the app is for.
{neg_constraints}

### Expected Output Specification:
Provide the deliverable structured cleanly, accompanied by the following standardized verification schema:
```
{kb['output_schema']}
```
"""
        else:
            generated = f"""[Act as]
Act as a {role}. You operate with the highest level of technical rigor, domain depth, and architectural precision in {kb['domain']}.

[Request]
Design and deliver an end-to-end, production-ready solution for: **{clean_topic.capitalize()}**.

### Context & Technical Foundations:
{context_lines}

### Dynamic Parameters & User Variables:
Before executing, replace or verify the following configuration parameters:
{placeholders_list}

### Step-by-Step Deliverables:
{steps_lines}

[Terms]
### Actionable Execution Constraints:
- Provide complete, robust implementations with zero truncation or omissions.
- Adhere strictly to the performance SLA: [SPECIFY OPERATING_SLA || "p99 < 100ms"].
- Include comprehensive inline documentation and automated unit verification tests.

### Negative Constraints (Strict Guardrails - WHAT NOT TO DO):
{neg_constraints}

### Expected Output Specification:
Provide the deliverable structured cleanly, accompanied by the following standardized verification schema:
```
{kb['output_schema']}
```
"""

    elif framework_style == FrameworkStyle.MODULAR_SPEC:
        discovery_section = ""
        if is_underspecified:
            discovery_section = """
## 2.1 Ambiguity Resolution & Discovery Protocol
Because this seed is open-ended, **DO NOT GENERATE CODE BLINDLY**. First execute the following discovery protocol:
- **Clarification 1 (Purpose)**: Ask the user for the specific business problem or use case.
- **Clarification 2 (Platform)**: Confirm whether the target is Web, iOS/Android Mobile, or Desktop.
- **Clarification 3 (Workflow)**: Pin down the primary user interaction flow.
- **Archetype Options**: Propose 3 tailored archetypes (SaaS Workflow, Real-Time App, or E-Commerce).
"""
        generated = f"""# System Specification: {clean_topic.upper()}{" (Interactive Discovery)" if is_underspecified else ""}
## 1. Persona & Operational Authority
Act as a **{role}** possessing verified expertise in {kb['domain']}.

## 2. Core Mission & Objectives
Develop a scalable, resilient, and enterprise-grade implementation for: **{clean_topic.capitalize()}**.{discovery_section}

## 3. Extrapolated System Context & Assumptions
{context_lines}

## 4. Parameter Placeholders (Dynamic Configuration)
{placeholders_list}

## 5. Sequential Execution Protocol
{steps_lines}

## 6. Actionable Guardrails & SLAs
- Ensure type-safe interfaces, robust error boundaries, and deterministic recovery.
- Validate all payloads against schema prior to processing.
{"- Require archetype confirmation before generating production codebase." if is_underspecified else ""}

## 7. Negative Constraints (Prohibited Anti-Patterns)
{"- DO NOT output mock code before confirming what the application does." if is_underspecified else ""}
{neg_constraints}

## 8. Verified Deliverable Schema
```
{kb['output_schema']}
```
"""

    elif framework_style == FrameworkStyle.XML_GUARDRAILED:
        discovery_xml = ""
        if is_underspecified:
            discovery_xml = """  <discovery_protocol>
    <question_1>What specific problem does this application solve and who are the core target users?</question_1>
    <question_2>What is the target platform (Responsive Web, iOS/Android Mobile, or Desktop)?</question_2>
    <question_3>What is the single most critical user workflow?</question_3>
    <proposed_archetypes>
      <archetype_a>SaaS Productivity & Workflow Tool (Next.js, Supabase, Tailwind)</archetype_a>
      <archetype_b>Real-Time Social / Messaging App (React, WebSockets)</archetype_b>
      <archetype_c>E-Commerce & Transactional Marketplace (Stripe, Postgres)</archetype_c>
    </proposed_archetypes>
  </discovery_protocol>
"""
        generated = f"""<system_directive>
  <role>{role}</role>
  <domain>{kb['domain']}</domain>
  
  <mission>
    Deliver an exhaustive, fault-tolerant production architecture for: {clean_topic.capitalize()}.
    {"Conduct an interactive Requirements Discovery before outputting full code." if is_underspecified else ""}
  </mission>
{discovery_xml}
  <context>
{context_lines}
  </context>

  <dynamic_placeholders>
{placeholders_list}
  </dynamic_placeholders>

  <execution_instructions>
{steps_lines}
  </execution_instructions>

  <negative_constraints>
{"  - DO NOT output mock code before clarifying requirements." if is_underspecified else ""}
{neg_constraints}
  </negative_constraints>

  <output_schema>
<![CDATA[
{kb['output_schema']}
]]>
  </output_schema>
</system_directive>
"""

    elif framework_style == FrameworkStyle.AUTONOMOUS_REACT:
        if is_underspecified:
            loop_text = f"""1. **Thought**: The seed '{clean_topic}' is open-ended. I must first prompt the user with discovery questions and 3 concrete application archetypes before generating code.
2. **Action**: Prompt the user to clarify purpose, platform (Web vs Mobile), and core workflow, or select Archetype 1 (SaaS), Archetype 2 (Real-Time), or Archetype 3 (E-Commerce).
3. **Observation**: Await user clarification or selection, validate input parameters, and scaffold the modular architecture."""
        else:
            loop_text = f"""1. **Thought**: Analyze the objective for '{clean_topic}', verify all dynamic parameters, and construct a risk-mitigated execution plan.
2. **Action**: Execute sequential pipeline steps using available tooling and verified schemas.
3. **Observation**: Inspect system feedback, validate edge-case stability, and self-correct any deviations."""

        generated = f"""### Autonomous Agent Mandate: {clean_topic.upper()}{" (Interactive Discovery)" if is_underspecified else ""}
**Agent Identity**: {role}
**Primary Domain**: {kb['domain']}

### ReAct Operational Loop
{loop_text}

### Dynamic Input Parameters:
{placeholders_list}

### Execution Instructions:
{steps_lines}

### Halting & Termination Criteria:
{"- Halt and present discovery questions if application purpose is unspecified." if is_underspecified else ""}
- Halt immediately and return structured output once all deliverables are verified.
- Trigger self-correction if an API error, rate limit, or schema mismatch is detected.

### Strict Negative Constraints (Prohibited Actions):
{"- DO NOT write blind generic code without confirming the app's purpose." if is_underspecified else ""}
{neg_constraints}

### Target Output Contract:
```
{kb['output_schema']}
```
"""
    else:
        generated = f"""[Act as] {role}\n[Request] {clean_topic}\n[Terms] Negative constraints:\n{neg_constraints}"""

    return generated.strip(), explanation
