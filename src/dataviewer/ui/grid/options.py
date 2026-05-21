from dataviewer.ui.grid.columns import default_col_defs, col_defs


def options(cart: bool) -> dict:
    return {
        "selectionColumnDef": {"hide": cart, "maxWidth": 35, "sortable": True},
        "columnDefs": col_defs(cart),
        "defaultColDef": default_col_defs(),
        "alwaysMultiSort": True,
        "rowSelection": {
            "mode": "multiRow",
            "selectAll": "filtered",
            "checkboxes": True,
            "headerCheckbox": True,
            ":isRowSelectable": "(r) => r.isRowPinned",
        }
        if not cart
        else "",
        "autoSizePadding": 1,
        "autoSizeStrategy": {
            "type": "fitCellContents",
        },
        "suppressRowHoverHighlight": cart,
        "undoRedoCellEditing": True,
        "undoRedoCellEditingLimit": 20,
        "readOnlyEdit": True,
        "invalidEditValueMode": "block",
        "suppressCellFocus": True,
        "enterNavigatesVerticallyAfterEdit": True,
        "singleClickEdit": True,
        "stopEditingWhenCellsLoseFocus": True,
        ":getRowId": "(p) => p.data.index.toString()",
    }
