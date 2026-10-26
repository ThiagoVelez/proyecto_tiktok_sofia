"""
Módulo de Reglas: Seguridad de Contenido y Moderación Automática
Proyecto Sofía - Plataforma de Videos Cortos (TikTok-like)

Este módulo implementa el motor de reglas para analizar textos (títulos, descripciones,
hashtags y comentarios), detectar lenguaje no apto para la audiencia, contenido ofensivo,
violencia o temas explícitos, y prevenir que afecte a la comunidad.
"""

import re
import unicodedata
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
import json
from pathlib import Path


class ModerationSeverity(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModerationAction(str, Enum):
    ALLOW = "allow"
    FLAG_CONTENT = "flag_content"
    AGE_RESTRICT = "age_restrict"
    HIDE_FROM_RECOMMENDATIONS = "hide_from_recommendations"
    BLOCK_IMMEDIATE = "block_immediate"


@dataclass
class SafetyScanResult:
    is_safe: bool
    risk_score: float  # De 0.0 (totalmente seguro) a 1.0 (extremadamente riesgoso)
    severity: ModerationSeverity
    recommended_action: ModerationAction
    triggered_categories: List[str] = field(default_factory=list)
    detected_keywords: List[str] = field(default_factory=list)
    sanitized_text: Optional[str] = None
    reason: str = "Contenido verificado y seguro."


class ContentSafetyEngine:
    """
    Motor heurístico y de reglas para la seguridad y moderación de contenidos.
    """

    # Diccionario de equivalencias leetspeak para evitar evasión de filtros
    LEET_MAP = {
        '4': 'a', '@': 'a',
        '3': 'e',
        '1': 'i', '!': 'i', '|': 'i',
        '0': 'o',
        '5': 's', '$': 's',
        '7': 't', '+': 't',
        '8': 'b',
    }

    def __init__(self, config_path: Optional[str] = None):
        self.categories: Dict[str, Any] = {}
        self._compiled_patterns: Dict[str, List[re.Pattern]] = {}
        self._load_configuration(config_path)

    def _load_configuration(self, config_path: Optional[str] = None):
        """Carga reglas y palabras clave desde config_rules.json o usa reglas base."""
        if not config_path:
            base_dir = Path(__file__).resolve().parent
            config_path = str(base_dir / "config_rules.json")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.categories = data.get("moderation_categories", {})
        except Exception:
            # Reglas predeterminadas de respaldo
            self.categories = {
                "violence": {
                    "severity": "high",
                    "keywords": ["matar", "asesinar", "arma", "bomba", "degollar", "terrorismo"],
                    "patterns": [r"\b(m[a4]t[a4]r|4s[e3]s[i1]n[a4]r)\b"]
                },
                "sexual_content": {
                    "severity": "critical",
                    "keywords": ["porno", "pornografía", "desnudo", "sexo explícito", "pack erótico"],
                    "patterns": [r"\b(p[o0]rn[o0]|s[e3]x[o0])\b"]
                },
                "harassment_bullying": {
                    "severity": "medium",
                    "keywords": ["inútil", "mátate", "muérete", "escoria", "idiota"],
                    "patterns": [r"\b(m[u4][e3]r[e3]t[e3]|m[a4]t[a4]t[e3])\b"]
                },
                "self_harm": {
                    "severity": "critical",
                    "keywords": ["suicidio", "suicidarme", "autolesión", "cortarme"],
                    "patterns": [r"\b(su[i1]c[i1]d[i1][o0])\b"]
                },
                "profanity_mild": {
                    "severity": "low",
                    "keywords": ["mierda", "estúpido", "carajo", "maldito", "puta"],
                    "patterns": [r"\b(m[i1][e3]rd[a4]|caraj[o0])\b"]
                }
            }

        # Compilar expresiones regulares para alto rendimiento
        for cat_name, cat_data in self.categories.items():
            compiled = []
            for pattern_str in cat_data.get("patterns", []):
                try:
                    compiled.append(re.compile(pattern_str, re.IGNORECASE))
                except re.error:
                    continue
            self._compiled_patterns[cat_name] = compiled

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """
        Normaliza el texto removiendo acentos, caracteres extraños y traduciendo leetspeak.
        Ejemplo: 'p0rn0 gr4t!s' -> 'porno gratis'
        """
        if not text:
            return ""

        # Eliminar acentos y diacríticos
        text_decomposed = unicodedata.normalize('NFD', text)
        cleaned_text = "".join(c for c in text_decomposed if unicodedata.category(c) != 'Mn')
        cleaned_text = cleaned_text.lower()

        # Reemplazar leetspeak común
        normalized_chars = []
        for char in cleaned_text:
            normalized_chars.append(cls.LEET_MAP.get(char, char))
        normalized = "".join(normalized_chars)

        # Quitar caracteres repetitivos sospechosos (ej: 'puuuutaaaa' -> 'puta')
        normalized = re.sub(r'(.)\1{2,}', r'\1\1', normalized)
        return normalized

    def scan_text(self, text: str, user_is_minor: bool = False) -> SafetyScanResult:
        """
        Analiza el texto de forma exhaustiva y retorna la evaluación de seguridad.
        """
        if not text or not text.strip():
            return SafetyScanResult(
                is_safe=True,
                risk_score=0.0,
                severity=ModerationSeverity.SAFE,
                recommended_action=ModerationAction.ALLOW,
                sanitized_text=text,
                reason="Texto vacío o seguro."
            )

        normalized = self.normalize_text(text)
        triggered_categories = []
        detected_keywords = []
        max_severity_weight = 0
        sanitized_copy = text

        # Pesos de severidad
        severity_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }

        for cat_name, cat_data in self.categories.items():
            cat_severity = cat_data.get("severity", "low")
            weight = severity_weights.get(cat_severity, 0.2)
            keywords = cat_data.get("keywords", [])
            matched = False

            # Búsqueda por palabras clave exactas o por límites de palabra
            for kw in keywords:
                clean_kw = self.normalize_text(kw)
                if re.search(r'\b' + re.escape(clean_kw) + r'\b', normalized, re.IGNORECASE):
                    matched = True
                    detected_keywords.append(kw)
                    # Enmascarar la palabra en el texto sanitizado
                    sanitized_copy = re.sub(
                        re.escape(kw),
                        lambda m: m.group(0)[0] + ("*" * (len(m.group(0)) - 1)),
                        sanitized_copy,
                        flags=re.IGNORECASE
                    )

            # Búsqueda por patrones regex
            for pat in self._compiled_patterns.get(cat_name, []):
                if pat.search(normalized):
                    matched = True

            if matched:
                triggered_categories.append(cat_name)
                if weight > max_severity_weight:
                    max_severity_weight = weight

        # Calcular severidad y acción recomendada
        if max_severity_weight >= 1.0:
            severity = ModerationSeverity.CRITICAL
            action = ModerationAction.BLOCK_IMMEDIATE
            is_safe = False
            reason = "El contenido viola gravemente las normas de seguridad de la comunidad (autolesión o contenido sexual explícito)."
        elif max_severity_weight >= 0.8:
            severity = ModerationSeverity.HIGH
            action = ModerationAction.HIDE_FROM_RECOMMENDATIONS
            is_safe = False
            reason = "El contenido contiene indicios de violencia, odio o agresión y ha sido ocultado para revisión."
        elif max_severity_weight >= 0.5:
            severity = ModerationSeverity.MEDIUM
            action = ModerationAction.AGE_RESTRICT
            is_safe = not user_is_minor
            reason = "El contenido contiene lenguaje ofensivo o acoso; restringido para menores de edad."
        elif max_severity_weight >= 0.2:
            severity = ModerationSeverity.LOW
            action = ModerationAction.FLAG_CONTENT if not user_is_minor else ModerationAction.AGE_RESTRICT
            is_safe = not user_is_minor
            reason = "Contiene groserías o lenguaje coloquial fuerte filtrado para audiencia infantil."
        else:
            severity = ModerationSeverity.SAFE
            action = ModerationAction.ALLOW
            is_safe = True
            reason = "Contenido adecuado para toda la audiencia."

        return SafetyScanResult(
            is_safe=is_safe,
            risk_score=round(max_severity_weight, 2),
            severity=severity,
            recommended_action=action,
            triggered_categories=triggered_categories,
            detected_keywords=list(set(detected_keywords)),
            sanitized_text=sanitized_copy,
            reason=reason
        )
