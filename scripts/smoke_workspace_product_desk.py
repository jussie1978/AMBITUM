"""UX-03B client contract smoke; browser scenarios provide behavioral proof."""

from pathlib import Path


def main() -> None:
    workspace = Path("app/templates/workspace.html").read_text(encoding="utf-8-sig")
    markup = Path("app/templates/partials/workspace_product_desk.html").read_text(encoding="utf-8-sig")
    script = Path("app/templates/partials/workspace_product_desk_script.html").read_text(encoding="utf-8-sig")
    styles = Path("app/templates/partials/workspace_product_desk_styles.html").read_text(encoding="utf-8-sig")

    for include in (
        'partials/workspace_product_desk.html',
        'partials/workspace_product_desk_script.html',
        'partials/workspace_product_desk_styles.html',
    ):
        assert workspace.count(include) == 1

    for marker in (
        'id="product-select"', 'id="new-product-button"', 'id="product-spine"',
        'id="organize-sections-dialog"', 'id="link-sections-dialog"',
        'id="pending-changes-dialog"', 'id="create-block-form"',
        'data-desk-reload-action', 'data-desk-navigation',
    ):
        assert marker in markup, marker

    for marker in (
        "expected_revision:confirmedProduct.revision",
        "mutationTail=Promise.resolve()",
        "capture={productId:activeProductId,sectionId,title,body:draft.body,version:draft.version}",
        "latest.version===capture.version",
        "redirect:'manual'",
        "response.type==='opaqueredirect'",
        "error.status!==409",
        "O servidor foi relido",
        "Resultado incerto",
        "sectionDrafts.clear();orderDraft=null;linkDrafts.clear()",
        "window.onbeforeunload=hasPendingChanges()",
        "Salvar e continuar",
        "workspaceDeskGuard.canContinue()",
        "window.history.replaceState",
        "localStorage.getItem",
        "productTransition=transition",
        "submitLegacyForm(form,event.submitter)",
        "if(event.defaultPrevented)return",
        "const controls=Array.from(form.elements||[])",
        "product.revision<confirmedProduct.revision",
        "pendingDialog.addEventListener('cancel'",
        "organizerDialog.addEventListener('cancel'",
        "linksDialog.addEventListener('cancel'",
        "decision.saving=true",
        "const workPane=document.getElementById('pane-work')",
        "const workScrollKey='circe-athena.workspace.work-scroll.'+operatorName+'.'+workspaceId",
        "workBlockAnchor(blockId)",
        "scrollHeight:workPane.scrollHeight,clientHeight:workPane.clientHeight",
        "anchorRect.top-paneRect.top",
        "workPane.scrollTop+=currentOffset-state.anchorOffset",
        "preserveWorkScroll(event.currentTarget);window.location.assign(href)",
        "if(document.fonts?.ready)await document.fonts.ready",
        "loadProducts().finally(restoreWorkScrollAfterRender)",
    ):
        assert marker in script or marker in markup, marker

    for marker in (
        "container-type:inline-size", "overflow-x:auto", "scrollIntoView",
        ":focus-visible", "min-height:32px", "@media(max-width:1279px)",
        ".desk-dialog{width:min(560px,calc(100vw - 32px));max-height:calc(100vh - 48px);margin:auto",
        '.desk-dialog input:not([type="checkbox"]):not([type="radio"]){width:100%;height:34px;box-sizing:border-box',
    ):
        assert marker in styles or marker in script, marker

    assert "innerHTML=draft" not in script
    assert "form.submit(" not in script
    assert "form.requestSubmit(" not in script
    assert 'id="cancel-new-product" type="button"' in markup
    assert "safeStorageSet(focusSectionPrefix+productId,sectionId)" in script
    assert "section.body=" not in script
    assert "fetch('/api/pool" not in script
    assert "let selectionControlsLocked=false" in workspace
    assert workspace.count("if(selectionControlsLocked)return;") == 2
    assert "setBlockSelectionLocked(true)" in script
    assert "setBlockSelectionLocked(false)" in script

    print("UX-03B PRODUCT DESK CLIENT CONTRACT: OK")
    print("confirmed-vs-draft=separate; mutations=serialized; stale-response=versioned")
    print("conflict=serialized-reload-without-retry; uncertain-result=no-false-success")
    print("legacy-submit=validation-veto+payload-before-control-lock")
    print("legacy-selection=clear+undo-locked-and-handler-guarded")
    print("dialog=viewport-centered+text-input-full-width")
    print("navigation=three-choice-guard; beforeunload=pending-only")
    print("product-section-focus=url+storage-fallback+legacy-redirect")
    print("work-scroll=pane-work+block-anchor+post-render-geometry-restore")
    print("note=interactive behavior is covered by the controlled integration harness")


if __name__ == "__main__":
    main()
