"""
Quality Filter and Gibberish Detection Engine for Easeprompt.
Intercepts nonsensical, keyboard-mashed, unpronounceable, or spam inputs
before prompt generation to ensure domain accuracy and system integrity.
"""

import re
from typing import Tuple, Optional, Set

# Valid technical and domain abbreviations / acronyms that might otherwise
# trigger vowelless or unusual morphology checks.
VALID_ACRONYMS: Set[str] = {
    # Web & Protocols
    "api", "cli", "sdk", "rest", "crud", "graphql", "gql", "grpc", "mqtt", "rpc",
    "http", "https", "dns", "tcp", "udp", "ip", "ipv4", "ipv6", "ssh", "ssl", "tls",
    "cors", "csrf", "xss", "jwt", "oauth", "sso", "saml", "oidc", "rbac", "abac", "pkce",
    "cdn", "url", "uri", "uuid", "guid", "dom", "html", "css", "svg", "pwa", "spa", "ssr",
    # Languages & Runtimes
    "js", "ts", "py", "sql", "wasm", "nosql", "php", "npm", "npx", "pnpm", "yarn", "pip",
    # Data & Storage
    "db", "dw", "etl", "elt", "dbt", "ddl", "dml", "cte", "orm", "acid", "json", "yaml",
    "xml", "csv", "blob", "s3", "gcs", "rds", "redis", "kafka", "mq", "cron",
    # Cloud & DevOps
    "aws", "gcp", "k8s", "ecs", "ec2", "iam", "vpc", "nat", "vpn", "ci", "cd", "pr",
    # AI & Compute
    "ai", "ml", "llm", "rag", "nlp", "ocr", "cv", "cpu", "gpu", "tpu", "ram", "ssd",
    # Business & Product
    "ui", "ux", "mrr", "arr", "clv", "cac", "roi", "kpi", "okr", "crm", "cms", "erp", "pos",
    # Common short valid English abbreviations
    "tv", "id", "ok", "app", "bot", "doc", "faq", "bio", "dev", "ops", "sec"
}

# Keyboard Mash Patterns (QWERTY layout walks)
KEYBOARD_WALKS = [
    "qwerty", "wertyu", "ertyui", "rtyuio", "tyuiop",
    "asdfgh", "sdfghj", "dfghjk", "fghjkl",
    "zxcvbn", "xcvbnm",
    "poiuyt", "lkjhgf", "mnbvcx",
    "qazwsx", "wsxedc", "edcrfv", "rfvtgb",
    "12345", "23456", "34567", "45678", "56789", "67890"
]

# Sequential consonant alphabet walks (e.g. bcdf, dfgh, fghj)
ALPHABET_CONSONANT_WALKS = [
    "bcdf", "cdfg", "dfgh", "fghj", "ghjk", "hjkl", "jklm",
    "klmn", "lmnp", "mnpq", "npqr", "pqrs", "qrst", "rstv", "stvw", "tvwx", "vwxz"
]

# Standard alphabet walks of 4+ characters
ALPHABET_WALKS = [
    "abcd", "bcde", "cdef", "defg", "efgh", "fghi", "ghij", "hijk",
    "ijkl", "jklm", "klmn", "lmno", "mnop", "nopq", "opqr", "pqrs",
    "qrst", "rstu", "stuv", "tuvw", "uvwx", "vwxy", "wxyz"
]

# Legitimate English words with 5 consecutive consonants
LEGITIMATE_CONSONANT_EXCEPTIONS = {
    "strengths", "length", "lengths", "twelfths", "catchphrase", "latchstring",
    "bortsch", "angsts", "rhythms"
}


def check_word_gibberish(word: str) -> Optional[str]:
    """
    Checks if an individual token is unpronounceable gibberish or keyboard mash.
    Returns an explanatory error string if gibberish, otherwise None.
    """
    w = word.lower().strip()
    # Strip leading/trailing punctuation
    w = re.sub(r'^[^a-z0-9]+|[^a-z0-9]+$', '', w)
    
    if len(w) < 2:
        return None

    # Check against known technical abbreviations
    if w in VALID_ACRONYMS:
        return None

    # 1. Check for single character repeated 3 or more times (e.g. 'aaaaa', 'zzzz', '1111')
    if re.search(r'(.)\1{2,}', w):
        return f"repeated character sequence ('{word}')"

    # 2. Check for 2-3 char pattern repeated 3+ times (e.g. 'asdasd', 'qwqwqw', 'ababab')
    if re.search(r'(.{2,3})\1{2,}', w):
        return f"repetitive pattern ('{word}')"

    # 3. Check for keyboard mash sequences (e.g. 'qwerty', 'asdfgh', 'zxcvbn')
    for kw in KEYBOARD_WALKS:
        if kw in w:
            return f"keyboard mash pattern ('{word}')"

    # 4. Check for sequential consonant alphabet walks (e.g. 'bcdf', 'dfgh' in 'ABCDFGHAG')
    for cw in ALPHABET_CONSONANT_WALKS:
        if cw in w:
            return f"alphabet consonant mash ('{word}')"

    for aw in ALPHABET_WALKS:
        if aw in w and len(aw) >= 4 and len(w) <= 8 and w not in {"feedback", "backdoor"}:
            return f"alphabetical sequence ('{word}')"

    # 5. Check for 5 or more consecutive consonants (treating a, e, i, o, u, y as vowels)
    if w not in LEGITIMATE_CONSONANT_EXCEPTIONS:
        consonants_match = re.search(r'[bcdfghjklmnpqrstvwxz]{5,}', w)
        if consonants_match:
            return f"unpronounceable consonant cluster ('{word}')"

    # 6. Check for words >= 4 characters with NO vowels at all (a, e, i, o, u, y)
    if len(w) >= 4 and not re.search(r'[aeiouy]', w):
        return f"unpronounceable vowel-less word ('{word}')"

    # 7. Check for 4 or more consecutive vowels (e.g. 'aeiou', 'uuuii')
    if re.search(r'[aeiouy]{4,}', w) and w not in {"queueing", "onomatopoeia"}:
        return f"unnatural vowel sequence ('{word}')"

    return None


def validate_prompt_input_quality(input_text: str) -> Tuple[bool, str]:
    """
    Validates whether the user's prompt input is meaningful, coherent text.
    Returns (is_valid, error_message).
    """
    cleaned = input_text.strip()
    if not cleaned:
        return False, "Input cannot be empty. Please enter your task or idea."

    # 1. Require at least 2 alphanumeric characters
    alnum = re.sub(r'[^a-zA-Z0-9]', '', cleaned)
    if len(alnum) < 2:
        return False, (
            "Please enter a meaningful task or concept (e.g. 'Fitness tracking app' or 'Sales pitch email'). "
            "A symbol or single character like '.' is not enough to construct a valid prompt."
        )

    # 2. Check if the input is exclusively numbers and symbols without any words
    letters = re.findall(r'[a-zA-Z]', cleaned)
    if len(letters) < 2:
        return False, (
            "Please include descriptive words. Numbers and symbols alone cannot be converted into a prompt."
        )

    # 3. Tokenize words
    tokens = re.findall(r'[a-zA-Z0-9]+', cleaned)
    if not tokens:
        return False, "Please enter a meaningful prompt using letters and words."

    # 4. Check each token for blatant gibberish / keyboard mash
    gibberish_reasons = []
    for token in tokens:
        reason = check_word_gibberish(token)
        if reason:
            gibberish_reasons.append(reason)

    if gibberish_reasons:
        # If any token is flagrant keyboard mash or impossible consonant cluster
        first_issue = gibberish_reasons[0]
        return False, (
            f"The input appears to contain nonsensical or keyboard-mashed text ({first_issue}). "
            "Please describe what you want to create using real words or valid technical terms."
        )

    # 5. Check if the input is a single token of length >= 6 that has an extremely skewed vowel-to-consonant ratio
    if len(tokens) == 1:
        tok = tokens[0].lower()
        if len(tok) >= 6 and tok not in VALID_ACRONYMS:
            vowels = sum(1 for c in tok if c in "aeiouy")
            ratio = vowels / len(tok)
            if ratio < 0.15:
                return False, (
                    f"'{tokens[0]}' does not appear to be a recognizable word. "
                    "Please provide a meaningful idea or task (e.g. 'crypto price tracker' or 'customer feedback form')."
                )

    return True, ""
