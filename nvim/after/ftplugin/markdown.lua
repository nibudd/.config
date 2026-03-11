vim.opt_local.wrap = true       -- Enable visual wrapping
vim.opt_local.linebreak = true  -- Wrap at word boundaries rather than in the middle of a word
vim.opt_local.breakindent = true -- Maintain indentation on wrapped lines
vim.bo.expandtab = true
vim.bo.shiftwidth = 2
vim.bo.softtabstop = 2
vim.bo.tabstop = 2

-- remap j/k to navigate by screen lines (gj/gk)
vim.keymap.set("n", "j", "gj", { buffer = true })
vim.keymap.set("n", "k", "gk", { buffer = true })

