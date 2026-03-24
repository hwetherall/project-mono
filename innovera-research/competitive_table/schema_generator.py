"""
Step 1: LLM-based schema generation for the Competitive Table.
Determines attributes and target competitor count based on venture context.
"""
import json
import logging

from openai import OpenAI

from competitive_table.models import CompetitiveTableSchema, CompetitiveAttribute, AttributeGroup
from competitive_table.prompts import SCHEMA_GENERATION_SYSTEM, SCHEMA_GENERATION_USER
from context_extraction.models import ContextSignals
from config.settings import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL,
    CONTEXT_LLM_MODEL, CONTEXT_LLM_MAX_TOKENS,
)

logger = logging.getLogger(__name__)


def generate_table_schema(
    context: ContextSignals,
    must_include_companies: list[str] | None = None,
    custom_parameters: list[str] | None = None,
) -> CompetitiveTableSchema:
    """Call the LLM to generate a competitive table schema tailored to the venture."""
    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)

    schema_json = json.dumps(CompetitiveTableSchema.model_json_schema(), indent=2)

    user_message = SCHEMA_GENERATION_USER.format(
        venture_name=context.venture_name,
        industry=context.industry_vertical,
        sub_vertical=context.sub_vertical or "General",
        geography=context.geography,
        stage=context.stage,
        business_model=context.business_model_type,
        solution_category=context.solution_category,
        target_buyer=context.target_buyer_type,
        problem_summary=context.problem_summary,
        solution_summary=context.solution_summary,
        named_competitors=", ".join(context.named_competitors) if context.named_competitors else "None provided",
        schema_json=schema_json,
    )

    response = client.chat.completions.create(
        model=CONTEXT_LLM_MODEL,
        max_tokens=CONTEXT_LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": SCHEMA_GENERATION_SYSTEM},
            {"role": "user", "content": user_message},
        ],
    )

    response_text = response.choices[0].message.content
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    schema = CompetitiveTableSchema.model_validate_json(response_text)

    # Seed known competitors from the brief
    if context.named_competitors:
        existing = {c.lower() for c in schema.seeded_competitors}
        for name in context.named_competitors:
            if name.lower() not in existing:
                schema.seeded_competitors.append(name)

    # --- Inject must-include companies (user-specified Y axis) ---
    if must_include_companies:
        existing_seeded = {c.lower() for c in schema.seeded_competitors}
        for name in must_include_companies:
            if name.strip() and name.strip().lower() not in existing_seeded:
                schema.seeded_competitors.append(name.strip())
                existing_seeded.add(name.strip().lower())
        schema.must_include_companies = [n.strip() for n in must_include_companies if n.strip()]
        logger.info("Injected %d must-include companies: %s", len(schema.must_include_companies), schema.must_include_companies)

    # --- Inject custom parameters (user-specified X axis) ---
    if custom_parameters:
        import re
        existing_ids = {a.attribute_id for a in schema.attributes}
        for param in custom_parameters:
            param = param.strip()
            if not param:
                continue
            param_id = re.sub(r'[^a-z0-9]+', '_', param.lower()).strip('_')
            if param_id not in existing_ids:
                schema.attributes.append(CompetitiveAttribute(
                    attribute_id=param_id,
                    name=param,
                    description=f"User-specified parameter: {param}",
                    group="custom",
                    data_type="text",
                    priority="required",
                ))
                existing_ids.add(param_id)
        # Ensure a "custom" group exists
        group_ids = {g.group_id for g in schema.attribute_groups}
        if "custom" not in group_ids and any(a.group == "custom" for a in schema.attributes):
            schema.attribute_groups.append(AttributeGroup(
                group_id="custom",
                name="Custom Parameters",
                attribute_ids=[a.attribute_id for a in schema.attributes if a.group == "custom"],
            ))
        schema.custom_parameters = [p.strip() for p in custom_parameters if p.strip()]
        logger.info("Injected %d custom parameters: %s", len(schema.custom_parameters), schema.custom_parameters)

    logger.info(
        "Schema generated: %d attributes, %d groups, target %d–%d competitors",
        len(schema.attributes), len(schema.attribute_groups),
        schema.target_competitor_min, schema.target_competitor_max,
    )
    return schema
