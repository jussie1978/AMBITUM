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
    "smart-bins": 'id="smart-bins"',
    "target-bin-group": 'data-smart-bin-group="target"',
    "topic-bin-group": 'data-smart-bin-group="topic"',
    "tag-bin-group": 'data-smart-bin-group="tag"',
    "dynamic-bin-counts": "documents:new Set()",
    "active-bin": "button.classList.add('is-active')",
    "bin-filter": "metadata.kind===activeSmartBin.kind",
    "target-badge": "data-metadata-targets=",
    "topic-badge": "data-metadata-topics=",
    "tag-badge": "data-metadata-tags=",
    "badge-kind": 'data-metadata-kind="{{ metadata.kind }}"',
    "clean-chip-label": "valueButton.textContent=metadata.value_text",
    "chip-navigation": "toggleSmartBin(metadata.kind,metadata.value_text)",
    "chip-direct-remove": "className='metadata-chip__remove'",
    "generic-selection": '.pool-inventory-select[data-source-token]',
    "document-selection": 'data-source-token="document:{{ item.id }}"',
    "quick-target": 'data-quick-kind="target"',
    "quick-topic": 'data-quick-kind="topic"',
    "quick-tag": 'data-quick-kind="tag"',
    "inline-editor": 'id="pool-quick-editor"',
    "enter-applies": "if(event.key==='Enter')",
    "escape-cancels": "else if(event.key==='Escape')",
    "target-people": "smartMetadataPeople.forEach(person=>suggestions.push",
    "explicit-person-id": "quickLinkedPersonId=item.personId",
    "common-intersection": "otherKeys.every(keys=>keys.has(metadataIdentity(metadata)))",
    "common-remove": "createMetadataChip(metadata,{common:true})",
    "batch-endpoint": "smartMetadataEndpoint+'/batch'",
    "canonical-refresh": "async function refreshSmartMetadata()",
    "case-isolation": "encodeURIComponent(caseRef)",
    "batch-put": "method:'PUT'",
    "batch-documents": "document_ids:documentIds",
    "human-agnostic-browser": "linked_person_id:linkedPersonId",
    "filter-function": "function applyPoolInventoryFilters()",
    "source-selection-change": "item.addEventListener('change'",
}
missing_template = [
    name for name, marker in required_template.items() if marker not in template
]

# Selection must remain independent of a legacy form when one is present.
# The presence or functionality of a legacy block/bridge is not a PR-02 gate.
block_form_start = template.find('id="create-block-form"')
block_form_end = template.find("</form>", block_form_start)
selection_start = template.find('id="context-selection-bar"')
selection_decoupled = selection_start >= 0 and not (
    block_form_start >= 0 and block_form_start < selection_start < block_form_end
)
legacy_quick_action_absent = not any(marker in template for marker in (
    'id="use-selection-in-block"', "useSelectionInBlock", "Usar no bloco",
))

# The Smart Metadata mutation segment must only call the Case batch API; it
# must not create or depend on blocks/workspaces.
mutation_start = template.find("async function mutateSmartMetadata({operation,documentIds,kind,value,linkedPersonId=null})")
mutation_end = template.find("function addMessage(", mutation_start)
mutation_segment = template[mutation_start:mutation_end] if mutation_start >= 0 else ""
metadata_block_coupling = any(
    marker in mutation_segment.lower()
    for marker in ("create-block", "workspace_id", "/blocks", "investigativeblock")
)
permanent_form_absent = not any(marker in template for marker in (
    'id="smart-metadata-kind"',
    'id="smart-metadata-value"',
    'id="smart-metadata-person"',
    'id="smart-metadata-add"',
    'id="smart-metadata-remove"',
))
metadata_reload_absent = "window.location.reload()" not in mutation_segment
metadata_select_filters_absent = not any(marker in template for marker in (
    'id="pool-target-filter"',
    'id="pool-topic-filter"',
    'id="pool-tag-filter"',
))

if (
    missing_route or missing_template or not selection_decoupled
    or not legacy_quick_action_absent
    or metadata_block_coupling or not permanent_form_absent
    or not metadata_reload_absent or not metadata_select_filters_absent
):
    details = []
    if missing_route:
        details.append("missing-route=" + ",".join(missing_route))
    if missing_template:
        details.append("missing-template=" + ",".join(missing_template))
    if not selection_decoupled:
        details.append("selection-still-coupled-to-block-form")
    if not legacy_quick_action_absent:
        details.append("legacy-block-quick-action-present")
    if metadata_block_coupling:
        details.append("metadata-block-coupling")
    if not permanent_form_absent:
        details.append("permanent-metadata-form-present")
    if not metadata_reload_absent:
        details.append("metadata-reloads-page")
    if not metadata_select_filters_absent:
        details.append("legacy-metadata-select-filters-present")
    raise SystemExit("PR-02 WORKSPACE SMART METADATA SMOKE: FAIL -> " + " | ".join(details))

print("PR-02 WORKSPACE SMART METADATA SMOKE: OK")
print("case-context=real-metadata")
print("target-topic-tag=quick-actions-clean-chips-smart-bins")
print("selection=generic-pool-independent-of-legacy-blocks")
print("batch=inline-editor-common-intersection-direct-remove")
print("refresh=canonical-get-without-page-reload")
print("metadata-to-block-dependency=no")
print("jinja=parse-ok")
