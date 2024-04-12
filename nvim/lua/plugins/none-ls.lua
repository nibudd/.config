-- neovim as language server
return {
  "nvimtools/none-ls.nvim",
  config = function()
    local null_ls = require("null-ls")
    null_ls.setup({
      sources = {
        null_ls.builtins.diagnostics.mypy,
        null_ls.builtins.diagnostics.ruff,
        null_ls.builtins.formatting.black,
      },
    })

    vim.keymap.set("n", "<leader>fm", vim.lsp.buf.format, {})
  end,
}
