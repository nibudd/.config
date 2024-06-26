-- convenient folding
return {
    "jghauser/fold-cycle.nvim",
    config = function()
        local fold_cycle = require("fold-cycle")

        fold_cycle.setup({
            open_if_max_closed = false,    -- closing a fully closed fold will open it
            close_if_max_opened = false,   -- opening a fully open fold will close it
        })

        vim.keymap.set("n", "<S-Tab>",
            function() return fold_cycle.close() end,
            {silent = true, desc = "Fold-cycle: close folds"})

        vim.keymap.set("n", "<M-Tab>",
            function() return fold_cycle.open() end,
            {silent = true, desc = "Fold-cycle: open folds"})

        -- vim.keymap.set("n", "<M-Tab>",
        --     function() return fold_cycle.toggle_all() end,
        --     {remap = true, silent = true, desc = "Fold-cycle: toggle all folds"})
    end
}
