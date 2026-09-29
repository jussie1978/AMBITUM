"""PR-02 smoke: Smart Metadata is a Case/SharedDocument Pool capability."""

from pathlib import Path

from jinja2 import Environment


template = Path("app/templates/workspace.html").read_text(encoding="utf-8-sig")
route = Path("app/routes/workspace.py").read_text(encoding="utf-8-sig")

# Parsing catches malformed Jinja without requiring a live database or session.
Environment().parse(template)

required_route = {
    "metadata-service": "from app.services.smart_metadata_service import list_metadata",
    "case-scoped-list": "list_metadata(db, case_ref=case_ref)",
    "document-grouping": "smart_metadata_by_document",
    "filter-data": '"smart_metadata_filter_values"',
    "pool-context": '"smart_metadata_by_document": smart_metadata_by_document',
}
missing_route = [name for name, marker in required_route.items() if marker not in route]

required_template = {
    "real-target-filter": 'id="pool-target-filter"',
    "real-topic-filter": 'id="pool-topic-filter"',
    "real-tag-filter": 'id="pool-tag-filter"',
    "real-target-values": "smart_metadata_filter_values.target",
    "real-topic-values": "smart_metadata_filter_values.topic",
    "real-tag-values": "smart_metadata_filter_values.tag",
    "target-badge": "data-metadata-targets=",
    "topic-badge": "data-metadata-topics=",
    "tag-badge": "data-metadata-tags=",
    "badge-kind": 'data-metadata-kind="{{ metadata.kind }}"',
    "generic-selection": '.pool-inventory-select[data-source-token]',
    "document-selection": 'data-source-token="document:{{ item.id }}"',
    "batch-controls": 'id="smart-metadata-add"',
    "batch-remove": 'id="smart-metadata-remove"',
    "batch-endpoint": "/smart-metadata/batch",
    "case-isolation": "encodeURIComponent(caseRef)",
    "batch-put": "method:'PUT'",
    "batch-documents": "document_ids:documentIds",
    "human-agnostic-browser": "linked_person_id:linkedPersonId",
    "filter-function": "function applyPoolInventoryFilters()",
    "target-filter-listener": "poolMetadataFilters.forEach(filter=>filter.addEventListener('change',applyPoolInventoryFilters))",
    "source-selection-change": "item.addEventListener('change'",
    "batch-add-listener": "smartMetadataAdd?.addEventListener('click',()=>mutateSmartMetadata('add'))",
    "batch-remove-listener": "smartMetadataRemove?.addEventListener('click',()=>mutateSmartMetadata('remove'))",
    "legacy-block-bridge": "hidden.name='sources'",
    "legacy-block-bridge-class": "pool-selection-bridge-input",
}
missing_template = [
    name for name, marker in required_template.items() if marker not in template
]

# Selection controls must be siblings of the block form and submit values only
# through the compatibility bridge when the legacy form is submitted.
block_form_start = template.find('id="create-block-form"')
block_form_end = template.find("</form>", block_form_start)
selection_start = template.find('id="context-selection-bar"')
if block_form_start < 0 or block_form_end < 0 or selection_start < 0:
    selection_decoupled = False
else:
    selection_decoupled = not (block_form_start < selection_start < block_form_end)

# The Smart Metadata mutation segment must only call the Case batch API; it
# must not create or depend on blocks/workspaces.
mutation_start = template.find("async function mutateSmartMetadata(operation)")
mutation_end = template.find("function addMessage(", mutation_start)
mutation_segment = template[mutation_start:mutation_end] if mutation_start >= 0 else ""
metadata_block_coupling = any(
    marker in mutation_segment.lower()
    for marker in ("create-block", "workspace_id", "/blocks", "investigativeblock")
)

if missing_route or missing_template or not selection_decoupled or metadata_block_coupling:
    details = []
    if missing_route:
        details.append("missing-route=" + ",".join(missing_route))
    if missing_template:
        details.append("missing-template=" + ",".join(missing_template))
    if not selection_decoupled:
        details.append("selection-still-coupled-to-block-form")
    if metadata_block_coupling:
        details.append("metadata-block-coupling")
    raise SystemExit("PR-02 WORKSPACE SMART METADATA SMOKE: FAIL -> " + " | ".join(details))

print("PR-02 WORKSPACE SMART METADATA SMOKE: OK")
print("case-context=real-metadata-and-filter-values")
print("target-topic-tag=real-data-filters-and-badges")
print("selection=generic-pool-with-legacy-submit-bridge")
print("batch=case-scoped-put-controls-and-listeners")
print("metadata-to-block-dependency=no")
print("jinja=parse-ok")
